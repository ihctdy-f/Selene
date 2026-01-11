#!/usr/bin/env python3
"""
SENSITIVITY ANALYSIS
====================
Systematically vary each parameter while holding others at baseline.
Measure impact on key outcomes to identify which parameters matter.

Method: One-at-a-time (OAT) sensitivity + variance-based importance
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selene_bilateral.upgraded_simulator import UpgradedBilateralSimulator
from selene_bilateral.state_agent import StateAgent, RegimeType
from selene_bilateral.sectors import SectorDependency, DependencyMatrix
from selene_bilateral.third_party import ThirdParty, ThirdPartySystem
from selene_bilateral.actions import ActionSpace, JAPAN_CHINA_ACTIONS

import random
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json


# ============================================================================
# BASELINE CONFIGURATION - NOW V2
# ============================================================================
BASELINE_DEESC = {
    "maintenance_cost": 0.35,
    "time_accel": 0.30,
    "grace_period": 1,
    "pressure_rate": 0.15,
    "duration_sens": 0.15,
    "friction_thresh": 0.15,
    "max_pressure": 0.50,
    "fatigue_rate": 0.05,
    "gdp_thresh": 0.3,
    "max_fatigue": 0.40,
    "bleed_rate": 0.020,
    "intensity_thresh": 0.25,
    "friction_memory_decay": 0.85,
    "memory_coefficient": 0.12,
    "peak_coefficient": 0.10,
}

# Parameter ranges to test (low, baseline, high)
PARAM_RANGES = {
    "maintenance_cost": (0.10, 0.35, 0.60),
    "time_accel": (0.10, 0.30, 0.50),
    "grace_period": (0, 1, 4),
    "pressure_rate": (0.05, 0.15, 0.30),
    "duration_sens": (0.05, 0.15, 0.25),
    "friction_thresh": (0.05, 0.15, 0.35),
    "max_pressure": (0.25, 0.50, 0.75),
    "fatigue_rate": (0.02, 0.05, 0.10),
    "gdp_thresh": (0.1, 0.3, 0.8),
    "max_fatigue": (0.20, 0.40, 0.60),
    "bleed_rate": (0.010, 0.020, 0.040),
    "intensity_thresh": (0.10, 0.25, 0.45),
    "friction_memory_decay": (0.75, 0.85, 0.95),
    "memory_coefficient": (0.05, 0.12, 0.20),
    "peak_coefficient": (0.04, 0.10, 0.18),
}

BASELINE_CONFIG = {
    "max_steps": 18,
    "pain_relief_coefficient": 0.40,
    "relationship_coefficient": 0.20,
    "audience_cost_base": 0.25,
    "action_threshold": 0.03,
    "decision_noise": 0.04,
    "diversification_rate": 0.02,
}


def create_test_scenario():
    """Create a bilateral scenario for sensitivity testing (based on 2019)."""
    
    japan = StateAgent(
        agent_id="JPN", name="Japan",
        gdp=5.1, regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.50, approval_rating=0.45,
        escalation_threshold=0.45, de_escalation_threshold=0.35,
        retaliation_propensity=0.30,
    )
    japan.proactive_nationalism_coefficient = 0.40
    japan.coercion_hope_coefficient = 0.45
    japan.weakness_signal_coefficient = 0.35
    japan.action_cooldown = 3
    japan.restriction_intensity = {"sector_a": 0.50}
    
    korea = StateAgent(
        agent_id="KOR", name="Korea",
        gdp=1.6, regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.65, approval_rating=0.50,
        escalation_threshold=0.30, de_escalation_threshold=0.40,
        retaliation_propensity=0.65,
    )
    korea.proactive_nationalism_coefficient = 0.45
    korea.coercion_hope_coefficient = 0.40
    korea.weakness_signal_coefficient = 0.50
    korea.action_cooldown = 2
    korea.restriction_intensity = {"sector_a": 0.20}
    
    sector_a = SectorDependency(
        sector_name="sector_a",
        a_exports_to_b=0.70, b_exports_to_a=0.15,
        a_substitution_time=6, b_substitution_time=18,
        a_substitution_cost=0.4, b_substitution_cost=2.0,
        a_criticality_score=0.30, b_criticality_score=0.80,
        a_political_salience=0.60, b_political_salience=0.75,
        a_restriction_self_harm=0.30, b_restriction_self_harm=0.50,
    )
    
    sector_b = SectorDependency(
        sector_name="sector_b",
        a_exports_to_b=0.40, b_exports_to_a=0.35,
        a_substitution_time=4, b_substitution_time=4,
        a_substitution_cost=0.3, b_substitution_cost=0.3,
        a_criticality_score=0.25, b_criticality_score=0.25,
        a_political_salience=0.50, b_political_salience=0.55,
        a_restriction_self_harm=0.35, b_restriction_self_harm=0.35,
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {"sector_a": sector_a, "sector_b": sector_b}
    
    usa = ThirdParty("USA", "United States", alignment_with_a=0.45,
                     intervention_threshold=0.30, coordination_bonus=0.55)
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {"usa": usa}
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return japan, korea, dep_matrix, third_party_system, actions


@dataclass
class RunResult:
    peak_friction: float
    final_friction: float
    normalization: bool  # final < 0.10
    deesc_events: int
    steps_to_peak: int


def run_simulation(deesc_config: Dict, n_runs: int = 100) -> List[RunResult]:
    """Run multiple simulations with given config."""
    results = []
    
    for _ in range(n_runs):
        a, b, dep, tp, actions = create_test_scenario()
        
        sim = UpgradedBilateralSimulator(
            state_a=a, state_b=b,
            dependency_matrix=dep,
            action_space=actions,
            third_party_system=tp,
            config=BASELINE_CONFIG,
            deescalation_config=deesc_config,
        )
        
        peak = 0
        peak_step = 0
        for step in range(18):
            sim.step()
            if sim.get_friction_level() > peak:
                peak = sim.get_friction_level()
                peak_step = step
        
        results.append(RunResult(
            peak_friction=sim.peak_friction,
            final_friction=sim.get_friction_level(),
            normalization=sim.get_friction_level() < 0.10,
            deesc_events=sim.deescalation_events,
            steps_to_peak=peak_step,
        ))
    
    return results


def compute_metrics(results: List[RunResult]) -> Dict[str, float]:
    """Compute summary metrics from results."""
    return {
        "avg_peak": statistics.mean(r.peak_friction for r in results),
        "avg_final": statistics.mean(r.final_friction for r in results),
        "norm_rate": sum(1 for r in results if r.normalization) / len(results),
        "avg_deesc": statistics.mean(r.deesc_events for r in results),
        "std_final": statistics.stdev(r.final_friction for r in results) if len(results) > 1 else 0,
    }


def run_oat_sensitivity(n_runs_per_config: int = 100):
    """One-at-a-time sensitivity analysis."""
    
    print("=" * 70)
    print("ONE-AT-A-TIME SENSITIVITY ANALYSIS")
    print("=" * 70)
    print(f"\nVarying each parameter (low → baseline → high)")
    print(f"Runs per config: {n_runs_per_config}")
    
    # First, get baseline metrics
    print("\n--- Running Baseline ---")
    baseline_results = run_simulation(BASELINE_DEESC, n_runs_per_config)
    baseline_metrics = compute_metrics(baseline_results)
    print(f"Baseline: peak={baseline_metrics['avg_peak']:.3f}, "
          f"final={baseline_metrics['avg_final']:.3f}, "
          f"norm={baseline_metrics['norm_rate']:.1%}")
    
    # Store sensitivity results
    sensitivity = {}
    
    for param, (low, base, high) in PARAM_RANGES.items():
        print(f"\n--- Testing: {param} ---")
        
        results_by_level = {}
        
        for level, value in [("low", low), ("baseline", base), ("high", high)]:
            config = BASELINE_DEESC.copy()
            config[param] = value
            
            results = run_simulation(config, n_runs_per_config)
            metrics = compute_metrics(results)
            results_by_level[level] = metrics
            
            print(f"  {level:>8} ({value:>6}): final={metrics['avg_final']:.3f}, "
                  f"norm={metrics['norm_rate']:.1%}, deesc={metrics['avg_deesc']:.1f}")
        
        # Compute sensitivity metrics
        final_range = results_by_level["high"]["avg_final"] - results_by_level["low"]["avg_final"]
        norm_range = results_by_level["high"]["norm_rate"] - results_by_level["low"]["norm_rate"]
        deesc_range = results_by_level["high"]["avg_deesc"] - results_by_level["low"]["avg_deesc"]
        
        sensitivity[param] = {
            "final_range": final_range,
            "norm_range": norm_range,
            "deesc_range": deesc_range,
            "results": results_by_level,
        }
    
    return baseline_metrics, sensitivity


def compute_importance_scores(sensitivity: Dict) -> Dict[str, float]:
    """Compute normalized importance scores for each parameter."""
    
    # Normalize ranges to 0-1 scale based on max observed range
    max_final = max(abs(s["final_range"]) for s in sensitivity.values())
    max_norm = max(abs(s["norm_range"]) for s in sensitivity.values())
    max_deesc = max(abs(s["deesc_range"]) for s in sensitivity.values())
    
    importance = {}
    for param, data in sensitivity.items():
        # Combined importance: weighted sum of normalized impacts
        final_imp = abs(data["final_range"]) / max_final if max_final > 0 else 0
        norm_imp = abs(data["norm_range"]) / max_norm if max_norm > 0 else 0
        deesc_imp = abs(data["deesc_range"]) / max_deesc if max_deesc > 0 else 0
        
        # Weight: final friction and normalization matter most
        importance[param] = 0.4 * final_imp + 0.4 * norm_imp + 0.2 * deesc_imp
    
    return importance


def run_interaction_test(param1: str, param2: str, n_runs: int = 80):
    """Test interaction between two parameters."""
    
    low1, base1, high1 = PARAM_RANGES[param1]
    low2, base2, high2 = PARAM_RANGES[param2]
    
    results_grid = {}
    
    for v1, l1 in [(low1, "low"), (high1, "high")]:
        for v2, l2 in [(low2, "low"), (high2, "high")]:
            config = BASELINE_DEESC.copy()
            config[param1] = v1
            config[param2] = v2
            
            results = run_simulation(config, n_runs)
            metrics = compute_metrics(results)
            results_grid[(l1, l2)] = metrics["avg_final"]
    
    # Interaction effect: deviation from additive model
    # If no interaction: (high,high) - (low,high) ≈ (high,low) - (low,low)
    effect_p1_at_low_p2 = results_grid[("high", "low")] - results_grid[("low", "low")]
    effect_p1_at_high_p2 = results_grid[("high", "high")] - results_grid[("low", "high")]
    
    interaction = effect_p1_at_high_p2 - effect_p1_at_low_p2
    
    return results_grid, interaction


def main():
    print("=" * 70)
    print("BILATERAL FRICTION MODEL - SENSITIVITY ANALYSIS")
    print("=" * 70)
    
    # Run OAT analysis
    baseline, sensitivity = run_oat_sensitivity(n_runs_per_config=100)
    
    # Compute importance scores
    importance = compute_importance_scores(sensitivity)
    
    # Sort by importance
    sorted_params = sorted(importance.items(), key=lambda x: -x[1])
    
    print("\n" + "=" * 70)
    print("PARAMETER IMPORTANCE RANKING")
    print("=" * 70)
    print(f"\n{'Rank':<5} {'Parameter':<22} {'Importance':<12} {'Final Δ':<12} {'Norm Δ':<12}")
    print("-" * 65)
    
    for rank, (param, imp) in enumerate(sorted_params, 1):
        data = sensitivity[param]
        final_delta = data["final_range"]
        norm_delta = data["norm_range"]
        
        bar = "█" * int(imp * 30)
        print(f"{rank:<5} {param:<22} {imp:>8.3f}    {final_delta:>+8.3f}    {norm_delta:>+8.1%}")
        print(f"      {bar}")
    
    # Categorize parameters
    print("\n" + "=" * 70)
    print("PARAMETER CATEGORIES")
    print("=" * 70)
    
    high_impact = [p for p, i in sorted_params if i > 0.5]
    med_impact = [p for p, i in sorted_params if 0.2 <= i <= 0.5]
    low_impact = [p for p, i in sorted_params if i < 0.2]
    
    print(f"\n🔴 HIGH IMPACT (tune carefully):")
    for p in high_impact:
        low, base, high = PARAM_RANGES[p]
        print(f"   {p}: range [{low} - {high}]")
    
    print(f"\n🟡 MEDIUM IMPACT:")
    for p in med_impact:
        low, base, high = PARAM_RANGES[p]
        print(f"   {p}: range [{low} - {high}]")
    
    print(f"\n🟢 LOW IMPACT (can simplify/fix):")
    for p in low_impact:
        low, base, high = PARAM_RANGES[p]
        print(f"   {p}: range [{low} - {high}]")
    
    # Test top interactions
    if len(high_impact) >= 2:
        print("\n" + "=" * 70)
        print("INTERACTION EFFECTS (Top 2 Parameters)")
        print("=" * 70)
        
        p1, p2 = high_impact[0], high_impact[1]
        print(f"\nTesting interaction: {p1} × {p2}")
        
        grid, interaction = run_interaction_test(p1, p2, n_runs=80)
        
        print(f"\n  Final friction grid:")
        print(f"  {'':>15} {p2}=low    {p2}=high")
        print(f"  {p1}=low      {grid[('low','low')]:>8.3f}   {grid[('low','high')]:>8.3f}")
        print(f"  {p1}=high     {grid[('high','low')]:>8.3f}   {grid[('high','high')]:>8.3f}")
        print(f"\n  Interaction effect: {interaction:+.3f}")
        
        if abs(interaction) > 0.05:
            print(f"  ⚠️  Significant interaction - parameters affect each other")
        else:
            print(f"  ✓ Weak interaction - parameters roughly additive")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"""
Key findings:
1. {len(high_impact)} parameters have high impact on outcomes
2. {len(low_impact)} parameters could be fixed/removed to simplify model
3. Focus calibration effort on: {', '.join(high_impact[:3])}

Model parsimony recommendation:
- Essential parameters: {', '.join(high_impact)}
- Optional parameters: {', '.join(med_impact)}  
- Remove/fix: {', '.join(low_impact)}
""")
    
    # Save results
    output = {
        "baseline": baseline,
        "importance": importance,
        "sensitivity": {k: {"final_range": v["final_range"], 
                           "norm_range": v["norm_range"],
                           "deesc_range": v["deesc_range"]} 
                        for k, v in sensitivity.items()},
        "categories": {
            "high_impact": high_impact,
            "medium_impact": med_impact,
            "low_impact": low_impact,
        }
    }
    
    with open("sensitivity_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nResults saved to sensitivity_results.json")


if __name__ == "__main__":
    main()
