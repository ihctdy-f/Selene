#!/usr/bin/env python3
"""
Current Japan-China Scenario (2026)
Run bilateral friction simulation for present-day tensions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selene_bilateral.bilateral_sim import BilateralFrictionSimulator, run_batch
from selene_bilateral.state_agent import StateAgent, RegimeType
from selene_bilateral.sectors import SectorDependency, DependencyMatrix
from selene_bilateral.third_party import ThirdParty, ThirdPartySystem
from selene_bilateral.actions import ActionSpace, JAPAN_CHINA_ACTIONS

import random


def create_2026_scenario():
    """
    Current Japan-China scenario (January 2026)
    
    Context:
    - Ongoing Taiwan tensions
    - Japan joined US semiconductor export controls (2023-ongoing)
    - China retaliated with critical minerals restrictions (Ga, Ge, graphite)
    - Both sides elevated nationalism
    - Japan increasing defense budget significantly
    - US-Japan alliance strengthened
    """
    
    # Japan (State A) - January 2026
    # Ishiba government (since Oct 2024), moderate but firm on China
    japan = StateAgent(
        agent_id="JPN",
        name="Japan_2026",
        gdp=4.2,  # Trillion USD (slight decline from 2010)
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.65,         # Elevated - defense buildup, Taiwan concerns
        approval_rating=0.35,           # Ishiba struggling domestically
        escalation_threshold=0.40,      # More willing to act than 2010
        de_escalation_threshold=0.25,   # Still prefers stability
        retaliation_propensity=0.45,    # Higher than 2010 - joined chip controls
    )
    japan.proactive_nationalism_coefficient = 0.15  # More proactive than 2010
    japan.coercion_hope_coefficient = 0.20          # Some belief in pressure working
    japan.weakness_signal_coefficient = 0.30        # Worried about credibility
    japan.action_cooldown = 3                       # Faster than 2010
    
    # Pre-existing restrictions: Japan's semiconductor equipment controls
    japan.restriction_intensity = {
        "semiconductors": 0.70,  # Strong export controls on chip equipment
    }
    
    # China (State B) - January 2026
    # Xi Jinping, consolidated power, nationalist posture
    china = StateAgent(
        agent_id="CHN",
        name="China_2026",
        gdp=17.8,  # Trillion USD
        regime_type=RegimeType.AUTOCRACY,
        nationalism_index=0.80,         # High - Taiwan, "century of humiliation" narrative
        approval_rating=0.65,           # Economic slowdown affecting support
        escalation_threshold=0.15,      # Quick to respond to perceived slights
        de_escalation_threshold=0.30,   # Higher than 2010 - more stubborn
        retaliation_propensity=0.85,    # Very high - "wolf warrior" era
    )
    china.proactive_nationalism_coefficient = 0.50  # Initiates pressure
    china.coercion_hope_coefficient = 0.55          # Believes in economic leverage
    china.weakness_signal_coefficient = 0.25        # Some concern about face
    china.action_cooldown = 1                       # Fast reactor
    
    # Pre-existing restrictions: China's critical minerals controls
    china.restriction_intensity = {
        "critical_minerals": 0.60,  # Ga, Ge, graphite export controls
        "rare_earths": 0.30,        # Ongoing informal pressure
    }
    
    # === SECTORS ===
    
    # Semiconductors - Japan restricts equipment to China
    semiconductors = SectorDependency(
        sector_name="semiconductors",
        a_exports_to_b=0.4,             # Japan exports significant chip equipment
        b_exports_to_a=0.2,             # China exports some chips to Japan
        a_substitution_time=24,         # China working on domestic alternatives
        b_substitution_time=18,         # Japan can source elsewhere
        a_substitution_cost=1.5,
        b_substitution_cost=1.2,
        a_criticality_score=0.70,       # Important but not existential for China
        b_criticality_score=0.50,       # Japan has alternatives
        a_political_salience=0.80,      # High visibility in China
        b_political_salience=0.60,
        a_restriction_self_harm=0.35,   # Japan loses China market
        b_restriction_self_harm=0.20,   # China loses some chips
    )
    
    # Critical Minerals - China restricts to Japan
    critical_minerals = SectorDependency(
        sector_name="critical_minerals",
        a_exports_to_b=0.05,            # Japan exports little
        b_exports_to_a=0.70,            # China dominates Ga, Ge, graphite
        a_substitution_time=36,         # Hard to replace
        b_substitution_time=12,
        a_substitution_cost=2.5,        # Very expensive alternatives
        b_substitution_cost=1.0,
        a_criticality_score=0.85,       # Critical for Japan's tech industry
        b_criticality_score=0.15,
        a_political_salience=0.70,
        b_political_salience=0.50,
        a_restriction_self_harm=0.05,
        b_restriction_self_harm=0.40,   # China loses export revenue
    )
    
    # Rare Earths - ongoing leverage
    rare_earths = SectorDependency(
        sector_name="rare_earths",
        a_exports_to_b=0.05,
        b_exports_to_a=0.60,            # Reduced from 2010 (Japan diversified)
        a_substitution_time=24,         # Faster than 2010 - lessons learned
        b_substitution_time=12,
        a_substitution_cost=1.8,
        b_substitution_cost=1.1,
        a_criticality_score=0.75,       # Still important
        b_criticality_score=0.20,
        a_political_salience=0.65,
        b_political_salience=0.55,
        a_restriction_self_harm=0.05,
        b_restriction_self_harm=0.50,
    )
    
    # Tourism - potential pressure point
    tourism = SectorDependency(
        sector_name="tourism",
        a_exports_to_b=0.3,             # Japanese tourists to China
        b_exports_to_a=0.5,             # Chinese tourists to Japan (big business)
        a_substitution_time=3,
        b_substitution_time=6,
        a_substitution_cost=0.3,
        b_substitution_cost=0.5,
        a_criticality_score=0.25,
        b_criticality_score=0.35,       # Japan tourism industry depends on Chinese
        a_political_salience=0.40,
        b_political_salience=0.50,
        a_restriction_self_harm=0.15,
        b_restriction_self_harm=0.25,
    )
    
    # Automotive - major trade flow
    automotive = SectorDependency(
        sector_name="automotive",
        a_exports_to_b=0.5,             # Japan exports cars/parts to China
        b_exports_to_a=0.3,             # China exports EV batteries, parts
        a_substitution_time=18,
        b_substitution_time=24,
        a_substitution_cost=1.3,
        b_substitution_cost=1.5,
        a_criticality_score=0.60,       # China is huge market for Japan
        b_criticality_score=0.55,       # Japan parts still important
        a_political_salience=0.70,
        b_political_salience=0.65,
        a_restriction_self_harm=0.40,   # Japan loses huge market
        b_restriction_self_harm=0.35,   # China loses quality imports
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {
        "semiconductors": semiconductors,
        "critical_minerals": critical_minerals,
        "rare_earths": rare_earths,
        "tourism": tourism,
        "automotive": automotive,
    }
    
    # === THIRD PARTIES ===
    
    usa = ThirdParty(
        party_id="USA",
        name="United States",
        alignment_with_a=0.85,          # Strong Japan alliance
        intervention_threshold=0.30,    # Quick to support Japan
        coordination_bonus=0.25,        # High coordination
        alternative_supply_capacity=0.15,  # Can provide some alternatives
    )
    
    eu = ThirdParty(
        party_id="EU",
        name="European Union",
        alignment_with_a=0.50,          # Balanced but leaning Japan
        intervention_threshold=0.50,
        coordination_bonus=0.10,
        alternative_supply_capacity=0.10,
    )
    
    south_korea = ThirdParty(
        party_id="KOR",
        name="South Korea",
        alignment_with_a=0.60,          # Improved relations with Japan
        intervention_threshold=0.45,
        coordination_bonus=0.15,
        alternative_supply_capacity=0.20,  # Significant chip capacity
    )
    
    taiwan = ThirdParty(
        party_id="TWN",
        name="Taiwan",
        alignment_with_a=0.90,          # Strong alignment
        intervention_threshold=0.20,    # Very sensitive to tensions
        coordination_bonus=0.20,
        alternative_supply_capacity=0.30,  # Major chip supplier
    )
    
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {
        "usa": usa,
        "eu": eu,
        "south_korea": south_korea,
        "taiwan": taiwan,
    }
    
    # === ACTIONS ===
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    # === SHOCK CONFIG ===
    shock_config = {
        "territorial_incident_prob": 0.05,   # Higher - Senkaku tensions
        "military_exercise_prob": 0.08,      # Frequent exercises
        "election_prob": 0.02,
        "leadership_change_prob": 0.01,
        "economic_recession_prob": 0.04,     # Both economies stressed
        "commodity_spike_prob": 0.06,
    }
    
    return japan, china, dep_matrix, third_party_system, actions, shock_config


def run_2026_simulation(n_runs=500, max_steps=48):
    """Run current scenario simulation"""
    
    print("=" * 70)
    print("JAPAN-CHINA 2026 SCENARIO - BILATERAL FRICTION SIMULATION")
    print("=" * 70)
    
    japan, china, dep_matrix, third_party_system, actions, shock_config = create_2026_scenario()
    
    print("\n--- Initial Conditions ---")
    print(f"Japan: nationalism={japan.nationalism_index}, approval={japan.approval_rating}")
    print(f"  Pre-existing restrictions: {japan.restriction_intensity}")
    print(f"China: nationalism={china.nationalism_index}, approval={china.approval_rating}")
    print(f"  Pre-existing restrictions: {china.restriction_intensity}")
    print(f"\nSectors: {list(dep_matrix.sectors.keys())}")
    print(f"Third parties: {list(third_party_system.parties.keys())}")
    
    # Calculate initial friction
    japan_friction = sum(japan.restriction_intensity.values()) / len(japan.restriction_intensity) if japan.restriction_intensity else 0
    china_friction = sum(china.restriction_intensity.values()) / len(china.restriction_intensity) if china.restriction_intensity else 0
    initial_friction = (japan_friction + china_friction) / 2
    print(f"\nInitial friction level: {initial_friction:.3f}")
    
    print(f"\nRunning {n_runs} simulations ({max_steps} months each)...")
    
    config = {
        "max_steps": max_steps,
        "shock_probabilities": shock_config,
        "pain_relief_coefficient": 0.4,
        "relationship_coefficient": 0.2,
        "audience_cost_base": 0.25,
        "reputation_coefficient": 0.15,
        "action_threshold": 0.03,
        "decision_noise": 0.04,
        "diversification_rate": 0.015,
    }
    
    results = []
    for i in range(n_runs):
        if (i + 1) % 100 == 0:
            print(f"  Completed {i+1}/{n_runs}...")
        
        # Fresh agents each run
        japan, china, dep_matrix, third_party_system, actions, shock_config = create_2026_scenario()
        
        sim = BilateralFrictionSimulator(
            state_a=japan,
            state_b=china,
            dependency_matrix=dep_matrix,
            action_space=actions,
            third_party_system=third_party_system,
            config=config,
        )
        
        result = sim.run()
        results.append(result)
    
    # === ANALYZE RESULTS ===
    print("\n" + "=" * 70)
    print("SIMULATION RESULTS")
    print("=" * 70)
    
    # Outcome distribution
    outcome_counts = {}
    for r in results:
        cat = r.outcome_category.value if hasattr(r.outcome_category, 'value') else str(r.outcome_category)
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
    
    # Key metrics
    avg_peak = sum(r.peak_friction_level for r in results) / n_runs
    avg_gdp_japan = sum(r.cumulative_gdp_loss_a for r in results) / n_runs
    avg_gdp_china = sum(r.cumulative_gdp_loss_b for r in results) / n_runs
    avg_div_japan = sum(r.final_diversification_a for r in results) / n_runs
    avg_div_china = sum(r.final_diversification_b for r in results) / n_runs
    avg_steps = sum(r.steps_to_terminal for r in results) / n_runs
    avg_escalation_cycles = sum(r.escalation_cycles for r in results) / n_runs
    
    print("\n--- Key Metrics ---")
    print(f"Average Peak Friction:    {avg_peak:.3f}")
    print(f"Average Escalation Cycles: {avg_escalation_cycles:.1f}")
    print(f"Average Steps to End:     {avg_steps:.1f} months")
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
                   outcome_counts.get('stable_interdependence', 0)) / n_runs
    
    print("\n--- Risk Assessment ---")
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
    
    print("\n" + "=" * 70)
    
    return results


def run_diagnostic_2026():
    """Run single diagnostic simulation with step-by-step output"""
    
    japan, china, dep_matrix, third_party_system, actions, shock_config = create_2026_scenario()
    
    config = {
        "max_steps": 24,
        "shock_probabilities": shock_config,
        "pain_relief_coefficient": 0.4,
        "relationship_coefficient": 0.2,
        "audience_cost_base": 0.25,
        "reputation_coefficient": 0.15,
        "action_threshold": 0.03,
        "decision_noise": 0.04,
    }
    
    sim = BilateralFrictionSimulator(
        state_a=japan,
        state_b=china,
        dependency_matrix=dep_matrix,
        action_space=actions,
        third_party_system=third_party_system,
        config=config,
    )
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC RUN - 2026 JAPAN-CHINA")
    print("=" * 70)
    print(f"\nInitial Japan restrictions: {japan.restriction_intensity}")
    print(f"Initial China restrictions: {china.restriction_intensity}")
    print()
    
    for step in range(24):
        friction = sim.get_friction_level()
        japan_restr = japan.get_total_friction_level()
        china_restr = china.get_total_friction_level()
        
        print(f"Month {step:2d}: friction={friction:.3f} | "
              f"JPN={japan_restr:.2f} loss={japan.cumulative_gdp_loss:5.1f} | "
              f"CHN={china_restr:.2f} loss={china.cumulative_gdp_loss:5.1f}")
        
        record = sim.step()
        
        if record.actions_taken:
            for action in record.actions_taken:
                actor = "Japan" if action['actor'] == 'A' else "China"
                print(f"       -> {actor} {action['type']}: {action['sector']} "
                      f"({action.get('from_intensity', 0):.2f} -> {action.get('to_intensity', 0):.2f})")
    
    final_friction = sim.get_friction_level()
    print(f"\n--- Final State ---")
    print(f"Final friction: {final_friction:.3f}")
    print(f"Peak friction:  {sim.peak_friction:.3f}")
    print(f"Japan restrictions: {dict(japan.restriction_intensity)}")
    print(f"China restrictions: {dict(china.restriction_intensity)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run 2026 Japan-China scenario")
    parser.add_argument("-n", "--runs", type=int, default=500, help="Number of runs")
    parser.add_argument("-d", "--diagnostic", action="store_true", help="Run single diagnostic")
    parser.add_argument("-s", "--steps", type=int, default=48, help="Max steps per run")
    
    args = parser.parse_args()
    
    if args.diagnostic:
        run_diagnostic_2026()
    else:
        run_2026_simulation(n_runs=args.runs, max_steps=args.steps)
