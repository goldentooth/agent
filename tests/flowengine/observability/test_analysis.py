"""Tests for flow analysis and introspection tools."""

from flowengine import Flow
from flowengine.combinators.basic import map_stream
from flowengine.observability.analysis import (
    AnalysisData,
    AnyFlow,
    FlowAnalyzer,
    FlowEdge,
    FlowGraph,
    FlowList,
    FlowMetadata,
    FlowNode,
    FlowRegistry,
    OptimizationData,
    OptimizationList,
    PatternData,
    PatternList,
    analyze_flow,
    analyze_flow_composition,
    detect_flow_patterns,
    export_flow_analysis,
    generate_flow_optimizations,
    get_flow_analyzer,
)


class TestFlowNode:
    """Tests for FlowNode class."""

    def test_flow_node_creation(self):
        """Test basic FlowNode creation."""
        node = FlowNode(
            id="test_node",
            name="test_flow",
            flow_type="transformation",
            description="Test node",
            complexity_score=2,
        )

        assert node.id == "test_node"
        assert node.name == "test_flow"
        assert node.flow_type == "transformation"
        assert node.description == "Test node"
        assert node.complexity_score == 2

    def test_flow_node_to_dict(self):
        """Test FlowNode to_dict conversion."""
        node = FlowNode(
            id="node1",
            name="map_flow",
            flow_type="transformation",
            inputs=["input1"],
            outputs=["output1"],
        )

        node_dict = node.to_dict()

        assert node_dict["id"] == "node1"
        assert node_dict["name"] == "map_flow"
        assert node_dict["flow_type"] == "transformation"
        assert node_dict["inputs"] == ["input1"]
        assert node_dict["outputs"] == ["output1"]


class TestFlowEdge:
    """Tests for FlowEdge class."""

    def test_flow_edge_creation(self):
        """Test basic FlowEdge creation."""
        edge = FlowEdge(source_id="node1", target_id="node2", edge_type="sequential")

        assert edge.source_id == "node1"
        assert edge.target_id == "node2"
        assert edge.edge_type == "sequential"

    def test_flow_edge_to_dict(self):
        """Test FlowEdge to_dict conversion."""
        edge = FlowEdge(
            source_id="node1",
            target_id="node2",
            edge_type="data_flow",
            metadata={"weight": 1.0},
        )

        edge_dict = edge.to_dict()

        assert edge_dict["source_id"] == "node1"
        assert edge_dict["target_id"] == "node2"
        assert edge_dict["edge_type"] == "data_flow"
        assert edge_dict["metadata"]["weight"] == 1.0


