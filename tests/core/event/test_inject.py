"""Tests for event injection module."""

from __future__ import annotations

import asyncio

import pytest
from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from goldentooth_agent.core.event.inject import (
    get_async_event_emitter,
    get_sync_event_emitter,
)


class TestEventInjection:
    """Test suite for event emitter injection."""

    def test_get_sync_event_emitter(self) -> None:
        """Test getting synchronous event emitter."""
        emitter = get_sync_event_emitter()

        assert isinstance(emitter, EventEmitter)

    def test_get_sync_event_emitter_singleton(self) -> None:
        """Test that sync event emitter is a singleton."""
        emitter1 = get_sync_event_emitter()
        emitter2 = get_sync_event_emitter()

        # Should be the same instance due to @lazy decorator
        assert emitter1 is emitter2

    def test_get_async_event_emitter(self) -> None:
        """Test getting asynchronous event emitter."""
        emitter = get_async_event_emitter()

        assert isinstance(emitter, AsyncIOEventEmitter)

    def test_get_async_event_emitter_singleton(self) -> None:
        """Test that async event emitter is a singleton."""
        emitter1 = get_async_event_emitter()
        emitter2 = get_async_event_emitter()

        # Should be the same instance due to @lazy decorator
        assert emitter1 is emitter2

    def test_sync_emitter_functionality(self) -> None:
        """Test basic functionality of injected sync emitter."""
        emitter = get_sync_event_emitter()
        received_data = []

        def handler(data: str) -> None:
            received_data.append(data)

        emitter.on("test_event", handler)
        emitter.emit("test_event", "test_data")

        assert received_data == ["test_data"]

    @pytest.mark.asyncio
    async def test_async_emitter_functionality(self) -> None:
        """Test basic functionality of injected async emitter."""
        emitter = get_async_event_emitter()
        received_data = []

        async def handler(data: str) -> None:
            received_data.append(data)

        emitter.on("test_event", handler)
        emitter.emit("test_event", "test_data")

        # Give handler time to process
        import asyncio

        await asyncio.sleep(0.01)

        assert received_data == ["test_data"]

    def test_emitters_are_separate_instances(self) -> None:
        """Test that sync and async emitters are separate instances."""
        sync_emitter = get_sync_event_emitter()
        async_emitter = get_async_event_emitter()

        assert sync_emitter is not async_emitter
        assert type(sync_emitter) is not type(async_emitter)

    @pytest.mark.asyncio
    async def test_emitters_cross_event_isolation(self) -> None:
        """Test that sync and async emitters don't interfere with each other."""
        sync_emitter = get_sync_event_emitter()
        async_emitter = get_async_event_emitter()

        sync_received = []
        async_received = []

        def sync_handler(data: str) -> None:
            sync_received.append(data)

        async def async_handler(data: str) -> None:
            async_received.append(data)

        # Register handlers for same event name on both emitters
        sync_emitter.on("shared_event", sync_handler)
        async_emitter.on("shared_event", async_handler)

        # Emit on sync emitter only
        sync_emitter.emit("shared_event", "sync_data")

        # Only sync handler should receive data
        assert sync_received == ["sync_data"]
        assert async_received == []

        # Emit on async emitter only
        async_emitter.emit("shared_event", "async_data")

        # Allow async handler to complete
        await asyncio.sleep(0.01)

        # Now both should have their respective data
        assert sync_received == ["sync_data"]
        assert async_received == ["async_data"]
