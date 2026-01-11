"""
Architecture Upgrade: De-escalation Dynamics Module
====================================================

Addresses the identified limitation where the model favors escalation on new 
sectors over de-escalation on existing sectors.

Key mechanisms added:
1. TIME-DECAY COSTS: Maintaining restrictions becomes increasingly costly
2. INTERNATIONAL PRESSURE: Third parties impose costs for sustained restrictions  
3. ECONOMIC FATIGUE: Domestic constituencies tire of trade war
4. REPUTATION BLEEDING: Long-term reputation costs accumulate

These create pressure to de-escalate that wasn't present in the base model.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import random


@dataclass
class RestrictionHistory:
    """Tracks how long each restriction has been in place."""
    
    sector: str
    intensity: float
    start_step: int
    current_step: int
    peak_intensity: float = 0.0
    escalation_count: int = 0
    
    @property
    def duration(self) -> int:
        """Months restriction has been active."""
        return self.current_step - self.start_step
    
    @property
    def is_prolonged(self) -> bool:
        """More than 12 months at significant intensity."""
        return self.duration > 12 and self.intensity > 0.3


@dataclass 
class TimeDecayCosts:
    """
    Calculates increasing costs of maintaining restrictions over time.
    
    Rationale: 
    - Domestic industries adapt and complain about lost opportunities
    - Alternative suppliers emerge, reducing leverage
    - Political attention wanders, costs become more salient than benefits
    """
    
    # Base monthly cost of maintaining restrictions (as % of restriction intensity)
    base_maintenance_cost: float = 0.02
    
    # How quickly costs accelerate over time
    time_acceleration_factor: float = 0.08
    
    # Maximum multiplier (costs plateau eventually)
    max_time_multiplier: float = 3.0
    
    # Threshold before time costs kick in (months)
    grace_period: int = 6
    
    def calculate_maintenance_cost(
        self, 
        history: RestrictionHistory,
        self_harm_base: float
    ) -> float:
        """
        Calculate monthly cost of maintaining a restriction.
        
        Returns cost as positive number (to be added to pain).
        """
        if history.duration <= self.grace_period:
            return 0.0
        
        months_past_grace = history.duration - self.grace_period
        
        # Logarithmic growth - rapid at first, slowing over time
        time_multiplier = min(
            self.max_time_multiplier,
            1.0 + self.time_acceleration_factor * math.log1p(months_past_grace)
        )
        
        maintenance = (
            self.base_maintenance_cost * 
            history.intensity * 
            self_harm_base *
            time_multiplier
        )
        
        return maintenance
    
    def calculate_leverage_decay(
        self,
        history: RestrictionHistory,
        opponent_diversification: float
    ) -> float:
        """
        Calculate reduction in coercive leverage over time.
        
        As opponent diversifies and adapts, restrictions become less effective.
        Returns multiplier 0.0-1.0 (1.0 = full leverage, 0.0 = no leverage).
        """
        # Base decay from time
        time_decay = math.exp(-0.03 * history.duration)
        
        # Additional decay from opponent adaptation
        adaptation_decay = 1.0 - (0.7 * opponent_diversification)
        
        return max(0.1, time_decay * adaptation_decay)


@dataclass
class InternationalPressure:
    """
    Models how third parties impose costs for sustained restrictions.
    
    Rationale:
    - Trading partners complain about disrupted supply chains
    - International forums (WTO, G7, etc.) create reputational pressure
    - Allies worry about precedent and reliability
    """
    
    # Base pressure per third party per month
    base_pressure_rate: float = 0.01
    
    # How much third parties care about long restrictions
    duration_sensitivity: float = 0.05
    
    # Threshold friction before pressure builds
    friction_threshold: float = 0.4
    
    # Maximum pressure from international community
    max_pressure: float = 0.3
    
    def calculate_pressure(
        self,
        state_id: str,
        friction_level: float,
        restriction_duration_avg: float,
        third_parties: List[Dict],
        state_alignment: float = 0.0
    ) -> float:
        """
        Calculate international pressure on a state to de-escalate.
        
        Args:
            state_id: Which state is being pressured
            friction_level: Current bilateral friction
            restriction_duration_avg: Average months of active restrictions
            third_parties: List of third party dicts with alignment
            state_alignment: How aligned state is with third parties (-1 to 1)
        
        Returns:
            Pressure value 0.0-max_pressure
        """
        if friction_level < self.friction_threshold:
            return 0.0
        
        # Base pressure from friction level
        friction_excess = friction_level - self.friction_threshold
        base = friction_excess * self.base_pressure_rate
        
        # Duration multiplier
        duration_mult = 1.0 + (self.duration_sensitivity * restriction_duration_avg)
        
        # Third party alignment effect
        # States aligned with third parties face MORE pressure to behave
        # States opposed face less (third parties don't care as much)
        alignment_mult = 1.0 + (0.5 * state_alignment)
        
        # Aggregate third party influence
        tp_influence = sum(
            tp.get('intervention_threshold', 0.5) * tp.get('coordination_bonus', 0.1)
            for tp in third_parties
        ) / max(1, len(third_parties))
        
        pressure = base * duration_mult * alignment_mult * (1 + tp_influence)
        
        return min(self.max_pressure, pressure)


@dataclass
class EconomicFatigue:
    """
    Models domestic economic fatigue with prolonged trade conflict.
    
    Rationale:
    - Businesses tire of uncertainty and lobby for resolution
    - Consumers face higher prices and reduced choices
    - Economic damage becomes politically salient
    """
    
    # How quickly fatigue builds (per month)
    fatigue_rate: float = 0.02
    
    # GDP loss threshold before fatigue kicks in
    gdp_loss_threshold: float = 5.0
    
    # Maximum fatigue effect
    max_fatigue: float = 0.25
    
    # Regime type effects
    regime_sensitivity: Dict[str, float] = field(default_factory=lambda: {
        "DEMOCRACY": 1.0,     # High sensitivity to economic pain
        "HYBRID": 0.7,        # Moderate
        "AUTOCRACY": 0.4,     # Can suppress complaints longer
    })
    
    def calculate_fatigue(
        self,
        cumulative_gdp_loss: float,
        conflict_duration: int,
        regime_type: str,
        approval_rating: float
    ) -> float:
        """
        Calculate economic fatigue pressure.
        
        Returns value 0.0-max_fatigue representing domestic pressure to end conflict.
        """
        if cumulative_gdp_loss < self.gdp_loss_threshold:
            return 0.0
        
        # Base fatigue from GDP loss
        excess_loss = cumulative_gdp_loss - self.gdp_loss_threshold
        gdp_fatigue = self.fatigue_rate * math.log1p(excess_loss)
        
        # Duration effect (conflicts get tiresome)
        duration_fatigue = 0.005 * conflict_duration
        
        # Regime sensitivity
        sensitivity = self.regime_sensitivity.get(regime_type, 0.7)
        
        # Low approval amplifies fatigue (people blame leader for economic pain)
        approval_mult = 1.0 + (0.5 * (1.0 - approval_rating))
        
        fatigue = (gdp_fatigue + duration_fatigue) * sensitivity * approval_mult
        
        return min(self.max_fatigue, fatigue)


@dataclass
class ReputationBleeding:
    """
    Models slow accumulation of reputation costs from sustained restrictions.
    
    Rationale:
    - Being seen as "weaponizer" of trade creates long-term credibility issues
    - Future partners hedge more aggressively
    - Trust once lost is hard to rebuild
    """
    
    # Base reputation cost per month of high restrictions
    monthly_bleed_rate: float = 0.005
    
    # Intensity threshold for reputation damage
    intensity_threshold: float = 0.5
    
    # How much past actions continue to hurt
    memory_decay: float = 0.95  # 5% decay per month
    
    accumulated_damage: float = 0.0
    
    def update_and_calculate(
        self,
        avg_restriction_intensity: float,
        is_initiator: bool
    ) -> float:
        """
        Update accumulated reputation damage and return current effect.
        
        Args:
            avg_restriction_intensity: Current average restriction level
            is_initiator: Whether this state initiated the restrictions
        
        Returns:
            Current reputation cost
        """
        # Decay old damage
        self.accumulated_damage *= self.memory_decay
        
        # Add new damage if above threshold
        if avg_restriction_intensity > self.intensity_threshold:
            new_damage = (
                self.monthly_bleed_rate * 
                (avg_restriction_intensity - self.intensity_threshold)
            )
            # Initiators get blamed more
            if is_initiator:
                new_damage *= 1.5
            
            self.accumulated_damage += new_damage
        
        return self.accumulated_damage


class DeescalationIncentiveCalculator:
    """
    Combines all de-escalation pressure mechanisms into unified calculation.
    
    This is the main interface for the upgraded decision logic.
    """
    
    def __init__(
        self,
        time_decay: Optional[TimeDecayCosts] = None,
        intl_pressure: Optional[InternationalPressure] = None,
        econ_fatigue: Optional[EconomicFatigue] = None,
        reputation: Optional[ReputationBleeding] = None,
        config: Optional[Dict] = None,
    ):
        self.time_decay = time_decay or TimeDecayCosts()
        self.intl_pressure = intl_pressure or InternationalPressure()
        self.econ_fatigue = econ_fatigue or EconomicFatigue()
        self.reputation = reputation or ReputationBleeding()
        self.config = config or {}
        
        # Track restriction histories per state
        self.restriction_histories: Dict[str, Dict[str, RestrictionHistory]] = {}
        self.current_step = 0
    
    def update_step(self, step: int):
        """Advance simulation step."""
        self.current_step = step
        
        # Update all history records
        for state_histories in self.restriction_histories.values():
            for history in state_histories.values():
                history.current_step = step
    
    def record_restriction(
        self,
        state_id: str,
        sector: str,
        intensity: float
    ):
        """Record or update a restriction."""
        if state_id not in self.restriction_histories:
            self.restriction_histories[state_id] = {}
        
        histories = self.restriction_histories[state_id]
        
        if sector not in histories:
            histories[sector] = RestrictionHistory(
                sector=sector,
                intensity=intensity,
                start_step=self.current_step,
                current_step=self.current_step,
                peak_intensity=intensity,
            )
        else:
            h = histories[sector]
            h.intensity = intensity
            h.current_step = self.current_step
            h.peak_intensity = max(h.peak_intensity, intensity)
            if intensity > h.intensity:
                h.escalation_count += 1
    
    def calculate_deescalation_benefit(
        self,
        state_id: str,
        sector: str,
        current_intensity: float,
        proposed_reduction: float,
        state_params: Dict,
        opponent_diversification: float,
        third_parties: List[Dict],
        friction_level: float,
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate total benefit of de-escalating a restriction.
        
        Returns:
            Tuple of (total_benefit, breakdown_dict)
        """
        history = self.restriction_histories.get(state_id, {}).get(sector)
        if not history:
            return 0.0, {}
        
        breakdown = {}
        
        # 1. Pain relief (base model already has this)
        breakdown["pain_relief"] = proposed_reduction * state_params.get("self_harm", 0.1)
        
        # 2. Time-decay cost savings
        # If we de-escalate, we stop paying maintenance costs
        maintenance_saved = self.time_decay.calculate_maintenance_cost(
            history,
            state_params.get("self_harm", 0.1)
        ) * (proposed_reduction / max(0.01, current_intensity))
        breakdown["maintenance_saved"] = maintenance_saved
        
        # 3. International pressure relief
        # Partial de-escalation provides partial relief
        pressure = self.intl_pressure.calculate_pressure(
            state_id=state_id,
            friction_level=friction_level,
            restriction_duration_avg=history.duration,
            third_parties=third_parties,
            state_alignment=state_params.get("third_party_alignment", 0.0)
        )
        # Relief proportional to reduction
        relief_fraction = proposed_reduction / max(0.01, current_intensity)
        breakdown["pressure_relief"] = pressure * relief_fraction * 0.5  # Partial relief
        
        # 4. Economic fatigue relief
        fatigue = self.econ_fatigue.calculate_fatigue(
            cumulative_gdp_loss=state_params.get("gdp_loss", 0),
            conflict_duration=history.duration,
            regime_type=state_params.get("regime_type", "HYBRID"),
            approval_rating=state_params.get("approval", 0.5)
        )
        breakdown["fatigue_relief"] = fatigue * relief_fraction * 0.3
        
        # 5. Reputation recovery
        # De-escalation starts to repair reputation
        breakdown["reputation_recovery"] = (
            self.reputation.accumulated_damage * 0.1 * relief_fraction
        )
        
        # Total benefit
        total = sum(breakdown.values())
        
        return total, breakdown
    
    def calculate_escalation_penalty(
        self,
        state_id: str,
        sector: str,
        current_intensity: float,
        proposed_increase: float,
        state_params: Dict,
        opponent_diversification: float,
        third_parties: List[Dict],
        friction_level: float,
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate additional penalties for escalation beyond base model.
        
        These make escalation less attractive relative to de-escalation.
        """
        breakdown = {}
        
        # 1. Leverage decay - restrictions less effective over time
        history = self.restriction_histories.get(state_id, {}).get(sector)
        if history:
            leverage = self.time_decay.calculate_leverage_decay(
                history, opponent_diversification
            )
            # Reduce coercion benefit by decay factor
            expected_coercion = state_params.get("coercion_hope", 0.3) * proposed_increase
            breakdown["leverage_decay_cost"] = expected_coercion * (1 - leverage)
        
        # 2. International backlash
        # Escalation increases pressure
        current_pressure = self.intl_pressure.calculate_pressure(
            state_id=state_id,
            friction_level=friction_level,
            restriction_duration_avg=history.duration if history else 0,
            third_parties=third_parties,
        )
        # New pressure from escalation
        new_pressure = self.intl_pressure.calculate_pressure(
            state_id=state_id,
            friction_level=friction_level + proposed_increase * 0.1,
            restriction_duration_avg=(history.duration if history else 0) + 1,
            third_parties=third_parties,
        )
        breakdown["intl_backlash"] = max(0, new_pressure - current_pressure)
        
        # 3. Reputation cost
        breakdown["reputation_cost"] = self.reputation.monthly_bleed_rate * proposed_increase
        
        total = sum(breakdown.values())
        
        return total, breakdown
    
    def get_prolonged_restriction_pressure(
        self,
        state_id: str,
        state_params: Dict,
        third_parties: List[Dict],
        friction_level: float,
    ) -> float:
        """
        Calculate total pressure from all prolonged restrictions.
        
        This is added to the state's overall pain, creating pressure to de-escalate.
        """
        histories = self.restriction_histories.get(state_id, {})
        if not histories:
            return 0.0
        
        total_pressure = 0.0
        
        for sector, history in histories.items():
            if history.intensity < 0.1:
                continue
            
            # Time decay maintenance cost
            maintenance = self.time_decay.calculate_maintenance_cost(
                history,
                state_params.get("self_harm", {}).get(sector, 0.1)
            )
            total_pressure += maintenance
        
        # International pressure (aggregate)
        avg_duration = sum(h.duration for h in histories.values()) / max(1, len(histories))
        intl = self.intl_pressure.calculate_pressure(
            state_id=state_id,
            friction_level=friction_level,
            restriction_duration_avg=avg_duration,
            third_parties=third_parties,
            state_alignment=state_params.get("third_party_alignment", 0.0)
        )
        total_pressure += intl
        
        # Economic fatigue
        fatigue = self.econ_fatigue.calculate_fatigue(
            cumulative_gdp_loss=state_params.get("gdp_loss", 0),
            conflict_duration=int(avg_duration),
            regime_type=state_params.get("regime_type", "HYBRID"),
            approval_rating=state_params.get("approval", 0.5)
        )
        total_pressure += fatigue
        
        return total_pressure


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def upgrade_decision_logic(
    base_decide_action,
    deescalation_calc: DeescalationIncentiveCalculator,
):
    """
    Decorator to upgrade base decision logic with de-escalation incentives.
    
    Usage:
        calculator = DeescalationIncentiveCalculator()
        agent.decide_action = upgrade_decision_logic(
            agent.decide_action, 
            calculator
        )
    """
    def upgraded_decide_action(
        state,
        opponent,
        own_pain,
        opponent_pain,
        friction_level,
        **kwargs
    ):
        # First get base action
        base_result = base_decide_action(
            state, opponent, own_pain, opponent_pain, friction_level, **kwargs
        )
        
        # Add prolonged restriction pressure to own pain
        extra_pressure = deescalation_calc.get_prolonged_restriction_pressure(
            state_id=state.agent_id,
            state_params={
                "gdp_loss": state.cumulative_gdp_loss,
                "regime_type": state.regime_type.value,
                "approval": state.approval_rating,
                "self_harm": {},  # Would need sector-specific
            },
            third_parties=kwargs.get("third_parties", []),
            friction_level=friction_level,
        )
        
        adjusted_pain = own_pain + extra_pressure
        
        # Re-evaluate with adjusted pain
        # If pain now exceeds de-escalation threshold, prefer de-escalation
        if adjusted_pain > state.de_escalation_threshold:
            # Check if de-escalation has positive net benefit
            for sector, intensity in state.restriction_intensity.items():
                if intensity > 0.2:
                    benefit, _ = deescalation_calc.calculate_deescalation_benefit(
                        state_id=state.agent_id,
                        sector=sector,
                        current_intensity=intensity,
                        proposed_reduction=0.2,
                        state_params={
                            "gdp_loss": state.cumulative_gdp_loss,
                            "regime_type": state.regime_type.value,
                            "approval": state.approval_rating,
                        },
                        opponent_diversification=opponent.get_avg_diversification(),
                        third_parties=kwargs.get("third_parties", []),
                        friction_level=friction_level,
                    )
                    
                    # Compare to escalation penalty
                    if base_result and base_result.get("type") == "escalate":
                        penalty, _ = deescalation_calc.calculate_escalation_penalty(
                            state_id=state.agent_id,
                            sector=base_result.get("sector", sector),
                            current_intensity=0,
                            proposed_increase=0.2,
                            state_params={},
                            opponent_diversification=opponent.get_avg_diversification(),
                            third_parties=kwargs.get("third_parties", []),
                            friction_level=friction_level,
                        )
                        
                        # If de-escalation benefit > escalation net benefit, switch
                        if benefit > (base_result.get("net_benefit", 0) - penalty):
                            return {
                                "type": "de_escalate",
                                "sector": sector,
                                "intensity_change": -0.2,
                                "net_benefit": benefit,
                            }
        
        return base_result
    
    return upgraded_decide_action


# ============================================================================
# TESTING
# ============================================================================

def test_deescalation_module():
    """Test the de-escalation incentive calculations."""
    
    print("Testing De-escalation Dynamics Module")
    print("=" * 50)
    
    calc = DeescalationIncentiveCalculator()
    
    # Simulate a 24-month trade conflict
    for step in range(24):
        calc.update_step(step)
        
        if step == 0:
            calc.record_restriction("CHN", "rare_earths", 0.6)
        elif step == 6:
            calc.record_restriction("CHN", "rare_earths", 0.8)
        elif step == 12:
            calc.record_restriction("CHN", "rare_earths", 0.9)
    
    print("\nTime Decay Costs (months 0-24):")
    history = calc.restriction_histories["CHN"]["rare_earths"]
    for month in [0, 6, 12, 18, 24]:
        history.current_step = month
        cost = calc.time_decay.calculate_maintenance_cost(history, self_harm_base=0.4)
        print(f"  Month {month:2d}: maintenance cost = {cost:.4f}")
    
    print("\nLeverage Decay (vs opponent diversification):")
    for div in [0.0, 0.2, 0.4, 0.6]:
        leverage = calc.time_decay.calculate_leverage_decay(history, div)
        print(f"  Diversification {div:.1f}: leverage = {leverage:.3f}")
    
    print("\nInternational Pressure (friction levels):")
    third_parties = [
        {"intervention_threshold": 0.3, "coordination_bonus": 0.2},
        {"intervention_threshold": 0.5, "coordination_bonus": 0.1},
    ]
    for friction in [0.3, 0.4, 0.5, 0.6, 0.7]:
        pressure = calc.intl_pressure.calculate_pressure(
            state_id="CHN",
            friction_level=friction,
            restriction_duration_avg=18,
            third_parties=third_parties,
        )
        print(f"  Friction {friction:.1f}: pressure = {pressure:.4f}")
    
    print("\nEconomic Fatigue (GDP loss levels):")
    for gdp_loss in [0, 5, 10, 20, 40]:
        fatigue = calc.econ_fatigue.calculate_fatigue(
            cumulative_gdp_loss=gdp_loss,
            conflict_duration=18,
            regime_type="DEMOCRACY",
            approval_rating=0.4,
        )
        print(f"  GDP loss {gdp_loss:3d}: fatigue = {fatigue:.4f}")
    
    print("\nDe-escalation Benefit (sector: rare_earths, 0.8 -> 0.6):")
    benefit, breakdown = calc.calculate_deescalation_benefit(
        state_id="CHN",
        sector="rare_earths",
        current_intensity=0.8,
        proposed_reduction=0.2,
        state_params={
            "self_harm": 0.4,
            "gdp_loss": 15,
            "regime_type": "AUTOCRACY",
            "approval": 0.6,
            "third_party_alignment": -0.3,
        },
        opponent_diversification=0.35,
        third_parties=third_parties,
        friction_level=0.65,
    )
    print(f"  Total benefit: {benefit:.4f}")
    for k, v in breakdown.items():
        print(f"    {k}: {v:.4f}")
    
    print("\n" + "=" * 50)
    print("Module test complete.")


if __name__ == "__main__":
    test_deescalation_module()
