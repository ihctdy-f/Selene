#!/usr/bin/env python3
"""
Verify V2 config produces reasonable outcomes on calibration cases.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selene_bilateral.upgraded_simulator import UpgradedBilateralSimulator
from selene_bilateral.state_agent import StateAgent, RegimeType
from selene_bilateral.sectors import SectorDependency, DependencyMatrix
from selene_bilateral.third_party import ThirdParty, ThirdPartySystem
from selene_bilateral.actions import ActionSpace, JAPAN_CHINA_ACTIONS
from selene_bilateral.deesc_config_v2 import DEESCALATION_CONFIG_V2, DEESCALATION_CONFIG_V1

import random
import statistics


def create_2010_scenario():
    """2010 China-Japan rare earth crisis - single actor, external pressure."""
    
    china = StateAgent(
        agent_id="CHN", name="China", gdp=6.0,
        regime_type=RegimeType.AUTOCRACY,
        nationalism_index=0.70, approval_rating=0.65,
        escalation_threshold=0.50, de_escalation_threshold=0.35,
        retaliation_propensity=0.25,
    )
    china.proactive_nationalism_coefficient = 0.55
    china.coercion_hope_coefficient = 0.60
    china.weakness_signal_coefficient = 0.40
    china.action_cooldown = 2
    china.restriction_intensity = {"rare_earths": 0.70}  # Started restricted
    
    japan = StateAgent(
        agent_id="JPN", name="Japan", gdp=5.5,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.40, approval_rating=0.40,
        escalation_threshold=0.95,  # Very high - Japan did NOT retaliate
        de_escalation_threshold=0.30,
        retaliation_propensity=0.15,
    )
    japan.proactive_nationalism_coefficient = 0.20
    japan.coercion_hope_coefficient = 0.30
    japan.weakness_signal_coefficient = 0.60
    japan.action_cooldown = 4
    japan.restriction_intensity = {}
    
    rare_earths = SectorDependency(
        sector_name="rare_earths",
        a_exports_to_b=0.95, b_exports_to_a=0.05,
        a_substitution_time=24, b_substitution_time=3,
        a_substitution_cost=0.3, b_substitution_cost=2.5,
        a_criticality_score=0.20, b_criticality_score=0.85,
        a_political_salience=0.70, b_political_salience=0.80,
        a_restriction_self_harm=0.15, b_restriction_self_harm=0.60,
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {"rare_earths": rare_earths}
    
    usa = ThirdParty("USA", "United States", alignment_with_a=-0.3,
                     intervention_threshold=0.35, coordination_bonus=0.60)
    eu = ThirdParty("EU", "European Union", alignment_with_a=-0.2,
                    intervention_threshold=0.40, coordination_bonus=0.50)
    wto = ThirdParty("WTO", "WTO", alignment_with_a=0.0,
                     intervention_threshold=0.50, coordination_bonus=0.40)
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {"usa": usa, "eu": eu, "wto": wto}
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return china, japan, dep_matrix, third_party_system, actions


def run_test(deesc_config, label, n_runs=200):
    """Run simulation and report key metrics."""
    
    config = {
        "max_steps": 24,
        "action_threshold": 0.03,
        "decision_noise": 0.04,
    }
    
    results = []
    for _ in range(n_runs):
        a, b, dep, tp, actions = create_2010_scenario()
        
        sim = UpgradedBilateralSimulator(
            state_a=a, state_b=b,
            dependency_matrix=dep,
            action_space=actions,
            third_party_system=tp,
            config=config,
            deescalation_config=deesc_config,
        )
        
        for _ in range(24):
            sim.step()
        
        results.append({
            "peak": sim.peak_friction,
            "final": sim.get_friction_level(),
            "normalized": sim.get_friction_level() < 0.15,
        })
    
    avg_peak = statistics.mean(r["peak"] for r in results)
    avg_final = statistics.mean(r["final"] for r in results)
    norm_rate = sum(1 for r in results if r["normalized"]) / len(results)
    
    print(f"\n{label}")
    print(f"  Peak friction:     {avg_peak:.3f}")
    print(f"  Final friction:    {avg_final:.3f}")
    print(f"  Normalization:     {norm_rate:.1%}")
    
    # 2010 targets: peak ~0.50-0.70, final < 0.15, normalization > 80%
    peak_ok = 0.40 <= avg_peak <= 0.80
    final_ok = avg_final < 0.20
    norm_ok = norm_rate > 0.70
    
    print(f"  Peak in range:     {'✓' if peak_ok else '✗'} (target 0.40-0.80)")
    print(f"  Final low enough:  {'✓' if final_ok else '✗'} (target < 0.20)")
    print(f"  Normalization:     {'✓' if norm_ok else '✗'} (target > 70%)")
    
    return peak_ok and final_ok and norm_ok


def create_2019_scenario():
    """2019 Japan-Korea trade dispute - bilateral, managed competition outcome."""
    
    japan = StateAgent(
        agent_id="JPN", name="Japan", gdp=5.1,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.50, approval_rating=0.45,
        escalation_threshold=0.45, de_escalation_threshold=0.35,
        retaliation_propensity=0.30,
    )
    japan.proactive_nationalism_coefficient = 0.40
    japan.coercion_hope_coefficient = 0.45
    japan.weakness_signal_coefficient = 0.35
    japan.action_cooldown = 3
    japan.restriction_intensity = {"semiconductors": 0.60}
    
    korea = StateAgent(
        agent_id="KOR", name="Korea", gdp=1.6,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.65, approval_rating=0.50,
        escalation_threshold=0.30, de_escalation_threshold=0.40,
        retaliation_propensity=0.65,
    )
    korea.proactive_nationalism_coefficient = 0.45
    korea.coercion_hope_coefficient = 0.40
    korea.weakness_signal_coefficient = 0.50
    korea.action_cooldown = 2
    korea.restriction_intensity = {"tourism": 0.30}
    
    semiconductors = SectorDependency(
        sector_name="semiconductors",
        a_exports_to_b=0.85, b_exports_to_a=0.20,
        a_substitution_time=4, b_substitution_time=18,
        a_substitution_cost=0.3, b_substitution_cost=2.0,
        a_criticality_score=0.35, b_criticality_score=0.80,
        a_political_salience=0.55, b_political_salience=0.75,
        a_restriction_self_harm=0.25, b_restriction_self_harm=0.45,
    )
    
    tourism = SectorDependency(
        sector_name="tourism",
        a_exports_to_b=0.40, b_exports_to_a=0.35,
        a_substitution_time=2, b_substitution_time=2,
        a_substitution_cost=0.2, b_substitution_cost=0.2,
        a_criticality_score=0.15, b_criticality_score=0.20,
        a_political_salience=0.55, b_political_salience=0.60,
        a_restriction_self_harm=0.30, b_restriction_self_harm=0.35,
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {"semiconductors": semiconductors, "tourism": tourism}
    
    usa = ThirdParty("USA", "United States", alignment_with_a=0.30,
                     intervention_threshold=0.40, coordination_bonus=0.50)
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {"usa": usa}
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return japan, korea, dep_matrix, third_party_system, actions


def run_2019_test(deesc_config, label, n_runs=200):
    """Run 2019 simulation and report key metrics."""
    
    config = {
        "max_steps": 18,
        "action_threshold": 0.03,
        "decision_noise": 0.04,
    }
    
    results = []
    for _ in range(n_runs):
        a, b, dep, tp, actions = create_2019_scenario()
        
        sim = UpgradedBilateralSimulator(
            state_a=a, state_b=b,
            dependency_matrix=dep,
            action_space=actions,
            third_party_system=tp,
            config=config,
            deescalation_config=deesc_config,
        )
        
        for _ in range(18):
            sim.step()
        
        final = sim.get_friction_level()
        results.append({
            "peak": sim.peak_friction,
            "final": final,
            "normalized": final < 0.10,
            "managed_competition": 0.15 <= final <= 0.40,
        })
    
    avg_peak = statistics.mean(r["peak"] for r in results)
    avg_final = statistics.mean(r["final"] for r in results)
    norm_rate = sum(1 for r in results if r["normalized"]) / len(results)
    mc_rate = sum(1 for r in results if r["managed_competition"]) / len(results)
    
    print(f"\n{label}")
    print(f"  Peak friction:     {avg_peak:.3f}")
    print(f"  Final friction:    {avg_final:.3f}")
    print(f"  Normalization:     {norm_rate:.1%}")
    print(f"  Managed Comp:      {mc_rate:.1%}")
    
    # 2019 targets: should NOT normalize, should reach managed competition
    norm_ok = norm_rate < 0.25  # Should NOT fully normalize
    mc_ok = mc_rate > 0.40 or avg_final > 0.15  # Should stay elevated
    
    print(f"  NOT normalized:    {'✓' if norm_ok else '✗'} (target norm < 25%)")
    print(f"  Elevated final:    {'✓' if mc_ok else '✗'} (target MC > 40% or final > 0.15)")
    
    return norm_ok and mc_ok


def main():
    print("=" * 60)
    print("V2 CONFIG VERIFICATION")
    print("=" * 60)
    
    print("\n--- 2010 China-Japan (should normalize) ---")
    v1_2010 = run_test(DEESCALATION_CONFIG_V1, "V1 CONFIG")
    v2_2010 = run_test(DEESCALATION_CONFIG_V2, "V2 CONFIG")
    
    print("\n--- 2019 Japan-Korea (should NOT normalize) ---")
    v1_2019 = run_2019_test(DEESCALATION_CONFIG_V1, "V1 CONFIG")
    v2_2019 = run_2019_test(DEESCALATION_CONFIG_V2, "V2 CONFIG")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"2010 (normalization case):")
    print(f"  V1: {'✓' if v1_2010 else '✗'}  V2: {'✓' if v2_2010 else '✗'}")
    print(f"2019 (managed competition case):")
    print(f"  V1: {'✓' if v1_2019 else '✗'}  V2: {'✓' if v2_2019 else '✗'}")
    
    all_pass = v1_2010 and v2_2010 and v1_2019 and v2_2019
    if all_pass:
        print("\n✓ V2 config produces qualitatively correct outcomes for both cases")
    elif v2_2010 and v2_2019:
        print("\n✓ V2 config passes both scenarios")
    else:
        print("\n⚠ V2 config needs adjustment")


if __name__ == "__main__":
    main()