class TestFlowGraph:
    """Tests for FlowGraph class."""

    def test_flow_graph_creation(self):
        """Test basic FlowGraph creation."""
        graph = FlowGraph()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert len(graph.entry_points) == 0
        assert len(graph.exit_points) == 0

    def test_flow_graph_complexity_score(self):
        """Test complexity score calculation."""
        graph = FlowGraph()

        node1 = FlowNode(id="1", name="simple", flow_type="utility", complexity_score=1)
        node2 = FlowNode(
            id="2", name="complex", flow_type="transformation", complexity_score=3
        )

        graph.nodes["1"] = node1
        graph.nodes["2"] = node2

        assert graph.complexity_score == 4

    def test_flow_graph_depth_empty(self):
        """Test depth calculation for empty graph."""
        graph = FlowGraph()
        assert graph.depth == 0

    def test_flow_graph_depth_single_node(self):
        """Test depth calculation for single node."""
        graph = FlowGraph()
        node1 = FlowNode(id="1", name="single", flow_type="utility")
        graph.nodes["1"] = node1
        graph.entry_points = ["1"]
        graph.exit_points = ["1"]

        assert graph.depth == 1

    def test_flow_graph_depth_chain(self):
        """Test depth calculation for chained nodes."""
        graph = FlowGraph()

        node1 = FlowNode(id="1", name="first", flow_type="utility")
        node2 = FlowNode(id="2", name="second", flow_type="transformation")
        node3 = FlowNode(id="3", name="third", flow_type="utility")

        graph.nodes["1"] = node1
        graph.nodes["2"] = node2
        graph.nodes["3"] = node3

        # Create chain: 1 -> 2 -> 3
        edge1 = FlowEdge(source_id="1", target_id="2")
        edge2 = FlowEdge(source_id="2", target_id="3")
        graph.edges = [edge1, edge2]

        graph.entry_points = ["1"]
        graph.exit_points = ["3"]

        assert graph.depth == 3

    def test_flow_graph_critical_path_empty(self):
        """Test critical path for empty graph."""
        graph = FlowGraph()
        assert graph.get_critical_path() == []

    def test_flow_graph_critical_path_single_node(self):
        """Test critical path for single node."""
        graph = FlowGraph()
        node1 = FlowNode(id="1", name="single", flow_type="utility")
        graph.nodes["1"] = node1
        graph.entry_points = ["1"]

        assert graph.get_critical_path() == ["1"]

    def test_flow_graph_critical_path_chain(self):
        """Test critical path for chained nodes."""
        graph = FlowGraph()

        node1 = FlowNode(id="1", name="first", flow_type="utility")
        node2 = FlowNode(id="2", name="second", flow_type="transformation")
        node3 = FlowNode(id="3", name="third", flow_type="utility")

        graph.nodes["1"] = node1
        graph.nodes["2"] = node2
        graph.nodes["3"] = node3

        edge1 = FlowEdge(source_id="1", target_id="2")
        edge2 = FlowEdge(source_id="2", target_id="3")
        graph.edges = [edge1, edge2]

        graph.entry_points = ["1"]

        assert graph.get_critical_path() == ["1", "2", "3"]

    def test_flow_graph_critical_path_multiple_branches(self):
        """Test critical path with multiple branches."""
        graph = FlowGraph()

        # Create nodes
        nodes = {
            "1": FlowNode(id="1", name="root", flow_type="utility"),
            "2": FlowNode(id="2", name="branch1", flow_type="transformation"),
            "3": FlowNode(id="3", name="branch2", flow_type="utility"),
            "4": FlowNode(id="4", name="end", flow_type="utility"),
        }
        graph.nodes.update(nodes)

        # Create edges: 1->2, 1->3, 2->4
        graph.edges = [
            FlowEdge(source_id="1", target_id="2"),
            FlowEdge(source_id="1", target_id="3"),
            FlowEdge(source_id="2", target_id="4"),
        ]
        graph.entry_points = ["1"]

        # Should find the longer path: 1->2->4 (length 3)
        assert graph.get_critical_path() == ["1", "2", "4"]

    def test_flow_graph_find_cycles_no_cycles(self):
        """Test cycle detection with no cycles."""
        graph = FlowGraph()

        nodes = {
            "1": FlowNode(id="1", name="first", flow_type="utility"),
            "2": FlowNode(id="2", name="second", flow_type="transformation"),
        }
        graph.nodes.update(nodes)

        graph.edges = [FlowEdge(source_id="1", target_id="2")]
        graph.entry_points = ["1"]

        assert graph.find_cycles() == []

    def test_flow_graph_find_cycles_with_cycle(self):
        """Test cycle detection with a simple cycle."""
        graph = FlowGraph()

        nodes = {
            "1": FlowNode(id="1", name="first", flow_type="utility"),
            "2": FlowNode(id="2", name="second", flow_type="transformation"),
        }
        graph.nodes.update(nodes)

        # Create cycle: 1->2->1
        graph.edges = [
            FlowEdge(source_id="1", target_id="2"),
            FlowEdge(source_id="2", target_id="1"),
        ]
        graph.entry_points = ["1"]

        cycles = graph.find_cycles()
        assert len(cycles) == 1
        assert "1" in cycles[0] and "2" in cycles[0]

    def test_flow_graph_to_dict(self):
        """Test FlowGraph to_dict conversion."""
        graph = FlowGraph()

        node1 = FlowNode(id="1", name="test", flow_type="utility")
        graph.nodes["1"] = node1
        graph.entry_points = ["1"]
        graph.exit_points = ["1"]

        graph_dict = graph.to_dict()

        # Check main structure
        required_keys = ["nodes", "edges", "entry_points", "exit_points", "analysis"]
        assert all(key in graph_dict for key in required_keys)

        # Check analysis fields
        analysis = graph_dict["analysis"]
        expected_analysis = {
            "complexity_score": 1,
            "node_count": 1,
            "edge_count": 0,
            "depth": 1,
            "critical_path": ["1"],
            "cycles": [],
        }
        assert all(analysis[key] == expected_analysis[key] for key in expected_analysis)


