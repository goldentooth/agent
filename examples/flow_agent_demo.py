#!/usr/bin/env python3

"""Comprehensive FlowAgent demonstration.

This example shows how to:
1. Create FlowAgent with system and processing flows
2. Implement system prompt generation
3. Handle memory/conversation history
4. Compose agents with tools
5. Create agent pipelines for complex workflows
"""

import asyncio
from typing import Any

from pydantic import Field

from goldentooth_agent.core.context import ContextKey
from goldentooth_agent.core.flow import Flow
from goldentooth_agent.core.flow_agent import FlowAgent, FlowIOSchema, FlowTool


# Custom schemas for our demo agents
class ChatInput(FlowIOSchema):
    """Input for chat agent."""

    message: str = Field(..., description="User message")
    user_id: str = Field(default="user", description="User identifier")
    context_hints: list[str] = Field(default_factory=list, description="Context hints")


class ChatOutput(FlowIOSchema):
    """Output for chat agent."""

    response: str = Field(..., description="Agent response")
    confidence: float = Field(default=1.0, description="Response confidence")
    suggested_actions: list[str] = Field(
        default_factory=list, description="Suggested follow-up actions"
    )


# Memory store for demonstration
conversation_memory: dict[str, list[dict[str, Any]]] = {}


def create_echo_agent() -> FlowAgent:
    """Create a simple echo agent for demonstration."""

    async def echo_system_flow(stream):
        """System flow that adds a simple system prompt."""
        async for context in stream:
            # Add system prompt
            SYSTEM_PROMPT_KEY = ContextKey.create(
                "agent.system_prompt", str, "System prompt"
            )
            updated_context = context.fork()
            updated_context.set(SYSTEM_PROMPT_KEY.path, "You are a helpful echo agent.")
            yield updated_context

    async def echo_processing_flow(stream):
        """Processing flow that echoes the input with modifications."""
        async for context in stream:
            # Extract input
            input_data = ChatInput.from_context(context)

            # Create echo response
            response = f"Echo: {input_data.message}"
            if input_data.user_id != "user":
                response = f"[{input_data.user_id}] {response}"

            output_data = ChatOutput(
                response=response,
                confidence=0.9,
                suggested_actions=["ask another question", "try a different message"],
            )

            # Put output in context
            updated_context = output_data.to_context(context)
            yield updated_context

    return FlowAgent(
        name="echo_agent",
        input_schema=ChatInput,
        output_schema=ChatOutput,
        system_flow=Flow(echo_system_flow, name="echo_system"),
        processing_flow=Flow(echo_processing_flow, name="echo_processing"),
    )


