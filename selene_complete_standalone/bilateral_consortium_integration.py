#!/usr/bin/env python3
"""
BILATERAL → CONSORTIUM INTEGRATION
==================================
Novel contribution: Link the bilateral friction model to consortium dynamics

Concept:
- Bilateral model generates friction/crisis events between specific pairs
- These become "external shocks" in the consortium model
- High bilateral friction → higher shock probability for affected agents

This creates a realistic feedback loop:
1. Japan-China friction escalates in bilateral model
2. That friction feeds into consortium as targeted shock
3. Consortium mechanisms either absorb or amplify the shock
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

# Import consortium components
from null_model_comparison import (
    FullSeleneSimulator, NullModelSimulator,
    SimConfig, MechanismConfig, Agent, AgentType, Phase
)


# =============================================================================
# BILATERAL MODEL (Simplified from selene_bilateral)
# =============================================================================

@dataclass
class BilateralState:
    """State of bilateral relationship between two agents."""
    agent_a: str
    agent_b: str
    friction: float = 0.2  # 0-1 scale
    trust: float = 0.5
    crisis_active: bool = False
    months_in_crisis: int = 0
    peak_friction: float = 0.0


class SimpleBilateralModel:
    """
    Simplified bilateral friction model.
    
    Generates friction events that can feed into consortium.
    Based on the upgraded bilateral simulator dynamics.
    """
    
    def __init__(
        self, 
        agent_a: str, 
        agent_b: str,
        baseline_friction: float = 0.2,
        escalation_prob: float = 0.15,
        deescalation_rate: float = 0.08,
    ):
        self.state = BilateralState(
            agent_a=agent_a,
            agent_b=agent_b,
            friction=baseline_friction,
        )
        self.escalation_prob = escalation_prob
        self.deescalation_rate = deescalation_rate
        self.history: List[float] = []
        
    def step(self) -> float:
        """
        Advance one time step, return current friction level.
        """
        # Random escalation events
        if random.random() < self.escalation_prob:
            escalation = random.uniform(0.1, 0.3)
            self.state.friction = min(1.0, self.state.friction + escalation)
            self.state.crisis_active = self.state.friction > 0.5
        
        # De-escalation pressure
        if not self.state.crisis_active:
            self.state.friction *= (1.0 - self.deescalation_rate)
            self.state.friction = max(0.05, self.state.friction)
        else:
            # Slower de-escalation during crisis
            self.state.friction *= (1.0 - self.deescalation_rate * 0.3)
            self.state.months_in_crisis += 1
            
            # Crisis fatigue
            if self.state.months_in_crisis > 6:
                self.state.friction *= 0.95
                
            if self.state.friction < 0.4:
                self.state.crisis_active = False
                self.state.months_in_crisis = 0
        
        # Track peak
        if self.state.friction > self.state.peak_friction:
            self.state.peak_friction = self.state.friction
        
        self.history.append(self.state.friction)
        return self.state.friction
    
    def run(self, n_steps: int = 18) -> List[float]:
        """Run for n steps, return friction history."""
        for _ in range(n_steps):
            self.step()
        return self.history


# =============================================================================
# INTEGRATED CONSORTIUM MODEL
# =============================================================================

@dataclass 
class BilateralLink:
    """Links bilateral relationship to consortium agents."""
    bilateral_model: SimpleBilateralModel
    consortium_agent_a: str  # Agent ID in consortium
    consortium_agent_b: str  # Agent ID in consortium
    shock_multiplier: float = 1.0  # How much bilateral friction affects consortium


class IntegratedConsortiumSimulator(FullSeleneSimulator):
    """
    Consortium simulator with bilateral friction integration.
    
    Bilateral friction between specific agent pairs creates
    targeted shocks in the consortium simulation.
    """
    
    def __init__(self, config: SimConfig, bilateral_links: List[BilateralLink] = None):
        super().__init__(config)
        self.bilateral_links = bilateral_links or []
        self.bilateral_shocks_delivered = 0
        
    def calculate_bilateral_shock(self, agent: Agent, step: int) -> float:
        """
        Calculate shock to specific agent from bilateral friction.
        """
        total_shock = 0.0
        
        for link in self.bilateral_links:
            # Check if this agent is involved in the bilateral relationship
            if agent.agent_id in [link.consortium_agent_a, link.consortium_agent_b]:
                # Get current friction level
                if step < len(link.bilateral_model.history):
                    friction = link.bilateral_model.history[step]
                else:
                    friction = link.bilateral_model.state.friction
                
                # Convert friction to shock
                # High friction (>0.5) creates significant shock
                if friction > 0.3:
                    shock = (friction - 0.3) * link.shock_multiplier
                    total_shock += shock
                    
                    if shock > 0.1:
                        self.bilateral_shocks_delivered += 1
        
        return min(0.5, total_shock)  # Cap shock
    
    def run_integrated(self) -> Dict:
        """
        Run with bilateral integration.
        """
        self.setup()
        
        result = {
            "structural_success": False,
            "partial_success": False,
            "catastrophic_failure": False,
            "final_agents": 0,
            "bilateral_shocks": 0,
            "cascade_triggered": False,
        }
        
        # Pre-run bilateral models
        for link in self.bilateral_links:
            link.bilateral_model.run(n_steps=self.config.n_phases * 4)  # 4 months per phase
        
        for phase_num in range(self.config.n_phases):
            self.current_phase = Phase(phase_num)
            step = phase_num * 4  # Map phase to bilateral timeline
            
            # Global shock (same as before)
            global_shock = 0.0
            if random.random() < self.config.shock_probability:
                global_shock = random.uniform(0.1, self.config.shock_intensity)
            
            defections_this_phase = 0
            
            for agent in self.agents:
                if not agent.active:
                    continue
                
                # Calculate bilateral-specific shock
                bilateral_shock = self.calculate_bilateral_shock(agent, step)
                
                # Combined shock
                total_shock = global_shock + bilateral_shock
                
                # Standard defection calculation (from parent class)
                prob = self.calculate_defection_prob_full(agent, total_shock, result)
                
                if random.random() < prob:
                    agent.active = False
                    agent.defection_phase = self.current_phase
                    defections_this_phase += 1
            
            # Cascade check
            if self.config.mechanisms.poison_pill_cascade:
                if defections_this_phase >= self.config.poison_pill_threshold:
                    if phase_num >= 2:
                        result["cascade_triggered"] = True
                        for agent in self.agents:
                            if agent.active:
                                agent.active = False
                        break
            
            # Trust evolution
            if self.config.mechanisms.audit_trust_evolution:
                if defections_this_phase == 0:
                    for agent in self.agents:
                        if agent.active:
                            agent.trust_level = min(0.95, agent.trust_level * 1.05)
            
            # Update capital
            for agent in self.agents:
                if agent.active:
                    agent.committed_capital += self.config.capital_per_phase
                    agent.lunar_credit_balance += random.uniform(5, 15)
            
            if sum(1 for a in self.agents if a.active) == 0:
                break
        
        # Classify result
        result["final_agents"] = sum(1 for a in self.agents if a.active)
        result["bilateral_shocks"] = self.bilateral_shocks_delivered
        
        if result["final_agents"] >= 4:
            result["structural_success"] = True
        elif result["final_agents"] >= 2:
            result["partial_success"] = True
        else:
            result["catastrophic_failure"] = True
        
        return result
    
    def calculate_defection_prob_full(self, agent: Agent, shock: float, result: Dict) -> float:
        """Reuse parent calculation."""
        # Simplified version
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
        
        # Escrow effect
        if self.config.mechanisms.escrow_forfeiture:
            forfeiture_deterrent = min(0.4, agent.committed_capital / 100.0)
            base_prob *= (1.0 - forfeiture_deterrent)
        
        # Wealth effect
        if self.config.mechanisms.lunar_credit_wealth:
            wealth_stake = min(0.3, agent.lunar_credit_balance / 200.0)
            base_prob *= (1.0 - wealth_stake)
        
        # Sunk cost effect
        if self.config.mechanisms.sunk_cost_lock_in:
            phase_mult = {
                Phase.PHASE_0: 1.2,
                Phase.PHASE_1: 1.0,
                Phase.PHASE_2: 0.7,
                Phase.PHASE_3: 0.5,
                Phase.PHASE_4: 0.3,
            }.get(self.current_phase, 1.0)
            base_prob *= phase_mult
        
        return max(0.0, min(0.95, base_prob))


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def run_integration_comparison(n_runs: int = 1000):
    """
    Compare consortium outcomes with and without bilateral integration.
    """
    print("="*70)
    print("BILATERAL → CONSORTIUM INTEGRATION TEST")
    print("="*70)
    print("""
