"""
Project Selene Consortium Simulator v2.0
========================================

An agent-based model for stress-testing multilateral cooperation frameworks.

Core modules:
- agent: Heterogeneous consortium participants
- dependency_chain: Technical interdependency graphs
- shocks: External political/economic disruptions
- simulation: Main orchestration engine

Usage:
    from selene_sim import ConsortiumSimulator, summarize_results
    
    config = load_config("scenarios/selene_default.yaml")
    sim = ConsortiumSimulator(config)
    results = sim.run_batch(n_runs=100)
    summary = summarize_results(results)
"""

from .agent import (
    ConsortiumAgent,
    AgentType,
    AgentProfile,
    create_agent_from_config,
)
from .dependency_chain import (
    DependencyChain,
    DependencyNode,
    create_selene_dependency_chain,
)
from .shocks import (
    ShockGenerator,
    ExternalShock,
    ShockType,
    create_shock_generator,
)
from .simulation import (
    ConsortiumSimulator,
    SimulationResult,
    OutcomeCategory,
    summarize_results,
)

__version__ = "2.0.0"
__all__ = [
    # Agent
    "ConsortiumAgent",
    "AgentType", 
    "AgentProfile",
    "create_agent_from_config",
    # Dependency Chain
    "DependencyChain",
    "DependencyNode",
    "create_selene_dependency_chain",
    # Shocks
    "ShockGenerator",
    "ExternalShock",
    "ShockType",
    "create_shock_generator",
    # Simulation
    "ConsortiumSimulator",
    "SimulationResult",
    "OutcomeCategory",
    "summarize_results",
]
