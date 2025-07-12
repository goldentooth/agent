"""Unit tests for chat command implementation."""

from unittest.mock import Mock

from context import Context
from context_flow.trampoline import SHOULD_EXIT_KEY
from goldentooth_agent.cli.commands.chat import (
    ChatInputHandler,
    chat_flow_implementation,
    chat_implementation,
)


class TestChatInputHandler:
    """Test the ChatInputHandler class."""

    def test_get_input_returns_user_text(self) -> None:
        """Test that ChatInputHandler can get user input."""
        # Arrange
        mock_input_source = Mock()
        mock_input_source.get_input.return_value = "Hello, world!"
        handler = ChatInputHandler(input_source=mock_input_source)

        # Act
        result = handler.get_input()

        # Assert
        assert result == "Hello, world!"

    def test_is_exit_command_recognizes_quit(self) -> None:
        """Test that ChatInputHandler recognizes /quit as exit command."""
        # Arrange
        handler = ChatInputHandler()

        # Act & Assert
        assert handler.is_exit_command("/quit") is True
        assert handler.is_exit_command("/exit") is True
        assert handler.is_exit_command("hello") is False

    def test_process_input_handles_regular_text(self) -> None:
        """Test that ChatInputHandler processes regular text."""
        # Arrange
        handler = ChatInputHandler()

        # Act
        result = handler.process_input("Hello, world!")

        # Assert
        assert result.is_exit is False
        assert result.text == "Hello, world!"


class TestChatImplementation:
    """Test the core chat implementation."""

    def test_chat_implementation_basic_echo_loop(self) -> None:
        """Test that chat implementation can handle basic input/output loop."""
        # Arrange
        inputs = ["Hello", "How are you?", "/quit"]
        expected_outputs = ["Echo: Hello", "Echo: How are you?"]

        mock_input_handler = Mock()
        mock_input_handler.get_input.side_effect = inputs
        mock_input_handler.is_exit_command.side_effect = [False, False, True]

        outputs = []
        mock_output_handler = Mock()
        mock_output_handler.display.side_effect = lambda text: outputs.append(text)

        # Act
        chat_implementation(
            input_handler=mock_input_handler,
            output_handler=mock_output_handler,
            agent_name="echo",
        )

        # Assert
        assert outputs == expected_outputs
        assert mock_input_handler.get_input.call_count == 3
        assert mock_output_handler.display.call_count == 2

    def test_chat_implementation_exits_on_quit_command(self) -> None:
        """Test that chat implementation exits when /quit is entered."""
        # Arrange
        mock_input_handler = Mock()
        mock_input_handler.get_input.return_value = "/quit"
        mock_input_handler.is_exit_command.return_value = True

        mock_output_handler = Mock()

        # Act
        chat_implementation(
            input_handler=mock_input_handler,
            output_handler=mock_output_handler,
            agent_name="echo",
        )

        # Assert
        assert mock_input_handler.get_input.call_count == 1
        assert mock_output_handler.display.call_count == 0


class TestChatFlowImplementation:
    """Test the trampoline-based chat flow implementation."""

    def test_chat_flow_basic_trampoline_loop(self) -> None:
        """Test that chat flow uses trampoline architecture for looping."""
        # Arrange
        inputs = ["Hello", "How are you?", "/quit"]
        expected_outputs = ["Echo: Hello", "Echo: How are you?"]

        mock_input_handler = Mock()
        mock_input_handler.get_input.side_effect = inputs
        mock_input_handler.is_exit_command.side_effect = [False, False, True]

        outputs = []
        mock_output_handler = Mock()
        mock_output_handler.display.side_effect = lambda text: outputs.append(text)

        context = Context()

        # Act
        final_context = chat_flow_implementation(
            context=context,
            input_handler=mock_input_handler,
            output_handler=mock_output_handler,
            agent_name="echo",
        )

        # Assert
        assert outputs == expected_outputs
        assert mock_input_handler.get_input.call_count == 3
        assert mock_output_handler.display.call_count == 2
        assert final_context.get(SHOULD_EXIT_KEY.path) is True

    def test_chat_flow_sets_exit_signal_on_quit(self) -> None:
        """Test that chat flow sets SHOULD_EXIT_KEY when /quit is entered."""
        # Arrange
        mock_input_handler = Mock()
        mock_input_handler.get_input.return_value = "/quit"
        mock_input_handler.is_exit_command.return_value = True

        mock_output_handler = Mock()
        context = Context()

        # Act
        final_context = chat_flow_implementation(
            context=context,
            input_handler=mock_input_handler,
            output_handler=mock_output_handler,
            agent_name="echo",
        )

        # Assert
        assert final_context.get(SHOULD_EXIT_KEY.path) is True
        assert mock_input_handler.get_input.call_count == 1
        assert mock_output_handler.display.call_count == 0

    def test_chat_flow_continues_without_exit_signal(self) -> None:
        """Test that chat flow processes single iteration without exit."""
        # Arrange
        mock_input_handler = Mock()
        # First call returns "Hello", second call returns "/quit" to exit
        mock_input_handler.get_input.side_effect = ["Hello", "/quit"]
        mock_input_handler.is_exit_command.side_effect = [False, True]

        mock_output_handler = Mock()
        context = Context()

        # Act
        final_context = chat_flow_implementation(
            context=context,
            input_handler=mock_input_handler,
            output_handler=mock_output_handler,
            agent_name="echo",
        )

        # Assert
        assert final_context.get(SHOULD_EXIT_KEY.path) is True
        assert mock_input_handler.get_input.call_count == 2
        assert mock_output_handler.display.call_count == 1
        mock_output_handler.display.assert_called_with("Echo: Hello")
