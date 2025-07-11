"""Unit tests for chat command implementation."""

from unittest.mock import Mock

from goldentooth_agent.cli.commands.chat import ChatInputHandler, chat_implementation


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
