"""Tests for flow registry system - core functionality.

This module contains the TestFlowRegistry class which tests basic CRUD operations,
flow retrieval, listing, and search functionality.
"""

from flowengine import Flow
from flowengine.combinators.basic import map_stream
from flowengine.registry import (
    FlowRegistry,
    flow_registry,
    get_flow,
    list_flows,
    register_flow,
    registered_flow,
    search_flows,
)


def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


def double(x: int) -> int:
    """Double a number."""
    return x * 2


class TestFlowRegistry:
    """Tests for FlowRegistry class - core registry functionality."""
