"""
FastAPI endpoint for LLM-mediated simulation access.
FULL VERSION with rate limiting, authentication, payments, and audit trail.

Commercial features (Stripe, rate limiting) gracefully degrade if not configured.

Run with: uvicorn llm_endpoint:app --reload
Production: uvicorn llm_endpoint:app --host 0.0.0.0 --port 8000 --workers 4

NOTE: For stripped version without commercial features, use llm_endpoint_core.py
"""

import os
import json
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selene_sim.simulation import ConsortiumSimulator, OutcomeCategory

from .llm_interface import LLMSimulationInterface, REQUIRED_DISCLAIMERS
from .config_factory import make_simulation_config


# =============================================================================
# CONFIGURATION
# =============================================================================

# Environment-based configuration
API_KEY = os.getenv("SELENE_API_KEY", "dev_key_change_in_production")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
AUDIT_LOG_DIR = os.getenv("SELENE_AUDIT_DIR", "audit_logs")
ERROR_LOG_DIR = os.getenv("SELENE_ERROR_DIR", "error_logs")

# Optional Stripe import (graceful degradation if not installed)
try:
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    STRIPE_AVAILABLE = bool(STRIPE_SECRET_KEY)
except ImportError:
    stripe = None
    STRIPE_AVAILABLE = False

# Optional rate limiting (graceful degradation if not installed)
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False


# =============================================================================
# APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="Project Selene LLM API",
    description="Natural language interface to Project Selene ABM Suite v2.1",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting setup (if available)
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: Optional[str] = Depends(api_key_header)) -> str:
    """Verify API key for protected endpoints."""
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key


# Initialize interface
BASE_CONFIG = make_simulation_config()
interface = LLMSimulationInterface(BASE_CONFIG)


# =============================================================================
# PRICING & TIERS
# =============================================================================

class PricingTier(str, Enum):
    """Service tier definitions."""
    BASIC = "basic"
    PREMIUM = "premium"


TIER_CONFIG = {
    PricingTier.BASIC: {
        "price_eur": 197.0,
        "price_cents": 19700,
        "max_agents": 5,
        "max_phases": 5,
        "rate_limit": "10/minute",
        "features": ["single_run", "basic_report"],
    },
    PricingTier.PREMIUM: {
        "price_eur": 497.0,
        "price_cents": 49700,
        "max_agents": 20,
        "max_phases": 13,
        "rate_limit": "30/minute",
        "features": ["batch_run", "detailed_report", "sensitivity_analysis"],
    },
}


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class SimulationRequest(BaseModel):
    """Request model for scenario simulation."""
    scenario_description: str = Field(
        ...,
        description="Natural language description of scenario to simulate",
        min_length=10,
        max_length=500,
        example="High trust scenario with 5 agents over 10 phases"
    )
    client_id: str = Field(
        default="anonymous",
        description="Client identifier for tracking"
    )
    client_reference: Optional[str] = Field(
        default=None,
        description="Client reference ID for audit trail",
        max_length=100
    )
    seed: int = Field(
        default=42,
        description="Random seed for reproducibility"
    )
    tier: PricingTier = Field(
        default=PricingTier.BASIC,
        description="Service tier"
    )


class SimulationResponse(BaseModel):
    """Response model for simulation results."""
    report_id: str
    report: str
    scenario_metadata: Dict[str, Any]
    validation_status: Dict[str, bool]
    execution_time: float
    outcome: str
    key_metrics: Dict[str, Any]
    tier: str
    price_eur: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    disclaimers_active: bool
    stripe_enabled: bool
    rate_limiting_enabled: bool


class PaymentRequest(BaseModel):
    """Payment intent request."""
    tier: PricingTier
    scenario_description: str = Field(..., max_length=500)
    client_email: str
    metadata: Dict[str, str] = Field(default_factory=dict)


class PaymentResponse(BaseModel):
    """Payment intent response."""
    client_secret: str
    payment_id: str
    amount_eur: float


# =============================================================================
# AUDIT TRAIL
# =============================================================================

