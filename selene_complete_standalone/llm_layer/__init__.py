"""
LLM Layer for Project Selene ABM Suite v2.1

Provides natural language interface to simulation.
Core version without commercial endpoint features.
"""

from .llm_interface import LLMSimulationInterface, REQUIRED_DISCLAIMERS
from .config_factory import make_simulation_config

__all__ = [
    "LLMSimulationInterface",
    "REQUIRED_DISCLAIMERS", 
    "make_simulation_config",
]
