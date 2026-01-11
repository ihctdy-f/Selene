#!/usr/bin/env python3
"""
Calibrate Bilateral Friction Model to 2019 Japan-Korea Trade Dispute
=====================================================================

This is an excellent calibration case because:
1. BILATERAL restrictions (both sides acted)
2. Historical grievances (wartime labor)
3. Semiconductor supply chain (critical materials)
4. Strong third party intervention (US pressure)
5. PARTIAL de-escalation (not full normalization)

Historical Timeline:
- July 1, 2019: Japan announces export controls (HF, photoresists, fluorinated polyimide)
- July 4: Controls take effect
- Aug 2: Japan removes Korea from whitelist
- Aug 12: Korea announces counter-whitelist removal
- Aug 22: Korea threatens GSOMIA withdrawal
- Sept: Both file WTO complaints
- Nov 22, 2019: Korea suspends GSOMIA termination (US pressure)
- 2020: Gradual easing but no normalization
- March 2023: Korea drops WTO case, partial rapprochement

Target Pattern:
- Peak friction: ~0.55-0.70 (bilateral but not total breakdown)
- Peak timing: Month 2-4 (Aug-Oct 2019)
- Partial de-escalation: friction drops but doesn't normalize
- Final state: 0.20-0.40 (managed competition, not normalization)
- Both sides diversify supply chains
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
import statistics


def create_2019_japan_korea_scenario():
    """
    Create 2019 Japan-Korea trade dispute scenario.
    
    Key characteristics:
    - Japan initiated over historical grievance (court ruling)
    - Korea retaliated strongly (nationalism + elections)
    - US intervened to prevent security spillover (GSOMIA)
    - Both democracies with high nationalism
    - Asymmetric dependencies (Korea more dependent on Japan for materials)
    """
    
    # Japan 2019 - Abe government, historically assertive but measured
    japan = StateAgent(
        agent_id="JPN",
        name="Japan_2019",
        gdp=5.1,  # Trillion USD
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.50,         # Moderate (not as high as China on issues)
        approval_rating=0.45,           # Stable Abe government
        escalation_threshold=0.45,      # Somewhat cautious
        de_escalation_threshold=0.35,   # Willing to back down under pressure
        retaliation_propensity=0.30,    # Measured response style
    )
    japan.proactive_nationalism_coefficient = 0.40  # Initiated but measured
    japan.coercion_hope_coefficient = 0.45          # Some hope
    japan.weakness_signal_coefficient = 0.35        # Moderate face concerns
    japan.action_cooldown = 3                       # Slow to act
    
    # Japan's initial restriction (the trigger)
    # Started with specific material controls, will escalate
    japan.restriction_intensity = {
        "semiconductor_materials": 0.50,  # HF, photoresists, fluorinated polyimide
    }
    
    # Korea 2019 - Moon government, strong anti-Japan sentiment but US pressure
    korea = StateAgent(
        agent_id="KOR",
        name="Korea_2019",
        gdp=1.6,  # Trillion USD
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.65,         # High on Japan issues
        approval_rating=0.50,           # Moon government
        escalation_threshold=0.30,      # Quick to respond to Japan
        de_escalation_threshold=0.40,   # But also responsive to US pressure
        retaliation_propensity=0.65,    # Strong retaliation tendency
    )
    korea.proactive_nationalism_coefficient = 0.45  # Domestic pressure but constrained
    korea.coercion_hope_coefficient = 0.40          # Realistic about limits
    korea.weakness_signal_coefficient = 0.50        # Concerned about face
    korea.action_cooldown = 2                       # Quick but not instant
    
    # Korea's initial counter-restrictions (whitelist threat)
    korea.restriction_intensity = {
        "semiconductor_materials": 0.20,  # Counter-whitelist threat
    }
    
    # === SECTORS ===
    
    # Semiconductor Materials - Core of dispute
    # Japan had ~90% of global fluorinated polyimide, ~70% hydrogen fluoride
    semiconductor_materials = SectorDependency(
        sector_name="semiconductor_materials",
        a_exports_to_b=0.85,            # Japan dominant exporter to Korea
        b_exports_to_a=0.05,            # Korea exports little to Japan
        a_substitution_time=6,          # Japan can find other buyers
        b_substitution_time=24,         # Korea struggled to diversify (Samsung etc.)
        a_substitution_cost=0.3,        # Low cost for Japan
        b_substitution_cost=2.5,        # High cost for Korea
        a_criticality_score=0.20,       # Not critical for Japan
        b_criticality_score=0.90,       # VERY critical for Korea's chip industry
        a_political_salience=0.65,      # Historical grievance issue
        b_political_salience=0.85,      # National pride + economic
        a_restriction_self_harm=0.25,   # Japan loses some revenue
        b_restriction_self_harm=0.60,   # Korea hurts itself more
    )
    
    # Tourism - Significant bilateral flow
    tourism = SectorDependency(
        sector_name="tourism",
        a_exports_to_b=0.35,            # Japanese tourists to Korea
        b_exports_to_a=0.40,            # Korean tourists to Japan (boycott!)
        a_substitution_time=2, b_substitution_time=2,
        a_substitution_cost=0.2, b_substitution_cost=0.2,
        a_criticality_score=0.15, b_criticality_score=0.20,
        a_political_salience=0.40, b_political_salience=0.55,
        a_restriction_self_harm=0.30, b_restriction_self_harm=0.35,
    )
    
    # Consumer goods - Korean boycott of Japanese products
    consumer_goods = SectorDependency(
        sector_name="consumer_goods",
        a_exports_to_b=0.45,            # Japanese goods to Korea
        b_exports_to_a=0.30,            # Korean goods to Japan
        a_substitution_time=6, b_substitution_time=6,
        a_substitution_cost=0.5, b_substitution_cost=0.5,
        a_criticality_score=0.25, b_criticality_score=0.20,
        a_political_salience=0.50, b_political_salience=0.70,  # "No Japan" movement
        a_restriction_self_harm=0.35, b_restriction_self_harm=0.30,
    )
    
    # Security cooperation (GSOMIA) - US PREVENTED escalation
    # This sector should be very resistant to escalation
    security_cooperation = SectorDependency(
        sector_name="security_cooperation",
        a_exports_to_b=0.50,            # Japan intel sharing
        b_exports_to_a=0.50,            # Korea intel sharing
        a_substitution_time=24, b_substitution_time=24,  # Very hard to replace
        a_substitution_cost=3.0, b_substitution_cost=3.0,  # Very costly
        a_criticality_score=0.75,       # Very important for Japan
        b_criticality_score=0.70,       # Very important for Korea
        a_political_salience=0.80, b_political_salience=0.85,  # High visibility
        a_restriction_self_harm=0.80, b_restriction_self_harm=0.85,  # HIGH self-harm (US anger)
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {
        "semiconductor_materials": semiconductor_materials,
        "tourism": tourism,
        "consumer_goods": consumer_goods,
        "security_cooperation": security_cooperation,
    }
    
    # === THIRD PARTIES ===
    
    # USA - KEY ACTOR - VERY strong pressure to prevent GSOMIA collapse
    usa = ThirdParty(
        party_id="USA",
        name="United States",
        alignment_with_a=0.45,          # Allied with both, slight tilt to Japan
        intervention_threshold=0.30,    # Quick to intervene on security issues
        coordination_bonus=0.65,        # VERY STRONG pressure (Pompeo, DoD etc.)
        alternative_supply_capacity=0.10,
    )
    
    # China - benefits from Japan-Korea friction
    china = ThirdParty(
        party_id="CHN",
        name="China",
        alignment_with_a=-0.20,         # Slight tilt toward Korea
        intervention_threshold=0.60,    # Less likely to intervene
        coordination_bonus=0.10,
        alternative_supply_capacity=0.15,  # Some material alternatives
    )
    
    # EU/WTO - Rules-based pressure
    wto = ThirdParty(
        party_id="WTO",
        name="WTO/International",
        alignment_with_a=0.0,           # Neutral
        intervention_threshold=0.45,
        coordination_bonus=0.20,
        alternative_supply_capacity=0.05,
    )
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {
        "usa": usa,
        "china": china,
        "wto": wto,
    }
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)  # Reuse Japan-China actions
    
    return japan, korea, dep_matrix, third_party_system, actions


def run_2019_calibration(n_runs=500, max_steps=18):
    """
    Calibrate to 2019 Japan-Korea case (18 months = July 2019 to Dec 2020).
    
    Targets:
    - Peak friction: 0.55-0.70
    - Peak timing: Month 2-4 (Aug-Oct 2019)
    - Final friction: 0.20-0.40 (managed competition, NOT normalization)
    - Normalization rate: < 20% (most should be managed competition)
    - Diversification: Korea diversifies significantly
    """
    
    print("=" * 70)
    print("CALIBRATING MODEL TO 2019 JAPAN-KOREA TRADE DISPUTE")
    print("=" * 70)
    
    # De-escalation parameters for Japan-Korea
    # KEY INSIGHT: US pressure stopped escalation but historical grievances
    # prevented full normalization - reached "managed competition" not peace
    deesc_config = {
        "maintenance_cost": 0.04,       # Moderate
        "time_accel": 0.14,             # Moderate acceleration
        "grace_period": 4,              # Medium grace
        "pressure_rate": 0.08,          # Strong US pressure (GSOMIA)
        "duration_sens": 0.10,
        "friction_thresh": 0.35,
        "max_pressure": 0.45,           # Strong but limited (US only on security)
        "fatigue_rate": 0.04,           # Moderate - historical grievances persist
        "gdp_thresh": 2.5,              # Higher threshold
        "max_fatigue": 0.35,            # Limited fatigue (nationalism sustains conflict)
        "bleed_rate": 0.010,            # Lower reputation cost (both seen as justified)
        "intensity_thresh": 0.40,
        "friction_memory_decay": 0.92,  # Strong historical memory - prevents normalization
    }
    
    config = {
        "max_steps": max_steps,
        "pain_relief_coefficient": 0.45,
        "relationship_coefficient": 0.25,
        "audience_cost_base": 0.30,     # High for democracies
        "action_threshold": 0.03,
        "decision_noise": 0.04,
        "diversification_rate": 0.025,  # Korea actively diversified
    }
    
    print(f"\nRunning {n_runs} simulations ({max_steps} months each)...")
    
    results = []
    friction_trajectories = []
    final_frictions = []
    diversification_results = []
    
    for i in range(n_runs):
        if (i + 1) % 100 == 0:
            print(f"  Completed {i+1}/{n_runs}...")
        
        japan, korea, dep_matrix, third_party_system, actions = create_2019_japan_korea_scenario()
        
        sim = UpgradedBilateralSimulator(
            state_a=japan,
            state_b=korea,
            dependency_matrix=dep_matrix,
            action_space=actions,
            third_party_system=third_party_system,
            config=config,
            deescalation_config=deesc_config,
        )
        
        # Track trajectory
        trajectory = []
        for step in range(max_steps):
            friction = sim.get_friction_level()
            trajectory.append(friction)
            sim.step()
        
        final_friction = sim.get_friction_level()
        trajectory.append(final_friction)
        friction_trajectories.append(trajectory)
        final_frictions.append(final_friction)
        
        diversification_results.append({
            'japan': japan.get_avg_diversification(),
            'korea': korea.get_avg_diversification(),
        })
        
        results.append({
            'outcome': sim.classify_outcome(),
            'peak': sim.peak_friction,
            'final': final_friction,
            'deesc_events': sim.deescalation_events,
            'japan_div': japan.get_avg_diversification(),
            'korea_div': korea.get_avg_diversification(),
        })
    
    # === ANALYZE RESULTS ===
    print("\n" + "=" * 70)
    print("CALIBRATION RESULTS")
    print("=" * 70)
    
    # Outcome distribution
    outcome_counts = {}
    for r in results:
        cat = r['outcome'].value if hasattr(r['outcome'], 'value') else str(r['outcome'])
        outcome_counts[cat] = outcome_counts.get(cat, 0) + 1
    
    print("\n--- Outcome Distribution ---")
    for outcome in ['normalization', 'stable_interdependence', 'managed_competition',
                    'escalation_spiral', 'gradual_decoupling', 'asymmetric_lock_in']:
        count = outcome_counts.get(outcome, 0)
        pct = count / n_runs * 100
        bar = "█" * int(pct / 2.5)
        print(f"{outcome:<25} {count:>5} ({pct:>5.1f}%) {bar}")
    
    # Key metrics
    avg_peak = sum(r['peak'] for r in results) / n_runs
    avg_final = sum(final_frictions) / n_runs
    avg_deesc = sum(r['deesc_events'] for r in results) / n_runs
    avg_japan_div = sum(r['japan_div'] for r in results) / n_runs
    avg_korea_div = sum(r['korea_div'] for r in results) / n_runs
    
    # Managed competition rate (final friction 0.20-0.45)
    managed_count = sum(1 for f in final_frictions if 0.15 <= f <= 0.45)
    managed_rate = managed_count / n_runs
    
    # Normalization rate (final friction < 0.15)
    norm_count = sum(1 for f in final_frictions if f < 0.15)
    norm_rate = norm_count / n_runs
    
    # Peak timing
    avg_trajectory = [sum(t[i] for t in friction_trajectories) / n_runs 
                      for i in range(max_steps + 1)]
    peak_month = avg_trajectory.index(max(avg_trajectory))
    
    print("\n--- Key Metrics ---")
    print(f"Average Peak Friction:     {avg_peak:.3f}")
    print(f"Peak Timing:               Month {peak_month}")
    print(f"Average Final Friction:    {avg_final:.3f}")
    print(f"Managed Competition Rate:  {managed_rate*100:.1f}%")
    print(f"Normalization Rate:        {norm_rate*100:.1f}%")
    print(f"Avg De-escalation Events:  {avg_deesc:.1f}")
    print(f"Japan Diversification:     {avg_japan_div:.2f}")
    print(f"Korea Diversification:     {avg_korea_div:.2f}")
    
    # === CALIBRATION SCORING ===
    print("\n--- Calibration Targets vs Results ---")
    print(f"{'Target':<30} {'Actual':>10} {'Target':>15} {'Score':>10}")
    print("-" * 70)
    
    scores = []
    
    # Peak friction target: 0.55-0.70
    if 0.55 <= avg_peak <= 0.70:
        peak_score = 1.0
    elif 0.45 <= avg_peak <= 0.80:
        peak_score = 0.7
    else:
        peak_score = max(0, 1 - abs(avg_peak - 0.62) / 0.25)
    scores.append(peak_score)
    print(f"{'Peak Friction':<30} {avg_peak:>10.3f} {'0.55-0.70':>15} {peak_score:>10.2f}")
    
    # Peak timing target: Month 2-4
    if 2 <= peak_month <= 4:
        timing_score = 1.0
    elif 1 <= peak_month <= 6:
        timing_score = 0.7
    else:
        timing_score = 0.4
    scores.append(timing_score)
    print(f"{'Peak Timing (month)':<30} {peak_month:>10} {'2-4':>15} {timing_score:>10.2f}")
    
    # Final friction target: 0.20-0.40 (managed competition)
    if 0.20 <= avg_final <= 0.40:
        final_score = 1.0
    elif 0.15 <= avg_final <= 0.50:
        final_score = 0.7
    else:
        final_score = max(0, 1 - abs(avg_final - 0.30) / 0.25)
    scores.append(final_score)
    print(f"{'Final Friction':<30} {avg_final:>10.3f} {'0.20-0.40':>15} {final_score:>10.2f}")
    
    # Managed competition rate target: > 40%
    if managed_rate > 0.45:
        mgmt_score = 1.0
    elif managed_rate > 0.30:
        mgmt_score = 0.7
    else:
        mgmt_score = managed_rate / 0.45
    scores.append(mgmt_score)
    print(f"{'Managed Competition Rate':<30} {managed_rate*100:>9.1f}% {'> 40%':>15} {mgmt_score:>10.2f}")
    
    # Normalization rate target: < 25% (shouldn't fully normalize)
    if norm_rate < 0.20:
        norm_score = 1.0
    elif norm_rate < 0.35:
        norm_score = 0.7
    else:
        norm_score = max(0, 1 - (norm_rate - 0.20) / 0.30)
    scores.append(norm_score)
    print(f"{'Normalization Rate':<30} {norm_rate*100:>9.1f}% {'< 25%':>15} {norm_score:>10.2f}")
    
    # Korea diversification target: > 0.35 (Samsung etc. diversified)
    if avg_korea_div > 0.40:
        korea_div_score = 1.0
    elif avg_korea_div > 0.25:
        korea_div_score = 0.7
    else:
        korea_div_score = avg_korea_div / 0.40
    scores.append(korea_div_score)
    print(f"{'Korea Diversification':<30} {avg_korea_div:>10.2f} {'> 0.35':>15} {korea_div_score:>10.2f}")
    
    # Overall score
    overall_score = sum(scores) / len(scores)
    print("-" * 70)
    print(f"{'OVERALL CALIBRATION SCORE':<30} {overall_score:>10.2f}")
    
    if overall_score >= 0.75:
        print("✓ CALIBRATION PASSED")
    elif overall_score >= 0.60:
        print("⚡ CALIBRATION MARGINAL - needs tuning")
    else:
        print("✗ CALIBRATION FAILED - significant gap")
    
    # Show average trajectory
    print("\n--- Average Friction Trajectory ---")
    months = list(range(max_steps + 1))
    print("Month: " + " ".join(f"{m:>5}" for m in months[:13]))
    print("Fric:  " + " ".join(f"{f:>5.2f}" for f in avg_trajectory[:13]))
    if len(avg_trajectory) > 13:
        print("Month: " + " ".join(f"{m:>5}" for m in months[13:]))
        print("Fric:  " + " ".join(f"{f:>5.2f}" for f in avg_trajectory[13:]))
    
    # Historical comparison
    print("\n--- Historical Comparison ---")
    print("July 2019 (M0):  Japan announces controls")
    print("Aug 2019 (M1-2): Bilateral escalation, whitelist removals")
    print("Sept 2019 (M2-3): WTO complaints, peak tension")
    print("Nov 2019 (M4-5): GSOMIA crisis, US pressure, partial backing")
    print("2020 (M6-18):    Gradual easing but no normalization")
    print("March 2023:      Korea drops WTO case (outside simulation period)")
    
    print("\n" + "=" * 70)
    
    return results, avg_trajectory, overall_score


def run_diagnostic_2019():
    """Run single diagnostic simulation for 2019 case."""
    
    japan, korea, dep_matrix, third_party_system, actions = create_2019_japan_korea_scenario()
    
    deesc_config = {
        "maintenance_cost": 0.04,
        "time_accel": 0.14,
        "grace_period": 4,
        "pressure_rate": 0.08,
        "duration_sens": 0.10,
        "friction_thresh": 0.35,
        "max_pressure": 0.45,
        "fatigue_rate": 0.04,
        "gdp_thresh": 2.5,
        "max_fatigue": 0.35,
        "bleed_rate": 0.010,
        "intensity_thresh": 0.40,
        "friction_memory_decay": 0.92,
    }
    
    config = {
        "max_steps": 18,
        "audience_cost_base": 0.30,
        "action_threshold": 0.03,
        "decision_noise": 0.04,
        "diversification_rate": 0.025,
    }
    
    sim = UpgradedBilateralSimulator(
        state_a=japan,
        state_b=korea,
        dependency_matrix=dep_matrix,
        action_space=actions,
        third_party_system=third_party_system,
        config=config,
        deescalation_config=deesc_config,
    )
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC - 2019 JAPAN-KOREA TRADE DISPUTE")
    print("=" * 70)
    print(f"\nInitial Japan restrictions: {japan.restriction_intensity}")
    print(f"Initial Korea restrictions: {korea.restriction_intensity}")
    print()
    
    for step in range(18):
        record = sim.step()
        
        # Month labels
        month_labels = ['Jul19', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                        'Jan20', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul20', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec20']
        
        print(f"{month_labels[step]:>6}: friction={record.friction_level:.3f} | "
              f"JPN deesc_p={record.deescalation_pressure_a:.3f} | "
              f"KOR deesc_p={record.deescalation_pressure_b:.3f}")
        
        for action in record.actions_taken:
            actor = "Japan" if action['actor'] == 'A' else "Korea"
            symbol = "↓" if action['type'] == 'de_escalate' else "↑"
            print(f"       {symbol} {actor} {action['type']}: {action['sector']} "
                  f"({action.get('from_intensity', 0):.2f} -> {action.get('to_intensity', 0):.2f})")
    
    final_friction = sim.get_friction_level()
    print(f"\n--- Final State ---")
    print(f"Final friction: {final_friction:.3f}")
    print(f"Peak friction:  {sim.peak_friction:.3f}")
    print(f"De-escalation events: {sim.deescalation_events}")
    print(f"Japan restrictions: {dict(japan.restriction_intensity)}")
    print(f"Korea restrictions: {dict(korea.restriction_intensity)}")
    print(f"Japan diversification: {japan.get_avg_diversification():.2f}")
    print(f"Korea diversification: {korea.get_avg_diversification():.2f}")
    print(f"Outcome: {sim.classify_outcome()}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--runs", type=int, default=500)
    parser.add_argument("-d", "--diagnostic", action="store_true")
    
    args = parser.parse_args()
    
    if args.diagnostic:
        run_diagnostic_2019()
    else:
        run_2019_calibration(n_runs=args.runs)
