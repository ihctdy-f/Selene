#!/usr/bin/env python3
"""
FIX MECHANISM THRESHOLDS
========================
Recalibrate so all 4 de-escalation mechanisms actually fire and contribute.

Current problem:
- Time-decay: grace_period=4, then tiny 0.001/month
- Intl-pressure: friction_thresh=0.35, goes to 0 when friction drops
- Econ-fatigue: gdp_thresh=2.0, never reached in 18 months
- Memory: no threshold, does 95% of work

Goal: Each mechanism should contribute 15-35% of total pressure.
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


def create_scenario():
    """Standard test scenario - bilateral with moderate stickiness."""
    japan = StateAgent(
        agent_id="JPN", name="Japan", gdp=5.1,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.60,        # Higher nationalism = stickier
        approval_rating=0.45,
        escalation_threshold=0.35,     # Lower = more willing to escalate
        de_escalation_threshold=0.45,  # Higher = harder to de-escalate
        retaliation_propensity=0.40,
    )
    japan.proactive_nationalism_coefficient = 0.50
    japan.coercion_hope_coefficient = 0.50
    japan.weakness_signal_coefficient = 0.45
    japan.action_cooldown = 3
    japan.restriction_intensity = {"sector_a": 0.50}
    
    korea = StateAgent(
        agent_id="KOR", name="Korea", gdp=1.6,
        regime_type=RegimeType.DEMOCRACY,
        nationalism_index=0.70,        # High nationalism
        approval_rating=0.50,
        escalation_threshold=0.25,     # Very willing to retaliate
        de_escalation_threshold=0.50,  # Hard to de-escalate
        retaliation_propensity=0.70,
    )
    korea.proactive_nationalism_coefficient = 0.55
    korea.coercion_hope_coefficient = 0.45
    korea.weakness_signal_coefficient = 0.55
    korea.action_cooldown = 2
    korea.restriction_intensity = {"sector_a": 0.30}
    
    sector_a = SectorDependency(
        sector_name="sector_a",
        a_exports_to_b=0.70, b_exports_to_a=0.15,
        a_substitution_time=6, b_substitution_time=18,
        a_substitution_cost=0.4, b_substitution_cost=2.0,
        a_criticality_score=0.30, b_criticality_score=0.80,
        a_political_salience=0.60, b_political_salience=0.75,
        a_restriction_self_harm=0.30, b_restriction_self_harm=0.50,
    )
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {"sector_a": sector_a}
    
    usa = ThirdParty("USA", "United States", alignment_with_a=0.45,
                     intervention_threshold=0.30, coordination_bonus=0.55)
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {"usa": usa}
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return japan, korea, dep_matrix, third_party_system, actions


def run_diagnostic(deesc_config: dict, label: str):
    """Run simulation and compute mechanism contributions."""
    
    config = {
        "max_steps": 18,
        "action_threshold": 0.03,
        "decision_noise": 0.02,
    }
    
    japan, korea, dep, tp, actions = create_scenario()
    
    sim = UpgradedBilateralSimulator(
        state_a=japan, state_b=korea,
        dependency_matrix=dep,
        action_space=actions,
        third_party_system=tp,
        config=config,
        deescalation_config=deesc_config,
    )
    
    print(f"\n{'='*80}")
    print(f"CONFIG: {label}")
    print(f"{'='*80}")
    
    # Track contributions over time
    contributions = {"time_decay": [], "intl_pres": [], "econ_fat": [], "memory": [], "total": []}
    
    print(f"\n{'Month':>5} {'Fric':>6} {'TimeDec':>8} {'IntlPr':>8} {'EconFat':>8} {'Memory':>8} {'TOTAL':>8} {'GDP%':>6}")
    print("-" * 75)
    
    for step in range(18):
        friction = sim.get_friction_level()
        state_id = "A"
        histories = sim.deesc_calc.restriction_histories.get(state_id, {})
        
        # Time decay
        time_decay_total = 0
        for sector, history in histories.items():
            if history.intensity >= 0.1:
                td = sim.deesc_calc.time_decay.calculate_maintenance_cost(
                    history, japan.restriction_intensity.get(sector, 0) * 0.3
                )
                time_decay_total += td
        
        # International pressure
        avg_dur = sum(h.duration for h in histories.values()) / max(1, len(histories)) if histories else 0
        tp_list = [{"intervention_threshold": 0.30, "coordination_bonus": 0.55}]
        intl_pres = sim.deesc_calc.intl_pressure.calculate_pressure(
            state_id=state_id,
            friction_level=friction,
            restriction_duration_avg=avg_dur,
            third_parties=tp_list,
            state_alignment=0.5
        )
        
        # Economic fatigue
        econ_fat = sim.deesc_calc.econ_fatigue.calculate_fatigue(
            cumulative_gdp_loss=japan.cumulative_gdp_loss,
            conflict_duration=step,
            regime_type="democracy",
            approval_rating=japan.approval_rating
        )
        
        # Memory pressure (now configurable)
        mem_coef = deesc_config.get("memory_coefficient", 0.20)
        peak_coef = deesc_config.get("peak_coefficient", 0.15)
        memory_pres = sim.cumulative_friction_a * mem_coef + sim.peak_friction * peak_coef
        
        total = time_decay_total + intl_pres + econ_fat + memory_pres
        
        contributions["time_decay"].append(time_decay_total)
        contributions["intl_pres"].append(intl_pres)
        contributions["econ_fat"].append(econ_fat)
        contributions["memory"].append(memory_pres)
        contributions["total"].append(total)
        
        print(f"{step:>5} {friction:>6.3f} {time_decay_total:>8.4f} {intl_pres:>8.4f} {econ_fat:>8.4f} {memory_pres:>8.4f} {total:>8.4f} {japan.cumulative_gdp_loss:>6.2f}")
        
        sim.step()
    
    # Compute average contributions during PEAK period (2-6) and LATE period (6-17)
    peak = slice(2, 7)   # Months 2-6 (high friction)
    late = slice(6, 18)  # Months 6-17 (after de-escalation)
    
    avg_td_peak = statistics.mean(contributions["time_decay"][peak]) if len(contributions["time_decay"]) > 6 else 0
    avg_ip_peak = statistics.mean(contributions["intl_pres"][peak]) if len(contributions["intl_pres"]) > 6 else 0
    avg_ef_peak = statistics.mean(contributions["econ_fat"][peak]) if len(contributions["econ_fat"]) > 6 else 0
    avg_mem_peak = statistics.mean(contributions["memory"][peak]) if len(contributions["memory"]) > 6 else 0
    avg_total_peak = statistics.mean(contributions["total"][peak]) if len(contributions["total"]) > 6 else 0
    
    print(f"\n--- Average Contribution During PEAK (Months 2-6) ---")
    if avg_total_peak > 0:
        print(f"Time-Decay:    {avg_td_peak:.4f}  ({100*avg_td_peak/avg_total_peak:>5.1f}%)")
        print(f"Intl-Pressure: {avg_ip_peak:.4f}  ({100*avg_ip_peak/avg_total_peak:>5.1f}%)")
        print(f"Econ-Fatigue:  {avg_ef_peak:.4f}  ({100*avg_ef_peak/avg_total_peak:>5.1f}%)")
        print(f"Memory:        {avg_mem_peak:.4f}  ({100*avg_mem_peak/avg_total_peak:>5.1f}%)")
        print(f"TOTAL:         {avg_total_peak:.4f}")
    
    avg_td = statistics.mean(contributions["time_decay"][late])
    avg_ip = statistics.mean(contributions["intl_pres"][late])
    avg_ef = statistics.mean(contributions["econ_fat"][late])
    avg_mem = statistics.mean(contributions["memory"][late])
    avg_total = statistics.mean(contributions["total"][late])
    
    print(f"\n--- Average Contribution POST-PEAK (Months 6-17) ---")
    if avg_total > 0:
        print(f"Time-Decay:    {avg_td:.4f}  ({100*avg_td/avg_total:>5.1f}%)")
        print(f"Intl-Pressure: {avg_ip:.4f}  ({100*avg_ip/avg_total:>5.1f}%)")
        print(f"Econ-Fatigue:  {avg_ef:.4f}  ({100*avg_ef/avg_total:>5.1f}%)")
        print(f"Memory:        {avg_mem:.4f}  ({100*avg_mem/avg_total:>5.1f}%)")
        print(f"TOTAL:         {avg_total:.4f}")
    
    return contributions


def main():
    # ORIGINAL CONFIG (broken)
    original = {
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
    
    # FIXED CONFIG
    fixed = {
        # Time-decay: Start immediately, strong effect
        "maintenance_cost": 0.35,      # Strong when active
        "time_accel": 0.30,            # Faster accumulation
        "grace_period": 1,             # Starts after 1 month
        
        # International pressure: Lower threshold, moderate
        "pressure_rate": 0.15,         # Moderate
        "duration_sens": 0.15,         
        "friction_thresh": 0.15,       # Stays active at lower friction
        "max_pressure": 0.50,          
        
        # Economic fatigue: Lower threshold
        "fatigue_rate": 0.05,          
        "gdp_thresh": 0.3,             # Triggers after ~3 months
        "max_fatigue": 0.40,           
        
        # Reputation bleed
        "bleed_rate": 0.020,           
        "intensity_thresh": 0.25,      
        
        # Memory: Reduced since other mechanisms now work
        "friction_memory_decay": 0.85, 
        "memory_coefficient": 0.12,    
        "peak_coefficient": 0.10,      
    }
    
    print("=" * 80)
    print("MECHANISM THRESHOLD FIX")
    print("=" * 80)
    print("\nGoal: Each of 4 mechanisms should contribute 15-35% of pressure")
    
    # Run original
    run_diagnostic(original, "ORIGINAL (broken)")
    
    # Run fixed
    run_diagnostic(fixed, "FIXED THRESHOLDS")
    
    print("\n" + "=" * 80)
    print("FIXED CONFIG FOR USE IN MODEL:")
    print("=" * 80)
    print("\nDEESCALATION_CONFIG_V2 = {")
    for k, v in fixed.items():
        print(f'    "{k}": {v},')
    print("}")


if __name__ == "__main__":
    main()
