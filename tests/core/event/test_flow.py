"""Comprehensive tests for Flow-integrated event system."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from goldentooth_agent.core.event.flow import (
    AsyncEventFlow,
    SyncEventFlow,
    create_async_event_flow,
    create_sync_event_flow,
    create_typed_async_event_flow,
    create_typed_sync_event_flow,
    event_filter,
    event_sink,
    event_source,
    event_transform,
)
from goldentooth_agent.flow_engine.main import Flow


class TestSyncEventFlow:
    """Test suite for SyncEventFlow class."""

    def test_sync_event_flow_creation(self) -> None:
        """Test basic SyncEventFlow creation."""
        event_flow = SyncEventFlow[str]("test_event")

        assert event_flow.event_name == "test_event"
        assert isinstance(event_flow.emitter, EventEmitter)

    def test_sync_event_flow_with_custom_emitter(self) -> None:
        """Test SyncEventFlow with custom emitter."""
        custom_emitter = EventEmitter()
        event_flow = SyncEventFlow[str]("test_event", custom_emitter)

        assert event_flow.event_name == "test_event"
        assert event_flow.emitter is custom_emitter

    def test_sync_event_flow_emit_and_listen(self) -> None:
        """Test emitting and listening to synchronous events."""
        event_flow = SyncEventFlow[str]("test_event")
        received_data = []

        def handler(data: str) -> None:
            received_data.append(data)

        event_flow.on(handler)
        event_flow.emit("hello")
        event_flow.emit("world")

        assert received_data == ["hello", "world"]

    def test_sync_event_flow_once_handler(self) -> None:
        """Test one-time event handler."""
        event_flow = SyncEventFlow[str]("test_event")
        received_data = []

        def handler(data: str) -> None:
            received_data.append(data)

        event_flow.once(handler)
        event_flow.emit("first")
        event_flow.emit("second")

        assert received_data == ["first"]

    def test_sync_event_flow_remove_handler(self) -> None:
        """Test removing event handlers."""
        event_flow = SyncEventFlow[str]("test_event")
        received_data = []

        def handler(data: str) -> None:
            received_data.append(data)

        event_flow.on(handler)
        event_flow.emit("before_remove")

        event_flow.off(handler)
        event_flow.emit("after_remove")

        assert received_data == ["before_remove"]

    def test_sync_event_flow_remove_all_listeners(self) -> None:
        """Test removing all event listeners."""
        event_flow = SyncEventFlow[str]("test_event")
        received_data = []

        def handler1(data: str) -> None:
            received_data.append(f"h1:{data}")

        def handler2(data: str) -> None:
            received_data.append(f"h2:{data}")

        event_flow.on(handler1)
        event_flow.on(handler2)
        event_flow.emit("before_remove")

        event_flow.remove_all_listeners()
        event_flow.emit("after_remove")

        assert received_data == ["h1:before_remove", "h2:before_remove"]

    def test_sync_event_flow_listeners_info(self) -> None:
        """Test getting listener information."""
        event_flow = SyncEventFlow[str]("test_event")

        def handler1(data: str) -> None:
            pass

        def handler2(data: str) -> None:
            pass

        assert event_flow.listener_count() == 0
        assert event_flow.listeners() == []

        event_flow.on(handler1)
        event_flow.on(handler2)

        assert event_flow.listener_count() == 2
        assert len(event_flow.listeners()) == 2
        assert handler1 in event_flow.listeners()
        assert handler2 in event_flow.listeners()

    @pytest.mark.asyncio
    async def test_sync_event_flow_as_flow(self) -> None:
        """Test converting SyncEventFlow to Flow."""
        event_flow = SyncEventFlow[str]("test_event")
        flow = event_flow.as_flow()

        assert isinstance(flow, Flow)
        assert flow.name == "from_emitter"

        # Test the flow receives events
        received_data = []

        async def collect_events() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for event_data in flow(empty_stream()):
                received_data.append(event_data)
                count += 1
                if count >= 2:  # Stop after 2 events to avoid infinite loop
                    break

        # Start the flow collection task
        collection_task = asyncio.create_task(collect_events())

        # Give the flow time to set up
        await asyncio.sleep(0.01)

        # Emit some events
        event_flow.emit("event1")
        event_flow.emit("event2")

        # Wait for collection to complete
        await collection_task

        assert received_data == ["event1", "event2"]


class TestAsyncEventFlow:
    """Test suite for AsyncEventFlow class."""

    def test_async_event_flow_creation(self) -> None:
        """Test basic AsyncEventFlow creation."""
        event_flow = AsyncEventFlow[str]("test_event")

        assert event_flow.event_name == "test_event"
        assert isinstance(event_flow.emitter, AsyncIOEventEmitter)

    def test_async_event_flow_with_custom_emitter(self) -> None:
        """Test AsyncEventFlow with custom emitter."""
        custom_emitter = AsyncIOEventEmitter()
        event_flow = AsyncEventFlow[str]("test_event", custom_emitter)

        assert event_flow.event_name == "test_event"
        assert event_flow.emitter is custom_emitter

    @pytest.mark.asyncio
    async def test_async_event_flow_emit_and_listen(self) -> None:
        """Test emitting and listening to asynchronous events."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        async def handler(data: str) -> None:
            received_data.append(data)

        await event_flow.on(handler)
        event_flow.emit("hello")
        event_flow.emit("world")

        # Give async handlers time to process
        await asyncio.sleep(0.01)

        assert received_data == ["hello", "world"]

    @pytest.mark.asyncio
    async def test_async_event_flow_sync_handler(self) -> None:
        """Test async event flow with synchronous handler."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        def sync_handler(data: str) -> None:
            received_data.append(data)

        await event_flow.on(sync_handler)
        event_flow.emit("sync_test")

        # Give handlers time to process
        await asyncio.sleep(0.01)

        assert received_data == ["sync_test"]

    @pytest.mark.asyncio
    async def test_async_event_flow_once_handler(self) -> None:
        """Test one-time async event handler."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        async def handler(data: str) -> None:
            received_data.append(data)

        await event_flow.once(handler)
        event_flow.emit("first")
        event_flow.emit("second")

        # Give handlers time to process
        await asyncio.sleep(0.01)

        assert received_data == ["first"]

    @pytest.mark.asyncio
    async def test_async_event_flow_remove_handler(self) -> None:
        """Test removing async event handlers."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        async def handler(data: str) -> None:
            received_data.append(data)

        await event_flow.on(handler)
        event_flow.emit("before_remove")

        await asyncio.sleep(0.01)  # Let handler process

        await event_flow.off(handler)
        event_flow.emit("after_remove")

        await asyncio.sleep(0.01)  # Let any remaining handlers process

        assert received_data == ["before_remove"]

    @pytest.mark.asyncio
    async def test_async_event_flow_remove_all_listeners(self) -> None:
        """Test removing all async event listeners."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        async def handler1(data: str) -> None:
            received_data.append(f"h1:{data}")

        async def handler2(data: str) -> None:
            received_data.append(f"h2:{data}")

        await event_flow.on(handler1)
        await event_flow.on(handler2)
        event_flow.emit("before_remove")

        await asyncio.sleep(0.01)  # Let handlers process

        await event_flow.remove_all_listeners()
        event_flow.emit("after_remove")

        await asyncio.sleep(0.01)  # Let any remaining handlers process

        assert received_data == ["h1:before_remove", "h2:before_remove"]

    def test_async_event_flow_listeners_info(self) -> None:
        """Test getting async listener information."""
        event_flow = AsyncEventFlow[str]("test_event")

        async def handler1(data: str) -> None:
            pass

        async def handler2(data: str) -> None:
            pass

        assert event_flow.listener_count() == 0
        assert event_flow.listeners() == []

        # Note: This is testing the info methods, not actually registering
        # handlers since that requires async context

    @pytest.mark.asyncio
    async def test_async_event_flow_as_flow(self) -> None:
        """Test converting AsyncEventFlow to Flow."""
        event_flow = AsyncEventFlow[str]("test_event")
        flow = event_flow.as_flow()

        assert isinstance(flow, Flow)
        assert flow.name == "from_emitter"

        # Test the flow receives events
        received_data = []

        async def collect_events() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for event_data in flow(empty_stream()):
                received_data.append(event_data)
                count += 1
                if count >= 2:  # Stop after 2 events to avoid infinite loop
                    break

        # Start the flow collection task
        collection_task = asyncio.create_task(collect_events())

        # Give the flow time to set up
        await asyncio.sleep(0.01)

        # Emit some events
        event_flow.emit("event1")
        event_flow.emit("event2")

        # Wait for collection to complete
        await collection_task

        assert received_data == ["event1", "event2"]


