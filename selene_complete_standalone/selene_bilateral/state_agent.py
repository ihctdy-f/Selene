"""
State Agent module for Selene Bilateral Friction Extension
Handles sovereign state actors with graduated friction postures.

Key difference from ConsortiumAgent:
- Actions are continuous (0-100% intensity per sector)
- Decisions based on pain/gain calculus, not defection probability
- Includes audience costs and signaling dynamics
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import random


class RegimeType(Enum):
    """Political system classification affecting decision dynamics."""
    DEMOCRACY = "democracy"         # High audience costs, election cycles
    HYBRID = "hybrid"               # Mixed constraints
    AUTOCRACY = "autocracy"         # Lower audience costs, longer horizons


@dataclass
class PainAssessment:
    """Quantified impact of friction on a state."""
    economic: float         # GDP/trade impact
    political: float        # Domestic political cost
    reputational: float     # International standing
    total: float            # Weighted combination
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "economic": round(self.economic, 4),
            "political": round(self.political, 4),
            "reputational": round(self.reputational, 4),
            "total": round(self.total, 4),
        }


@dataclass
class StateAgent:
    """
    Represents a sovereign state in bilateral friction scenario.
    
    Unlike ConsortiumAgent (binary defect/cooperate), StateAgent
    chooses continuous intensity levels across multiple sectors.
    """
    
    # Identity
    agent_id: str                               # e.g., "JPN", "CHN"
    name: str                                   # e.g., "Japan", "China"
    
    # Economic fundamentals
    gdp: float = 5.0                            # Trillion USD
    trade_openness: float = 0.3                 # Trade/GDP ratio
    
    # Political state
    regime_type: RegimeType = RegimeType.DEMOCRACY
    leader_tenure: int = 3                      # Years in power
    approval_rating: float = 0.5                # 0-1 scale
    nationalism_index: float = 0.5             # 0-1, affects audience costs
    
    # Current friction posture (sector -> intensity 0-1)
    restriction_intensity: Dict[str, float] = field(default_factory=dict)
    
    # Accumulated costs
    cumulative_gdp_loss: float = 0.0
    cumulative_reputation_cost: float = 0.0
    cumulative_pain_inflicted: float = 0.0     # Pain caused to opponent
    
    # Decision parameters (can be calibrated)
    escalation_threshold: float = 0.3          # Pain level triggering escalation
    de_escalation_threshold: float = 0.6       # Pain level triggering backing down
    signaling_preference: float = 0.5          # 0=substance focus, 1=theater focus
    retaliation_propensity: float = 0.7        # How likely to respond to opponent action
    
    # State tracking
    steps_at_current_level: int = 0
    last_action_step: int = -1
    diversification_progress: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize empty dicts if needed."""
        if self.restriction_intensity is None:
            self.restriction_intensity = {}
        if self.diversification_progress is None:
            self.diversification_progress = {}
    
    def get_total_friction_level(self) -> float:
        """Average restriction intensity across all active sectors."""
        if not self.restriction_intensity:
            return 0.0
        return sum(self.restriction_intensity.values()) / len(self.restriction_intensity)
    
    def get_audience_cost_multiplier(self) -> float:
        """
        Calculate audience cost multiplier based on regime type and nationalism.
        
        Higher = harder to back down after public escalation.
        Democracies with high nationalism face highest audience costs.
        """
        base_cost = {
            RegimeType.DEMOCRACY: 1.0,
            RegimeType.HYBRID: 0.6,
            RegimeType.AUTOCRACY: 0.3,
        }[self.regime_type]
        
        # Nationalism amplifies audience costs
        nationalism_multiplier = 1.0 + self.nationalism_index * 0.5
        
        # Low approval makes backing down harder (need to look strong)
        approval_factor = 1.0 + (1 - self.approval_rating) * 0.3
        
        return base_cost * nationalism_multiplier * approval_factor
    
    def calculate_escalation_benefit(
        self,
        sector: str,
        proposed_intensity: float,
        opponent_pain: float,
        config: Dict[str, Any]
    ) -> float:
        """
        Calculate expected benefit from escalating in a sector.
        
        Benefits:
        - Coercion value (opponent might back down)
        - Domestic political boost (nationalism satisfaction)
        - Signaling value (reputation for toughness)
        - Proactive nationalism (desire to act even without provocation)
        """
        current_intensity = self.restriction_intensity.get(sector, 0.0)
        intensity_delta = proposed_intensity - current_intensity
        
        if intensity_delta <= 0:
            return 0.0
        
        # Coercion hope: belief that pain will make opponent concede
        coercion_coefficient = config.get("coercion_coefficient", 0.3)
        coercion_value = opponent_pain * coercion_coefficient * intensity_delta
        
        # Domestic boost: nationalism satisfaction
        domestic_coefficient = config.get("domestic_boost_coefficient", 0.2)
        domestic_boost = self.nationalism_index * domestic_coefficient * intensity_delta
        
        # Signaling: reputation for resolve
        signaling_coefficient = config.get("signaling_coefficient", 0.15)
        signaling_value = signaling_coefficient * intensity_delta * self.signaling_preference
        
        # Proactive nationalism: desire to act even without provocation
        # Higher nationalism = more likely to initiate friction
        # Low approval = more likely to seek nationalist distraction
        proactive_coefficient = config.get("proactive_nationalism_coefficient", 0.15)
        approval_desperation = max(0, 0.5 - self.approval_rating)  # Boost if approval < 0.5
        proactive_value = (self.nationalism_index * proactive_coefficient + 
                          approval_desperation * 0.2) * intensity_delta
        
        return coercion_value + domestic_boost + signaling_value + proactive_value
    
    def calculate_escalation_cost(
        self,
        sector: str,
        proposed_intensity: float,
        self_harm: float,
        retaliation_risk: float,
        config: Dict[str, Any]
    ) -> float:
        """
        Calculate expected cost from escalating.
        
        Costs:
        - Self-harm (own economy hurt)
        - Retaliation risk (opponent escalates back)
        - Reputation cost (international standing)
        """
        current_intensity = self.restriction_intensity.get(sector, 0.0)
        intensity_delta = proposed_intensity - current_intensity
        
        if intensity_delta <= 0:
            return 0.0
        
        # Direct self-harm
        self_harm_cost = self_harm * intensity_delta
        
        # Expected retaliation
        retaliation_coefficient = config.get("retaliation_fear_coefficient", 0.4)
        expected_retaliation = retaliation_risk * retaliation_coefficient * intensity_delta
        
        # International reputation
        reputation_coefficient = config.get("reputation_coefficient", 0.1)
        reputation_cost = reputation_coefficient * intensity_delta
        
        return self_harm_cost + expected_retaliation + reputation_cost
    
    def calculate_de_escalation_benefit(
        self,
        sector: str,
        proposed_intensity: float,
        current_self_pain: float,
        config: Dict[str, Any]
    ) -> float:
        """
        Calculate benefit from reducing friction.
        
        Benefits:
        - Pain relief (reduced self-harm)
        - Relationship improvement
        - International reputation recovery
        """
        current_intensity = self.restriction_intensity.get(sector, 0.0)
        intensity_delta = current_intensity - proposed_intensity  # Positive = reduction
        
        if intensity_delta <= 0:
            return 0.0
        
        # Pain relief
        relief_coefficient = config.get("pain_relief_coefficient", 0.5)
        pain_relief = current_self_pain * relief_coefficient * intensity_delta
        
        # Relationship benefit
        relationship_coefficient = config.get("relationship_coefficient", 0.2)
        relationship_benefit = relationship_coefficient * intensity_delta
        
        return pain_relief + relationship_benefit
    
    def calculate_de_escalation_cost(
        self,
        sector: str,
        proposed_intensity: float,
        config: Dict[str, Any]
    ) -> float:
        """
        Calculate cost of backing down.
        
        Costs:
        - Audience cost (looking weak domestically)
        - Weakness signal (opponent may push harder)
        """
        current_intensity = self.restriction_intensity.get(sector, 0.0)
        intensity_delta = current_intensity - proposed_intensity
        
        if intensity_delta <= 0:
            return 0.0
        
        # Audience cost (regime-dependent)
        audience_multiplier = self.get_audience_cost_multiplier()
        audience_cost = audience_multiplier * intensity_delta * 0.3
        
        # Weakness signal
        weakness_coefficient = config.get("weakness_signal_coefficient", 0.2)
        weakness_cost = weakness_coefficient * intensity_delta
        
        return audience_cost + weakness_cost
    
    def decide_action(
        self,
        opponent: 'StateAgent',
        own_pain: PainAssessment,
        opponent_pain: PainAssessment,
        available_actions: List[Dict[str, Any]],
        config: Dict[str, Any],
        step: int
    ) -> Optional[Dict[str, Any]]:
        """
        Core decision logic: choose whether and how to adjust friction.
        
        Returns action dict or None if no change.
        """
        # Check if we should even consider action this step
        action_cooldown = config.get("action_cooldown", 2)
        if step - self.last_action_step < action_cooldown:
            return None
        
        best_action = None
        best_net_benefit = 0.0
        
        # Get escalation pressure from environment (shocks, nationalism)
        base_escalation_pressure = config.get("escalatory_pressure", 0.0)
        
        for action in available_actions:
            sector = action["sector"]
            current = self.restriction_intensity.get(sector, 0.0)
            
            # Consider escalation
            if current < action.get("max_intensity", 1.0):
                escalation_target = min(current + 0.2, action.get("max_intensity", 1.0))
                
                benefit = self.calculate_escalation_benefit(
                    sector, escalation_target, opponent_pain.total, config
                )
                cost = self.calculate_escalation_cost(
                    sector, escalation_target,
                    action.get("self_harm_coefficient", 0.1),
                    opponent.retaliation_propensity,
                    config
                )
                
                net = benefit - cost
                
                # Escalation pressure from shocks
                net += base_escalation_pressure * 0.1
                
                # Pain threshold check: more likely to escalate if in pain
                if own_pain.total > self.escalation_threshold:
                    net *= 1.3  # Boost escalation appeal when hurting
                
                # Retaliation: if opponent just escalated, we're more likely to respond
                if opponent.get_total_friction_level() > 0.1:
                    net += self.retaliation_propensity * 0.1
                
                if net > best_net_benefit:
                    best_net_benefit = net
                    best_action = {
                        "type": "escalate",
                        "sector": sector,
                        "from_intensity": current,
                        "to_intensity": escalation_target,
                        "net_benefit": net,
                    }
            
            # Consider de-escalation
            if current > 0.0:
                de_escalation_target = max(current - 0.2, 0.0)
                
                benefit = self.calculate_de_escalation_benefit(
                    sector, de_escalation_target, own_pain.total, config
                )
                cost = self.calculate_de_escalation_cost(
                    sector, de_escalation_target, config
                )
                
                net = benefit - cost
                
                # Pain threshold check: more likely to de-escalate if really hurting
                if own_pain.total > self.de_escalation_threshold:
                    net *= 1.5  # Boost de-escalation appeal when pain is high
                
                if net > best_net_benefit:
                    best_net_benefit = net
                    best_action = {
                        "type": "de_escalate",
                        "sector": sector,
                        "from_intensity": current,
                        "to_intensity": de_escalation_target,
                        "net_benefit": net,
                    }
        
        # Add randomness to prevent deterministic cycles
        noise = random.gauss(0, config.get("decision_noise", 0.05))
        
        if best_action and best_net_benefit + noise > config.get("action_threshold", 0.05):
            return best_action
        
        return None
    
    def apply_action(self, action: Dict[str, Any], step: int):
        """Apply a chosen action, updating restriction intensity."""
        sector = action["sector"]
        new_intensity = action["to_intensity"]
        
        self.restriction_intensity[sector] = new_intensity
        self.last_action_step = step
        
        if new_intensity == 0.0 and sector in self.restriction_intensity:
            # Clean up zero entries
            pass  # Keep for tracking
    
    def apply_pain(self, pain: PainAssessment, step: int):
        """Record accumulated pain from opponent's restrictions."""
        self.cumulative_gdp_loss += pain.economic
        self.cumulative_reputation_cost += pain.reputational
        
        # Pain affects approval rating (but gradually)
        approval_hit = pain.political * 0.01  # Reduced from 0.02
        self.approval_rating = max(0.1, self.approval_rating - approval_hit)
    
    def progress_diversification(self, sector: str, rate: float = 0.02):
        """
        Advance supply chain diversification in a sector.
        
        Diversification reduces future pain from opponent restrictions.
        """
        current = self.diversification_progress.get(sector, 0.0)
        self.diversification_progress[sector] = min(1.0, current + rate)
    
    def get_diversification_modifier(self, sector: str) -> float:
        """
        Get pain reduction from diversification.
        
        Returns multiplier (0.5 = 50% pain reduction).
        """
        progress = self.diversification_progress.get(sector, 0.0)
        # Diversification up to 50% pain reduction
        return 1.0 - (progress * 0.5)
    
    def get_avg_diversification(self) -> float:
        """Get average diversification progress across all sectors."""
        if not self.diversification_progress:
            return 0.0
        return sum(self.diversification_progress.values()) / max(1, len(self.diversification_progress))
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for logging."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "gdp": self.gdp,
            "regime_type": self.regime_type.value,
            "approval_rating": round(self.approval_rating, 3),
            "nationalism_index": round(self.nationalism_index, 3),
            "restriction_intensity": {k: round(v, 3) for k, v in self.restriction_intensity.items()},
            "total_friction": round(self.get_total_friction_level(), 3),
            "cumulative_gdp_loss": round(self.cumulative_gdp_loss, 4),
            "cumulative_reputation_cost": round(self.cumulative_reputation_cost, 4),
            "diversification_progress": {k: round(v, 3) for k, v in self.diversification_progress.items()},
        }
    
    def __repr__(self):
        friction = self.get_total_friction_level()
        return f"StateAgent({self.name}, friction={friction:.2f}, approval={self.approval_rating:.2f})"


def create_state_from_config(config: Dict[str, Any]) -> StateAgent:
    """Factory function to create StateAgent from YAML config."""
    regime_map = {
        "democracy": RegimeType.DEMOCRACY,
        "hybrid": RegimeType.HYBRID,
        "autocracy": RegimeType.AUTOCRACY,
    }
    
    return StateAgent(
        agent_id=config["agent_id"],
        name=config.get("name", config["agent_id"]),
        gdp=config.get("gdp", 5.0),
        trade_openness=config.get("trade_openness", 0.3),
        regime_type=regime_map.get(config.get("regime_type", "democracy"), RegimeType.DEMOCRACY),
        leader_tenure=config.get("leader_tenure", 3),
        approval_rating=config.get("approval_rating", 0.5),
        nationalism_index=config.get("nationalism_index", 0.5),
        escalation_threshold=config.get("escalation_threshold", 0.3),
        de_escalation_threshold=config.get("de_escalation_threshold", 0.6),
        signaling_preference=config.get("signaling_preference", 0.5),
        retaliation_propensity=config.get("retaliation_propensity", 0.7),
    )
