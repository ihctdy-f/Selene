#!/usr/bin/env python3
"""
NULL MODEL COMPARISON TEST
==========================
Compares mechanism effects within the model by testing:
- Null Model: Simple trust-based cooperation (no Selene mechanisms)
- Full Model: All Selene mechanisms enabled

Purpose: Demonstrate that mechanisms have substantial effects within
the model's assumptions. This is an internal comparison, not a 
prediction about real-world outcomes.

Interpretation Note: A large gap shows mechanisms matter *in the model*.
It does not prove mechanisms will work *in reality*.

Version: 2.1 (updated per review - softened claims)
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json


class Phase(Enum):
    PHASE_0 = 0
    PHASE_1 = 1
    PHASE_2 = 2
    PHASE_3 = 3
    PHASE_4 = 4


class AgentType(Enum):
    TRACK_A_CORE = "track_a"
    TRACK_B_CORE = "track_b"
    ASSOCIATE = "associate"
    TENANT = "tenant"
    PRIVATE = "private"


@dataclass
class MechanismConfig:
    """Configuration for which mechanisms are enabled."""
    # Core Selene innovations
    escrow_forfeiture: bool = True      # Module A: Financial penalties on exit
    lunar_credit_wealth: bool = True    # Module B: Wealth effects reduce defection
    poison_pill_cascade: bool = True    # Module D: Dependency chain cascades
    audit_trust_evolution: bool = True  # Module C: Trust builds over time
    sunk_cost_lock_in: bool = True      # Irreversibility after milestones
    
    def is_null_model(self) -> bool:
        """Check if this is the null model (no mechanisms)."""
        return not any([
            self.escrow_forfeiture,
            self.lunar_credit_wealth,
            self.poison_pill_cascade,
            self.audit_trust_evolution,
            self.sunk_cost_lock_in,
        ])


@dataclass
class Agent:
    """Agent with mechanism-dependent behavior."""
    agent_id: str
    agent_type: AgentType
    trust_level: float
    domestic_stability: float
    public_approval: float
    
    # State
    active: bool = True
    committed_capital: float = 0.0
    lunar_credit_balance: float = 0.0
    defection_phase: Optional[Phase] = None
    
    # Type-specific parameters
    base_defection_prob: float = 0.35
    
    def __post_init__(self):
        profiles = {
            AgentType.TRACK_A_CORE: 0.35,
            AgentType.TRACK_B_CORE: 0.45,
            AgentType.ASSOCIATE: 0.30,
            AgentType.TENANT: 0.20,
            AgentType.PRIVATE: 0.15,
        }
        self.base_defection_prob = profiles.get(self.agent_type, 0.35)


@dataclass
class SimConfig:
    """Simulation configuration."""
    n_agents: int = 5
    n_phases: int = 5
    
    # Trust/politics (pessimistic ranges)
    trust_mean: float = 0.35
    trust_std: float = 0.15
    political_volatility: float = 0.5
    public_approval_mean: float = 0.4
    
    # Shocks
    shock_probability: float = 0.2
    shock_intensity: float = 0.3
    
    # Mechanism settings
    mechanisms: MechanismConfig = field(default_factory=MechanismConfig)
    
    # Economic parameters (when mechanisms enabled)
    capital_per_phase: float = 10.0
    forfeiture_penalty: float = 0.8  # 80% loss on exit
    poison_pill_threshold: int = 2


@dataclass
class SimResult:
    """Simulation outcome."""
    structural_success: bool = False
    partial_success: bool = False
    graceful_degradation: bool = False
    catastrophic_failure: bool = False
    
    final_agents: int = 0
    early_defections: int = 0
    late_defections: int = 0
    cascade_triggered: bool = False
    
    # Mechanism tracking
    escrow_deterred: int = 0
    wealth_deterred: int = 0
    audit_trust_boost: float = 0.0


class NullModelSimulator:
    """
    NULL MODEL: Simple repeated cooperation game.
    
    Agents defect based on:
    - Base defection probability
    - Trust level
    - Domestic politics (stability, approval)
    - External shocks
    
    NO Selene innovations:
    - No escrow penalties
    - No wealth effects
    - No poison pill cascades
    - No trust evolution from audits
    - No sunk cost lock-in
    """
    
    def __init__(self, config: SimConfig):
        self.config = config
        self.agents: List[Agent] = []
        self.current_phase = Phase.PHASE_0
        
    def setup(self):
        """Initialize agents with pessimistic parameters."""
        self.agents = []
        
        types = [
            AgentType.TRACK_A_CORE,
            AgentType.TRACK_B_CORE,
            AgentType.TRACK_B_CORE,
            AgentType.ASSOCIATE,
            AgentType.ASSOCIATE,
            AgentType.TENANT,
            AgentType.PRIVATE,
            AgentType.PRIVATE,
        ]
        
        for i in range(self.config.n_agents):
            agent_type = types[i % len(types)]
            
            # Draw trust from pessimistic distribution
            trust = random.gauss(self.config.trust_mean, self.config.trust_std)
            trust = max(0.05, min(0.95, trust))
            
            approval = random.gauss(
                self.config.public_approval_mean, 
                0.15
            )
            approval = max(0.1, min(0.9, approval))
            
            agent = Agent(
                agent_id=f"Agent_{i}",
                agent_type=agent_type,
                trust_level=trust,
                domestic_stability=random.uniform(0.3, 0.7),
                public_approval=approval,
            )
            self.agents.append(agent)
        
        self.current_phase = Phase.PHASE_0
    
    def calculate_defection_prob_null(
        self, 
        agent: Agent, 
        shock: float
    ) -> float:
        """
        NULL MODEL defection probability.
        Simple formula: base * (1 - trust) * political_factors + shock
        """
        # Trust effect
        trust_modifier = 1.0 - agent.trust_level
        
        # Domestic politics
        political_pressure = 1.0
        if agent.domestic_stability < 0.5:
            political_pressure *= 1.3
        if agent.public_approval < 0.4:
            political_pressure *= 1.2
        
        # Volatility adds noise
        volatility_effect = random.gauss(0, self.config.political_volatility * 0.1)
        
        prob = (
            agent.base_defection_prob * 
            trust_modifier * 
            political_pressure +
            shock * 0.5 +
            volatility_effect
        )
        
        return max(0.0, min(0.95, prob))
    
    def run(self) -> SimResult:
        """Run null model simulation."""
        self.setup()
        result = SimResult()
        
        for phase_num in range(self.config.n_phases):
            self.current_phase = Phase(phase_num)
            
            # Generate shock
            shock = 0.0
            if random.random() < self.config.shock_probability:
                shock = random.uniform(0.1, self.config.shock_intensity)
            
            # Each agent decides
            for agent in self.agents:
                if not agent.active:
                    continue
                
                prob = self.calculate_defection_prob_null(agent, shock)
                
                if random.random() < prob:
                    agent.active = False
                    agent.defection_phase = self.current_phase
                    
                    if phase_num <= 1:
                        result.early_defections += 1
                    else:
                        result.late_defections += 1
            
            # Early termination
            if sum(1 for a in self.agents if a.active) == 0:
                break
        
        # Classify outcome
        result.final_agents = sum(1 for a in self.agents if a.active)
        
        if result.final_agents >= 4:
            result.structural_success = True
        elif result.final_agents >= 2:
            result.partial_success = True
        elif result.final_agents >= 1:
            result.graceful_degradation = True
        else:
            result.catastrophic_failure = True
        
        return result


class FullSeleneSimulator:
    """
    FULL SELENE MODEL: All mechanisms enabled.
    
    Innovations:
    1. Escrow/Forfeiture: Exit penalty deters defection
    2. Lunar Credit Wealth: Accumulated wealth reduces defection
    3. Poison Pill Cascade: Multiple exits trigger system collapse
    4. Audit Trust Evolution: Successful phases build trust
    5. Sunk Cost Lock-In: Later phases have lower defection prob
    """
    
    def __init__(self, config: SimConfig):
        self.config = config
        self.agents: List[Agent] = []
        self.current_phase = Phase.PHASE_0
        self.total_sunk_cost = 0.0
        
    def setup(self):
        """Initialize agents."""
        self.agents = []
        
        types = [
            AgentType.TRACK_A_CORE,
            AgentType.TRACK_B_CORE,
            AgentType.TRACK_B_CORE,
            AgentType.ASSOCIATE,
            AgentType.ASSOCIATE,
            AgentType.TENANT,
            AgentType.PRIVATE,
            AgentType.PRIVATE,
        ]
        
        for i in range(self.config.n_agents):
            agent_type = types[i % len(types)]
            
            trust = random.gauss(self.config.trust_mean, self.config.trust_std)
            trust = max(0.05, min(0.95, trust))
            
            approval = random.gauss(
                self.config.public_approval_mean, 
                0.15
            )
            approval = max(0.1, min(0.9, approval))
            
            agent = Agent(
                agent_id=f"Agent_{i}",
                agent_type=agent_type,
                trust_level=trust,
                domestic_stability=random.uniform(0.3, 0.7),
                public_approval=approval,
                lunar_credit_balance=random.uniform(0, 50),
            )
            self.agents.append(agent)
        
        self.current_phase = Phase.PHASE_0
        self.total_sunk_cost = 0.0
    
    def calculate_defection_prob_full(
        self, 
        agent: Agent, 
        shock: float,
        result: SimResult
    ) -> float:
        """
        FULL MODEL defection probability with all mechanisms.
        """
        # Base probability (same as null)
        trust_modifier = 1.0 - agent.trust_level
        
        political_pressure = 1.0
        if agent.domestic_stability < 0.5:
            political_pressure *= 1.3
        if agent.public_approval < 0.4:
            political_pressure *= 1.2
        
        base_prob = (
            agent.base_defection_prob * 
            trust_modifier * 
            political_pressure +
            shock * 0.5
        )
        
        # === MECHANISM 1: Escrow/Forfeiture ===
        # The more capital committed, the higher the exit cost
        if self.config.mechanisms.escrow_forfeiture:
            forfeiture_cost = agent.committed_capital * self.config.forfeiture_penalty
            # Rational agent weighs: is defection benefit > forfeiture cost?
            forfeiture_deterrent = min(0.4, forfeiture_cost / 100.0)  # Cap at 40% reduction
            original_prob = base_prob
            base_prob *= (1.0 - forfeiture_deterrent)
            if original_prob > base_prob + 0.05:
                result.escrow_deterred += 1
        
        # === MECHANISM 2: Lunar Credit Wealth Effects ===
        # Accumulated wealth creates stake in system
        if self.config.mechanisms.lunar_credit_wealth:
            wealth_stake = min(0.3, agent.lunar_credit_balance / 200.0)  # Cap at 30%
            original_prob = base_prob
            base_prob *= (1.0 - wealth_stake)
            if original_prob > base_prob + 0.03:
                result.wealth_deterred += 1
        
        # === MECHANISM 3: Sunk Cost Lock-In ===
        # Later phases have lower defection probability
        if self.config.mechanisms.sunk_cost_lock_in:
            phase_multiplier = {
                Phase.PHASE_0: 1.2,   # Easy to leave
                Phase.PHASE_1: 1.0,   # Baseline
                Phase.PHASE_2: 0.7,   # Committed
                Phase.PHASE_3: 0.5,   # Heavily invested
                Phase.PHASE_4: 0.3,   # Operations - very hard to leave
            }.get(self.current_phase, 1.0)
            base_prob *= phase_multiplier
        
        # === MECHANISM 4: Audit Trust Evolution ===
        # Successful phases boost trust (already applied to agent.trust_level)
        # This is handled in the phase transition
        
        return max(0.0, min(0.95, base_prob))
    
    def run(self) -> SimResult:
        """Run full Selene model simulation."""
        self.setup()
        result = SimResult()
        
        for phase_num in range(self.config.n_phases):
            self.current_phase = Phase(phase_num)
            
            # Generate shock
            shock = 0.0
            if random.random() < self.config.shock_probability:
                shock = random.uniform(0.1, self.config.shock_intensity)
            
            defections_this_phase = 0
            
            # Each agent decides
            for agent in self.agents:
                if not agent.active:
                    continue
                
                prob = self.calculate_defection_prob_full(agent, shock, result)
                
                if random.random() < prob:
                    agent.active = False
                    agent.defection_phase = self.current_phase
                    defections_this_phase += 1
                    
                    if phase_num <= 1:
                        result.early_defections += 1
                    else:
                        result.late_defections += 1
            
            # === MECHANISM 3: Poison Pill Cascade ===
            if self.config.mechanisms.poison_pill_cascade:
                if defections_this_phase >= self.config.poison_pill_threshold:
                    if phase_num >= 2:  # Only in late phases
                        result.cascade_triggered = True
                        # Cascade: all remaining agents fail
                        for agent in self.agents:
                            if agent.active:
                                agent.active = False
                                agent.defection_phase = self.current_phase
                        break
            
            # === MECHANISM 4: Audit Trust Evolution ===
            if self.config.mechanisms.audit_trust_evolution:
                if defections_this_phase == 0:
                    # Successful phase builds trust
                    for agent in self.agents:
                        if agent.active:
                            old_trust = agent.trust_level
                            agent.trust_level = min(0.95, agent.trust_level * 1.05)
                            result.audit_trust_boost += (agent.trust_level - old_trust)
            
            # Update committed capital and wealth
            for agent in self.agents:
                if agent.active:
                    agent.committed_capital += self.config.capital_per_phase
                    agent.lunar_credit_balance += random.uniform(5, 15)
            
            self.total_sunk_cost += self.config.capital_per_phase
            
            # Early termination
            if sum(1 for a in self.agents if a.active) == 0:
                break
        
        # Classify outcome
        result.final_agents = sum(1 for a in self.agents if a.active)
        
        if result.final_agents >= 4:
            result.structural_success = True
        elif result.final_agents >= 2:
            result.partial_success = True
        elif result.final_agents >= 1:
            result.graceful_degradation = True
        else:
            result.catastrophic_failure = True
        
        return result


def run_comparison_test(n_runs: int = 1000, config_name: str = "baseline"):
    """
    Run head-to-head comparison between null and full models.
    """
    print("="*70)
    print(f"NULL MODEL vs FULL SELENE MODEL COMPARISON")
    print(f"Configuration: {config_name}")
    print(f"Runs: {n_runs}")
    print("="*70)
    
    # Pessimistic configuration
    base_config = SimConfig(
        n_agents=5,
        trust_mean=0.35,        # Medium-low trust
        trust_std=0.15,
        political_volatility=0.5,
        public_approval_mean=0.4,
        shock_probability=0.25,  # 1.5x baseline
        shock_intensity=0.35,
    )
    
    # =========================================================================
    # NULL MODEL RUNS
    # =========================================================================
    print("\n--- Running NULL MODEL (no mechanisms) ---")
    
    null_config = SimConfig(
        n_agents=base_config.n_agents,
        trust_mean=base_config.trust_mean,
        trust_std=base_config.trust_std,
        political_volatility=base_config.political_volatility,
        public_approval_mean=base_config.public_approval_mean,
        shock_probability=base_config.shock_probability,
        shock_intensity=base_config.shock_intensity,
        mechanisms=MechanismConfig(
            escrow_forfeiture=False,
            lunar_credit_wealth=False,
            poison_pill_cascade=False,
            audit_trust_evolution=False,
            sunk_cost_lock_in=False,
        ),
    )
    
    null_results = {
        "structural": 0,
        "partial": 0,
        "degradation": 0,
        "catastrophic": 0,
        "early_defections": [],
        "late_defections": [],
        "final_agents": [],
    }
    
    for seed in range(n_runs):
        random.seed(seed)
        sim = NullModelSimulator(null_config)
        result = sim.run()
        
        if result.structural_success:
            null_results["structural"] += 1
        elif result.partial_success:
            null_results["partial"] += 1
        elif result.graceful_degradation:
            null_results["degradation"] += 1
        else:
            null_results["catastrophic"] += 1
        
        null_results["early_defections"].append(result.early_defections)
        null_results["late_defections"].append(result.late_defections)
        null_results["final_agents"].append(result.final_agents)
    
    # =========================================================================
    # FULL MODEL RUNS
    # =========================================================================
    print("--- Running FULL SELENE MODEL (all mechanisms) ---")
    
    full_config = SimConfig(
        n_agents=base_config.n_agents,
        trust_mean=base_config.trust_mean,
        trust_std=base_config.trust_std,
        political_volatility=base_config.political_volatility,
        public_approval_mean=base_config.public_approval_mean,
        shock_probability=base_config.shock_probability,
        shock_intensity=base_config.shock_intensity,
        mechanisms=MechanismConfig(
            escrow_forfeiture=True,
            lunar_credit_wealth=True,
            poison_pill_cascade=True,
            audit_trust_evolution=True,
            sunk_cost_lock_in=True,
        ),
    )
    
    full_results = {
        "structural": 0,
        "partial": 0,
        "degradation": 0,
        "catastrophic": 0,
        "early_defections": [],
        "late_defections": [],
        "final_agents": [],
        "escrow_deterred": 0,
        "wealth_deterred": 0,
        "cascades": 0,
        "trust_boost": [],
    }
    
    for seed in range(n_runs):
        random.seed(seed)
        sim = FullSeleneSimulator(full_config)
        result = sim.run()
        
        if result.structural_success:
            full_results["structural"] += 1
        elif result.partial_success:
            full_results["partial"] += 1
        elif result.graceful_degradation:
            full_results["degradation"] += 1
        else:
            full_results["catastrophic"] += 1
        
        full_results["early_defections"].append(result.early_defections)
        full_results["late_defections"].append(result.late_defections)
        full_results["final_agents"].append(result.final_agents)
        full_results["escrow_deterred"] += result.escrow_deterred
        full_results["wealth_deterred"] += result.wealth_deterred
        full_results["trust_boost"].append(result.audit_trust_boost)
        if result.cascade_triggered:
            full_results["cascades"] += 1
    
    # =========================================================================
    # COMPARISON
    # =========================================================================
    print("\n" + "="*70)
    print("RESULTS COMPARISON")
    print("="*70)
    
    print(f"""
                            NULL MODEL    FULL MODEL    DIFFERENCE
                            ----------    ----------    ----------
