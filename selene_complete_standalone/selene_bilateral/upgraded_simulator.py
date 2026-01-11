#!/usr/bin/env python3
"""
Upgraded Bilateral Friction Simulator with De-escalation Dynamics
=================================================================

Integrates the de-escalation architecture fix into the core simulator.
This version adds time-decay costs, international pressure, economic fatigue,
and reputation bleeding to create realistic de-escalation incentives.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import random
import math

from selene_bilateral.state_agent import StateAgent, RegimeType
from selene_bilateral.sectors import SectorDependency, DependencyMatrix
from selene_bilateral.actions import ActionSpace
from selene_bilateral.third_party import ThirdParty, ThirdPartySystem
from selene_bilateral.deescalation_dynamics import (
    DeescalationIncentiveCalculator,
    TimeDecayCosts,
    InternationalPressure,
    EconomicFatigue,
    ReputationBleeding,
)


class OutcomeCategory(Enum):
    NORMALIZATION = "normalization"
    STABLE_INTERDEPENDENCE = "stable_interdependence"
    MANAGED_COMPETITION = "managed_competition"
    ESCALATION_SPIRAL = "escalation_spiral"
    GRADUAL_DECOUPLING = "gradual_decoupling"
    ASYMMETRIC_LOCK_IN = "asymmetric_lock_in"
    POLITICAL_RUPTURE = "political_rupture"


@dataclass
class StepRecord:
    step: int
    friction_level: float
    pain_a: float
    pain_b: float
    deescalation_pressure_a: float = 0.0
    deescalation_pressure_b: float = 0.0
    actions_taken: List[Dict] = field(default_factory=list)
    shocks: List[Dict] = field(default_factory=list)


@dataclass
class SimulationResult:
    outcome_category: OutcomeCategory
    steps_to_terminal: int
    peak_friction_level: float
    cumulative_gdp_loss_a: float
    cumulative_gdp_loss_b: float
    final_diversification_a: float
    final_diversification_b: float
    escalation_cycles: int
    deescalation_events: int  # NEW: track de-escalations
    history: List[StepRecord] = field(default_factory=list)


class UpgradedBilateralSimulator:
    """
    Bilateral friction simulator with de-escalation dynamics.
    
    Key improvements over base model:
    1. Time-decay costs for maintaining restrictions
    2. International pressure accumulation
    3. Economic fatigue from prolonged conflict
    4. Reputation bleeding from aggressive behavior
    5. Historical friction memory (prevents oscillation)
    """
    
    def __init__(
        self,
        state_a: StateAgent,
        state_b: StateAgent,
        dependency_matrix: DependencyMatrix,
        action_space: ActionSpace,
        third_party_system: Optional[ThirdPartySystem] = None,
        config: Optional[Dict] = None,
        deescalation_config: Optional[Dict] = None,
    ):
        self.state_a = state_a
        self.state_b = state_b
        self.dep_matrix = dependency_matrix
        self.action_space = action_space
        self.third_parties = third_party_system
        
        # Default config
        self.config = {
            "max_steps": 48,
            "pain_relief_coefficient": 0.4,
            "relationship_coefficient": 0.2,
            "audience_cost_base": 0.25,
            "reputation_coefficient": 0.15,
            "action_threshold": 0.03,
            "decision_noise": 0.04,
            "diversification_rate": 0.015,
        }
        if config:
            self.config.update(config)
        
        # De-escalation dynamics - TUNED UP from defaults
        deesc_cfg = deescalation_config or {}
        self.deesc_calc = DeescalationIncentiveCalculator(
            time_decay=TimeDecayCosts(
                base_maintenance_cost=deesc_cfg.get("maintenance_cost", 0.05),  # UP from 0.02
                time_acceleration_factor=deesc_cfg.get("time_accel", 0.15),     # UP from 0.08
                max_time_multiplier=deesc_cfg.get("max_time_mult", 4.0),
                grace_period=deesc_cfg.get("grace_period", 4),                   # DOWN from 6
            ),
            intl_pressure=InternationalPressure(
                base_pressure_rate=deesc_cfg.get("pressure_rate", 0.03),        # UP from 0.01
                duration_sensitivity=deesc_cfg.get("duration_sens", 0.08),      # UP from 0.05
                friction_threshold=deesc_cfg.get("friction_thresh", 0.35),      # DOWN from 0.4
                max_pressure=deesc_cfg.get("max_pressure", 0.4),                # UP from 0.3
            ),
            econ_fatigue=EconomicFatigue(
                fatigue_rate=deesc_cfg.get("fatigue_rate", 0.04),               # UP from 0.02
                gdp_loss_threshold=deesc_cfg.get("gdp_thresh", 3.0),            # DOWN from 5.0
                max_fatigue=deesc_cfg.get("max_fatigue", 0.35),                 # UP from 0.25
            ),
            reputation=ReputationBleeding(
                monthly_bleed_rate=deesc_cfg.get("bleed_rate", 0.01),           # UP from 0.005
                intensity_threshold=deesc_cfg.get("intensity_thresh", 0.4),     # DOWN from 0.5
            ),
            config=deesc_cfg,  # Pass full config for memory coefficients
        )
        
        # State tracking
        self.current_step = 0
        self.history: List[StepRecord] = []
        self.peak_friction = 0.0
        self.escalation_cycles = 0
        self.deescalation_events = 0
        
        # NEW: Historical friction memory (prevents oscillation)
        self.cumulative_friction_a = 0.0  # Accumulated friction from A's restrictions
        self.cumulative_friction_b = 0.0  # Accumulated friction from B's restrictions
        self.friction_memory_decay = deesc_cfg.get("friction_memory_decay", 0.85)  # Slow decay
        
        # Initialize restriction histories
        self._init_restriction_histories()
    
    def _init_restriction_histories(self):
        """Record initial restrictions in de-escalation calculator."""
        for sector, intensity in self.state_a.restriction_intensity.items():
            if intensity > 0:
                self.deesc_calc.record_restriction("A", sector, intensity)
        for sector, intensity in self.state_b.restriction_intensity.items():
            if intensity > 0:
                self.deesc_calc.record_restriction("B", sector, intensity)
    
    def get_friction_level(self) -> float:
        """Calculate current bilateral friction level."""
        a_friction = self.state_a.get_total_friction_level()
        b_friction = self.state_b.get_total_friction_level()
        return (a_friction + b_friction) / 2
    
    def calculate_pain(self, state: StateAgent, opponent: StateAgent) -> Tuple[float, float]:
        """
        Calculate economic and political pain for a state.
        
        Returns:
            (economic_pain, political_pain)
        """
        econ_pain = 0.0
        
        # Pain from opponent's restrictions
        for sector, dep in self.dep_matrix.sectors.items():
            opp_restriction = opponent.restriction_intensity.get(sector, 0)
            if opp_restriction > 0:
                if state == self.state_a:
                    # Pain to A from B's restrictions
                    criticality = dep.a_criticality_score
                    exposure = dep.b_exports_to_a
                    diversification = state.diversification_progress.get(sector, 0)
                else:
                    # Pain to B from A's restrictions
                    criticality = dep.b_criticality_score
                    exposure = dep.a_exports_to_b
                    diversification = state.diversification_progress.get(sector, 0)
                
                # Pain reduced by diversification
                effective_exposure = exposure * (1 - diversification * 0.7)
                econ_pain += opp_restriction * criticality * effective_exposure
        
        # Self-harm from own restrictions
        for sector, intensity in state.restriction_intensity.items():
            if intensity > 0 and sector in self.dep_matrix.sectors:
                dep = self.dep_matrix.sectors[sector]
                if state == self.state_a:
                    self_harm = dep.a_restriction_self_harm
                else:
                    self_harm = dep.b_restriction_self_harm
                econ_pain += intensity * self_harm
        
        # Political pain (simplified)
        polit_pain = (1 - state.approval_rating) * state.nationalism_index * 0.3
        
        return econ_pain, polit_pain
    
    def calculate_deescalation_pressure(self, state: StateAgent, friction: float) -> float:
        """Calculate additional pressure to de-escalate from architecture upgrade."""
        state_id = "A" if state == self.state_a else "B"
        
        # Get self-harm coefficients per sector
        self_harm = {}
        for sector, dep in self.dep_matrix.sectors.items():
            if state == self.state_a:
                self_harm[sector] = dep.a_restriction_self_harm
            else:
                self_harm[sector] = dep.b_restriction_self_harm
        
        # Third party info
        tp_list = []
        if self.third_parties:
            for tp in self.third_parties.parties.values():
                tp_list.append({
                    "intervention_threshold": tp.intervention_threshold,
                    "coordination_bonus": tp.coordination_bonus,
                })
        
        pressure = self.deesc_calc.get_prolonged_restriction_pressure(
            state_id=state_id,
            state_params={
                "gdp_loss": state.cumulative_gdp_loss,
                "regime_type": state.regime_type.value,
                "approval": state.approval_rating,
                "self_harm": self_harm,
                "third_party_alignment": 0.5 if state == self.state_a else -0.3,
            },
            third_parties=tp_list,
            friction_level=friction,
        )
        
        # NEW: Add pressure from cumulative friction memory
        # This prevents oscillation by "remembering" past high friction
        memory_coef = self.deesc_calc.config.get("memory_coefficient", 0.20)
        if state == self.state_a:
            memory_pressure = self.cumulative_friction_a * memory_coef
        else:
            memory_pressure = self.cumulative_friction_b * memory_coef
        
        # NEW: Peak reputation pressure - once you've been aggressive, reputation sticks
        peak_coef = self.deesc_calc.config.get("peak_coefficient", 0.15)
        peak_reputation_pressure = self.peak_friction * peak_coef
        
        return pressure + memory_pressure + peak_reputation_pressure
    
    def decide_action(
        self,
        state: StateAgent,
        opponent: StateAgent,
        own_pain: float,
        opponent_pain: float,
        deesc_pressure: float,
    ) -> Optional[Dict]:
        """
        Upgraded decision logic with de-escalation incentives.
        """
        state_id = "A" if state == self.state_a else "B"
        friction = self.get_friction_level()
        
        # Adjust pain with de-escalation pressure
        adjusted_pain = own_pain + deesc_pressure
        
        best_action = None
        best_net_benefit = -999
        
        # Get third party info
        tp_list = []
        if self.third_parties:
            for tp in self.third_parties.parties.values():
                tp_list.append({
                    "intervention_threshold": tp.intervention_threshold,
                    "coordination_bonus": tp.coordination_bonus,
                })
        
        # EVALUATE ESCALATION OPTIONS
        for sector in self.dep_matrix.sectors:
            current = state.restriction_intensity.get(sector, 0)
            if current < 1.0:  # Can escalate
                # Base escalation benefit
                coercion_hope = state.coercion_hope_coefficient
                opponent_exposure = self._get_opponent_exposure(state, opponent, sector)
                
                benefit = coercion_hope * opponent_exposure * 0.5
                
                # Nationalism boost
                if state.nationalism_index > 0.5:
                    benefit += state.proactive_nationalism_coefficient * 0.2
                
                # Retaliation response (if opponent restricted us)
                if opponent.restriction_intensity.get(sector, 0) > 0:
                    benefit += state.retaliation_propensity * 0.3
                
                # PENALTIES (upgraded)
                cost = 0.0
                
                # Self-harm
                dep = self.dep_matrix.sectors[sector]
                if state == self.state_a:
                    cost += 0.2 * dep.a_restriction_self_harm
                else:
                    cost += 0.2 * dep.b_restriction_self_harm
                
                # NEW: Re-escalation penalty (flip-flop cost)
                # If we previously had higher restrictions in this sector, re-escalating looks bad
                # This captures the "once you back down, face cost prevents re-escalation"
                history = self.deesc_calc.restriction_histories.get(state_id, {}).get(sector)
                if history and history.peak_intensity > current + 0.1:
                    # We've backed down before - re-escalating is very costly
                    reescalation_penalty = 0.50 * (history.peak_intensity - current)
                    # Additional penalty based on how many times we've de-escalated
                    if self.deescalation_events > 0:
                        reescalation_penalty += 0.10 * min(5, self.deescalation_events)
                    cost += reescalation_penalty
                
                # NEW: Escalation penalty from architecture
                penalty, _ = self.deesc_calc.calculate_escalation_penalty(
                    state_id=state_id,
                    sector=sector,
                    current_intensity=current,
                    proposed_increase=0.2,
                    state_params={},
                    opponent_diversification=opponent.get_avg_diversification(),
                    third_parties=tp_list,
                    friction_level=friction,
                )
                cost += penalty
                
                net = benefit - cost + random.gauss(0, self.config["decision_noise"])
                
                if net > best_net_benefit and net > self.config["action_threshold"]:
                    if adjusted_pain > state.escalation_threshold or benefit > 0.3:
                        best_action = {
                            "type": "escalate",
                            "sector": sector,
                            "intensity_change": 0.2,
                            "net_benefit": net,
                        }
                        best_net_benefit = net
        
        # EVALUATE DE-ESCALATION OPTIONS
        for sector, current in state.restriction_intensity.items():
            if current > 0.1:  # Can de-escalate
                # NEW: De-escalation benefit from architecture
                benefit, breakdown = self.deesc_calc.calculate_deescalation_benefit(
                    state_id=state_id,
                    sector=sector,
                    current_intensity=current,
                    proposed_reduction=0.2,
                    state_params={
                        "self_harm": self._get_self_harm(state, sector),
                        "gdp_loss": state.cumulative_gdp_loss,
                        "regime_type": state.regime_type.value,
                        "approval": state.approval_rating,
                    },
                    opponent_diversification=opponent.get_avg_diversification(),
                    third_parties=tp_list,
                    friction_level=friction,
                )
                
                # Add base pain relief
                benefit += current * 0.3  # Relief from ending restriction
                
                # Costs of de-escalation
                cost = 0.0
                
                # Audience cost (looking weak)
                audience = self.config["audience_cost_base"]
                if state.regime_type == RegimeType.DEMOCRACY:
                    audience *= 1.2
                elif state.regime_type == RegimeType.AUTOCRACY:
                    audience *= 0.5
                cost += audience * state.nationalism_index
                
                # Weakness signal
                cost += state.weakness_signal_coefficient * 0.15
                
                net = benefit - cost + random.gauss(0, self.config["decision_noise"])
                
                # De-escalation triggered by adjusted pain
                if adjusted_pain > state.de_escalation_threshold:
                    net += 0.1  # Bonus when in pain
                
                if net > best_net_benefit and net > self.config["action_threshold"]:
                    best_action = {
                        "type": "de_escalate",
                        "sector": sector,
                        "intensity_change": -0.2,
                        "net_benefit": net,
                    }
                    best_net_benefit = net
        
        return best_action
    
    def _get_opponent_exposure(
        self, state: StateAgent, opponent: StateAgent, sector: str
    ) -> float:
        """Get opponent's exposure to restrictions in a sector."""
        if sector not in self.dep_matrix.sectors:
            return 0.0
        dep = self.dep_matrix.sectors[sector]
        if state == self.state_a:
            return dep.a_exports_to_b * dep.b_criticality_score
        else:
            return dep.b_exports_to_a * dep.a_criticality_score
    
    def _get_self_harm(self, state: StateAgent, sector: str) -> float:
        """Get self-harm coefficient for a sector."""
        if sector not in self.dep_matrix.sectors:
            return 0.1
        dep = self.dep_matrix.sectors[sector]
        if state == self.state_a:
            return dep.a_restriction_self_harm
        return dep.b_restriction_self_harm
    
    def apply_action(self, state: StateAgent, action: Dict) -> Dict:
        """Apply an action and return record."""
        sector = action["sector"]
        change = action["intensity_change"]
        
        old_intensity = state.restriction_intensity.get(sector, 0)
        new_intensity = max(0, min(1.0, old_intensity + change))
        state.restriction_intensity[sector] = new_intensity
        
        # Record in de-escalation calculator
        state_id = "A" if state == self.state_a else "B"
        self.deesc_calc.record_restriction(state_id, sector, new_intensity)
        
        # Track events
        if action["type"] == "de_escalate":
            self.deescalation_events += 1
        elif action["type"] == "escalate":
            if old_intensity == 0:
                self.escalation_cycles += 1
        
        return {
            "actor": state_id,
            "type": action["type"],
            "sector": sector,
            "from_intensity": old_intensity,
            "to_intensity": new_intensity,
        }
    
    def update_diversification(self):
        """States diversify away from restricted sectors."""
        rate = self.config["diversification_rate"]
        
        for sector in self.dep_matrix.sectors:
            # A diversifies if B restricts
            if self.state_b.restriction_intensity.get(sector, 0) > 0.2:
                current = self.state_a.diversification_progress.get(sector, 0)
                intensity = self.state_b.restriction_intensity[sector]
                progress = rate * (1 + intensity)
                self.state_a.diversification_progress[sector] = min(1.0, current + progress)
            
            # B diversifies if A restricts
            if self.state_a.restriction_intensity.get(sector, 0) > 0.2:
                current = self.state_b.diversification_progress.get(sector, 0)
                intensity = self.state_a.restriction_intensity[sector]
                progress = rate * (1 + intensity)
                self.state_b.diversification_progress[sector] = min(1.0, current + progress)
    
    def step(self) -> StepRecord:
        """Execute one simulation step."""
        friction = self.get_friction_level()
        self.peak_friction = max(self.peak_friction, friction)
        
        # Calculate pain
        econ_a, polit_a = self.calculate_pain(self.state_a, self.state_b)
        econ_b, polit_b = self.calculate_pain(self.state_b, self.state_a)
        
        pain_a = econ_a * 0.7 + polit_a * 0.3
        pain_b = econ_b * 0.7 + polit_b * 0.3
        
        # Calculate de-escalation pressure (NEW)
        deesc_a = self.calculate_deescalation_pressure(self.state_a, friction)
        deesc_b = self.calculate_deescalation_pressure(self.state_b, friction)
        
        # Accumulate GDP loss
        self.state_a.cumulative_gdp_loss += econ_a
        self.state_b.cumulative_gdp_loss += econ_b
        
        # Decisions
        actions_taken = []
        
        action_a = self.decide_action(
            self.state_a, self.state_b, pain_a, pain_b, deesc_a
        )
        if action_a:
            record = self.apply_action(self.state_a, action_a)
            actions_taken.append(record)
        
        action_b = self.decide_action(
            self.state_b, self.state_a, pain_b, pain_a, deesc_b
        )
        if action_b:
            record = self.apply_action(self.state_b, action_b)
            actions_taken.append(record)
        
        # Update diversification
        self.update_diversification()
        
        # Update de-escalation calculator step
        self.deesc_calc.update_step(self.current_step)
        
        # NEW: Update cumulative friction memory (prevents oscillation)
        a_friction = self.state_a.get_total_friction_level()
        b_friction = self.state_b.get_total_friction_level()
        self.cumulative_friction_a = (self.cumulative_friction_a * self.friction_memory_decay) + a_friction * 0.2
        self.cumulative_friction_b = (self.cumulative_friction_b * self.friction_memory_decay) + b_friction * 0.2
        
        # Record
        step_record = StepRecord(
            step=self.current_step,
            friction_level=friction,
            pain_a=pain_a,
            pain_b=pain_b,
            deescalation_pressure_a=deesc_a,
            deescalation_pressure_b=deesc_b,
            actions_taken=actions_taken,
        )
        self.history.append(step_record)
        self.current_step += 1
        
        return step_record
    
    def classify_outcome(self) -> OutcomeCategory:
        """Classify the simulation outcome."""
        friction = self.get_friction_level()
        div_a = self.state_a.get_avg_diversification()
        div_b = self.state_b.get_avg_diversification()
        
        # Check for de-escalation success (true normalization = very low friction + low diversification)
        # If diversification is high, it's decoupling, not normalization
        if friction < 0.10 and self.peak_friction > 0.4 and div_a < 0.4 and div_b < 0.4:
            return OutcomeCategory.NORMALIZATION
        
        if friction > 0.75:
            return OutcomeCategory.ESCALATION_SPIRAL
        
        # Decoupling: significant diversification by either side
        if div_a > 0.5 or div_b > 0.5:
            return OutcomeCategory.GRADUAL_DECOUPLING
        
        if friction < 0.20:
            return OutcomeCategory.STABLE_INTERDEPENDENCE
        
        if (div_a > 0.6 and div_b < 0.3) or (div_b > 0.6 and div_a < 0.3):
            return OutcomeCategory.ASYMMETRIC_LOCK_IN
        
        return OutcomeCategory.MANAGED_COMPETITION
    
    def run(self) -> SimulationResult:
        """Run simulation to completion."""
        max_steps = self.config["max_steps"]
        
        for _ in range(max_steps):
            self.step()
            
            # Early termination conditions
            friction = self.get_friction_level()
            if friction > 0.9:  # Spiral out of control
                break
            if friction < 0.1 and self.current_step > 12:  # Normalized
                break
        
        outcome = self.classify_outcome()
        
        return SimulationResult(
            outcome_category=outcome,
            steps_to_terminal=self.current_step,
            peak_friction_level=self.peak_friction,
            cumulative_gdp_loss_a=self.state_a.cumulative_gdp_loss,
            cumulative_gdp_loss_b=self.state_b.cumulative_gdp_loss,
            final_diversification_a=self.state_a.get_avg_diversification(),
            final_diversification_b=self.state_b.get_avg_diversification(),
            escalation_cycles=self.escalation_cycles,
            deescalation_events=self.deescalation_events,
            history=self.history,
        )


if __name__ == "__main__":
    print("Upgraded Bilateral Simulator module loaded.")
    print("Use run_2026_upgraded.py to run scenarios.")
