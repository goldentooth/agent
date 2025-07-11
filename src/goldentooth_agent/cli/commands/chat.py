"""Chat command implementation with trampoline-based flow architecture."""

from dataclasses import dataclass
from typing import Optional, Protocol


class InputSource(Protocol):
    """Protocol for input sources (CLI, stdin, agents, tests)."""

    def get_input(self) -> str:
        """Get input from the source."""
        ...


class OutputHandler(Protocol):
    """Protocol for output handlers."""

    def display(self, text: str) -> None:
        """Display text to the output."""
        ...


@dataclass
class InputResult:
    """Result of processing input."""

    text: str
    is_exit: bool = False


class ChatInputHandler:
    """Handles input processing with support for slash commands."""

    def __init__(self, input_source: Optional[InputSource] = None):
        """Initialize with optional input source."""
        super().__init__()
        self.input_source = input_source

    def get_input(self) -> str:
        """Get input from the configured source."""
        if self.input_source:
            return self.input_source.get_input()
        return input(">>> ")

    def is_exit_command(self, text: str) -> bool:
        """Check if the input is an exit command."""
        return text.strip() in ["/quit", "/exit"]

    def process_input(self, text: str) -> InputResult:
        """Process input and return structured result."""
        return InputResult(text=text, is_exit=self.is_exit_command(text))


def chat_implementation(
    input_handler: ChatInputHandler,
    output_handler: OutputHandler,
    agent_name: str = "echo",
) -> None:
    """Core chat implementation - the actual business logic."""
    while True:
        # Get user input
        user_input = input_handler.get_input()

        # Check for exit condition
        if input_handler.is_exit_command(user_input):
            break

        # Process with agent (for now, just echo)
        if agent_name == "echo":
            response = f"Echo: {user_input}"
        else:
            response = f"Unknown agent: {agent_name}"

        # Display response
        output_handler.display(response)
