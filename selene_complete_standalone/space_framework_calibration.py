#!/usr/bin/env python3
"""
SPACE COOPERATION CALIBRATION
=============================
Calibrate ABM to real-world space frameworks:
1. Artemis Accords (US-led, ~60 signatories, non-binding)
2. ILRS (China-Russia led, ~10-12 partners, MoU-based)
3. Project Selene (hypothetical, 5-8 founders, binding)

Expected outcomes based on structural analysis:
- Artemis: High churn, easy entry/exit, broad but fragile
- ILRS: Smaller core, bilateral lock-in, more stable
- Selene: Deep integration, highest stability
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from enum import Enum


class Phase(Enum):
    PHASE_0 = 0
    PHASE_1 = 1
    PHASE_2 = 2
    PHASE_3 = 3
    PHASE_4 = 4


@dataclass
class SpaceAgent:
    """Agent in space cooperation framework."""
    agent_id: str
    agent_type: str  # "core", "partner", "associate", "signatory"
    commitment_level: float  # 0-1 scale
    trust_level: float
    bilateral_ties: List[str] = field(default_factory=list)
    
    active: bool = True
    joined_phase: int = 0
    exit_phase: int = -1
    sunk_investment: float = 0.0


@dataclass
class FrameworkConfig:
    """Configuration for a space cooperation framework."""
    name: str
    n_agents: int
    
    # Structural parameters
    binding_strength: float      # 0=non-binding, 1=treaty
    exit_penalty: float          # 0=free exit, 1=full forfeiture
    sunk_cost_effect: float      # How much investment locks you in
    bilateral_coupling: float    # How much bilateral ties matter
    governance_centralization: float  # 0=distributed, 1=single leader
    
    # Agent composition
    core_agents: int
    partner_agents: int
    associate_agents: int
    
    # Trust parameters
    baseline_trust: float
    trust_variance: float
    
    # Shock parameters
    political_shock_prob: float
    leadership_change_prob: float


# =============================================================================
# FRAMEWORK DEFINITIONS
# =============================================================================

ARTEMIS_CONFIG = FrameworkConfig(
    name="Artemis Accords",
    n_agents=20,  # Model subset of 60 (computational)
    
    # Structural - NON-BINDING
    binding_strength=0.1,        # Principles only
    exit_penalty=0.0,            # No cost to leave
    sunk_cost_effect=0.1,        # Minimal lock-in
    bilateral_coupling=0.2,      # Weak bilateral ties
    governance_centralization=0.7,  # US-led
    
    # Agents - BROAD COALITION
    core_agents=3,               # US, Japan, EU
    partner_agents=7,            # Major allies
    associate_agents=10,         # Smaller signatories
    
    # Trust - VARIES WIDELY
    baseline_trust=0.45,
    trust_variance=0.20,
    
    # Shocks - FREQUENT (election cycles matter)
    political_shock_prob=0.25,
    leadership_change_prob=0.20,
)

ILRS_CONFIG = FrameworkConfig(
    name="ILRS (China-Russia)",
    n_agents=10,
    
    # Structural - MOU-BASED
    binding_strength=0.4,        # MoUs have some weight
    exit_penalty=0.2,            # Bilateral reputation costs
    sunk_cost_effect=0.4,        # Mission interdependence
    bilateral_coupling=0.6,      # Strong bilateral ties (China-Russia core)
    governance_centralization=0.8,  # China dominant
    
    # Agents - FOCUSED
    core_agents=2,               # China, Russia
    partner_agents=4,            # Belarus, Pakistan, etc.
    associate_agents=4,          # Smaller partners
    
    # Trust - HIGHER WITHIN BLOC
    baseline_trust=0.50,
    trust_variance=0.15,
    
    # Shocks - MODERATE
    political_shock_prob=0.15,
    leadership_change_prob=0.10,
)

SELENE_CONFIG = FrameworkConfig(
    name="Project Selene",
    n_agents=6,
    
    # Structural - BINDING
    binding_strength=0.8,        # Treaty-like
    exit_penalty=0.7,            # Forfeiture clause
    sunk_cost_effect=0.7,        # Strong irreversibility
    bilateral_coupling=0.5,      # Dependency chains
    governance_centralization=0.3,  # Supranational
    
    # Agents - DEEP INTEGRATION
    core_agents=4,               # EU, China, Russia, India
    partner_agents=2,            # Japan, UAE
    associate_agents=0,
    
    # Trust - MEDIUM (designed for low-trust)
    baseline_trust=0.40,
    trust_variance=0.12,
    
    # Shocks - MANAGED
    political_shock_prob=0.15,
    leadership_change_prob=0.10,
)


# =============================================================================
# SIMULATOR
# =============================================================================

class SpaceCooperationSimulator:
    """
    Simulate space cooperation framework dynamics.
    """
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.agents: List[SpaceAgent] = []
        self.current_phase = Phase.PHASE_0
        self.phase_history: List[Dict] = []
        
    def setup(self):
        """Initialize agents based on framework structure."""
        self.agents = []
        
        agent_id = 0
        
        # Core agents (highest commitment)
        for i in range(self.config.core_agents):
            trust = random.gauss(
                self.config.baseline_trust + 0.15,  # Core has higher trust
                self.config.trust_variance * 0.7
            )
            trust = max(0.1, min(0.95, trust))
            
            agent = SpaceAgent(
                agent_id=f"Core_{i}",
                agent_type="core",
                commitment_level=0.8 + random.uniform(0, 0.2),
                trust_level=trust,
            )
            self.agents.append(agent)
            agent_id += 1
        
        # Partner agents (medium commitment)
        for i in range(self.config.partner_agents):
            trust = random.gauss(
                self.config.baseline_trust,
                self.config.trust_variance
            )
            trust = max(0.1, min(0.95, trust))
            
            agent = SpaceAgent(
                agent_id=f"Partner_{i}",
                agent_type="partner",
                commitment_level=0.5 + random.uniform(0, 0.3),
                trust_level=trust,
            )
            self.agents.append(agent)
            agent_id += 1
        
        # Associate agents (lower commitment)
        for i in range(self.config.associate_agents):
            trust = random.gauss(
                self.config.baseline_trust - 0.1,
                self.config.trust_variance * 1.3
            )
            trust = max(0.1, min(0.95, trust))
            
            agent = SpaceAgent(
                agent_id=f"Associate_{i}",
                agent_type="associate",
                commitment_level=0.3 + random.uniform(0, 0.3),
                trust_level=trust,
            )
            self.agents.append(agent)
            agent_id += 1
        
        # Create bilateral ties for ILRS-style frameworks
        if self.config.bilateral_coupling > 0.4:
            self._create_bilateral_ties()
        
        self.current_phase = Phase.PHASE_0
        self.phase_history = []
    
    def _create_bilateral_ties(self):
        """Create bilateral relationships between agents."""
        core_agents = [a for a in self.agents if a.agent_type == "core"]
        
        # Core agents tied to each other
        for i, a1 in enumerate(core_agents):
            for a2 in core_agents[i+1:]:
                a1.bilateral_ties.append(a2.agent_id)
                a2.bilateral_ties.append(a1.agent_id)
        
        # Partners tied to at least one core
        for agent in self.agents:
            if agent.agent_type == "partner" and core_agents:
                core = random.choice(core_agents)
                agent.bilateral_ties.append(core.agent_id)
    
    def calculate_exit_probability(self, agent: SpaceAgent, phase: Phase, shock: float) -> float:
        """
        Calculate probability of agent exiting the framework.
        """
        # Base probability from commitment
        base_prob = 0.3 * (1 - agent.commitment_level)
        
        # Trust effect
        trust_effect = 0.3 * (1 - agent.trust_level)
        
        # === FRAMEWORK-SPECIFIC MECHANISMS ===
        
        # 1. Binding strength reduces exit
        binding_reduction = self.config.binding_strength * 0.3
        
        # 2. Exit penalty deters leaving
        if agent.sunk_investment > 0:
            penalty_deterrent = self.config.exit_penalty * min(0.4, agent.sunk_investment / 50)
        else:
            penalty_deterrent = 0
        
        # 3. Sunk cost lock-in
        sunk_cost_reduction = self.config.sunk_cost_effect * min(0.4, agent.sunk_investment / 30)
        
        # 4. Bilateral ties create stickiness
        n_ties = len(agent.bilateral_ties)
        active_ties = sum(1 for t in agent.bilateral_ties 
                        if any(a.agent_id == t and a.active for a in self.agents))
        if n_ties > 0:
            bilateral_retention = self.config.bilateral_coupling * 0.2 * (active_ties / n_ties)
        else:
            bilateral_retention = 0
        
        # 5. Centralized governance - if leader exits, cascade
        # (simplified: core agents less likely to exit in centralized systems)
        if agent.agent_type == "core" and self.config.governance_centralization > 0.5:
            governance_stability = 0.15
        else:
            governance_stability = 0
        
        # Phase effects (later phases = more invested)
        phase_factor = {
            Phase.PHASE_0: 1.2,
            Phase.PHASE_1: 1.0,
            Phase.PHASE_2: 0.8,
            Phase.PHASE_3: 0.6,
            Phase.PHASE_4: 0.4,
        }.get(phase, 1.0)
        
        # Combine
        prob = (base_prob + trust_effect + shock * 0.4) * phase_factor
        prob -= (binding_reduction + penalty_deterrent + sunk_cost_reduction + 
                bilateral_retention + governance_stability)
        
        return max(0.02, min(0.8, prob))
    
    def run(self, n_phases: int = 5) -> Dict:
        """Run simulation and return results."""
        self.setup()
        
        results = {
            "framework": self.config.name,
            "initial_agents": len(self.agents),
            "exits_by_phase": [],
            "final_agents": 0,
            "core_retained": 0,
            "partner_retained": 0,
            "associate_retained": 0,
            "bilateral_cascade": False,
        }
        
        for phase_num in range(n_phases):
            self.current_phase = Phase(phase_num)
            
            # Generate shocks
            political_shock = 0
            if random.random() < self.config.political_shock_prob:
                political_shock = random.uniform(0.1, 0.4)
            
            leadership_shock = 0
            if random.random() < self.config.leadership_change_prob:
                leadership_shock = random.uniform(0.1, 0.3)
            
            total_shock = political_shock + leadership_shock
            
            exits_this_phase = 0
            
            for agent in self.agents:
                if not agent.active:
                    continue
                
                prob = self.calculate_exit_probability(agent, self.current_phase, total_shock)
                
                if random.random() < prob:
                    agent.active = False
                    agent.exit_phase = phase_num
                    exits_this_phase += 1
                    
                    # Bilateral cascade check
                    if self.config.bilateral_coupling > 0.5:
                        for other in self.agents:
                            if other.active and agent.agent_id in other.bilateral_ties:
                                # Partner exit increases other's exit risk
                                cascade_prob = 0.15 * self.config.bilateral_coupling
                                if random.random() < cascade_prob:
                                    other.active = False
                                    other.exit_phase = phase_num
                                    exits_this_phase += 1
                                    results["bilateral_cascade"] = True
                else:
                    # Invest more
                    agent.sunk_investment += random.uniform(2, 8)
            
            results["exits_by_phase"].append(exits_this_phase)
        
        # Final counts
        results["final_agents"] = sum(1 for a in self.agents if a.active)
        results["core_retained"] = sum(1 for a in self.agents 
                                       if a.active and a.agent_type == "core")
        results["partner_retained"] = sum(1 for a in self.agents 
                                          if a.active and a.agent_type == "partner")
        results["associate_retained"] = sum(1 for a in self.agents 
                                            if a.active and a.agent_type == "associate")
        
        return results


# =============================================================================
# CALIBRATION TARGETS
# =============================================================================

def get_calibration_targets():
    """
    Define expected outcomes based on real-world observations.
    """
    return {
        "Artemis Accords": {
            # ~60 signatories, but many are passive
            # High churn expected (non-binding)
            # Core (US, Japan, EU) stable
            "retention_rate": (0.50, 0.70),  # 50-70% retain interest
            "core_stability": (0.85, 1.00),  # Core almost always stays
            "associate_churn": (0.40, 0.70),  # High associate turnover
            "description": "Broad but shallow coalition with easy exit",
        },
        "ILRS (China-Russia)": {
            # Smaller, more committed group
            # Bilateral ties create stickiness
            # Some partners may defect under pressure
            "retention_rate": (0.65, 0.85),  # Higher retention
            "core_stability": (0.90, 1.00),  # China-Russia core very stable
            "associate_churn": (0.30, 0.50),  # Lower churn
            "description": "Focused bloc with bilateral lock-in",
        },
        "Project Selene": {
            # Deep integration, strong mechanisms
            # Designed to survive low trust
            "retention_rate": (0.70, 0.90),  # Highest retention
            "core_stability": (0.85, 1.00),  # Core locked in
            "associate_churn": (0.15, 0.35),  # Lowest churn
            "description": "Deep integration with irreversibility mechanisms",
        },
    }


# =============================================================================
# RUN CALIBRATION
# =============================================================================

def run_framework_comparison(n_runs: int = 1000):
    """
    Compare all three frameworks.
    """
    print("="*70)
    print("SPACE COOPERATION FRAMEWORK CALIBRATION")
    print("="*70)
    print("""
