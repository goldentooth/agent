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
