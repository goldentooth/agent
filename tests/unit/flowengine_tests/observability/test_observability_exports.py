"""Tests for observability module exports to verify Epic 20 completion."""


def test_analysis_exports() -> None:
    """Test that analysis exports are available from observability module."""
    from flowengine.observability import (
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

    # Verify imports worked
    assert FlowNode is not None
    assert FlowEdge is not None
    assert FlowGraph is not None
    assert FlowAnalyzer is not None
    assert analyze_flow is not None
    assert analyze_flow_composition is not None
    assert detect_flow_patterns is not None
    assert generate_flow_optimizations is not None
    assert export_flow_analysis is not None
    assert get_flow_analyzer is not None


def test_analysis_exports_in_all() -> None:
    """Test that analysis exports are included in __all__."""
    from flowengine.observability import __all__

    expected_analysis_exports = [
        "FlowNode",
        "FlowEdge",
        "FlowGraph",
        "FlowAnalyzer",
        "analyze_flow",
        "analyze_flow_composition",
        "detect_flow_patterns",
        "generate_flow_optimizations",
        "export_flow_analysis",
        "get_flow_analyzer",
    ]

    for export in expected_analysis_exports:
        assert export in __all__, f"Missing {export} in __all__"
