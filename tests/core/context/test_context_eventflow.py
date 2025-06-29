"""Comprehensive tests for Context class with EventFlow integration."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from goldentooth_agent.core.context import Context, ContextFrame
from goldentooth_agent.core.event.flow import AsyncEventFlow, SyncEventFlow
from goldentooth_agent.flow_engine import Flow


class TestContextEventFlowIntegration:
    """Test suite for Context class EventFlow integration."""

    def test_context_initialization_with_eventflow(self) -> None:
        """Test that Context initializes properly with EventFlow components."""
        context = Context()

        # Check basic structure
        assert len(context.frames) == 1
        assert isinstance(context.frames[0], ContextFrame)

        # Check EventFlow components are initialized
        assert isinstance(context._sync_events, dict)
        assert isinstance(context._async_events, dict)
        assert isinstance(context._global_sync_events, SyncEventFlow)
        assert isinstance(context._global_async_events, AsyncEventFlow)

        # Check event names
        assert context._global_sync_events.event_name == "context.global_changes"
        assert context._global_async_events.event_name == "context.global_changes"

    def test_subscribe_sync_creates_event_flow(self) -> None:
        """Test that subscribe_sync creates and returns SyncEventFlow instances."""
        context = Context()

        # First call should create new event flow
        event_flow1 = context.subscribe_sync("test_key")
        assert isinstance(event_flow1, SyncEventFlow)
        assert event_flow1.event_name == "context.test_key"
        assert "test_key" in context._sync_events

        # Second call should return same instance
        event_flow2 = context.subscribe_sync("test_key")
        assert event_flow2 is event_flow1

    def test_subscribe_async_creates_event_flow(self) -> None:
        """Test that subscribe_async creates and returns AsyncEventFlow instances."""
        context = Context()

        # First call should create new event flow
        event_flow1 = context.subscribe_async("test_key")
        assert isinstance(event_flow1, AsyncEventFlow)
        assert event_flow1.event_name == "context.test_key"
        assert "test_key" in context._async_events

        # Second call should return same instance
        event_flow2 = context.subscribe_async("test_key")
        assert event_flow2 is event_flow2

    def test_sync_event_emission_on_value_change(self) -> None:
        """Test that setting values emits events through sync EventFlow."""
        context = Context()
        event_flow = context.subscribe_sync("test_key")

        received_values = []

        def handler(value: Any) -> None:
            received_values.append(value)

        event_flow.on(handler)

        # Set values and verify events are emitted
        context["test_key"] = "value1"
        assert received_values == ["value1"]

        context["test_key"] = "value2"
        assert received_values == ["value1", "value2"]

    @pytest.mark.asyncio
    async def test_async_event_emission_on_value_change(self) -> None:
        """Test that setting values emits events through async EventFlow."""
        context = Context()
        event_flow = context.subscribe_async("test_key")

        received_values = []

        async def handler(value: Any) -> None:
            received_values.append(value)

        await event_flow.on(handler)

        # Set values and verify events are emitted
        context["test_key"] = "value1"
        await asyncio.sleep(0.01)  # Allow async handlers to process
        assert received_values == ["value1"]

        context["test_key"] = "value2"
        await asyncio.sleep(0.01)
        assert received_values == ["value1", "value2"]

    def test_global_sync_change_events(self) -> None:
        """Test global context change events through sync EventFlow."""
        context = Context()
        global_events = context.global_changes_sync()

        received_events = []

        def handler(change_data: dict[str, Any]) -> None:
            received_events.append(change_data)

        global_events.on(handler)

        # Set a value and check global event
        context["test_key"] = "test_value"

        assert len(received_events) == 1
        event = received_events[0]
        assert event["key"] == "test_key"
        assert event["new_value"] == "test_value"
        assert event["old_value"] is None
        assert "timestamp" in event
        assert event["context_id"] == id(context)

    @pytest.mark.asyncio
    async def test_global_async_change_events(self) -> None:
        """Test global context change events through async EventFlow."""
        context = Context()
        global_events = context.global_changes_async()

        received_events = []

        async def handler(change_data: dict[str, Any]) -> None:
            received_events.append(change_data)

        await global_events.on(handler)

        # Set a value and check global event
        context["test_key"] = "test_value"
        await asyncio.sleep(0.01)

        assert len(received_events) == 1
        event = received_events[0]
        assert event["key"] == "test_key"
        assert event["new_value"] == "test_value"
        assert event["old_value"] is None
        assert "timestamp" in event
        assert event["context_id"] == id(context)

    def test_old_value_tracking_in_events(self) -> None:
        """Test that global events correctly track old values."""
        context = Context()
        global_events = context.global_changes_sync()

        received_events = []

        def handler(change_data: dict[str, Any]) -> None:
            received_events.append(change_data)

        global_events.on(handler)

        # Set initial value
        context["test_key"] = "initial"
        assert received_events[0]["old_value"] is None
        assert received_events[0]["new_value"] == "initial"

        # Update value
        context["test_key"] = "updated"
        assert received_events[1]["old_value"] == "initial"
        assert received_events[1]["new_value"] == "updated"

    @pytest.mark.asyncio
    async def test_as_flow_integration(self) -> None:
        """Test that as_flow() creates working Flow streams."""
        context = Context()

        # Test async flow
        async_flow = context.as_flow("test_key", use_async=True)
        assert isinstance(async_flow, Flow)

        # Test sync flow
        sync_flow = context.as_flow("test_key", use_async=False)
        assert isinstance(sync_flow, Flow)

        # Test that flows receive events
        received_values = []

        async def collect_values() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for value in async_flow(empty_stream()):
                received_values.append(value)
                count += 1
                if count >= 2:
                    break

        # Start collection
        collection_task = asyncio.create_task(collect_values())
        await asyncio.sleep(0.01)

        # Emit values
        context["test_key"] = "flow_value1"
        context["test_key"] = "flow_value2"

        await collection_task
        assert received_values == ["flow_value1", "flow_value2"]

    @pytest.mark.asyncio
    async def test_global_changes_as_flow(self) -> None:
        """Test global_changes_as_flow() creates working Flow streams."""
        context = Context()
        global_flow = context.global_changes_as_flow(use_async=True)

        received_changes = []

        async def collect_changes() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for change in global_flow(empty_stream()):
                received_changes.append(change)
                count += 1
                if count >= 2:
                    break

        # Start collection
        collection_task = asyncio.create_task(collect_changes())
        await asyncio.sleep(0.01)

        # Make changes
        context["key1"] = "value1"
        context["key2"] = "value2"

        await collection_task

        assert len(received_changes) == 2
        assert received_changes[0]["key"] == "key1"
        assert received_changes[0]["new_value"] == "value1"
        assert received_changes[1]["key"] == "key2"
        assert received_changes[1]["new_value"] == "value2"

    def test_multiple_key_subscriptions(self) -> None:
        """Test subscribing to multiple keys with different EventFlows."""
        context = Context()

        key1_flow = context.subscribe_sync("key1")
        key2_flow = context.subscribe_sync("key2")

        key1_values = []
        key2_values = []

        key1_flow.on(lambda v: key1_values.append(v))
        key2_flow.on(lambda v: key2_values.append(v))

        # Set values for different keys
        context["key1"] = "value1a"
        context["key2"] = "value2a"
        context["key1"] = "value1b"

        # Each flow should only receive its key's events
        assert key1_values == ["value1a", "value1b"]
        assert key2_values == ["value2a"]

    def test_context_layering_with_events(self) -> None:
        """Test that context layering works correctly with event emission."""
        context = Context()
        event_flow = context.subscribe_sync("test_key")

        received_values = []
        event_flow.on(lambda v: received_values.append(v))

        # Set value in base layer
        context["test_key"] = "base_value"
        assert received_values == ["base_value"]

        # Push new layer and set value
        context.push_layer()
        context["test_key"] = "layer_value"
        assert received_values == ["base_value", "layer_value"]

        # Pop layer - value should revert to base layer value
        # Note: The current implementation doesn't emit events on pop_layer()
        context.pop_layer()
        assert context["test_key"] == "base_value"

    def test_context_fork_preserves_event_isolation(self) -> None:
        """Test that forked contexts have isolated event systems."""
        original = Context()
        original["shared_key"] = "original_value"

        # Fork the context
        forked = original.fork()

        # Set up separate event listeners
        original_events = []
        forked_events = []

        original.subscribe_sync("test_key").on(lambda v: original_events.append(v))
        forked.subscribe_sync("test_key").on(lambda v: forked_events.append(v))

        # Set values in each context
        original["test_key"] = "original_value"
        forked["test_key"] = "forked_value"

        # Events should be isolated
        assert original_events == ["original_value"]
        assert forked_events == ["forked_value"]

        # Data should be isolated too
        assert original["test_key"] == "original_value"
        assert forked["test_key"] == "forked_value"
        assert original["shared_key"] == "original_value"
        assert forked["shared_key"] == "original_value"  # Inherited from fork


class TestContextEventFlowAdvanced:
    """Advanced test scenarios for Context EventFlow integration."""

    @pytest.mark.asyncio
    async def test_high_frequency_updates(self) -> None:
        """Test EventFlow handling of rapid context updates."""
        context = Context()
        event_flow = context.subscribe_async("counter")

        received_values = []

        async def handler(value: Any) -> None:
            received_values.append(value)

        await event_flow.on(handler)

        # Rapidly update the context
        for i in range(100):
            context["counter"] = i

        # Give async handlers time to process all events
        await asyncio.sleep(0.1)

        # Should receive all values
        assert len(received_values) == 100
        assert received_values == list(range(100))

    def test_event_flow_with_context_merge(self) -> None:
        """Test that merging contexts works with EventFlow subscriptions."""
        context1 = Context()
        context2 = Context()

        # Set up data in both contexts
        context1["key1"] = "value1"
        context2["key2"] = "value2"
        context2["key1"] = "value1_updated"  # Override key1

        # Merge contexts
        merged = context1.merge(context2)

        # Test that merged context has isolated event system
        merged_events = []
        merged.subscribe_sync("test_key").on(lambda v: merged_events.append(v))

        # Original contexts should not receive events from merged
        context1_events = []
        context1.subscribe_sync("test_key").on(lambda v: context1_events.append(v))

        merged["test_key"] = "merged_value"
        context1["test_key"] = "context1_value"

        assert merged_events == ["merged_value"]
        assert context1_events == ["context1_value"]

    @pytest.mark.asyncio
    async def test_eventflow_with_flow_operations(self) -> None:
        """Test using Flow operations on context event streams."""
        context = Context()

        # Create a Flow that filters and transforms context changes
        context_flow = context.as_flow("number_key", use_async=True)
        processed_flow = context_flow.filter(
            lambda x: isinstance(x, int) and x % 2 == 0
        ).map(  # Only even numbers
            lambda x: x * 2
        )  # Double them

        results = []

        async def collect_results() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for result in processed_flow(empty_stream()):
                results.append(result)
                count += 1
                if count >= 3:  # Collect 3 processed values
                    break

        # Start collection
        collection_task = asyncio.create_task(collect_results())
        await asyncio.sleep(0.01)

        # Set various values
        context["number_key"] = 1  # Odd - filtered out
        context["number_key"] = 2  # Even - becomes 4
        context["number_key"] = "string"  # Non-int - filtered out
        context["number_key"] = 4  # Even - becomes 8
        context["number_key"] = 5  # Odd - filtered out
        context["number_key"] = 6  # Even - becomes 12

        await collection_task
        assert results == [4, 8, 12]  # Only processed even numbers

    def test_error_handling_in_event_handlers(self) -> None:
        """Test that errors in event handlers don't break the system."""
        context = Context()
        event_flow = context.subscribe_sync("test_key")

        success_calls = []
        error_calls = []

        def good_handler(value: Any) -> None:
            success_calls.append(value)

        def bad_handler(value: Any) -> None:
            error_calls.append(value)
            raise ValueError(f"Handler error for: {value}")

        event_flow.on(good_handler)
        event_flow.on(bad_handler)

        # Set value - should not raise despite bad handler
        context["test_key"] = "test_value"

        # Good handler should still work
        assert success_calls == ["test_value"]
        assert error_calls == ["test_value"]

    @pytest.mark.asyncio
    async def test_performance_with_many_subscribers(self) -> None:
        """Test performance characteristics with many event subscribers."""
        context = Context()

        # Create many subscribers
        num_subscribers = 50
        all_received = []

        for i in range(num_subscribers):
            subscriber_events = []
            all_received.append(subscriber_events)

            if i % 2 == 0:  # Mix of sync and async
                event_flow = context.subscribe_sync("perf_key")
                event_flow.on(lambda v, events=subscriber_events: events.append(v))
            else:
                event_flow = context.subscribe_async("perf_key")
                await event_flow.on(
                    lambda v, events=subscriber_events: events.append(v)
                )

        # Set value and measure
        start_time = time.time()
        context["perf_key"] = "performance_test"

        # Give async handlers time to complete
        await asyncio.sleep(0.01)

        duration = time.time() - start_time

        # All subscribers should have received the event
        for subscriber_events in all_received:
            assert subscriber_events == ["performance_test"]

        # Should complete reasonably quickly (adjust threshold as needed)
        assert duration < 1.0  # Should take less than 1 second

    def test_context_dump_with_eventflow_state(self) -> None:
        """Test that context dump works correctly with EventFlow integration."""
        context = Context()

        # Set some values and create subscriptions
        context["key1"] = "value1"
        context["key2"] = {"nested": "value"}
        context.subscribe_sync("key1")  # Create event flow
        context.subscribe_async("key2")  # Create event flow

        # Dump should work normally and include all data
        dump = context.dump()
        assert "key1" in dump
        assert "value1" in dump
        assert "nested" in dump

        # Dump should be valid JSON
        import json

        parsed = json.loads(dump)
        assert parsed["key1"] == "value1"
        assert parsed["key2"]["nested"] == "value"
