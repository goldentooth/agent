"""Tests for flow analysis and introspection tools."""

from flowengine import Flow
from flowengine.combinators.basic import map_stream
from flowengine.observability.analysis import (
    AnalysisData,
    AnyFlow,
    FlowEdge,
    FlowList,
    FlowMetadata,
    FlowNode,
    FlowRegistry,
    OptimizationData,
    OptimizationList,
    PatternData,
    PatternList,
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
