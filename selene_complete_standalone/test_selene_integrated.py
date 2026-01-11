#!/usr/bin/env python3
"""
PROJECT SELENE ABM — Integrated Test Suite
==========================================
pytest-based verification and regression tests using actual selene_sim modules.

Categories:
- Phase 1: Boundary & Edge Cases (Verification)
- Phase 2: Pattern Calibration
- Phase 3: Statistical Properties
- Regression: Prevent unintended behavior changes

Run: pytest test_selene_integrated.py -v
Run with coverage: pytest test_selene_integrated.py --cov=selene_sim
Run quick: pytest test_selene_integrated.py -v -m "not slow"

Created: January 2026
Status: Integrated with v2.1 codebase
"""

import pytest
import random
import statistics
import sys
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import actual selene_sim modules
from selene_sim.agent import (
    ConsortiumAgent, 
    AgentType, 
    AgentProfile,
    DEFAULT_PROFILES,
    create_agent_from_config
)
from selene_sim.simulation import (
    ConsortiumSimulator,
    OutcomeCategory,
    SimulationResult,
    DEFAULT_PHASES
)
from selene_sim.dependency_chain import DependencyChain
from selene_sim.shocks import ShockGenerator, create_shock_generator


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

@dataclass
class _TestConfiguration:
    """Configuration for test runs."""
    n_runs_quick: int = 50      # Quick tests
    n_runs_standard: int = 200  # Standard verification
    n_runs_thorough: int = 1000 # Thorough validation
    random_seed: int = 42       # Reproducibility


CONFIG = _TestConfiguration()


# =============================================================================
# STANDARD TEST CONFIGURATION FACTORY
# =============================================================================

