#!/usr/bin/env python3
"""
ECSC HISTORICAL CALIBRATION
============================
Phase 2 Pattern Calibration: Sunk Cost Lock-In

Historical Reference:
- European Coal and Steel Community (1951)
- 6 founding members: France, Germany, Italy, Belgium, Netherlands, Luxembourg
- Post-WWII hostility → medium initial trust
- Strong sunk cost effects (shared industrial infrastructure)
- Result: ~95% "lock-in" (became EU, no defections)

Purpose: Find parameters that produce ECSC-like patterns.
This is CALIBRATION (fitting parameters to a target), not VALIDATION 
(demonstrating out-of-sample predictive accuracy).

Interpretation: Successful calibration shows parameters EXIST that match
ECSC patterns. It does not prove the model is correct or predictive.

Target: Model should produce 85-95% structural success rate
to match historical pattern of durable cooperation despite
initial distrust.

Version: 2.1 (updated per review - clarified calibration vs validation)
"""

import random
import statistics
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum

# Import from verification module
from consortium_abm_verification import (
    ConsortiumAgent, AgentType, Phase, SimulationConfig, 
    SimulationResult, ConsortiumSimulator
)


@dataclass
class ECSCAgent(ConsortiumAgent):
    """
    ECSC-specific agent with historical characteristics.
    """
    country_name: str = ""
    historical_grievance: float = 0.0  # France-Germany specific
    
    def __post_init__(self):
        # Override base class to use ECSC-specific parameters
        pass


class ECSCSimulator(ConsortiumSimulator):
    """
    ECSC-specific simulator with historical calibration.
    
    Key ECSC features that reduced defection:
    1. Supranational High Authority (oath-bound, not national)
    2. Immediate economic benefits (reduced tariffs, increased trade)
    3. Post-war desperation (cooperation or ruin)
    4. US Marshall Plan support (external backing)
    """
    
    def __init__(self, config: SimulationConfig):
        super().__init__(config)
        # ECSC-specific modifiers - tuned for 85-95% success
        self.governance_lock = 0.40  # Increased: Strong supranational authority
        self.economic_benefit = 0.25  # Increased: Significant immediate gains
        self.marshall_plan_support = True  # External backing
    
    def setup(self):
        """Initialize 6 ECSC founding members with historical parameters."""
        self.agents = []
        
        # ECSC founding members with historical context
        # Key: ALL members had strong incentives due to post-war situation
        # Trust levels reflect desperate need for cooperation AND US backing
        members = [
            # (name, trust, stability, is_major_power)
            ("France", 0.60, 0.75, True),      # Major, desperate for security
            ("Germany", 0.65, 0.65, True),     # Eager to rehabilitate
            ("Italy", 0.60, 0.60, True),       # Rebuilding, needs cooperation
            ("Belgium", 0.70, 0.80, False),    # Small, very cooperative
            ("Netherlands", 0.70, 0.80, False),# Small, very cooperative
            ("Luxembourg", 0.75, 0.90, False), # Tiny, extremely cooperative
        ]
        
        for i, (name, trust, stability, is_major) in enumerate(members):
            # Add variance based on config
            if self.config.trust_variance > 0:
                trust += random.gauss(0, self.config.trust_variance)
                trust = max(0.0, min(1.0, trust))
            
            # ECSC-specific: Very low base defection due to structural factors
            # Historical reality: NO member ever left ECSC
            base_defect = 0.06 if is_major else 0.03  # Lower: reflects historical success
            
            agent = ConsortiumAgent(
                agent_id=name,
                agent_type=AgentType.TRACK_A_CORE,
                trust_level=trust,
                domestic_stability=stability,
                technical_capability=0.85,
                base_defection_prob=base_defect,
                sunk_cost_sensitivity=0.03,  # Very strong lock-in (ECSC was binding)
                shock_sensitivity=0.10,       # Very low: 1950s was stable rebuilding period
            )
            self.agents.append(agent)
        
        self.current_phase = Phase.PHASE_0
        self.total_sunk_cost = 0.0
        self.history = []
    
    def run_phase(self) -> Dict:
        """Execute phase with ECSC-specific modifiers."""
        phase_record = {
            "phase": self.current_phase.value,
            "defections": [],
            "active_before": sum(1 for a in self.agents if a.active),
            "sunk_cost": self.total_sunk_cost,
        }
        
        # ECSC: Lower shock probability due to Marshall Plan backing
        shock = 0.0
        if not self.config.disable_shocks:
            effective_shock_prob = self.config.shock_probability * 0.5  # Half as likely
            if random.random() < effective_shock_prob:
                shock = random.uniform(*self.config.shock_intensity_range) * 0.7
        
        phase_record["shock"] = shock
        
        n_active = sum(1 for a in self.agents if a.active)
        
        # Each agent decides with ECSC modifiers
        defections_this_phase = []
        for agent in self.agents:
            if agent.active:
                # Calculate base probability
                prob = agent.calculate_defection_probability(
                    self.current_phase, self.total_sunk_cost, shock, n_active
                )
                
                # Apply ECSC governance lock (supranational authority)
                prob *= (1.0 - self.governance_lock)
                
                # Apply economic benefit (immediate gains)
                if self.current_phase.value >= 1:  # Benefits kick in after Phase 0
                    prob *= (1.0 - self.economic_benefit)
                
                # Marshall Plan support reduces defection in early phases
                if self.marshall_plan_support and self.current_phase.value <= 2:
                    prob *= 0.6  # Strong US backing was critical
                
                if random.random() < prob:
                    agent.active = False
                    agent.defection_phase = self.current_phase
                    agent.defection_reason = f"prob={prob:.2f}"
                    defections_this_phase.append(agent.agent_id)
        
        phase_record["defections"] = defections_this_phase
        
        # Check poison pill cascade (ECSC had strong mutual dependencies)
        if not self.config.disable_poison_pill:
            if len(defections_this_phase) >= self.config.poison_pill_threshold:
                if self.current_phase.value >= 2:
                    phase_record["cascade"] = True
                    for agent in self.agents:
                        if agent.active:
                            agent.active = False
                            agent.defection_phase = self.current_phase
                            agent.defection_reason = "cascade"
        
        phase_record["active_after"] = sum(1 for a in self.agents if a.active)
        self.total_sunk_cost += self.config.capital_per_phase
        self.history.append(phase_record)
        
        return phase_record


