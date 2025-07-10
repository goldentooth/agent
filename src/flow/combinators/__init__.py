"""Flow combinators for stream processing and composition.

This module provides essential building blocks for creating and composing flows:

- **Basic combinators**: Core operations like map, filter, compose, etc.
- **Aggregation combinators**: Batching, grouping, scanning, and windowing operations
- **Temporal combinators**: Time-based operations like debounce, throttle, and delay
- **Control flow combinators**: Conditional processing, error handling, and flow control
- **Source flows**: Functions that create streams from various inputs
- **Observability combinators**: Functions for logging, tracing, and monitoring streams
- **Advanced combinators**: Parallel processing, merging, racing, and other advanced patterns
- **Utility functions**: Helper functions for flow creation and introspection
"""

from __future__ import annotations

# Advanced combinators (10 functions migrated in Epic 13)
from .advanced import (
    chain_stream,
    combine_latest_stream,
    flat_map_ctx_stream,
    merge_async_generators,
    merge_flows,
    merge_stream,
    parallel_stream,
    parallel_stream_successful,
    race_stream,
    zip_stream,
)

# Aggregation combinators (11 functions migrated in Epic 9)
from .aggregation import (
    batch_stream,
    buffer_stream,
    chunk_stream,
    distinct_stream,
    expand_stream,
    finalize_stream,
    group_by_stream,
    memoize_stream,
    pairwise_stream,
    scan_stream,
    window_stream,
)

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

# Control flow combinators (11 functions migrated in Epic 12)
from .control_flow import (
    branch_flows,
    catch_and_continue_stream,
    chain_flows,
    circuit_breaker_stream,
    if_then_stream,
    recover_stream,
    retry_stream,
    switch_stream,
    tap_stream,
    then_stream,
    while_condition_stream,
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

# Sources (4 functions migrated in Epic 6)
from .sources import empty_flow, range_flow, repeat_flow, start_with_stream

# Temporal combinators (5 functions migrated in Epic 10)
from .temporal import (
    debounce_stream,
    delay_stream,
    sample_stream,
    throttle_stream,
    timeout_stream,
)

# Utils (2 functions migrated in Epic 5)
from .utils import create_single_item_stream, get_function_name

__all__ = [
    # Utils (2 functions)
    "get_function_name",
    "create_single_item_stream",
    # Sources (4 functions)
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
    # Aggregation combinators (11 functions)
    "batch_stream",
    "buffer_stream",
    "chunk_stream",
    "distinct_stream",
    "expand_stream",
    "finalize_stream",
    "group_by_stream",
    "memoize_stream",
    "pairwise_stream",
    "scan_stream",
    "window_stream",
    # Temporal combinators (5 functions)
    "debounce_stream",
    "delay_stream",
    "sample_stream",
    "throttle_stream",
    "timeout_stream",
    # Control flow combinators (11 functions)
    "if_then_stream",
    "retry_stream",
    "recover_stream",
    "switch_stream",
    "tap_stream",
    "while_condition_stream",
    "then_stream",
    "catch_and_continue_stream",
    "circuit_breaker_stream",
    "chain_flows",
    "branch_flows",
    # Observability combinators (5 functions + 4 classes)
    "log_stream",
    "trace_stream",
    "metrics_stream",
    "inspect_stream",
    "materialize_stream",
    "OnNext",
    "OnError",
    "OnComplete",
    "StreamNotification",
    # Advanced combinators (10 functions)
    "race_stream",
    "parallel_stream",
    "parallel_stream_successful",
    "zip_stream",
    "chain_stream",
    "merge_stream",
    "merge_flows",
    "combine_latest_stream",
    "flat_map_ctx_stream",
    "merge_async_generators",
]
