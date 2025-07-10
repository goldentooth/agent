"""Tests for core event flow classes."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from flow import Flow
from flow_events.flow import AsyncEventFlow, EventFlow, SyncEventFlow


class TestEventFlow:
    """Test suite for EventFlow base class."""

    def test_event_flow_initialization(self) -> None:
        """Test EventFlow base class initialization."""
        event_flow = EventFlow[str]("test_event")
        assert event_flow.event_name == "test_event"

    def test_event_flow_emit_not_implemented(self) -> None:
        """Test that EventFlow emit method raises NotImplementedError."""
        event_flow = EventFlow[str]("test_event")

        with pytest.raises(
            NotImplementedError, match="Subclasses must implement emit method"
        ):
            event_flow.emit("test_data")

    def test_event_flow_as_flow_not_implemented(self) -> None:
        """Test that EventFlow as_flow method raises NotImplementedError."""
        event_flow = EventFlow[str]("test_event")

        with pytest.raises(
            NotImplementedError, match="Subclasses must implement as_flow method"
        ):
            event_flow.as_flow()


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
        """Test one-time event handler registration."""
        event_flow = SyncEventFlow[str]("test_event")
        received_data = []

        def handler(data: str) -> None:
            received_data.append(data)

        event_flow.once(handler)
        event_flow.emit("first")
        event_flow.emit("second")

        # Should only receive the first emission
        assert received_data == ["first"]

    def test_sync_event_flow_remove_handler(self) -> None:
        """Test removing event handlers."""
        event_flow = SyncEventFlow[str]("test_event")
        received_data = []

        def handler(data: str) -> None:
            received_data.append(data)

        event_flow.on(handler)
        event_flow.emit("before_removal")

        event_flow.off(handler)
        event_flow.emit("after_removal")

        assert received_data == ["before_removal"]

    def test_sync_event_flow_remove_all_listeners(self) -> None:
        """Test removing all event listeners."""
        event_flow = SyncEventFlow[str]("test_event")
        received_data = []

        def handler1(data: str) -> None:
            received_data.append(f"handler1: {data}")

        def handler2(data: str) -> None:
            received_data.append(f"handler2: {data}")

        event_flow.on(handler1)
        event_flow.on(handler2)
        event_flow.emit("before_removal")

        event_flow.remove_all_listeners()
        event_flow.emit("after_removal")

        assert received_data == ["handler1: before_removal", "handler2: before_removal"]

    def test_sync_event_flow_listeners_and_count(self) -> None:
        """Test getting listeners and listener count."""
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
        listeners = event_flow.listeners()
        assert handler1 in listeners
        assert handler2 in listeners


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

        # Give handlers time to process
        await asyncio.sleep(0.01)

        assert received_data == ["hello", "world"]

    @pytest.mark.asyncio
    async def test_async_event_flow_once_handler(self) -> None:
        """Test one-time async event handler registration."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        async def handler(data: str) -> None:
            received_data.append(data)

        await event_flow.once(handler)
        event_flow.emit("first")
        event_flow.emit("second")

        # Give handlers time to process
        await asyncio.sleep(0.01)

        # Should only receive the first emission
        assert received_data == ["first"]

    @pytest.mark.asyncio
    async def test_async_event_flow_remove_handler(self) -> None:
        """Test removing async event handlers."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        async def handler(data: str) -> None:
            received_data.append(data)

        await event_flow.on(handler)
        event_flow.emit("before_removal")

        # Give handler time to process
        await asyncio.sleep(0.01)

        await event_flow.off(handler)
        event_flow.emit("after_removal")

        # Give any handlers time to process
        await asyncio.sleep(0.01)

        assert received_data == ["before_removal"]

    @pytest.mark.asyncio
    async def test_async_event_flow_remove_all_listeners(self) -> None:
        """Test removing all async event listeners."""
        event_flow = AsyncEventFlow[str]("test_event")
        received_data = []

        async def handler1(data: str) -> None:
            received_data.append(f"handler1: {data}")

        async def handler2(data: str) -> None:
            received_data.append(f"handler2: {data}")

        await event_flow.on(handler1)
        await event_flow.on(handler2)
        event_flow.emit("before_removal")

        # Give handlers time to process
        await asyncio.sleep(0.01)

        await event_flow.remove_all_listeners()
        event_flow.emit("after_removal")

        # Give any handlers time to process
        await asyncio.sleep(0.01)

        assert received_data == ["handler1: before_removal", "handler2: before_removal"]

    def test_async_event_flow_listeners_and_count(self) -> None:
        """Test getting async listeners and listener count."""
        event_flow = AsyncEventFlow[str]("test_event")

        assert event_flow.listener_count() == 0
        assert event_flow.listeners() == []

        # Note: We can't test adding handlers here without async context
        # That's covered in the async tests above

    def test_sync_event_flow_as_flow(self) -> None:
        """Test converting SyncEventFlow to Flow and basic functionality."""
        event_flow = SyncEventFlow[str]("test_event")
        flow = event_flow.as_flow()

        assert isinstance(flow, Flow)

        # Test that the flow can be used to register callbacks
        # (though we can't directly test the flow execution without complex setup)

    def test_async_event_flow_as_flow(self) -> None:
        """Test converting AsyncEventFlow to Flow and basic functionality."""
        event_flow = AsyncEventFlow[str]("test_event")
        flow = event_flow.as_flow()

        assert isinstance(flow, Flow)

        # Test that the flow can be used to register callbacks
        # (though we can't directly test the flow execution without complex setup)
