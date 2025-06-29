"""Basic tests for event Flow integration without complex async patterns."""

from __future__ import annotations

import asyncio

import pytest
from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from goldentooth_agent.core.event.flow import (
    AsyncEventFlow,
    SyncEventFlow,
    create_async_event_flow,
    create_sync_event_flow,
    event_sink,
)
from goldentooth_agent.flow_engine.main import Flow


class TestBasicEventFlow:
    """Basic tests for event flow functionality."""

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

    def test_sync_event_flow_listeners_info(self) -> None:
        """Test getting listener information."""
        event_flow = SyncEventFlow[str]("unique_listener_test_event")

        def handler1(data: str) -> None:
            pass

        def handler2(data: str) -> None:
            pass

        # Clean up any existing listeners first
        event_flow.remove_all_listeners()

        assert event_flow.listener_count() == 0
        assert event_flow.listeners() == []

        event_flow.on(handler1)
        event_flow.on(handler2)

        assert event_flow.listener_count() == 2
        assert len(event_flow.listeners()) == 2
        assert handler1 in event_flow.listeners()
        assert handler2 in event_flow.listeners()

        # Clean up after test
        event_flow.remove_all_listeners()

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

    def test_factory_functions(self) -> None:
        """Test factory functions."""
        sync_flow = create_sync_event_flow("sync_test")
        async_flow = create_async_event_flow("async_test")

        assert isinstance(sync_flow, SyncEventFlow)
        assert sync_flow.event_name == "sync_test"

        assert isinstance(async_flow, AsyncEventFlow)
        assert async_flow.event_name == "async_test"

    @pytest.mark.asyncio
    async def test_event_sink_basic_functionality(self) -> None:
        """Test basic event sink functionality with simple data flow."""
        # Create an event sink
        sink_flow = event_sink("test_sink", use_async=True)

        # Set up an event listener to capture emitted events
        event_flow = AsyncEventFlow[str]("test_sink")
        received_events = []

        async def event_handler(data: str) -> None:
            received_events.append(data)

        await event_flow.on(event_handler)

        # Create input data and process through sink
        input_data = ["item1", "item2", "item3"]

        # Create input stream manually
        async def input_stream():
            for item in input_data:
                yield item

        # Process through sink flow
        output_data = []
        async for item in sink_flow(input_stream()):
            output_data.append(item)

        # Give async handlers time to process
        await asyncio.sleep(0.01)

        # Verify items passed through unchanged
        assert output_data == input_data

        # Verify events were emitted
        assert received_events == input_data

    @pytest.mark.asyncio
    async def test_sync_event_flow_as_flow_basic(self) -> None:
        """Test converting SyncEventFlow to Flow with basic functionality."""
        event_flow = SyncEventFlow[str]("test_event")
        flow = event_flow.as_flow()

        assert isinstance(flow, Flow)
        assert flow.name == "from_emitter"

        # Test with a simple emit scenario
        received_data = []

        # Create task to collect exactly 2 events
        async def collect_two_events() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for event_data in flow(empty_stream()):
                received_data.append(event_data)
                count += 1
                if count >= 2:
                    break

        # Start collection
        collection_task = asyncio.create_task(collect_two_events())

        # Give the flow time to set up
        await asyncio.sleep(0.01)

        # Emit events
        event_flow.emit("event1")
        event_flow.emit("event2")

        # Wait for collection to complete
        await collection_task

        assert received_data == ["event1", "event2"]

    @pytest.mark.asyncio
    async def test_flow_integration_with_standard_operations(self) -> None:
        """Test event flows work with standard Flow operations."""
        # Create an event source
        event_emitter = SyncEventFlow[int]("numbers")
        source_flow = event_emitter.as_flow()

        # Chain with standard Flow operations
        processed_flow = source_flow.map(lambda x: x * 2).filter(lambda x: x > 5)

        # Collect results
        results = []

        async def collect_results() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for result in processed_flow(empty_stream()):
                results.append(result)
                count += 1
                if count >= 2:  # Stop after getting 2 results
                    break

        # Start collection
        collection_task = asyncio.create_task(collect_results())
        await asyncio.sleep(0.01)

        # Emit numbers - only 3 and 4 should result in values > 5 after doubling
        event_emitter.emit(1)  # 1*2 = 2, filtered out
        event_emitter.emit(3)  # 3*2 = 6, kept
        event_emitter.emit(4)  # 4*2 = 8, kept
        event_emitter.emit(2)  # 2*2 = 4, filtered out

        await collection_task

        assert results == [6, 8]