Scenario: Japan-China bilateral friction feeds into consortium dynamics.

Test cases:
1. Baseline: No bilateral friction (global shocks only)
2. Low bilateral: Mild Japan-China tension
3. High bilateral: Serious Japan-China crisis

We expect: Higher bilateral friction → more targeted defection pressure
on Japan/China agents, potentially triggering cascades.
    """)
    
    # Agent mapping
    # Agent_0 = EU (Track A)
    # Agent_1 = Russia (Track B)
    # Agent_2 = China (Track B)  <- Bilateral link
    # Agent_3 = Japan (Associate) <- Bilateral link
    # Agent_4 = India (Associate)
    
    base_config = SimConfig(
        n_agents=5,
        trust_mean=0.40,
        trust_std=0.10,
        political_volatility=0.4,
        public_approval_mean=0.45,
        shock_probability=0.15,
        shock_intensity=0.25,
        mechanisms=MechanismConfig(
            escrow_forfeiture=True,
            lunar_credit_wealth=True,
            poison_pill_cascade=True,
            audit_trust_evolution=True,
            sunk_cost_lock_in=True,
        ),
    )
    
    scenarios = [
        ("No bilateral", 0.1, 0.05),      # Low escalation, fast de-escalation
        ("Low bilateral", 0.15, 0.08),    # Moderate
        ("High bilateral", 0.25, 0.04),   # High escalation, slow de-escalation
        ("Crisis bilateral", 0.35, 0.02), # Frequent crises
    ]
    
    results = []
    
    for name, esc_prob, deesc_rate in scenarios:
        print(f"\n--- Scenario: {name} ---")
        print(f"    Escalation prob: {esc_prob}, De-escalation rate: {deesc_rate}")
        
        positive = 0
        cascades = 0
        total_bilateral_shocks = 0
        china_defections = 0
        japan_defections = 0
        
        for seed in range(n_runs):
            random.seed(seed)
            
            # Create bilateral model for Japan-China
            bilateral = SimpleBilateralModel(
                agent_a="China",
                agent_b="Japan",
                baseline_friction=0.25,
                escalation_prob=esc_prob,
                deescalation_rate=deesc_rate,
            )
            
            link = BilateralLink(
                bilateral_model=bilateral,
                consortium_agent_a="Agent_2",  # China
                consortium_agent_b="Agent_3",  # Japan (mapped to Associate)
                shock_multiplier=1.5,
            )
            
            sim = IntegratedConsortiumSimulator(base_config, bilateral_links=[link])
            result = sim.run_integrated()
            
            if result["structural_success"] or result["partial_success"]:
                positive += 1
            if result["cascade_triggered"]:
                cascades += 1
            total_bilateral_shocks += result["bilateral_shocks"]
            
            # Track specific agent defections
            for agent in sim.agents:
                if agent.defection_phase is not None:
                    if agent.agent_id == "Agent_2":
                        china_defections += 1
                    elif agent.agent_id == "Agent_3":
                        japan_defections += 1
        
        pos_rate = positive / n_runs
        cascade_rate = cascades / n_runs
        avg_shocks = total_bilateral_shocks / n_runs
        
        results.append({
            "scenario": name,
            "positive_rate": pos_rate,
            "cascade_rate": cascade_rate,
            "avg_bilateral_shocks": avg_shocks,
            "china_defections": china_defections / n_runs,
            "japan_defections": japan_defections / n_runs,
        })
        
        print(f"    Positive outcomes: {pos_rate*100:.1f}%")
        print(f"    Cascades: {cascade_rate*100:.1f}%")
        print(f"    Avg bilateral shocks: {avg_shocks:.1f}")
        print(f"    China defection rate: {china_defections/n_runs*100:.1f}%")
        print(f"    Japan defection rate: {japan_defections/n_runs*100:.1f}%")
    
    # Summary
    print("\n" + "="*70)
    print("INTEGRATION RESULTS SUMMARY")
    print("="*70)
    
    print(f"\n{'Scenario':<20} {'Positive':>10} {'Cascades':>10} {'Bi-Shocks':>10} {'CN Defect':>10} {'JP Defect':>10}")
    print("-" * 70)
    for r in results:
        print(f"{r['scenario']:<20} {r['positive_rate']*100:>9.1f}% {r['cascade_rate']*100:>9.1f}% {r['avg_bilateral_shocks']:>10.1f} {r['china_defections']*100:>9.1f}% {r['japan_defections']*100:>9.1f}%")
    
    # Calculate degradation from bilateral friction
    baseline = results[0]["positive_rate"]
    crisis = results[-1]["positive_rate"]
    degradation = baseline - crisis
    
    print(f"\n--- Analysis ---")
    print(f"Baseline (no bilateral): {baseline*100:.1f}% positive")
    print(f"Crisis bilateral:        {crisis*100:.1f}% positive")
    print(f"Degradation:             {degradation*100:+.1f}pp")
    
    if degradation > 0.10:
        print(f"\n✓ INTEGRATION VALIDATED: Bilateral friction meaningfully impacts consortium")
        print(f"  High bilateral tension reduces positive outcomes by {degradation*100:.1f}pp")
    else:
        print(f"\n⚠ LIMITED INTEGRATION EFFECT: {degradation*100:.1f}pp change")
    
    return results


def run_bilateral_cascade_analysis(n_runs: int = 500):
    """
    Analyze how bilateral crises can trigger consortium cascades.
    """
    print("\n" + "="*70)
    print("BILATERAL CRISIS → CASCADE ANALYSIS")
    print("="*70)
    print("""
