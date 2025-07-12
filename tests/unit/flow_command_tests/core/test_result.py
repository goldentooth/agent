from __future__ import annotations

import time
from typing import Any

import pytest

from flow_command.core.result import FlowCommandResult


class TestFlowCommandResult:
    """Test suite for FlowCommandResult generic result type."""

    def test_success_result_basic(self) -> None:
        """FlowCommandResult should create successful result."""
        result = FlowCommandResult.success_result("test_data")
        assert result.success is True
        assert result.data == "test_data"
        assert result.error is None
        assert result.execution_time == 0.0

    def test_success_result_with_timing(self) -> None:
        """FlowCommandResult should support execution timing."""
        result = FlowCommandResult.success_result("test_data", 1.5)
        assert result.success is True
        assert result.data == "test_data"
        assert result.execution_time == 1.5

    def test_error_result_basic(self) -> None:
        """FlowCommandResult should create error result."""
        result: FlowCommandResult[str] = FlowCommandResult.error_result("Test error")
        assert result.success is False
        assert result.data is None
        assert result.error == "Test error"
        assert result.execution_time == 0.0

    def test_error_result_with_timing(self) -> None:
        """FlowCommandResult should support error timing."""
        result: FlowCommandResult[str] = FlowCommandResult.error_result(
            "Test error", 2.5
        )
        assert result.success is False
        assert result.error == "Test error"
        assert result.execution_time == 2.5

    def test_to_json_success(self) -> None:
        """FlowCommandResult should serialize to JSON."""
        result: FlowCommandResult[str] = FlowCommandResult(
            success=True,
            data="test_data",
            execution_time=1.0,
            metadata={"key": "value"},
        )
        json_data = result.to_json()
        expected: dict[str, Any] = {
            "success": True,
            "data": "test_data",
            "error": None,
            "metadata": {"key": "value"},
            "execution_time": 1.0,
        }
        assert json_data == expected

    def test_to_json_error(self) -> None:
        """FlowCommandResult should serialize error to JSON."""
        result: FlowCommandResult[str] = FlowCommandResult(
            success=False, error="Test error", execution_time=0.5
        )
        json_data = result.to_json()
        expected: dict[str, Any] = {
            "success": False,
            "data": None,
            "error": "Test error",
            "metadata": {},
            "execution_time": 0.5,
        }
        assert json_data == expected

    def test_timed_execution_success(self) -> None:
        """FlowCommandResult should time function execution."""

        def test_function(value: str) -> str:
            time.sleep(0.01)  # Small delay for timing
            return f"processed_{value}"

        result: FlowCommandResult[str] = FlowCommandResult.timed_execution(
            test_function, "test"
        )
        assert result.success is True
        assert result.data == "processed_test"
        assert result.error is None
        assert result.execution_time > 0.0

    def test_timed_execution_error(self) -> None:
        """FlowCommandResult should handle function exceptions."""

        def failing_function() -> None:
            raise ValueError("Test exception")

        result: FlowCommandResult[None] = FlowCommandResult.timed_execution(
            failing_function
        )
        assert result.success is False
        assert result.data is None
        assert result.error == "Test exception"
        assert result.execution_time > 0.0

    def test_metadata_default(self) -> None:
        """FlowCommandResult should have empty metadata by default."""
        result: FlowCommandResult[Any] = FlowCommandResult(success=True)
        assert result.metadata == {}

    def test_metadata_custom(self) -> None:
        """FlowCommandResult should support custom metadata."""
        metadata = {"operation": "test", "user_id": "123"}
        result: FlowCommandResult[Any] = FlowCommandResult(
            success=True, metadata=metadata
        )
        assert result.metadata == metadata

    def test_generic_typing(self) -> None:
        """FlowCommandResult should support generic typing."""
        # Test with string type
        str_result: FlowCommandResult[str] = FlowCommandResult.success_result("hello")
        assert str_result.data == "hello"

        # Test with list type
        list_result: FlowCommandResult[list[int]] = FlowCommandResult.success_result(
            [1, 2, 3]
        )
        assert list_result.data == [1, 2, 3]

        # Test with dict type
        dict_result: FlowCommandResult[dict[str, Any]] = (
            FlowCommandResult.success_result({"key": "value"})
        )
        assert dict_result.data == {"key": "value"}
