# Selene Bilateral Friction Extension

Agent-based model for simulating graduated economic friction between interdependent states.

## Overview

This extension to the Selene ABM framework models bilateral trade disputes with:

- **Graduated actions** (0-100% intensity per sector, not binary)
- **Asymmetric dependencies** (Japan's rare earth dependence ≠ China's semiconductor equipment dependence)
- **Substitutability timers** (how long to find alternatives)
- **Third party interventions** (US, EU, ASEAN dynamics)
- **Signaling vs substance** distinction
- **Diversification dynamics** (supply chain de-risking over time)

## Quick Start

```bash
# Install dependencies
pip install pyyaml

# Run default Japan-China scenario (100 runs)
python run_bilateral.py

# Run with custom config
python run_bilateral.py -c selene_bilateral/config/japan_china_high_tension.yaml

# Compare all scenarios
python run_bilateral.py --compare

# Single detailed run
python run_bilateral.py --single -v
```

## Outcome Categories

| Category | Definition |
|----------|------------|
| **Stable Interdependence** | Friction < 0.2 after 24 months |
| **Managed Competition** | Friction 0.2-0.5, stable plateau |
| **Gradual Decoupling** | Both sides diversify > 60% |
| **Escalation Spiral** | Friction > 0.7, still rising |
| **Asymmetric Lock-in** | One diversifies, other doesn't |
| **Normalization** | Friction returns to < 0.1 |
| **Political Rupture** | Domestic crisis ends simulation |

## Key Components

### StateAgent (`state_agent.py`)
Sovereign states with:
- Economic fundamentals (GDP, trade openness)
- Political state (regime type, approval, nationalism)
- Decision parameters (escalation/de-escalation thresholds)
- Graduated restriction intensity per sector

### DependencyMatrix (`sectors.py`)
Bilateral trade structure:
- Sector-specific trade flows ($ billions)
- Substitution times and costs
- Criticality scores (downstream effects)
- Political salience (voter visibility)

### ActionSpace (`actions.py`)
Available policy moves:
- Export controls, import bans, tariffs
- Investment screening, visa restrictions
- Each with self-harm coefficient and signal strength

### ThirdPartySystem (`third_party.py`)
External actors (US, EU, ASEAN):
- Alignment coefficients
- Alternative supply capacity
- Mediation effectiveness
- Intervention thresholds

### BilateralShockGenerator (`shocks.py`)
External events:
- Territorial incidents, military exercises
- Elections, leadership changes
- Economic recessions, commodity spikes
- Historical anniversaries

## Configuration

See `selene_bilateral/config/` for example YAML configs:

```yaml
state_a:
  nationalism_index: 0.5
  escalation_threshold: 0.35
  retaliation_propensity: 0.6

state_b:
  nationalism_index: 0.6
  escalation_threshold: 0.3
  retaliation_propensity: 0.75

shock_probabilities:
  territorial_incident: 0.02
  military_exercise: 0.05
```

## Integration with Base Selene

This extension can run standalone or integrate with the base consortium simulator:

```python
from selene_sim import ConsortiumSimulator
from selene_bilateral import BilateralFrictionSimulator

# Bilateral friction affects consortium trust
# Consortium participation affects bilateral exit costs
```

See spec Section 8 for integration architecture.

## Validation Approach

1. **Historical calibration**: 2010 rare earth crisis, 2012 island standoff, 2019 Japan-Korea dispute
2. **Sensitivity analysis**: Sweep nationalism, third party thresholds, substitution times
3. **Expert validation**: Run past Japan/China trade policy researchers

## Limitations

This model **cannot**:
- Predict specific GDP impacts with confidence intervals
- Forecast timing of specific events
- Model individual firm decisions

This model **can**:
- Identify escalation paths leading to lock-in
- Test sensitivity to key parameters
- Compare scenarios (with/without third party coordination)
- Generate structured questions for expert judgment

## File Structure

```
selene_bilateral/
├── __init__.py
├── state_agent.py       # StateAgent with graduated actions
├── sectors.py           # SectorDependency, DependencyMatrix
├── actions.py           # FrictionAction, ActionSpace
├── third_party.py       # ThirdParty intervention logic
├── shocks.py            # BilateralShockGenerator
├── bilateral_sim.py     # Main simulator
└── config/
    ├── japan_china_default.yaml
    ├── japan_china_high_tension.yaml
    └── japan_china_stabilization.yaml

run_bilateral.py         # CLI runner
```

## License

MIT License - See LICENSE file
