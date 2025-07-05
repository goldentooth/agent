"""Flow composition analysis and introspection tools.

This module provides tools for analyzing Flow compositions, generating visualizations,
and understanding the structure and behavior of complex Flow pipelines.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from ..flow import Flow

# Type aliases for flow analysis
FlowMetadata = dict[str, Any]
AnalysisData = dict[str, Any]
PatternData = dict[str, Any]
OptimizationData = dict[str, Any]
AnyFlow = Flow[Any, Any]
FlowList = list[AnyFlow]
PatternList = list[PatternData]
OptimizationList = list[OptimizationData]
FlowRegistry = dict[str, AnyFlow]


@dataclass
class FlowNode:
    """Represents a node in a Flow composition graph."""

    id: str
    name: str
    flow_type: str
    description: str | None = None
    metadata: FlowMetadata = field(default_factory=lambda: {})
    inputs: list[str] = field(default_factory=lambda: [])
    outputs: list[str] = field(default_factory=lambda: [])
    complexity_score: int = 1

    def to_dict(self) -> AnalysisData:
        """Convert node to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "flow_type": self.flow_type,
            "description": self.description,
            "metadata": self.metadata,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "complexity_score": self.complexity_score,
        }


@dataclass
class FlowEdge:
    """Represents an edge (connection) between Flow nodes."""

    source_id: str
    target_id: str
    edge_type: str = "data_flow"
    metadata: FlowMetadata = field(default_factory=lambda: {})

    def to_dict(self) -> AnalysisData:
        """Convert edge to dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "metadata": self.metadata,
        }


@dataclass
class FlowGraph:
    """Represents a complete Flow composition as a directed graph."""

    nodes: dict[str, FlowNode] = field(default_factory=lambda: {})
    edges: list[FlowEdge] = field(default_factory=lambda: [])
    entry_points: list[str] = field(default_factory=lambda: [])
    exit_points: list[str] = field(default_factory=lambda: [])

    @property
    def complexity_score(self) -> int:
        """Calculate total complexity score of the graph."""
        return sum(node.complexity_score for node in self.nodes.values())

    def to_dict(self) -> AnalysisData:
        """Convert graph to dictionary representation."""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
            "entry_points": self.entry_points,
            "exit_points": self.exit_points,
            "analysis": {
                "complexity_score": self.complexity_score,
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
            },
        }


class FlowAnalyzer:
    """Analyzer for Flow compositions and structures."""

    def __init__(self) -> None:
        """Initialize the FlowAnalyzer."""
        super().__init__()
        self.node_id_counter = 0
        self.flow_registry: FlowRegistry = {}

    def _generate_node_id(self) -> str:
        """Generate a unique node ID."""
        self.node_id_counter += 1
        return f"node_{self.node_id_counter}"

    def _get_flow_signature(self, flow: AnyFlow) -> str:
        """Generate a signature for a flow based on its properties."""
        components = [flow.name, str(type(flow)), str(getattr(flow, "metadata", {}))]
        signature = hashlib.md5(
            "|".join(components).encode(), usedforsecurity=False
        ).hexdigest()[:8]
        return signature