class TestEventFlowDerivatives:
    """Test suite for event Flow derivative functions."""

    @pytest.mark.asyncio
    async def test_event_source_async(self) -> None:
        """Test event_source function with async emitter."""
        flow = event_source("test_source_event", use_async=True)

        assert isinstance(flow, Flow)
        assert flow.name == "from_emitter"

        # Get the underlying event flow to emit events
        event_flow = AsyncEventFlow[str]("test_source_event")

        received_data = []

        async def collect_events() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for event_data in flow(empty_stream()):
                received_data.append(event_data)
                count += 1
                if count >= 2:
                    break

        collection_task = asyncio.create_task(collect_events())
        await asyncio.sleep(0.01)

        event_flow.emit("source1")
        event_flow.emit("source2")

        await collection_task
        assert received_data == ["source1", "source2"]

    @pytest.mark.asyncio
    async def test_event_source_sync(self) -> None:
        """Test event_source function with sync emitter."""
        flow = event_source("test_source_event_sync", use_async=False)

        assert isinstance(flow, Flow)

        # Get the underlying event flow to emit events
        event_flow = SyncEventFlow[str]("test_source_event_sync")

        received_data = []

        async def collect_events() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for event_data in flow(empty_stream()):
                received_data.append(event_data)
                count += 1
                if count >= 2:
                    break

        collection_task = asyncio.create_task(collect_events())
        await asyncio.sleep(0.01)

        event_flow.emit("sync1")
        event_flow.emit("sync2")

        await collection_task
        assert received_data == ["sync1", "sync2"]

    @pytest.mark.asyncio
    async def test_event_sink_async(self) -> None:
        """Test event_sink function with async emitter."""
        flow = event_sink("test_sink_event", use_async=True)

        assert isinstance(flow, Flow)
        assert flow.name == "event_sink(test_sink_event)"

        # Set up an event listener to capture emitted events
        event_flow = AsyncEventFlow[str]("test_sink_event")
        received_events = []

        async def event_handler(data: str) -> None:
            received_events.append(data)

        await event_flow.on(event_handler)

        # Test the sink flow
        input_data = ["item1", "item2", "item3"]

        async def input_stream():
            for item in input_data:
                yield item

        output_data = []
        async for item in flow(input_stream()):
            output_data.append(item)

        # Give async handlers time to process
        await asyncio.sleep(0.01)

        # Verify items passed through unchanged
        assert output_data == input_data

        # Verify events were emitted
        assert received_events == input_data

    @pytest.mark.asyncio
    async def test_event_sink_sync(self) -> None:
        """Test event_sink function with sync emitter."""
        flow = event_sink("test_sink_event_sync", use_async=False)

        assert isinstance(flow, Flow)

        # Set up an event listener to capture emitted events
        event_flow = SyncEventFlow[str]("test_sink_event_sync")
        received_events = []

        def event_handler(data: str) -> None:
            received_events.append(data)

        event_flow.on(event_handler)

        # Test the sink flow
        input_data = ["item1", "item2", "item3"]

        async def input_stream():
            for item in input_data:
                yield item

        output_data = []
        async for item in flow(input_stream()):
            output_data.append(item)

        # Verify items passed through unchanged
        assert output_data == input_data

        # Verify events were emitted
        assert received_events == input_data

    @pytest.mark.asyncio
    async def test_event_filter_async(self) -> None:
        """Test event_filter function with async emitter."""

        # Create a filter that only allows strings starting with "keep"
        def keep_filter(data: str) -> bool:
            return data.startswith("keep")

        flow = event_filter("test_filter_event", keep_filter, use_async=True)

        assert isinstance(flow, Flow)
        assert flow.name == "event_filter(test_filter_event)"

        # Get the underlying event flow to emit events
        event_flow = AsyncEventFlow[str]("test_filter_event")

        received_data = []

        async def collect_events() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for event_data in flow(empty_stream()):
                received_data.append(event_data)
                count += 1
                if count >= 2:  # Stop after getting 2 matching events
                    break

        collection_task = asyncio.create_task(collect_events())
        await asyncio.sleep(0.01)

        # Emit mixed events
        event_flow.emit("discard1")
        event_flow.emit("keep1")
        event_flow.emit("discard2")
        event_flow.emit("keep2")
        event_flow.emit("discard3")

        await collection_task
        assert received_data == ["keep1", "keep2"]

    @pytest.mark.asyncio
    async def test_event_transform_async(self) -> None:
        """Test event_transform function with async emitter."""

        # Create a transformer that converts to uppercase
        def uppercase_transform(data: str) -> str:
            return data.upper()

        flow = event_transform(
            "test_transform_event", uppercase_transform, use_async=True
        )

        assert isinstance(flow, Flow)
        assert flow.name == "event_transform(test_transform_event)"

        # Get the underlying event flow to emit events
        event_flow = AsyncEventFlow[str]("test_transform_event")

        received_data = []

        async def collect_events() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for event_data in flow(empty_stream()):
                received_data.append(event_data)
                count += 1
                if count >= 2:
                    break

        collection_task = asyncio.create_task(collect_events())
        await asyncio.sleep(0.01)

        event_flow.emit("hello")
        event_flow.emit("world")

        await collection_task
        assert received_data == ["HELLO", "WORLD"]