def run_ecsc_calibration(n_runs: int = 1000) -> Dict:
    """
    Run ECSC calibration to target 85-95% structural success.
    """
    print("="*70)
    print("ECSC HISTORICAL CALIBRATION")
    print("="*70)
    print("""
Historical Context:
- 6 members: France, Germany, Italy, Belgium, Netherlands, Luxembourg
- Post-WWII (1950-1951): Medium trust, high motivation for peace
- Strong sunk costs: Shared coal/steel infrastructure
- Result: Complete success, became EU foundation

Target: 85-95% structural success rate
    """)
    
    results = {}
    
    # =========================================================================
    # Baseline: Use ECSC-specific parameters
    # =========================================================================
    print("\n--- Baseline ECSC Configuration ---")
    
    config = SimulationConfig(
        n_agents=6,
        initial_trust=0.55,      # Medium trust (post-WWII)
        trust_variance=0.05,     # Small variance
        disable_shocks=False,
        shock_probability=0.05,  # Low shocks (1950s stability)
        shock_intensity_range=(0.05, 0.15),  # Mild when they occur
        capital_per_phase=8.0,   # €8B equivalent per phase
        poison_pill_threshold=3, # Moderate cascade threshold
    )
    
    # Run with ECSC-specific simulator
    outcomes = {
        "structural": 0,
        "partial": 0,
        "degradation": 0,
        "catastrophic": 0,
    }
    final_agents = []
    
    for seed in range(n_runs):
        random.seed(seed)
        sim = ECSCSimulator(config)
        result = sim.run()
        
        if result.structural_success:
            outcomes["structural"] += 1
        elif result.partial_success:
            outcomes["partial"] += 1
        elif result.graceful_degradation:
            outcomes["degradation"] += 1
        else:
            outcomes["catastrophic"] += 1
        
        final_agents.append(result.final_active_agents)
    
    success_rate = outcomes["structural"] / n_runs
    positive_rate = (outcomes["structural"] + outcomes["partial"]) / n_runs
    avg_agents = statistics.mean(final_agents)
    
    results["baseline"] = {
        "structural_success": success_rate,
        "positive_outcomes": positive_rate,
        "avg_final_agents": avg_agents,
        "outcomes": outcomes,
    }
    
    print(f"Structural Success: {success_rate:.1%}")
    print(f"Positive Outcomes:  {positive_rate:.1%}")
    print(f"Avg Final Agents:   {avg_agents:.2f} / 6")
    print(f"Target: 85-95% structural success")
    
    if 0.85 <= success_rate <= 0.95:
        print("✓ CALIBRATION TARGET MET")
    elif success_rate < 0.85:
        print("✗ Below target - need to increase cooperation factors")
    else:
        print("✗ Above target - may be too optimistic")
    
    # =========================================================================
    # Sensitivity: What trust level achieves target?
    # =========================================================================
    print("\n--- Trust Sensitivity Analysis ---")
    print("Finding trust level that produces 85-95% success:\n")
    
    trust_sweep = {}
    for trust in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
        config.initial_trust = trust
        
        successes = 0
        for seed in range(500):  # Faster sweep
            random.seed(seed)
            sim = ECSCSimulator(config)
            result = sim.run()
            if result.structural_success:
                successes += 1
        
        rate = successes / 500
        trust_sweep[trust] = rate
        
        marker = "◀ TARGET" if 0.85 <= rate <= 0.95 else ""
        print(f"  Trust {trust:.2f}: {rate:.1%} structural success {marker}")
    
    results["trust_sweep"] = trust_sweep
    
    # =========================================================================
    # Comparison: ECSC vs Generic Consortium
    # =========================================================================
    print("\n--- ECSC vs Generic Consortium ---")
    print("Same trust level, different sunk cost sensitivity:\n")
    
    # Generic consortium (weaker sunk cost effect)
    config_generic = SimulationConfig(
        n_agents=6,
        initial_trust=0.55,
        trust_variance=0.05,
        disable_shocks=False,
        shock_probability=0.05,
        shock_intensity_range=(0.05, 0.15),
    )
    
    generic_successes = 0
    for seed in range(500):
        random.seed(seed)
        sim = ConsortiumSimulator(config_generic)  # Generic, not ECSC
        result = sim.run()
        if result.structural_success:
            generic_successes += 1
    
    generic_rate = generic_successes / 500
    ecsc_rate = trust_sweep.get(0.55, success_rate)
    
    print(f"  ECSC (strong sunk costs):    {ecsc_rate:.1%}")
    print(f"  Generic (normal sunk costs): {generic_rate:.1%}")
    print(f"  Difference:                  {(ecsc_rate - generic_rate)*100:+.1f} pp")
    
    results["comparison"] = {
        "ecsc": ecsc_rate,
        "generic": generic_rate,
        "sunk_cost_effect": ecsc_rate - generic_rate,
    }
    
    # =========================================================================
    # Pattern Validation: Sunk Cost Lock-In
    # =========================================================================
    print("\n--- Sunk Cost Lock-In Pattern ---")
    print("Defection probability should drop ≥50% post-Phase 1:\n")
    
    # Track defection rates by phase
    config.initial_trust = 0.55
    phase_defections = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    phase_opportunities = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    
    for seed in range(500):
        random.seed(seed)
        sim = ECSCSimulator(config)
        sim.setup()
        
        for phase_num in range(5):
            sim.current_phase = Phase(phase_num)
            active_before = sum(1 for a in sim.agents if a.active)
            phase_opportunities[phase_num] += active_before
            
            record = sim.run_phase()
            defections = len(record["defections"])
            phase_defections[phase_num] += defections
            
            if active_before == 0:
                break
    
    print("Phase | Defection Rate | Lock-In Effect")
    print("-" * 45)
    
    phase0_rate = phase_defections[0] / max(1, phase_opportunities[0])
    for phase in range(5):
        rate = phase_defections[phase] / max(1, phase_opportunities[phase])
        lock_in = (1 - rate / max(0.001, phase0_rate)) * 100 if phase > 0 else 0
        bar = "█" * int(rate * 50)
        print(f"  {phase}   | {rate:.1%}          | {lock_in:+.0f}% vs Phase 0")
    
    # Check pattern
    phase1_rate = phase_defections[1] / max(1, phase_opportunities[1])
    phase3_rate = phase_defections[3] / max(1, phase_opportunities[3])
    lock_in_achieved = (phase0_rate - phase3_rate) / max(0.001, phase0_rate) >= 0.50
    
    results["lock_in_pattern"] = {
        "phase_0_rate": phase0_rate,
        "phase_3_rate": phase3_rate,
        "reduction": (phase0_rate - phase3_rate) / max(0.001, phase0_rate),
        "pattern_validated": lock_in_achieved,
    }
    
    print(f"\nPhase 0→3 reduction: {results['lock_in_pattern']['reduction']:.1%}")
    print(f"Target: ≥50% reduction")
    print(f"Status: {'✓ PATTERN VALIDATED' if lock_in_achieved else '✗ PATTERN NOT MET'}")
    
    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "="*70)
    print("ECSC CALIBRATION SUMMARY")
    print("="*70)
    
    calibrated = 0.85 <= results["baseline"]["structural_success"] <= 0.95
    lock_in_ok = results["lock_in_pattern"]["pattern_validated"]
    sunk_cost_ok = results["comparison"]["sunk_cost_effect"] > 0.10  # >10pp difference
    
    print(f"""
Test                          | Result | Target
------------------------------|--------|--------
Structural success rate       | {results['baseline']['structural_success']:.1%}  | 85-95%
Sunk cost effect vs generic   | {results['comparison']['sunk_cost_effect']*100:+.1f}pp | >10pp
Lock-in pattern (Phase 0→3)   | {results['lock_in_pattern']['reduction']:.1%}  | ≥50%

Overall: {'✓ ECSC CALIBRATION PASSED' if (calibrated and lock_in_ok) else '⚠ NEEDS TUNING'}
    """)
    
    return results


