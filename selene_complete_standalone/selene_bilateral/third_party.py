"""
Third Party module for Selene Bilateral Friction Extension
Handles external actor intervention in bilateral disputes.

Third parties can:
- Provide alternative supply (reducing target's pain)
- Coordinate sanctions/support (amplifying pressure)
- Offer mediation (de-escalation pathways)
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import random


@dataclass
class ThirdParty:
    """
    External actor that can influence bilateral friction.
    
    Examples: USA, EU, ASEAN in Japan-China dispute
    """
    
    party_id: str                           # e.g., "USA", "EU", "ASEAN"
    name: str
    
    # Alignment (-1 to 1: negative=aligned with B, positive=aligned with A)
    alignment_with_a: float = 0.0
    
    # Intervention capabilities
    coordination_bonus: float = 0.2         # Boost to aligned party's position
    alternative_supply_capacity: float = 0.2  # Can replace X% of restricted goods
    market_access_leverage: float = 0.2     # Economic pressure capability
    mediation_effectiveness: float = 0.3    # De-escalation influence
    
    # Activation thresholds
    intervention_threshold: float = 0.4     # Friction level that triggers involvement
    
    # State tracking
    active: bool = False
    intervention_step: Optional[int] = None
    cumulative_cost: float = 0.0            # Cost of intervention to third party
    
    def check_activation(
        self,
        friction_level: float,
        step: int,
        config: Dict[str, Any]
    ) -> bool:
        """
        Decide whether to activate based on friction level.
        
        Returns True if newly activating this step.
        """
        if self.active:
            return False
        
        # Base probability from threshold
        if friction_level >= self.intervention_threshold:
            activation_prob = (friction_level - self.intervention_threshold) / (1 - self.intervention_threshold)
            activation_prob *= config.get("third_party_activation_multiplier", 1.0)
            
            # Add noise
            if random.random() < activation_prob:
                self.active = True
                self.intervention_step = step
                return True
        
        return False
    
    def check_deactivation(
        self,
        friction_level: float,
        step: int,
        config: Dict[str, Any]
    ) -> bool:
        """
        Check if third party withdraws from involvement.
        
        Returns True if deactivating.
        """
        if not self.active:
            return False
        
        # Deactivate if friction drops significantly
        deactivation_threshold = self.intervention_threshold * 0.5
        
        if friction_level < deactivation_threshold:
            cooldown = config.get("third_party_cooldown", 6)
            if step - self.intervention_step >= cooldown:
                if random.random() < 0.3:  # 30% chance per step below threshold
                    self.active = False
                    return True
        
        return False
    
    def calculate_support_effect(
        self,
        target: str,  # "A" or "B"
        friction_level: float,
        config: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate support provided to aligned party.
        
        Returns dict with various support metrics.
        """
        if not self.active:
            return {"coordination": 0.0, "supply": 0.0, "pressure": 0.0}
        
        # Check alignment
        if target == "A" and self.alignment_with_a > 0:
            alignment_strength = self.alignment_with_a
        elif target == "B" and self.alignment_with_a < 0:
            alignment_strength = -self.alignment_with_a
        else:
            # Neutral or wrong alignment
            return {"coordination": 0.0, "supply": 0.0, "pressure": 0.0}
        
        # Scale support by alignment strength and friction level
        intensity = alignment_strength * friction_level
        
        return {
            "coordination": self.coordination_bonus * intensity,
            "supply": self.alternative_supply_capacity * intensity,
            "pressure": self.market_access_leverage * intensity,
        }
    
    def apply_cost(self, cost: float):
        """Record cost of intervention."""
        self.cumulative_cost += cost
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "party_id": self.party_id,
            "name": self.name,
            "alignment_with_a": self.alignment_with_a,
            "active": self.active,
            "intervention_step": self.intervention_step,
            "cumulative_cost": round(self.cumulative_cost, 4),
        }


