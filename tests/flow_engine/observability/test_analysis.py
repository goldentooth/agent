"""Tests for flow analysis and introspection tools."""

from goldentooth_agent.flow_engine import Flow
from goldentooth_agent.flow_engine.combinators.basic import map_stream
from goldentooth_agent.flow_engine.observability.analysis import (
    FlowAnalyzer,
    FlowEdge,
    FlowGraph,
    FlowNode,
    analyze_flow,
    analyze_flow_composition,
    detect_flow_patterns,
    export_flow_analysis,
    generate_flow_optimizations,
    get_flow_analyzer,
)


def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


def double(x: int) -> int:
    """Double a number."""
    return x * 2


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

    def test_flow_graph_depth_simple(self):
        """Test depth calculation for simple linear graph."""
        graph = FlowGraph()

        node1 = FlowNode(id="1", name="start", flow_type="utility")
        node2 = FlowNode(id="2", name="middle", flow_type="transformation")
        node3 = FlowNode(id="3", name="end", flow_type="utility")

        graph.nodes["1"] = node1
        graph.nodes["2"] = node2
        graph.nodes["3"] = node3

        graph.edges = [
            FlowEdge("1", "2"),
            FlowEdge("2", "3"),
        ]

        graph.entry_points = ["1"]
        graph.exit_points = ["3"]

        assert graph.depth == 3

    def test_flow_graph_critical_path(self):
        """Test critical path finding."""
        graph = FlowGraph()

        # Create a simple linear path
        for i in range(3):
            node = FlowNode(id=str(i), name=f"node_{i}", flow_type="utility")
            graph.nodes[str(i)] = node

        graph.edges = [
            FlowEdge("0", "1"),
            FlowEdge("1", "2"),
        ]

        graph.entry_points = ["0"]
        graph.exit_points = ["2"]

        critical_path = graph.get_critical_path()
        assert critical_path == ["0", "1", "2"]

    def test_flow_graph_find_cycles_no_cycles(self):
        """Test cycle detection when no cycles exist."""
        graph = FlowGraph()

        node1 = FlowNode(id="1", name="start", flow_type="utility")
        node2 = FlowNode(id="2", name="end", flow_type="utility")

        graph.nodes["1"] = node1
        graph.nodes["2"] = node2
        graph.edges = [FlowEdge("1", "2")]
        graph.entry_points = ["1"]

        cycles = graph.find_cycles()
        assert cycles == []

    def test_flow_graph_to_dict(self):
        """Test FlowGraph to_dict conversion."""
        graph = FlowGraph()

        node1 = FlowNode(id="1", name="test", flow_type="utility")
        graph.nodes["1"] = node1
        graph.entry_points = ["1"]
        graph.exit_points = ["1"]

        graph_dict = graph.to_dict()

        assert "nodes" in graph_dict
        assert "edges" in graph_dict
        assert "entry_points" in graph_dict
        assert "exit_points" in graph_dict
        assert "analysis" in graph_dict
        assert graph_dict["analysis"]["complexity_score"] == 1
        assert graph_dict["analysis"]["node_count"] == 1


