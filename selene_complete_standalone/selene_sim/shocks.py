"""
External Shocks module for Project Selene Consortium Simulator v2.0
Generates political, economic, and technical disruptions.

From OpinionStressTests.txt:
"External shocks: Probabilistic events like sanctions imposition, 
leadership change, or technical delay"
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class ShockType(Enum):
    """Categories of external shocks."""
    ELECTION = "election"                   # Leadership change
    ECONOMIC_CRISIS = "economic_crisis"     # Recession, currency crisis
    TECHNICAL_FAILURE = "technical_failure" # ISRU fails, launch failure
    SANCTIONS = "sanctions"                 # New sanctions imposed
    GEOPOLITICAL = "geopolitical"          # War, territorial dispute
    PUBLIC_SCANDAL = "public_scandal"       # Corruption, safety incident


@dataclass
class ExternalShock:
    """A single shock event."""
    shock_type: ShockType
    target_agent_id: Optional[str]          # None = affects all
    intensity: float                         # 0-1
    phase: int                               # When it occurred
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.shock_type.value,
            "target": self.target_agent_id,
            "intensity": round(self.intensity, 3),
            "phase": self.phase,
            "description": self.description,
        }


class ShockGenerator:
    """
    Generates external shocks based on scenario parameters.
    
    Shocks can be:
    - Targeted (affects one agent)
    - Global (affects all agents)
    - System-level (affects project itself)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Base probabilities per phase (can override in config)
        self.election_prob = config.get("election_probability", 0.20)
        self.economic_prob = config.get("economic_crisis_probability", 0.10)
        self.technical_prob = config.get("technical_failure_probability", 0.08)
        self.sanctions_prob = config.get("sanctions_probability", 0.05)
        self.geopolitical_prob = config.get("geopolitical_probability", 0.03)
        self.scandal_prob = config.get("scandal_probability", 0.05)
        
        # Intensity ranges
        self.intensity_min = config.get("shock_intensity_min", 0.2)
        self.intensity_max = config.get("shock_intensity_max", 0.8)
        
        # Agent-specific vulnerability (optional override)
        self.agent_vulnerabilities = config.get("agent_vulnerabilities", {})
    
    def generate_shocks(
        self,
        phase: int,
        active_agents: List[str],
        global_state: Dict[str, Any]
    ) -> List[ExternalShock]:
        """
        Generate shocks for a single phase.
        
        Returns list of shocks that occurred.
        """
        shocks = []
        
        # Phase-based modifiers
        # Early phases more volatile (less committed)
        # Late phases more stable (more invested)
        phase_volatility = max(0.5, 1.5 - (phase * 0.1))
        
        # Election shocks (targeted)
        if random.random() < self.election_prob * phase_volatility:
            target = random.choice(active_agents)
            intensity = random.uniform(self.intensity_min, self.intensity_max)
            
            # Apply agent-specific vulnerability
            vuln = self.agent_vulnerabilities.get(target, {}).get("election", 1.0)
            intensity *= vuln
            
            shocks.append(ExternalShock(
                shock_type=ShockType.ELECTION,
                target_agent_id=target,
                intensity=min(1.0, intensity),
                phase=phase,
                description=f"Leadership transition in {target}",
            ))
        
        # Economic crisis (can be targeted or global)
        if random.random() < self.economic_prob * phase_volatility:
            # 30% chance of global crisis
            if random.random() < 0.3:
                target = None
                desc = "Global economic downturn"
            else:
                target = random.choice(active_agents)
                desc = f"Economic stress in {target}"
            
            intensity = random.uniform(self.intensity_min, self.intensity_max)
            
            shocks.append(ExternalShock(
                shock_type=ShockType.ECONOMIC_CRISIS,
                target_agent_id=target,
                intensity=intensity,
                phase=phase,
                description=desc,
            ))
        
        # Technical failure (system-level)
        if random.random() < self.technical_prob:
            # More likely in build phases (3-8)
            if 3 <= phase <= 8:
                intensity = random.uniform(0.3, 0.7)
                systems = ["ISRU demo", "launch vehicle", "habitat deployment", 
                          "comms relay", "power system"]
                failed_system = random.choice(systems)
                
                shocks.append(ExternalShock(
                    shock_type=ShockType.TECHNICAL_FAILURE,
                    target_agent_id=None,  # Affects whole project
                    intensity=intensity,
                    phase=phase,
                    description=f"Technical setback: {failed_system}",
                ))
        
        # Sanctions (targeted, mainly affects Track B)
        if random.random() < self.sanctions_prob * phase_volatility:
            # More likely to target Track B core
            track_b_agents = [a for a in active_agents 
                            if "russia" in a.lower() or "china" in a.lower()]
            if track_b_agents:
                target = random.choice(track_b_agents)
                intensity = random.uniform(0.4, 0.9)
                
                shocks.append(ExternalShock(
                    shock_type=ShockType.SANCTIONS,
                    target_agent_id=target,
                    intensity=intensity,
                    phase=phase,
                    description=f"New sanctions affecting {target}",
                ))
        
        # Geopolitical event
        if random.random() < self.geopolitical_prob:
            intensity = random.uniform(0.5, 1.0)
            events = ["border incident", "diplomatic crisis", 
                     "territorial dispute", "alliance shift"]
            
            shocks.append(ExternalShock(
                shock_type=ShockType.GEOPOLITICAL,
                target_agent_id=None,
                intensity=intensity,
                phase=phase,
                description=f"Geopolitical event: {random.choice(events)}",
            ))
        
        # Public scandal (targeted)
        if random.random() < self.scandal_prob:
            target = random.choice(active_agents)
            intensity = random.uniform(0.3, 0.7)
            
            shocks.append(ExternalShock(
                shock_type=ShockType.PUBLIC_SCANDAL,
                target_agent_id=target,
                intensity=intensity,
                phase=phase,
                description=f"Public controversy involving {target}",
            ))
        
        return shocks
    
    def apply_shocks_to_agents(
        self,
        shocks: List[ExternalShock],
        agents: Dict[str, Any],  # agent_id -> ConsortiumAgent
        global_state: Dict[str, Any]
    ):
        """
        Apply generated shocks to agent states.
        Modifies agents in place.
        """
        for shock in shocks:
            if shock.target_agent_id:
                # Targeted shock
                if shock.target_agent_id in agents:
                    agent = agents[shock.target_agent_id]
                    self._apply_shock_to_agent(shock, agent)
            else:
                # Global shock
                for agent in agents.values():
                    if agent.active:
                        self._apply_shock_to_agent(shock, agent, global_modifier=True)
            
            # Update global state
            self._apply_shock_to_global(shock, global_state)
    
    def _apply_shock_to_agent(
        self,
        shock: ExternalShock,
        agent: Any,
        global_modifier: bool = False
    ):
        """Apply shock effects to a single agent."""
        intensity = shock.intensity
        if global_modifier:
            intensity *= 0.5  # Global shocks hit everyone but less hard
        
        if shock.shock_type == ShockType.ELECTION:
            # Leadership change: affects stability and possibly approval
            agent.update_domestic_state(
                stability_delta=-intensity * 0.4,
                approval_delta=random.uniform(-0.2, 0.1) * intensity
            )
            agent.update_trust(-intensity * 0.1)
        
        elif shock.shock_type == ShockType.ECONOMIC_CRISIS:
            # Economic stress: affects approval and trust
            agent.update_domestic_state(approval_delta=-intensity * 0.3)
            agent.update_trust(-intensity * 0.15)
        
        elif shock.shock_type == ShockType.TECHNICAL_FAILURE:
            # Technical setback: affects trust in project
            agent.update_trust(-intensity * 0.2)
            agent.update_domestic_state(approval_delta=-intensity * 0.1)
        
        elif shock.shock_type == ShockType.SANCTIONS:
            # Sanctions: major trust and approval hit
            agent.update_trust(-intensity * 0.3)
            agent.update_domestic_state(
                approval_delta=-intensity * 0.2,
                stability_delta=-intensity * 0.1
            )
        
        elif shock.shock_type == ShockType.GEOPOLITICAL:
            # Geopolitical: trust damage
            agent.update_trust(-intensity * 0.25)
        
        elif shock.shock_type == ShockType.PUBLIC_SCANDAL:
            # Scandal: approval hit
            agent.update_domestic_state(approval_delta=-intensity * 0.35)
    
    def _apply_shock_to_global(
        self,
        shock: ExternalShock,
        global_state: Dict[str, Any]
    ):
        """Update global state based on shock."""
        # Accumulate volatility
        current_volatility = global_state.get("political_volatility", 0.0)
        
        if shock.shock_type in [ShockType.GEOPOLITICAL, ShockType.SANCTIONS]:
            global_state["political_volatility"] = min(1.0, current_volatility + shock.intensity * 0.3)
        elif shock.shock_type == ShockType.ECONOMIC_CRISIS:
            global_state["economic_stress"] = min(1.0, 
                global_state.get("economic_stress", 0.0) + shock.intensity * 0.4)
        elif shock.shock_type == ShockType.TECHNICAL_FAILURE:
            global_state["technical_risk"] = min(1.0,
                global_state.get("technical_risk", 0.0) + shock.intensity * 0.2)


def create_shock_generator(config: Optional[Dict[str, Any]] = None) -> ShockGenerator:
    """Factory with sensible defaults."""
    default_config = {
        "election_probability": 0.20,
        "economic_crisis_probability": 0.10,
        "technical_failure_probability": 0.08,
        "sanctions_probability": 0.05,
        "geopolitical_probability": 0.03,
        "scandal_probability": 0.05,
        "shock_intensity_min": 0.2,
        "shock_intensity_max": 0.8,
    }
    if config:
        default_config.update(config)
    return ShockGenerator(default_config)
