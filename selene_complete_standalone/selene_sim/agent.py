"""
Agent module for Project Selene Consortium Simulator v2.0
Handles heterogeneous agent profiles, defection logic, and domestic politics.
"""

import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class AgentType(Enum):
    """Agent classification following Track A/B structure from white papers."""
    TRACK_A_CORE = "track_a_core"      # EU, Ukraine - protected founders
    TRACK_B_CORE = "track_b_core"      # China, Russia - multipolar track
    ASSOCIATE = "associate"             # UAE, India, Brazil - can switch
    STRATEGIC_TENANT = "tenant"         # US/NASA - no governance, commercial rights
    PRIVATE_SECTOR = "private"          # SpaceX etc - contract-bound


@dataclass
class AgentProfile:
    """
    Configuration profile for agent type.
    Loaded from config, not hardcoded.
    """
    base_defection_prob: float          # Starting defection probability
    sunk_cost_sensitivity: float        # How much sunk costs reduce defection (0-1)
    revenue_sensitivity: float          # How much revenue reduces defection
    domestic_veto_risk: float           # EDC-style domestic politics risk
    has_veto_rights: bool               # Can block strategic decisions
    can_switch_tracks: bool             # Associate-only feature
    min_phase_for_veto_exposure: int    # When domestic politics kicks in
    lc_access: bool                     # Lunar Credit system access


# Default profiles - can be overridden by config
DEFAULT_PROFILES: Dict[AgentType, AgentProfile] = {
    AgentType.TRACK_A_CORE: AgentProfile(
        base_defection_prob=0.35,
        sunk_cost_sensitivity=0.8,      # Strong lock-in
        revenue_sensitivity=0.7,
        domestic_veto_risk=0.4,         # Democratic accountability
        has_veto_rights=True,
        can_switch_tracks=False,
        min_phase_for_veto_exposure=3,
        lc_access=True
    ),
    AgentType.TRACK_B_CORE: AgentProfile(
        base_defection_prob=0.45,
        sunk_cost_sensitivity=0.6,
        revenue_sensitivity=0.5,
        domestic_veto_risk=0.2,         # Less democratic pressure
        has_veto_rights=True,
        can_switch_tracks=False,
        min_phase_for_veto_exposure=4,
        lc_access=True
    ),
    AgentType.ASSOCIATE: AgentProfile(
        base_defection_prob=0.25,
        sunk_cost_sensitivity=0.4,
        revenue_sensitivity=0.8,        # ROI-driven
        domestic_veto_risk=0.3,
        has_veto_rights=False,
        can_switch_tracks=True,
        min_phase_for_veto_exposure=3,
        lc_access=True
    ),
    AgentType.STRATEGIC_TENANT: AgentProfile(
        base_defection_prob=0.15,
        sunk_cost_sensitivity=0.2,      # Minimal lock-in
        revenue_sensitivity=0.9,        # Very market-driven
        domestic_veto_risk=0.5,         # High democratic exposure
        has_veto_rights=False,
        can_switch_tracks=False,
        min_phase_for_veto_exposure=2,
        lc_access=False                 # Uses USD
    ),
    AgentType.PRIVATE_SECTOR: AgentProfile(
        base_defection_prob=0.10,
        sunk_cost_sensitivity=0.1,
        revenue_sensitivity=0.95,       # Extreme market sensitivity
        domestic_veto_risk=0.0,         # No domestic politics
        has_veto_rights=False,
        can_switch_tracks=False,
        min_phase_for_veto_exposure=99, # Never
        lc_access=True
    ),
}