Question: Can a bilateral crisis between two agents trigger a
consortium-wide cascade through the poison pill mechanism?
    """)
    
    # High crisis scenario
    config = SimConfig(
        n_agents=5,
        trust_mean=0.35,  # Lower trust makes cascade more likely
        trust_std=0.10,
        political_volatility=0.45,
        public_approval_mean=0.40,
        shock_probability=0.10,  # Lower global shocks
        shock_intensity=0.20,
        mechanisms=MechanismConfig(
            escrow_forfeiture=True,
            lunar_credit_wealth=True,
            poison_pill_cascade=True,
            audit_trust_evolution=True,
            sunk_cost_lock_in=True,
        ),
        poison_pill_threshold=2,  # Strong pill
    )
    
    # Track cascade triggers
    cascade_from_bilateral = 0
    cascade_from_global = 0
    no_cascade = 0
    
    bilateral_crisis_runs = 0
    
    for seed in range(n_runs):
        random.seed(seed)
        
        # Create high-tension bilateral
        bilateral = SimpleBilateralModel(
            agent_a="China",
            agent_b="Japan",
            baseline_friction=0.4,  # Start elevated
            escalation_prob=0.30,   # Frequent escalation
            deescalation_rate=0.03, # Very slow de-escalation
        )
        
        link = BilateralLink(
            bilateral_model=bilateral,
            consortium_agent_a="Agent_2",
            consortium_agent_b="Agent_3",
            shock_multiplier=2.0,  # Strong coupling
        )
        
        sim = IntegratedConsortiumSimulator(config, bilateral_links=[link])
        result = sim.run_integrated()
        
        # Check if bilateral reached crisis
        if bilateral.state.peak_friction > 0.6:
            bilateral_crisis_runs += 1
        
        if result["cascade_triggered"]:
            # Try to attribute cascade
            if result["bilateral_shocks"] > 3:
                cascade_from_bilateral += 1
            else:
                cascade_from_global += 1
        else:
            no_cascade += 1
    
    print(f"""