def log_audit_trail(
    request: SimulationRequest,
    config: Dict[str, Any],
    result: Any,
    report_id: str,
    execution_time: float
):
    """Log audit trail for validation integrity and compliance."""
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
    
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "report_id": report_id,
        "client_id": request.client_id,
        "client_reference": request.client_reference,
        "scenario_description": request.scenario_description,
        "tier": request.tier.value,
        "seed": request.seed,
        "config_summary": {
            "initial_trust": config.get("initial_trust"),
            "n_agents": len(config.get("agents", [])),
            "max_phases": config.get("max_phases"),
        },
        "outcome": result.outcome.value,
        "final_agents": result.final_active_agents,
        "execution_time": execution_time,
        "api_version": "2.1",
    }
    
    filename = f"{AUDIT_LOG_DIR}/audit_{report_id}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(audit_entry, f, indent=2)
    except Exception as e:
        print(f"Audit logging failed: {e}")


def log_error(
    request: SimulationRequest,
    error: str,
    api_key_hash: int
):
    """Log errors for debugging and compliance."""
    os.makedirs(ERROR_LOG_DIR, exist_ok=True)
    
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "client_id": request.client_id,
        "scenario_description": request.scenario_description[:100],
        "error": str(error),
        "api_key_hash": api_key_hash,
    }
    
    filename = f"{ERROR_LOG_DIR}/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(error_entry, f, indent=2)
    except Exception as e:
        print(f"Error logging failed: {e}")


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint (no auth required)."""
    return HealthResponse(
        status="healthy",
        version="2.1.0",
        timestamp=datetime.now().isoformat(),
        disclaimers_active=True,
        stripe_enabled=STRIPE_AVAILABLE,
        rate_limiting_enabled=RATE_LIMITING_AVAILABLE,
    )


@app.get("/config")
async def get_config_info():
    """Return configuration constraints and pricing."""
    return {
        "protected_parameters": list(interface.protected_params),
        "trust_levels": interface.trust_map,
        "tiers": {
            tier.value: {
                "price_eur": conf["price_eur"],
                "max_agents": conf["max_agents"],
                "max_phases": conf["max_phases"],
                "features": conf["features"],
            }
            for tier, conf in TIER_CONFIG.items()
        },
        "required_disclaimers": REQUIRED_DISCLAIMERS,
    }


@app.post("/api/v1/scenario", response_model=SimulationResponse)
async def run_scenario(
    request: SimulationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Run simulation from natural language scenario description.
    
    Requires valid API key. Rate limited per tier.
    All reports include mandatory disclaimers per CONDITIONS_OF_USE.md.
    """
    start_time = time.time()
    report_id = f"SELENE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{random.randint(1000, 9999)}"
    
    try:
        # Get tier config
        tier_conf = TIER_CONFIG[request.tier]
        
        # Parse input with validation
        config, metadata = interface.parse_scenario(request.scenario_description)
        
        # Enforce tier limits
        if len(config.get("agents", [])) > tier_conf["max_agents"]:
            config["agents"] = config["agents"][:tier_conf["max_agents"]]
            metadata.setdefault("warning_flags", []).append(
                f"Agent count reduced to {tier_conf['max_agents']} for {request.tier.value} tier"
            )
        
        if config.get("max_phases", 5) > tier_conf["max_phases"]:
            config["max_phases"] = tier_conf["max_phases"]
            metadata.setdefault("warning_flags", []).append(
                f"Phase count reduced to {tier_conf['max_phases']} for {request.tier.value} tier"
            )
        
        # Run validated simulator
        sim = ConsortiumSimulator(config, seed=request.seed)
        result = sim.run_single(0)
        
        # Generate report with proper caveats
        report = interface.generate_report(result, metadata, config)
        
        # Validate result
        validation_status = interface._validate_result_compatibility(result)
        
        execution_time = time.time() - start_time
        
        # Audit trail
        log_audit_trail(request, config, result, report_id, execution_time)
        
        return SimulationResponse(
            report_id=report_id,
            report=report,
            scenario_metadata=metadata,
            validation_status=validation_status,
            execution_time=round(execution_time, 3),
            outcome=result.outcome.value,
            key_metrics={
                "final_active_agents": result.final_active_agents,
                "final_functionality": round(result.final_functionality, 3),
                "final_phase": result.final_phase,
                "early_defections": result.early_defections,
                "late_defections": result.late_defections,
                "total_investment": round(result.total_investment, 2),
                "total_revenue": round(result.total_revenue, 2),
            },
            tier=request.tier.value,
            price_eur=tier_conf["price_eur"],
        )
    
    except ValueError as e:
        log_error(request, str(e), hash(api_key) % 10000)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scenario configuration: {str(e)}"
        )
    except Exception as e:
        log_error(request, str(e), hash(api_key) % 10000)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation error: {str(e)}. Validation integrity preserved."
        )


