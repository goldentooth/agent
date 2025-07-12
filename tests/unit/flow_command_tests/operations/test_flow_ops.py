from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flow_command.core.context import FlowCommandContext
from flow_command.core.exceptions import FlowCommandError
from flow_command.core.flow_info import FlowInfo
from flow_command.core.result import FlowCommandResult
from flow_command.operations.flow_ops import (
    flow_list_implementation,
    flow_run_implementation,
    flow_search_implementation,
)


class TestFlowListImplementation:
    """Test suite for flow_list_implementation."""

    def test_flow_list_basic(self) -> None:
        """flow_list_implementation should list flows from registry."""
        context = FlowCommandContext.from_test()

        # Mock the registry to return test flows
        mock_registry = Mock()
        mock_registry.list.return_value = ["flow1", "flow2"]
        mock_registry.categories = {}
        mock_registry.tags = {}
        mock_registry.metadata = {}

        with patch.object(context, "flow_registry", mock_registry):
            result = flow_list_implementation(context=context)

        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 2
        assert result.data[0].name == "flow1"
        assert result.data[1].name == "flow2"
        assert result.error is None

    def test_flow_list_with_category(self) -> None:
        """flow_list_implementation should filter by category."""
        context = FlowCommandContext.from_test()

        mock_registry = Mock()
        mock_registry.list.return_value = ["nlp_flow1", "nlp_flow2"]
        mock_registry.categories = {"nlp": ["nlp_flow1", "nlp_flow2"]}
        mock_registry.tags = {}
        mock_registry.metadata = {}

        with patch.object(context, "flow_registry", mock_registry):
            result = flow_list_implementation(category="nlp", context=context)

        mock_registry.list.assert_called_once_with(category="nlp")
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 2
        assert all(flow.category == "nlp" for flow in result.data)

    def test_flow_list_with_tag_ignored(self) -> None:
        """flow_list_implementation should ignore tag parameter (not implemented)."""
        context = FlowCommandContext.from_test()

        mock_registry = Mock()
        mock_registry.list.return_value = ["flow1"]
        mock_registry.categories = {}
        mock_registry.tags = {}
        mock_registry.metadata = {}

        with patch.object(context, "flow_registry", mock_registry):
            result = flow_list_implementation(tag="test", context=context)

        # Tag filtering is not implemented, so it should call list without tag
        mock_registry.list.assert_called_once_with(category=None)
        assert result.success is True

    def test_flow_list_no_context(self) -> None:
        """flow_list_implementation should create test context if none provided."""
        with patch(
            "flow_command.operations.flow_ops.FlowCommandContext.from_test"
        ) as mock_from_test:
            mock_context = Mock()
            mock_context.flow_registry.list.return_value = ["flow1"]
            mock_context.flow_registry.categories = {}
            mock_context.flow_registry.tags = {}
            mock_context.flow_registry.metadata = {}
            mock_from_test.return_value = mock_context

            result = flow_list_implementation()

        mock_from_test.assert_called_once()
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0].name == "flow1"

    def test_flow_list_registry_error(self) -> None:
        """flow_list_implementation should handle registry errors."""
        context = FlowCommandContext.from_test()

        with patch.object(
            context.flow_registry, "list", side_effect=Exception("Registry error")
        ):
            result = flow_list_implementation(context=context)

        assert result.success is False
        assert result.error is not None
        assert "Failed to list flows: Registry error" in result.error


class TestFlowSearchImplementation:
    """Test suite for flow_search_implementation."""

    def test_flow_search_basic(self) -> None:
        """flow_search_implementation should search flows in registry."""
        context = FlowCommandContext.from_test()

        mock_registry = Mock()
        mock_registry.search.return_value = ["matching_flow"]
        mock_registry.categories = {}
        mock_registry.tags = {}
        mock_registry.metadata = {}

        with patch.object(context, "flow_registry", mock_registry):
            result = flow_search_implementation("test_query", context=context)

        mock_registry.search.assert_called_once_with("test_query")
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0].name == "matching_flow"

    def test_flow_search_no_context(self) -> None:
        """flow_search_implementation should create test context if none provided."""
        with patch(
            "flow_command.operations.flow_ops.FlowCommandContext.from_test"
        ) as mock_from_test:
            mock_context = Mock()
            mock_context.flow_registry.search.return_value = ["flow1"]
            mock_context.flow_registry.categories = {}
            mock_context.flow_registry.tags = {}
            mock_context.flow_registry.metadata = {}
            mock_from_test.return_value = mock_context

            result = flow_search_implementation("query")

        mock_from_test.assert_called_once()
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0].name == "flow1"

    def test_flow_search_registry_error(self) -> None:
        """flow_search_implementation should handle registry errors."""
        context = FlowCommandContext.from_test()

        with patch.object(
            context.flow_registry, "search", side_effect=Exception("Search error")
        ):
            result = flow_search_implementation("query", context=context)

        assert result.success is False
        assert result.error is not None
        assert "Failed to search flows: Search error" in result.error


