#!/usr/bin/env python3
"""
STATISTICAL RIGOR: Bootstrap CIs + Extreme Bounds Analysis
===========================================================
Phase 3 Analysis: Parametric uncertainty quantification

A) Bootstrap Confidence Intervals on key metrics
B) Extreme Bounds: Find trust threshold that flips outcomes

IMPORTANT INTERPRETATION NOTE (per review):
These CIs capture PARAMETRIC uncertainty - variation across Monte Carlo 
runs with fixed model structure. They do NOT capture:
- Structural uncertainty (how results change under different model specs)
- Real-world uncertainty (whether model accurately represents reality)

For novel systems, structural uncertainty likely dominates. These CIs
should not be interpreted as confidence about real-world outcomes.

Version: 2.1 (updated per review - added uncertainty interpretation)
"""

import random
import statistics
import math
from typing import List, Dict, Tuple
from null_model_comparison import (
    NullModelSimulator, FullSeleneSimulator, 
    SimConfig, MechanismConfig, SimResult
)


# =============================================================================
# A) BOOTSTRAP CONFIDENCE INTERVALS
# =============================================================================

def bootstrap_ci(data: List[float], n_bootstrap: int = 1000, ci: float = 0.95) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval.
    Returns: (mean, lower_bound, upper_bound)
    """
    n = len(data)
    means = []
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        sample = [random.choice(data) for _ in range(n)]
        means.append(statistics.mean(sample))
    
    means.sort()
    
    alpha = 1 - ci
    lower_idx = int(n_bootstrap * alpha / 2)
    upper_idx = int(n_bootstrap * (1 - alpha / 2))
    
    return (
        statistics.mean(data),
        means[lower_idx],
        means[upper_idx]
    )


def run_with_bootstrap(n_runs: int = 2000, n_bootstrap: int = 2000):
    """
    Run null vs full comparison with bootstrap CIs.
    """
    print("="*70)
    print("BOOTSTRAP CONFIDENCE INTERVALS")
    print("="*70)
    print(f"Simulation runs: {n_runs}")
    print(f"Bootstrap samples: {n_bootstrap}")
    print(f"Confidence level: 95%")
    print()
    
    # Configuration (pessimistic)
    base_config = {
        "n_agents": 5,
        "trust_mean": 0.35,
        "trust_std": 0.12,
        "political_volatility": 0.5,
        "public_approval_mean": 0.4,
        "shock_probability": 0.20,
        "shock_intensity": 0.30,
    }
    
    # Run NULL model
    print("Running NULL model...")
    null_config = SimConfig(
        **base_config,
        mechanisms=MechanismConfig(
            escrow_forfeiture=False,
            lunar_credit_wealth=False,
            poison_pill_cascade=False,
            audit_trust_evolution=False,
            sunk_cost_lock_in=False,
        ),
    )
    
    null_positive = []  # 1 if positive outcome, 0 otherwise
    null_structural = []
    null_final_agents = []
    
    for seed in range(n_runs):
        random.seed(seed)
        sim = NullModelSimulator(null_config)
        result = sim.run()
        
        null_positive.append(1 if (result.structural_success or result.partial_success) else 0)
        null_structural.append(1 if result.structural_success else 0)
        null_final_agents.append(result.final_agents)
    
    # Run FULL model
    print("Running FULL model...")
    full_config = SimConfig(
        **base_config,
        mechanisms=MechanismConfig(
            escrow_forfeiture=True,
            lunar_credit_wealth=True,
            poison_pill_cascade=True,
            audit_trust_evolution=True,
            sunk_cost_lock_in=True,
        ),
    )
    
    full_positive = []
    full_structural = []
    full_final_agents = []
    
    for seed in range(n_runs):
        random.seed(seed)
        sim = FullSeleneSimulator(full_config)
        result = sim.run()
        
        full_positive.append(1 if (result.structural_success or result.partial_success) else 0)
        full_structural.append(1 if result.structural_success else 0)
        full_final_agents.append(result.final_agents)
    
    # Compute bootstrap CIs
    print("\nComputing bootstrap CIs...")
    
    results = {}
    
    # Positive outcome rate
    null_pos_mean, null_pos_lo, null_pos_hi = bootstrap_ci(null_positive, n_bootstrap)
    full_pos_mean, full_pos_lo, full_pos_hi = bootstrap_ci(full_positive, n_bootstrap)
    
    results["positive_outcome"] = {
        "null": {"mean": null_pos_mean, "ci": (null_pos_lo, null_pos_hi)},
        "full": {"mean": full_pos_mean, "ci": (full_pos_lo, full_pos_hi)},
    }
    
    # Structural success rate
    null_str_mean, null_str_lo, null_str_hi = bootstrap_ci(null_structural, n_bootstrap)
    full_str_mean, full_str_lo, full_str_hi = bootstrap_ci(full_structural, n_bootstrap)
    
    results["structural_success"] = {
        "null": {"mean": null_str_mean, "ci": (null_str_lo, null_str_hi)},
        "full": {"mean": full_str_mean, "ci": (full_str_lo, full_str_hi)},
    }
    
    # Final agents
    null_ag_mean, null_ag_lo, null_ag_hi = bootstrap_ci(null_final_agents, n_bootstrap)
    full_ag_mean, full_ag_lo, full_ag_hi = bootstrap_ci(full_final_agents, n_bootstrap)
    
    results["final_agents"] = {
        "null": {"mean": null_ag_mean, "ci": (null_ag_lo, null_ag_hi)},
        "full": {"mean": full_ag_mean, "ci": (full_ag_lo, full_ag_hi)},
    }
    
    # Gap with CI (bootstrap the difference)
    gaps = [full_positive[i] - null_positive[i] for i in range(n_runs)]
    gap_mean, gap_lo, gap_hi = bootstrap_ci(gaps, n_bootstrap)
    
    results["gap"] = {"mean": gap_mean, "ci": (gap_lo, gap_hi)}
    
    # Print results
    print("\n" + "="*70)
    print("RESULTS WITH 95% CONFIDENCE INTERVALS")
    print("="*70)
    
    print(f"""