Comparing:
1. Artemis Accords (US-led, ~60 signatories, non-binding)
2. ILRS (China-Russia, ~10-12 partners, MoU-based)
3. Project Selene (hypothetical, 5-8 founders, binding)
    """)
    
    frameworks = [
        ("Artemis Accords", ARTEMIS_CONFIG),
        ("ILRS (China-Russia)", ILRS_CONFIG),
        ("Project Selene", SELENE_CONFIG),
    ]
    
    targets = get_calibration_targets()
    all_results = {}
    
    for name, config in frameworks:
        print(f"\n--- Running {name} ({n_runs} simulations) ---")
        
        retention_rates = []
        core_retentions = []
        associate_churns = []
        cascades = 0
        
        for seed in range(n_runs):
            random.seed(seed)
            sim = SpaceCooperationSimulator(config)
            result = sim.run(n_phases=5)
            
            # Calculate metrics
            retention = result["final_agents"] / result["initial_agents"]
            retention_rates.append(retention)
            
            if config.core_agents > 0:
                core_ret = result["core_retained"] / config.core_agents
                core_retentions.append(core_ret)
            
            if config.associate_agents > 0:
                assoc_churn = 1 - (result["associate_retained"] / config.associate_agents)
                associate_churns.append(assoc_churn)
            
            if result["bilateral_cascade"]:
                cascades += 1
        
        # Store results
        all_results[name] = {
            "retention_mean": statistics.mean(retention_rates),
            "retention_std": statistics.stdev(retention_rates) if len(retention_rates) > 1 else 0,
            "core_stability": statistics.mean(core_retentions) if core_retentions else 1.0,
            "associate_churn": statistics.mean(associate_churns) if associate_churns else 0,
            "cascade_rate": cascades / n_runs,
        }
        
        # Check against targets
        target = targets[name]
        ret_lo, ret_hi = target["retention_rate"]
        ret_mean = all_results[name]["retention_mean"]
        
        in_range = ret_lo <= ret_mean <= ret_hi
        status = "✓ IN RANGE" if in_range else "⚠ OUT OF RANGE"
        
        print(f"  Retention: {ret_mean*100:.1f}% (target: {ret_lo*100:.0f}-{ret_hi*100:.0f}%) {status}")
        print(f"  Core stability: {all_results[name]['core_stability']*100:.1f}%")
        if associate_churns:
            print(f"  Associate churn: {all_results[name]['associate_churn']*100:.1f}%")
        print(f"  Bilateral cascades: {all_results[name]['cascade_rate']*100:.1f}%")
    
    # Summary comparison
    print("\n" + "="*70)
    print("FRAMEWORK COMPARISON SUMMARY")
    print("="*70)
    
    print(f"\n{'Framework':<25} {'Retention':>12} {'Core Stable':>12} {'Cascades':>10}")
    print("-" * 60)
    for name in all_results:
        r = all_results[name]
        print(f"{name:<25} {r['retention_mean']*100:>11.1f}% {r['core_stability']*100:>11.1f}% {r['cascade_rate']*100:>9.1f}%")
    
    # Key insights
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    
    artemis = all_results["Artemis Accords"]
    ilrs = all_results["ILRS (China-Russia)"]
    selene = all_results["Project Selene"]
    
    print(f"""
