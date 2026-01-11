"""
Selene Bilateral Friction Extension
====================================

Agent-based model for simulating graduated economic friction
between interdependent states.

Key difference from base selene_sim:
- Actions are continuous (0-100% intensity per sector)
- Sector-specific dependencies with asymmetric substitutability
- Third party interventions
- Signaling vs substance dynamics

Usage:
    from selene_bilateral import create_japan_china_simulator, run_batch
    
    # Single run
    sim = create_japan_china_simulator()
    metrics = sim.run()
    print(metrics.outcome_category)
    
    # Batch run
    results = run_batch(num_runs=100)
    print(results["outcome_distribution"])
"""

from .state_agent import (
    StateAgent,
    RegimeType,
    PainAssessment,
    create_state_from_config,
)

from .sectors import (
    SectorDependency,
    DependencyMatrix,
    create_japan_china_matrix,
    JAPAN_CHINA_SECTORS,
)

from .actions import (
    FrictionAction,
    ActionType,
    Rationale,
    ActionSpace,
    create_japan_china_action_space,
    JAPAN_CHINA_ACTIONS,
)

from .third_party import (
    ThirdParty,
    ThirdPartySystem,
    create_japan_china_third_parties,
    JAPAN_CHINA_THIRD_PARTIES,
)

from .shocks import (
    BilateralShock,
    BilateralShockType,
    BilateralShockGenerator,
)

from .bilateral_sim import (
    BilateralFrictionSimulator,
    OutcomeCategory,
    SimulationMetrics,
    StepRecord,
    create_japan_china_simulator,
    run_batch,
)

__version__ = "0.1.0"
__all__ = [
    # State agents
    "StateAgent",
    "RegimeType",
    "PainAssessment",
    "create_state_from_config",
    
    # Sectors
    "SectorDependency",
    "DependencyMatrix",
    "create_japan_china_matrix",
    "JAPAN_CHINA_SECTORS",
    
    # Actions
    "FrictionAction",
    "ActionType",
    "Rationale",
    "ActionSpace",
    "create_japan_china_action_space",
    "JAPAN_CHINA_ACTIONS",
    
    # Third parties
    "ThirdParty",
    "ThirdPartySystem",
    "create_japan_china_third_parties",
    "JAPAN_CHINA_THIRD_PARTIES",
    
    # Shocks
    "BilateralShock",
    "BilateralShockType",
    "BilateralShockGenerator",
    
    # Simulator
    "BilateralFrictionSimulator",
    "OutcomeCategory",
    "SimulationMetrics",
    "StepRecord",
    "create_japan_china_simulator",
    "run_batch",
]

# Upgraded simulator with de-escalation dynamics
from selene_bilateral.upgraded_simulator import (
    UpgradedBilateralSimulator,
    StepRecord,
    SimulationResult,
)

from selene_bilateral.deescalation_dynamics import (
    DeescalationIncentiveCalculator,
    TimeDecayCosts,
    InternationalPressure,
    EconomicFatigue,
    ReputationBleeding,
)