@dataclass
class ConsortiumAgent:
    """
    A single participant in the consortium.
    
    Tracks state over simulation phases and makes defection decisions
    based on profile, accumulated investment, and external conditions.
    """
    agent_id: str
    agent_type: AgentType
    name: str                                   # Human-readable (e.g., "EU/ESA")
    
    # Dynamic state
    trust_level: float = 0.5                    # Trust in consortium (0-1)
    public_approval: float = 0.6                # Domestic support (0-1)
    leadership_stability: float = 0.7           # Government stability (0-1)
    sunk_cost: float = 0.0                      # Accumulated investment (€B)
    lc_balance: float = 0.0                     # Lunar Credit holdings
    equity_share: float = 0.0                   # Ownership percentage
    
    # Status flags
    active: bool = True
    defected: bool = False
    defection_phase: Optional[int] = None
    defection_reason: Optional[str] = None
    
    # Profile (loaded at init)
    profile: AgentProfile = field(default_factory=lambda: DEFAULT_PROFILES[AgentType.ASSOCIATE])
    
    def __post_init__(self):
        """Load profile based on agent type if not provided."""
        if self.profile is None or isinstance(self.profile, type(field)):
            self.profile = DEFAULT_PROFILES.get(self.agent_type, DEFAULT_PROFILES[AgentType.ASSOCIATE])
    
    def calculate_defection_probability(
        self,
        current_phase: int,
        global_state: Dict[str, Any],
        config: Dict[str, Any]
    ) -> float:
        """
        Core decision logic. Returns probability of defecting this phase.
        
        Implements the formula from ODD protocol:
        P(defect) = base * trust_modifier - sunk_cost_effect - lc_effect + shock_effect + domestic_effect
        
        Key insight: Trust level directly scales base defection probability.
        High trust (0.8+) dramatically reduces defection risk.
        """
        if not self.active or self.defected:
            return 0.0
        
        base = self.profile.base_defection_prob
        max_sunk_cost = config.get("max_sunk_cost", 50.0)  # €50B default
        
        # TRUST EFFECT (REDUCES defection) - THIS IS THE KEY MECHANIC
        # trust_level 1.0 -> multiply base by 0.3 (70% reduction)
        # trust_level 0.5 -> multiply base by 0.65 (35% reduction)
        # trust_level 0.0 -> multiply base by 1.0 (no reduction)
        trust_effect = 1.0 - (self.trust_level * 0.7)
        base = base * trust_effect
        
        # Sunk cost effect (REDUCES defection)
        # As investment grows, defection becomes more costly
        sunk_cost_ratio = min(1.0, self.sunk_cost / max_sunk_cost)
        sunk_cost_effect = base * self.profile.sunk_cost_sensitivity * sunk_cost_ratio
        
        # Lunar Credit wealth effect (REDUCES defection)
        # Wealth in consortium currency incentivizes staying
        lc_threshold = config.get("lc_wealth_threshold", 500.0)
        lc_effect = 0.1 * min(1.0, self.lc_balance / lc_threshold) if self.profile.lc_access else 0.0
        
        # External shock effect (INCREASES defection)
        political_volatility = global_state.get("political_volatility", 0.0)
        shock_multiplier = config.get("shock_multiplier", 0.3)
        shock_effect = political_volatility * shock_multiplier
        
        # Domestic politics effect (INCREASES defection)
        # EDC-style: low public approval + advanced phase = veto risk
        domestic_effect = 0.0
        if current_phase >= self.profile.min_phase_for_veto_exposure:
            if self.public_approval < config.get("approval_danger_threshold", 0.3):
                domestic_effect = self.profile.domestic_veto_risk * (1 - self.public_approval)
        
        # Leadership instability amplifies negative effects only
        instability_factor = (1 - self.leadership_stability) * 0.3
        
        # Calculate final probability
        probability = base - sunk_cost_effect - lc_effect + (shock_effect + domestic_effect) * (1 + instability_factor)
        
        # Clamp to valid range with floor/ceiling
        floor = config.get("defection_floor", 0.02)
        ceiling = config.get("defection_ceiling", 0.95)
        return max(floor, min(ceiling, probability))
    
    def decide_defection(
        self,
        current_phase: int,
        global_state: Dict[str, Any],
        config: Dict[str, Any]
    ) -> bool:
        """
        Make defection decision for this phase.
        Returns True if agent defects.
        """
        if not self.active or self.defected:
            return False
        
        prob = self.calculate_defection_probability(current_phase, global_state, config)
        
        if random.random() < prob:
            self.defect(current_phase, reason="calculated_defection")
            return True
        return False
    
    def domestic_veto_check(
        self,
        current_phase: int,
        config: Dict[str, Any]
    ) -> bool:
        """
        EDC-style domestic politics check.
        Separate from regular defection - represents involuntary withdrawal.
        """
        if not self.active or self.defected:
            return False
        
        if current_phase < self.profile.min_phase_for_veto_exposure:
            return False
        
        if self.public_approval < config.get("approval_danger_threshold", 0.3):
            veto_roll = random.random()
            if veto_roll < self.profile.domestic_veto_risk:
                self.defect(current_phase, reason="domestic_veto")
                return True
        
        return False
    
    def defect(self, phase: int, reason: str = "unknown"):
        """Mark agent as defected."""
        self.active = False
        self.defected = True
        self.defection_phase = phase
        self.defection_reason = reason
    
    def invest(self, amount: float):
        """Add to sunk costs."""
        self.sunk_cost += amount
    
    def receive_lc(self, amount: float):
        """Receive Lunar Credits (from revenue distribution)."""
        self.lc_balance += amount
    
    def receive_forfeiture(self, amount: float, lc_amount: float = 0.0):
        """Receive forfeited assets from departing agent."""
        self.sunk_cost += amount
        self.lc_balance += lc_amount
    
    def update_domestic_state(
        self,
        approval_delta: float = 0.0,
        stability_delta: float = 0.0
    ):
        """Update domestic political conditions."""
        self.public_approval = max(0.0, min(1.0, self.public_approval + approval_delta))
        self.leadership_stability = max(0.0, min(1.0, self.leadership_stability + stability_delta))
    
    def update_trust(self, delta: float):
        """Update trust level."""
        self.trust_level = max(0.0, min(1.0, self.trust_level + delta))
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent state for logging/output."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "active": self.active,
            "defected": self.defected,
            "defection_phase": self.defection_phase,
            "defection_reason": self.defection_reason,
            "trust_level": round(self.trust_level, 3),
            "public_approval": round(self.public_approval, 3),
            "leadership_stability": round(self.leadership_stability, 3),
            "sunk_cost": round(self.sunk_cost, 2),
            "lc_balance": round(self.lc_balance, 2),
            "equity_share": round(self.equity_share, 3),
        }
    
    def __repr__(self):
        status = "ACTIVE" if self.active else f"DEFECTED@{self.defection_phase}"
        return f"Agent({self.name}, {self.agent_type.value}, {status}, €{self.sunk_cost:.1f}B)"