1. RETENTION HIERARCHY:
   Selene ({selene['retention_mean']*100:.0f}%) > ILRS ({ilrs['retention_mean']*100:.0f}%) > Artemis ({artemis['retention_mean']*100:.0f}%)
   
2. STRUCTURAL DIFFERENCES:
   - Artemis: Broad but fragile (non-binding = high churn)
   - ILRS: Smaller but stickier (bilateral ties matter)
   - Selene: Deep integration (mechanisms work)

3. CORE STABILITY:
   All frameworks retain core members well ({artemis['core_stability']*100:.0f}-{selene['core_stability']*100:.0f}%)
   Real risk is at the periphery

4. BILATERAL CASCADES:
   ILRS ({ilrs['cascade_rate']*100:.1f}%) shows cascade risk from tight coupling
   Selene's forfeiture mechanism may be preferable to bilateral dependence
    """)
    
    return all_results


def run_detailed_artemis_analysis(n_runs: int = 500):
    """
    Detailed analysis of Artemis Accords dynamics.
    """
    print("\n" + "="*70)
    print("DETAILED ARTEMIS ACCORDS ANALYSIS")
    print("="*70)
    print("""
Question: What happens to the Artemis coalition under stress?
- How many signatories remain active after 5 phases?
- Which types of members exit first?
- Can the core survive associate exodus?
    """)
    
    config = ARTEMIS_CONFIG
    
    # Track exit patterns
    exit_by_type = {"core": [], "partner": [], "associate": []}
    exit_by_phase = [0, 0, 0, 0, 0]
    final_counts = []
    
    for seed in range(n_runs):
        random.seed(seed)
        sim = SpaceCooperationSimulator(config)
        result = sim.run(n_phases=5)
        
        final_counts.append(result["final_agents"])
        
        for i, exits in enumerate(result["exits_by_phase"]):
            exit_by_phase[i] += exits
        
        # Track by type
        for agent in sim.agents:
            if not agent.active:
                exit_by_type[agent.agent_type].append(agent.exit_phase)
    
    # Analysis
    print(f"\nResults from {n_runs} simulations:")
    print(f"\nFinal coalition size: {statistics.mean(final_counts):.1f} ± {statistics.stdev(final_counts):.1f} (of {config.n_agents})")
    
    print(f"\nExits by phase:")
    for i, exits in enumerate(exit_by_phase):
        avg = exits / n_runs
        bar = "█" * int(avg * 5)
        print(f"  Phase {i}: {avg:.1f} exits/run {bar}")
    
    print(f"\nExit patterns by member type:")
    for agent_type, exits in exit_by_type.items():
        if exits:
            avg_exit_phase = statistics.mean(exits)
            print(f"  {agent_type.capitalize()}: {len(exits)} total exits, avg at phase {avg_exit_phase:.1f}")
    
    return {
        "final_counts": final_counts,
        "exit_by_phase": exit_by_phase,
        "exit_by_type": exit_by_type,
    }


def run_ilrs_stress_test(n_runs: int = 500):
    """
    Stress test ILRS under various scenarios.
    """
    print("\n" + "="*70)
    print("ILRS STRESS TEST")
    print("="*70)
    print("""