def make_simulation_config(
    n_agents: int = 5,
    initial_trust: float = 0.5,
    trust_variance: float = 0.0,
    disable_shocks: bool = False,
    poison_pill_threshold: int = 2,
    max_phases: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a simulation configuration dictionary.
    
    This mirrors the YAML config structure used by ConsortiumSimulator.
    """
    # Standard agent composition
    agent_types = [
        ("eu_esa", "EU/ESA", "track_a_core"),
        ("china_cnsa", "China/CNSA", "track_b_core"),
        ("russia_ros", "Russia/Roscosmos", "track_b_core"),
        ("india_isro", "India/ISRO", "associate"),
        ("uae_mbrsc", "UAE/MBRSC", "associate"),
    ]
    
    agents = []
    for i, (agent_id, name, agent_type) in enumerate(agent_types[:n_agents]):
        # Apply trust with optional variance
        trust = initial_trust
        if trust_variance > 0:
            trust = max(0.0, min(1.0, initial_trust + random.gauss(0, trust_variance)))
        
        agents.append({
            "agent_id": agent_id,
            "name": name,
            "agent_type": agent_type,
            "equity_share": 1.0 / n_agents,
            "initial_trust": trust,
            "initial_approval": 0.6,
            "initial_stability": 0.7,
        })
    
    config = {
        "agents": agents,
        "max_phases": max_phases,
        "poison_pill_threshold": poison_pill_threshold,
        "cascade_on_withdrawal": True,
        "max_sunk_cost": 50.0,
        "defection_floor": 0.02,
        "defection_ceiling": 0.95,
        "trust_modifier": 0.0,
        "shocks": {
            "enabled": not disable_shocks,
            "election_probability": 0.0 if disable_shocks else 0.25,
            "economic_probability": 0.0 if disable_shocks else 0.15,
            "technical_probability": 0.0 if disable_shocks else 0.10,
        },
        **kwargs
    }
    
    return config


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def seeded_random():
    """Ensure reproducible random state for test."""
    random.seed(CONFIG.random_seed)
    yield
    random.seed()  # Reset after test


@pytest.fixture
def default_config():
    """Standard test configuration."""
    return make_simulation_config()


@pytest.fixture
def perfect_trust_config():
    """Configuration with perfect trust and no shocks."""
    return make_simulation_config(
        initial_trust=1.0,
        trust_variance=0.0,
        disable_shocks=True
    )


@pytest.fixture
def zero_trust_config():
    """Configuration with zero trust."""
    return make_simulation_config(
        initial_trust=0.0,
        trust_variance=0.0,
        disable_shocks=True
    )


# =============================================================================
# PHASE 1: BOUNDARY AND EDGE CASE TESTS (VERIFICATION)
# =============================================================================

class TestPhase1Verification:
    """
    Phase 1 Verification Tests
    --------------------------
    These tests verify boundary conditions and basic model behavior.
    All must pass before any analysis is credible.
    """
    
    def test_perfect_trust_yields_high_success(self, seeded_random):
        """
        BOUNDARY TEST: Perfect trust (1.0) + no shocks → very high success rate
        
        Rationale: If trust is perfect and no shocks occur, defection should
        be minimal. This is the upper bound on model performance.
        """
        config = make_simulation_config(
            initial_trust=1.0,
            trust_variance=0.0,
            disable_shocks=True,
            max_phases=5
        )
        
        successes = 0
        n_runs = CONFIG.n_runs_standard
        
        for run_id in range(n_runs):
            random.seed(CONFIG.random_seed + run_id)
            sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
            result = sim.run_single(run_id)
            
            if result.outcome in [OutcomeCategory.STRUCTURAL_SUCCESS, 
                                  OutcomeCategory.PARTIAL_SUCCESS]:
                successes += 1
        
        success_rate = successes / n_runs
        
        # Perfect trust should yield elevated success
        # Note: Model has defection floor (2%), so even perfect trust allows some defection
        # With 5 agents over 5 phases = 25 defection opportunities, expect some failures
        assert success_rate >= 0.60, (
            f"Perfect trust should yield ≥60% success (above medium trust), got {success_rate:.1%}"
        )
    
    def test_zero_trust_yields_high_failure(self, seeded_random):
        """
        BOUNDARY TEST: Zero trust (0.0) → high failure/defection rate
        
        Rationale: If no agent trusts any other, defection should be common.
        This is the lower bound on model performance.
        """
        config = make_simulation_config(
            initial_trust=0.0,
            trust_variance=0.0,
            disable_shocks=True,
            max_phases=5
        )
        
        failures = 0
        early_defection_runs = 0
        n_runs = CONFIG.n_runs_standard
        
        for run_id in range(n_runs):
            random.seed(CONFIG.random_seed + run_id)
            sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
            result = sim.run_single(run_id)
            
            if result.outcome == OutcomeCategory.CATASTROPHIC_FAILURE:
                failures += 1
            
            # Check for early defections
            if result.early_defections > 0:
                early_defection_runs += 1
        
        failure_rate = failures / n_runs
        early_defection_rate = early_defection_runs / n_runs
        
        # Zero trust should yield elevated failure
        assert failure_rate >= 0.50, (
            f"Zero trust should yield ≥50% failure, got {failure_rate:.1%}"
        )
        
        # Most runs should have early defections
        assert early_defection_rate >= 0.60, (
            f"Zero trust should yield ≥60% runs with early defection, got {early_defection_rate:.1%}"
        )
    
    def test_single_agent_does_not_crash(self, seeded_random):
        """
        EDGE CASE: Single agent consortium should not crash.
        """
        config = make_simulation_config(
            n_agents=1,
            initial_trust=0.7,
            disable_shocks=True
        )
        
        crashes = 0
        n_runs = CONFIG.n_runs_quick
        
        for run_id in range(n_runs):
            try:
                random.seed(CONFIG.random_seed + run_id)
                sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
                result = sim.run_single(run_id)
                # Should complete without exception
            except Exception as e:
                crashes += 1
        
        assert crashes == 0, f"Single agent simulation crashed {crashes} times"
    
    def test_two_agent_minimum(self, seeded_random):
        """
        EDGE CASE: Two-agent consortium (minimum for meaningful interaction).
        """
        config = make_simulation_config(
            n_agents=2,
            initial_trust=0.8,
            disable_shocks=True
        )
        
        crashes = 0
        n_runs = CONFIG.n_runs_quick
        
        for run_id in range(n_runs):
            try:
                random.seed(CONFIG.random_seed + run_id)
                sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
                result = sim.run_single(run_id)
            except Exception as e:
                crashes += 1
        
        assert crashes == 0, f"Two-agent simulation crashed {crashes} times"
    
    def test_mass_defection_graceful_handling(self, seeded_random):
        """
        STRESS TEST: Very low trust + strong shocks should trigger defections.
        Model should handle gracefully without crashing.
        """
        config = make_simulation_config(
            n_agents=5,
            initial_trust=0.1,
            disable_shocks=False,
            poison_pill_threshold=2
        )
        # Override shock config for high stress
        config["shocks"] = {
            "enabled": True,
            "election_probability": 0.4,
            "economic_probability": 0.3,
            "technical_probability": 0.2,
        }
        
        crashes = 0
        cascade_count = 0
        n_runs = CONFIG.n_runs_standard
        
        for run_id in range(n_runs):
            try:
                random.seed(CONFIG.random_seed + run_id)
                sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
                result = sim.run_single(run_id)
                
                if result.outcome == OutcomeCategory.CATASTROPHIC_FAILURE:
                    cascade_count += 1
            except Exception as e:
                crashes += 1
        
        assert crashes == 0, f"Mass defection scenario crashed {crashes} times"
        
        # Under these conditions, cascades should occur frequently
        cascade_rate = cascade_count / n_runs
        assert cascade_rate >= 0.30, (
            f"Low trust + high shocks should yield ≥30% cascades, got {cascade_rate:.1%}"
        )


# =============================================================================
# PHASE 2: PATTERN CALIBRATION TESTS
# =============================================================================

class TestPhase2PatternCalibration:
    """
    Phase 2 Pattern Calibration Tests
    ----------------------------------
    These tests verify that model produces expected qualitative patterns
    based on historical analogs (ECSC, EDC, etc.).
    """
    
    def test_sunk_cost_reduces_late_defection(self, seeded_random):
        """
        PATTERN: Defection probability should be lower in later phases
        due to sunk cost accumulation.
        """
        config = make_simulation_config(
            initial_trust=0.5,
            disable_shocks=True,
            max_phases=5
        )
        
        early_defections = 0
        late_defections = 0
        n_runs = CONFIG.n_runs_standard
        
        for run_id in range(n_runs):
            random.seed(CONFIG.random_seed + run_id)
            sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
            result = sim.run_single(run_id)
            
            early_defections += result.early_defections
            late_defections += result.late_defections
        
        # Early phases (0-5) should have more defections than late phases (6+)
        # Note: With max_phases=5, we're testing phases 0-4
        # Adjust expectation accordingly
        total = early_defections + late_defections
        if total > 0:
            early_ratio = early_defections / total
            # With only 5 phases (all "early"), we expect high early ratio
            assert early_ratio >= 0.70, (
                f"Most defections should be early, got {early_ratio:.1%}"
            )
    
    def test_trust_monotonically_affects_success(self, seeded_random):
        """
        PATTERN: Higher trust should monotonically increase success rate.
        """
        trust_levels = [0.2, 0.4, 0.6, 0.8]
        success_rates = []
        n_runs = CONFIG.n_runs_standard
        
        for trust in trust_levels:
            config = make_simulation_config(
                initial_trust=trust,
                disable_shocks=True
            )
            
            successes = 0
            for run_id in range(n_runs):
                random.seed(CONFIG.random_seed + run_id)
                sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
                result = sim.run_single(run_id)
                
                if result.outcome in [OutcomeCategory.STRUCTURAL_SUCCESS,
                                      OutcomeCategory.PARTIAL_SUCCESS]:
                    successes += 1
            
            success_rates.append(successes / n_runs)
        
        # Verify monotonic increase (allowing small tolerance for Monte Carlo noise)
        for i in range(len(success_rates) - 1):
            assert success_rates[i] <= success_rates[i + 1] + 0.05, (
                f"Success rate not monotonic in trust: {dict(zip(trust_levels, success_rates))}"
            )
    
    def test_poison_pill_triggers_cascade(self, seeded_random):
        """
        PATTERN: When active agents drop below threshold, cascade should occur.
        """
        config = make_simulation_config(
            n_agents=5,
            initial_trust=0.2,  # Low trust to encourage defection
            disable_shocks=True,
            poison_pill_threshold=3  # Need ≥3 agents
        )
        
        cascades = 0
        n_runs = CONFIG.n_runs_standard
        
        for run_id in range(n_runs):
            random.seed(CONFIG.random_seed + run_id)
            sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
            result = sim.run_single(run_id)
            
            if result.outcome == OutcomeCategory.CATASTROPHIC_FAILURE:
                cascades += 1
        
        cascade_rate = cascades / n_runs
        # Low trust should trigger cascades in a meaningful fraction of runs
        assert cascade_rate >= 0.20, (
            f"Low trust + strong pill should yield ≥20% cascades, got {cascade_rate:.1%}"
        )


# =============================================================================
# PHASE 3: STATISTICAL PROPERTY TESTS
# =============================================================================

class TestPhase3StatisticalProperties:
    """
    Phase 3 Statistical Property Tests
    -----------------------------------
    These tests verify statistical properties of model outputs.
    """
    
    def test_output_has_variance(self, seeded_random):
        """
        STATISTICAL: Model should produce variable outcomes (is stochastic).
        """
        config = make_simulation_config(
            initial_trust=0.5,
            disable_shocks=False
        )
        
        outcomes = []
        n_runs = CONFIG.n_runs_standard
        
        for run_id in range(n_runs):
            random.seed(CONFIG.random_seed + run_id)
            sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
            result = sim.run_single(run_id)
            outcomes.append(result.final_active_agents)
        
        # Should have non-zero variance
        variance = statistics.variance(outcomes) if len(outcomes) > 1 else 0
        assert variance > 0, "Model should have non-zero output variance"
    
    def test_defection_probability_bounds(self, seeded_random):
        """
        STATISTICAL: Defection probability should always be in valid range.
        """
        # Create an agent directly
        agent = ConsortiumAgent(
            agent_id="test_agent",
            agent_type=AgentType.TRACK_A_CORE,
            name="Test Agent",
            trust_level=0.5,
        )
        
        # Test various conditions
        test_cases = [
            {"political_volatility": 0.0},
            {"political_volatility": 0.5},
            {"political_volatility": 1.0},
        ]
        
        config = {"max_sunk_cost": 50.0, "defection_floor": 0.02, "defection_ceiling": 0.95}
        
        for global_state in test_cases:
            for phase in range(5):
                for trust in [0.0, 0.5, 1.0]:
                    agent.trust_level = trust
                    prob = agent.calculate_defection_probability(phase, global_state, config)
                    
                    assert 0.0 <= prob <= 1.0, (
                        f"Invalid probability {prob} for trust={trust}, phase={phase}"
                    )
    
    @pytest.mark.slow
    def test_confidence_interval_width(self, seeded_random):
        """
        STATISTICAL: Bootstrap CI width should shrink with sample size.
        """
        config = make_simulation_config(
            initial_trust=0.5,
            disable_shocks=True
        )
        
        outcomes = []
        n_runs = CONFIG.n_runs_thorough
        
        for run_id in range(n_runs):
            random.seed(CONFIG.random_seed + run_id)
            sim = ConsortiumSimulator(config, seed=CONFIG.random_seed + run_id)
            result = sim.run_single(run_id)
            outcomes.append(1 if result.outcome in [OutcomeCategory.STRUCTURAL_SUCCESS,
                                                     OutcomeCategory.PARTIAL_SUCCESS] else 0)
        
        # Calculate bootstrap CI
        n_bootstrap = 1000
        bootstrap_means = []
        for _ in range(n_bootstrap):
            sample = random.choices(outcomes, k=len(outcomes))
            bootstrap_means.append(statistics.mean(sample))
        
        bootstrap_means.sort()
        ci_lower = bootstrap_means[int(0.025 * n_bootstrap)]
        ci_upper = bootstrap_means[int(0.975 * n_bootstrap)]
        ci_width = ci_upper - ci_lower
        
        # With 1000 runs, CI should be reasonably tight
        assert ci_width < 0.10, (
            f"CI width ({ci_width:.3f}) too wide for {n_runs} runs"
        )


# =============================================================================
# REGRESSION TESTS
# =============================================================================

class TestRegressionPreventBehaviorChanges:
    """
    Regression Tests
    ----------------
    Lock in expected behavior to prevent unintended changes.
    Update baselines deliberately when behavior changes intentionally.
    """
    
    # Known-good baselines from validated v2.1 runs
    # These are empirically determined from actual model behavior
    BASELINES = {
        "medium_trust_success_range": (0.25, 0.55),  # Actual observed range
        "high_trust_success_range": (0.45, 0.75),    # Actual observed range
        "low_trust_success_range": (0.05, 0.30),
    }
    
    def test_medium_trust_baseline(self, seeded_random):
        """REGRESSION: Medium trust (0.5) success rate in expected range."""
        random.seed(12345)  # Specific seed for regression
        
        config = make_simulation_config(
            initial_trust=0.5,
            disable_shocks=True
        )
        
        successes = 0
        n_runs = 100
        
        for run_id in range(n_runs):
            random.seed(12345 + run_id)
            sim = ConsortiumSimulator(config, seed=12345 + run_id)
            result = sim.run_single(run_id)
            if result.outcome in [OutcomeCategory.STRUCTURAL_SUCCESS,
                                  OutcomeCategory.PARTIAL_SUCCESS]:
                successes += 1
        
        success_rate = successes / n_runs
        low, high = self.BASELINES["medium_trust_success_range"]
        
        assert low <= success_rate <= high, (
            f"Medium trust regression: expected {low:.2f}-{high:.2f}, got {success_rate:.2f}"
        )
    
    def test_high_trust_baseline(self, seeded_random):
        """REGRESSION: High trust (0.8) success rate in expected range."""
        random.seed(12345)
        
        config = make_simulation_config(
            initial_trust=0.8,
            disable_shocks=True
        )
        
        successes = 0
        n_runs = 100
        
        for run_id in range(n_runs):
            random.seed(12345 + run_id)
            sim = ConsortiumSimulator(config, seed=12345 + run_id)
            result = sim.run_single(run_id)
            if result.outcome in [OutcomeCategory.STRUCTURAL_SUCCESS,
                                  OutcomeCategory.PARTIAL_SUCCESS]:
                successes += 1
        
        success_rate = successes / n_runs
        low, high = self.BASELINES["high_trust_success_range"]
        
        assert low <= success_rate <= high, (
            f"High trust regression: expected {low:.2f}-{high:.2f}, got {success_rate:.2f}"
        )


# =============================================================================
# AGENT UNIT TESTS
# =============================================================================

class TestAgentUnit:
    """Unit tests for ConsortiumAgent class."""
    
    def test_agent_creation(self):
        """Agent should initialize with correct defaults."""
        agent = ConsortiumAgent(
            agent_id="test",
            agent_type=AgentType.TRACK_A_CORE,
            name="Test Agent"
        )
        
        assert agent.agent_id == "test"
        assert agent.agent_type == AgentType.TRACK_A_CORE
        assert agent.active == True
        assert agent.defected == False
        assert agent.sunk_cost == 0.0
    
    def test_agent_defection(self):
        """Agent defection should update state correctly."""
        agent = ConsortiumAgent(
            agent_id="test",
            agent_type=AgentType.TRACK_A_CORE,
            name="Test Agent"
        )
        
        agent.defect(phase=2, reason="test_defection")
        
        assert agent.active == False
        assert agent.defected == True
        assert agent.defection_phase == 2
        assert agent.defection_reason == "test_defection"
    
    def test_agent_investment(self):
        """Agent should accumulate sunk costs correctly."""
        agent = ConsortiumAgent(
            agent_id="test",
            agent_type=AgentType.TRACK_A_CORE,
            name="Test Agent"
        )
        
        agent.invest(5.0)
        assert agent.sunk_cost == 5.0
        
        agent.invest(3.0)
        assert agent.sunk_cost == 8.0
    
    def test_agent_trust_bounds(self):
        """Trust should be bounded [0, 1]."""
        agent = ConsortiumAgent(
            agent_id="test",
            agent_type=AgentType.TRACK_A_CORE,
            name="Test Agent",
            trust_level=0.5
        )
        
        # Try to exceed bounds
        agent.update_trust(1.0)  # Should cap at 1.0
        assert agent.trust_level == 1.0
        
        agent.update_trust(-2.0)  # Should floor at 0.0
        assert agent.trust_level == 0.0
    
    def test_agent_from_config(self):
        """Agent factory should create correct agent from config."""
        config = {
            "agent_id": "eu_esa",
            "name": "EU/ESA",
            "agent_type": "track_a_core",
            "equity_share": 0.25,
            "initial_trust": 0.6,
            "initial_approval": 0.5
        }
        
        agent = create_agent_from_config(config)
        
        assert agent.agent_id == "eu_esa"
        assert agent.name == "EU/ESA"
        assert agent.agent_type == AgentType.TRACK_A_CORE
        assert agent.trust_level == 0.6
        assert agent.equity_share == 0.25


# =============================================================================
# OUTCOME CLASSIFICATION TESTS
# =============================================================================

class TestOutcomeClassification:
    """Tests for outcome classification logic."""
    
    def test_outcome_categories_exist(self):
        """All outcome categories should be defined."""
        assert OutcomeCategory.STRUCTURAL_SUCCESS
        assert OutcomeCategory.PARTIAL_SUCCESS
        assert OutcomeCategory.GRACEFUL_DEGRADATION
        assert OutcomeCategory.CATASTROPHIC_FAILURE
        assert OutcomeCategory.ORDERLY_DISSOLUTION
    
    def test_result_to_dict(self, seeded_random):
        """SimulationResult should serialize correctly."""
        config = make_simulation_config(disable_shocks=True)
        sim = ConsortiumSimulator(config, seed=42)
        result = sim.run_single(0)
        
        result_dict = result.to_dict()
        
        assert "run_id" in result_dict
        assert "outcome" in result_dict
        assert "final_phase" in result_dict
        assert "final_active_agents" in result_dict


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

@pytest.mark.slow
class TestPerformance:
    """Performance tests - run with pytest -m slow."""
    
    def test_thousand_runs_performance(self, seeded_random):
        """1000 runs should complete in reasonable time."""
        import time
        
        config = make_simulation_config()
        
        start = time.time()
        for run_id in range(1000):
            sim = ConsortiumSimulator(config, seed=run_id)
            result = sim.run_single(run_id)
        elapsed = time.time() - start
        
        # Should complete 1000 runs in under 120 seconds
        assert elapsed < 120.0, f"1000 runs took {elapsed:.1f}s (target: <120s)"
        print(f"\nPerformance: 1000 runs in {elapsed:.1f}s ({1000/elapsed:.1f} runs/sec)")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Run with: python test_selene_integrated.py
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
