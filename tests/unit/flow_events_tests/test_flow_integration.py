"""Tests for flow_events.flow_integration module."""

from typing import Any
from unittest.mock import AsyncMock, Mock, call

import pytest

from flow_events.flow_integration import (
    event_bridge,
    event_filter,
    event_sink,
    event_source,
    event_transform,
)


class TestEventSource:
    """Test suite for event_source function."""

    def test_event_source_async_default(self) -> None:
        """Test event_source creates async flow by default."""
        flow = event_source("test_event")

        assert flow is not None
        assert flow.name == "from_emitter"

    def test_event_source_async_explicit(self) -> None:
        """Test event_source creates async flow when explicitly requested."""
        flow = event_source("test_event", use_async=True)

        assert flow is not None
        assert flow.name == "from_emitter"

    def test_event_source_sync(self) -> None:
        """Test event_source creates sync flow when requested."""
        flow = event_source("test_event", use_async=False)

        assert flow is not None
        assert flow.name == "from_emitter"

    def test_event_source_different_event_names(self) -> None:
        """Test event_source with different event names."""
        flow1 = event_source("event1")
        flow2 = event_source("event2")

        assert flow1.name == "from_emitter"
        assert flow2.name == "from_emitter"

    def test_event_source_empty_event_name(self) -> None:
        """Test event_source with empty event name."""
        flow = event_source("")

        assert flow is not None
        assert flow.name == "from_emitter"

    def test_event_source_special_characters_in_name(self) -> None:
        """Test event_source with special characters in event name."""
        flow = event_source("test.event-name_123")

        assert flow is not None
        assert flow.name == "from_emitter"


class TestEventSink:
    """Test suite for event_sink function."""

    def test_event_sink_async_default(self) -> None:
        """Test event_sink creates async flow by default."""
        flow: Any = event_sink("test_event")

        assert flow is not None
        assert flow.name == "event_sink(test_event)"

    def test_event_sink_async_explicit(self) -> None:
        """Test event_sink creates async flow when explicitly requested."""
        flow: Any = event_sink("test_event", use_async=True)

        assert flow is not None
        assert flow.name == "event_sink(test_event)"

    def test_event_sink_sync(self) -> None:
        """Test event_sink creates sync flow when requested."""
        flow: Any = event_sink("test_event", use_async=False)

        assert flow is not None
        assert flow.name == "event_sink(test_event)"

    def test_event_sink_different_event_names(self) -> None:
        """Test event_sink with different event names."""
        flow1: Any = event_sink("event1")
        flow2: Any = event_sink("event2")

        assert flow1.name == "event_sink(event1)"
        assert flow2.name == "event_sink(event2)"

    def test_event_sink_empty_event_name(self) -> None:
        """Test event_sink with empty event name."""
        flow: Any = event_sink("")

        assert flow is not None
        assert flow.name == "event_sink()"

    def test_event_sink_special_characters_in_name(self) -> None:
        """Test event_sink with special characters in event name."""
        flow: Any = event_sink("test.event-name_123")

        assert flow is not None
        assert flow.name == "event_sink(test.event-name_123)"


class TestEventBridge:
    """Test suite for event_bridge function."""

    def test_event_bridge_async_default(self) -> None:
        """Test event_bridge creates async flow by default."""
        flow = event_bridge("source_event", "target_event")

        assert flow is not None
        assert flow.name == "event_bridge(source_event->target_event)"

    def test_event_bridge_async_explicit(self) -> None:
        """Test event_bridge creates async flow when explicitly requested."""
        flow = event_bridge("source_event", "target_event", use_async=True)

        assert flow is not None
        assert flow.name == "event_bridge(source_event->target_event)"

    def test_event_bridge_sync(self) -> None:
        """Test event_bridge creates sync flow when requested."""
        flow = event_bridge("source_event", "target_event", use_async=False)

        assert flow is not None
        assert flow.name == "event_bridge(source_event->target_event)"

    def test_event_bridge_different_event_names(self) -> None:
        """Test event_bridge with different event names."""
        flow1 = event_bridge("event1", "event2")
        flow2 = event_bridge("eventA", "eventB")

        assert flow1.name == "event_bridge(event1->event2)"
        assert flow2.name == "event_bridge(eventA->eventB)"

    def test_event_bridge_same_source_and_target(self) -> None:
        """Test event_bridge with same source and target event."""
        flow = event_bridge("same_event", "same_event")

        assert flow is not None
        assert flow.name == "event_bridge(same_event->same_event)"

    def test_event_bridge_empty_event_names(self) -> None:
        """Test event_bridge with empty event names."""
        flow = event_bridge("", "")

        assert flow is not None
        assert flow.name == "event_bridge(->)"

    def test_event_bridge_special_characters_in_names(self) -> None:
        """Test event_bridge with special characters in event names."""
        flow = event_bridge("source.event-1", "target_event.2")

        assert flow is not None
        assert flow.name == "event_bridge(source.event-1->target_event.2)"


