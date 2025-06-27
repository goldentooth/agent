"""Flow composition analysis and introspection tools.

This module provides tools for analyzing Flow compositions, generating visualizations,
and understanding the structure and behavior of complex Flow pipelines.
"""

from __future__ import annotations
import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set, Tuple
from collections import defaultdict, deque
import hashlib

from .main import Flow


@dataclass
class FlowNode:
    """Represents a node in a Flow composition graph."""

    id: str
    name: str
    flow_type: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    complexity_score: int = 1

    def to_dict(self) -> Dict[str, Any]:
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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

    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    edges: List[FlowEdge] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    exit_points: List[str] = field(default_factory=list)

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

    def _calculate_depth_from_node(self, node_id: str, visited: Set[str]) -> int:
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

    def get_critical_path(self) -> List[str]:
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
        self, node_id: str, visited: Set[str]
    ) -> List[str]:
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

    def find_cycles(self) -> List[List[str]]:
        """Find cycles in the graph."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node_id: str, path: List[str]) -> None:
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

    def to_dict(self) -> Dict[str, Any]:
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
        self.node_id_counter = 0
        self.flow_registry: Dict[str, Flow[Any, Any]] = {}

    def _generate_node_id(self) -> str:
        """Generate a unique node ID."""
        self.node_id_counter += 1
        return f"node_{self.node_id_counter}"

    def _get_flow_signature(self, flow: Flow[Any, Any]) -> str:
        """Generate a signature for a flow based on its properties."""
        components = [flow.name, str(type(flow)), str(getattr(flow, "metadata", {}))]
        signature = hashlib.md5("|".join(components).encode()).hexdigest()[:8]
        return signature

    def analyze_flow(self, flow: Flow[Any, Any]) -> FlowGraph:
        """Analyze a single Flow and return its graph representation."""
        graph = FlowGraph()

        # Create a node for the flow
        node_id = self._generate_node_id()
        node = self._create_flow_node(flow, node_id)

        graph.nodes[node_id] = node
        graph.entry_points = [node_id]
        graph.exit_points = [node_id]

        return graph

    def analyze_composition(self, flows: List[Flow[Any, Any]]) -> FlowGraph:
        """Analyze a composition of multiple flows."""
        graph = FlowGraph()

        if not flows:
            return graph

        # Create nodes for each flow
        node_ids = []
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

    def _create_flow_node(self, flow: Flow[Any, Any], node_id: str) -> FlowNode:
        """Create a FlowNode from a Flow object."""
        flow_type = self._categorize_flow_type(flow)
        complexity = self._calculate_complexity(flow)
        description = self._extract_description(flow)

        return FlowNode(
            id=node_id,
            name=flow.name,
            flow_type=flow_type,
            description=description,
            complexity_score=complexity,
            metadata={
                "signature": self._get_flow_signature(flow),
                "has_metadata": hasattr(flow, "metadata") and bool(flow.metadata),
            },
        )

    def _categorize_flow_type(self, flow: Flow[Any, Any]) -> str:
        """Categorize the type of flow based on its name and characteristics."""
        name = flow.name.lower()

        if any(term in name for term in ["map", "transform", "convert"]):
            return "transformation"
        elif any(term in name for term in ["filter", "where", "select"]):
            return "filtering"
        elif any(term in name for term in ["batch", "chunk", "group"]):
            return "aggregation"
        elif any(term in name for term in ["take", "skip", "limit"]):
            return "selection"
        elif any(term in name for term in ["parallel", "race", "merge"]):
            return "concurrency"
        elif any(term in name for term in ["retry", "recover", "catch"]):
            return "error_handling"
        elif any(term in name for term in ["delay", "timeout", "throttle"]):
            return "timing"
        elif any(term in name for term in ["log", "debug", "trace", "inspect"]):
            return "observability"
        elif any(term in name for term in ["distinct", "unique", "memoize"]):
            return "deduplication"
        else:
            return "utility"

    def _calculate_complexity(self, flow: Flow[Any, Any]) -> int:
        """Calculate complexity score for a flow."""
        base_complexity = 1
        name = flow.name.lower()

        # Add complexity based on operation type
        if any(term in name for term in ["parallel", "race", "merge", "branch"]):
            base_complexity += 3  # Concurrency operations are complex
        elif any(term in name for term in ["retry", "circuit_breaker", "recover"]):
            base_complexity += 2  # Error handling adds complexity
        elif any(term in name for term in ["flat_map", "expand", "window"]):
            base_complexity += 2  # Stream manipulation is complex
        elif any(term in name for term in ["batch", "chunk", "scan"]):
            base_complexity += 1  # Aggregation operations

        return base_complexity

    def _extract_description(self, flow: Flow[Any, Any]) -> Optional[str]:
        """Extract description from flow function docstring."""
        if hasattr(flow, "_flow") and hasattr(flow._flow, "__doc__"):
            docstring = flow._flow.__doc__
            if docstring and isinstance(docstring, str):
                # Return first line of docstring
                return str(docstring.strip().split("\n")[0])
        return None

    def detect_patterns(self, graph: FlowGraph) -> List[Dict[str, Any]]:
        """Detect common patterns in the flow graph."""
        patterns = []

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

    def _detect_map_filter_pattern(self, graph: FlowGraph) -> Optional[Dict[str, Any]]:
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

    def _detect_fan_out_pattern(self, graph: FlowGraph) -> Optional[Dict[str, Any]]:
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

    def _detect_pipeline_pattern(self, graph: FlowGraph) -> Optional[Dict[str, Any]]:
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

    def _detect_error_handling_pattern(
        self, graph: FlowGraph
    ) -> Optional[Dict[str, Any]]:
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

    def generate_optimization_suggestions(
        self, graph: FlowGraph
    ) -> List[Dict[str, Any]]:
        """Generate optimization suggestions for the flow graph."""
        suggestions = []

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
            node.id for node in graph.nodes.values() if node.complexity_score > 3
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

    def _find_sequential_transformations(self, graph: FlowGraph) -> List[str]:
        """Find sequences of transformation nodes."""
        transformation_sequences = []

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

    def export_analysis(self, graph: FlowGraph, filepath: str) -> None:
        """Export comprehensive flow analysis to JSON file."""
        patterns = self.detect_patterns(graph)
        optimizations = self.generate_optimization_suggestions(graph)

        analysis_data = {
            "timestamp": str(graph.to_dict().get("timestamp", "unknown")),
            "graph": graph.to_dict(),
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


def analyze_flow(flow: Flow[Any, Any]) -> FlowGraph:
    """Analyze a single Flow and return its graph representation."""
    return _flow_analyzer.analyze_flow(flow)


def analyze_flow_composition(flows: List[Flow[Any, Any]]) -> FlowGraph:
    """Analyze a composition of multiple flows."""
    return _flow_analyzer.analyze_composition(flows)


def detect_flow_patterns(graph: FlowGraph) -> List[Dict[str, Any]]:
    """Detect common patterns in a flow graph."""
    return _flow_analyzer.detect_patterns(graph)


def generate_flow_optimizations(graph: FlowGraph) -> List[Dict[str, Any]]:
    """Generate optimization suggestions for a flow graph."""
    return _flow_analyzer.generate_optimization_suggestions(graph)


def export_flow_analysis(graph: FlowGraph, filepath: str) -> None:
    """Export comprehensive flow analysis to JSON file."""
    _flow_analyzer.export_analysis(graph, filepath)


def get_flow_analyzer() -> FlowAnalyzer:
    """Get the global flow analyzer instance."""
    return _flow_analyzer
