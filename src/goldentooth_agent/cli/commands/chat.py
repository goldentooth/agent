from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Annotated, Any, Callable

import typer
from antidote import inject
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent import AgentInput, AgentOutput, FlowAgent
from goldentooth_agent.core.llm import create_claude_agent
from goldentooth_agent.flow_engine import Flow

if TYPE_CHECKING:
    from goldentooth_agent.core.rag.simple_rag_agent import SimpleRAGAgent

app = typer.Typer()


class SlashCommandHandler:
    """Extensible slash command handler for chat interface."""

    def __init__(self, console: Console) -> None:
        self.console = console
        self.commands: dict[str, dict[str, Any]] = {}
        self._register_core_commands()

    def _register_core_commands(self) -> None:
        """Register core built-in commands."""
        # Exit commands
        self.register_command(
            names=["quit", "exit", "bye"],
            handler=self._handle_exit,
            description="End the chat session",
            category="exit",
        )

        # Help commands
        self.register_command(
            names=["help", "h"],
            handler=self._handle_help,
            description="Show this help message",
            category="help",
        )

        # Clear screen command
        self.register_command(
            names=["clear", "cls"],
            handler=self._handle_clear,
            description="Clear the screen",
            category="utility",
        )

        # Status command
        self.register_command(
            names=["status"],
            handler=self._handle_status,
            description="Show system status and information",
            category="utility",
        )

    def register_command(
        self,
        names: list[str],
        handler: Callable[[str], str],
        description: str,
        category: str = "general",
        aliases: list[str] | None = None,
    ) -> None:
        """Register a new command.

        Args:
            names: Primary command names (e.g., ['quit', 'exit'])
            handler: Function to handle the command
            description: Help text for the command
            category: Category for grouping in help
            aliases: Additional aliases for the command
        """
        all_names = names + (aliases or [])
        command_info = {
            "handler": handler,
            "description": description,
            "category": category,
            "primary_names": names,
        }

        for name in all_names:
            self.commands[name.lower()] = command_info

    def handle_command(self, user_input: str) -> str | None:
        """Handle slash-prefixed commands.

        Args:
            user_input: The user input string

        Returns:
            Command result type or None if not a command
        """
        if not user_input.startswith("/"):
            return None

        # Extract command and arguments
        command_part = user_input[1:].strip()
        if not command_part:
            self.console.print(
                "[yellow]Empty command. Type /help for available commands.[/yellow]"
            )
            return "continue"

        # Split into command and args
        parts = command_part.split(" ", 1)
        command_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Find and execute command
        if command_name in self.commands:
            handler = self.commands[command_name]["handler"]
            result = handler(args)
            return str(result) if result is not None else None
        else:
            self.console.print(f"[yellow]Unknown command: /{command_name}[/yellow]")
            self.console.print("[dim]Type /help for available commands[/dim]")
            return "continue"

    def _handle_exit(self, args: str) -> str:
        """Handle exit commands."""
        return "exit"

    def _handle_help(self, args: str) -> str:
        """Handle help commands."""
        self.show_help()
        return "continue"

    def _handle_clear(self, args: str) -> str:
        """Handle clear screen commands."""
        import os

        os.system("cls" if os.name == "nt" else "clear")
        return "continue"

    def _handle_status(self, args: str) -> str:
        """Handle status command."""
        import platform
        import sys

        from rich.table import Table

        table = Table(title="System Status", show_header=True)
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")

        table.add_row("Python Version", sys.version.split()[0])
        table.add_row("Platform", platform.system())
        table.add_row("Available Commands", str(len(set(self.commands.keys()))))

        # Show registered command categories
        categories = set(cmd["category"] for cmd in self.commands.values())
        table.add_row("Command Categories", ", ".join(sorted(categories)))

        self.console.print(table)
        return "continue"

    def show_help(self) -> None:
        """Display available slash commands grouped by category."""
        from rich.table import Table

        # Group commands by category
        categories: dict[str, list[tuple[list[str], str]]] = {}
        seen_commands = set()

        for cmd_name, cmd_info in self.commands.items():
            if cmd_name in seen_commands:
                continue

            category = cmd_info["category"]
            primary_names = cmd_info["primary_names"]
            description = cmd_info["description"]

            if category not in categories:
                categories[category] = []

            categories[category].append((primary_names, description))
            seen_commands.update(primary_names)

        # Create help table
        table = Table(title="Available Slash Commands", show_header=True)
        table.add_column("Command", style="green", width=20)
        table.add_column("Description", style="cyan")

        # Add commands by category
        for category in sorted(categories.keys()):
            if len(categories) > 1:
                table.add_row(f"[bold yellow]{category.upper()}[/bold yellow]", "")

            for names, description in sorted(categories[category]):
                command_str = "/" + ", /".join(names)
                table.add_row(f"  {command_str}", description)

        self.console.print(table)
        self.console.print(
            "\n[dim]Legacy commands (quit, exit, bye) also work without /[/dim]"
        )


