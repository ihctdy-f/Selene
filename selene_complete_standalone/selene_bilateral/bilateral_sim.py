"""
Main simulator for Selene Bilateral Friction Extension.

Orchestrates the simulation loop:
1. Generate shocks
2. Apply shock effects to states
3. States decide actions (graduated friction)
4. Calculate pain from restrictions
5. Third parties react
6. States diversify supply chains
7. Update state and record metrics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import random
import copy

from .state_agent import StateAgent, PainAssessment, create_state_from_config
from .sectors import DependencyMatrix, create_japan_china_matrix
from .actions import ActionSpace, create_japan_china_action_space
from .third_party import ThirdPartySystem, create_japan_china_third_parties
from .shocks import BilateralShockGenerator


class OutcomeCategory(Enum):
    """Terminal outcome classification (from spec Section 6.2)."""
    STABLE_INTERDEPENDENCE = "stable_interdependence"   # Friction < 0.2 after 24 months
    MANAGED_COMPETITION = "managed_competition"          # Friction 0.2-0.5, stable
    GRADUAL_DECOUPLING = "gradual_decoupling"           # High diversification both sides
    ESCALATION_SPIRAL = "escalation_spiral"             # Friction > 0.7, still rising
    ASYMMETRIC_LOCK_IN = "asymmetric_lock_in"           # One diversifies, other doesn't
    NORMALIZATION = "normalization"                      # Friction returns to < 0.1
    POLITICAL_RUPTURE = "political_rupture"             # Domestic crisis ends game


@dataclass
class SimulationMetrics:
    """Outcome measures for each simulation run."""
    
    outcome_category: OutcomeCategory
    steps_to_terminal: int
    
    # Economic impact
    cumulative_gdp_loss_a: float
    cumulative_gdp_loss_b: float
    peak_friction_level: float
    
    # Supply chain evolution
    final_diversification_a: float
    final_diversification_b: float
    
    # Political dynamics
    escalation_cycles: int
    third_party_interventions: int
    shock_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome_category": self.outcome_category.value,
            "steps_to_terminal": self.steps_to_terminal,
            "cumulative_gdp_loss_a": round(self.cumulative_gdp_loss_a, 4),
            "cumulative_gdp_loss_b": round(self.cumulative_gdp_loss_b, 4),
            "peak_friction_level": round(self.peak_friction_level, 3),
            "final_diversification_a": round(self.final_diversification_a, 3),
            "final_diversification_b": round(self.final_diversification_b, 3),
            "escalation_cycles": self.escalation_cycles,
            "third_party_interventions": self.third_party_interventions,
            "shock_count": self.shock_count,
        }


@dataclass
class StepRecord:
    """Record of a single simulation step."""
    step: int
    friction_level: float
    state_a: Dict[str, Any]
    state_b: Dict[str, Any]
    actions_taken: List[Dict[str, Any]]
    shocks: List[Dict[str, Any]]
    third_party_status: Dict[str, Any]
    pain_a: Dict[str, float]
    pain_b: Dict[str, float]


class BilateralFrictionSimulator:
    """
    Main simulation engine for bilateral economic friction.
    
    Handles:
    - State agent decisions
    - Dependency-based pain calculations
    - Third party interventions
    - External shocks
    - Diversification dynamics
    """
    
    def __init__(
        self,
        state_a: StateAgent,
        state_b: StateAgent,
        dependency_matrix: DependencyMatrix,
        action_space: ActionSpace,
        third_party_system: ThirdPartySystem,
        config: Dict[str, Any] = None
    ):
        self.state_a = state_a
        self.state_b = state_b
        self.dependency_matrix = dependency_matrix
        self.action_space = action_space
        self.third_party_system = third_party_system
        self.config = config or {}
        
        # Initialize shock generator
        self.shock_generator = BilateralShockGenerator(self.config)
        
        # Simulation state
        self.current_step = 0
        self.history: List[StepRecord] = []
        
        # Tracking metrics
        self.peak_friction = 0.0
        self.escalation_cycles = 0
        self.last_friction_direction = 0  # 1=rising, -1=falling
        self.total_shocks = 0
        self.third_party_intervention_count = 0
        
        # Decision parameters from config
        self.steps_per_month = self.config.get("steps_per_month", 1)
        self.max_steps = self.config.get("max_steps", 48)  # 4 years default
        self.decision_config = {
            "coercion_coefficient": self.config.get("coercion_coefficient", 0.3),
            "domestic_boost_coefficient": self.config.get("domestic_boost_coefficient", 0.2),
            "signaling_coefficient": self.config.get("signaling_coefficient", 0.15),
            "retaliation_fear_coefficient": self.config.get("retaliation_fear_coefficient", 0.4),
            "reputation_coefficient": self.config.get("reputation_coefficient", 0.1),
            "pain_relief_coefficient": self.config.get("pain_relief_coefficient", 0.5),
            "relationship_coefficient": self.config.get("relationship_coefficient", 0.2),
            "weakness_signal_coefficient": self.config.get("weakness_signal_coefficient", 0.2),
            "action_cooldown": self.config.get("action_cooldown", 2),
            "action_threshold": self.config.get("action_threshold", 0.05),
            "decision_noise": self.config.get("decision_noise", 0.05),
            "third_party_activation_multiplier": self.config.get("third_party_activation_multiplier", 1.0),
            "third_party_cooldown": self.config.get("third_party_cooldown", 6),
            "diversification_rate": self.config.get("diversification_rate", 0.02),
        }
    
    def get_friction_level(self) -> float:
        """Calculate overall friction level (average of both states' restrictions)."""
        a_friction = self.state_a.get_total_friction_level()
        b_friction = self.state_b.get_total_friction_level()
        return (a_friction + b_friction) / 2
    
    def step(self) -> StepRecord:
        """Execute one simulation step."""
        
        friction = self.get_friction_level()
        
        # 1. Generate and apply shocks
        new_shocks = self.shock_generator.generate_shocks(
            self.current_step,
            friction,
            self.state_a,
            self.state_b
        )
        self.total_shocks += len(new_shocks)
        
        shock_effects = self.shock_generator.get_aggregate_shock_effect()
        self._apply_shock_effects(shock_effects)
        
        # 2. Calculate current pain levels
        pain_a = self.dependency_matrix.calculate_pain_to_a(
            self.state_b.restriction_intensity,
            self.state_a.diversification_progress,
            self.current_step,
            self.steps_per_month
        )
        
        pain_b = self.dependency_matrix.calculate_pain_to_b(
            self.state_a.restriction_intensity,
            self.state_b.diversification_progress,
            self.current_step,
            self.steps_per_month
        )
        
        # Add self-harm from own restrictions
        self_harm_a = self.dependency_matrix.calculate_self_harm("A", self.state_a.restriction_intensity)
        self_harm_b = self.dependency_matrix.calculate_self_harm("B", self.state_b.restriction_intensity)
        
        pain_a = PainAssessment(
            economic=pain_a.economic + self_harm_a,
            political=pain_a.political,
            reputational=pain_a.reputational,
            total=pain_a.total + self_harm_a * 0.5
        )
        
        pain_b = PainAssessment(
            economic=pain_b.economic + self_harm_b,
            political=pain_b.political,
            reputational=pain_b.reputational,
            total=pain_b.total + self_harm_b * 0.5
        )
        
        # Apply pain to states
        self.state_a.apply_pain(pain_a, self.current_step)
        self.state_b.apply_pain(pain_b, self.current_step)
        
        # 3. Third party reactions
        newly_active = self.third_party_system.update_activations(
            friction, self.current_step, self.decision_config
        )
        self.third_party_intervention_count += len(newly_active)
        
        # Get third party support
        support_a = self.third_party_system.get_aggregate_support("A", friction, self.decision_config)
        support_b = self.third_party_system.get_aggregate_support("B", friction, self.decision_config)
        
        # Modify pain based on third party support (alternative supply reduces pain)
        pain_a_modified = PainAssessment(
            economic=pain_a.economic * (1 - support_a["supply"] * 0.3),
            political=pain_a.political * (1 - support_a["coordination"] * 0.2),
            reputational=pain_a.reputational,
            total=pain_a.total * (1 - support_a["supply"] * 0.2)
        )
        
        pain_b_modified = PainAssessment(
            economic=pain_b.economic * (1 - support_b["supply"] * 0.3),
            political=pain_b.political * (1 - support_b["coordination"] * 0.2),
            reputational=pain_b.reputational,
            total=pain_b.total * (1 - support_b["supply"] * 0.2)
        )
        
        # 4. State decisions
        actions_taken = []
        
        # Adjust decision parameters based on shock pressure
        modified_config = self.decision_config.copy()
        modified_config["escalatory_pressure"] = shock_effects["escalatory_pressure"]
        if shock_effects["escalatory_pressure"] > 0:
            # Escalatory shocks make states more aggressive
            modified_config["action_threshold"] *= (1 - shock_effects["escalatory_pressure"] * 0.3)
        
        # State A decides
        available_a = self.action_space.get_available_escalations("A", self.state_a.restriction_intensity)
        available_a.extend(self.action_space.get_available_de_escalations("A", self.state_a.restriction_intensity))
        
        action_a = self.state_a.decide_action(
            self.state_b,
            pain_a_modified,
            pain_b,
            available_a,
            modified_config,
            self.current_step
        )
        
        if action_a:
            self.state_a.apply_action(action_a, self.current_step)
            actions_taken.append({"actor": "A", **action_a})
            
            # Record restriction timing for dependency matrix
            if action_a["type"] == "escalate":
                self.dependency_matrix.record_restriction_start("A", action_a["sector"], self.current_step)
            elif action_a["type"] == "de_escalate" and action_a["to_intensity"] == 0:
                self.dependency_matrix.clear_restriction("A", action_a["sector"])
        
        # State B decides
        available_b = self.action_space.get_available_escalations("B", self.state_b.restriction_intensity)
        available_b.extend(self.action_space.get_available_de_escalations("B", self.state_b.restriction_intensity))
        
        action_b = self.state_b.decide_action(
            self.state_a,
            pain_b_modified,
            pain_a,
            available_b,
            modified_config,
            self.current_step
        )
        
        if action_b:
            self.state_b.apply_action(action_b, self.current_step)
            actions_taken.append({"actor": "B", **action_b})
            
            if action_b["type"] == "escalate":
                self.dependency_matrix.record_restriction_start("B", action_b["sector"], self.current_step)
            elif action_b["type"] == "de_escalate" and action_b["to_intensity"] == 0:
                self.dependency_matrix.clear_restriction("B", action_b["sector"])
        
        # 5. Diversification progress
        self._advance_diversification()
        
        # 6. Update tracking metrics
        new_friction = self.get_friction_level()
        
        if new_friction > self.peak_friction:
            self.peak_friction = new_friction
        
        # Track escalation cycles
        if new_friction > friction + 0.05:
            if self.last_friction_direction == -1:
                self.escalation_cycles += 1
            self.last_friction_direction = 1
        elif new_friction < friction - 0.05:
            self.last_friction_direction = -1
        
        # 7. Record step
        record = StepRecord(
            step=self.current_step,
            friction_level=new_friction,
            state_a=self.state_a.to_dict(),
            state_b=self.state_b.to_dict(),
            actions_taken=actions_taken,
            shocks=[s.to_dict() for s in new_shocks],
            third_party_status=self.third_party_system.to_dict(),
            pain_a=pain_a.to_dict(),
            pain_b=pain_b.to_dict(),
        )
        
        self.history.append(record)
        self.current_step += 1
        
        return record
    
    def _apply_shock_effects(self, effects: Dict[str, Any]):
        """Apply aggregate shock effects to states."""
        # Nationalism adjustments (capped)
        self.state_a.nationalism_index = max(0.2, min(0.9,
            self.state_a.nationalism_index + effects["nationalism_delta_a"]
        ))
        self.state_b.nationalism_index = max(0.2, min(0.9,
            self.state_b.nationalism_index + effects["nationalism_delta_b"]
        ))
        
        # Approval adjustments (with tighter bounds, scaled down impact)
        self.state_a.approval_rating = max(0.2, min(0.85,
            self.state_a.approval_rating + effects["approval_delta_a"] * 0.5
        ))
        self.state_b.approval_rating = max(0.2, min(0.85,
            self.state_b.approval_rating + effects["approval_delta_b"] * 0.5
        ))
    
    def _advance_diversification(self):
        """Progress supply chain diversification based on current restrictions."""
        base_rate = self.decision_config["diversification_rate"]
        
        # State A diversifies away from sectors where B is restricting
        for sector, intensity in self.state_b.restriction_intensity.items():
            if intensity > 0.2:  # Only diversify if meaningful restriction
                rate = base_rate * (1 + intensity)
                self.state_a.progress_diversification(sector, rate)
        
        # State B diversifies away from sectors where A is restricting
        for sector, intensity in self.state_a.restriction_intensity.items():
            if intensity > 0.2:
                rate = base_rate * (1 + intensity)
                self.state_b.progress_diversification(sector, rate)
    
    def check_terminal_condition(self) -> Optional[OutcomeCategory]:
        """Check if simulation should terminate and classify outcome."""
        
        if self.current_step < 12:
            return None  # Minimum runtime
        
        friction = self.get_friction_level()
        
        # Political rupture check - only if approval critically low
        if self.state_a.approval_rating < 0.1 or self.state_b.approval_rating < 0.1:
            return OutcomeCategory.POLITICAL_RUPTURE
        
        # Time-based checks (after 24 steps / months)
        if self.current_step >= 24:
            avg_diversification_a = sum(self.state_a.diversification_progress.values()) / max(1, len(self.state_a.diversification_progress)) if self.state_a.diversification_progress else 0
            avg_diversification_b = sum(self.state_b.diversification_progress.values()) / max(1, len(self.state_b.diversification_progress)) if self.state_b.diversification_progress else 0
            
            # Stable interdependence
            if friction < 0.2:
                return OutcomeCategory.STABLE_INTERDEPENDENCE
            
            # Normalization
            if friction < 0.1 and self.peak_friction > 0.3:
                return OutcomeCategory.NORMALIZATION
            
            # Gradual decoupling
            if avg_diversification_a > 0.6 and avg_diversification_b > 0.6:
                return OutcomeCategory.GRADUAL_DECOUPLING
            
            # Asymmetric lock-in
            if (avg_diversification_a > 0.6 and avg_diversification_b < 0.3) or \
               (avg_diversification_b > 0.6 and avg_diversification_a < 0.3):
                return OutcomeCategory.ASYMMETRIC_LOCK_IN
            
            # Escalation spiral
            if friction > 0.7 and self.last_friction_direction == 1:
                return OutcomeCategory.ESCALATION_SPIRAL
            
            # Managed competition (default stable high-friction state)
            if 0.2 <= friction <= 0.5 and self.current_step >= 36:
                recent_friction = [r.friction_level for r in self.history[-12:]]
                friction_variance = max(recent_friction) - min(recent_friction)
                if friction_variance < 0.15:
                    return OutcomeCategory.MANAGED_COMPETITION
        
        # Max steps reached
        if self.current_step >= self.max_steps:
            friction = self.get_friction_level()
            if friction < 0.2:
                return OutcomeCategory.STABLE_INTERDEPENDENCE
            elif friction > 0.7:
                return OutcomeCategory.ESCALATION_SPIRAL
            else:
                return OutcomeCategory.MANAGED_COMPETITION
        
        return None
    
    def run(self) -> SimulationMetrics:
        """Run simulation to completion."""
        
        outcome = None
        
        while outcome is None:
            self.step()
            outcome = self.check_terminal_condition()
        
        # Calculate final metrics
        avg_div_a = sum(self.state_a.diversification_progress.values()) / max(1, len(self.state_a.diversification_progress)) if self.state_a.diversification_progress else 0
        avg_div_b = sum(self.state_b.diversification_progress.values()) / max(1, len(self.state_b.diversification_progress)) if self.state_b.diversification_progress else 0
        
        return SimulationMetrics(
            outcome_category=outcome,
            steps_to_terminal=self.current_step,
            cumulative_gdp_loss_a=self.state_a.cumulative_gdp_loss,
            cumulative_gdp_loss_b=self.state_b.cumulative_gdp_loss,
            peak_friction_level=self.peak_friction,
            final_diversification_a=avg_div_a,
            final_diversification_b=avg_div_b,
            escalation_cycles=self.escalation_cycles,
            third_party_interventions=self.third_party_intervention_count,
            shock_count=self.total_shocks,
        )
    
    def reset(self):
        """Reset simulator to initial state (for batch runs)."""
        self.current_step = 0
        self.history = []
        self.peak_friction = 0.0
        self.escalation_cycles = 0
        self.last_friction_direction = 0
        self.total_shocks = 0
        self.third_party_intervention_count = 0
        
        self.shock_generator.reset()
        self.third_party_system.reset()
        self.dependency_matrix.restriction_start_times = {"A": {}, "B": {}}


def create_japan_china_simulator(config: Dict[str, Any] = None) -> BilateralFrictionSimulator:
    """
    Factory function for Japan-China bilateral friction simulator.
    
    Uses default Japan-China configuration.
    """
    config = config or {}
    
    # Create Japan (State A)
    japan_config = {
        "agent_id": "JPN",
        "name": "Japan",
        "gdp": 4.2,
        "trade_openness": 0.35,
        "regime_type": "democracy",
        "leader_tenure": config.get("jpn_leader_tenure", 3),
        "approval_rating": config.get("jpn_approval", 0.45),
        "nationalism_index": config.get("jpn_nationalism", 0.5),
        "escalation_threshold": config.get("jpn_escalation_threshold", 0.35),
        "de_escalation_threshold": config.get("jpn_de_escalation_threshold", 0.55),
        "signaling_preference": config.get("jpn_signaling_preference", 0.4),
        "retaliation_propensity": config.get("jpn_retaliation_propensity", 0.6),
    }
    japan = create_state_from_config(japan_config)
    
    # Create China (State B)
    china_config = {
        "agent_id": "CHN",
        "name": "China",
        "gdp": 17.7,
        "trade_openness": 0.38,
        "regime_type": "autocracy",
        "leader_tenure": config.get("chn_leader_tenure", 12),
        "approval_rating": config.get("chn_approval", 0.7),
        "nationalism_index": config.get("chn_nationalism", 0.6),
        "escalation_threshold": config.get("chn_escalation_threshold", 0.3),
        "de_escalation_threshold": config.get("chn_de_escalation_threshold", 0.65),
        "signaling_preference": config.get("chn_signaling_preference", 0.6),
        "retaliation_propensity": config.get("chn_retaliation_propensity", 0.75),
    }
    china = create_state_from_config(china_config)
    
    # Create components
    dependency_matrix = create_japan_china_matrix()
    action_space = create_japan_china_action_space()
    third_party_system = create_japan_china_third_parties()
    
    return BilateralFrictionSimulator(
        state_a=japan,
        state_b=china,
        dependency_matrix=dependency_matrix,
        action_space=action_space,
        third_party_system=third_party_system,
        config=config
    )


def run_batch(
    num_runs: int = 100,
    config: Dict[str, Any] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run batch simulation and return aggregate statistics.
    """
    config = config or {}
    
    results = []
    outcome_counts = {cat.value: 0 for cat in OutcomeCategory}
    
    for i in range(num_runs):
        sim = create_japan_china_simulator(config)
        metrics = sim.run()
        results.append(metrics)
        outcome_counts[metrics.outcome_category.value] += 1
        
        if verbose and (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/{num_runs} runs...")
    
    # Aggregate statistics
    avg_gdp_loss_a = sum(r.cumulative_gdp_loss_a for r in results) / num_runs
    avg_gdp_loss_b = sum(r.cumulative_gdp_loss_b for r in results) / num_runs
    avg_peak_friction = sum(r.peak_friction_level for r in results) / num_runs
    avg_steps = sum(r.steps_to_terminal for r in results) / num_runs
    avg_div_a = sum(r.final_diversification_a for r in results) / num_runs
    avg_div_b = sum(r.final_diversification_b for r in results) / num_runs
    avg_escalation_cycles = sum(r.escalation_cycles for r in results) / num_runs
    
    return {
        "num_runs": num_runs,
        "outcome_distribution": {k: v / num_runs for k, v in outcome_counts.items()},
        "outcome_counts": outcome_counts,
        "averages": {
            "gdp_loss_a": round(avg_gdp_loss_a, 4),
            "gdp_loss_b": round(avg_gdp_loss_b, 4),
            "peak_friction": round(avg_peak_friction, 3),
            "steps_to_terminal": round(avg_steps, 1),
            "diversification_a": round(avg_div_a, 3),
            "diversification_b": round(avg_div_b, 3),
            "escalation_cycles": round(avg_escalation_cycles, 2),
        },
    }
