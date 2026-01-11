#!/usr/bin/env python3
"""
Check if de-escalation mechanisms are actually generating meaningful pressure.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selene_bilateral.upgraded_simulator import UpgradedBilateralSimulator
from selene_bilateral.state_agent import StateAgent, RegimeType
from selene_bilateral.sectors import SectorDependency, DependencyMatrix
from selene_bilateral.third_party import ThirdParty, ThirdPartySystem
from selene_bilateral.actions import ActionSpace, JAPAN_CHINA_ACTIONS


def create_scenario():
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
    japan.restriction_intensity = {"sector_a": 0.50}
    
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
    
    dep_matrix = DependencyMatrix()
    dep_matrix.sectors = {"sector_a": sector_a}
    
    usa = ThirdParty("USA", "United States", alignment_with_a=0.45,
                     intervention_threshold=0.30, coordination_bonus=0.55)
    third_party_system = ThirdPartySystem()
    third_party_system.parties = {"usa": usa}
    
    actions = ActionSpace()
    actions.load_from_config(JAPAN_CHINA_ACTIONS)
    
    return japan, korea, dep_matrix, third_party_system, actions


def run_diagnostic():
    """Run simulation and print component-level pressure values."""
    
    deesc_config = {
        "maintenance_cost": 0.04,
        "time_accel": 0.15,
        "grace_period": 4,
        "pressure_rate": 0.08,
        "friction_thresh": 0.35,
        "max_pressure": 0.50,
        "fatigue_rate": 0.05,
        "gdp_thresh": 2.0,
        "max_fatigue": 0.40,
        "bleed_rate": 0.012,
        "duration_sens": 0.10,
        "intensity_thresh": 0.40,
        "friction_memory_decay": 0.88,
    }
    
    config = {
        "max_steps": 18,
        "action_threshold": 0.03,
        "decision_noise": 0.02,  # Lower noise for cleaner view
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
    
    print("=" * 80)
    print("MECHANISM DIAGNOSTIC: What's actually happening inside?")
    print("=" * 80)
    
    print("\n{:>5} {:>8} {:>10} {:>10} {:>10} {:>10} {:>10} {:>10}".format(
        "Month", "Friction", "Time-Decay", "Intl-Pres", "Econ-Fat", "Memory", "TOTAL", "GDP_Loss"))
    print("-" * 90)
    
    for step in range(18):
        friction = sim.get_friction_level()
        
        # Manually compute each component for Japan (A)
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
        
        # Memory pressure (hardcoded additions)
        memory_pres = sim.cumulative_friction_a * 0.20 + sim.peak_friction * 0.15
        
        total = time_decay_total + intl_pres + econ_fat + memory_pres
        
        print("{:>5} {:>8.3f} {:>10.4f} {:>10.4f} {:>10.4f} {:>10.4f} {:>10.4f} {:>10.2f}".format(
            step, friction, time_decay_total, intl_pres, econ_fat, memory_pres, total,
            japan.cumulative_gdp_loss))
        
        # Step simulation
        sim.step()
    
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)


if __name__ == "__main__":
    run_diagnostic()