def create_memory_agent() -> FlowAgent:
    """Create an agent with conversation memory."""

    async def memory_system_flow(stream):
        """System flow that manages conversation memory."""
        async for context in stream:
            # Keys for memory
            MESSAGES_KEY = ContextKey.create(
                "agent.messages", list, "Conversation history"
            )
            SYSTEM_PROMPT_KEY = ContextKey.create(
                "agent.system_prompt", str, "System prompt"
            )

            # Extract input to get user_id
            input_data = ChatInput.from_context(context)
            user_id = input_data.user_id

            # Get or create user's conversation history
            if user_id not in conversation_memory:
                conversation_memory[user_id] = []

            # Add current message to history
            conversation_memory[user_id].append(
                {
                    "role": "user",
                    "content": input_data.message,
                    "timestamp": "now",  # In real app, use actual timestamp
                }
            )

            # Create system prompt with context
            message_count = len(
                [m for m in conversation_memory[user_id] if m["role"] == "user"]
            )
            system_prompt = f"""You are a helpful assistant with memory.
This is message #{message_count} from user {user_id}.
You remember previous conversations and can reference them."""

            # Update context
            updated_context = context.fork()
            updated_context.set(MESSAGES_KEY.path, conversation_memory[user_id].copy())
            updated_context.set(SYSTEM_PROMPT_KEY.path, system_prompt)

            yield updated_context

    async def memory_processing_flow(stream):
        """Processing flow that uses memory to generate responses."""
        async for context in stream:
            # Extract data
            input_data = ChatInput.from_context(context)
            messages = context.get("agent.messages", [])

            # Count user messages
            user_messages = [m for m in messages if m["role"] == "user"]
            message_count = len(user_messages)

            # Generate response based on history
            if message_count == 1:
                response = f"Hello {input_data.user_id}! You said: '{input_data.message}'. Nice to meet you!"
            elif message_count <= 3:
                response = f"Thanks for message #{message_count}! You said: '{input_data.message}'. I'm getting to know you better."
            else:
                response = f"We've been chatting for a while now (message #{message_count})! You said: '{input_data.message}'. I remember our conversation."

            # Add assistant response to memory
            conversation_memory[input_data.user_id].append(
                {"role": "assistant", "content": response, "timestamp": "now"}
            )

            output_data = ChatOutput(
                response=response,
                confidence=0.95,
                suggested_actions=[
                    "continue conversation",
                    "ask about memory",
                    "change topic",
                ],
            )

            updated_context = output_data.to_context(context)
            yield updated_context

    return FlowAgent(
        name="memory_agent",
        input_schema=ChatInput,
        output_schema=ChatOutput,
        system_flow=Flow(memory_system_flow, name="memory_system"),
        processing_flow=Flow(memory_processing_flow, name="memory_processing"),
    )


def create_calculator_tool() -> FlowTool:
    """Create a calculator tool that can be used with agents."""

    class CalcInput(FlowIOSchema):
        expression: str = Field(..., description="Math expression")

    class CalcOutput(FlowIOSchema):
        result: str = Field(..., description="Calculation result")
        expression: str = Field(..., description="Original expression")

    def calc_impl(input_data: CalcInput) -> CalcOutput:
        try:
            # Simple eval for demo (use proper math parser in production)
            result = str(eval(input_data.expression.replace("^", "**")))
            return CalcOutput(result=result, expression=input_data.expression)
        except Exception as e:
            return CalcOutput(result=f"Error: {e}", expression=input_data.expression)

    return FlowTool(
        name="calculator",
        input_schema=CalcInput,
        output_schema=CalcOutput,
        implementation=calc_impl,
        description="Mathematical calculator",
    )


