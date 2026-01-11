# LLM Layer for Project Selene ABM Suite

Natural language interface for the simulation framework.

## Contents

| File | Purpose |
|------|---------|
| `llm_interface.py` | Core: NL→config parsing, report generation |
| `config_factory.py` | Core: Simulation config factory |
| `llm_endpoint_core.py` | **Stripped endpoint** - no auth/payments |
| `llm_endpoint.py` | Full endpoint with Stripe, rate limiting, API keys |

## Quick Start (Core Version)

```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Run
cd selene_complete_standalone
uvicorn llm_layer.llm_endpoint_core:app --reload
```

Then visit `http://localhost:8000/docs` for interactive API.

## Quick Start (Full Version)

```bash
# Install dependencies
pip install fastapi uvicorn pydantic stripe slowapi

# Set environment variables (optional - graceful degradation if missing)
export SELENE_API_KEY="your-api-key"
export STRIPE_SECRET_KEY="sk_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Run
uvicorn llm_layer.llm_endpoint:app --reload
```

## Usage Example

```python
from llm_layer import LLMSimulationInterface

interface = LLMSimulationInterface()
result, report = interface.run_scenario("High trust scenario with 5 agents")
print(report)
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/config` | GET | Show protected params, trust levels |
| `/api/v1/scenario` | POST | Run simulation from NL description |
| `/api/v1/parse` | POST | Parse scenario without running |
| `/api/v1/disclaimers` | GET | Required disclaimer phrases |

Full version adds:
| `/api/v1/payment/create` | POST | Stripe payment intent |
| `/api/v1/webhook/stripe` | POST | Stripe webhook handler |

## Version Notes

- **Core** (`llm_endpoint_core.py`): No authentication, no payments, no rate limiting. Good for internal use, testing, development.
- **Full** (`llm_endpoint.py`): API key auth, Stripe payments, rate limiting. Features gracefully degrade if not configured.
