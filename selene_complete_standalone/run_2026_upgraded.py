#!/usr/bin/env python3
"""
2026 Japan-China Scenario - UPGRADED with De-escalation Dynamics
================================================================

Runs the same scenario but with the architecture fix that enables
realistic de-escalation patterns.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selene_bilateral.upgraded_simulator import (
    UpgradedBilateralSimulator,
    OutcomeCategory,
)
from selene_bilateral.state_agent import StateAgent, RegimeType
from selene_bilateral.sectors import SectorDependency, DependencyMatrix
from selene_bilateral.third_party import ThirdParty, ThirdPartySystem
from selene_bilateral.actions import ActionSpace, JAPAN_CHINA_ACTIONS

import random


def create_2026_scenario():
    """Create 2026 Japan-China scenario (same as base version)."""
    
    japan = StateAgent(
        agent_id="JPN",
        name="Japan_2026",
        gdp=4.2,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.65,
        approval_rating=0.35,
        escalation_threshold=0.40,
        de_escalation_threshold=0.25,
        retaliation_propensity=0.45,
    )
    japan.proactive_nationalism_coefficient = 0.15
    japan.coercion_hope_coefficient = 0.20
    japan.weakness_signal_coefficient = 0.30
    japan.action_cooldown = 3
    japan.restriction_intensity = {"semiconductors": 0.70}
    
    china = StateAgent(
        agent_id="CHN",
        name="China_2026",
        gdp=17.8,
        regime_type=RegimeType.AUTOCRACY,
        nationalism_index=0.80,
        approval_rating=0.65,
        escalation_threshold=0.15,
        de_escalation_threshold=0.30,
        retaliation_propensity=0.85,
    )
    china.proactive_nationalism_coefficient = 0.50
    china.coercion_hope_coefficient = 0.55
    china.weakness_signal_coefficient = 0.25
    china.action_cooldown = 1
    china.restriction_intensity = {
        "critical_minerals": 0.60,
        "rare_earths": 0.30,
    }
    
    # Sectors (same as before)
    semiconductors = SectorDependency(
        sector_name="semiconductors",
        a_exports_to_b=0.4, b_exports_to_a=0.2,
        a_substitution_time=24, b_substitution_time=18,
        a_substitution_cost=1.5, b_substitution_cost=1.2,
        a_criticality_score=0.70, b_criticality_score=0.50,
        a_political_salience=0.80, b_political_salience=0.60,
        a_restriction_self_harm=0.35, b_restriction_self_harm=0.20,
    )
    
    critical_minerals = SectorDependency(
        sector_name="critical_minerals",
        a_exports_to_b=0.05, b_exports_to_a=0.70,
        a_substitution_time=36, b_substitution_time=12,
        a_substitution_cost=2.5, b_substitution_cost=1.0,
        a_criticality_score=0.85, b_criticality_score=0.15,
        a_political_salience=0.70, b_political_salience=0.50,
        a_restriction_self_harm=0.05, b_restriction_self_harm=0.40,
    )
    
    rare_earths = SectorDependency(
        sector_name="rare_earths",
        a_exports_to_b=0.05, b_exports_to_a=0.60,
        a_substitution_time=24, b_substitution_time=12,
        a_substitution_cost=1.8, b_substitution_cost=1.1,
        a_criticality_score=0.75, b_criticality_score=0.20,
        a_political_salience=0.65, b_political_salience=0.55,
        a_restriction_self_harm=0.05, b_restriction_self_harm=0.50,
    )
    
    tourism = SectorDependency(
        sector_name="tourism",
        a_exports_to_b=0.3, b_exports_to_a=0.5,
        a_substitution_time=3, b_substitution_time=6,
        a_substitution_cost=0.3, b_substitution_cost=0.5,
        a_criticality_score=0.25, b_criticality_score=0.35,
        a_political_salience=0.40, b_political_salience=0.50,
        a_restriction_self_harm=0.15, b_restriction_self_harm=0.25,
    )
    
    automotive = SectorDependency(
        sector_name="automotive",
        a_exports_to_b=0.5, b_exports_to_a=0.3,
        a_substitution_time=18, b_substitution_time=24,
        a_substitution_cost=1.3, b_substitution_cost=1.5,
        a_criticality_score=0.60, b_criticality_score=0.55,
        a_political_salience=0.70, b_political_salience=0.65,
        a_restriction_self_harm=0.40, b_restriction_self_harm=0.35,
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {
        "semiconductors": semiconductors,
        "critical_minerals": critical_minerals,
        "rare_earths": rare_earths,
        "tourism": tourism,
        "automotive": automotive,
    }
    
    # Third parties (same)
    usa = ThirdParty(
        party_id="USA", name="United States",
        alignment_with_a=0.85, intervention_threshold=0.30,
        coordination_bonus=0.25, alternative_supply_capacity=0.15,
    )
    eu = ThirdParty(
        party_id="EU", name="European Union",
        alignment_with_a=0.50, intervention_threshold=0.50,
        coordination_bonus=0.10, alternative_supply_capacity=0.10,
    )
    south_korea = ThirdParty(
        party_id="KOR", name="South Korea",
        alignment_with_a=0.60, intervention_threshold=0.45,
        coordination_bonus=0.15, alternative_supply_capacity=0.20,
    )
    taiwan = ThirdParty(
        party_id="TWN", name="Taiwan",
        alignment_with_a=0.90, intervention_threshold=0.20,
        coordination_bonus=0.20, alternative_supply_capacity=0.30,
    )
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {
        "usa": usa, "eu": eu, "south_korea": south_korea, "taiwan": taiwan,
    }
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return japan, china, dep_matrix, third_party_system, actions


def run_upgraded_2026(n_runs=500, max_steps=48):
    """Run upgraded scenario."""
    
    print("=" * 70)
    print("JAPAN-CHINA 2026 - UPGRADED DE-ESCALATION DYNAMICS")
    print("=" * 70)
    
    japan, china, dep_matrix, third_party_system, actions = create_2026_scenario()
    
    print("\n--- Initial Conditions (same as base) ---")
    print(f"Japan restrictions: {japan.restriction_intensity}")
    print(f"China restrictions: {china.restriction_intensity}")
    
    print(f"\nRunning {n_runs} simulations ({max_steps} months each)...")
    print("(with time-decay, intl pressure, econ fatigue, reputation)")
    
    config = {
        "max_steps": max_steps,
        "pain_relief_coefficient": 0.4,
        "relationship_coefficient": 0.2,
        "audience_cost_base": 0.25,
        "action_threshold": 0.03,
        "decision_noise": 0.04,
        "diversification_rate": 0.015,
    }
    
    # De-escalation config - TUNED FOR 2026 ONGOING COMPETITION
    # Weaker than 2010 crisis because:
    # - Both sides restricting (no clear "bad actor")
    # - Normalized rivalry, not acute crisis
    # - Lower international pressure (US encouraging Japan)
    deesc_config = {
        "maintenance_cost": 0.025,      # Lower - normalized rivalry
        "time_accel": 0.08,             # Slower acceleration
        "grace_period": 8,              # Longer grace - ongoing competition
        "pressure_rate": 0.02,          # Lower international pressure
        "duration_sens": 0.04,          # Less sensitive to duration
        "friction_thresh": 0.50,        # Higher threshold
        "max_pressure": 0.25,           # Lower max pressure
        "fatigue_rate": 0.02,           # Slower fatigue
        "gdp_thresh": 5.0,              # Higher threshold
        "max_fatigue": 0.25,
        "bleed_rate": 0.005,            # Lower reputation cost
        "intensity_thresh": 0.55,
        "friction_memory_decay": 0.95,  # Slower memory decay
    }
    
    results = []
    for i in range(n_runs):
        if (i + 1) % 100 == 0:
            print(f"  Completed {i+1}/{n_runs}...")
        
        japan, china, dep_matrix, third_party_system, actions = create_2026_scenario()
        
        sim = UpgradedBilateralSimulator(
            state_a=japan,
            state_b=china,
            dependency_matrix=dep_matrix,
            action_space=actions,
            third_party_system=third_party_system,
            config=config,
            deescalation_config=deesc_config,
        )
        
        result = sim.run()
        results.append(result)
    
    # Analyze
    print("\n" + "=" * 70)
    print("UPGRADED SIMULATION RESULTS")
    print("=" * 70)
    
    outcome_counts = {}
    for r in results:
        cat = r.outcome_category.value
        outcome_counts[cat] = outcome_counts.get(cat, 0) + 1
    
    print("\n--- Outcome Distribution ---")
    print(f"{'Outcome':<30} {'Count':>8} {'Percent':>10}")
    print("-" * 50)
    for outcome in ['normalization', 'stable_interdependence', 'managed_competition',
                    'escalation_spiral', 'gradual_decoupling', 'asymmetric_lock_in']:
        count = outcome_counts.get(outcome, 0)
        pct = count / n_runs * 100
        bar = "█" * int(pct / 2.5)
        print(f"{outcome:<30} {count:>8} {pct:>9.1f}% {bar}")
    
    # Metrics
    avg_peak = sum(r.peak_friction_level for r in results) / n_runs
    avg_gdp_japan = sum(r.cumulative_gdp_loss_a for r in results) / n_runs
    avg_gdp_china = sum(r.cumulative_gdp_loss_b for r in results) / n_runs
    avg_div_japan = sum(r.final_diversification_a for r in results) / n_runs
    avg_div_china = sum(r.final_diversification_b for r in results) / n_runs
    avg_steps = sum(r.steps_to_terminal for r in results) / n_runs
    avg_escalations = sum(r.escalation_cycles for r in results) / n_runs
    avg_deescalations = sum(r.deescalation_events for r in results) / n_runs
    
    print("\n--- Key Metrics ---")
    print(f"Average Peak Friction:    {avg_peak:.3f}")
    print(f"Average Steps:            {avg_steps:.1f} months")
    print(f"Avg Escalation Cycles:    {avg_escalations:.1f}")
    print(f"Avg De-escalation Events: {avg_deescalations:.1f}")  # NEW
    print(f"\nJapan:")
    print(f"  Avg GDP Loss:           {avg_gdp_japan:.1f}")
    print(f"  Avg Diversification:    {avg_div_japan:.2f}")
    print(f"\nChina:")
    print(f"  Avg GDP Loss:           {avg_gdp_china:.1f}")
    print(f"  Avg Diversification:    {avg_div_china:.2f}")
    
    # Risk assessment
    spiral_rate = outcome_counts.get('escalation_spiral', 0) / n_runs
    decouple_rate = outcome_counts.get('gradual_decoupling', 0) / n_runs
    stable_rate = (outcome_counts.get('normalization', 0) +
                   outcome_counts.get('stable_interdependence', 0) +
                   outcome_counts.get('managed_competition', 0)) / n_runs
    
    print("\n--- Risk Assessment (Upgraded) ---")
    print(f"Escalation Spiral Risk:   {spiral_rate*100:>5.1f}%", end="")
    if spiral_rate > 0.20:
        print(" ⚠️  HIGH RISK")
    elif spiral_rate > 0.10:
        print(" ⚡ ELEVATED")
    else:
        print(" ✓ LOW")
    
    print(f"Decoupling Risk:          {decouple_rate*100:>5.1f}%", end="")
    if decouple_rate > 0.30:
        print(" ⚠️  HIGH RISK")
    elif decouple_rate > 0.15:
        print(" ⚡ ELEVATED")
    else:
        print(" ✓ LOW")
    
    print(f"Stabilization Chance:     {stable_rate*100:>5.1f}%", end="")
    if stable_rate > 0.50:
        print(" ✓ GOOD")
    elif stable_rate > 0.25:
        print(" ⚡ MODERATE")
    else:
        print(" ⚠️  LOW")
    
    # De-escalation effectiveness
    print(f"\n--- De-escalation Dynamics ---")
    print(f"Avg de-escalations per run: {avg_deescalations:.2f}")
    if avg_deescalations > 1.0:
        print("✓ Architecture fix is generating de-escalation behavior")
    else:
        print("⚠️  De-escalation still rare - may need parameter tuning")
    
    print("\n" + "=" * 70)
    
    return results


def run_diagnostic_upgraded():
    """Single diagnostic run with step-by-step output."""
    
    japan, china, dep_matrix, third_party_system, actions = create_2026_scenario()
    
    config = {
        "max_steps": 36,
        "action_threshold": 0.03,
        "decision_noise": 0.04,
    }
    
    deesc_config = {
        "maintenance_cost": 0.025,
        "time_accel": 0.08,
        "grace_period": 8,
        "pressure_rate": 0.02,
        "duration_sens": 0.04,
        "friction_thresh": 0.50,
        "max_pressure": 0.25,
        "fatigue_rate": 0.02,
        "gdp_thresh": 5.0,
        "max_fatigue": 0.25,
        "bleed_rate": 0.005,
        "intensity_thresh": 0.55,
        "friction_memory_decay": 0.95,
    }
    
    sim = UpgradedBilateralSimulator(
        state_a=japan,
        state_b=china,
        dependency_matrix=dep_matrix,
        action_space=actions,
        third_party_system=third_party_system,
        config=config,
        deescalation_config=deesc_config,
    )
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC - UPGRADED 2026 SCENARIO")
    print("=" * 70)
    print(f"\nInitial Japan restrictions: {japan.restriction_intensity}")
    print(f"Initial China restrictions: {china.restriction_intensity}")
    print()
    
    for step in range(36):
        record = sim.step()
        
        print(f"Month {record.step:2d}: friction={record.friction_level:.3f} | "
              f"JPN loss={japan.cumulative_gdp_loss:5.1f} deesc_p={record.deescalation_pressure_a:.3f} | "
              f"CHN loss={china.cumulative_gdp_loss:5.1f} deesc_p={record.deescalation_pressure_b:.3f}")
        
        for action in record.actions_taken:
            actor = "Japan" if action['actor'] == 'A' else "China"
            symbol = "↓" if action['type'] == 'de_escalate' else "↑"
            print(f"       {symbol} {actor} {action['type']}: {action['sector']} "
                  f"({action.get('from_intensity', 0):.2f} -> {action.get('to_intensity', 0):.2f})")
    
    print(f"\n--- Final State ---")
    print(f"Final friction: {sim.get_friction_level():.3f}")
    print(f"Peak friction:  {sim.peak_friction:.3f}")
    print(f"De-escalation events: {sim.deescalation_events}")
    print(f"Japan restrictions: {dict(japan.restriction_intensity)}")
    print(f"China restrictions: {dict(china.restriction_intensity)}")


def compare_base_vs_upgraded(n_runs=300):
    """Run comparison between base and upgraded models."""
    
    print("=" * 70)
    print("COMPARISON: BASE MODEL vs UPGRADED DE-ESCALATION")
    print("=" * 70)
    
    # Import base simulator
    from run_2026_scenario import run_2026_simulation
    
    print("\n>>> Running BASE model...")
    base_results = run_2026_simulation(n_runs=n_runs, max_steps=48)
    
    print("\n>>> Running UPGRADED model...")
    upgraded_results = run_upgraded_2026(n_runs=n_runs, max_steps=48)
    
    # Summary comparison
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    
    def get_stats(results):
        outcomes = {}
        for r in results:
            cat = r.outcome_category.value if hasattr(r.outcome_category, 'value') else str(r.outcome_category)
            outcomes[cat] = outcomes.get(cat, 0) + 1
        return {
            "spiral": outcomes.get('escalation_spiral', 0) / len(results),
            "decouple": outcomes.get('gradual_decoupling', 0) / len(results),
            "normalize": outcomes.get('normalization', 0) / len(results),
            "stable": outcomes.get('stable_interdependence', 0) / len(results),
            "managed": outcomes.get('managed_competition', 0) / len(results),
            "peak": sum(r.peak_friction_level for r in results) / len(results),
        }
    
    base = get_stats(base_results)
    upgr = get_stats(upgraded_results)
    
    print(f"\n{'Metric':<30} {'Base':>12} {'Upgraded':>12} {'Change':>12}")
    print("-" * 70)
    print(f"{'Escalation Spiral':<30} {base['spiral']*100:>11.1f}% {upgr['spiral']*100:>11.1f}% {(upgr['spiral']-base['spiral'])*100:>+11.1f}%")
    print(f"{'Gradual Decoupling':<30} {base['decouple']*100:>11.1f}% {upgr['decouple']*100:>11.1f}% {(upgr['decouple']-base['decouple'])*100:>+11.1f}%")
    print(f"{'Normalization':<30} {base['normalize']*100:>11.1f}% {upgr['normalize']*100:>11.1f}% {(upgr['normalize']-base['normalize'])*100:>+11.1f}%")
    print(f"{'Stable Interdep.':<30} {base['stable']*100:>11.1f}% {upgr['stable']*100:>11.1f}% {(upgr['stable']-base['stable'])*100:>+11.1f}%")
    print(f"{'Managed Competition':<30} {base['managed']*100:>11.1f}% {upgr['managed']*100:>11.1f}% {(upgr['managed']-base['managed'])*100:>+11.1f}%")
    print(f"{'Peak Friction':<30} {base['peak']:>12.3f} {upgr['peak']:>12.3f} {upgr['peak']-base['peak']:>+12.3f}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--runs", type=int, default=500)
    parser.add_argument("-d", "--diagnostic", action="store_true")
    parser.add_argument("-c", "--compare", action="store_true")
    parser.add_argument("-s", "--steps", type=int, default=48)
    
    args = parser.parse_args()
    
    if args.diagnostic:
        run_diagnostic_upgraded()
    elif args.compare:
        compare_base_vs_upgraded(n_runs=args.runs)
    else:
        run_upgraded_2026(n_runs=args.runs, max_steps=args.steps)