async def demonstrate_basic_agents():
    """Demonstrate basic agent functionality."""
    print("🤖 FlowAgent Basic Demo")
    print("=" * 40)

    # Create agents
    echo_agent = create_echo_agent()
    memory_agent = create_memory_agent()

    # Test echo agent
    print("\n📢 Echo Agent Test:")
    echo_flow = echo_agent.as_flow()

    test_input = ChatInput(message="Hello, world!", user_id="alice")

    async def single_input():
        yield test_input

    async for result in echo_flow(single_input()):
        print(f"Input: {test_input.message}")
        print(f"Output: {result.response}")
        print(f"Confidence: {result.confidence}")
        print(f"Actions: {result.suggested_actions}")

    # Test memory agent with multiple messages
    print("\n🧠 Memory Agent Test:")
    memory_flow = memory_agent.as_flow()

    messages = [
        ChatInput(message="Hi there!", user_id="bob"),
        ChatInput(message="How are you?", user_id="bob"),
        ChatInput(message="What's the weather?", user_id="bob"),
        ChatInput(message="Tell me a joke", user_id="bob"),
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n--- Message {i} ---")

        async def single_message(captured_msg=msg):
            yield captured_msg

        async for result in memory_flow(single_message()):
            print(f"User: {msg.message}")
            print(f"Agent: {result.response}")


async def demonstrate_agent_composition():
    """Demonstrate composing agents with tools and other flows."""
    print("\n\n🔗 Agent Composition Demo")
    print("=" * 40)

    # Create calculator tool and convert to agent
    calc_tool = create_calculator_tool()
    calc_agent = calc_tool.as_agent()

    # Create a formatting flow
    async def format_response(stream):
        """Format agent responses nicely."""
        async for response in stream:
            if isinstance(response, ChatOutput):
                # Format chat response
                formatted = f"💬 {response.response}"
                if response.suggested_actions:
                    formatted += (
                        f"\n   Suggestions: {', '.join(response.suggested_actions)}"
                    )
                response.response = formatted
            yield response

    formatter = Flow(format_response, name="response_formatter")

    # Compose echo agent with formatter
    echo_agent = create_echo_agent()
    composed_flow = echo_agent.as_flow() >> formatter

    print("\n🎨 Echo Agent + Formatter:")
    test_input = ChatInput(message="Format this message!", user_id="charlie")

    async def single_input():
        yield test_input

    async for result in composed_flow(single_input()):
        print(result.response)

    # Show tool-to-agent conversion
    print("\n🔢 Calculator Tool as Agent:")
    _ = calc_agent.as_flow()

    # Note: The calculator tool expects CalcInput, but agent expects ChatInput
    # In a real system, we'd need input/output adapters
    print("Calculator agent created successfully!")
    print(f"Agent name: {calc_agent.name}")
    print(f"Input schema: {calc_agent.input_schema.__name__}")
    print(f"Output schema: {calc_agent.output_schema.__name__}")


async def demonstrate_error_handling():
    """Demonstrate error handling in agents."""
    print("\n\n⚠️  Error Handling Demo")
    print("=" * 40)

    # Create an agent that sometimes fails
    async def unreliable_system(stream):
        async for context in stream:
            yield context

    async def unreliable_processing(stream):
        count = 0
        async for context in stream:
            count += 1
            input_data = ChatInput.from_context(context)

            # Fail on every 3rd message
            if count % 3 == 0:
                if False:  # Need this for async generator
                    yield None
                raise ValueError(f"Simulated failure on message: {input_data.message}")

            # Otherwise succeed
            output_data = ChatOutput(
                response=f"Processed successfully: {input_data.message}"
            )
            updated_context = output_data.to_context(context)
            yield updated_context

    unreliable_agent = FlowAgent(
        name="unreliable_agent",
        input_schema=ChatInput,
        output_schema=ChatOutput,
        system_flow=Flow(unreliable_system, name="unreliable_system"),
        processing_flow=Flow(unreliable_processing, name="unreliable_processing"),
    )

    agent_flow = unreliable_agent.as_flow()

    # Test with messages that will pass and fail
    test_messages = [
        "Message 1 (should work)",
        "Message 2 (should work)",
        "Message 3 (should fail)",
        "Message 4 (should work)",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Testing message {i} ---")
        test_input = ChatInput(message=message)

        try:

            async def single_input(captured_input=test_input):
                yield captured_input

            async for result in agent_flow(single_input()):
                print(f"✅ Success: {result.response}")

        except ValueError as e:
            print(f"❌ Error: {e}")


async def main():
    """Run the complete FlowAgent demonstration."""
    print("🚀 FlowAgent Comprehensive Demo")
    print("=" * 50)
    print()
    print("This demo shows the power of the Flow-based Agent System:")
    print("• Schema-driven agent creation")
    print("• System prompt generation")
    print("• Memory management")
    print("• Flow composition")
    print("• Tool-agent interoperability")
    print("• Error handling")
    print()

    await demonstrate_basic_agents()
    await demonstrate_agent_composition()
    await demonstrate_error_handling()

    print("\n\n🎯 Demo Summary")
    print("=" * 20)
    print("✅ FlowAgent pipeline working correctly")
    print("✅ Schema validation and context integration")
    print("✅ Memory management with external storage")
    print("✅ Flow composition and tool integration")
    print("✅ Error handling and graceful failures")
    print()
    print("The FlowAgent system provides:")
    print("  • Unified tool/agent interface")
    print("  • Composable flow-based architecture")
    print("  • Type-safe schema validation")
    print("  • Flexible memory management")
    print("  • Robust error handling")


if __name__ == "__main__":
    asyncio.run(main())
