"""Tests for flow analysis and introspection tools."""

from flowengine import Flow
from flowengine.combinators.basic import map_stream
from flowengine.observability.analysis import (
    AnalysisData,
    AnyFlow,
    FlowList,
    FlowMetadata,
    FlowRegistry,
    OptimizationData,
    OptimizationList,
    PatternData,
    PatternList,
)
