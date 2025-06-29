"""Tests for observability flow combinators."""

import asyncio
import sys
from io import StringIO

import pytest

from goldentooth_agent.flow_engine.combinators.observability import (
    OnComplete,
    OnError,
    OnNext,
    inspect_stream,
    log_stream,
    materialize_stream,
    metrics_stream,
    trace_stream,
)


async def async_range(n: int):
    """Generate an async range of integers."""
    for i in range(n):
        yield i


async def failing_stream():
    """Stream that yields some items then fails."""
    yield 1
    yield 2
    raise ValueError("Test error")


class TestLogStream:
    """Tests for log_stream function."""

    @pytest.mark.asyncio
    async def test_log_basic(self):
        """Test basic logging functionality."""
        log_flow = log_stream("test_logger")
        assert "log_stream(test_logger)" in log_flow.name

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            input_stream = async_range(3)
            result_stream = log_flow(input_stream)
            values = [item async for item in result_stream]

            assert values == [0, 1, 2]
            # No output by default (DEBUG level)
            assert captured_output.getvalue() == ""
        finally:
            sys.stdout = old_stdout

    @pytest.mark.asyncio
    async def test_log_with_prefix(self):
        """Test logging with prefix."""
        import logging

        log_flow = log_stream("test", prefix="[TEST] ", level=logging.INFO)

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            input_stream = async_range(2)
            result_stream = log_flow(input_stream)
            values = [item async for item in result_stream]

            assert values == [0, 1]
            output = captured_output.getvalue()
            assert "[TEST] 0" in output
            assert "[TEST] 1" in output
        finally:
            sys.stdout = old_stdout

    @pytest.mark.asyncio
    async def test_log_metadata(self):
        """Test log stream metadata."""
        import logging

        log_flow = log_stream("meta_test", prefix=">>", level=logging.WARNING)

        assert log_flow.metadata["prefix"] == ">>"
        assert log_flow.metadata["level"] == logging.WARNING


class TestTraceStream:
    """Tests for trace_stream function."""

    @pytest.mark.asyncio
    async def test_trace_basic(self):
        """Test basic tracing functionality."""
        traced_events = []

        def tracer(event: str, data):
            traced_events.append((event, data))

        trace_flow = trace_stream(tracer)
        assert "trace(tracer)" in trace_flow.name

        input_stream = async_range(2)
        result_stream = trace_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1]
        assert traced_events == [
            ("stream_start", None),
            ("item", 0),
            ("item", 1),
            ("stream_end", None),
        ]

    @pytest.mark.asyncio
    async def test_trace_with_error(self):
        """Test tracing with stream error."""
        traced_events = []

        def tracer(event: str, data):
            traced_events.append((event, data))

        trace_flow = trace_stream(tracer)

        with pytest.raises(ValueError) as exc_info:
            result_stream = trace_flow(failing_stream())
            _ = [item async for item in result_stream]

        assert str(exc_info.value) == "Test error"

        # Check traced events
        assert len(traced_events) == 5
        assert traced_events[0] == ("stream_start", None)
        assert traced_events[1] == ("item", 1)
        assert traced_events[2] == ("item", 2)
        assert traced_events[3][0] == "error"
        assert isinstance(traced_events[3][1], ValueError)
        assert traced_events[4] == ("stream_end", None)

    @pytest.mark.asyncio
    async def test_trace_empty_stream(self):
        """Test tracing empty stream."""
        traced_events = []

        def tracer(event: str, data):
            traced_events.append((event, data))

        trace_flow = trace_stream(tracer)

        async def empty_stream():
            if False:
                yield 0

        result_stream = trace_flow(empty_stream())
        values = [item async for item in result_stream]

        assert values == []
        assert traced_events == [("stream_start", None), ("stream_end", None)]