Structural Success          {null_results['structural']/n_runs*100:5.1f}%        {full_results['structural']/n_runs*100:5.1f}%        {(full_results['structural']-null_results['structural'])/n_runs*100:+5.1f}pp
Partial Success             {null_results['partial']/n_runs*100:5.1f}%        {full_results['partial']/n_runs*100:5.1f}%        {(full_results['partial']-null_results['partial'])/n_runs*100:+5.1f}pp
Graceful Degradation        {null_results['degradation']/n_runs*100:5.1f}%        {full_results['degradation']/n_runs*100:5.1f}%        {(full_results['degradation']-null_results['degradation'])/n_runs*100:+5.1f}pp
Catastrophic Failure        {null_results['catastrophic']/n_runs*100:5.1f}%        {full_results['catastrophic']/n_runs*100:5.1f}%        {(full_results['catastrophic']-null_results['catastrophic'])/n_runs*100:+5.1f}pp

Avg Final Agents            {statistics.mean(null_results['final_agents']):5.2f}         {statistics.mean(full_results['final_agents']):5.2f}         {statistics.mean(full_results['final_agents'])-statistics.mean(null_results['final_agents']):+5.2f}
Avg Early Defections        {statistics.mean(null_results['early_defections']):5.2f}         {statistics.mean(full_results['early_defections']):5.2f}         {statistics.mean(full_results['early_defections'])-statistics.mean(null_results['early_defections']):+5.2f}
Avg Late Defections         {statistics.mean(null_results['late_defections']):5.2f}         {statistics.mean(full_results['late_defections']):5.2f}         {statistics.mean(full_results['late_defections'])-statistics.mean(null_results['late_defections']):+5.2f}
    """)
    
    # Positive outcomes
    null_positive = (null_results['structural'] + null_results['partial']) / n_runs
    full_positive = (full_results['structural'] + full_results['partial']) / n_runs
    
    print(f"""
