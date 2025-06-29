from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from typing import Annotated

import typer
from antidote import inject
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow import Flow
from goldentooth_agent.core.flow_agent import AgentInput, AgentOutput, FlowAgent
from goldentooth_agent.core.llm import create_claude_agent

app = typer.Typer()


async def process_rag_input(rag_agent, question: str, conversation_history: list[dict[str, str]]):
    """Process input through a RAG agent."""
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


def create_rag_agent():
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
                "[dim]Type 'quit', 'exit', or press Ctrl+C to end the session[/dim]\n"
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
    conversation_history = []
    
    try:
        if agent_name == "echo":
            agent = create_echo_agent()
            console.print("[dim]Using echo agent (demonstration mode)[/dim]")
        elif agent_name == "rag":
            try:
                rag_agent = create_rag_agent()
                console.print("[dim]Using RAG agent (document-powered responses)[/dim]")
            except Exception as e:
                console.print(f"[yellow]RAG agent unavailable: {str(e)[:100]}...[/yellow]")
                console.print("[yellow]To use the RAG agent, ensure you have:[/yellow]")
                console.print("[yellow]  1. OPENAI_API_KEY environment variable set[/yellow]")
                console.print("[yellow]  2. ANTHROPIC_API_KEY environment variable set[/yellow]")  
                console.print("[yellow]  3. Documents loaded in the vector store[/yellow]")
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
        console.print(f"[yellow]{agent_name or 'Claude'} unavailable ({e}), using echo agent[/yellow]")
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

            # Check for exit commands
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
                        result = await process_rag_input(rag_agent, user_input, conversation_history)
                        live.update(Text(f"[bold blue]RAG Agent[/bold blue]: {result.response}"))
                        await asyncio.sleep(0.1)
                else:
                    with console.status("[dim]🔍 Searching documents...[/dim]"):
                        result = await process_rag_input(rag_agent, user_input, conversation_history)
                
                console.print(f"[bold blue]RAG Agent[/bold blue]: {result.response}")
                
                # Show RAG-specific metadata
                if result.sources:
                    console.print(f"[dim]Sources: {len(result.sources)} documents | Confidence: {result.confidence:.2f}[/dim]")
                
                if result.suggestions:
                    console.print(f"[dim]Suggestions: {', '.join(result.suggestions[:2])}[/dim]")
                
                # Add to conversation history
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": result.response})
                
                # Keep conversation history manageable
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]
                    
            else:
                # Standard FlowAgent processing
                if stream_enabled:
                    with Live(
                        Text("🤖 Thinking...", style="dim"),
                        console=console,
                        refresh_per_second=10,
                    ) as live:
                        await asyncio.sleep(0.5)
                        result = await process_agent_input(agent, input_data)
                        live.update(Text(f"[bold blue]Agent[/bold blue]: {result.response}"))
                        await asyncio.sleep(0.1)
                else:
                    with console.status("[dim]🤖 Processing...[/dim]"):
                        result = await process_agent_input(agent, input_data)

                console.print(f"[bold blue]Agent[/bold blue]: {result.response}")

                # Show standard metadata
                if result.metadata:
                    metadata_text = " | ".join(
                        [f"{k}: {v}" for k, v in result.metadata.items()]
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
            input_data = AgentInput(message=message, context_data={"single_message": True})
            return await process_agent_input(agent, input_data)
        elif agent_name == "rag":
            try:
                rag_agent = create_rag_agent()
                # Process with RAG agent
                rag_result = await process_rag_input(rag_agent, message, [])
                # Convert RAG result to AgentOutput for compatibility
                return AgentOutput(
                    response=rag_result.response,
                    metadata={
                        "sources": len(rag_result.sources),
                        "confidence": rag_result.confidence,
                        "agent_type": "rag",
                    }
                )
            except Exception as e:
                console.print(f"[yellow]RAG agent unavailable ({e}), using echo agent[/yellow]")
                agent = create_echo_agent()
                input_data = AgentInput(message=message, context_data={"single_message": True})
                return await process_agent_input(agent, input_data)
        else:
            # Try to create Claude agent
            agent = create_claude_agent(
                name=agent_name or "claude",
                system_prompt="You are a helpful AI assistant. Be concise and helpful.",
            )
            # Create input and process
            input_data = AgentInput(message=message, context_data={"single_message": True})
            return await process_agent_input(agent, input_data)
    except ValueError as e:
        # If requested agent fails, fallback to echo
        console.print(f"[yellow]{agent_name or 'Claude'} unavailable ({e}), using echo agent[/yellow]")
        agent = create_echo_agent()
        input_data = AgentInput(message=message, context_data={"single_message": True})
        return await process_agent_input(agent, input_data)
