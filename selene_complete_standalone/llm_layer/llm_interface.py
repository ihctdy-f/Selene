"""
LLM Interface for Project Selene ABM Suite v2.1

Provides natural language → simulation parameter translation
and simulation result → human-readable report generation.

Architecture: LLM as I/O translator only. Core simulation untouched.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selene_sim.simulation import (
    ConsortiumSimulator,
    SimulationResult,
    OutcomeCategory,
)
from selene_sim.agent import AgentType

from .config_factory import make_simulation_config


# Required disclaimer phrases - tested by autocaveat tests
REQUIRED_DISCLAIMERS = [
    "EXPLORATORY ANALYSIS ONLY",
    "Not validated for predictive use",
    "CONDITIONS_OF_USE.md",
]


class LLMSimulationInterface:
    """
    LLM interface that preserves validation framework integrity.
    
    Responsibilities:
    - Parse natural language into validated simulation configs
    - Generate reports with mandatory institutional caveats
    - Protect critical parameters from override
    
    Non-responsibilities:
    - Modifying simulation logic
    - Changing agent behavior rules
    - Bypassing validation constraints
    """
    
    def __init__(self, base_simulator_config: Optional[Dict[str, Any]] = None):
        """
        Initialize with optional base config for consistency.
        
        Args:
            base_simulator_config: Base configuration (uses defaults if None)
        """
        self.base_config = base_simulator_config or make_simulation_config()
        
        # Phrases that indicate proper epistemic framing
        self.trusted_phrases = [
            "exploratory analysis",
            "under specified assumptions",
            "not validated for predictive use",
            "confidence intervals capture parametric uncertainty only"
        ]
        
        # Parameters that cannot be modified via natural language
        self.protected_params = {
            "poison_pill_threshold",
            "defection_floor",
            "defection_ceiling",
            "cascade_on_withdrawal",
            "max_sunk_cost",
        }
        
        # Trust level keyword mapping
        self.trust_map = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
            "very high": 0.9,
            "very low": 0.1,
        }
    
    def parse_scenario(self, natural_language: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Convert natural language to simulation parameters.
        
        Args:
            natural_language: Free-text scenario description
        
        Returns:
            Tuple of (simulation_config, scenario_metadata)
        
        Maintains test suite compatibility by using factory patterns.
        """
        text_lower = natural_language.lower()
        
        # Extract trust level using regex (avoids LLM hallucination)
        trust_level = self._extract_trust_level(text_lower)
        
        # Extract scenario metadata
        scenario_metadata = self._extract_scenario_metadata(text_lower)
        
        # Extract safe parameters
        extracted_params = self._extract_parameters(natural_language)
        
        # Merge any warning flags
        if extracted_params.get("_warning_flags"):
            scenario_metadata["warning_flags"].extend(extracted_params.pop("_warning_flags"))
        
        # Build config using factory method - maintains test compatibility
        simulation_config = make_simulation_config(
            initial_trust=trust_level,
            **extracted_params
        )
        
        return simulation_config, scenario_metadata
    
    def _extract_trust_level(self, text: str) -> float:
        """Extract trust level from natural language."""
        # Check for keyword trust levels first
        for keyword, value in self.trust_map.items():
            if f"{keyword} trust" in text:
                return value
        
        # Try to extract numeric trust value
        trust_match = re.search(r'(\d+(\.\d+)?)\s*trust', text)
        if trust_match:
            try:
                trust_level = float(trust_match.group(1))
                # Handle percentage vs decimal
                if trust_level > 1.0:
                    trust_level = trust_level / 100.0
                return max(0.0, min(1.0, trust_level))
            except (ValueError, TypeError):
                pass
        
        # Default to medium trust
        return 0.5
    
    def _extract_scenario_metadata(self, text: str) -> Dict[str, Any]:
        """Extract scenario type and metadata from natural language."""
        metadata = {
            "scenario_type": "generic",
            "confidence": "MEDIUM",
            "warning_flags": [],
            "extracted_at": datetime.now().isoformat(),
        }
        
        # Detect specific scenario patterns
        if "turkey" in text and "nato" in text:
            metadata.update({
                "scenario_type": "nato_defection",
                "primary_actor": "Turkey",
                "historical_calibration": "NATO_2022",
            })
        elif "brexit" in text or "uk leave" in text:
            metadata.update({
                "scenario_type": "brexit_analog",
                "primary_actor": "UK",
                "historical_calibration": "ECSC_1957",
            })
        elif "sanctions" in text:
            metadata.update({
                "scenario_type": "sanctions_scenario",
                "confidence": "LOW",  # Sanctions scenarios are harder to calibrate
            })
        elif "china" in text and ("withdraw" in text or "defect" in text):
            metadata.update({
                "scenario_type": "major_power_exit",
                "primary_actor": "China",
            })
        
        return metadata
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """
        Safe parameter extraction that preserves test constraints.
        
        Only extracts parameters that the test suite validates.
        Protected parameters are logged as warnings but not applied.
        """
        params = {}
        warning_flags = []
        text_lower = text.lower()
        
        # Agent count
        agent_patterns = [
            (r'(\d+)\s*agents?', lambda m: int(m.group(1))),
            (r'(one|two|three|four|five)\s*agents?', 
             lambda m: {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}[m.group(1)]),
        ]
        for pattern, extractor in agent_patterns:
            match = re.search(pattern, text_lower)
            if match:
                n_agents = extractor(match)
                if 1 <= n_agents <= 5:
                    params["n_agents"] = n_agents
                else:
                    warning_flags.append(f"Agent count {n_agents} outside valid range 1-5, using default")
                break
        
        # Phase count
        phase_match = re.search(r'(\d+)\s*phases?', text_lower)
        if phase_match:
            phases = int(phase_match.group(1))
            if 1 <= phases <= 13:
                params["max_phases"] = phases
        
        # Shock control
        if "disable shock" in text_lower or "no shock" in text_lower:
            params["disable_shocks"] = True
        elif "enable shock" in text_lower or "with shock" in text_lower:
            params["disable_shocks"] = False
        
        # Trust variance
        if "varied trust" in text_lower or "heterogeneous trust" in text_lower:
            params["trust_variance"] = 0.15
        
        # Check for attempts to override protected parameters
        for param in self.protected_params:
            # Check various override patterns
            patterns = [
                rf'{param}\s*[=:]\s*[\d.]+',
                rf'set\s+{param}',
                rf'override\s+{param}',
                rf'{param.replace("_", " ")}\s*[=:]\s*[\d.]+',
            ]
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    warning_flags.append(f"Ignored unsafe parameter override attempt: {param}")
                    break
        
        if warning_flags:
            params["_warning_flags"] = warning_flags
        
        return params
    
    def generate_report(
        self, 
        simulation_result: SimulationResult, 
        metadata: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate human-readable report with proper institutional caveats.
        
        Args:
            simulation_result: Result from ConsortiumSimulator.run_single()
            metadata: Scenario metadata from parse_scenario()
            config: Optional config dict (for initial_trust lookup)
        
        Returns:
            Formatted report string with mandatory disclaimers
        """
        # Use provided config or fall back to base
        config = config or self.base_config
        
        # Validate result against test expectations
        validation_status = self._validate_result_compatibility(simulation_result)
        
        # Build report with mandatory caveats
        report = self._build_structured_report(
            simulation_result, 
            metadata, 
            validation_status,
            config
        )
        
        return report
    
    def _validate_result_compatibility(self, result: SimulationResult) -> Dict[str, bool]:
        """
        Ensure result respects test suite constraints.
        
        Returns dict of validation checks and their status.
        """
        return {
            "valid_outcome_category": isinstance(result.outcome, OutcomeCategory),
            "agent_count_valid": result.final_active_agents >= 0,
            "functionality_bounded": 0.0 <= result.final_functionality <= 1.0,
            "phase_valid": result.final_phase >= 0,
            "investment_non_negative": result.total_investment >= 0,
        }
    
    def _build_structured_report(
        self, 
        result: SimulationResult, 
        metadata: Dict[str, Any], 
        validation: Dict[str, bool],
        config: Dict[str, Any]
    ) -> str:
        """
        Build report that maintains institutional validation standards.
        
        Includes all required disclaimers per CONDITIONS_OF_USE.md
        """
        # Get initial trust from config (not on result)
        initial_trust = config.get("initial_trust", 0.5)
        
        # Validation status indicator
        all_valid = all(validation.values())
        validation_icon = "✅" if all_valid else "⚠️"
        
        # Mandatory disclaimer - preserves institutional integrity
        disclaimer = (
            "⚠️ EXPLORATORY ANALYSIS ONLY\n"
            "Results reflect model behavior under specified assumptions.\n"
            "Confidence intervals capture parametric uncertainty only.\n"
            "Not validated for predictive use or decision support.\n"
            "See CONDITIONS_OF_USE.md for authorized applications.\n"
            f"Validation status: {validation_icon}\n"
        )
        
        # Outcome descriptions matching OutcomeCategory enum
        outcome_descriptions = {
            OutcomeCategory.STRUCTURAL_SUCCESS: "High success probability (≥4 agents, high functionality)",
            OutcomeCategory.PARTIAL_SUCCESS: "Partial success (2-3 agents, moderate functionality)",
            OutcomeCategory.GRACEFUL_DEGRADATION: "Graceful degradation (1-2 agents, reduced functionality)",
            OutcomeCategory.CATASTROPHIC_FAILURE: "Catastrophic failure (poison pill triggered)",
            OutcomeCategory.ORDERLY_DISSOLUTION: "Orderly dissolution (early exit, no cascade)",
        }
        outcome_text = outcome_descriptions.get(result.outcome, "Unknown outcome")
        
        # Warning flags from metadata
        warnings_section = ""
        if metadata.get("warning_flags"):
            warnings_section = "\nWARNINGS\n--------\n"
            for flag in metadata["warning_flags"]:
                warnings_section += f"• {flag}\n"
        
        # Build report
        report = f"""
{disclaimer}

SCENARIO ANALYSIS REPORT
========================

Input Scenario: "{metadata.get('scenario_type', 'generic')}" with {initial_trust:.1f} initial trust
Validation: {validation_icon} {'PASSED' if all_valid else 'WARNINGS PRESENT'}
{warnings_section}
KEY RESULTS
-----------
• Final Outcome: {outcome_text}
• Active Agents: {result.final_active_agents}/5
• Final Phase: {result.final_phase}
• System Functionality: {result.final_functionality:.1%}
• Early Defections (Phase 0-5): {result.early_defections}
• Late Defections (Phase 6+): {result.late_defections}
• Total Investment: €{result.total_investment:.1f}B
• Total Revenue: €{result.total_revenue:.1f}B

MODEL LIMITATIONS (REQUIRED)
----------------------------
• This is exploratory analysis, not prediction
• Results depend on specified assumptions about trust and shocks
• Structural uncertainty (behavioral rules) not quantified
• Calibration ≠ Validation (see STRUCTURAL_ASSUMPTIONS.md)

RECOMMENDED NEXT STEPS
----------------------
1. Run formal verification tests (pytest test_selene_integrated.py)
2. Consult domain experts before application
3. Document assumptions for stakeholder review
4. Review CONDITIONS_OF_USE.md before sharing

Generated by Project Selene ABM v2.1 • {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        return report.strip()
    
    def run_scenario(
        self, 
        natural_language: str, 
        seed: int = 42
    ) -> Tuple[SimulationResult, str]:
        """
        Convenience method: parse, run, and generate report in one call.
        
        Args:
            natural_language: Free-text scenario description
            seed: Random seed for reproducibility
        
        Returns:
            Tuple of (SimulationResult, report_string)
        """
        config, metadata = self.parse_scenario(natural_language)
        
        sim = ConsortiumSimulator(config, seed=seed)
        result = sim.run_single(0)
        
        report = self.generate_report(result, metadata, config)
        
        return result, report
