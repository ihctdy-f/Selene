"""
Shocks module for Selene Bilateral Friction Extension
Generates external events that influence bilateral dynamics.

Key shock types:
- Geopolitical triggers (territorial disputes, military exercises)
- Economic shocks (recessions, commodity price spikes)
- Domestic political events (elections, scandals, leadership changes)
- Third party actions (US policy changes, ASEAN moves)
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
import random


class BilateralShockType(Enum):
    """Types of shocks specific to bilateral friction."""
    TERRITORIAL_INCIDENT = "territorial_incident"
    MILITARY_EXERCISE = "military_exercise"
    DIPLOMATIC_STATEMENT = "diplomatic_statement"
    ELECTION = "election"
    LEADERSHIP_CHANGE = "leadership_change"
    PUBLIC_SCANDAL = "public_scandal"
    ECONOMIC_RECESSION = "economic_recession"
    COMMODITY_SPIKE = "commodity_spike"
    THIRD_PARTY_ACTION = "third_party_action"
    HISTORICAL_ANNIVERSARY = "historical_anniversary"
    TECH_BREAKTHROUGH = "tech_breakthrough"
    SUPPLY_DISRUPTION = "supply_disruption"


@dataclass
class BilateralShock:
    """A shock event affecting bilateral relations."""
    
    shock_type: BilateralShockType
    step: int
    
    # Who is affected
    primary_target: Optional[str] = None  # "A", "B", or None (both)
    
    # Intensity and direction
    intensity: float = 0.5               # 0-1 scale
    escalatory: bool = True              # True = increases friction pressure
    
    # Duration
    duration_steps: int = 1              # How long effects last
    
    # Specific effects
    nationalism_boost: float = 0.0       # Increase in nationalism
    approval_impact: float = 0.0         # Impact on leader approval
    sector_affected: Optional[str] = None
    
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "shock_type": self.shock_type.value,
            "step": self.step,
            "primary_target": self.primary_target,
            "intensity": round(self.intensity, 3),
            "escalatory": self.escalatory,
            "duration_steps": self.duration_steps,
            "description": self.description,
        }


class BilateralShockGenerator:
    """
    Generates shocks for bilateral friction simulation.
    
    Calibrated for Japan-China but generalizable.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.active_shocks: List[BilateralShock] = []
        
        # Base probabilities per step (can be overridden)
        self.shock_probabilities = {
            BilateralShockType.TERRITORIAL_INCIDENT: 0.02,
            BilateralShockType.MILITARY_EXERCISE: 0.05,
            BilateralShockType.DIPLOMATIC_STATEMENT: 0.08,
            BilateralShockType.ELECTION: 0.01,
            BilateralShockType.LEADERSHIP_CHANGE: 0.005,
            BilateralShockType.PUBLIC_SCANDAL: 0.03,
            BilateralShockType.ECONOMIC_RECESSION: 0.01,
            BilateralShockType.COMMODITY_SPIKE: 0.02,
            BilateralShockType.THIRD_PARTY_ACTION: 0.04,
            BilateralShockType.HISTORICAL_ANNIVERSARY: 0.03,
            BilateralShockType.TECH_BREAKTHROUGH: 0.01,
            BilateralShockType.SUPPLY_DISRUPTION: 0.02,
        }
        
        # Override from config
        if "shock_probabilities" in self.config:
            self.shock_probabilities.update(self.config["shock_probabilities"])
    
    def generate_shocks(
        self,
        step: int,
        current_friction: float,
        state_a: Any,
        state_b: Any
    ) -> List[BilateralShock]:
        """
        Generate shocks for a simulation step.
        
        Higher friction increases probability of escalatory shocks.
        """
        new_shocks = []
        
        # Friction modifier: higher friction = more likely shocks
        friction_mod = 1.0 + current_friction * 0.5
        
        for shock_type, base_prob in self.shock_probabilities.items():
            adjusted_prob = base_prob * friction_mod
            
            if random.random() < adjusted_prob:
                shock = self._create_shock(shock_type, step, current_friction, state_a, state_b)
                if shock:
                    new_shocks.append(shock)
        
        # Update active shocks
        self._update_active_shocks(step)
        self.active_shocks.extend(new_shocks)
        
        return new_shocks
    
    def _create_shock(
        self,
        shock_type: BilateralShockType,
        step: int,
        friction: float,
        state_a: Any,
        state_b: Any
    ) -> Optional[BilateralShock]:
        """Create a specific shock with appropriate parameters."""
        
        if shock_type == BilateralShockType.TERRITORIAL_INCIDENT:
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                intensity=random.uniform(0.4, 0.9),
                escalatory=True,
                duration_steps=random.randint(3, 8),
                nationalism_boost=random.uniform(0.05, 0.15),
                description="Incident in disputed waters/airspace",
            )
        
        elif shock_type == BilateralShockType.MILITARY_EXERCISE:
            target = random.choice(["A", "B"])
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                primary_target="B" if target == "A" else "A",  # Other side reacts
                intensity=random.uniform(0.3, 0.7),
                escalatory=True,
                duration_steps=random.randint(2, 5),
                nationalism_boost=random.uniform(0.02, 0.08),
                description=f"State {'A' if target == 'A' else 'B'} conducts military exercises",
            )
        
        elif shock_type == BilateralShockType.DIPLOMATIC_STATEMENT:
            escalatory = random.random() < 0.6  # 60% escalatory
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                intensity=random.uniform(0.2, 0.5),
                escalatory=escalatory,
                duration_steps=random.randint(1, 3),
                nationalism_boost=0.02 if escalatory else -0.01,
                description="Official statement on bilateral relations",
            )
        
        elif shock_type == BilateralShockType.ELECTION:
            target = random.choice(["A", "B"])
            # Elections can go either way
            hawkish = random.random() < 0.5
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                primary_target=target,
                intensity=random.uniform(0.4, 0.8),
                escalatory=hawkish,
                duration_steps=random.randint(6, 12),
                nationalism_boost=0.1 if hawkish else -0.05,
                approval_impact=random.uniform(-0.2, 0.2),  # Reset approval
                description=f"Election in State {target}",
            )
        
        elif shock_type == BilateralShockType.LEADERSHIP_CHANGE:
            target = random.choice(["A", "B"])
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                primary_target=target,
                intensity=random.uniform(0.5, 0.9),
                escalatory=random.random() < 0.4,  # New leaders often de-escalate initially
                duration_steps=random.randint(8, 16),
                approval_impact=0.2,  # Honeymoon period
                description=f"New leader in State {target}",
            )
        
        elif shock_type == BilateralShockType.PUBLIC_SCANDAL:
            target = random.choice(["A", "B"])
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                primary_target=target,
                intensity=random.uniform(0.3, 0.6),
                escalatory=random.random() < 0.7,  # Scandals often lead to diversionary conflict
                duration_steps=random.randint(2, 6),
                approval_impact=-random.uniform(0.05, 0.15),
                description=f"Domestic scandal in State {target}",
            )
        
        elif shock_type == BilateralShockType.ECONOMIC_RECESSION:
            target = random.choice(["A", "B", None])
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                primary_target=target,
                intensity=random.uniform(0.4, 0.8),
                escalatory=False,  # Usually pushes toward pragmatism
                duration_steps=random.randint(8, 24),
                approval_impact=-random.uniform(0.1, 0.2),
                description="Economic downturn",
            )
        
        elif shock_type == BilateralShockType.COMMODITY_SPIKE:
            sector = random.choice(["rare_earths", "automotive_parts", "dual_use_goods"])
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                intensity=random.uniform(0.3, 0.6),
                escalatory=True,  # Price spikes increase pressure
                duration_steps=random.randint(4, 12),
                sector_affected=sector,
                description=f"Price spike in {sector}",
            )
        
        elif shock_type == BilateralShockType.THIRD_PARTY_ACTION:
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                intensity=random.uniform(0.3, 0.7),
                escalatory=random.random() < 0.5,
                duration_steps=random.randint(3, 8),
                description="Third party (US/EU/ASEAN) policy action",
            )
        
        elif shock_type == BilateralShockType.HISTORICAL_ANNIVERSARY:
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                intensity=random.uniform(0.2, 0.5),
                escalatory=True,
                duration_steps=random.randint(1, 3),
                nationalism_boost=random.uniform(0.03, 0.08),
                description="Sensitive historical anniversary",
            )
        
        elif shock_type == BilateralShockType.TECH_BREAKTHROUGH:
            target = random.choice(["A", "B"])
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                primary_target=target,
                intensity=random.uniform(0.3, 0.6),
                escalatory=False,  # Reduces dependency
                duration_steps=random.randint(12, 24),
                sector_affected=random.choice(["semiconductor_equipment", "rare_earths"]),
                description=f"Tech breakthrough reduces {target}'s dependency",
            )
        
        elif shock_type == BilateralShockType.SUPPLY_DISRUPTION:
            sector = random.choice(["rare_earths", "semiconductor_equipment", "automotive_parts"])
            return BilateralShock(
                shock_type=shock_type,
                step=step,
                intensity=random.uniform(0.4, 0.7),
                escalatory=True,
                duration_steps=random.randint(2, 8),
                sector_affected=sector,
                description=f"Supply chain disruption in {sector}",
            )
        
        return None
    
    def _update_active_shocks(self, current_step: int):
        """Remove expired shocks."""
        self.active_shocks = [
            s for s in self.active_shocks
            if current_step < s.step + s.duration_steps
        ]
    
    def get_aggregate_shock_effect(self) -> Dict[str, Any]:
        """
        Calculate aggregate effect of all active shocks.
        
        Returns combined modifiers for simulation.
        """
        total_escalatory_pressure = 0.0
        total_nationalism_a = 0.0
        total_nationalism_b = 0.0
        total_approval_a = 0.0
        total_approval_b = 0.0
        affected_sectors = set()
        
        for shock in self.active_shocks:
            if shock.escalatory:
                total_escalatory_pressure += shock.intensity * 0.3
            else:
                total_escalatory_pressure -= shock.intensity * 0.2
            
            if shock.primary_target == "A" or shock.primary_target is None:
                total_nationalism_a += shock.nationalism_boost
                total_approval_a += shock.approval_impact
            
            if shock.primary_target == "B" or shock.primary_target is None:
                total_nationalism_b += shock.nationalism_boost
                total_approval_b += shock.approval_impact
            
            if shock.sector_affected:
                affected_sectors.add(shock.sector_affected)
        
        return {
            "escalatory_pressure": total_escalatory_pressure,
            "nationalism_delta_a": total_nationalism_a,
            "nationalism_delta_b": total_nationalism_b,
            "approval_delta_a": total_approval_a,
            "approval_delta_b": total_approval_b,
            "affected_sectors": list(affected_sectors),
            "active_shock_count": len(self.active_shocks),
        }
    
    def reset(self):
        """Clear all active shocks."""
        self.active_shocks = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_shocks": [s.to_dict() for s in self.active_shocks],
            "aggregate_effect": self.get_aggregate_shock_effect(),
        }