class TestFlowRunImplementation:
    """Test suite for flow_run_implementation."""

    def test_flow_run_basic(self) -> None:
        """flow_run_implementation should execute flow successfully."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()

        # Mock the registry and flow execution
        with (
            patch.object(
                context.flow_registry, "get", return_value=mock_flow
            ) as mock_get,
            patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run,
        ):

            mock_result = FlowCommandResult.success_result(["output1", "output2"])
            mock_run.return_value = mock_result

            result = flow_run_implementation("test_flow", context=context)

        mock_get.assert_called_once_with("test_flow")
        mock_run.assert_called_once_with(mock_flow, [], context)
        assert result.success is True
        assert result.data == ["output1", "output2"]

    def test_flow_run_flow_not_found(self) -> None:
        """flow_run_implementation should handle missing flow."""
        context = FlowCommandContext.from_test()

        with patch.object(context.flow_registry, "get", return_value=None):
            result = flow_run_implementation("missing_flow", context=context)

        assert result.success is False
        assert result.error is not None
        assert "Flow 'missing_flow' not found" in result.error

    def test_flow_run_with_json_file(self) -> None:
        """flow_run_implementation should load JSON input files."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()

        # Create temporary JSON file
        test_data = ["item1", "item2", "item3"]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            with (
                patch.object(context.flow_registry, "get", return_value=mock_flow),
                patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run,
            ):

                mock_result = FlowCommandResult.success_result(["processed"])
                mock_run.return_value = mock_result

                result = flow_run_implementation(
                    "test_flow", input_file=temp_path, context=context
                )

            # Should have called run_flow_sync with the loaded JSON data
            mock_run.assert_called_once_with(mock_flow, test_data, context)
            assert result.success is True
        finally:
            temp_path.unlink()  # Clean up

    def test_flow_run_with_text_file(self) -> None:
        """flow_run_implementation should load text input files."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()

        # Create temporary text file
        test_content = "line1\nline2\nline3"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(test_content)
            temp_path = Path(f.name)

        try:
            with (
                patch.object(context.flow_registry, "get", return_value=mock_flow),
                patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run,
            ):

                mock_result = FlowCommandResult.success_result(["processed"])
                mock_run.return_value = mock_result

                result = flow_run_implementation(
                    "test_flow", input_file=temp_path, context=context
                )

            # Should have called run_flow_sync with lines from the file
            expected_lines = ["line1", "line2", "line3"]
            mock_run.assert_called_once_with(mock_flow, expected_lines, context)
            assert result.success is True
        finally:
            temp_path.unlink()  # Clean up

    def test_flow_run_with_input_data_list(self) -> None:
        """flow_run_implementation should handle list input data."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()
        input_data = ["item1", "item2"]

        with (
            patch.object(context.flow_registry, "get", return_value=mock_flow),
            patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run,
        ):

            mock_result = FlowCommandResult.success_result(["processed"])
            mock_run.return_value = mock_result

            result = flow_run_implementation(
                "test_flow", input_data=input_data, context=context
            )

        mock_run.assert_called_once_with(mock_flow, input_data, context)
        assert result.success is True

    def test_flow_run_with_input_data_single(self) -> None:
        """flow_run_implementation should handle single input data."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()
        input_data = "single_item"

        with (
            patch.object(context.flow_registry, "get", return_value=mock_flow),
            patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run,
        ):

            mock_result = FlowCommandResult.success_result(["processed"])
            mock_run.return_value = mock_result

            result = flow_run_implementation(
                "test_flow", input_data=input_data, context=context
            )

        # Single item should be wrapped in list
        mock_run.assert_called_once_with(mock_flow, ["single_item"], context)
        assert result.success is True

    def test_flow_run_with_json_file_single_item(self) -> None:
        """flow_run_implementation should handle JSON file with single item."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()

        # Create temporary JSON file with single item
        test_data = "single_string"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            with (
                patch.object(context.flow_registry, "get", return_value=mock_flow),
                patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run,
            ):

                mock_result = FlowCommandResult.success_result(["processed"])
                mock_run.return_value = mock_result

                result = flow_run_implementation(
                    "test_flow", input_file=temp_path, context=context
                )

            # Single JSON item should be wrapped in list
            mock_run.assert_called_once_with(mock_flow, ["single_string"], context)
            assert result.success is True
        finally:
            temp_path.unlink()  # Clean up

    def test_flow_run_nonexistent_file(self) -> None:
        """flow_run_implementation should handle nonexistent input files."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()
        nonexistent_path = Path("/nonexistent/file.json")

        with (
            patch.object(context.flow_registry, "get", return_value=mock_flow),
            patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run,
        ):

            mock_result = FlowCommandResult.success_result(["processed"])
            mock_run.return_value = mock_result

            result = flow_run_implementation(
                "test_flow", input_file=nonexistent_path, context=context
            )

        # Should use empty list when file doesn't exist
        mock_run.assert_called_once_with(mock_flow, [], context)
        assert result.success is True

    def test_flow_run_no_context(self) -> None:
        """flow_run_implementation should create test context if none provided."""
        with patch(
            "flow_command.operations.flow_ops.FlowCommandContext.from_test"
        ) as mock_from_test:
            mock_context = Mock()
            mock_flow = Mock()
            mock_context.flow_registry.get.return_value = mock_flow
            mock_from_test.return_value = mock_context

            with patch("flow_command.operations.flow_ops.run_flow_sync") as mock_run:
                mock_result = FlowCommandResult.success_result(["output"])
                mock_run.return_value = mock_result

                result = flow_run_implementation("test_flow")

        mock_from_test.assert_called_once()
        assert result.success is True

    def test_flow_run_execution_error(self) -> None:
        """flow_run_implementation should handle execution errors."""
        context = FlowCommandContext.from_test()
        mock_flow = Mock()

        with (
            patch.object(context.flow_registry, "get", return_value=mock_flow),
            patch(
                "flow_command.operations.flow_ops.run_flow_sync",
                side_effect=Exception("Execution error"),
            ),
        ):

            result = flow_run_implementation("test_flow", context=context)

        assert result.success is False
        assert result.error is not None
        assert "Failed to run flow: Execution error" in result.error