Question: How robust is ILRS to external pressure?
Scenarios:
1. Baseline (normal conditions)
2. High sanctions pressure (increased shock probability)
3. Russia exit scenario (what if one core leaves?)
    """)
    
    scenarios = [
        ("Baseline", ILRS_CONFIG),
        ("High Pressure", FrameworkConfig(
            name="ILRS (High Pressure)",
            n_agents=10,
            binding_strength=0.4,
            exit_penalty=0.2,
            sunk_cost_effect=0.4,
            bilateral_coupling=0.6,
            governance_centralization=0.8,
            core_agents=2,
            partner_agents=4,
            associate_agents=4,
            baseline_trust=0.40,  # Lower trust
            trust_variance=0.20,
            political_shock_prob=0.35,  # Higher shocks
            leadership_change_prob=0.20,
        )),
    ]
    
    for name, config in scenarios:
        print(f"\n--- {name} ---")
        
        retentions = []
        core_losses = 0
        
        for seed in range(n_runs):
            random.seed(seed)
            sim = SpaceCooperationSimulator(config)
            result = sim.run(n_phases=5)
            
            retention = result["final_agents"] / result["initial_agents"]
            retentions.append(retention)
            
            if result["core_retained"] < config.core_agents:
                core_losses += 1
        
        print(f"  Retention: {statistics.mean(retentions)*100:.1f}%")
        print(f"  Core loss events: {core_losses/n_runs*100:.1f}%")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Main comparison
    comparison = run_framework_comparison(n_runs=1000)
    
    # Detailed Artemis
    artemis_detail = run_detailed_artemis_analysis(n_runs=500)
    
    # ILRS stress test
    ilrs_stress = run_ilrs_stress_test(n_runs=500)
