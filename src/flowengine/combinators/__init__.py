"""Flow combinators for stream processing and composition.

This module provides essential building blocks for creating and composing flows:

- **Basic combinators**: Core operations like map, filter, compose, etc.
- **Source flows**: Functions that create streams from various inputs
- **Observability combinators**: Functions for logging, tracing, and monitoring streams
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

# Observability combinators (5 functions + 3 notification classes migrated in Epic 11)
from .observability import (
    OnComplete,
    OnError,
    OnNext,
    StreamNotification,
    inspect_stream,
    log_stream,
    materialize_stream,
    metrics_stream,
    trace_stream,
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
    # Observability combinators (5 functions + 3 notification classes)
    "log_stream",
    "trace_stream",
    "metrics_stream",
    "inspect_stream",
    "materialize_stream",
    "OnNext",
    "OnError",
    "OnComplete",
    "StreamNotification",
]