class TestEventFilter:
    """Test suite for event_filter function."""

    def test_event_filter_async_default(self) -> None:
        """Test event_filter creates async flow by default."""
        predicate = lambda x: x > 0
        flow = event_filter("test_event", predicate)

        assert flow is not None
        assert flow.name == "event_filter(test_event)"

    def test_event_filter_async_explicit(self) -> None:
        """Test event_filter creates async flow when explicitly requested."""
        predicate = lambda x: x > 0
        flow = event_filter("test_event", predicate, use_async=True)

        assert flow is not None
        assert flow.name == "event_filter(test_event)"

    def test_event_filter_sync(self) -> None:
        """Test event_filter creates sync flow when requested."""
        predicate = lambda x: x > 0
        flow = event_filter("test_event", predicate, use_async=False)

        assert flow is not None
        assert flow.name == "event_filter(test_event)"

    def test_event_filter_different_predicates(self) -> None:
        """Test event_filter with different predicate functions."""
        predicate1 = lambda x: x > 0
        predicate2 = lambda x: x % 2 == 0

        flow1 = event_filter("test_event", predicate1)
        flow2 = event_filter("test_event", predicate2)

        assert flow1.name == "event_filter(test_event)"
        assert flow2.name == "event_filter(test_event)"

    def test_event_filter_different_event_names(self) -> None:
        """Test event_filter with different event names."""
        predicate = lambda x: True

        flow1 = event_filter("event1", predicate)
        flow2 = event_filter("event2", predicate)

        assert flow1.name == "event_filter(event1)"
        assert flow2.name == "event_filter(event2)"

    def test_event_filter_empty_event_name(self) -> None:
        """Test event_filter with empty event name."""
        predicate = lambda x: True
        flow = event_filter("", predicate)

        assert flow is not None
        assert flow.name == "event_filter()"

    def test_event_filter_special_characters_in_name(self) -> None:
        """Test event_filter with special characters in event name."""
        predicate = lambda x: True
        flow = event_filter("test.event-name_123", predicate)

        assert flow is not None
        assert flow.name == "event_filter(test.event-name_123)"

    def test_event_filter_complex_predicate(self) -> None:
        """Test event_filter with complex predicate function."""

        def complex_predicate(x: dict[str, Any]) -> bool:
            return "valid" in x and x["valid"] is True

        flow = event_filter("test_event", complex_predicate)

        assert flow is not None
        assert flow.name == "event_filter(test_event)"


class TestEventTransform:
    """Test suite for event_transform function."""

    def test_event_transform_async_default(self) -> None:
        """Test event_transform creates async flow by default."""
        transformer = lambda x: x * 2
        flow = event_transform("test_event", transformer)

        assert flow is not None
        assert flow.name == "event_transform(test_event)"

    def test_event_transform_async_explicit(self) -> None:
        """Test event_transform creates async flow when explicitly requested."""
        transformer = lambda x: x * 2
        flow = event_transform("test_event", transformer, use_async=True)

        assert flow is not None
        assert flow.name == "event_transform(test_event)"

    def test_event_transform_sync(self) -> None:
        """Test event_transform creates sync flow when requested."""
        transformer = lambda x: x * 2
        flow = event_transform("test_event", transformer, use_async=False)

        assert flow is not None
        assert flow.name == "event_transform(test_event)"

    def test_event_transform_different_transformers(self) -> None:
        """Test event_transform with different transformer functions."""
        transformer1 = lambda x: x * 2
        transformer2 = lambda x: str(x).upper()

        flow1 = event_transform("test_event", transformer1)
        flow2 = event_transform("test_event", transformer2)

        assert flow1.name == "event_transform(test_event)"
        assert flow2.name == "event_transform(test_event)"

    def test_event_transform_different_event_names(self) -> None:
        """Test event_transform with different event names."""
        transformer = lambda x: x

        flow1 = event_transform("event1", transformer)
        flow2 = event_transform("event2", transformer)

        assert flow1.name == "event_transform(event1)"
        assert flow2.name == "event_transform(event2)"

    def test_event_transform_empty_event_name(self) -> None:
        """Test event_transform with empty event name."""
        transformer = lambda x: x
        flow = event_transform("", transformer)

        assert flow is not None
        assert flow.name == "event_transform()"

    def test_event_transform_special_characters_in_name(self) -> None:
        """Test event_transform with special characters in event name."""
        transformer = lambda x: x
        flow = event_transform("test.event-name_123", transformer)

        assert flow is not None
        assert flow.name == "event_transform(test.event-name_123)"

    def test_event_transform_complex_transformer(self) -> None:
        """Test event_transform with complex transformer function."""

        def complex_transformer(x: dict[str, Any]) -> dict[str, Any]:
            result = x.copy()
            result["transformed"] = True
            return result

        flow = event_transform("test_event", complex_transformer)

        assert flow is not None
        assert flow.name == "event_transform(test_event)"

    def test_event_transform_identity_transformer(self) -> None:
        """Test event_transform with identity transformer."""
        transformer = lambda x: x
        flow = event_transform("test_event", transformer)

        assert flow is not None
        assert flow.name == "event_transform(test_event)"


