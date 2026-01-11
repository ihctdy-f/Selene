"""
Configuration Factory for Project Selene ABM Suite v2.1

Provides standardized simulation configuration generation.
Extracted from test suite for reuse in LLM layer.
"""

import random
from typing import Dict, Any, List


def make_simulation_config(
    n_agents: int = 5,
    initial_trust: float = 0.5,
    trust_variance: float = 0.0,
    disable_shocks: bool = False,
    poison_pill_threshold: int = 2,
    max_phases: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a simulation configuration dictionary.
    
    This mirrors the YAML config structure used by ConsortiumSimulator.
    
    Args:
        n_agents: Number of consortium agents (1-5)
        initial_trust: Base trust level for all agents (0.0-1.0)
        trust_variance: Gaussian variance applied to individual agent trust
        disable_shocks: If True, disables all external shock generation
        poison_pill_threshold: Minimum agents required for consortium survival
        max_phases: Number of simulation phases to run
        **kwargs: Additional config overrides
    
    Returns:
        Configuration dictionary compatible with ConsortiumSimulator
    """
    # Standard agent composition
    agent_types = [
        ("eu_esa", "EU/ESA", "track_a_core"),
        ("china_cnsa", "China/CNSA", "track_b_core"),
        ("russia_ros", "Russia/Roscosmos", "track_b_core"),
        ("india_isro", "India/ISRO", "associate"),
        ("uae_mbrsc", "UAE/MBRSC", "associate"),
    ]
    
    agents = []
    for i, (agent_id, name, agent_type) in enumerate(agent_types[:n_agents]):
        # Apply trust with optional variance
        trust = initial_trust
        if trust_variance > 0:
            trust = max(0.0, min(1.0, initial_trust + random.gauss(0, trust_variance)))
        
        agents.append({
            "agent_id": agent_id,
            "name": name,
            "agent_type": agent_type,
            "equity_share": 1.0 / n_agents,
            "initial_trust": trust,
            "initial_approval": 0.6,
            "initial_stability": 0.7,
        })
    
    config = {
        "agents": agents,
        "max_phases": max_phases,
        "poison_pill_threshold": poison_pill_threshold,
        "cascade_on_withdrawal": True,
        "max_sunk_cost": 50.0,
        "defection_floor": 0.02,
        "defection_ceiling": 0.95,
        "trust_modifier": 0.0,
        "initial_trust": initial_trust,  # Store for report generation
        "shocks": {
            "enabled": not disable_shocks,
            "election_probability": 0.0 if disable_shocks else 0.25,
            "economic_probability": 0.0 if disable_shocks else 0.15,
            "technical_probability": 0.0 if disable_shocks else 0.10,
        },
    }
    
    # Apply any additional overrides (but protect critical params)
    protected = {"poison_pill_threshold", "defection_floor", "defection_ceiling", 
                 "cascade_on_withdrawal", "max_sunk_cost"}
    
    for key, value in kwargs.items():
        if key not in protected:
            config[key] = value
    
    return config


def get_default_agent_configs() -> List[Dict[str, Any]]:
    """
    Return default agent configuration list.
    Useful for understanding standard consortium composition.
    """
    return [
        {
            "agent_id": "eu_esa",
            "name": "EU/ESA",
            "agent_type": "track_a_core",
            "description": "European Space Agency - Track A founder, democratic accountability",
        },
        {
            "agent_id": "china_cnsa",
            "name": "China/CNSA",
            "agent_type": "track_b_core",
            "description": "China National Space Administration - Track B core, multipolar track",
        },
        {
            "agent_id": "russia_ros",
            "name": "Russia/Roscosmos",
            "agent_type": "track_b_core",
            "description": "Roscosmos - Track B core, sanctions exposure",
        },
        {
            "agent_id": "india_isro",
            "name": "India/ISRO",
            "agent_type": "associate",
            "description": "Indian Space Research Organisation - Associate member, ROI-driven",
        },
        {
            "agent_id": "uae_mbrsc",
            "name": "UAE/MBRSC",
            "agent_type": "associate",
            "description": "Mohammed Bin Rashid Space Centre - Associate member, can switch tracks",
        },
    ]