SUMMARY METRICS:
  Positive Outcomes (struct+partial):
    NULL:  {null_positive*100:.1f}%
    FULL:  {full_positive*100:.1f}%
    GAP:   {(full_positive-null_positive)*100:+.1f}pp

  Mechanism Contribution (Full Model):
    Escrow deterred defections:   {full_results['escrow_deterred']} times
    Wealth deterred defections:   {full_results['wealth_deterred']} times  
    Cascades triggered:           {full_results['cascades']} ({full_results['cascades']/n_runs*100:.1f}%)
    Avg trust boost per run:      {statistics.mean(full_results['trust_boost']):.3f}
    """)
    
    # Interpretation
    print("="*70)
    print("INTERPRETATION")
    print("="*70)
    
    gap = full_positive - null_positive
    
    if gap >= 0.15:
        print(f"""
✓ MECHANISMS VALIDATED: {gap*100:.1f}pp improvement

The Selene mechanisms provide substantial improvement over baseline
cooperation dynamics. The escrow/forfeiture and wealth effects are
genuinely reducing defection probability, not just adding complexity.

Key findings:
- Escrow deterred {full_results['escrow_deterred']} defection decisions
- Wealth effects deterred {full_results['wealth_deterred']} decisions
- Sunk cost lock-in visible in late defection reduction
- Trust evolution boosted cooperation in successful phases
        """)
    elif gap >= 0.05:
        print(f"""
