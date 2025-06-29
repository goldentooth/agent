"""Flow combinators organized by category.

This package provides flow combinators split into focused submodules:
- basic: Core operations (map, filter, compose, etc.)
- sources: Flow creation and data sources
- temporal: Time-based operations
- observability: Debugging and monitoring
- aggregation: Aggregation operations (batch, scan, etc.)
- control_flow: Control flow operations (retry, circuit_breaker, etc.)
- advanced: Complex operations (parallel, merge, race, etc.)

During transition, this imports from both legacy file and new submodules.
"""

# Import everything from legacy file first
from ..combinators_legacy import *  # noqa: F403

# Advanced operations
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

# Aggregation operations
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

# Override with new modular implementations
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

# Control flow operations
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

# Observability
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

# Source flows
from .sources import empty_flow, range_flow, repeat_flow, start_with_stream

# Temporal operations
from .temporal import (
    debounce_stream,
    delay_stream,
    sample_stream,
    throttle_stream,
    timeout_stream,
)