class ThirdPartySystem:
    """
    Manages all third party actors and their aggregate effects.
    """
    
    def __init__(self):
        self.parties: Dict[str, ThirdParty] = {}
    
    def add_party(self, party: ThirdParty):
        """Add a third party to the system."""
        self.parties[party.party_id] = party
    
    def load_from_config(self, parties_config: List[Dict[str, Any]]):
        """Load third parties from YAML config."""
        for pc in parties_config:
            party = ThirdParty(
                party_id=pc["party_id"],
                name=pc.get("name", pc["party_id"]),
                alignment_with_a=pc.get("alignment_with_a", 0.0),
                coordination_bonus=pc.get("coordination_bonus", 0.2),
                alternative_supply_capacity=pc.get("alternative_supply_capacity", 0.2),
                market_access_leverage=pc.get("market_access_leverage", 0.2),
                mediation_effectiveness=pc.get("mediation_effectiveness", 0.3),
                intervention_threshold=pc.get("intervention_threshold", 0.4),
            )
            self.add_party(party)
    
    def update_activations(
        self,
        friction_level: float,
        step: int,
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Update all third party activation states.
        
        Returns list of newly activated party IDs.
        """
        newly_activated = []
        
        for party in self.parties.values():
            if party.check_activation(friction_level, step, config):
                newly_activated.append(party.party_id)
            party.check_deactivation(friction_level, step, config)
        
        return newly_activated
    
    def get_aggregate_support(
        self,
        target: str,
        friction_level: float,
        config: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Get total third party support for target state.
        """
        total_coordination = 0.0
        total_supply = 0.0
        total_pressure = 0.0
        
        for party in self.parties.values():
            support = party.calculate_support_effect(target, friction_level, config)
            total_coordination += support["coordination"]
            total_supply += support["supply"]
            total_pressure += support["pressure"]
        
        return {
            "coordination": total_coordination,
            "supply": min(1.0, total_supply),  # Cap at 100% alternative supply
            "pressure": total_pressure,
        }
    
    def get_active_parties(self) -> List[str]:
        """Get list of currently active third parties."""
        return [p.party_id for p in self.parties.values() if p.active]
    
    def calculate_mediation_potential(self, config: Dict[str, Any]) -> float:
        """
        Calculate aggregate mediation potential from active parties.
        
        Higher = more likely de-escalation pathways exist.
        """
        if not self.parties:
            return 0.0
        
        # Active neutral parties contribute most
        mediation = 0.0
        for party in self.parties.values():
            if party.active:
                # More neutral = better mediator
                neutrality = 1 - abs(party.alignment_with_a)
                mediation += party.mediation_effectiveness * neutrality
        
        return min(1.0, mediation)
    
    def reset(self):
        """Reset all parties to initial state."""
        for party in self.parties.values():
            party.active = False
            party.intervention_step = None
            party.cumulative_cost = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "parties": {pid: p.to_dict() for pid, p in self.parties.items()},
            "active_parties": self.get_active_parties(),
        }


# Japan-China Default Third Parties
JAPAN_CHINA_THIRD_PARTIES = [
    {
        "party_id": "USA",
        "name": "United States",
        "alignment_with_a": 0.8,            # Strongly pro-Japan
        "coordination_bonus": 0.4,
        "alternative_supply_capacity": 0.15,
        "market_access_leverage": 0.35,
        "mediation_effectiveness": 0.1,     # Not a neutral mediator
        "intervention_threshold": 0.3,      # Intervenes early
    },
    {
        "party_id": "EU",
        "name": "European Union",
        "alignment_with_a": 0.3,            # Slightly pro-Japan
        "coordination_bonus": 0.2,
        "alternative_supply_capacity": 0.2,
        "market_access_leverage": 0.3,
        "mediation_effectiveness": 0.4,
        "intervention_threshold": 0.5,
    },
    {
        "party_id": "ASEAN",
        "name": "ASEAN",
        "alignment_with_a": 0.0,            # Neutral (hedging)
        "coordination_bonus": 0.1,
        "alternative_supply_capacity": 0.35,  # Can absorb diverted trade
        "market_access_leverage": 0.15,
        "mediation_effectiveness": 0.5,
        "intervention_threshold": 0.6,      # Only at high friction
    },
    {
        "party_id": "SKR",
        "name": "South Korea",
        "alignment_with_a": 0.2,            # Complex relationship
        "coordination_bonus": 0.15,
        "alternative_supply_capacity": 0.25,
        "market_access_leverage": 0.1,
        "mediation_effectiveness": 0.2,
        "intervention_threshold": 0.5,
    },
]


def create_japan_china_third_parties() -> ThirdPartySystem:
    """Factory function for Japan-China third party system."""
    system = ThirdPartySystem()
    system.load_from_config(JAPAN_CHINA_THIRD_PARTIES)
    return system