def tune_to_target(target_low: float = 0.85, target_high: float = 0.95, n_runs: int = 500):
    """
    Automatically tune parameters to hit target success rate.
    """
    print("\n" + "="*70)
    print("AUTO-TUNING TO TARGET")
    print("="*70)
    
    best_config = None
    best_rate = 0
    best_distance = float('inf')
    
    # Grid search over key parameters
    for base_defect in [0.10, 0.12, 0.15, 0.18, 0.20]:
        for sunk_sensitivity in [0.05, 0.08, 0.10, 0.12, 0.15]:
            for trust in [0.50, 0.55, 0.60]:
                
                config = SimulationConfig(
                    n_agents=6,
                    initial_trust=trust,
                    trust_variance=0.05,
                    disable_shocks=False,
                    shock_probability=0.05,
                    shock_intensity_range=(0.05, 0.15),
                )
                
                # Create custom agents
                successes = 0
                for seed in range(n_runs):
                    random.seed(seed)
                    sim = ConsortiumSimulator(config)
                    sim.setup()
                    
                    # Override agent parameters
                    for agent in sim.agents:
                        agent.base_defection_prob = base_defect
                        agent.sunk_cost_sensitivity = sunk_sensitivity
                    
                    result = sim.run()
                    if result.structural_success:
                        successes += 1
                
                rate = successes / n_runs
                target_mid = (target_low + target_high) / 2
                distance = abs(rate - target_mid)
                
                if distance < best_distance and target_low <= rate <= target_high:
                    best_distance = distance
                    best_rate = rate
                    best_config = {
                        "base_defection": base_defect,
                        "sunk_cost_sensitivity": sunk_sensitivity,
                        "trust": trust,
                    }
    
    if best_config:
        print(f"\n✓ Found configuration hitting target:")
        print(f"  Base defection:      {best_config['base_defection']}")
        print(f"  Sunk cost sens:      {best_config['sunk_cost_sensitivity']}")
        print(f"  Trust level:         {best_config['trust']}")
        print(f"  Success rate:        {best_rate:.1%}")
    else:
        print("\n✗ Could not find configuration in target range")
        print("  Expanding search...")
    
    return best_config, best_rate


if __name__ == "__main__":
    # Run main calibration
    results = run_ecsc_calibration(n_runs=1000)
    
    # If not in target range, auto-tune
    if not (0.85 <= results["baseline"]["structural_success"] <= 0.95):
        print("\n--- Auto-tuning to reach target ---")
        best_config, best_rate = tune_to_target()