def create_agent_from_config(agent_config: Dict[str, Any]) -> ConsortiumAgent:
    """
    Factory function to create agent from YAML/JSON config.
    
    Example config:
    {
        "agent_id": "eu_esa",
        "name": "EU/ESA",
        "agent_type": "track_a_core",
        "equity_share": 0.25,
        "initial_trust": 0.6,
        "initial_approval": 0.5
    }
    """
    agent_type = AgentType(agent_config.get("agent_type", "associate"))
    
    # Allow profile overrides from config
    profile = DEFAULT_PROFILES[agent_type]
    if "profile_overrides" in agent_config:
        overrides = agent_config["profile_overrides"]
        profile = AgentProfile(
            base_defection_prob=overrides.get("base_defection_prob", profile.base_defection_prob),
            sunk_cost_sensitivity=overrides.get("sunk_cost_sensitivity", profile.sunk_cost_sensitivity),
            revenue_sensitivity=overrides.get("revenue_sensitivity", profile.revenue_sensitivity),
            domestic_veto_risk=overrides.get("domestic_veto_risk", profile.domestic_veto_risk),
            has_veto_rights=overrides.get("has_veto_rights", profile.has_veto_rights),
            can_switch_tracks=overrides.get("can_switch_tracks", profile.can_switch_tracks),
            min_phase_for_veto_exposure=overrides.get("min_phase_for_veto_exposure", profile.min_phase_for_veto_exposure),
            lc_access=overrides.get("lc_access", profile.lc_access),
        )
    
    return ConsortiumAgent(
        agent_id=agent_config["agent_id"],
        agent_type=agent_type,
        name=agent_config.get("name", agent_config["agent_id"]),
        trust_level=agent_config.get("initial_trust", 0.5),
        public_approval=agent_config.get("initial_approval", 0.6),
        leadership_stability=agent_config.get("initial_stability", 0.7),
        equity_share=agent_config.get("equity_share", 0.1),
        profile=profile,
    )