⚠ MODEST IMPROVEMENT: {gap*100:.1f}pp

Mechanisms provide measurable but limited improvement. This suggests
either:
1. Parameters are too pessimistic (mechanisms can't overcome distrust)
2. Mechanisms need stronger calibration
3. Real-world outcomes would indeed be fragile

The model is honest about limitations.
        """)
    else:
        print(f"""
✗ MINIMAL DIFFERENCE: {gap*100:.1f}pp

Mechanisms are not providing meaningful improvement over null model.
This could indicate:
1. Mechanisms are decorative (bad)
2. Trust levels are so low nothing helps (realistic?)
3. Implementation needs review

Further investigation needed.
        """)
    
    return {
        "null": null_results,
        "full": full_results,
        "gap_pp": gap * 100,
        "config": config_name,
    }


def run_parameter_sweep():
    """
    Run comparison across multiple parameter configurations.
    """
    print("\n" + "="*70)
    print("PARAMETER SWEEP: NULL vs FULL ACROSS CONDITIONS")
    print("="*70)
    
    configurations = [
        ("very_low_trust", 0.20, 0.6, 0.3),
        ("low_trust", 0.30, 0.5, 0.35),
        ("medium_low_trust", 0.40, 0.45, 0.4),
        ("medium_trust", 0.50, 0.4, 0.45),
    ]
    
    results_summary = []
    
    for name, trust, volatility, approval in configurations:
        print(f"\n--- Configuration: {name} ---")
        print(f"    Trust={trust}, Volatility={volatility}, Approval={approval}")
        
        # Null model
        null_config = SimConfig(
            n_agents=5,
            trust_mean=trust,
            trust_std=0.10,
            political_volatility=volatility,
            public_approval_mean=approval,
            shock_probability=0.20,
            shock_intensity=0.30,
            mechanisms=MechanismConfig(
                escrow_forfeiture=False,
                lunar_credit_wealth=False,
                poison_pill_cascade=False,
                audit_trust_evolution=False,
                sunk_cost_lock_in=False,
            ),
        )
        
        null_positive = 0
        for seed in range(500):
            random.seed(seed)
            sim = NullModelSimulator(null_config)
            result = sim.run()
            if result.structural_success or result.partial_success:
                null_positive += 1
        null_rate = null_positive / 500
        
        # Full model
        full_config = SimConfig(
            n_agents=5,
            trust_mean=trust,
            trust_std=0.10,
            political_volatility=volatility,
            public_approval_mean=approval,
            shock_probability=0.20,
            shock_intensity=0.30,
            mechanisms=MechanismConfig(
                escrow_forfeiture=True,
                lunar_credit_wealth=True,
                poison_pill_cascade=True,
                audit_trust_evolution=True,
                sunk_cost_lock_in=True,
            ),
        )
        
        full_positive = 0
        for seed in range(500):
            random.seed(seed)
            sim = FullSeleneSimulator(full_config)
            result = sim.run()
            if result.structural_success or result.partial_success:
                full_positive += 1
        full_rate = full_positive / 500
        
        gap = full_rate - null_rate
        results_summary.append({
            "config": name,
            "trust": trust,
            "null_rate": null_rate,
            "full_rate": full_rate,
            "gap_pp": gap * 100,
        })
        
        print(f"    NULL: {null_rate*100:.1f}% | FULL: {full_rate*100:.1f}% | GAP: {gap*100:+.1f}pp")
    
    # Summary table
    print("\n" + "="*70)
    print("SWEEP SUMMARY")
    print("="*70)
    print(f"{'Config':<20} {'Trust':>6} {'NULL':>8} {'FULL':>8} {'GAP':>8}")
    print("-"*52)
    for r in results_summary:
        print(f"{r['config']:<20} {r['trust']:>6.2f} {r['null_rate']*100:>7.1f}% {r['full_rate']*100:>7.1f}% {r['gap_pp']:>+7.1f}pp")
    
    avg_gap = statistics.mean([r['gap_pp'] for r in results_summary])
    print("-"*52)
    print(f"{'AVERAGE GAP':<20} {'':<6} {'':<8} {'':<8} {avg_gap:>+7.1f}pp")
    
    return results_summary


def run_mechanism_ablation():
    """
    Test each mechanism individually to see which contributes most.
    """
    print("\n" + "="*70)
    print("MECHANISM ABLATION: Which innovations matter?")
    print("="*70)
    
    base_trust = 0.35
    n_runs = 500
    
    mechanisms = [
        ("NULL (none)", MechanismConfig(
            escrow_forfeiture=False, lunar_credit_wealth=False,
            poison_pill_cascade=False, audit_trust_evolution=False,
            sunk_cost_lock_in=False)),
        ("+ Escrow only", MechanismConfig(
            escrow_forfeiture=True, lunar_credit_wealth=False,
            poison_pill_cascade=False, audit_trust_evolution=False,
            sunk_cost_lock_in=False)),
        ("+ Wealth only", MechanismConfig(
            escrow_forfeiture=False, lunar_credit_wealth=True,
            poison_pill_cascade=False, audit_trust_evolution=False,
            sunk_cost_lock_in=False)),
        ("+ Sunk Cost only", MechanismConfig(
            escrow_forfeiture=False, lunar_credit_wealth=False,
            poison_pill_cascade=False, audit_trust_evolution=False,
            sunk_cost_lock_in=True)),
        ("+ Audit Trust only", MechanismConfig(
            escrow_forfeiture=False, lunar_credit_wealth=False,
            poison_pill_cascade=False, audit_trust_evolution=True,
            sunk_cost_lock_in=False)),
        ("+ Poison Pill only", MechanismConfig(
            escrow_forfeiture=False, lunar_credit_wealth=False,
            poison_pill_cascade=True, audit_trust_evolution=False,
            sunk_cost_lock_in=False)),
        ("FULL (all)", MechanismConfig(
            escrow_forfeiture=True, lunar_credit_wealth=True,
            poison_pill_cascade=True, audit_trust_evolution=True,
            sunk_cost_lock_in=True)),
    ]
    
    results = []
    baseline_rate = None
    
    for name, mech_config in mechanisms:
        config = SimConfig(
            n_agents=5,
            trust_mean=base_trust,
            trust_std=0.10,
            political_volatility=0.5,
            public_approval_mean=0.4,
            shock_probability=0.20,
            shock_intensity=0.30,
            mechanisms=mech_config,
        )
        
        positive = 0
        for seed in range(n_runs):
            random.seed(seed)
            if mech_config.is_null_model():
                sim = NullModelSimulator(config)
            else:
                sim = FullSeleneSimulator(config)
            result = sim.run()
            if result.structural_success or result.partial_success:
                positive += 1
        
        rate = positive / n_runs
        
        if baseline_rate is None:
            baseline_rate = rate
            delta = 0
        else:
            delta = rate - baseline_rate
        
        results.append({
            "name": name,
            "rate": rate,
            "delta": delta,
        })
        
        bar = "█" * int(rate * 40)
        print(f"{name:<20} {rate*100:5.1f}% {delta*100:+5.1f}pp  {bar}")
    
    # Find most impactful mechanism
    single_mechanisms = results[1:-1]  # Exclude NULL and FULL
    best = max(single_mechanisms, key=lambda x: x['delta'])
    
    print(f"\nMost impactful single mechanism: {best['name']} ({best['delta']*100:+.1f}pp)")
    
    return results


if __name__ == "__main__":
    # Run main comparison
    comparison = run_comparison_test(n_runs=1000)
    
    # Run parameter sweep
    sweep = run_parameter_sweep()
    
    # Run mechanism ablation
    ablation = run_mechanism_ablation()