# Global command handler instance
_command_handler: SlashCommandHandler | None = None


def get_command_handler(console: Console) -> SlashCommandHandler:
    """Get or create the command handler instance."""
    global _command_handler
    if _command_handler is None:
        _command_handler = SlashCommandHandler(console)
    return _command_handler


async def process_rag_input(
    rag_agent: SimpleRAGAgent,
    question: str,
    conversation_history: list[dict[str, str]],
) -> dict[str, Any]:
    """Process input through a RAG agent.

    Returns:
        Dictionary with keys: 'response', 'sources', 'confidence', 'suggestions', 'metadata'
    """
    return await rag_agent.process_question(
        question=question,
        conversation_history=conversation_history,
    )


async def process_agent_input(agent: FlowAgent, input_data: AgentInput) -> AgentOutput:
    """Process input through a FlowAgent using the correct Flow pattern."""

    # Convert agent to a flow
    agent_flow = agent.as_flow()

    # Create an async iterator stream with the input data
    async def input_stream() -> AsyncIterator[AgentInput]:
        yield input_data

    # Process the stream through the flow
    results = []
    async for output_data in agent_flow(input_stream()):
        results.append(output_data)

    # Return the last result (or first, for single input)
    if results:
        # Cast to AgentOutput since we know the agent produces AgentOutput
        return results[-1]  # type: ignore[return-value]  # FlowAgent guarantees AgentOutput
    else:
        # Fallback if no results (shouldn't happen in normal operation)
        return AgentOutput(
            response="No response generated",
            metadata={"error": "No output from agent flow"},
        )


def create_rag_agent() -> SimpleRAGAgent:
    """Create a simplified RAG agent for document-based conversations."""
    from goldentooth_agent.core.rag.simple_rag_agent import create_simple_rag_agent

    try:
        return create_simple_rag_agent()
    except Exception as e:
        raise ValueError(f"Failed to create RAG agent: {e}") from e


def create_echo_agent() -> FlowAgent:
    """Create a simple echo agent for demonstration."""

    async def echo_system_flow(
        stream: AsyncIterator[Context],
    ) -> AsyncIterator[Context]:
        """System flow that adds a simple system prompt."""
        async for context in stream:
            # Add system prompt to context
            context.set("system_prompt", "You are a helpful echo agent.")
            context.set("agent_name", "EchoBot")
            yield context

    async def echo_processing_flow(
        stream: AsyncIterator[Context],
    ) -> AsyncIterator[Context]:
        """Processing flow that implements echo logic."""
        async for context in stream:
            # Extract input data
            input_data = AgentInput.from_context(context)

            # Create echo response
            output_data = AgentOutput(
                response=f"Echo: {input_data.message}",
                metadata={
                    "agent": "echo",
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "message_length": len(input_data.message),
                },
            )

            # Add output to context and yield
            yield output_data.to_context(context)

    return FlowAgent(
        name="echo_agent",
        input_schema=AgentInput,
        output_schema=AgentOutput,
        system_flow=Flow(echo_system_flow, name="echo_system"),
        processing_flow=Flow(echo_processing_flow, name="echo_processing"),
    )


