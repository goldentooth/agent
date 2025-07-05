"""Tests for observability combinators."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any

import pytest

from flowengine.combinators.observability import (
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
from flowengine.flow import Flow


async def empty_stream() -> AsyncGenerator[int, None]:
    """Create an empty stream for testing."""
    return
    yield  # pragma: no cover


class TestStreamNotifications:
    """Test stream notification classes."""

    def test_on_next_creation(self) -> None:
        """Test OnNext notification creation."""
        notification = OnNext(42)
        assert notification.value == 42
        assert repr(notification) == "OnNext(42)"

    def test_on_error_creation(self) -> None:
        """Test OnError notification creation."""
        error = ValueError("test error")
        notification = OnError(error)
        assert notification.error is error
        assert repr(notification) == "OnError(test error)"

    def test_on_complete_creation(self) -> None:
        """Test OnComplete notification creation."""
        notification = OnComplete()
        assert repr(notification) == "OnComplete()"

    def test_stream_notification_inheritance(self) -> None:
        """Test that all notifications inherit from StreamNotification."""
        assert isinstance(OnNext(1), StreamNotification)
        assert isinstance(OnError(ValueError()), StreamNotification)
        assert isinstance(OnComplete(), StreamNotification)

    def test_stream_notification_abstract_repr(self) -> None:
        """Test the abstract base class repr method."""

        # Create a simple concrete subclass to test the base __repr__
        class TestNotification(StreamNotification):
            pass

        notification = TestNotification()
        assert repr(notification) == "TestNotification()"


class TestLogStream:
    """Test log_stream combinator."""

    async def get_sample_stream(self) -> AsyncGenerator[int, None]:
        """Create a sample stream."""
        for i in range(3):
            yield i

    @pytest.mark.asyncio
    async def test_log_stream_passes_items_through(self) -> None:
        """Test that log_stream passes items through unchanged."""
        log_flow: Flow[int, int] = log_stream("test")
        result_stream = log_flow(self.get_sample_stream())
        result: list[int] = [item async for item in result_stream]
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_log_stream_with_prefix(self) -> None:
        """Test log_stream with prefix."""
        log_flow: Flow[int, int] = log_stream("test", prefix="DEBUG: ")
        result_stream = log_flow(self.get_sample_stream())
        result: list[int] = [item async for item in result_stream]
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_log_stream_with_level(self) -> None:
        """Test log_stream with different levels."""
        log_flow: Flow[int, int] = log_stream("test", level=logging.INFO)
        result_stream = log_flow(self.get_sample_stream())
        result: list[int] = [item async for item in result_stream]
        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_log_stream_with_enabled_logging(self) -> None:
        """Test log_stream with logging enabled to ensure coverage."""
        import logging

        # Configure logging to capture the log output
        logger = logging.getLogger("flowengine.combinators.observability")
        logger.setLevel(logging.DEBUG)

        # Create a handler to capture logs
        import logging
        from io import StringIO

        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        try:
            log_flow: Flow[int, int] = log_stream("test", level=logging.DEBUG)
            result_stream = log_flow(self.get_sample_stream())
            result: list[int] = [item async for item in result_stream]
            assert result == [0, 1, 2]

            # Verify that logging actually occurred
            log_output = log_capture.getvalue()
            assert "0" in log_output or "1" in log_output or "2" in log_output
        finally:
            logger.removeHandler(handler)

    def test_log_stream_metadata(self) -> None:
        """Test log_stream metadata."""
        log_flow: Flow[int, int] = log_stream(
            "test", prefix="PREFIX: ", level=logging.INFO
        )
        assert log_flow.name == "log_stream(test)"
        assert log_flow.metadata["prefix"] == "PREFIX: "
        assert log_flow.metadata["level"] == logging.INFO

    @pytest.mark.asyncio
    async def test_log_stream_empty_stream(self) -> None:
        """Test log_stream with empty stream."""
        log_flow: Flow[int, int] = log_stream("test")
        result_stream = log_flow(empty_stream())
        result: list[int] = [item async for item in result_stream]
        assert result == []


class TestTraceStream:
    """Test trace_stream combinator."""

    async def get_sample_stream(self) -> AsyncGenerator[int, None]:
        """Create a sample stream."""
        for i in range(3):
            yield i

    @pytest.mark.asyncio
    async def test_trace_stream_passes_items_through(self) -> None:
        """Test that trace_stream passes items through unchanged."""
        trace_calls: list[tuple[str, Any]] = []

        def tracer(event_type: str, item: Any) -> None:
            trace_calls.append((event_type, item))

        trace_flow: Flow[int, int] = trace_stream(tracer)
        result_stream = trace_flow(self.get_sample_stream())
        result: list[int] = [item async for item in result_stream]

        assert result == [0, 1, 2]
        expected_calls = [
            ("stream_start", None),
            ("item", 0),
            ("item", 1),
            ("item", 2),
            ("stream_end", None),
        ]
        assert trace_calls == expected_calls

    @pytest.mark.asyncio
    async def test_trace_stream_with_error(self) -> None:
        """Test trace_stream with error in stream."""
        trace_calls: list[tuple[str, Any]] = []

        def tracer(event_type: str, item: Any) -> None:
            trace_calls.append((event_type, item))

        async def error_stream() -> AsyncGenerator[int, None]:
            yield 1
            raise ValueError("test error")

        trace_flow: Flow[int, int] = trace_stream(tracer)

        with pytest.raises(ValueError, match="test error"):
            result_stream = trace_flow(error_stream())
            [item async for item in result_stream]

        assert len(trace_calls) >= 3  # stream_start, item, error
        assert trace_calls[0] == ("stream_start", None)
        assert trace_calls[1] == ("item", 1)
        assert trace_calls[2][0] == "error"
        assert isinstance(trace_calls[2][1], ValueError)

    def test_trace_stream_metadata(self) -> None:
        """Test trace_stream metadata."""

        def tracer(event_type: str, item: Any) -> None:
            pass

        tracer.__name__ = "my_tracer"
        trace_flow: Flow[int, int] = trace_stream(tracer)
        assert trace_flow.name == "trace(my_tracer)"

    @pytest.mark.asyncio
    async def test_trace_stream_empty_stream(self) -> None:
        """Test trace_stream with empty stream."""
        trace_calls: list[tuple[str, Any]] = []

        def tracer(event_type: str, item: Any) -> None:
            trace_calls.append((event_type, item))

        trace_flow: Flow[int, int] = trace_stream(tracer)
        result_stream = trace_flow(empty_stream())
        result: list[int] = [item async for item in result_stream]

        assert result == []
        assert trace_calls == [("stream_start", None), ("stream_end", None)]


class TestMetricsStream:
    """Test metrics_stream combinator."""

    async def get_sample_stream(self) -> AsyncGenerator[int, None]:
        """Create a sample stream."""
        for i in range(3):
            yield i

    @pytest.mark.asyncio
    async def test_metrics_stream_passes_items_through(self) -> None:
        """Test that metrics_stream passes items through unchanged."""
        metrics_calls: list[str] = []

        def counter(metric_name: str) -> None:
            metrics_calls.append(metric_name)

        metrics_flow: Flow[int, int] = metrics_stream(counter)
        result_stream = metrics_flow(self.get_sample_stream())
        result: list[int] = [item async for item in result_stream]

        assert result == [0, 1, 2]
        expected_calls = [
            "stream.started",
            "stream.item",
            "stream.item",
            "stream.item",
            "stream.completed",
            "stream.total_items.3",
        ]
        assert metrics_calls == expected_calls

    @pytest.mark.asyncio
    async def test_metrics_stream_with_error(self) -> None:
        """Test metrics_stream with error in stream."""
        metrics_calls: list[str] = []

        def counter(metric_name: str) -> None:
            metrics_calls.append(metric_name)

        async def error_stream() -> AsyncGenerator[int, None]:
            yield 1
            raise ValueError("test error")

        metrics_flow: Flow[int, int] = metrics_stream(counter)

        with pytest.raises(ValueError, match="test error"):
            result_stream = metrics_flow(error_stream())
            [item async for item in result_stream]

        expected_calls = [
            "stream.started",
            "stream.item",
            "stream.error",
            "stream.completed",
            "stream.total_items.1",
        ]
        assert metrics_calls == expected_calls

    def test_metrics_stream_metadata(self) -> None:
        """Test metrics_stream metadata."""

        def counter(metric_name: str) -> None:
            pass

        counter.__name__ = "my_counter"
        metrics_flow: Flow[int, int] = metrics_stream(counter)
        assert metrics_flow.name == "metrics(my_counter)"

    @pytest.mark.asyncio
    async def test_metrics_stream_empty_stream(self) -> None:
        """Test metrics_stream with empty stream."""
        metrics_calls: list[str] = []

        def counter(metric_name: str) -> None:
            metrics_calls.append(metric_name)

        metrics_flow: Flow[int, int] = metrics_stream(counter)
        result_stream = metrics_flow(empty_stream())
        result: list[int] = [item async for item in result_stream]

        assert result == []
        expected_calls = [
            "stream.started",
            "stream.completed",
            "stream.total_items.0",
        ]
        assert metrics_calls == expected_calls


class TestInspectStream:
    """Test inspect_stream combinator."""

    async def get_sample_stream(self) -> AsyncGenerator[int, None]:
        """Create a sample stream."""
        for i in range(3):
            yield i

    @pytest.mark.asyncio
    async def test_inspect_stream_passes_items_through(self) -> None:
        """Test that inspect_stream passes items through unchanged."""
        inspect_calls: list[tuple[Any, dict[str, Any]]] = []

        def inspector(item: Any, context: dict[str, Any]) -> None:
            inspect_calls.append((item, context.copy()))

        inspect_flow: Flow[int, int] = inspect_stream(inspector)
        result_stream = inspect_flow(self.get_sample_stream())
        result: list[int] = [item async for item in result_stream]

        assert result == [0, 1, 2]
        assert len(inspect_calls) == 3

        # Check context metadata
        for i, (item, context) in enumerate(inspect_calls):
            assert item == i
            assert context["item_index"] == i
            assert context["stream_position"] == i + 1
            assert "elapsed_time" in context
            assert isinstance(context["elapsed_time"], (int, float))

    def test_inspect_stream_metadata(self) -> None:
        """Test inspect_stream metadata."""

        def inspector(item: Any, context: dict[str, Any]) -> None:
            pass

        inspector.__name__ = "my_inspector"
        inspect_flow: Flow[int, int] = inspect_stream(inspector)
        assert inspect_flow.name == "inspect(my_inspector)"

    @pytest.mark.asyncio
    async def test_inspect_stream_empty_stream(self) -> None:
        """Test inspect_stream with empty stream."""
        inspect_calls: list[tuple[Any, dict[str, Any]]] = []

        def inspector(item: Any, context: dict[str, Any]) -> None:
            inspect_calls.append((item, context.copy()))

        inspect_flow: Flow[int, int] = inspect_stream(inspector)
        result_stream = inspect_flow(empty_stream())
        result: list[int] = [item async for item in result_stream]

        assert result == []
        assert inspect_calls == []


class TestMaterializeStream:
    """Test materialize_stream combinator."""

    async def get_sample_stream(self) -> AsyncGenerator[int, None]:
        """Create a sample stream."""
        for i in range(3):
            yield i

    @pytest.mark.asyncio
    async def test_materialize_stream_normal_items(self) -> None:
        """Test materialize_stream with normal items."""
        materialize_flow: Flow[int, StreamNotification] = materialize_stream()
        result_stream = materialize_flow(self.get_sample_stream())
        result: list[StreamNotification] = [item async for item in result_stream]

        assert len(result) == 4  # 3 items + 1 completion
        assert isinstance(result[0], OnNext)
        assert isinstance(result[1], OnNext)
        assert isinstance(result[2], OnNext)
        assert isinstance(result[3], OnComplete)

        assert result[0].value == 0
        assert result[1].value == 1
        assert result[2].value == 2

    @pytest.mark.asyncio
    async def test_materialize_stream_with_error(self) -> None:
        """Test materialize_stream with error in stream."""

        async def error_stream() -> AsyncGenerator[int, None]:
            yield 1
            raise ValueError("test error")

        materialize_flow: Flow[int, StreamNotification] = materialize_stream()
        result_stream = materialize_flow(error_stream())
        result: list[StreamNotification] = [item async for item in result_stream]

        assert len(result) == 2  # 1 item + 1 error (no completion after error)
        assert isinstance(result[0], OnNext)
        assert isinstance(result[1], OnError)

        assert result[0].value == 1
        assert isinstance(result[1].error, ValueError)
        assert str(result[1].error) == "test error"

    def test_materialize_stream_metadata(self) -> None:
        """Test materialize_stream metadata."""
        materialize_flow: Flow[int, StreamNotification] = materialize_stream()
        assert materialize_flow.name == "materialize"

    @pytest.mark.asyncio
    async def test_materialize_stream_empty_stream(self) -> None:
        """Test materialize_stream with empty stream."""
        materialize_flow: Flow[int, StreamNotification] = materialize_stream()
        result_stream = materialize_flow(empty_stream())
        result: list[StreamNotification] = [item async for item in result_stream]

        assert len(result) == 1  # Just completion
        assert isinstance(result[0], OnComplete)
