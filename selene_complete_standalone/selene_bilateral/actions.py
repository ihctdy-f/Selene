"""
Actions module for Selene Bilateral Friction Extension
Defines the action space for graduated economic friction.

Key distinction from base Selene:
- Actions are continuous (0-100% intensity)
- Actions are sector-specific
- Actions have signaling vs substance components
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class ActionType(Enum):
    """Categories of friction actions."""
    EXPORT_CONTROL = "export_control"
    IMPORT_BAN = "import_ban"
    INVESTMENT_SCREEN = "investment_screen"
    VISA_RESTRICTION = "visa_restriction"
    TARIFF = "tariff"
    REGULATORY_BARRIER = "regulatory_barrier"
    INFORMAL_PRESSURE = "informal_pressure"  # "Guidance" to firms


class Rationale(Enum):
    """Stated justifications for restrictions."""
    NATIONAL_SECURITY = "national_security"
    DUMPING = "dumping"
    RECIPROCITY = "reciprocity"
    ENVIRONMENTAL = "environmental"
    HEALTH_SAFETY = "health_safety"
    HUMAN_RIGHTS = "human_rights"
    UNSPECIFIED = "unspecified"


@dataclass
class FrictionAction:
    """
    A graduated action a state can take.
    
    Represents a specific policy move with both
    substantive effects and signaling properties.
    """
    
    action_id: str                          # Unique identifier
    actor: str                              # "A" or "B"
    target_sector: str                      # Which sector affected
    action_type: ActionType
    
    # Intensity parameters
    current_intensity: float = 0.0          # 0-1 current level
    max_intensity: float = 1.0              # Maximum possible
    min_step: float = 0.1                   # Minimum adjustment increment
    
    # Economic parameters
    self_harm_coefficient: float = 0.1      # Hurt own economy
    target_harm_multiplier: float = 1.0     # Damage to opponent
    
    # Signaling properties
    is_public: bool = True                  # Announced vs quiet
    stated_rationale: Rationale = Rationale.UNSPECIFIED
    signal_strength: float = 0.5            # 0-1, visibility/impact of signal
    
    # Substitution vulnerability
    substitution_vulnerability: float = 0.5  # How easily target can adapt
    
    # Escalation ladder position
    escalation_tier: int = 1                # 1=mild, 3=severe
    
    def calculate_target_impact(self, intensity: float) -> float:
        """Calculate damage to target from this action at given intensity."""
        base_impact = intensity * self.target_harm_multiplier
        # Reduce impact if target can substitute
        substitution_reduction = 1 - (self.substitution_vulnerability * 0.3)
        return base_impact * substitution_reduction
    
    def calculate_self_cost(self, intensity: float) -> float:
        """Calculate cost to actor from this action."""
        return intensity * self.self_harm_coefficient
    
    def calculate_signal_value(self, intensity: float) -> float:
        """Calculate signaling/political value of action."""
        if not self.is_public:
            return intensity * self.signal_strength * 0.3
        return intensity * self.signal_strength
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "actor": self.actor,
            "target_sector": self.target_sector,
            "action_type": self.action_type.value,
            "current_intensity": round(self.current_intensity, 3),
            "max_intensity": self.max_intensity,
            "self_harm_coefficient": self.self_harm_coefficient,
            "signal_strength": self.signal_strength,
            "escalation_tier": self.escalation_tier,
        }


class ActionSpace:
    """
    Available actions and their parameters for a bilateral scenario.
    
    Provides the menu of possible friction moves for each state.
    """
    
    def __init__(self):
        self.actions: Dict[str, FrictionAction] = {}
    
    def add_action(self, action: FrictionAction):
        """Add an action to the space."""
        self.actions[action.action_id] = action
    
    def load_from_config(self, actions_config: List[Dict[str, Any]]):
        """Load actions from YAML config."""
        action_type_map = {
            "export_control": ActionType.EXPORT_CONTROL,
            "import_ban": ActionType.IMPORT_BAN,
            "investment_screen": ActionType.INVESTMENT_SCREEN,
            "visa_restriction": ActionType.VISA_RESTRICTION,
            "tariff": ActionType.TARIFF,
            "regulatory_barrier": ActionType.REGULATORY_BARRIER,
            "informal_pressure": ActionType.INFORMAL_PRESSURE,
        }
        
        rationale_map = {
            "national_security": Rationale.NATIONAL_SECURITY,
            "dumping": Rationale.DUMPING,
            "reciprocity": Rationale.RECIPROCITY,
            "environmental": Rationale.ENVIRONMENTAL,
            "health_safety": Rationale.HEALTH_SAFETY,
            "human_rights": Rationale.HUMAN_RIGHTS,
            "unspecified": Rationale.UNSPECIFIED,
        }
        
        for ac in actions_config:
            action = FrictionAction(
                action_id=ac["action_id"],
                actor=ac["actor"],
                target_sector=ac["target_sector"],
                action_type=action_type_map.get(
                    ac.get("action_type", "export_control"),
                    ActionType.EXPORT_CONTROL
                ),
                max_intensity=ac.get("max_intensity", 1.0),
                min_step=ac.get("min_step", 0.1),
                self_harm_coefficient=ac.get("self_harm_coefficient", 0.1),
                target_harm_multiplier=ac.get("target_harm_multiplier", 1.0),
                is_public=ac.get("is_public", True),
                stated_rationale=rationale_map.get(
                    ac.get("stated_rationale", "unspecified"),
                    Rationale.UNSPECIFIED
                ),
                signal_strength=ac.get("signal_strength", 0.5),
                substitution_vulnerability=ac.get("substitution_vulnerability", 0.5),
                escalation_tier=ac.get("escalation_tier", 1),
            )
            self.add_action(action)
    
    def get_actions_for_actor(self, actor: str) -> List[FrictionAction]:
        """Get all actions available to an actor."""
        return [a for a in self.actions.values() if a.actor == actor]
    
    def get_actions_for_sector(self, sector: str) -> List[FrictionAction]:
        """Get all actions affecting a sector."""
        return [a for a in self.actions.values() if a.target_sector == sector]
    
    def get_actions_by_tier(self, tier: int) -> List[FrictionAction]:
        """Get actions at a specific escalation tier."""
        return [a for a in self.actions.values() if a.escalation_tier == tier]
    
    def get_available_escalations(
        self,
        actor: str,
        current_restrictions: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Get list of available escalation moves for an actor.
        
        Returns simplified action descriptors for decision logic.
        """
        available = []
        
        for action in self.get_actions_for_actor(actor):
            current = current_restrictions.get(action.target_sector, 0.0)
            
            if current < action.max_intensity:
                available.append({
                    "action_id": action.action_id,
                    "sector": action.target_sector,
                    "current": current,
                    "max_intensity": action.max_intensity,
                    "self_harm_coefficient": action.self_harm_coefficient,
                    "signal_strength": action.signal_strength,
                    "escalation_tier": action.escalation_tier,
                })
        
        return available
    
    def get_available_de_escalations(
        self,
        actor: str,
        current_restrictions: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Get list of available de-escalation moves."""
        available = []
        
        for action in self.get_actions_for_actor(actor):
            current = current_restrictions.get(action.target_sector, 0.0)
            
            if current > 0:
                available.append({
                    "action_id": action.action_id,
                    "sector": action.target_sector,
                    "current": current,
                    "min_step": action.min_step,
                    "self_harm_coefficient": action.self_harm_coefficient,
                })
        
        return available
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "actions": {aid: a.to_dict() for aid, a in self.actions.items()},
            "total_actions": len(self.actions),
        }


# Japan-China Default Actions (from spec)
JAPAN_CHINA_ACTIONS = [
    # China → Japan actions
    {
        "action_id": "chn_rare_earth_control",
        "actor": "B",  # China = B
        "target_sector": "rare_earths",
        "action_type": "export_control",
        "max_intensity": 1.0,
        "self_harm_coefficient": 0.15,
        "target_harm_multiplier": 1.2,
        "signal_strength": 0.9,
        "substitution_vulnerability": 0.4,  # Japan has diversified somewhat
        "escalation_tier": 2,
        "stated_rationale": "national_security",
    },
    {
        "action_id": "chn_seafood_ban",
        "actor": "B",
        "target_sector": "seafood",
        "action_type": "import_ban",
        "max_intensity": 1.0,
        "self_harm_coefficient": 0.05,
        "target_harm_multiplier": 0.8,
        "signal_strength": 0.7,
        "substitution_vulnerability": 0.6,
        "escalation_tier": 1,
        "stated_rationale": "health_safety",
    },
    {
        "action_id": "chn_tourism_advisory",
        "actor": "B",
        "target_sector": "tourism",
        "action_type": "informal_pressure",
        "max_intensity": 0.8,
        "self_harm_coefficient": 0.1,
        "target_harm_multiplier": 0.9,
        "signal_strength": 0.6,
        "substitution_vulnerability": 0.5,
        "escalation_tier": 1,
    },
    {
        "action_id": "chn_dual_use_restriction",
        "actor": "B",
        "target_sector": "dual_use_goods",
        "action_type": "export_control",
        "max_intensity": 0.9,
        "self_harm_coefficient": 0.2,
        "target_harm_multiplier": 1.0,
        "signal_strength": 0.8,
        "substitution_vulnerability": 0.3,
        "escalation_tier": 2,
        "stated_rationale": "national_security",
    },
    {
        "action_id": "chn_auto_parts_barrier",
        "actor": "B",
        "target_sector": "automotive_parts",
        "action_type": "regulatory_barrier",
        "max_intensity": 0.7,
        "self_harm_coefficient": 0.15,
        "target_harm_multiplier": 0.9,
        "signal_strength": 0.5,
        "substitution_vulnerability": 0.4,
        "escalation_tier": 1,
    },
    
    # Japan → China actions
    {
        "action_id": "jpn_chip_equipment_control",
        "actor": "A",  # Japan = A
        "target_sector": "semiconductor_equipment",
        "action_type": "export_control",
        "max_intensity": 1.0,
        "self_harm_coefficient": 0.25,
        "target_harm_multiplier": 1.3,
        "signal_strength": 0.9,
        "substitution_vulnerability": 0.2,  # Hard for China to substitute
        "escalation_tier": 3,
        "stated_rationale": "national_security",
    },
    {
        "action_id": "jpn_dual_use_screen",
        "actor": "A",
        "target_sector": "dual_use_goods",
        "action_type": "export_control",
        "max_intensity": 0.9,
        "self_harm_coefficient": 0.2,
        "target_harm_multiplier": 1.0,
        "signal_strength": 0.7,
        "substitution_vulnerability": 0.35,
        "escalation_tier": 2,
        "stated_rationale": "national_security",
    },
    {
        "action_id": "jpn_investment_screen",
        "actor": "A",
        "target_sector": "dual_use_goods",
        "action_type": "investment_screen",
        "max_intensity": 0.8,
        "self_harm_coefficient": 0.1,
        "target_harm_multiplier": 0.7,
        "signal_strength": 0.6,
        "substitution_vulnerability": 0.5,
        "escalation_tier": 1,
    },
    {
        "action_id": "jpn_rare_earth_diversification",
        "actor": "A",
        "target_sector": "rare_earths",
        "action_type": "regulatory_barrier",  # Subsidy for alternatives
        "max_intensity": 0.6,
        "self_harm_coefficient": 0.05,  # Costs money but strategic
        "target_harm_multiplier": 0.4,
        "signal_strength": 0.4,
        "substitution_vulnerability": 0.8,
        "escalation_tier": 1,
    },
    {
        "action_id": "jpn_visa_restriction",
        "actor": "A",
        "target_sector": "tourism",
        "action_type": "visa_restriction",
        "max_intensity": 0.5,
        "self_harm_coefficient": 0.15,
        "target_harm_multiplier": 0.6,
        "signal_strength": 0.5,
        "substitution_vulnerability": 0.7,
        "escalation_tier": 1,
    },
]


def create_japan_china_action_space() -> ActionSpace:
    """Factory function for Japan-China action space."""
    space = ActionSpace()
    space.load_from_config(JAPAN_CHINA_ACTIONS)
    return space