@app.command()
def chat(
    agent: Annotated[
        str | None, typer.Option("--agent", "-a", help="Agent to chat with")
    ] = None,
    session: Annotated[
        str | None,
        typer.Option("--session", "-s", help="Session ID for context persistence"),
    ] = None,
    stream: Annotated[
        bool, typer.Option("--stream", help="Enable streaming responses")
    ] = False,
    model: Annotated[
        str | None, typer.Option("--model", "-m", help="Model to use for responses")
    ] = None,
) -> None:
    """Start an interactive chat session with the Goldentooth Agent.

    This command creates a conversational interface where users can interact
    with AI agents using the Flow-Context-Agent architecture.
    """

    @inject
    def handle() -> None:
        """Handle the chat session logic."""
        console = Console()

        # Display welcome message
        console.print(
            Panel.fit(
                "[bold blue]🤖 Goldentooth Agent Interactive Chat[/bold blue]\n"
                "[dim]Type '/help' for commands, '/quit' to exit, or press Ctrl+C to end the session[/dim]\n"
                f"[dim]Agent: {agent or 'echo'} | Session: {session or 'default'}[/dim]",
                border_style="blue",
            )
        )

        # Run the async chat loop
        try:
            asyncio.run(chat_loop(console, agent, session, stream, model))
        except KeyboardInterrupt:
            console.print("\n[yellow]Chat session ended.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


async def chat_loop(
    console: Console,
    agent_name: str | None,
    session_id: str | None,
    stream_enabled: bool,
    model_name: str | None,
) -> None:
    """Main chat interaction loop."""

    # Create agent - support RAG, Claude, and echo
    agent = None
    rag_agent = None
    conversation_history: list[dict[str, str]] = []

    try:
        if agent_name == "echo":
            agent = create_echo_agent()
            console.print("[dim]Using echo agent (demonstration mode)[/dim]")
        elif agent_name == "rag":
            try:
                rag_agent = create_rag_agent()
                console.print("[dim]Using RAG agent (document-powered responses)[/dim]")
            except Exception as e:
                console.print(
                    f"[yellow]RAG agent unavailable: {str(e)[:100]}...[/yellow]"
                )
                console.print("[yellow]To use the RAG agent, ensure you have:[/yellow]")
                console.print(
                    "[yellow]  1. OPENAI_API_KEY environment variable set[/yellow]"
                )
                console.print(
                    "[yellow]  2. ANTHROPIC_API_KEY environment variable set[/yellow]"
                )
                console.print(
                    "[yellow]  3. Documents loaded in the vector store[/yellow]"
                )
                console.print("[yellow]Using echo agent as fallback.[/yellow]")
                agent = create_echo_agent()
                rag_agent = None
        else:
            # Try to create Claude agent
            agent = create_claude_agent(
                name=agent_name or "claude",
                model=model_name or "claude-3-5-sonnet-20241022",
                system_prompt="You are a helpful AI assistant. Be concise and helpful.",
            )
            console.print(
                f"[dim]Using Claude agent ({model_name or 'claude-3-5-sonnet-20241022'})[/dim]"
            )
    except ValueError as e:
        # If the requested agent fails, fallback to echo
        console.print(
            f"[yellow]{agent_name or 'Claude'} unavailable ({e}), using echo agent[/yellow]"
        )
        agent = create_echo_agent()
        rag_agent = None
    context = Context()

    # Add session context
    if session_id:
        context.set("session_id", session_id)
    if model_name:
        context.set("model_name", model_name)

    console.print(
        "[dim]Chat session started. You can now send messages to the agent.[/dim]\n"
    )

    message_count = 0

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold green]You[/bold green]", console=console)

            # Handle slash commands using extensible command handler
            command_handler = get_command_handler(console)
            command_result = command_handler.handle_command(user_input)

            if command_result == "exit":
                break
            elif command_result == "continue":
                continue

            # Check for legacy exit commands (backwards compatibility)
            if user_input.lower() in ["quit", "exit", "bye"]:
                break

            if not user_input.strip():
                continue

            message_count += 1

            # Create input for agent
            input_data = AgentInput(
                message=user_input,
                context_data={
                    "message_number": message_count,
                    "session_id": session_id or "default",
                },
            )

            # Process with appropriate agent type
            if rag_agent:
                # RAG agent processing
                if stream_enabled:
                    with Live(
                        Text("🔍 Searching documents...", style="dim"),
                        console=console,
                        refresh_per_second=10,
                    ) as live:
                        rag_result = await process_rag_input(
                            rag_agent, user_input, conversation_history
                        )
                        live.update(
                            Text(
                                f"[bold blue]RAG Agent[/bold blue]: {rag_result['response']}"
                            )
                        )
                        await asyncio.sleep(0.1)
                else:
                    with console.status("[dim]🔍 Searching documents...[/dim]"):
                        rag_result = await process_rag_input(
                            rag_agent, user_input, conversation_history
                        )

                console.print(
                    f"[bold blue]RAG Agent[/bold blue]: {rag_result['response']}"
                )

                # Show RAG-specific metadata
                if rag_result.get("sources"):
                    console.print(
                        f"[dim]Sources: {len(rag_result['sources'])} documents | Confidence: {rag_result['confidence']:.2f}[/dim]"
                    )

                if rag_result.get("suggestions"):
                    console.print(
                        f"[dim]Suggestions: {', '.join(rag_result['suggestions'][:2])}[/dim]"
                    )

                # Add to conversation history
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append(
                    {"role": "assistant", "content": rag_result["response"]}
                )

                # Keep conversation history manageable
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]

            else:
                # Standard FlowAgent processing
                if agent is None:
                    console.print("❌ No agent available", style="red")
                    continue

                if stream_enabled:
                    with Live(
                        Text("🤖 Thinking...", style="dim"),
                        console=console,
                        refresh_per_second=10,
                    ) as live:
                        await asyncio.sleep(0.5)
                        agent_result = await process_agent_input(agent, input_data)
                        live.update(
                            Text(
                                f"[bold blue]Agent[/bold blue]: {agent_result.response}"
                            )
                        )
                        await asyncio.sleep(0.1)
                else:
                    with console.status("[dim]🤖 Processing...[/dim]"):
                        agent_result = await process_agent_input(agent, input_data)

                console.print(f"[bold blue]Agent[/bold blue]: {agent_result.response}")

                # Show standard metadata
                if agent_result.metadata:
                    metadata_text = " | ".join(
                        [f"{k}: {v}" for k, v in agent_result.metadata.items()]
                    )
                    console.print(f"[dim]{metadata_text}[/dim]")

            console.print()  # Add spacing

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error processing message: {e}[/red]")
            continue

    console.print(
        f"[green]Chat session ended. Processed {message_count} messages.[/green]"
    )


