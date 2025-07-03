"""Flow combinators for stream processing and composition.

This module provides essential building blocks for creating and composing flows:

- **Basic combinators**: Core operations like map, filter, compose, etc.
- **Source flows**: Functions that create streams from various inputs
- **Utility functions**: Helper functions for flow creation and introspection
"""

from __future__ import annotations

# Basic combinators (13 functions migrated in Epic 7)
from .basic import (
    collect_stream,
    compose,
    filter_stream,
    flat_map_stream,
    flatten_stream,
    guard_stream,
    identity_stream,
    map_stream,
    run_fold,
    share_stream,
    skip_stream,
    take_stream,
    until_stream,
)

# Sources
from .sources import empty_flow, range_flow, repeat_flow, start_with_stream

# Utils
from .utils import create_single_item_stream, get_function_name

__all__ = [
    # Utils
    "get_function_name",
    "create_single_item_stream",
    # Sources
    "range_flow",
    "repeat_flow",
    "empty_flow",
    "start_with_stream",
    # Basic combinators (13 functions)
    "run_fold",
    "compose",
    "filter_stream",
    "map_stream",
    "flat_map_stream",
    "identity_stream",
    "take_stream",
    "skip_stream",
    "guard_stream",
    "flatten_stream",
    "collect_stream",
    "until_stream",
    "share_stream",
]