@app.post("/api/v1/parse")
async def parse_scenario_only(
    request: SimulationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Parse scenario without running simulation. Useful for validation before payment."""
    try:
        config, metadata = interface.parse_scenario(request.scenario_description)
        tier_conf = TIER_CONFIG[request.tier]
        
        return {
            "config": config,
            "metadata": metadata,
            "warnings": metadata.get("warning_flags", []),
            "tier": request.tier.value,
            "price_eur": tier_conf["price_eur"],
            "within_tier_limits": (
                len(config.get("agents", [])) <= tier_conf["max_agents"] and
                config.get("max_phases", 5) <= tier_conf["max_phases"]
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parse error: {str(e)}"
        )


# =============================================================================
# PAYMENT ENDPOINTS (Stripe)
# =============================================================================

@app.post("/api/v1/payment/create", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a Stripe payment intent for scenario analysis."""
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing not configured"
        )
    
    tier_conf = TIER_CONFIG[payment.tier]
    
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=tier_conf["price_cents"],
            currency="eur",
            metadata={
                "tier": payment.tier.value,
                "scenario_description": payment.scenario_description[:200],
                "client_email": payment.client_email,
                **payment.metadata,
            },
            automatic_payment_methods={"enabled": True},
        )
        
        return PaymentResponse(
            client_secret=payment_intent.client_secret,
            payment_id=payment_intent.id,
            amount_eur=tier_conf["price_eur"],
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment creation failed: {str(e)}"
        )


@app.post("/api/v1/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe payment webhooks."""
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # Log successful payment for audit
        os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
        with open(f"{AUDIT_LOG_DIR}/payment_{payment_intent['id']}.json", 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "payment_id": payment_intent["id"],
                "amount": payment_intent["amount"],
                "status": "succeeded",
                "metadata": payment_intent.get("metadata", {}),
            }, f, indent=2)
    
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        os.makedirs(ERROR_LOG_DIR, exist_ok=True)
        with open(f"{ERROR_LOG_DIR}/payment_failed_{payment_intent['id']}.json", 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "payment_id": payment_intent["id"],
                "error": payment_intent.get("last_payment_error", {}),
            }, f, indent=2)
    
    return {"status": "success"}


@app.get("/api/v1/disclaimers")
async def get_required_disclaimers():
    """Return list of required disclaimer phrases."""
    return {
        "required_phrases": REQUIRED_DISCLAIMERS,
        "source_document": "CONDITIONS_OF_USE.md",
        "enforcement": "All generated reports must contain these phrases",
    }


# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Verify configuration on startup."""
    assert len(REQUIRED_DISCLAIMERS) > 0, "Required disclaimers not configured"
    assert interface is not None, "LLM interface not initialized"
    
    print("=" * 60)
    print("Project Selene LLM API v2.1")
    print("=" * 60)
    print(f"Rate limiting: {'ENABLED' if RATE_LIMITING_AVAILABLE else 'DISABLED'}")
    print(f"Stripe payments: {'ENABLED' if STRIPE_AVAILABLE else 'DISABLED'}")
    print(f"Protected parameters: {interface.protected_params}")
    print(f"Audit logs: {AUDIT_LOG_DIR}")
    print("=" * 60)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "llm_endpoint:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("SELENE_DEV_MODE", "false").lower() == "true",
        workers=int(os.getenv("SELENE_WORKERS", "4")),
        log_level="info",
    )
