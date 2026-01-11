"""
Dependency Chain module for Project Selene Consortium Simulator v2.0
Handles graph-based technical dependencies and cascade failures.

Core concept from Module.txt:
"No participant controls more than one critical path component"
"Removal of any participant breaks the chain"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
import random


@dataclass
class DependencyNode:
    """
    A single component in the dependency graph.
    
    Example: "european_habitat" requires ["russian_cooling", "indian_power"]
    """
    node_id: str
    name: str
    owner_agent_id: str                     # Which agent controls this
    criticality: float                       # 0-1, importance to overall system
    requires: List[str] = field(default_factory=list)  # Dependencies
    replicability_years: float = 5.0        # Years to rebuild if lost
    replicability_cost: float = 2.0         # €B to rebuild
    functional: bool = True                  # Current status


class DependencyChain:
    """
    Manages the technical dependency graph and cascade logic.
    
    The core insight: asymmetric dependencies mean withdrawal
    doesn't just hurt the leaver—it cascades through the system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.nodes: Dict[str, DependencyNode] = {}
        self.config = config or {}
        
        # Cascade parameters (can be overridden for robustness testing)
        self.coupling_strength = self.config.get("coupling_strength", 0.6)
        self.cascade_threshold = self.config.get("cascade_threshold", 0.4)
        self.max_iterations = self.config.get("max_cascade_iterations", 10)
    
    def add_node(self, node: DependencyNode):
        """Add a component to the dependency graph."""
        self.nodes[node.node_id] = node
    
    def load_from_config(self, graph_config: List[Dict[str, Any]]):
        """
        Load dependency graph from config file.
        
        Example config:
        [
            {
                "node_id": "european_habitat",
                "name": "Habitat Modules",
                "owner_agent_id": "eu_esa",
                "criticality": 0.9,
                "requires": ["russian_cooling", "indian_power"]
            },
            ...
        ]
        """
        for node_config in graph_config:
            node = DependencyNode(
                node_id=node_config["node_id"],
                name=node_config.get("name", node_config["node_id"]),
                owner_agent_id=node_config["owner_agent_id"],
                criticality=node_config.get("criticality", 0.5),
                requires=node_config.get("requires", []),
                replicability_years=node_config.get("replicability_years", 5.0),
                replicability_cost=node_config.get("replicability_cost", 2.0),
            )
            self.add_node(node)
    
    def get_nodes_by_owner(self, agent_id: str) -> List[DependencyNode]:
        """Get all nodes controlled by an agent."""
        return [n for n in self.nodes.values() if n.owner_agent_id == agent_id]
    
    def withdraw_agent(self, agent_id: str) -> List[str]:
        """
        Mark all nodes owned by agent as non-functional.
        Returns list of affected node IDs.
        """
        affected = []
        for node in self.nodes.values():
            if node.owner_agent_id == agent_id:
                node.functional = False
                affected.append(node.node_id)
        return affected
    
    def propagate_cascade(
        self,
        coupling: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Propagate stress through the dependency graph.
        
        Returns dict of node_id -> stress level (0-1).
        Stress > threshold means node becomes non-functional.
        
        This is the core cascade algorithm from the ODD protocol.
        """
        coupling = coupling if coupling is not None else self.coupling_strength
        threshold = threshold if threshold is not None else self.cascade_threshold
        
        # Initialize stress: non-functional nodes start at 1.0
        stress: Dict[str, float] = {}
        for node_id, node in self.nodes.items():
            stress[node_id] = 1.0 if not node.functional else 0.0
        
        # Propagate stress through dependencies
        for iteration in range(self.max_iterations):
            new_stress = stress.copy()
            changed = False
            
            for node_id, node in self.nodes.items():
                if not node.functional:
                    continue  # Already failed
                
                # Calculate incoming stress from dependencies
                if node.requires:
                    incoming_stress = sum(
                        stress.get(dep, 0.0) * coupling
                        for dep in node.requires
                    ) / len(node.requires)
                    
                    # Stress accumulates
                    new_stress[node_id] = min(1.0, stress[node_id] + incoming_stress)
                    
                    # Check if stress exceeds threshold
                    if new_stress[node_id] > threshold and node.functional:
                        node.functional = False
                        new_stress[node_id] = 1.0
                        changed = True
            
            stress = new_stress
            if not changed:
                break  # Converged
        
        return stress
    
    def calculate_system_functionality(self) -> float:
        """
        Calculate overall system functionality (0-1).
        
        Weighted by criticality: losing high-criticality nodes hurts more.
        """
        if not self.nodes:
            return 1.0
        
        total_criticality = sum(n.criticality for n in self.nodes.values())
        if total_criticality == 0:
            return 1.0
        
        functional_criticality = sum(
            n.criticality for n in self.nodes.values() if n.functional
        )
        
        return functional_criticality / total_criticality
    
    def get_critical_path(self) -> List[str]:
        """
        Identify the critical path (nodes with no redundancy).
        These are single points of failure.
        """
        critical = []
        for node_id, node in self.nodes.items():
            # A node is critical if:
            # 1. High criticality
            # 2. Something depends on it
            # 3. No alternative source
            dependents = [
                n for n in self.nodes.values()
                if node_id in n.requires
            ]
            if node.criticality > 0.7 and dependents:
                critical.append(node_id)
        return critical
    
    def simulate_withdrawal_impact(self, agent_id: str) -> Dict[str, Any]:
        """
        Simulate what happens if an agent withdraws.
        Non-destructive: creates a copy for analysis.
        
        Returns impact assessment.
        """
        # Store original states
        original_states = {
            node_id: node.functional
            for node_id, node in self.nodes.items()
        }
        original_functionality = self.calculate_system_functionality()
        
        # Simulate withdrawal
        directly_lost = self.withdraw_agent(agent_id)
        stress = self.propagate_cascade()
        
        # Assess impact
        cascade_failures = [
            node_id for node_id, node in self.nodes.items()
            if not node.functional and node_id not in directly_lost
        ]
        final_functionality = self.calculate_system_functionality()
        
        # Restore original states
        for node_id, was_functional in original_states.items():
            self.nodes[node_id].functional = was_functional
        
        return {
            "agent_id": agent_id,
            "directly_lost": directly_lost,
            "cascade_failures": cascade_failures,
            "total_failures": len(directly_lost) + len(cascade_failures),
            "functionality_before": original_functionality,
            "functionality_after": final_functionality,
            "functionality_loss": original_functionality - final_functionality,
        }
    
    def reset(self):
        """Reset all nodes to functional state."""
        for node in self.nodes.values():
            node.functional = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for output."""
        return {
            "nodes": {
                node_id: {
                    "name": node.name,
                    "owner": node.owner_agent_id,
                    "criticality": node.criticality,
                    "requires": node.requires,
                    "functional": node.functional,
                }
                for node_id, node in self.nodes.items()
            },
            "system_functionality": self.calculate_system_functionality(),
            "critical_path": self.get_critical_path(),
        }


# Default Selene dependency graph
# Can be overridden by config file
DEFAULT_SELENE_GRAPH = [
    # European components
    {
        "node_id": "european_habitat",
        "name": "Habitat Modules (Airbus/Thales)",
        "owner_agent_id": "eu_esa",
        "criticality": 0.9,
        "requires": ["russian_cooling", "japanese_airlocks"],
    },
    {
        "node_id": "european_comms",
        "name": "MoonLight Constellation",
        "owner_agent_id": "eu_esa",
        "criticality": 0.7,
        "requires": [],
    },
    {
        "node_id": "european_robotics",
        "name": "Precision Robotics",
        "owner_agent_id": "eu_esa",
        "criticality": 0.6,
        "requires": ["indian_software"],
    },
    
    # Russian components
    {
        "node_id": "russian_transport",
        "name": "Crew Transport (Yenisei)",
        "owner_agent_id": "russia_roscosmos",
        "criticality": 0.85,
        "requires": [],
    },
    {
        "node_id": "russian_cooling",
        "name": "Cooling Fluid Systems",
        "owner_agent_id": "russia_roscosmos",
        "criticality": 0.75,
        "requires": ["chinese_rare_earths"],
    },
    {
        "node_id": "russian_isru",
        "name": "ISRU Drilling Equipment",
        "owner_agent_id": "russia_roscosmos",
        "criticality": 0.8,
        "requires": [],
    },
    
    # Chinese components
    {
        "node_id": "chinese_heavylift",
        "name": "Long March 9/10",
        "owner_agent_id": "china_cnsa",
        "criticality": 0.9,
        "requires": [],
    },
    {
        "node_id": "chinese_power",
        "name": "Nuclear Surface Power",
        "owner_agent_id": "china_cnsa",
        "criticality": 0.85,
        "requires": [],
    },
    {
        "node_id": "chinese_rare_earths",
        "name": "Rare Earth Processing",
        "owner_agent_id": "china_cnsa",
        "criticality": 0.7,
        "requires": [],
    },
    
    # Indian components
    {
        "node_id": "indian_logistics",
        "name": "Cost-Efficient Logistics (LVM3)",
        "owner_agent_id": "india_isro",
        "criticality": 0.6,
        "requires": [],
    },
    {
        "node_id": "indian_software",
        "name": "AI/Autonomy Software",
        "owner_agent_id": "india_isro",
        "criticality": 0.65,
        "requires": [],
    },
    {
        "node_id": "indian_landing",
        "name": "Precision Landing Tech",
        "owner_agent_id": "india_isro",
        "criticality": 0.7,
        "requires": [],
    },
    
    # Japanese components
    {
        "node_id": "japanese_rovers",
        "name": "Pressurized Rovers (Toyota)",
        "owner_agent_id": "japan_jaxa",
        "criticality": 0.65,
        "requires": ["european_robotics"],
    },
    {
        "node_id": "japanese_airlocks",
        "name": "High-Precision Airlocks",
        "owner_agent_id": "japan_jaxa",
        "criticality": 0.75,
        "requires": [],
    },
    
    # Ukraine components (Track A)
    {
        "node_id": "ukraine_aerospace",
        "name": "Aerospace Components (Yuzhnoye)",
        "owner_agent_id": "ukraine_ssau",
        "criticality": 0.55,
        "requires": [],
    },
    {
        "node_id": "ukraine_integration",
        "name": "Systems Integration",
        "owner_agent_id": "ukraine_ssau",
        "criticality": 0.6,
        "requires": ["indian_software"],
    },
]


def create_selene_dependency_chain(config: Optional[Dict[str, Any]] = None) -> DependencyChain:
    """Factory function to create default Selene dependency graph."""
    chain = DependencyChain(config)
    chain.load_from_config(DEFAULT_SELENE_GRAPH)
    return chain