Results from {n_runs} runs:
  Bilateral crises occurred: {bilateral_crisis_runs} ({bilateral_crisis_runs/n_runs*100:.1f}%)
  
  Cascade attribution:
    From bilateral friction: {cascade_from_bilateral} ({cascade_from_bilateral/n_runs*100:.1f}%)
    From global shocks:      {cascade_from_global} ({cascade_from_global/n_runs*100:.1f}%)
    No cascade:              {no_cascade} ({no_cascade/n_runs*100:.1f}%)
    """)
    
    if cascade_from_bilateral > 0:
        print(f"✓ BILATERAL-TRIGGERED CASCADES CONFIRMED")
        print(f"  {cascade_from_bilateral/n_runs*100:.1f}% of runs had cascades attributable to bilateral friction")
    
    return {
        "bilateral_crises": bilateral_crisis_runs,
        "cascade_bilateral": cascade_from_bilateral,
        "cascade_global": cascade_from_global,
        "no_cascade": no_cascade,
    }


def run_full_integration_demo():
    """
    Full demonstration of bilateral→consortium pipeline.
    """
    print("\n" + "="*70)
    print("FULL INTEGRATION DEMONSTRATION")
    print("="*70)
    print("""
Simulating a realistic scenario:
- 5-nation consortium (EU, Russia, China, Japan, India)
- Japan-China bilateral friction model running in parallel
- Friction feeds into consortium as targeted shocks
- Tracking how bilateral dynamics affect consortium survival
    """)
    
    # Run single detailed simulation
    random.seed(42)
    
    # Create bilateral model
    bilateral = SimpleBilateralModel(
        agent_a="China",
        agent_b="Japan",
        baseline_friction=0.3,
        escalation_prob=0.20,
        deescalation_rate=0.06,
    )
    
    # Run bilateral for 20 months
    friction_history = bilateral.run(n_steps=20)
    
    print("\n--- Japan-China Bilateral Friction Timeline ---")
    for i, f in enumerate(friction_history):
        bar = "█" * int(f * 40)
        crisis = " *** CRISIS ***" if f > 0.5 else ""
        print(f"Month {i+1:2d}: {f:.2f} {bar}{crisis}")
    
    print(f"\nPeak friction: {bilateral.state.peak_friction:.2f}")
    print(f"Crisis occurred: {bilateral.state.peak_friction > 0.5}")
    
    # Now run integrated consortium
    print("\n--- Consortium Simulation with Bilateral Integration ---")
    
    random.seed(42)  # Reset for consortium
    
    config = SimConfig(
        n_agents=5,
        trust_mean=0.40,
        trust_std=0.10,
        political_volatility=0.4,
        public_approval_mean=0.45,
        shock_probability=0.12,
        shock_intensity=0.20,
        mechanisms=MechanismConfig(
            escrow_forfeiture=True,
            lunar_credit_wealth=True,
            poison_pill_cascade=True,
            audit_trust_evolution=True,
            sunk_cost_lock_in=True,
        ),
    )
    
    # Re-create bilateral for consortium run
    bilateral2 = SimpleBilateralModel(
        agent_a="China",
        agent_b="Japan",
        baseline_friction=0.3,
        escalation_prob=0.20,
        deescalation_rate=0.06,
    )
    
    link = BilateralLink(
        bilateral_model=bilateral2,
        consortium_agent_a="Agent_2",  # China
        consortium_agent_b="Agent_3",  # Japan
        shock_multiplier=1.5,
    )
    
    sim = IntegratedConsortiumSimulator(config, bilateral_links=[link])
    result = sim.run_integrated()
    
    print(f"\nConsortium Outcome:")
    print(f"  Final agents: {result['final_agents']} / 5")
    print(f"  Bilateral shocks delivered: {result['bilateral_shocks']}")
    print(f"  Cascade triggered: {result['cascade_triggered']}")
    print(f"  Structural success: {result['structural_success']}")
    print(f"  Partial success: {result['partial_success']}")
    
    # Show agent status
    print("\n  Agent Status:")
    for agent in sim.agents:
        status = "ACTIVE" if agent.active else f"DEFECTED (Phase {agent.defection_phase.value if agent.defection_phase else '?'})"
        print(f"    {agent.agent_id}: {status}")
    
    return result


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Full demo first
    demo_result = run_full_integration_demo()
    
    # Statistical comparison
    comparison_results = run_integration_comparison(n_runs=1000)
    
    # Cascade analysis
    cascade_results = run_bilateral_cascade_analysis(n_runs=500)