POSITIVE OUTCOMES (Structural + Partial):
  NULL:  {null_pos_mean*100:5.1f}%  [{null_pos_lo*100:5.1f}%, {null_pos_hi*100:5.1f}%]
  FULL:  {full_pos_mean*100:5.1f}%  [{full_pos_lo*100:5.1f}%, {full_pos_hi*100:5.1f}%]
  GAP:   {gap_mean*100:+5.1f}pp [{gap_lo*100:+5.1f}pp, {gap_hi*100:+5.1f}pp]

STRUCTURAL SUCCESS (≥4 agents):
  NULL:  {null_str_mean*100:5.1f}%  [{null_str_lo*100:5.1f}%, {null_str_hi*100:5.1f}%]
  FULL:  {full_str_mean*100:5.1f}%  [{full_str_lo*100:5.1f}%, {full_str_hi*100:5.1f}%]

AVERAGE FINAL AGENTS:
  NULL:  {null_ag_mean:5.2f}   [{null_ag_lo:5.2f}, {null_ag_hi:5.2f}]
  FULL:  {full_ag_mean:5.2f}   [{full_ag_lo:5.2f}, {full_ag_hi:5.2f}]
    """)
    
    # Statistical significance check
    print("="*70)
    print("STATISTICAL SIGNIFICANCE")
    print("="*70)
    
    # Gap CI doesn't include zero?
    if gap_lo > 0:
        print(f"""
✓ STATISTICALLY SIGNIFICANT (p < 0.05)

The 95% CI for the gap [{gap_lo*100:+.1f}pp, {gap_hi*100:+.1f}pp] does not include zero.
We can reject the null hypothesis that mechanisms have no effect.

Effect size: {gap_mean*100:.1f}pp improvement in positive outcomes
        """)
    else:
        print(f"""
✗ NOT STATISTICALLY SIGNIFICANT

