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
