"""
Main Simulation module for Project Selene Consortium Simulator v2.0
Orchestrates agents, dependency chains, shocks, and outcomes.

This is the core runner that implements the ODD protocol process flow.
"""

import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pathlib import Path

from .agent import (
    ConsortiumAgent, AgentType, create_agent_from_config
)
from .dependency_chain import (
    DependencyChain, create_selene_dependency_chain
)
from .shocks import (
    ShockGenerator, ExternalShock, create_shock_generator
)


class OutcomeCategory(Enum):
    """Final outcome classification per ODD protocol."""
    STRUCTURAL_SUCCESS = "structural_success"      # ≥4 agents, functionality ≥0.8
    PARTIAL_SUCCESS = "partial_success"            # 2-3 agents, functionality 0.4-0.7
    GRACEFUL_DEGRADATION = "graceful_degradation"  # 1-2 agents, functionality 0.2-0.4
    ORDERLY_DISSOLUTION = "orderly_dissolution"    # Early exit before Phase 6, no cascade
    CATASTROPHIC_FAILURE = "catastrophic_failure"  # Poison pill triggered, total loss


@dataclass
class PhaseConfig:
    """Configuration for a single phase."""
    phase_number: int
    name: str
    duration_ticks: int = 2                        # 6 months per tick
    investment_required: float = 0.0               # €B per agent
    revenue_generated: float = 0.0                 # €B total (if operational)
    irreversibility_threshold: bool = False        # Point of no return?
    forfeiture_penalty: float = 0.0                # 0-1, fraction forfeited on exit


# Default Selene phase structure
DEFAULT_PHASES = [
    PhaseConfig(0, "Phase 0: Precursor", 4, 0.5, 0.0, False, 0.0),
    PhaseConfig(1, "Phase 1: Legal Foundation", 4, 1.0, 0.0, False, 0.1),
    PhaseConfig(2, "Phase 2: Initial Capital", 4, 3.0, 0.0, False, 0.2),
    PhaseConfig(3, "Phase 3: Robotic Precursor", 4, 5.0, 0.0, False, 0.3),
    PhaseConfig(4, "Phase 4: ISRU Demo", 4, 4.0, 0.0, False, 0.4),
    PhaseConfig(5, "Phase 5: Scale-Up", 4, 6.0, 0.0, False, 0.5),
    PhaseConfig(6, "Phase 6: Core Build Start", 4, 8.0, 0.0, True, 0.7),   # Irreversibility!
    PhaseConfig(7, "Phase 7: Habitat Deploy", 4, 7.0, 0.0, True, 0.8),
    PhaseConfig(8, "Phase 8: Power Install", 4, 5.0, 0.0, True, 0.9),
    PhaseConfig(9, "Phase 9: Pre-Operations", 4, 3.0, 0.5, True, 1.0),
    PhaseConfig(10, "Phase 10: Grand Opening", 4, 2.0, 1.0, True, 1.0),
    PhaseConfig(11, "Phase 11: Full Operations", 4, 1.0, 2.0, True, 1.0),
    PhaseConfig(12, "Phase 12: Mature Operations", 4, 0.5, 3.0, True, 1.0),
]


@dataclass
class SimulationResult:
    """Complete results from a single simulation run."""
    run_id: int
    outcome: OutcomeCategory
    final_phase: int
    final_active_agents: int
    final_functionality: float
    total_investment: float
    total_revenue: float
    
    # Detailed tracking
    defection_log: List[Dict[str, Any]] = field(default_factory=list)
    shock_log: List[Dict[str, Any]] = field(default_factory=list)
    phase_log: List[Dict[str, Any]] = field(default_factory=list)
    final_agent_states: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    early_defections: int = 0    # Phases 0-5
    late_defections: int = 0     # Phases 6+
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "outcome": self.outcome.value,
            "final_phase": self.final_phase,
            "final_active_agents": self.final_active_agents,
            "final_functionality": round(self.final_functionality, 3),
            "total_investment": round(self.total_investment, 2),
            "total_revenue": round(self.total_revenue, 2),
            "early_defections": self.early_defections,
            "late_defections": self.late_defections,
            "defection_log": self.defection_log,
            "shock_log": self.shock_log,
        }


