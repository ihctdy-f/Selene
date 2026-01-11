#!/usr/bin/env python3
"""
CLI runner for Selene Bilateral Friction Extension.

Usage:
    python run_bilateral.py                         # Default Japan-China, 100 runs
    python run_bilateral.py -c config/file.yaml -n 500
    python run_bilateral.py --compare               # Run all scenarios
    python run_bilateral.py --single --verbose      # Single detailed run
"""

import argparse
import sys
import os
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from selene_bilateral import (
    create_japan_china_simulator,
    run_batch,
    OutcomeCategory,
)
from selene_bilateral.state_agent import create_state_from_config
from selene_bilateral.sectors import DependencyMatrix
from selene_bilateral.actions import ActionSpace
from selene_bilateral.third_party import ThirdPartySystem


def load_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def merge_config(base: dict, override: dict) -> dict:
    """Merge config dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in result:
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value
    return result


def run_single(config: dict, verbose: bool = False):
    """Run a single simulation with detailed output."""
    sim = create_japan_china_simulator(config)
    
    print(f"\n{'='*60}")
    print(f"SINGLE RUN - {config.get('scenario_name', 'Custom')}")
    print(f"{'='*60}\n")
    
    print(f"State A: {sim.state_a.name}")
    print(f"  Nationalism: {sim.state_a.nationalism_index:.2f}")
    print(f"  Approval: {sim.state_a.approval_rating:.2f}")
    print(f"State B: {sim.state_b.name}")
    print(f"  Nationalism: {sim.state_b.nationalism_index:.2f}")
    print(f"  Approval: {sim.state_b.approval_rating:.2f}")
    print()
    
    while True:
        record = sim.step()
        
        if verbose:
            print(f"Step {record.step}: Friction={record.friction_level:.3f}")
            if record.actions_taken:
                for action in record.actions_taken:
                    print(f"  -> {action['actor']} {action['type']} {action['sector']} "
                          f"({action['from_intensity']:.2f} -> {action['to_intensity']:.2f})")
            if record.shocks:
                for shock in record.shocks:
                    print(f"  [SHOCK] {shock['shock_type']}: {shock['description']}")
        
        outcome = sim.check_terminal_condition()
        if outcome:
            break
    
    metrics = sim.run() if not outcome else None
    if metrics is None:
        # Calculate metrics manually since we already ran to completion
        from selene_bilateral.bilateral_sim import SimulationMetrics
        avg_div_a = sum(sim.state_a.diversification_progress.values()) / max(1, len(sim.state_a.diversification_progress)) if sim.state_a.diversification_progress else 0
        avg_div_b = sum(sim.state_b.diversification_progress.values()) / max(1, len(sim.state_b.diversification_progress)) if sim.state_b.diversification_progress else 0
        
        metrics = SimulationMetrics(
            outcome_category=outcome,
            steps_to_terminal=sim.current_step,
            cumulative_gdp_loss_a=sim.state_a.cumulative_gdp_loss,
            cumulative_gdp_loss_b=sim.state_b.cumulative_gdp_loss,
            peak_friction_level=sim.peak_friction,
            final_diversification_a=avg_div_a,
            final_diversification_b=avg_div_b,
            escalation_cycles=sim.escalation_cycles,
            third_party_interventions=sim.third_party_intervention_count,
            shock_count=sim.total_shocks,
        )
    
    print(f"\n{'='*60}")
    print("OUTCOME")
    print(f"{'='*60}")
    print(f"Category: {metrics.outcome_category.value}")
    print(f"Steps to terminal: {metrics.steps_to_terminal}")
    print(f"Peak friction: {metrics.peak_friction_level:.3f}")
    print(f"GDP Loss A ({sim.state_a.name}): {metrics.cumulative_gdp_loss_a:.4f}")
    print(f"GDP Loss B ({sim.state_b.name}): {metrics.cumulative_gdp_loss_b:.4f}")
    print(f"Diversification A: {metrics.final_diversification_a:.3f}")
    print(f"Diversification B: {metrics.final_diversification_b:.3f}")
    print(f"Escalation cycles: {metrics.escalation_cycles}")
    print(f"Third party interventions: {metrics.third_party_interventions}")
    print(f"Total shocks: {metrics.shock_count}")


def run_comparison():
    """Run comparison across all config files."""
    # Try multiple possible config locations
    possible_paths = [
        Path(__file__).parent / "selene_bilateral" / "config",
        Path(__file__).parent / "config",
        Path("selene_bilateral") / "config",
        Path("config"),
    ]
    
    config_dir = None
    for p in possible_paths:
        if p.exists():
            config_dir = p
            break
    
    config_files = list(config_dir.glob("*.yaml")) if config_dir else []
    
    if not config_files:
        print("No config files found. Running default scenarios...")
        scenarios = [
            ("baseline", {}),
            ("high_tension", {
                "jpn_nationalism": 0.7,
                "chn_nationalism": 0.75,
                "jpn_escalation_threshold": 0.25,
                "chn_escalation_threshold": 0.2,
            }),
            ("stabilization", {
                "jpn_nationalism": 0.35,
                "chn_nationalism": 0.45,
                "jpn_escalation_threshold": 0.45,
                "chn_escalation_threshold": 0.4,
            }),
        ]
    else:
        print(f"Found {len(config_files)} config files in {config_dir}")
        scenarios = []
        for f in config_files:
            config = load_config(str(f))
            # Flatten config for simulator
            flat_config = {}
            if "simulation" in config:
                flat_config.update(config["simulation"])
            if "decision" in config:
                flat_config.update(config["decision"])
            if "state_a" in config:
                for k, v in config["state_a"].items():
                    if k != "agent_id" and k != "name":
                        flat_config[f"jpn_{k}"] = v
            if "state_b" in config:
                for k, v in config["state_b"].items():
                    if k != "agent_id" and k != "name":
                        flat_config[f"chn_{k}"] = v
            if "shock_probabilities" in config:
                flat_config["shock_probabilities"] = config["shock_probabilities"]
            scenarios.append((f.stem, flat_config))
    
    print(f"\n{'='*70}")
    print("SCENARIO COMPARISON - 100 runs each")
    print(f"{'='*70}\n")
    
    all_results = {}
    
    for name, config in scenarios:
        print(f"Running: {name}...")
        results = run_batch(num_runs=100, config=config, verbose=True)
        all_results[name] = results
        print()
    
    # Summary table
    print(f"\n{'='*70}")
    print("OUTCOME DISTRIBUTION")
    print(f"{'='*70}")
    
    header = f"{'Scenario':<25}"
    for cat in OutcomeCategory:
        short_name = cat.value[:15]
        header += f"{short_name:>12}"
    print(header)
    print("-" * 70)
    
    for name, results in all_results.items():
        row = f"{name:<25}"
        for cat in OutcomeCategory:
            pct = results["outcome_distribution"].get(cat.value, 0) * 100
            row += f"{pct:>11.1f}%"
        print(row)
    
    print(f"\n{'='*70}")
    print("AVERAGES")
    print(f"{'='*70}")
    
    print(f"{'Scenario':<25}{'Peak Fric':>12}{'GDP Loss A':>12}{'GDP Loss B':>12}{'Div A':>10}{'Div B':>10}")
    print("-" * 70)
    
    for name, results in all_results.items():
        avgs = results["averages"]
        print(f"{name:<25}{avgs['peak_friction']:>12.3f}{avgs['gdp_loss_a']:>12.4f}"
              f"{avgs['gdp_loss_b']:>12.4f}{avgs['diversification_a']:>10.3f}"
              f"{avgs['diversification_b']:>10.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Selene Bilateral Friction Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_bilateral.py                    # Default Japan-China, 100 runs
  python run_bilateral.py -n 500             # 500 runs
  python run_bilateral.py --compare          # Compare all scenarios
  python run_bilateral.py --single -v        # Single detailed run
        """
    )
    
    parser.add_argument("-c", "--config", type=str, default=None,
                        help="Path to YAML config file")
    parser.add_argument("-n", "--num-runs", type=int, default=100,
                        help="Number of simulation runs (default: 100)")
    parser.add_argument("--compare", action="store_true",
                        help="Run comparison across all config files")
    parser.add_argument("--single", action="store_true",
                        help="Run single simulation")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output (for single runs)")
    
    args = parser.parse_args()
    
    # Load config
    config = {}
    if args.config:
        config = load_config(args.config)
        print(f"Loaded config: {args.config}")
    
    if args.compare:
        run_comparison()
    elif args.single:
        run_single(config, verbose=args.verbose)
    else:
        # Batch run
        print(f"\n{'='*60}")
        print(f"BATCH RUN - {args.num_runs} simulations")
        print(f"{'='*60}\n")
        
        results = run_batch(num_runs=args.num_runs, config=config, verbose=True)
        
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}\n")
        
        print("Outcome Distribution:")
        for outcome, pct in results["outcome_distribution"].items():
            count = results["outcome_counts"][outcome]
            print(f"  {outcome:<25}: {pct*100:>6.1f}% ({count})")
        
        print("\nAverages:")
        for key, value in results["averages"].items():
            print(f"  {key:<25}: {value}")


if __name__ == "__main__":
    main()
