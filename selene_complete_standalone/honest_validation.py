#!/usr/bin/env python3
"""
HONEST VALIDATION TEST (Structural Consistency)
================================================
Use SAME de-escalation parameters for both 2010 and 2019 cases.
If the model architecture is sound, it should produce QUALITATIVELY
different outcomes based on scenario setup alone, not parameter tuning.

The key structural differences are:
- 2010: Single-actor (China only), strong int'l pressure, acute crisis
- 2019: Bilateral (both sides), US mediation, historical grievances

If parameters are held constant, the MODEL STRUCTURE (agent profiles,
sector dependencies, third parties) should drive different outcomes.

PURPOSE: This tests whether model structure contributes to results,
or whether all the work is done by case-specific parameter tuning.
A positive result suggests the model has genuine structural content.

INTERPRETATION: This is an internal consistency test, not external 
validation. Passing this test does not prove the model is correct
about reality - only that its architecture has some predictive 
content beyond parameter flexibility.

Version: 2.1 (updated per review - clarified test purpose)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selene_bilateral.upgraded_simulator import UpgradedBilateralSimulator
from selene_bilateral.state_agent import StateAgent, RegimeType
from selene_bilateral.sectors import SectorDependency, DependencyMatrix
from selene_bilateral.third_party import ThirdParty, ThirdPartySystem
from selene_bilateral.actions import ActionSpace, JAPAN_CHINA_ACTIONS


# ============================================================================
# SINGLE PARAMETER SET FOR ALL CASES
# ============================================================================
UNIVERSAL_DEESC_CONFIG = {
    "maintenance_cost": 0.04,
    "time_accel": 0.15,
    "grace_period": 4,
    "pressure_rate": 0.08,
    "duration_sens": 0.10,
    "friction_thresh": 0.35,
    "max_pressure": 0.50,
    "fatigue_rate": 0.05,
    "gdp_thresh": 2.0,
    "max_fatigue": 0.40,
    "bleed_rate": 0.012,
    "intensity_thresh": 0.40,
    "friction_memory_decay": 0.88,
}

UNIVERSAL_CONFIG = {
    "max_steps": 18,
    "pain_relief_coefficient": 0.40,
    "relationship_coefficient": 0.20,
    "audience_cost_base": 0.25,
    "action_threshold": 0.03,
    "decision_noise": 0.04,
    "diversification_rate": 0.02,
}


def create_2010_scenario():
    """2010 China-Japan: SINGLE ACTOR crisis."""
    
    # Japan 2010 - DPJ government, did NOT retaliate
    japan = StateAgent(
        agent_id="JPN",
        name="Japan_2010",
        gdp=5.7,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.40,
        approval_rating=0.35,
        escalation_threshold=0.95,      # KEY: Japan did NOT escalate
        de_escalation_threshold=0.30,
        retaliation_propensity=0.05,    # KEY: Very low retaliation
    )
    japan.proactive_nationalism_coefficient = 0.10
    japan.coercion_hope_coefficient = 0.20
    japan.weakness_signal_coefficient = 0.30
    japan.action_cooldown = 5
    japan.restriction_intensity = {}  # Japan imposed NOTHING
    
    # China 2010 - Pre-Xi, aggressive on RE
    china = StateAgent(
        agent_id="CHN",
        name="China_2010",
        gdp=6.1,
        regime_type=RegimeType.AUTOCRACY,
        nationalism_index=0.75,
        approval_rating=0.70,
        escalation_threshold=0.10,      # Quick to escalate
        de_escalation_threshold=0.45,   # But backs down under pressure
        retaliation_propensity=0.60,
    )
    china.proactive_nationalism_coefficient = 0.65
    china.coercion_hope_coefficient = 0.70
    china.weakness_signal_coefficient = 0.50
    china.action_cooldown = 1
    china.restriction_intensity = {"rare_earths": 0.70}  # Initial restriction
    
    # Single sector - rare earths
    rare_earths = SectorDependency(
        sector_name="rare_earths",
        a_exports_to_b=0.05,
        b_exports_to_a=0.93,            # China dominance
        a_substitution_time=24, b_substitution_time=3,
        a_substitution_cost=3.0, b_substitution_cost=0.2,
        a_criticality_score=0.95,
        b_criticality_score=0.10,
        a_political_salience=0.80, b_political_salience=0.70,
        a_restriction_self_harm=0.10,
        b_restriction_self_harm=0.45,   # China self-harm from embargo
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {"rare_earths": rare_earths}
    
    # Strong international pressure
    usa = ThirdParty("USA", "United States", alignment_with_a=0.70,
                     intervention_threshold=0.25, coordination_bonus=0.50)
    eu = ThirdParty("EU", "European Union", alignment_with_a=0.55,
                    intervention_threshold=0.35, coordination_bonus=0.35)
    wto = ThirdParty("WTO", "WTO", alignment_with_a=0.40,
                     intervention_threshold=0.40, coordination_bonus=0.25)
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {"usa": usa, "eu": eu, "wto": wto}
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return japan, china, dep_matrix, third_party_system, actions


def create_2019_scenario():
    """2019 Japan-Korea: BILATERAL dispute."""
    
    # Japan 2019 - Abe, initiated controls
    japan = StateAgent(
        agent_id="JPN",
        name="Japan_2019",
        gdp=5.1,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.50,
        approval_rating=0.45,
        escalation_threshold=0.45,      # Willing to act
        de_escalation_threshold=0.35,
        retaliation_propensity=0.30,
    )
    japan.proactive_nationalism_coefficient = 0.40
    japan.coercion_hope_coefficient = 0.45
    japan.weakness_signal_coefficient = 0.35
    japan.action_cooldown = 3
    japan.restriction_intensity = {"semiconductor_materials": 0.50}
    
    # Korea 2019 - Moon, strong response
    korea = StateAgent(
        agent_id="KOR",
        name="Korea_2019",
        gdp=1.6,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.65,
        approval_rating=0.50,
        escalation_threshold=0.30,      # Quick to respond
        de_escalation_threshold=0.40,
        retaliation_propensity=0.65,    # KEY: Strong retaliation
    )
    korea.proactive_nationalism_coefficient = 0.45
    korea.coercion_hope_coefficient = 0.40
    korea.weakness_signal_coefficient = 0.50
    korea.action_cooldown = 2
    korea.restriction_intensity = {"semiconductor_materials": 0.20}
    
    # Multiple sectors including security
    semi = SectorDependency(
        sector_name="semiconductor_materials",
        a_exports_to_b=0.85, b_exports_to_a=0.05,
        a_substitution_time=6, b_substitution_time=24,
        a_substitution_cost=0.3, b_substitution_cost=2.5,
        a_criticality_score=0.20, b_criticality_score=0.90,
        a_political_salience=0.65, b_political_salience=0.85,
        a_restriction_self_harm=0.25, b_restriction_self_harm=0.60,
    )
    
    tourism = SectorDependency(
        sector_name="tourism",
        a_exports_to_b=0.35, b_exports_to_a=0.40,
        a_substitution_time=2, b_substitution_time=2,
        a_substitution_cost=0.2, b_substitution_cost=0.2,
        a_criticality_score=0.15, b_criticality_score=0.20,
        a_political_salience=0.40, b_political_salience=0.55,
        a_restriction_self_harm=0.30, b_restriction_self_harm=0.35,
    )
    
    consumer = SectorDependency(
        sector_name="consumer_goods",
        a_exports_to_b=0.45, b_exports_to_a=0.30,
        a_substitution_time=6, b_substitution_time=6,
        a_substitution_cost=0.5, b_substitution_cost=0.5,
        a_criticality_score=0.25, b_criticality_score=0.20,
        a_political_salience=0.50, b_political_salience=0.70,
        a_restriction_self_harm=0.35, b_restriction_self_harm=0.30,
    )
    
    security = SectorDependency(
        sector_name="security_cooperation",
        a_exports_to_b=0.50, b_exports_to_a=0.50,
        a_substitution_time=24, b_substitution_time=24,
        a_substitution_cost=3.0, b_substitution_cost=3.0,
        a_criticality_score=0.75, b_criticality_score=0.70,
        a_political_salience=0.80, b_political_salience=0.85,
        a_restriction_self_harm=0.80, b_restriction_self_harm=0.85,
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {
        "semiconductor_materials": semi,
        "tourism": tourism,
        "consumer_goods": consumer,
        "security_cooperation": security,
    }
    
    # US pressure (but more limited than 2010 - only on security)
    usa = ThirdParty("USA", "United States", alignment_with_a=0.45,
                     intervention_threshold=0.30, coordination_bonus=0.65)
    china = ThirdParty("CHN", "China", alignment_with_a=-0.20,
                       intervention_threshold=0.60, coordination_bonus=0.10)
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {"usa": usa, "china": china}
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return japan, korea, dep_matrix, third_party_system, actions


def run_case(name, create_fn, n_runs=300, max_steps=18):
    """Run a single case with universal parameters."""
    
    print(f"\n{'='*60}")
    print(f"CASE: {name}")
    print(f"{'='*60}")
    
    config = UNIVERSAL_CONFIG.copy()
    config["max_steps"] = max_steps
    
    results = []
    final_frictions = []
    peaks = []
    
    for i in range(n_runs):
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{n_runs}...")
        
        a, b, dep, tp, actions = create_fn()
        
        sim = UpgradedBilateralSimulator(
            state_a=a, state_b=b,
            dependency_matrix=dep,
            action_space=actions,
            third_party_system=tp,
            config=config,
            deescalation_config=UNIVERSAL_DEESC_CONFIG,
        )
        
        for _ in range(max_steps):
            sim.step()
        
        final_frictions.append(sim.get_friction_level())
        peaks.append(sim.peak_friction)
        results.append({
            'outcome': sim.classify_outcome(),
            'final': sim.get_friction_level(),
            'peak': sim.peak_friction,
            'deesc': sim.deescalation_events,
        })
    
    # Analyze
    avg_peak = sum(peaks) / n_runs
    avg_final = sum(final_frictions) / n_runs
    avg_deesc = sum(r['deesc'] for r in results) / n_runs
    
    outcome_counts = {}
    for r in results:
        cat = r['outcome'].value if hasattr(r['outcome'], 'value') else str(r['outcome'])
        outcome_counts[cat] = outcome_counts.get(cat, 0) + 1
    
    norm_rate = sum(1 for f in final_frictions if f < 0.10) / n_runs
    managed_rate = sum(1 for f in final_frictions if 0.15 <= f <= 0.45) / n_runs
    
    print(f"\nResults:")
    print(f"  Peak Friction:     {avg_peak:.3f}")
    print(f"  Final Friction:    {avg_final:.3f}")
    print(f"  De-escalations:    {avg_deesc:.1f}")
    print(f"  Normalization:     {norm_rate*100:.1f}%")
    print(f"  Managed Comp:      {managed_rate*100:.1f}%")
    print(f"\nOutcome Distribution:")
    for outcome, count in sorted(outcome_counts.items(), key=lambda x: -x[1]):
        pct = count / n_runs * 100
        bar = "█" * int(pct / 2.5)
        print(f"  {outcome:<25} {pct:5.1f}% {bar}")
    
    return {
        'avg_peak': avg_peak,
        'avg_final': avg_final,
        'norm_rate': norm_rate,
        'managed_rate': managed_rate,
        'outcomes': outcome_counts,
    }


def main():
    print("=" * 70)
    print("HONEST VALIDATION: SAME PARAMETERS FOR ALL CASES")
    print("=" * 70)
    print(f"\nUniversal de-escalation config:")
    for k, v in UNIVERSAL_DEESC_CONFIG.items():
        print(f"  {k}: {v}")
    
    # Run both cases
    results_2010 = run_case("2010 China-Japan (Single Actor)", 
                            create_2010_scenario, n_runs=300, max_steps=12)
    results_2019 = run_case("2019 Japan-Korea (Bilateral)", 
                            create_2019_scenario, n_runs=300, max_steps=18)
    
    # Compare
    print("\n" + "=" * 70)
    print("COMPARISON: Does model structure drive different outcomes?")
    print("=" * 70)
    
    print(f"\n{'Metric':<25} {'2010 (Single)':<15} {'2019 (Bilateral)':<15} {'Expected':<20}")
    print("-" * 75)
    print(f"{'Peak Friction':<25} {results_2010['avg_peak']:<15.3f} {results_2019['avg_peak']:<15.3f} {'2019 > 2010':<20}")
    print(f"{'Final Friction':<25} {results_2010['avg_final']:<15.3f} {results_2019['avg_final']:<15.3f} {'2019 > 2010':<20}")
    print(f"{'Normalization Rate':<25} {results_2010['norm_rate']*100:<14.1f}% {results_2019['norm_rate']*100:<14.1f}% {'2010 >> 2019':<20}")
    print(f"{'Managed Competition':<25} {results_2010['managed_rate']*100:<14.1f}% {results_2019['managed_rate']*100:<14.1f}% {'2019 > 2010':<20}")
    
    # Verdict
    print("\n" + "-" * 75)
    
    # Check if qualitative patterns hold
    checks = []
    
    # 2010 should normalize more
    if results_2010['norm_rate'] > results_2019['norm_rate']:
        checks.append("✓ 2010 normalizes more than 2019")
    else:
        checks.append("✗ 2010 should normalize more than 2019")
    
    # 2019 should have higher final friction
    if results_2019['avg_final'] > results_2010['avg_final']:
        checks.append("✓ 2019 has higher final friction")
    else:
        checks.append("✗ 2019 should have higher final friction")
    
    # 2019 should have more managed competition outcomes
    if results_2019['managed_rate'] > results_2010['managed_rate']:
        checks.append("✓ 2019 has more managed competition")
    else:
        checks.append("✗ 2019 should have more managed competition")
    
    # Both should have de-escalation (not spiral)
    spiral_2010 = results_2010['outcomes'].get('escalation_spiral', 0) / 300
    spiral_2019 = results_2019['outcomes'].get('escalation_spiral', 0) / 300
    if spiral_2010 < 0.10 and spiral_2019 < 0.10:
        checks.append("✓ Both avoid escalation spirals")
    else:
        checks.append(f"⚠ Spiral rates: 2010={spiral_2010:.1%}, 2019={spiral_2019:.1%}")
    
    print("\nVALIDATION CHECKS:")
    for c in checks:
        print(f"  {c}")
    
    passed = sum(1 for c in checks if c.startswith("✓"))
    print(f"\nPassed: {passed}/{len(checks)}")
    
    if passed == len(checks):
        print("\n✓ MODEL STRUCTURE DRIVES QUALITATIVELY CORRECT OUTCOMES")
        print("  (Even with same parameters, scenario setup creates different patterns)")
    elif passed >= len(checks) - 1:
        print("\n⚡ MODEL MOSTLY VALIDATED - minor issues")
    else:
        print("\n✗ MODEL NEEDS WORK - parameter tuning was doing heavy lifting")


if __name__ == "__main__":
    main()
