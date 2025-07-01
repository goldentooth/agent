"""Tests for enhanced debugging utilities."""

import time
from unittest.mock import patch

import pytest

from goldentooth_agent.dev.debugging import (
    DebugContext,
    DebugStats,
    debug_operation,
    log_function_call,
)


class TestDebugStats:
    """Test the DebugStats dataclass."""

    def test_debug_stats_creation_minimal(self):
        """Test creating DebugStats with minimal required fields."""
        stats = DebugStats(operation_name="test_operation", duration=1.23, success=True)

        assert stats.operation_name == "test_operation"
        assert stats.duration == 1.23
        assert stats.success is True
        assert stats.error_type is None
        assert stats.error_message is None
        assert stats.metadata is None

    def test_debug_stats_creation_complete(self):
        """Test creating DebugStats with all fields."""
        metadata = {"key": "value", "count": 42}
        stats = DebugStats(
            operation_name="complex_operation",
            duration=2.45,
            success=False,
            error_type="ValueError",
            error_message="Something went wrong",
            metadata=metadata,
        )

        assert stats.operation_name == "complex_operation"
        assert stats.duration == 2.45
        assert stats.success is False
        assert stats.error_type == "ValueError"
        assert stats.error_message == "Something went wrong"
        assert stats.metadata == metadata

    def test_debug_stats_equality(self):
        """Test DebugStats equality comparison."""
        stats1 = DebugStats("op", 1.0, True)
        stats2 = DebugStats("op", 1.0, True)
        stats3 = DebugStats("op", 2.0, True)

        assert stats1 == stats2
        assert stats1 != stats3


class TestDebugContext:
    """Test the DebugContext class."""

    def test_debug_context_initialization(self):
        """Test DebugContext initialization."""
        metadata = {"user_id": "123", "action": "test"}
        ctx = DebugContext("test_operation", **metadata)

        assert ctx.operation_name == "test_operation"
        assert ctx.metadata == metadata
        assert ctx.start_time is None
        assert ctx.stats is None

    def test_debug_context_successful_operation(self, caplog):
        """Test DebugContext with successful operation."""
        with caplog.at_level("DEBUG"):
            with DebugContext("successful_op", test_key="test_value") as ctx:
                time.sleep(0.01)  # Small delay to ensure measurable duration
                assert ctx.start_time is not None

        # Check that stats were created
        assert ctx.stats is not None
        assert ctx.stats.operation_name == "successful_op"
        assert ctx.stats.success is True
        assert ctx.stats.error_type is None
        assert ctx.stats.error_message is None
        assert ctx.stats.duration > 0
        assert ctx.stats.metadata == {"test_key": "test_value"}

        # Check logging
        assert "Starting successful_op" in caplog.text
        assert "successful_op completed in" in caplog.text

    def test_debug_context_failed_operation(self, caplog):
        """Test DebugContext with failed operation."""
        with caplog.at_level("DEBUG"):
            try:
                with DebugContext("failed_op", error_test=True) as ctx:
                    assert ctx.start_time is not None
                    raise ValueError("Test error")
            except ValueError:
                pass  # Expected exception

        # Check that stats were created for failure
        assert ctx.stats is not None
        assert ctx.stats.operation_name == "failed_op"
        assert ctx.stats.success is False
        assert ctx.stats.error_type == "ValueError"
        assert ctx.stats.error_message == "Test error"
        assert ctx.stats.duration > 0

        # Check error logging
        assert "Starting failed_op" in caplog.text
        assert "failed_op failed after" in caplog.text
        assert "ValueError" in caplog.text

    def test_add_metadata_during_execution(self):
        """Test adding metadata during execution."""
        with DebugContext("metadata_test", initial="value") as ctx:
            assert ctx.metadata == {"initial": "value"}

            ctx.add_metadata(added="new_value", count=42)
            assert ctx.metadata == {
                "initial": "value",
                "added": "new_value",
                "count": 42,
            }

            ctx.add_metadata(initial="updated")  # Should update existing
            assert ctx.metadata == {
                "initial": "updated",
                "added": "new_value",
                "count": 42,
            }

    def test_debug_context_zero_duration_edge_case(self):
        """Test DebugContext with very fast operation."""
        with DebugContext("fast_op") as ctx:
            pass  # No operation

        assert ctx.stats is not None
        assert ctx.stats.duration >= 0  # Should be non-negative

    def test_debug_context_nested_operations(self, caplog):
        """Test nested DebugContext operations."""
        with caplog.at_level("DEBUG"):
            with DebugContext("outer_op") as outer_ctx:
                with DebugContext("inner_op") as inner_ctx:
                    time.sleep(0.01)
                time.sleep(0.01)

        # Both operations should have stats
        assert outer_ctx.stats is not None
        assert inner_ctx.stats is not None
        assert outer_ctx.stats.duration > inner_ctx.stats.duration

        # Check logging for both operations
        assert "Starting outer_op" in caplog.text
        assert "Starting inner_op" in caplog.text
        assert "inner_op completed in" in caplog.text
        assert "outer_op completed in" in caplog.text