class TestTypeAliases:
    """Test suite for type aliases."""

    def test_type_aliases_are_defined(self) -> None:
        """Test that type aliases are properly defined."""
        from flow_events.flow_integration import (
            AnyFlow,
            AnyTransformer,
            AnyTransformFlow,
        )

        # These should be importable without errors
        assert AnyFlow is not None
        assert AnyTransformer is not None
        assert AnyTransformFlow is not None


class TestIntegrationBehavior:
    """Test suite for integration behavior and edge cases."""

    def test_all_functions_return_flow_objects(self) -> None:
        """Test that all functions return Flow objects."""
        predicate = lambda x: True
        transformer = lambda x: x

        flows = [
            event_source("test"),
            event_sink("test"),
            event_bridge("source", "target"),
            event_filter("test", predicate),
            event_transform("test", transformer),
        ]

        for flow in flows:
            assert flow is not None
            assert hasattr(flow, "name")
            assert hasattr(flow, "__call__")

    def test_async_and_sync_variants_both_work(self) -> None:
        """Test that both async and sync variants work."""
        predicate = lambda x: True
        transformer = lambda x: x

        # Test async variants
        async_flows = [
            event_source("test", use_async=True),
            event_sink("test", use_async=True),
            event_bridge("source", "target", use_async=True),
            event_filter("test", predicate, use_async=True),
            event_transform("test", transformer, use_async=True),
        ]

        # Test sync variants
        sync_flows = [
            event_source("test", use_async=False),
            event_sink("test", use_async=False),
            event_bridge("source", "target", use_async=False),
            event_filter("test", predicate, use_async=False),
            event_transform("test", transformer, use_async=False),
        ]

        for flow in async_flows + sync_flows:
            assert flow is not None
            assert hasattr(flow, "name")

    def test_function_names_reflect_parameters(self) -> None:
        """Test that function names properly reflect their parameters."""
        predicate = lambda x: True
        transformer = lambda x: x

        # Test that names include the event names (except event_source which uses from_emitter)
        assert event_source("test_event").name == "from_emitter"
        assert "test_event" in event_sink("test_event").name
        assert "source" in event_bridge("source", "target").name
        assert "target" in event_bridge("source", "target").name
        assert "test_event" in event_filter("test_event", predicate).name
        assert "test_event" in event_transform("test_event", transformer).name

    def test_unicode_event_names(self) -> None:
        """Test that unicode event names are handled correctly."""
        predicate = lambda x: True
        transformer = lambda x: x

        unicode_name = "测试事件"

        flows = [
            (event_source(unicode_name), "from_emitter"),
            (event_sink(unicode_name), unicode_name),
            (event_bridge(unicode_name, "target"), unicode_name),
            (event_filter(unicode_name, predicate), unicode_name),
            (event_transform(unicode_name, transformer), unicode_name),
        ]

        for flow, expected_name_part in flows:
            assert flow is not None
            if expected_name_part == "from_emitter":
                assert flow.name == "from_emitter"
            else:
                assert expected_name_part in flow.name

    def test_very_long_event_names(self) -> None:
        """Test that very long event names are handled correctly."""
        predicate = lambda x: True
        transformer = lambda x: x

        long_name = "a" * 100  # Reasonable long event name

        flows = [
            (event_source(long_name), "from_emitter"),
            (event_sink(long_name), long_name),
            (event_bridge(long_name, "target"), long_name),
            (event_filter(long_name, predicate), long_name),
            (event_transform(long_name, transformer), long_name),
        ]

        for flow, expected_name_part in flows:
            assert flow is not None
            if expected_name_part == "from_emitter":
                assert flow.name == "from_emitter"
            else:
                assert expected_name_part in flow.name
