from __future__ import annotations

from rich.console import Console

from flow_command.core.context import FlowCommandContext


class TestFlowCommandContext:
    """Test suite for FlowCommandContext universal command context."""

    def test_from_cli_basic(self) -> None:
        """FlowCommandContext.from_cli should create CLI context."""
        context = FlowCommandContext.from_cli()
        assert context.source == "cli"
        assert context.output_format == "text"
        assert context.plain_output is False
        assert context.interactive is True
        assert context.record_svg is False
        assert context.execution_timeout == 30.0
        assert context.user_id is None
        assert isinstance(context.console, Console)

    def test_from_cli_with_parameters(self) -> None:
        """FlowCommandContext.from_cli should accept custom parameters."""
        context = FlowCommandContext.from_cli(
            output_format="json",
            plain_output=True,
            interactive=False,
            record_svg=True,
            execution_timeout=60.0,
        )
        assert context.source == "cli"
        assert context.output_format == "json"
        assert context.plain_output is True
        assert context.interactive is False
        assert context.record_svg is True
        assert context.execution_timeout == 60.0

    def test_from_chat_basic(self) -> None:
        """FlowCommandContext.from_chat should create chat context."""
        context = FlowCommandContext.from_chat()
        assert context.source == "chat"
        assert context.output_format == "text"
        assert context.plain_output is False
        assert context.interactive is True
        assert context.record_svg is False
        assert context.execution_timeout == 30.0
        assert context.user_id is None

    def test_from_chat_with_parameters(self) -> None:
        """FlowCommandContext.from_chat should accept custom parameters."""
        context = FlowCommandContext.from_chat(
            output_format="table",
            user_id="test_user",
            execution_timeout=45.0,
        )
        assert context.source == "chat"
        assert context.output_format == "table"
        assert context.user_id == "test_user"
        assert context.execution_timeout == 45.0
        assert context.plain_output is False
        assert context.interactive is True
        assert context.record_svg is False

    def test_from_test_basic(self) -> None:
        """FlowCommandContext.from_test should create test context."""
        context = FlowCommandContext.from_test()
        assert context.source == "test"
        assert context.output_format == "text"
        assert context.plain_output is True
        assert context.interactive is False
        assert context.record_svg is False
        assert context.execution_timeout == 5.0
        assert context.user_id is None

    def test_from_test_with_parameters(self) -> None:
        """FlowCommandContext.from_test should accept custom parameters."""
        context = FlowCommandContext.from_test(
            output_format="json",
            execution_timeout=10.0,
        )
        assert context.source == "test"
        assert context.output_format == "json"
        assert context.execution_timeout == 10.0
        assert context.plain_output is True
        assert context.interactive is False
        assert context.record_svg is False

    def test_context_has_flow_registry(self) -> None:
        """FlowCommandContext should have access to flow registry."""
        context = FlowCommandContext.from_test()
        assert context.flow_registry is not None
        # Should be the global registry
        from flow.registry import flow_registry

        assert context.flow_registry is flow_registry

    def test_context_input_data_handling(self) -> None:
        """FlowCommandContext should handle input data properly."""
        test_data = ["item1", "item2"]
        context = FlowCommandContext.from_cli(input_data=test_data)
        assert context.input_data == test_data

    def test_context_console_customization(self) -> None:
        """FlowCommandContext should allow console customization."""
        custom_console = Console(width=80)
        context = FlowCommandContext(console=custom_console)
        assert context.console is custom_console
