"""Flow composition analysis and introspection tools.

This module provides tools for analyzing Flow compositions, generating visualizations,
and understanding the structure and behavior of complex Flow pipelines.
"""

from __future__ import annotations

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
