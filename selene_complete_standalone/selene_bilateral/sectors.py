"""
Sectors module for Selene Bilateral Friction Extension
Handles sector-specific dependencies and pain calculations.

Key features:
- Asymmetric dependencies (A→B different from B→A)
- Substitutability timers (how long to find alternatives)
- Criticality scoring (downstream economic effects)
- Political salience (voter awareness)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .state_agent import PainAssessment


@dataclass
class SectorDependency:
    """
    Represents bilateral interdependence in one economic sector.
    
    Asymmetric by design: Japan's rare earth dependence on China
    differs from China's semiconductor equipment dependence on Japan.
    """
    
    sector_name: str                    # e.g., "rare_earths", "semiconductors"
    
    # Trade flows (billion USD annual)
    a_exports_to_b: float               # State A sells to State B
    b_exports_to_a: float               # State B sells to State A
    
    # Substitutability (how fast can you find alternatives?)
    a_substitution_time: int = 24       # Months for A to replace B's goods
    b_substitution_time: int = 24       # Months for B to replace A's goods
    a_substitution_cost: float = 0.2    # Premium A pays for alternatives (0-1)
    b_substitution_cost: float = 0.2    # Premium B pays for alternatives
    
    # Criticality (downstream economic multiplier)
    a_criticality_score: float = 0.5    # 0-1, how essential to A's economy
    b_criticality_score: float = 0.5    # 0-1, how essential to B's economy
    
    # Political visibility
    a_political_salience: float = 0.5   # 0-1, how much A's voters notice
    b_political_salience: float = 0.5   # 0-1, how much B's voters notice
    
    # Self-harm coefficients (restricting hurts your own exporters)
    a_restriction_self_harm: float = 0.1  # Cost to A of restricting exports to B
    b_restriction_self_harm: float = 0.1  # Cost to B of restricting exports to A
    
    def get_trade_value(self, direction: str) -> float:
        """Get trade value for a direction ('a_to_b' or 'b_to_a')."""
        if direction == "a_to_b":
            return self.a_exports_to_b
        elif direction == "b_to_a":
            return self.b_exports_to_a
        else:
            raise ValueError(f"Unknown direction: {direction}")
    
    def calculate_pain_to_a(
        self,
        restriction_intensity: float,
        diversification_progress: float = 0.0,
        months_elapsed: int = 0
    ) -> Dict[str, float]:
        """
        Calculate pain to State A from B restricting exports.
        
        Args:
            restriction_intensity: 0-1, how severe B's restrictions
            diversification_progress: 0-1, how much A has diversified
            months_elapsed: Time since restrictions began
        """
        if restriction_intensity == 0:
            return {"economic": 0.0, "political": 0.0, "total": 0.0}
        
        # Base trade loss
        trade_loss = self.b_exports_to_a * restriction_intensity
        
        # Substitution cost (decreases over time as alternatives found)
        time_factor = max(0, 1 - months_elapsed / max(1, self.a_substitution_time))
        sub_cost = trade_loss * self.a_substitution_cost * time_factor
        
        # Diversification reduces impact
        diversification_reduction = 1 - diversification_progress * 0.5
        
        # Apply criticality multiplier
        economic_pain = (trade_loss + sub_cost) * self.a_criticality_score * diversification_reduction
        
        # Political pain (voter anger)
        political_pain = restriction_intensity * self.a_political_salience
        
        return {
            "economic": economic_pain,
            "political": political_pain,
            "total": 0.7 * economic_pain + 0.3 * political_pain,
        }
    
    def calculate_pain_to_b(
        self,
        restriction_intensity: float,
        diversification_progress: float = 0.0,
        months_elapsed: int = 0
    ) -> Dict[str, float]:
        """Calculate pain to State B from A restricting exports."""
        if restriction_intensity == 0:
            return {"economic": 0.0, "political": 0.0, "total": 0.0}
        
        trade_loss = self.a_exports_to_b * restriction_intensity
        
        time_factor = max(0, 1 - months_elapsed / max(1, self.b_substitution_time))
        sub_cost = trade_loss * self.b_substitution_cost * time_factor
        
        diversification_reduction = 1 - diversification_progress * 0.5
        
        economic_pain = (trade_loss + sub_cost) * self.b_criticality_score * diversification_reduction
        political_pain = restriction_intensity * self.b_political_salience
        
        return {
            "economic": economic_pain,
            "political": political_pain,
            "total": 0.7 * economic_pain + 0.3 * political_pain,
        }
    
    def calculate_self_harm(
        self,
        restrictor: str,
        restriction_intensity: float
    ) -> float:
        """
        Calculate self-harm to the state imposing restrictions.
        
        Restricting exports hurts your own exporters.
        """
        if restrictor == "A":
            return self.a_exports_to_b * restriction_intensity * self.a_restriction_self_harm
        else:
            return self.b_exports_to_a * restriction_intensity * self.b_restriction_self_harm
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector_name": self.sector_name,
            "a_exports_to_b": self.a_exports_to_b,
            "b_exports_to_a": self.b_exports_to_a,
            "a_substitution_time": self.a_substitution_time,
            "b_substitution_time": self.b_substitution_time,
            "a_criticality_score": self.a_criticality_score,
            "b_criticality_score": self.b_criticality_score,
        }


class DependencyMatrix:
    """
    Full bilateral dependency structure across all sectors.
    
    Central component for calculating aggregate pain and
    identifying leverage asymmetries.
    """
    
    def __init__(self):
        self.sectors: Dict[str, SectorDependency] = {}
        self.restriction_start_times: Dict[str, Dict[str, int]] = {
            "A": {},  # Sector -> step when A started restricting
            "B": {},  # Sector -> step when B started restricting
        }
    
    def add_sector(self, sector: SectorDependency):
        """Add a sector to the dependency matrix."""
        self.sectors[sector.sector_name] = sector
    
    def load_from_config(self, sectors_config: List[Dict[str, Any]]):
        """Load sectors from YAML config."""
        for sc in sectors_config:
            sector = SectorDependency(
                sector_name=sc["sector_name"],
                a_exports_to_b=sc.get("a_exports_to_b", 1.0),
                b_exports_to_a=sc.get("b_exports_to_a", 1.0),
                a_substitution_time=sc.get("a_substitution_time", 24),
                b_substitution_time=sc.get("b_substitution_time", 24),
                a_substitution_cost=sc.get("a_substitution_cost", 0.2),
                b_substitution_cost=sc.get("b_substitution_cost", 0.2),
                a_criticality_score=sc.get("a_criticality_score", 0.5),
                b_criticality_score=sc.get("b_criticality_score", 0.5),
                a_political_salience=sc.get("a_political_salience", 0.5),
                b_political_salience=sc.get("b_political_salience", 0.5),
                a_restriction_self_harm=sc.get("a_restriction_self_harm", 0.1),
                b_restriction_self_harm=sc.get("b_restriction_self_harm", 0.1),
            )
            self.add_sector(sector)
    
    def record_restriction_start(self, restrictor: str, sector: str, step: int):
        """Record when a restriction started (for substitution timing)."""
        if sector not in self.restriction_start_times[restrictor]:
            self.restriction_start_times[restrictor][sector] = step
    
    def clear_restriction(self, restrictor: str, sector: str):
        """Clear restriction timing when lifted."""
        if sector in self.restriction_start_times[restrictor]:
            del self.restriction_start_times[restrictor][sector]
    
    def calculate_pain_to_a(
        self,
        b_restrictions: Dict[str, float],
        a_diversification: Dict[str, float],
        current_step: int,
        steps_per_month: float = 1.0
    ) -> PainAssessment:
        """
        Calculate total pain to State A from all of B's restrictions.
        
        Args:
            b_restrictions: Sector -> intensity of B's restrictions
            a_diversification: Sector -> A's diversification progress
            current_step: Current simulation step
            steps_per_month: Conversion factor
        """
        total_economic = 0.0
        total_political = 0.0
        total_reputational = 0.0
        
        for sector_name, intensity in b_restrictions.items():
            if sector_name not in self.sectors:
                continue
            
            sector = self.sectors[sector_name]
            
            # Calculate months since restriction started
            start_step = self.restriction_start_times["B"].get(sector_name, current_step)
            months_elapsed = int((current_step - start_step) / steps_per_month)
            
            diversification = a_diversification.get(sector_name, 0.0)
            
            pain = sector.calculate_pain_to_a(intensity, diversification, months_elapsed)
            
            total_economic += pain["economic"]
            total_political += pain["political"]
        
        # Aggregate reputational cost (being targeted)
        total_reputational = sum(b_restrictions.values()) * 0.05
        
        total = 0.6 * total_economic + 0.3 * total_political + 0.1 * total_reputational
        
        return PainAssessment(
            economic=total_economic,
            political=total_political,
            reputational=total_reputational,
            total=total,
        )
    
    def calculate_pain_to_b(
        self,
        a_restrictions: Dict[str, float],
        b_diversification: Dict[str, float],
        current_step: int,
        steps_per_month: float = 1.0
    ) -> PainAssessment:
        """Calculate total pain to State B from all of A's restrictions."""
        total_economic = 0.0
        total_political = 0.0
        total_reputational = 0.0
        
        for sector_name, intensity in a_restrictions.items():
            if sector_name not in self.sectors:
                continue
            
            sector = self.sectors[sector_name]
            
            start_step = self.restriction_start_times["A"].get(sector_name, current_step)
            months_elapsed = int((current_step - start_step) / steps_per_month)
            
            diversification = b_diversification.get(sector_name, 0.0)
            
            pain = sector.calculate_pain_to_b(intensity, diversification, months_elapsed)
            
            total_economic += pain["economic"]
            total_political += pain["political"]
        
        total_reputational = sum(a_restrictions.values()) * 0.05
        total = 0.6 * total_economic + 0.3 * total_political + 0.1 * total_reputational
        
        return PainAssessment(
            economic=total_economic,
            political=total_political,
            reputational=total_reputational,
            total=total,
        )
    
    def calculate_self_harm(
        self,
        restrictor: str,
        restrictions: Dict[str, float]
    ) -> float:
        """Calculate total self-harm from own restrictions."""
        total = 0.0
        for sector_name, intensity in restrictions.items():
            if sector_name in self.sectors:
                total += self.sectors[sector_name].calculate_self_harm(restrictor, intensity)
        return total
    
    def get_leverage_asymmetry(self) -> Dict[str, float]:
        """
        Calculate which state has leverage in each sector.
        
        Positive = A has leverage (B more dependent)
        Negative = B has leverage (A more dependent)
        """
        asymmetries = {}
        for name, sector in self.sectors.items():
            # Compare criticality-weighted trade dependencies
            a_vulnerability = sector.b_exports_to_a * sector.a_criticality_score
            b_vulnerability = sector.a_exports_to_b * sector.b_criticality_score
            
            # Normalize to -1 to 1 scale
            total = a_vulnerability + b_vulnerability
            if total > 0:
                asymmetry = (b_vulnerability - a_vulnerability) / total
            else:
                asymmetry = 0.0
            
            asymmetries[name] = round(asymmetry, 3)
        
        return asymmetries
    
    def get_total_trade_value(self) -> Dict[str, float]:
        """Get total bilateral trade value."""
        a_to_b = sum(s.a_exports_to_b for s in self.sectors.values())
        b_to_a = sum(s.b_exports_to_a for s in self.sectors.values())
        return {
            "a_to_b": a_to_b,
            "b_to_a": b_to_a,
            "total": a_to_b + b_to_a,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sectors": {name: s.to_dict() for name, s in self.sectors.items()},
            "leverage_asymmetry": self.get_leverage_asymmetry(),
            "total_trade": self.get_total_trade_value(),
        }