class TestDebugOperationContextManager:
    """Test the debug_operation context manager function."""

    def test_debug_operation_successful(self, caplog):
        """Test debug_operation context manager with successful operation."""
        with caplog.at_level("DEBUG"):
            with debug_operation("test_op", param="value") as ctx:
                assert isinstance(ctx, DebugContext)
                assert ctx.operation_name == "test_op"
                assert ctx.metadata == {"param": "value"}
                time.sleep(0.01)

        # Check that stats were created
        assert ctx.stats is not None
        assert ctx.stats.success is True
        assert "Starting test_op" in caplog.text
        assert "test_op completed in" in caplog.text

    def test_debug_operation_with_exception(self, caplog):
        """Test debug_operation context manager with exception."""
        with caplog.at_level("DEBUG"):
            try:
                with debug_operation("failing_op") as ctx:
                    raise RuntimeError("Test failure")
            except RuntimeError:
                pass  # Expected

        # Stats should still be created
        assert ctx.stats is not None
        assert ctx.stats.success is False
        assert ctx.stats.error_type == "RuntimeError"
        assert "failing_op failed after" in caplog.text

    def test_debug_operation_no_metadata(self, caplog):
        """Test debug_operation with no metadata."""
        with caplog.at_level("DEBUG"):
            with debug_operation("simple_op") as ctx:
                assert ctx.metadata == {}

        assert "Starting simple_op" in caplog.text

    def test_debug_operation_modifying_context(self):
        """Test modifying context during debug_operation."""
        with debug_operation("modifiable_op", initial="value") as ctx:
            ctx.add_metadata(runtime="added")
            assert ctx.metadata == {"initial": "value", "runtime": "added"}


class TestLogFunctionCall:
    """Test the log_function_call function."""

    def test_log_function_call_simple_args(self, caplog):
        """Test logging function call with simple arguments."""
        with caplog.at_level("DEBUG"):
            log_function_call("test_function", "arg1", 42, True, None)

        assert "Calling test_function" in caplog.text

    def test_log_function_call_with_kwargs(self, caplog):
        """Test logging function call with keyword arguments."""
        with caplog.at_level("DEBUG"):
            log_function_call("test_function", "positional", keyword="value", count=123)

        assert "Calling test_function" in caplog.text

    def test_log_function_call_complex_objects(self, caplog):
        """Test logging function call with complex objects."""

        class CustomObject:
            pass

        custom_obj = CustomObject()
        complex_dict = {"nested": {"data": "value"}}

        with caplog.at_level("DEBUG"):
            log_function_call(
                "complex_function", custom_obj, complex_dict, custom_kwarg=custom_obj
            )

        assert "Calling complex_function" in caplog.text

    def test_log_function_call_exception_handling(self, caplog):
        """Test logging function call when string conversion fails."""

        class ProblematicObject:
            def __repr__(self):
                raise RuntimeError("Cannot convert to string")

        problematic = ProblematicObject()

        with caplog.at_level("DEBUG"):
            log_function_call("test_function", problematic, kwarg=problematic)

        assert "Calling test_function" in caplog.text

    def test_log_function_call_no_args(self, caplog):
        """Test logging function call with no arguments."""
        with caplog.at_level("DEBUG"):
            log_function_call("no_args_function")

        assert "Calling no_args_function" in caplog.text

    def test_log_function_call_empty_string_args(self, caplog):
        """Test logging function call with empty string arguments."""
        with caplog.at_level("DEBUG"):
            log_function_call("test_function", "", empty_kwarg="")

        assert "Calling test_function" in caplog.text

    def test_log_function_call_float_args(self, caplog):
        """Test logging function call with float arguments."""
        with caplog.at_level("DEBUG"):
            log_function_call("math_function", 3.14159, precision=0.001)

        assert "Calling math_function" in caplog.text

    def test_log_function_call_large_number_of_args(self, caplog):
        """Test logging function call with many arguments."""
        args = list(range(20))  # 20 integer arguments
        kwargs = {f"key_{i}": f"value_{i}" for i in range(10)}  # 10 keyword arguments

        with caplog.at_level("DEBUG"):
            log_function_call("many_args_function", *args, **kwargs)

        assert "Calling many_args_function" in caplog.text