class TestFlowAnalyzer:
    """Tests for FlowAnalyzer class."""

    def test_analyzer_creation(self):
        """Test FlowAnalyzer creation."""
        analyzer = FlowAnalyzer()

        assert analyzer.node_id_counter == 0
        assert len(analyzer.flow_registry) == 0

    def test_analyze_single_flow(self):
        """Test analyzing a single flow."""
        analyzer = FlowAnalyzer()
        flow = map_stream(increment)

        graph = analyzer.analyze_flow(flow)

        assert len(graph.nodes) == 1
        assert len(graph.entry_points) == 1
        assert len(graph.exit_points) == 1

        node = list(graph.nodes.values())[0]
        assert "map" in node.name

    def test_analyze_composition(self):
        """Test analyzing a composition of flows."""
        analyzer = FlowAnalyzer()
        flow1 = map_stream(increment)
        flow2 = map_stream(double)

        graph = analyzer.analyze_composition([flow1, flow2])

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert len(graph.entry_points) == 1
        assert len(graph.exit_points) == 1

        # Check edge connects the flows
        edge = graph.edges[0]
        assert edge.edge_type == "sequential"

    def test_categorize_flow_type(self):
        """Test flow type categorization."""
        analyzer = FlowAnalyzer()

        # Test transformation
        map_flow = map_stream(increment)
        assert analyzer._categorize_flow_type(map_flow) == "transformation"

        # Test utility (default case)
        custom_flow = Flow(lambda s: s, name="custom_operation")
        assert analyzer._categorize_flow_type(custom_flow) == "utility"

    def test_calculate_complexity(self):
        """Test complexity calculation."""
        analyzer = FlowAnalyzer()

        # Simple operation
        simple_flow = Flow(lambda s: s, name="simple")
        assert analyzer._calculate_complexity(simple_flow) == 1

        # Parallel operation (more complex)
        parallel_flow = Flow(lambda s: s, name="parallel_process")
        assert analyzer._calculate_complexity(parallel_flow) == 4  # base + 3

    def test_detect_patterns_empty_graph(self):
        """Test pattern detection on empty graph."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        patterns = analyzer.detect_patterns(graph)
        assert patterns == []

    def test_generate_optimization_suggestions_simple(self):
        """Test optimization suggestions for simple graph."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Add a single simple node
        node = FlowNode(id="1", name="simple", flow_type="utility", complexity_score=1)
        graph.nodes["1"] = node

        suggestions = analyzer.generate_optimization_suggestions(graph)
        assert len(suggestions) == 0  # No suggestions for simple graphs

    def test_generate_optimization_suggestions_complex(self):
        """Test optimization suggestions for complex graph."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Add multiple complex nodes
        for i in range(5):
            node = FlowNode(
                id=str(i), name=f"complex_{i}", flow_type="utility", complexity_score=3
            )
            graph.nodes[str(i)] = node

        suggestions = analyzer.generate_optimization_suggestions(graph)
        assert len(suggestions) > 0  # Should have suggestions for complex graphs

        # Check for batching suggestion
        batching_suggestions = [s for s in suggestions if s["type"] == "batching"]
        assert len(batching_suggestions) > 0

        # Check for caching suggestion
        caching_suggestions = [s for s in suggestions if s["type"] == "caching"]
        assert len(caching_suggestions) > 0


class TestAnalysisFunctions:
    """Tests for module-level analysis functions."""

    def test_analyze_flow_function(self):
        """Test analyze_flow convenience function."""
        flow = map_stream(increment)
        graph = analyze_flow(flow)

        assert len(graph.nodes) == 1
        assert len(graph.entry_points) == 1

    def test_analyze_flow_composition_function(self):
        """Test analyze_flow_composition convenience function."""
        flows = [map_stream(increment), map_stream(double)]
        graph = analyze_flow_composition(flows)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

    def test_detect_flow_patterns_function(self):
        """Test detect_flow_patterns convenience function."""
        graph = FlowGraph()
        patterns = detect_flow_patterns(graph)

        assert isinstance(patterns, list)

    def test_generate_flow_optimizations_function(self):
        """Test generate_flow_optimizations convenience function."""
        graph = FlowGraph()
        optimizations = generate_flow_optimizations(graph)

        assert isinstance(optimizations, list)

    def test_get_flow_analyzer_function(self):
        """Test get_flow_analyzer convenience function."""
        analyzer = get_flow_analyzer()

        assert isinstance(analyzer, FlowAnalyzer)

    def test_export_flow_analysis_function(self, tmp_path):
        """Test export_flow_analysis convenience function."""
        graph = FlowGraph()
        node = FlowNode(id="1", name="test", flow_type="utility")
        graph.nodes["1"] = node

        filepath = tmp_path / "analysis.json"
        export_flow_analysis(graph, str(filepath))

        assert filepath.exists()

        # Check that the file contains valid JSON
        import json

        with open(filepath) as f:
            data = json.load(f)

        assert "graph" in data
        assert "patterns" in data
        assert "optimization_suggestions" in data
        assert "summary" in data


class TestPatternDetection:
    """Tests for specific pattern detection functionality."""

    def test_detect_map_filter_pattern(self):
        """Test detection of map-filter pattern."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Create map node
        map_node = FlowNode(id="1", name="map", flow_type="transformation")
        # Create filter node
        filter_node = FlowNode(id="2", name="filter", flow_type="filtering")

        graph.nodes["1"] = map_node
        graph.nodes["2"] = filter_node
        graph.edges = [FlowEdge("1", "2")]

        patterns = analyzer.detect_patterns(graph)
        map_filter_patterns = [p for p in patterns if p.get("pattern") == "map_filter"]

        assert len(map_filter_patterns) == 1
        assert "optimization_hint" in map_filter_patterns[0]

    def test_detect_linear_pipeline_pattern(self):
        """Test detection of linear pipeline pattern."""
        analyzer = FlowAnalyzer()
        graph = FlowGraph()

        # Create a linear pipeline with 4 nodes
        for i in range(4):
            node = FlowNode(id=str(i), name=f"stage_{i}", flow_type="utility")
            graph.nodes[str(i)] = node

        # Connect them linearly
        for i in range(3):
            graph.edges.append(FlowEdge(str(i), str(i + 1)))

        graph.entry_points = ["0"]
        graph.exit_points = ["3"]

        patterns = analyzer.detect_patterns(graph)
        pipeline_patterns = [
            p for p in patterns if p.get("pattern") == "linear_pipeline"
        ]

        assert len(pipeline_patterns) == 1
        assert pipeline_patterns[0]["nodes"] == ["0", "1", "2", "3"]