@app.command()
def send(
    message: Annotated[
        str | None, typer.Argument(help="Message to send to the agent")
    ] = None,
    agent: Annotated[
        str | None, typer.Option("--agent", "-a", help="Agent to use")
    ] = "echo",
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: text, json")
    ] = "text",
) -> None:
    """Send a single message to an agent (UNIX pipe friendly).

    This command is designed for use in UNIX pipelines and scripts.
    """

    @inject
    def handle() -> None:
        """Handle single message processing."""
        console = Console(file=sys.stderr)  # Error output to stderr

        # Get message from argument or stdin
        if message:
            input_text = message
        else:
            # Read from stdin for pipe compatibility
            try:
                input_text = sys.stdin.read().strip()
            except Exception:
                console.print(
                    "[red]Error: No message provided and failed to read from stdin[/red]"
                )
                raise typer.Exit(1) from None

        if not input_text:
            console.print("[red]Error: Empty message provided[/red]")
            raise typer.Exit(1)

        # Run async processing
        try:
            result = asyncio.run(process_single_message(input_text, agent, console))

            # Output result in requested format
            if format == "json":
                import json

                output = {"response": result.response, "metadata": result.metadata}
                print(json.dumps(output))
            else:
                print(result.response)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


async def process_single_message(
    message: str, agent_name: str | None, console: Console
) -> AgentOutput:
    """Process a single message through an agent."""

    # Create agent - support RAG, Claude, and echo
    try:
        if agent_name == "echo":
            agent = create_echo_agent()
            # Create input and process
            input_data = AgentInput(
                message=message, context_data={"single_message": True}
            )
            return await process_agent_input(agent, input_data)
        elif agent_name == "rag":
            try:
                rag_agent = create_rag_agent()
                # Process with RAG agent
                rag_result = await process_rag_input(rag_agent, message, [])
                # Convert RAG result to AgentOutput for compatibility
                return AgentOutput(
                    response=rag_result["response"],
                    metadata={
                        "sources": len(rag_result.get("sources", [])),
                        "confidence": rag_result.get("confidence", 0.0),
                        "agent_type": "rag",
                    },
                )
            except Exception as e:
                console.print(
                    f"[yellow]RAG agent unavailable ({e}), using echo agent[/yellow]"
                )
                agent = create_echo_agent()
                input_data = AgentInput(
                    message=message, context_data={"single_message": True}
                )
                return await process_agent_input(agent, input_data)
        else:
            # Try to create Claude agent
            agent = create_claude_agent(
                name=agent_name or "claude",
                system_prompt="You are a helpful AI assistant. Be concise and helpful.",
            )
            # Create input and process
            input_data = AgentInput(
                message=message, context_data={"single_message": True}
            )
            return await process_agent_input(agent, input_data)
    except ValueError as e:
        # If requested agent fails, fallback to echo
        console.print(
            f"[yellow]{agent_name or 'Claude'} unavailable ({e}), using echo agent[/yellow]"
        )
        agent = create_echo_agent()
        input_data = AgentInput(message=message, context_data={"single_message": True})
        return await process_agent_input(agent, input_data)
