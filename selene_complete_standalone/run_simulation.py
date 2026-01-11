#!/usr/bin/env python3
"""
Project Selene Consortium Simulator v2.0
========================================

Main entry point for running simulations.

Usage:
    python run_simulation.py                           # Default scenario, 100 runs
    python run_simulation.py -c config/low_trust.yaml  # Custom config
    python run_simulation.py -n 1000                   # 1000 runs
    python run_simulation.py -c config/high_trust.yaml -n 500 -o results/
    python run_simulation.py --compare                 # Run all scenarios and compare
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import yaml

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from selene_sim import ConsortiumSimulator, summarize_results


def load_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_scenario(config_path: str, n_runs: int, seed: int = None, verbose: bool = True) -> dict:
    """Run a single scenario and return summary."""
    config = load_config(config_path)
    scenario_name = config.get("scenario_name", Path(config_path).stem)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running: {scenario_name}")
        print(f"Config: {config_path}")
        print(f"Runs: {n_runs}")
        print(f"{'='*60}")
    
    sim = ConsortiumSimulator(config, seed=seed)
    results = sim.run_batch(n_runs=n_runs, verbose=verbose)
    summary = summarize_results(results)
    summary["scenario_name"] = scenario_name
    summary["config_path"] = config_path
    
    if verbose:
        print_summary(summary)
    
    return summary, results


def print_summary(summary: dict):
    """Pretty print simulation summary."""
    print(f"\n{'-'*60}")
    print(f"RESULTS: {summary.get('scenario_name', 'Unknown')}")
    print(f"{'-'*60}")
    
    print("\nOutcome Distribution:")
    for outcome, pct in summary.get("outcome_percentages", {}).items():
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"  {outcome:25s} {bar} {pct:5.1f}%")
    
    print(f"\nKey Metrics:")
    print(f"  Avg Final Agents:     {summary.get('avg_final_agents', 0):.2f} / 5")
    print(f"  Avg Functionality:    {summary.get('avg_functionality', 0):.1%}")
    print(f"  Avg Early Defections: {summary.get('avg_early_defections', 0):.2f}")
    print(f"  Avg Late Defections:  {summary.get('avg_late_defections', 0):.2f}")
    print(f"  Avg Investment:       €{summary.get('avg_investment', 0):.1f}B")
    
    print(f"\nSuccess Rates:")
    print(f"  Structural Success:   {summary.get('structural_success_rate', 0):.1f}%")
    print(f"  Positive Outcomes:    {summary.get('positive_outcome_rate', 0):.1f}%")


def run_comparison(config_dir: str, n_runs: int, output_dir: str = None):
    """Run all configs in directory and compare."""
    config_dir = Path(config_dir)
    configs = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))
    
    if not configs:
        print(f"No config files found in {config_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"COMPARISON RUN: {len(configs)} scenarios, {n_runs} runs each")
    print(f"{'='*60}")
    
    all_summaries = []
    
    for config_path in sorted(configs):
        summary, _ = run_scenario(str(config_path), n_runs, verbose=True)
        all_summaries.append(summary)
    
    # Print comparison table
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"\n{'Scenario':<30} {'Success%':>10} {'Partial%':>10} {'Fail%':>10}")
    print("-" * 60)
    
    for s in all_summaries:
        name = s.get("scenario_name", "Unknown")[:28]
        outcomes = s.get("outcome_percentages", {})
        success = outcomes.get("structural_success", 0)
        partial = outcomes.get("partial_success", 0)
        fail = outcomes.get("catastrophic_failure", 0)
        print(f"{name:<30} {success:>10.1f} {partial:>10.1f} {fail:>10.1f}")
    
    # Save combined results
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"comparison_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(all_summaries, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Project Selene Consortium Simulator v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_simulation.py
  python run_simulation.py -c config/low_trust_weak_pill.yaml -n 500
  python run_simulation.py --compare -n 100
        """
    )
    
    parser.add_argument(
        "-c", "--config",
        default="config/selene_default.yaml",
        help="Path to scenario config file (default: config/selene_default.yaml)"
    )
    
    parser.add_argument(
        "-n", "--runs",
        type=int,
        default=100,
        help="Number of simulation runs (default: 100)"
    )
    
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run all configs in config/ directory and compare"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    if args.compare:
        run_comparison("config", args.runs, args.output)
    else:
        summary, results = run_scenario(
            args.config, 
            args.runs, 
            seed=args.seed,
            verbose=not args.quiet
        )
        
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scenario_name = summary.get("scenario_name", "unknown").replace(" ", "_").lower()
            
            # Save summary
            summary_file = output_dir / f"{scenario_name}_{timestamp}_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Save detailed results
            results_file = output_dir / f"{scenario_name}_{timestamp}_results.json"
            with open(results_file, 'w') as f:
                json.dump([r.to_dict() for r in results], f, indent=2)
            
            print(f"\nResults saved to: {output_dir}")


if __name__ == "__main__":
    main()
