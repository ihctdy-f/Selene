"""
FastAPI endpoint for LLM-mediated simulation access.
CORE VERSION - No commercial features (Stripe, rate limiting, pricing tiers).

Run with: uvicorn llm_endpoint_core:app --reload
"""

import os
import json
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selene_sim.simulation import ConsortiumSimulator, OutcomeCategory

from .llm_interface import LLMSimulationInterface, REQUIRED_DISCLAIMERS
from .config_factory import make_simulation_config


# =============================================================================
# CONFIGURATION
# =============================================================================

AUDIT_LOG_DIR = os.getenv("SELENE_AUDIT_DIR", "audit_logs")
ERROR_LOG_DIR = os.getenv("SELENE_ERROR_DIR", "error_logs")


# =============================================================================
# APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="Project Selene LLM API (Core)",
    description="Natural language interface to Project Selene ABM Suite v2.1",
    version="2.1.0-core",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize interface
BASE_CONFIG = make_simulation_config()
interface = LLMSimulationInterface(BASE_CONFIG)


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


class SimulationResponse(BaseModel):
    """Response model for simulation results."""
    report_id: str
    report: str
    scenario_metadata: Dict[str, Any]
    validation_status: Dict[str, bool]
    execution_time: float
    outcome: str
    key_metrics: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    disclaimers_active: bool


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
    """Log audit trail for validation integrity."""
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
    
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "report_id": report_id,
        "client_id": request.client_id,
        "client_reference": request.client_reference,
        "scenario_description": request.scenario_description,
        "seed": request.seed,
        "config_summary": {
            "initial_trust": config.get("initial_trust"),
            "n_agents": len(config.get("agents", [])),
            "max_phases": config.get("max_phases"),
        },
        "outcome": result.outcome.value,
        "final_agents": result.final_active_agents,
        "execution_time": execution_time,
        "api_version": "2.1-core",
    }
    
    filename = f"{AUDIT_LOG_DIR}/audit_{report_id}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(audit_entry, f, indent=2)
    except Exception as e:
        print(f"Audit logging failed: {e}")


def log_error(request: SimulationRequest, error: str):
    """Log errors for debugging."""
    os.makedirs(ERROR_LOG_DIR, exist_ok=True)
    
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "client_id": request.client_id,
        "scenario_description": request.scenario_description[:100],
        "error": str(error),
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
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.1.0-core",
        timestamp=datetime.now().isoformat(),
        disclaimers_active=True,
    )


@app.get("/config")
async def get_config_info():
    """Return configuration constraints."""
    return {
        "protected_parameters": list(interface.protected_params),
        "trust_levels": interface.trust_map,
        "required_disclaimers": REQUIRED_DISCLAIMERS,
    }


@app.post("/api/v1/scenario", response_model=SimulationResponse)
async def run_scenario(request: SimulationRequest):
    """
    Run simulation from natural language scenario description.
    
    All reports include mandatory disclaimers per CONDITIONS_OF_USE.md.
    """
    start_time = time.time()
    report_id = f"SELENE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{random.randint(1000, 9999)}"
    
    try:
        # Parse input with validation
        config, metadata = interface.parse_scenario(request.scenario_description)
        
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
        )
    
    except ValueError as e:
        log_error(request, str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scenario configuration: {str(e)}"
        )
    except Exception as e:
        log_error(request, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation error: {str(e)}. Validation integrity preserved."
        )


@app.post("/api/v1/parse")
async def parse_scenario_only(request: SimulationRequest):
    """Parse scenario without running simulation. Useful for validation."""
    try:
        config, metadata = interface.parse_scenario(request.scenario_description)
        
        return {
            "config": config,
            "metadata": metadata,
            "warnings": metadata.get("warning_flags", []),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parse error: {str(e)}"
        )


@app.get("/api/v1/disclaimers")
async def get_required_disclaimers():
    """Return list of required disclaimer phrases."""
    return {
        "required_phrases": REQUIRED_DISCLAIMERS,
        "source_document": "CONDITIONS_OF_USE.md",
        "enforcement": "All generated reports must contain these phrases",
    }


# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Verify configuration on startup."""
    assert len(REQUIRED_DISCLAIMERS) > 0, "Required disclaimers not configured"
    assert interface is not None, "LLM interface not initialized"
    
    print("=" * 60)
    print("Project Selene LLM API v2.1 (Core)")
    print("=" * 60)
    print(f"Protected parameters: {interface.protected_params}")
    print(f"Audit logs: {AUDIT_LOG_DIR}")
    print("=" * 60)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "llm_endpoint_core:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("SELENE_DEV_MODE", "false").lower() == "true",
        log_level="info",
    )