# Japan-China Default Sectors (from spec)
JAPAN_CHINA_SECTORS = [
    {
        "sector_name": "rare_earths",
        "a_exports_to_b": 0.1,        # Japan exports minimal RE to China
        "b_exports_to_a": 8.5,        # China exports significant RE to Japan
        "a_substitution_time": 36,    # Takes Japan 3 years to diversify
        "b_substitution_time": 6,     # China can find other buyers quickly
        "a_substitution_cost": 0.4,   # 40% premium for alternatives
        "b_substitution_cost": 0.1,
        "a_criticality_score": 0.85,  # Very critical for Japan's manufacturing
        "b_criticality_score": 0.2,
        "a_political_salience": 0.7,
        "b_political_salience": 0.3,
        "a_restriction_self_harm": 0.05,
        "b_restriction_self_harm": 0.15,  # Hurts Chinese RE exporters
    },
    {
        "sector_name": "semiconductor_equipment",
        "a_exports_to_b": 12.0,       # Japan exports significant chip equipment
        "b_exports_to_a": 2.0,
        "a_substitution_time": 12,
        "b_substitution_time": 48,    # Takes China years to develop alternatives
        "a_substitution_cost": 0.15,
        "b_substitution_cost": 0.5,   # Very expensive alternatives
        "a_criticality_score": 0.4,
        "b_criticality_score": 0.9,   # Critical for China's chip ambitions
        "a_political_salience": 0.6,
        "b_political_salience": 0.9,
        "a_restriction_self_harm": 0.25,  # Hurts Japanese equipment makers
        "b_restriction_self_harm": 0.1,
    },
    {
        "sector_name": "tourism",
        "a_exports_to_b": 2.0,        # Japanese tourism to China
        "b_exports_to_a": 15.0,       # Chinese tourism to Japan (pre-COVID peak)
        "a_substitution_time": 3,
        "b_substitution_time": 6,
        "a_substitution_cost": 0.1,
        "b_substitution_cost": 0.2,
        "a_criticality_score": 0.2,
        "b_criticality_score": 0.15,
        "a_political_salience": 0.4,
        "b_political_salience": 0.3,
        "a_restriction_self_harm": 0.05,
        "b_restriction_self_harm": 0.1,
    },
    {
        "sector_name": "seafood",
        "a_exports_to_b": 3.5,        # Japanese seafood to China
        "b_exports_to_a": 1.0,
        "a_substitution_time": 6,
        "b_substitution_time": 3,
        "a_substitution_cost": 0.2,
        "b_substitution_cost": 0.1,
        "a_criticality_score": 0.15,
        "b_criticality_score": 0.1,
        "a_political_salience": 0.5,  # Fukushima link raises salience
        "b_political_salience": 0.6,
        "a_restriction_self_harm": 0.05,
        "b_restriction_self_harm": 0.15,
    },
    {
        "sector_name": "dual_use_goods",
        "a_exports_to_b": 8.0,
        "b_exports_to_a": 6.0,
        "a_substitution_time": 18,
        "b_substitution_time": 24,
        "a_substitution_cost": 0.25,
        "b_substitution_cost": 0.3,
        "a_criticality_score": 0.5,
        "b_criticality_score": 0.6,
        "a_political_salience": 0.8,
        "b_political_salience": 0.9,
        "a_restriction_self_harm": 0.2,
        "b_restriction_self_harm": 0.2,
    },
    {
        "sector_name": "automotive_parts",
        "a_exports_to_b": 6.5,
        "b_exports_to_a": 4.0,
        "a_substitution_time": 12,
        "b_substitution_time": 18,
        "a_substitution_cost": 0.15,
        "b_substitution_cost": 0.2,
        "a_criticality_score": 0.6,
        "b_criticality_score": 0.5,
        "a_political_salience": 0.5,
        "b_political_salience": 0.4,
        "a_restriction_self_harm": 0.2,
        "b_restriction_self_harm": 0.15,
    },
]


def create_japan_china_matrix() -> DependencyMatrix:
    """Factory function for Japan-China dependency matrix."""
    matrix = DependencyMatrix()
    matrix.load_from_config(JAPAN_CHINA_SECTORS)
    return matrix