class ConsortiumSimulator:
    """
    Main simulation engine.
    
    Implements the ODD protocol process flow:
    1. External shock phase
    2. Domestic politics phase
    3. Defection decision phase
    4. Forfeiture phase
    5. Cascade phase
    6. Investment phase
    7. Revenue phase
    8. Audit phase
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        seed: Optional[int] = None
    ):
        self.config = config
        self.seed = seed
        
        # Core parameters
        self.max_phases = config.get("max_phases", 13)
        self.poison_pill_threshold = config.get("poison_pill_threshold", 2)  # Min agents for survival
        self.cascade_on_withdrawal = config.get("cascade_on_withdrawal", True)
        
        # Initialize components (will be reset each run)
        self.agents: Dict[str, ConsortiumAgent] = {}
        self.dependency_chain: Optional[DependencyChain] = None
        self.shock_generator: Optional[ShockGenerator] = None
        self.phases: List[PhaseConfig] = []
        
        # State tracking
        self.current_phase = 0
        self.global_state: Dict[str, Any] = {}
        self.run_id = 0
    
    def _setup_run(self, run_id: int):
        """Initialize/reset all state for a new run."""
        self.run_id = run_id
        
        if self.seed is not None:
            random.seed(self.seed + run_id)
        
        # Reset global state
        self.current_phase = 0
        self.global_state = {
            "political_volatility": self.config.get("initial_volatility", 0.1),
            "economic_stress": self.config.get("initial_economic_stress", 0.1),
            "technical_risk": self.config.get("initial_technical_risk", 0.1),
            "total_investment": 0.0,
            "total_revenue": 0.0,
            "isru_success": False,
        }
        
        # Create agents from config
        self.agents = {}
        agent_configs = self.config.get("agents", [])
        for agent_config in agent_configs:
            agent = create_agent_from_config(agent_config)
            
            # Apply scenario trust modifier
            trust_modifier = self.config.get("trust_modifier", 0.0)
            agent.trust_level = max(0.0, min(1.0, agent.trust_level + trust_modifier))
            
            self.agents[agent.agent_id] = agent
        
        # Create dependency chain
        dep_config = self.config.get("dependency_chain", {})
        self.dependency_chain = DependencyChain(dep_config)
        
        if "dependency_graph" in self.config:
            self.dependency_chain.load_from_config(self.config["dependency_graph"])
        else:
            # Use default Selene graph
            from .dependency_chain import DEFAULT_SELENE_GRAPH
            self.dependency_chain.load_from_config(DEFAULT_SELENE_GRAPH)
        
        # Create shock generator
        shock_config = self.config.get("shocks", {})
        self.shock_generator = create_shock_generator(shock_config)
        
        # Load phases
        if "phases" in self.config:
            self.phases = [
                PhaseConfig(**p) for p in self.config["phases"]
            ]
        else:
            self.phases = DEFAULT_PHASES.copy()
    
    def _get_active_agents(self) -> List[ConsortiumAgent]:
        """Get list of agents still in consortium."""
        return [a for a in self.agents.values() if a.active]
    
    def _get_active_agent_ids(self) -> List[str]:
        """Get IDs of active agents."""
        return [a.agent_id for a in self._get_active_agents()]
    
    def _run_external_shocks(self) -> List[ExternalShock]:
        """Generate and apply external shocks for current phase."""
        active_ids = self._get_active_agent_ids()
        if not active_ids:
            return []
        
        shocks = self.shock_generator.generate_shocks(
            self.current_phase,
            active_ids,
            self.global_state
        )
        
        # Apply to agents
        self.shock_generator.apply_shocks_to_agents(
            shocks,
            self.agents,
            self.global_state
        )
        
        return shocks
    
    def _run_domestic_politics(self) -> List[str]:
        """Run domestic veto checks. Returns list of agents that vetoed."""
        vetoed = []
        phase_config = self.phases[min(self.current_phase, len(self.phases) - 1)]
        
        for agent in self._get_active_agents():
            if agent.domestic_veto_check(self.current_phase, self.config):
                vetoed.append(agent.agent_id)
        
        return vetoed
    
    def _run_defection_decisions(self) -> List[str]:
        """Run defection probability checks. Returns list of defectors."""
        defected = []
        
        for agent in self._get_active_agents():
            if agent.decide_defection(self.current_phase, self.global_state, self.config):
                defected.append(agent.agent_id)
        
        return defected
    
    def _execute_forfeiture(self, defector_id: str) -> Dict[str, Any]:
        """
        Execute forfeiture when agent withdraws.
        Redistributes assets to remaining agents.
        """
        if defector_id not in self.agents:
            return {}
        
        defector = self.agents[defector_id]
        phase_config = self.phases[min(self.current_phase, len(self.phases) - 1)]
        
        # Calculate forfeiture amount
        forfeiture_amount = defector.sunk_cost * phase_config.forfeiture_penalty
        lc_forfeiture = defector.lc_balance * phase_config.forfeiture_penalty
        
        # Redistribute to remaining active agents
        remaining = self._get_active_agents()
        if remaining:
            total_equity = sum(a.equity_share for a in remaining)
            for agent in remaining:
                if total_equity > 0:
                    share = agent.equity_share / total_equity
                    agent.receive_forfeiture(
                        forfeiture_amount * share,
                        lc_forfeiture * share
                    )
                    # Trust boost from surviving together
                    agent.update_trust(0.05)
        
        return {
            "defector": defector_id,
            "forfeiture_amount": forfeiture_amount,
            "lc_forfeiture": lc_forfeiture,
            "phase": self.current_phase,
        }
    
    def _run_cascade(self, defector_ids: List[str]) -> Dict[str, Any]:
        """
        Run dependency chain cascade after withdrawals.
        """
        if not self.cascade_on_withdrawal:
            return {"cascade_occurred": False}
        
        # Mark defector nodes as non-functional
        for defector_id in defector_ids:
            self.dependency_chain.withdraw_agent(defector_id)
        
        # Propagate cascade
        stress = self.dependency_chain.propagate_cascade()
        functionality = self.dependency_chain.calculate_system_functionality()
        
        return {
            "cascade_occurred": True,
            "stress_levels": {k: round(v, 3) for k, v in stress.items()},
            "system_functionality": functionality,
        }
    
    def _run_investment_phase(self):
        """Active agents invest in current phase."""
        phase_config = self.phases[min(self.current_phase, len(self.phases) - 1)]
        
        for agent in self._get_active_agents():
            investment = phase_config.investment_required * agent.equity_share * 5
            agent.invest(investment)
            self.global_state["total_investment"] += investment
            
            # Investment builds commitment (trust boost)
            agent.update_trust(0.02)
            
            # Public approval from progress
            if self.current_phase >= 3:  # Visible progress
                agent.update_domestic_state(approval_delta=0.02)
    
    def _run_revenue_phase(self):
        """Distribute revenue if operational."""
        phase_config = self.phases[min(self.current_phase, len(self.phases) - 1)]
        
        if phase_config.revenue_generated > 0:
            total_revenue = phase_config.revenue_generated
            self.global_state["total_revenue"] += total_revenue
            
            # Distribute as Lunar Credits
            active = self._get_active_agents()
            total_equity = sum(a.equity_share for a in active)
            
            for agent in active:
                if total_equity > 0:
                    share = agent.equity_share / total_equity
                    agent.receive_lc(total_revenue * share * 100)  # Convert to LC
                    
                    # Revenue success builds trust and approval
                    agent.update_trust(0.03)
                    agent.update_domestic_state(approval_delta=0.03)
    
    def _check_isru_success(self):
        """Check for ISRU milestone (Phase 4-5)."""
        if self.current_phase >= 4 and not self.global_state["isru_success"]:
            # 80% success rate if we get this far
            if random.random() < 0.8:
                self.global_state["isru_success"] = True
    
    def _check_termination(self) -> Optional[OutcomeCategory]:
        """
        Check if simulation should end.
        Returns outcome category if terminated, None otherwise.
        """
        active_count = len(self._get_active_agents())
        functionality = self.dependency_chain.calculate_system_functionality()
        
        # Poison pill: too few agents
        if active_count < self.poison_pill_threshold:
            return OutcomeCategory.CATASTROPHIC_FAILURE
        
        # System functionality collapsed
        if functionality < 0.2 and self.current_phase > 2:
            return OutcomeCategory.CATASTROPHIC_FAILURE
        
        # Reached end successfully
        if self.current_phase >= self.max_phases - 1:
            if active_count >= 4 and functionality >= 0.8:
                return OutcomeCategory.STRUCTURAL_SUCCESS
            elif active_count >= 2 and functionality >= 0.4:
                return OutcomeCategory.PARTIAL_SUCCESS
            elif active_count >= 1:
                return OutcomeCategory.GRACEFUL_DEGRADATION
            else:
                return OutcomeCategory.CATASTROPHIC_FAILURE
        
        return None  # Continue
    
    def _classify_outcome(self) -> OutcomeCategory:
        """Classify final outcome based on state."""
        active_count = len(self._get_active_agents())
        functionality = self.dependency_chain.calculate_system_functionality()
        
        if active_count >= 4 and functionality >= 0.8:
            return OutcomeCategory.STRUCTURAL_SUCCESS
        elif active_count >= 2 and functionality >= 0.4:
            return OutcomeCategory.PARTIAL_SUCCESS
        elif active_count >= 1 and functionality >= 0.2:
            return OutcomeCategory.GRACEFUL_DEGRADATION
        elif self.current_phase < 6 and active_count == 0:
            return OutcomeCategory.ORDERLY_DISSOLUTION
        else:
            return OutcomeCategory.CATASTROPHIC_FAILURE
    
    def run_single(self, run_id: int = 0) -> SimulationResult:
        """
        Execute a single simulation run.
        """
        self._setup_run(run_id)
        
        defection_log = []
        shock_log = []
        phase_log = []
        
        outcome = None
        
        while self.current_phase < self.max_phases:
            phase_start_agents = len(self._get_active_agents())
            
            # 1. External shocks
            shocks = self._run_external_shocks()
            for shock in shocks:
                shock_log.append(shock.to_dict())
            
            # 2. Domestic politics (EDC-style veto)
            vetoed = self._run_domestic_politics()
            for agent_id in vetoed:
                defection_log.append({
                    "agent_id": agent_id,
                    "phase": self.current_phase,
                    "reason": "domestic_veto",
                    "type": "early" if self.current_phase < 6 else "late",
                })
            
            # 3. Defection decisions
            defected = self._run_defection_decisions()
            for agent_id in defected:
                defection_log.append({
                    "agent_id": agent_id,
                    "phase": self.current_phase,
                    "reason": "calculated_defection",
                    "type": "early" if self.current_phase < 6 else "late",
                })
            
            # 4. Forfeiture for all who left
            all_departures = vetoed + defected
            for agent_id in all_departures:
                self._execute_forfeiture(agent_id)
            
            # 5. Cascade effects
            if all_departures:
                cascade_result = self._run_cascade(all_departures)
            
            # 6. Check ISRU milestone
            self._check_isru_success()
            
            # 7. Investment phase
            self._run_investment_phase()
            
            # 8. Revenue phase
            self._run_revenue_phase()
            
            # Log phase state
            phase_log.append({
                "phase": self.current_phase,
                "active_agents": len(self._get_active_agents()),
                "functionality": self.dependency_chain.calculate_system_functionality(),
                "total_investment": self.global_state["total_investment"],
                "departures": len(all_departures),
            })
            
            # 9. Check termination
            outcome = self._check_termination()
            if outcome is not None:
                break
            
            # Decay volatility over time (stabilization)
            self.global_state["political_volatility"] *= 0.9
            self.global_state["economic_stress"] *= 0.95
            
            self.current_phase += 1
        
        # Final classification if not already set
        if outcome is None:
            outcome = self._classify_outcome()
        
        # Count early vs late defections
        early = sum(1 for d in defection_log if d["type"] == "early")
        late = sum(1 for d in defection_log if d["type"] == "late")
        
        return SimulationResult(
            run_id=run_id,
            outcome=outcome,
            final_phase=self.current_phase,
            final_active_agents=len(self._get_active_agents()),
            final_functionality=self.dependency_chain.calculate_system_functionality(),
            total_investment=self.global_state["total_investment"],
            total_revenue=self.global_state["total_revenue"],
            defection_log=defection_log,
            shock_log=shock_log,
            phase_log=phase_log,
            final_agent_states=[a.to_dict() for a in self.agents.values()],
            early_defections=early,
            late_defections=late,
        )
    
    def run_batch(
        self,
        n_runs: int = 100,
        verbose: bool = True
    ) -> List[SimulationResult]:
        """
        Run multiple simulations and return all results.
        """
        results = []
        
        for i in range(n_runs):
            result = self.run_single(run_id=i)
            results.append(result)
            
            if verbose and (i + 1) % 10 == 0:
                print(f"Completed {i + 1}/{n_runs} runs")
        
        return results


def summarize_results(results: List[SimulationResult]) -> Dict[str, Any]:
    """
    Generate aggregate statistics from batch results.
    """
    n = len(results)
    if n == 0:
        return {}
    
    # Outcome distribution
    outcomes = {}
    for cat in OutcomeCategory:
        outcomes[cat.value] = sum(1 for r in results if r.outcome == cat)
    
    # Averages
    avg_final_agents = sum(r.final_active_agents for r in results) / n
    avg_functionality = sum(r.final_functionality for r in results) / n
    avg_early_defections = sum(r.early_defections for r in results) / n
    avg_late_defections = sum(r.late_defections for r in results) / n
    avg_investment = sum(r.total_investment for r in results) / n
    
    # Success rates
    structural_rate = outcomes.get("structural_success", 0) / n
    partial_rate = outcomes.get("partial_success", 0) / n
    positive_rate = structural_rate + partial_rate + outcomes.get("graceful_degradation", 0) / n
    
    return {
        "n_runs": n,
        "outcome_distribution": outcomes,
        "outcome_percentages": {k: round(v/n * 100, 1) for k, v in outcomes.items()},
        "avg_final_agents": round(avg_final_agents, 2),
        "avg_functionality": round(avg_functionality, 3),
        "avg_early_defections": round(avg_early_defections, 2),
        "avg_late_defections": round(avg_late_defections, 2),
        "avg_investment": round(avg_investment, 2),
        "structural_success_rate": round(structural_rate * 100, 1),
        "positive_outcome_rate": round(positive_rate * 100, 1),
    }