class TestEventFlowFactories:
    """Test suite for event flow factory functions."""

    def test_create_sync_event_flow(self) -> None:
        """Test create_sync_event_flow factory."""
        event_flow = create_sync_event_flow("factory_test")

        assert isinstance(event_flow, SyncEventFlow)
        assert event_flow.event_name == "factory_test"

    def test_create_async_event_flow(self) -> None:
        """Test create_async_event_flow factory."""
        event_flow = create_async_event_flow("factory_test")

        assert isinstance(event_flow, AsyncEventFlow)
        assert event_flow.event_name == "factory_test"

    def test_create_typed_sync_event_flow(self) -> None:
        """Test create_typed_sync_event_flow factory."""
        factory = create_typed_sync_event_flow("typed_test")

        # Create a typed event flow
        event_flow = factory(str)

        assert isinstance(event_flow, SyncEventFlow)
        assert event_flow.event_name == "typed_test"

    def test_create_typed_async_event_flow(self) -> None:
        """Test create_typed_async_event_flow factory."""
        factory = create_typed_async_event_flow("typed_test")

        # Create a typed event flow
        event_flow = factory(str)

        assert isinstance(event_flow, AsyncEventFlow)
        assert event_flow.event_name == "typed_test"


class TestEventFlowIntegration:
    """Integration tests for event flows with complex scenarios."""

    @pytest.mark.asyncio
    async def test_multiple_event_flows_interaction(self) -> None:
        """Test multiple event flows interacting with each other."""
        # Create source and sink flows
        source_flow = SyncEventFlow[str]("source")
        sink_flow = AsyncEventFlow[str]("sink")

        # Set up data collection
        received_from_source = []
        received_from_sink = []

        def source_handler(data: str) -> None:
            received_from_source.append(data)

        async def sink_handler(data: str) -> None:
            received_from_sink.append(data)

        source_flow.on(source_handler)
        await sink_flow.on(sink_handler)

        # Emit events
        source_flow.emit("source_event_1")
        sink_flow.emit("sink_event_1")
        source_flow.emit("source_event_2")
        sink_flow.emit("sink_event_2")

        # Give async handlers time to process
        await asyncio.sleep(0.01)

        assert received_from_source == ["source_event_1", "source_event_2"]
        assert received_from_sink == ["sink_event_1", "sink_event_2"]

    @pytest.mark.asyncio
    async def test_event_flow_with_complex_data(self) -> None:
        """Test event flows with complex data structures."""
        event_flow = AsyncEventFlow[dict[str, Any]]("complex_data")

        received_data = []

        async def handler(data: dict[str, Any]) -> None:
            received_data.append(data)

        await event_flow.on(handler)

        # Emit complex data
        complex_data1 = {"id": 1, "name": "test", "nested": {"value": 42}}
        complex_data2 = {"id": 2, "items": [1, 2, 3], "metadata": None}

        event_flow.emit(complex_data1)
        event_flow.emit(complex_data2)

        # Give handlers time to process
        await asyncio.sleep(0.01)

        assert received_data == [complex_data1, complex_data2]

    @pytest.mark.asyncio
    async def test_event_flow_error_handling(self) -> None:
        """Test event flow behavior with handler errors."""
        event_flow = AsyncEventFlow[str]("error_test")

        successful_calls = []
        error_calls = []

        async def good_handler(data: str) -> None:
            successful_calls.append(data)

        async def bad_handler(data: str) -> None:
            error_calls.append(data)
            raise ValueError(f"Handler error for: {data}")

        await event_flow.on(good_handler)
        await event_flow.on(bad_handler)

        # Emit event - pyee should handle errors gracefully
        event_flow.emit("test_data")

        # Give handlers time to process
        await asyncio.sleep(0.01)

        # Good handler should still work despite bad handler errors
        assert successful_calls == ["test_data"]
        assert error_calls == ["test_data"]

    @pytest.mark.asyncio
    async def test_flow_chaining_with_events(self) -> None:
        """Test chaining flows with event emission and consumption."""
        # Create a flow that emits events for each item
        sink_flow = event_sink("chain_test", use_async=True)

        # Create a flow that listens to those events and transforms them
        transform_flow = event_transform(
            "chain_test", lambda x: f"processed_{x}", use_async=True
        )

        # Set up data collection from the transform flow
        transformed_data = []

        async def collect_transformed() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for data in transform_flow(empty_stream()):
                transformed_data.append(data)
                count += 1
                if count >= 3:
                    break

        # Start collection
        collection_task = asyncio.create_task(collect_transformed())
        await asyncio.sleep(0.01)

        # Process data through the sink flow
        input_data = ["item1", "item2", "item3"]

        async def input_stream():
            for item in input_data:
                yield item

        passthrough_data = []
        async for item in sink_flow(input_stream()):
            passthrough_data.append(item)

        # Wait for transformed data collection
        await collection_task

        # Verify both flows worked
        assert passthrough_data == input_data
        assert transformed_data == [
            "processed_item1",
            "processed_item2",
            "processed_item3",
        ]
