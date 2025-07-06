"""Flow composition analysis and introspection tools.

This module provides tools for analyzing Flow compositions, generating visualizations,
and understanding the structure and behavior of complex Flow pipelines.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
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

    @property
    def depth(self) -> int:
        """Calculate maximum depth of the graph."""
        if not self.nodes:
            return 0

        # Find longest path from entry to exit
        max_depth = 0
        for entry_id in self.entry_points:
            depth = self._calculate_depth_from_node(entry_id, set())
            max_depth = max(max_depth, depth)

        return max_depth

    def _calculate_depth_from_node(self, node_id: str, visited: set[str]) -> int:
        """Calculate depth from a specific node."""
        if node_id in visited or node_id not in self.nodes:
            return 0

        visited.add(node_id)

        # Find outgoing edges
        outgoing_edges = [edge for edge in self.edges if edge.source_id == node_id]

        if not outgoing_edges:
            return 1

        max_child_depth = 0
        for edge in outgoing_edges:
            child_depth = self._calculate_depth_from_node(
                edge.target_id, visited.copy()
            )
            max_child_depth = max(max_child_depth, child_depth)

        return 1 + max_child_depth

    def get_critical_path(self) -> list[str]:
        """Find the critical path (longest path) through the graph."""
        if not self.entry_points:
            return []

        longest_path = []
        max_length = 0

        for entry_id in self.entry_points:
            path = self._find_longest_path_from_node(entry_id, set())
            if len(path) > max_length:
                max_length = len(path)
                longest_path = path

        return longest_path

    def _find_longest_path_from_node(
        self, node_id: str, visited: set[str]
    ) -> list[str]:
        """Find the longest path from a specific node."""
        if node_id in visited or node_id not in self.nodes:
            return []

        visited.add(node_id)

        # Find outgoing edges
        outgoing_edges = [edge for edge in self.edges if edge.source_id == node_id]

        if not outgoing_edges:
            return [node_id]

        longest_child_path: list[str] = []
        for edge in outgoing_edges:
            child_path = self._find_longest_path_from_node(
                edge.target_id, visited.copy()
            )
            if len(child_path) > len(longest_child_path):
                longest_child_path = child_path

        return [node_id] + longest_child_path

    def find_cycles(self) -> list[list[str]]:
        """Find cycles in the graph."""
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node_id: str, path: list[str]) -> None:
            if node_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(node_id)
                cycle = path[cycle_start:]
                cycles.append(cycle)
                return

            if node_id in visited:
                return

            visited.add(node_id)
            rec_stack.add(node_id)

            # Follow outgoing edges
            outgoing_edges = [edge for edge in self.edges if edge.source_id == node_id]
            for edge in outgoing_edges:
                dfs(edge.target_id, path + [edge.target_id])

            rec_stack.remove(node_id)

        for entry_id in self.entry_points:
            if entry_id not in visited:
                dfs(entry_id, [entry_id])

        return cycles

    def to_dict(self) -> AnalysisData:
        """Convert graph to dictionary representation."""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
            "entry_points": self.entry_points,
            "exit_points": self.exit_points,
            "analysis": {
                "complexity_score": self.complexity_score,
                "depth": self.depth,
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "critical_path": self.get_critical_path(),
                "cycles": self.find_cycles(),
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

    def _categorize_flow_type(self, flow: AnyFlow) -> str:
        """Categorize the type of flow based on its name and characteristics."""
        name = flow.name.lower()

        type_keywords = {
            "transformation": ["map", "transform", "convert"],
            "filtering": ["filter", "where", "select"],
            "aggregation": ["batch", "chunk", "group"],
            "selection": ["take", "skip", "limit"],
            "concurrency": ["parallel", "race", "merge"],
            "error_handling": ["retry", "recover", "catch"],
            "timing": ["delay", "timeout", "throttle"],
            "observability": ["log", "debug", "trace", "inspect"],
            "deduplication": ["distinct", "unique", "memoize"],
        }

        for flow_type, keywords in type_keywords.items():
            if any(keyword in name for keyword in keywords):
                return flow_type

        return "utility"

    def _calculate_complexity(self, flow: AnyFlow) -> int:
        """Calculate complexity score for a flow."""
        base_complexity = 1
        name = flow.name.lower()

        complexity_additions = {
            3: ["parallel", "race", "merge", "branch"],
            2: ["retry", "circuit_breaker", "recover", "flat_map", "expand", "window"],
            1: ["batch", "chunk", "scan"],
        }

        for addition, keywords in complexity_additions.items():
            if any(keyword in name for keyword in keywords):
                base_complexity += addition
                break

        return base_complexity

    def _create_flow_node(self, flow: AnyFlow, node_id: str) -> FlowNode:
        """Create a FlowNode from a Flow object."""
        flow_type = self._categorize_flow_type(flow)
        complexity = self._calculate_complexity(flow)

        return FlowNode(
            id=node_id,
            name=flow.name,
            flow_type=flow_type,
            complexity_score=complexity,
            metadata={
                "signature": self._get_flow_signature(flow),
                "has_metadata": hasattr(flow, "metadata") and bool(flow.metadata),
            },
        )

    def analyze_flow(self, flow: AnyFlow) -> FlowGraph:
        """Analyze a single Flow and return its graph representation."""
        graph = FlowGraph()

        node_id = self._generate_node_id()
        node = self._create_flow_node(flow, node_id)

        graph.nodes[node_id] = node
        graph.entry_points = [node_id]
        graph.exit_points = [node_id]

        return graph

    def _extract_description(self, flow: AnyFlow) -> str | None:
        """Extract description from flow function docstring."""
        if hasattr(flow, "_flow"):
            flow_attr = getattr(flow, "_flow", None)
            if flow_attr and hasattr(flow_attr, "__doc__"):
                docstring = getattr(flow_attr, "__doc__", None)
                if docstring and isinstance(docstring, str):
                    # Return first line of docstring
                    return str(docstring.strip().split("\n")[0])
        return None

    def analyze_composition(self, flows: FlowList) -> FlowGraph:
        """Analyze a composition of multiple flows."""
        graph = FlowGraph()

        if not flows:
            return graph

        # Create nodes for each flow
        node_ids: list[str] = []
        for flow in flows:
            node_id = self._generate_node_id()
            node = self._create_flow_node(flow, node_id)
            graph.nodes[node_id] = node
            node_ids.append(node_id)

        # Create edges between consecutive flows
        for i in range(len(node_ids) - 1):
            edge = FlowEdge(
                source_id=node_ids[i], target_id=node_ids[i + 1], edge_type="sequential"
            )
            graph.edges.append(edge)

        # Set entry and exit points
        graph.entry_points = [node_ids[0]]
        graph.exit_points = [node_ids[-1]]

        return graph

    def detect_patterns(self, graph: FlowGraph) -> PatternList:
        """Detect common patterns in the flow graph."""
        patterns: PatternList = []

        # Detect map-filter pattern
        map_filter_pattern = self._detect_map_filter_pattern(graph)
        if map_filter_pattern:
            patterns.append(map_filter_pattern)

        # Detect fan-out pattern
        fan_out_pattern = self._detect_fan_out_pattern(graph)
        if fan_out_pattern:
            patterns.append(fan_out_pattern)

        # Detect pipeline pattern
        pipeline_pattern = self._detect_pipeline_pattern(graph)
        if pipeline_pattern:
            patterns.append(pipeline_pattern)

        # Detect error handling pattern
        error_handling_pattern = self._detect_error_handling_pattern(graph)
        if error_handling_pattern:
            patterns.append(error_handling_pattern)

        return patterns

    def _detect_map_filter_pattern(self, graph: FlowGraph) -> PatternData | None:
        """Detect map-filter sequential pattern."""
        for edge in graph.edges:
            source_node = graph.nodes.get(edge.source_id)
            target_node = graph.nodes.get(edge.target_id)

            if (
                source_node
                and target_node
                and source_node.flow_type == "transformation"
                and target_node.flow_type == "filtering"
            ):
                return {
                    "pattern": "map_filter",
                    "description": "Transformation followed by filtering",
                    "nodes": [source_node.id, target_node.id],
                    "optimization_hint": "Consider combining map and filter operations for efficiency",
                }
        return None

    def _detect_fan_out_pattern(self, graph: FlowGraph) -> PatternData | None:
        """Detect fan-out pattern (one node with multiple outputs)."""
        for node_id, node in graph.nodes.items():
            outgoing_edges = [edge for edge in graph.edges if edge.source_id == node_id]

            if len(outgoing_edges) > 2:
                return {
                    "pattern": "fan_out",
                    "description": f"Node '{node.name}' fans out to {len(outgoing_edges)} targets",
                    "nodes": [node_id] + [edge.target_id for edge in outgoing_edges],
                    "complexity_impact": "High - multiple parallel execution paths",
                }
        return None

    def _detect_pipeline_pattern(self, graph: FlowGraph) -> PatternData | None:
        """Detect linear pipeline pattern."""
        if len(graph.entry_points) == 1 and len(graph.exit_points) == 1:
            critical_path = graph.get_critical_path()

            if len(critical_path) >= 3:  # At least 3 nodes in sequence
                return {
                    "pattern": "linear_pipeline",
                    "description": f"Linear pipeline with {len(critical_path)} stages",
                    "nodes": critical_path,
                    "performance_characteristic": "Sequential processing, limited parallelism",
                }
        return None

    def _detect_error_handling_pattern(self, graph: FlowGraph) -> PatternData | None:
        """Detect error handling patterns."""
        error_handling_nodes = [
            node for node in graph.nodes.values() if node.flow_type == "error_handling"
        ]

        if error_handling_nodes:
            return {
                "pattern": "error_handling",
                "description": f"Pipeline includes {len(error_handling_nodes)} error handling stage(s)",
                "nodes": [node.id for node in error_handling_nodes],
                "reliability_impact": "High - improved fault tolerance",
            }
        return None

    def _find_sequential_transformations(self, graph: FlowGraph) -> list[str]:
        """Find sequences of transformation nodes."""
        transformation_sequences: list[str] = []

        for node_id, node in graph.nodes.items():
            if node.flow_type == "transformation":
                # Check if this transformation is followed by another transformation
                outgoing_edges = [
                    edge for edge in graph.edges if edge.source_id == node_id
                ]
                for edge in outgoing_edges:
                    target_node = graph.nodes.get(edge.target_id)
                    if target_node and target_node.flow_type == "transformation":
                        transformation_sequences.extend([node_id, target_node.id])

        return list(set(transformation_sequences))

    def generate_optimization_suggestions(self, graph: FlowGraph) -> OptimizationList:
        """Generate optimization suggestions for the flow graph."""
        suggestions: OptimizationList = []

        # Suggest parallel processing opportunities
        sequential_transformations = self._find_sequential_transformations(graph)
        if len(sequential_transformations) > 1:
            suggestions.append(
                {
                    "type": "parallelization",
                    "description": "Multiple sequential transformations could be parallelized",
                    "affected_nodes": sequential_transformations,
                    "potential_benefit": "Reduced latency through parallel execution",
                }
            )

        # Suggest batching opportunities
        if graph.complexity_score > 10:
            suggestions.append(
                {
                    "type": "batching",
                    "description": "High complexity pipeline could benefit from batching",
                    "potential_benefit": "Improved throughput for large datasets",
                }
            )

        # Suggest caching opportunities
        expensive_nodes = [
            node.id for node in graph.nodes.values() if node.complexity_score >= 3
        ]
        if expensive_nodes:
            suggestions.append(
                {
                    "type": "caching",
                    "description": "Expensive operations could benefit from caching",
                    "affected_nodes": expensive_nodes,
                    "potential_benefit": "Reduced computation for repeated inputs",
                }
            )

        return suggestions

    def export_analysis(self, graph: FlowGraph, filepath: str) -> None:
        """Export comprehensive flow analysis to JSON file."""
        patterns = self.detect_patterns(graph)
        optimizations = self.generate_optimization_suggestions(graph)

        graph_dict = graph.to_dict()
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "graph": graph_dict,
            "patterns": patterns,
            "optimization_suggestions": optimizations,
            "summary": {
                "total_nodes": len(graph.nodes),
                "total_edges": len(graph.edges),
                "complexity_score": graph.complexity_score,
                "depth": graph.depth,
                "has_cycles": bool(graph.find_cycles()),
                "patterns_detected": len(patterns),
                "optimization_opportunities": len(optimizations),
            },
        }

        with open(filepath, "w") as f:
            json.dump(analysis_data, f, indent=2)


# Global analyzer instance
_flow_analyzer = FlowAnalyzer()


def analyze_flow(flow: AnyFlow) -> FlowGraph:
    """Analyze a single Flow and return its graph representation."""
    return _flow_analyzer.analyze_flow(flow)


def analyze_flow_composition(flows: FlowList) -> FlowGraph:
    """Analyze a composition of multiple flows."""
    return _flow_analyzer.analyze_composition(flows)


def detect_flow_patterns(graph: FlowGraph) -> PatternList:
    """Detect common patterns in a flow graph."""
    return _flow_analyzer.detect_patterns(graph)


def generate_flow_optimizations(graph: FlowGraph) -> OptimizationList:
    """Generate optimization suggestions for a flow graph."""
    return _flow_analyzer.generate_optimization_suggestions(graph)


def export_flow_analysis(graph: FlowGraph, filepath: str) -> None:
    """Export comprehensive flow analysis to JSON file."""
    _flow_analyzer.export_analysis(graph, filepath)


def get_flow_analyzer() -> FlowAnalyzer:
    """Get the global flow analyzer instance."""
    return _flow_analyzer


def find_cycles(graph: FlowGraph) -> list[list[str]]:
    """Find cycles in a flow graph.

    Args:
        graph: The flow graph to analyze

    Returns:
        List of cycles, where each cycle is a list of node IDs
    """
    return graph.find_cycles()


def calculate_dependencies(graph: FlowGraph) -> dict[str, list[str]]:
    """Calculate dependency relationships between nodes in the graph.

    Args:
        graph: The flow graph to analyze

    Returns:
        Dictionary mapping node_id to list of dependency node_ids
    """
    dependencies: dict[str, list[str]] = {}

    # Initialize all nodes with empty dependencies
    for node_id in graph.nodes:
        dependencies[node_id] = []

    # For each node, find all nodes that have incoming edges (dependencies)
    for edge in graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id

        # target_id depends on source_id
        if target_id in dependencies:
            dependencies[target_id].append(source_id)

    return dependencies


def visualize_flow_graph(graph: FlowGraph, output_format: str = "dot") -> str:
    """Generate a visual representation of the flow graph.

    Args:
        graph: The flow graph to visualize
        output_format: Output format ("dot", "json")

    Returns:
        String representation of the graph in the specified format
    """
    if output_format == "dot":
        return _generate_dot_visualization(graph)
    elif output_format == "json":
        return _generate_json_visualization(graph)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def _generate_dot_visualization(graph: FlowGraph) -> str:
    """Generate DOT format visualization."""
    lines = ["digraph FlowGraph {", "  rankdir=TB;", "  node [shape=box];", ""]

    # Add nodes
    for node_id, node in graph.nodes.items():
        label = f"{node.name} ({node.flow_type})"
        lines.append(f'  "{node_id}" [label="{label}"];')

    lines.append("")

    # Add edges
    for edge in graph.edges:
        lines.append(f'  "{edge.source_id}" -> "{edge.target_id}";')

    lines.append("}")
    return "\n".join(lines)


def _generate_json_visualization(graph: FlowGraph) -> str:
    """Generate JSON format visualization."""
    data: dict[str, list[dict[str, str]]] = {
        "nodes": [],
        "edges": [],
    }

    # Add nodes
    for node_id, node in graph.nodes.items():
        data["nodes"].append(
            {
                "id": node_id,
                "label": f"{node.name} ({node.flow_type})",
                "type": node.flow_type,
            }
        )

    # Add edges
    for edge in graph.edges:
        data["edges"].append({"source": edge.source_id, "target": edge.target_id})

    return json.dumps(data, indent=2)