class TestMetricsStream:
    """Tests for metrics_stream function."""

    @pytest.mark.asyncio
    async def test_metrics_basic(self):
        """Test basic metrics collection."""
        metrics = []

        def counter(metric_name: str):
            metrics.append(metric_name)

        metrics_flow = metrics_stream(counter)
        assert "metrics(counter)" in metrics_flow.name

        input_stream = async_range(3)
        result_stream = metrics_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1, 2]
        assert metrics == [
            "stream.started",
            "stream.item",
            "stream.item",
            "stream.item",
            "stream.completed",
            "stream.total_items.3",
        ]

    @pytest.mark.asyncio
    async def test_metrics_with_error(self):
        """Test metrics collection with errors."""
        metrics = []

        def counter(metric_name: str):
            metrics.append(metric_name)

        metrics_flow = metrics_stream(counter)

        with pytest.raises(ValueError):
            result_stream = metrics_flow(failing_stream())
            _ = [item async for item in result_stream]

        assert "stream.started" in metrics
        assert metrics.count("stream.item") == 2
        assert "stream.error" in metrics
        assert "stream.completed" in metrics
        assert "stream.total_items.2" in metrics

    @pytest.mark.asyncio
    async def test_metrics_empty_stream(self):
        """Test metrics for empty stream."""
        metrics = []

        def counter(metric_name: str):
            metrics.append(metric_name)

        metrics_flow = metrics_stream(counter)

        async def empty_stream():
            if False:
                yield 0

        result_stream = metrics_flow(empty_stream())
        values = [item async for item in result_stream]

        assert values == []
        assert metrics == ["stream.started", "stream.completed", "stream.total_items.0"]


class TestInspectStream:
    """Tests for inspect_stream function."""

    @pytest.mark.asyncio
    async def test_inspect_basic(self):
        """Test basic inspection functionality."""
        inspections = []

        def inspector(item, context: dict):
            inspections.append((item, context.copy()))

        inspect_flow = inspect_stream(inspector)
        assert "inspect(inspector)" in inspect_flow.name

        input_stream = async_range(2)
        result_stream = inspect_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1]
        assert len(inspections) == 2

        # Check first inspection
        assert inspections[0][0] == 0
        assert inspections[0][1]["item_index"] == 0
        assert inspections[0][1]["stream_position"] == 1
        assert "elapsed_time" in inspections[0][1]

        # Check second inspection
        assert inspections[1][0] == 1
        assert inspections[1][1]["item_index"] == 1
        assert inspections[1][1]["stream_position"] == 2
        assert inspections[1][1]["elapsed_time"] > inspections[0][1]["elapsed_time"]

    @pytest.mark.asyncio
    async def test_inspect_with_delay(self):
        """Test inspection with time tracking."""
        inspections = []

        def inspector(item, context: dict):
            inspections.append((item, context.copy()))

        inspect_flow = inspect_stream(inspector)

        async def delayed_stream():
            yield "first"
            await asyncio.sleep(0.01)
            yield "second"

        result_stream = inspect_flow(delayed_stream())
        values = [item async for item in result_stream]

        assert values == ["first", "second"]

        # Elapsed time should increase
        assert inspections[1][1]["elapsed_time"] > inspections[0][1]["elapsed_time"]
        assert inspections[1][1]["elapsed_time"] >= 0.01


class TestMaterializeStream:
    """Tests for materialize_stream function."""

    @pytest.mark.asyncio
    async def test_materialize_basic(self):
        """Test basic materialization."""
        materialize_flow = materialize_stream()
        assert materialize_flow.name == "materialize"

        input_stream = async_range(2)
        result_stream = materialize_flow(input_stream)
        notifications = [item async for item in result_stream]

        assert len(notifications) == 3
        assert isinstance(notifications[0], OnNext)
        assert notifications[0].value == 0
        assert isinstance(notifications[1], OnNext)
        assert notifications[1].value == 1
        assert isinstance(notifications[2], OnComplete)

    @pytest.mark.asyncio
    async def test_materialize_with_error(self):
        """Test materialization with errors."""
        materialize_flow = materialize_stream()

        result_stream = materialize_flow(failing_stream())
        notifications = [item async for item in result_stream]

        assert len(notifications) == 4
        assert isinstance(notifications[0], OnNext)
        assert notifications[0].value == 1
        assert isinstance(notifications[1], OnNext)
        assert notifications[1].value == 2
        assert isinstance(notifications[2], OnError)
        assert isinstance(notifications[2].error, ValueError)
        assert str(notifications[2].error) == "Test error"
        assert isinstance(notifications[3], OnComplete)

    @pytest.mark.asyncio
    async def test_materialize_empty_stream(self):
        """Test materialization of empty stream."""
        materialize_flow = materialize_stream()

        async def empty_stream():
            if False:
                yield 0

        result_stream = materialize_flow(empty_stream())
        notifications = [item async for item in result_stream]

        assert len(notifications) == 1
        assert isinstance(notifications[0], OnComplete)

    @pytest.mark.asyncio
    async def test_notification_repr(self):
        """Test notification string representations."""
        on_next = OnNext(42)
        on_error = OnError(ValueError("test"))
        on_complete = OnComplete()

        assert repr(on_next) == "OnNext(42)"
        assert repr(on_error) == "OnError(test)"
        assert repr(on_complete) == "OnComplete()"