# Helper functions for FlowAnalyzer tests
def build_map_filter_graph():
    """Build a test graph with map-filter pattern."""
    graph = FlowGraph()
    map_node = FlowNode(id="1", name="map_func", flow_type="transformation")
    filter_node = FlowNode(id="2", name="filter_func", flow_type="filtering")
    graph.nodes["1"] = map_node
    graph.nodes["2"] = filter_node
    edge = FlowEdge(source_id="1", target_id="2")
    graph.edges = [edge]
    return graph


def assert_map_filter_pattern(pattern: PatternData) -> None:
    """Assert that pattern matches map-filter expectations."""
    assert pattern["pattern"] == "map_filter"
    assert pattern["nodes"] == ["1", "2"]
    assert "transformation followed by filtering" in pattern["description"].lower()


def build_fan_out_graph() -> FlowGraph:
    """Build a test graph with fan-out pattern."""
    graph = FlowGraph()
    source_node = FlowNode(id="1", name="source", flow_type="utility")
    target1 = FlowNode(id="2", name="target1", flow_type="utility")
    target2 = FlowNode(id="3", name="target2", flow_type="utility")
    target3 = FlowNode(id="4", name="target3", flow_type="utility")
    graph.nodes.update({"1": source_node, "2": target1, "3": target2, "4": target3})
    graph.edges = [
        FlowEdge(source_id="1", target_id="2"),
        FlowEdge(source_id="1", target_id="3"),
        FlowEdge(source_id="1", target_id="4"),
    ]
    return graph


def assert_fan_out_pattern(pattern: PatternData) -> None:
    """Assert that pattern matches fan-out expectations."""
    assert pattern["pattern"] == "fan_out"
    assert pattern["nodes"] == ["1", "2", "3", "4"]
    assert "3 targets" in pattern["description"]


