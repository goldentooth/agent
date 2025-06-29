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
