"""Sample flows for demonstration and testing.

This module provides a collection of sample flows that can be registered
automatically to demonstrate the flow command system.
"""

from __future__ import annotations

import json
import random
import time

from flow.combinators.basic import identity_stream
from flow.flow import Flow
from flow.registry import register_flow


def _register_text_flows() -> None:
    """Register text processing flows."""
    from flow.registry import flow_registry

    flow_registry.register(
        "uppercase",
        Flow.from_sync_fn(str.upper),
        category="text",
        tags=["transform", "case"],
    )

    flow_registry.register(
        "lowercase",
        Flow.from_sync_fn(str.lower),
        category="text",
        tags=["transform", "case"],
    )

    flow_registry.register(
        "reverse_text",
        Flow.from_sync_fn(lambda text: text[::-1]),
        category="text",
        tags=["transform", "string"],
    )

    flow_registry.register(
        "title_case",
        Flow.from_sync_fn(str.title),
        category="text",
        tags=["transform", "case"],
    )

    flow_registry.register(
        "greeting",
        Flow.from_sync_fn(lambda name: f"Hello, {name}!"),
        category="text",
        tags=["template", "format"],
    )


def _register_math_flows() -> None:
    """Register math processing flows."""
    from flow.registry import flow_registry

    flow_registry.register(
        "square",
        Flow.from_sync_fn(lambda x: x * x),
        category="math",
        tags=["arithmetic", "power"],
    )

    flow_registry.register(
        "double",
        Flow.from_sync_fn(lambda x: x * 2),
        category="math",
        tags=["arithmetic", "multiply"],
    )

    register_flow(
        "add_one",
        Flow.from_sync_fn(lambda x: x + 1),
        category="math",
    )

    flow_registry.register(
        "list_sum",
        Flow.from_sync_fn(sum),
        category="math",
        tags=["aggregate", "collection"],
    )

    register_flow(
        "list_max",
        Flow.from_sync_fn(max),
        category="math",
    )

    register_flow(
        "list_min",
        Flow.from_sync_fn(min),
        category="math",
    )


def _register_data_flows() -> None:
    """Register data processing flows."""
    register_flow(
        "json_stringify",
        Flow.from_sync_fn(lambda obj: json.dumps(obj, indent=2)),
        category="data",
    )

    register_flow(
        "json_parse",
        Flow.from_sync_fn(json.loads),
        category="data",
    )

    register_flow(
        "list_length",
        Flow.from_sync_fn(len),
        category="data",
    )


def _register_utility_flows() -> None:
    """Register utility flows."""
    register_flow(
        "identity",
        identity_stream(),
        category="utility",
    )

    register_flow(
        "timestamp",
        Flow.from_sync_fn(lambda _: int(time.time())),
        category="utility",
    )


def _register_fun_flows() -> None:
    """Register fun flows."""
    register_flow(
        "random_number",
        Flow.from_sync_fn(lambda _: random.randint(1, 100)),
        category="fun",
    )


def register_sample_flows() -> None:
    """Register sample flows in the global registry for demonstration."""
    _register_text_flows()
    _register_math_flows()
    _register_data_flows()
    _register_utility_flows()
    _register_fun_flows()


def clear_sample_flows() -> None:
    """Clear all sample flows from the registry."""
    from flow.registry import clear_registry

    categories = ["text", "math", "utility", "data", "fun"]
    for category in categories:
        try:
            clear_registry(category)
        except Exception:
            # Category might not exist, that's fine
            pass