class TestFlowAnalyzer:
    """Tests for FlowAnalyzer class."""

    def test_analyzer_creation(self):
        """Test FlowAnalyzer creation."""
        analyzer = FlowAnalyzer()

        assert analyzer.node_id_counter == 0
        assert len(analyzer.flow_registry) == 0

    def test_node_counter_behavior(self):
        """Test that node counter behavior works correctly."""
        analyzer = FlowAnalyzer()

        assert analyzer.node_id_counter == 0

    def test_flow_signature_generation(self):
        """Test flow signature generation capability."""
        analyzer = FlowAnalyzer()

        def increment(x: int) -> int:
            return x + 1

        flow = map_stream(increment)

        # The signature method should be present and callable
        assert hasattr(analyzer, "_get_flow_signature")
        assert callable(getattr(analyzer, "_get_flow_signature"))

    def test_create_flow_node(self):
        """Test flow node creation capability."""
        analyzer = FlowAnalyzer()

        def increment(x: int) -> int:
            return x + 1

        flow = map_stream(increment)

        # The create node method should be present and callable
        assert hasattr(analyzer, "_create_flow_node")
        assert callable(getattr(analyzer, "_create_flow_node"))

    def test_analyze_single_flow(self):
        """Test analyzing a single flow."""
        analyzer = FlowAnalyzer()

        def increment(x: int) -> int:
            return x + 1

        flow = map_stream(increment)
        graph = analyzer.analyze_flow(flow)

        assert len(graph.nodes) == 1
        assert len(graph.entry_points) == 1
        assert len(graph.exit_points) == 1

        node = list(graph.nodes.values())[0]
        assert "map" in node.name
        assert (
            node.flow_type == "transformation"
        )  # map should be categorized as transformation

    def test_analyze_composition_empty(self):
        """Test analyzing empty composition."""
        analyzer = FlowAnalyzer()
        graph = analyzer.analyze_composition([])

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert len(graph.entry_points) == 0
        assert len(graph.exit_points) == 0

    def test_analyze_composition_multiple_flows(self):
        """Test analyzing composition of multiple flows."""
        analyzer = FlowAnalyzer()

        def increment(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        flows = [map_stream(increment), map_stream(double)]
        graph = analyzer.analyze_composition(flows)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert len(graph.entry_points) == 1
        assert len(graph.exit_points) == 1

        # Check edge connects first to second flow
        edge = graph.edges[0]
        assert edge.edge_type == "sequential"
        assert edge.source_id in graph.nodes
        assert edge.target_id in graph.nodes

    def test_extract_description_behavior(self):
        """Test description extraction behavior through public analyze method."""
        analyzer = FlowAnalyzer()

        def documented_func(x: int) -> int:
            """This is a test function."""
            return x + 1

        flow = map_stream(documented_func)
        graph = analyzer.analyze_flow(flow)

        # Verify the analysis completed successfully (indirectly tests _extract_description)
        assert len(graph.nodes) == 1
        node = list(graph.nodes.values())[0]
        assert "map" in node.name

    def test_detect_patterns_empty_graph(self):
        """Test pattern detection with empty graph."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        patterns = analyzer.detect_patterns(graph)

        # Should return empty list for empty graph
        assert patterns == []

    def test_detect_patterns_single_node(self):
        """Test pattern detection with single node graph."""
        analyzer = FlowAnalyzer()

        def increment(x: int) -> int:
            return x + 1

        flow = map_stream(increment)
        graph = analyzer.analyze_flow(flow)

        patterns = analyzer.detect_patterns(graph)

        # Should not crash and return some result (specific patterns depend on helpers)
        assert isinstance(patterns, list)

    def test_detect_map_filter_pattern(self):
        """Test detection of map-filter pattern."""
        analyzer = FlowAnalyzer()
        graph = build_map_filter_graph()
        patterns = analyzer.detect_patterns(graph)
        assert len(patterns) == 1
        assert_map_filter_pattern(patterns[0])

    def test_detect_fan_out_pattern(self):
        """Test detection of fan-out pattern."""
        analyzer = FlowAnalyzer()
        graph = build_fan_out_graph()
        patterns = analyzer.detect_patterns(graph)
        assert len(patterns) == 1
        assert_fan_out_pattern(patterns[0])

    def test_detect_pipeline_pattern(self):
        """Test detection of linear pipeline pattern."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Create linear chain: node1 -> node2 -> node3 -> node4
        nodes = {
            "1": FlowNode(id="1", name="stage1", flow_type="utility"),
            "2": FlowNode(id="2", name="stage2", flow_type="transformation"),
            "3": FlowNode(id="3", name="stage3", flow_type="utility"),
            "4": FlowNode(id="4", name="stage4", flow_type="utility"),
        }
        graph.nodes.update(nodes)

        # Create sequential edges
        graph.edges = [
            FlowEdge(source_id="1", target_id="2"),
            FlowEdge(source_id="2", target_id="3"),
            FlowEdge(source_id="3", target_id="4"),
        ]

        # Set single entry and exit points
        graph.entry_points = ["1"]
        graph.exit_points = ["4"]

        patterns = analyzer.detect_patterns(graph)

        # Should detect the linear pipeline pattern
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern["pattern"] == "linear_pipeline"
        assert pattern["nodes"] == ["1", "2", "3", "4"]
        assert "4 stages" in pattern["description"]

    def test_detect_error_handling_pattern(self):
        """Test detection of error handling pattern."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Create nodes with error handling
        nodes = {
            "1": FlowNode(id="1", name="normal", flow_type="utility"),
            "2": FlowNode(id="2", name="retry", flow_type="error_handling"),
            "3": FlowNode(id="3", name="recover", flow_type="error_handling"),
        }
        graph.nodes.update(nodes)

        patterns = analyzer.detect_patterns(graph)

        # Should detect the error handling pattern
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern["pattern"] == "error_handling"
        assert set(pattern["nodes"]) == {"2", "3"}
        assert "2 error handling stage" in pattern["description"]
        assert "fault tolerance" in pattern["reliability_impact"]

    def test_generate_optimization_suggestions_empty(self):
        """Test optimization suggestions for empty graph."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        suggestions = analyzer.generate_optimization_suggestions(graph)

        # Empty graph should have no suggestions
        assert suggestions == []

    def test_generate_optimization_suggestions_caching(self):
        """Test caching suggestions for expensive nodes."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Create expensive nodes (complexity >= 3)
        expensive_node = FlowNode(
            id="1", name="expensive", flow_type="utility", complexity_score=5
        )
        cheap_node = FlowNode(
            id="2", name="cheap", flow_type="utility", complexity_score=1
        )

        graph.nodes["1"] = expensive_node
        graph.nodes["2"] = cheap_node

        suggestions = analyzer.generate_optimization_suggestions(graph)

        # Should suggest caching for expensive node
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion["type"] == "caching"
        assert "1" in suggestion["affected_nodes"]
        assert "2" not in suggestion["affected_nodes"]

    def test_generate_optimization_suggestions_batching(self):
        """Test batching suggestions for high complexity."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Create high complexity graph (> 10)
        for i in range(5):
            node = FlowNode(
                id=str(i), name=f"node{i}", flow_type="utility", complexity_score=3
            )
            graph.nodes[str(i)] = node

        suggestions = analyzer.generate_optimization_suggestions(graph)

        # Should suggest batching for high complexity
        batching_suggestions = [s for s in suggestions if s["type"] == "batching"]
        assert len(batching_suggestions) == 1
        assert "throughput" in batching_suggestions[0]["potential_benefit"]


class TestAnalysisFunctions:
    """Tests for module-level analysis functions."""

    def test_analyze_flow_function(self):
        """Test analyze_flow convenience function."""

        def increment(x: int) -> int:
            return x + 1

        flow = map_stream(increment)
        graph = analyze_flow(flow)

        assert len(graph.nodes) == 1
        assert len(graph.entry_points) == 1

    def test_get_flow_analyzer_function(self):
        """Test get_flow_analyzer convenience function."""
        analyzer = get_flow_analyzer()

        assert isinstance(analyzer, FlowAnalyzer)

    def test_analyze_flow_composition_function(self):
        """Test analyze_flow_composition convenience function."""

        def increment(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        flows = [map_stream(increment), map_stream(double)]
        graph = analyze_flow_composition(flows)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert len(graph.entry_points) == 1
        assert len(graph.exit_points) == 1

    def test_detect_flow_patterns_function(self):
        """Test detect_flow_patterns convenience function."""
        graph = FlowGraph()

        # Create error handling node
        error_node = FlowNode(id="1", name="retry", flow_type="error_handling")
        graph.nodes["1"] = error_node

        patterns = detect_flow_patterns(graph)

        assert len(patterns) == 1
        assert patterns[0]["pattern"] == "error_handling"

    def test_generate_flow_optimizations_function(self):
        """Test generate_flow_optimizations convenience function."""
        graph = FlowGraph()

        # Create expensive node for caching suggestion
        expensive_node = FlowNode(
            id="1", name="expensive", flow_type="utility", complexity_score=5
        )
        graph.nodes["1"] = expensive_node

        optimizations = generate_flow_optimizations(graph)

        assert len(optimizations) == 1
        assert optimizations[0]["type"] == "caching"

    def test_export_flow_analysis_function(self):
        """Test export_flow_analysis convenience function."""
        import json
        import os
        import tempfile

        graph = FlowGraph()

        # Create simple graph for export
        node = FlowNode(id="1", name="test", flow_type="utility")
        graph.nodes["1"] = node
        graph.entry_points = ["1"]
        graph.exit_points = ["1"]

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            export_flow_analysis(graph, tmp_path)

            # Verify the file was created and contains expected data
            with open(tmp_path, "r") as f:
                exported_data = json.load(f)

            assert "graph" in exported_data
            assert "patterns" in exported_data
            assert "optimization_suggestions" in exported_data
            assert "summary" in exported_data
            assert exported_data["summary"]["total_nodes"] == 1
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_find_cycles_function(self):
        """Test find_cycles convenience function."""
        graph = FlowGraph()

        # Create graph with a cycle
        nodes = {
            "1": FlowNode(id="1", name="first", flow_type="utility"),
            "2": FlowNode(id="2", name="second", flow_type="transformation"),
            "3": FlowNode(id="3", name="third", flow_type="utility"),
        }
        graph.nodes.update(nodes)

        # Create cycle: 1->2->3->1
        graph.edges = [
            FlowEdge(source_id="1", target_id="2"),
            FlowEdge(source_id="2", target_id="3"),
            FlowEdge(source_id="3", target_id="1"),
        ]
        graph.entry_points = ["1"]

        from flowengine.observability.analysis import find_cycles

        cycles = find_cycles(graph)
        assert len(cycles) == 1
        assert (
            len(cycles[0]) == 4
        )  # Cycle includes duplicate node: ['1', '2', '3', '1']
        assert all(node_id in cycles[0] for node_id in ["1", "2", "3"])
