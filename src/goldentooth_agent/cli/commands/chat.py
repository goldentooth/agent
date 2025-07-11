"""Chat command implementation with trampoline-based flow architecture."""

from dataclasses import dataclass
from typing import Optional, Protocol

from context import Context
from context_flow.trampoline import SHOULD_EXIT_KEY


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


def chat_flow_implementation(
    context: Context,
    input_handler: ChatInputHandler,
    output_handler: OutputHandler,
    agent_name: str = "echo",
) -> Context:
    """Trampoline-based chat implementation using Flow architecture."""

    def chat_step(ctx: Context) -> Context:
        """Single chat interaction step."""
        result = ctx.fork()

        # Get user input
        user_input = input_handler.get_input()

        # Check for exit condition
        if input_handler.is_exit_command(user_input):
            result[SHOULD_EXIT_KEY.path] = True
            return result

        # Process with agent (for now, just echo)
        if agent_name == "echo":
            response = f"Echo: {user_input}"
        else:
            response = f"Unknown agent: {agent_name}"

        # Display response
        output_handler.display(response)

        return result

    # For now, implement a synchronous trampoline loop
    # This follows the trampoline pattern: iterative execution until exit
    current_ctx = context
    while True:
        current_ctx = chat_step(current_ctx)
        if current_ctx.get(SHOULD_EXIT_KEY.path, False):
            break
    return current_ctx