The 95% CI for the gap includes zero.
Cannot reject null hypothesis.
        """)
    
    return results


# =============================================================================
# B) EXTREME BOUNDS ANALYSIS
# =============================================================================

def find_flip_threshold(target_null: float = 0.50, tolerance: float = 0.03, n_runs: int = 500):
    """
    Find the trust level where NULL model achieves ~50% positive outcomes.
    This is the "tipping point" - below this, cooperation fails; above, it might work.
    """
    print("\n" + "="*70)
    print("EXTREME BOUNDS: Finding Trust Tipping Points")
    print("="*70)
    print(f"Target: Find trust where NULL model hits {target_null*100:.0f}% positive")
    print()
    
    # Binary search for threshold
    low, high = 0.1, 0.9
    
    def eval_trust(trust_level):
        config = SimConfig(
            n_agents=5,
            trust_mean=trust_level,
            trust_std=0.08,
            political_volatility=0.45,
            public_approval_mean=0.45,
            shock_probability=0.15,
            shock_intensity=0.25,
            mechanisms=MechanismConfig(
                escrow_forfeiture=False,
                lunar_credit_wealth=False,
                poison_pill_cascade=False,
                audit_trust_evolution=False,
                sunk_cost_lock_in=False,
            ),
        )
        
        positive = 0
        for seed in range(n_runs):
            random.seed(seed)
            sim = NullModelSimulator(config)
            result = sim.run()
            if result.structural_success or result.partial_success:
                positive += 1
        
        return positive / n_runs
    
    # Binary search
    iterations = 0
    while high - low > 0.02 and iterations < 20:
        mid = (low + high) / 2
        rate = eval_trust(mid)
        print(f"  Trust {mid:.2f}: {rate*100:.1f}% positive")
        
        if rate < target_null:
            low = mid
        else:
            high = mid
        iterations += 1
    
    threshold = (low + high) / 2
    
    print(f"\n✓ NULL model 50% threshold: trust ≈ {threshold:.2f}")
    
    return threshold


def analyze_extreme_bounds(n_runs: int = 500):
    """
    Full extreme bounds analysis: sweep trust and find key thresholds.
    """
    print("\n" + "="*70)
    print("EXTREME BOUNDS: Trust Sensitivity Analysis")
    print("="*70)
    
    trust_levels = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
    
    results = []
    
    print(f"\n{'Trust':>6} | {'NULL':>8} | {'FULL':>8} | {'GAP':>8} | Visualization")
    print("-" * 60)
    
    for trust in trust_levels:
        # NULL
        null_config = SimConfig(
            n_agents=5,
            trust_mean=trust,
            trust_std=0.08,
            political_volatility=0.45,
            public_approval_mean=0.45,
            shock_probability=0.15,
            shock_intensity=0.25,
            mechanisms=MechanismConfig(
                escrow_forfeiture=False,
                lunar_credit_wealth=False,
                poison_pill_cascade=False,
                audit_trust_evolution=False,
                sunk_cost_lock_in=False,
            ),
        )
        
        null_pos = 0
        for seed in range(n_runs):
            random.seed(seed)
            sim = NullModelSimulator(null_config)
            result = sim.run()
            if result.structural_success or result.partial_success:
                null_pos += 1
        null_rate = null_pos / n_runs
        
        # FULL
        full_config = SimConfig(
            n_agents=5,
            trust_mean=trust,
            trust_std=0.08,
            political_volatility=0.45,
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
        
        full_pos = 0
        for seed in range(n_runs):
            random.seed(seed)
            sim = FullSeleneSimulator(full_config)
            result = sim.run()
            if result.structural_success or result.partial_success:
                full_pos += 1
        full_rate = full_pos / n_runs
        
        gap = full_rate - null_rate
        
        results.append({
            "trust": trust,
            "null": null_rate,
            "full": full_rate,
            "gap": gap,
        })
        
        # Visual bar
        null_bar = "░" * int(null_rate * 20)
        full_bar = "█" * int(full_rate * 20)
        
        print(f"{trust:>6.2f} | {null_rate*100:>7.1f}% | {full_rate*100:>7.1f}% | {gap*100:>+7.1f}pp | {null_bar}{full_bar}")
    
    # Find key thresholds
    print("\n" + "="*70)
    print("KEY THRESHOLDS")
    print("="*70)
    
    # Where does NULL hit 50%?
    null_50_trust = None
    for i in range(len(results) - 1):
        if results[i]["null"] < 0.5 <= results[i+1]["null"]:
            # Interpolate
            r1, r2 = results[i], results[i+1]
            null_50_trust = r1["trust"] + (0.5 - r1["null"]) / (r2["null"] - r1["null"]) * (r2["trust"] - r1["trust"])
            break
    
    # Where does FULL hit 50%?
    full_50_trust = None
    for i in range(len(results) - 1):
        if results[i]["full"] < 0.5 <= results[i+1]["full"]:
            r1, r2 = results[i], results[i+1]
            full_50_trust = r1["trust"] + (0.5 - r1["full"]) / (r2["full"] - r1["full"]) * (r2["trust"] - r1["trust"])
            break
    
    # Where is gap maximized?
    max_gap_result = max(results, key=lambda x: x["gap"])
    
    null_50_str = f"{null_50_trust:.2f}" if null_50_trust else "N/A"
    full_50_str = f"{full_50_trust:.2f}" if full_50_trust else "N/A"
    shift_str = f"{(null_50_trust - full_50_trust)*100:+.0f}pp" if (null_50_trust and full_50_trust) else "N/A"
    
    print(f"""
NULL model 50% threshold:  trust ≈ {null_50_str}
FULL model 50% threshold:  trust ≈ {full_50_str}
Threshold shift:           {shift_str}

Maximum gap at:            trust = {max_gap_result['trust']:.2f}
                           NULL = {max_gap_result['null']*100:.1f}%, FULL = {max_gap_result['full']*100:.1f}%
                           GAP = {max_gap_result['gap']*100:+.1f}pp
    """)
    
    # Interpretation
    print("="*70)
    print("INTERPRETATION")
    print("="*70)
    
    if null_50_trust and full_50_trust:
        shift = null_50_trust - full_50_trust
        print(f"""
The Selene mechanisms shift the "cooperation threshold" by ~{shift*100:.0f}pp.

This means:
- Without mechanisms, you need trust ≈ {null_50_trust:.2f} for 50% success
- With mechanisms, you only need trust ≈ {full_50_trust:.2f} for 50% success

In practice: Mechanisms make cooperation viable even in medium-low trust
environments where it would otherwise fail.
        """)
    
    return results


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # A) Bootstrap CIs
    ci_results = run_with_bootstrap(n_runs=2000, n_bootstrap=2000)
    
    # B) Extreme bounds
    bounds_results = analyze_extreme_bounds(n_runs=500)
