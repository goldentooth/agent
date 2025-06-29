"""Tests for FlowAgent class with pipeline composition."""

import pytest
from pydantic import Field

from goldentooth_agent.core.flow_agent.agent import FlowAgent
from goldentooth_agent.core.flow_agent.schema import (
    AgentInput,
    AgentOutput,
    FlowIOSchema,
)
from goldentooth_agent.flow_engine import Flow


# Test schemas
class ChatInput(FlowIOSchema):
    """Input schema for chat agent."""

    message: str = Field(..., description="User message")
    user_id: str = Field(default="anonymous", description="User identifier")


class ChatOutput(FlowIOSchema):
    """Output schema for chat agent."""

    response: str = Field(..., description="Agent response")
    confidence: float = Field(default=1.0, description="Response confidence")


class TestFlowAgent:
    """Test the FlowAgent class."""

    def test_flow_agent_creation(self):
        """Test basic FlowAgent creation."""

        # Create minimal flows for testing
        async def system_flow_impl(stream):
            async for context in stream:
                yield context

        async def processing_flow_impl(stream):
            async for context in stream:
                yield context

        system_flow = Flow(system_flow_impl, name="test_system")
        processing_flow = Flow(processing_flow_impl, name="test_processing")

        agent = FlowAgent(
            name="test_agent",
            input_schema=ChatInput,
            output_schema=ChatOutput,
            system_flow=system_flow,
            processing_flow=processing_flow,
            model="gpt-4",
        )

        assert agent.name == "test_agent"
        assert agent.input_schema == ChatInput
        assert agent.output_schema == ChatOutput
        assert agent.model == "gpt-4"
        assert agent.system_flow == system_flow
        assert agent.processing_flow == processing_flow

    def test_flow_agent_as_flow_conversion(self):
        """Test converting FlowAgent to Flow."""

        async def simple_system(stream):
            async for context in stream:
                yield context

        async def simple_processing(stream):
            async for context in stream:
                yield context

        agent = FlowAgent(
            name="test_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="system"),
            processing_flow=Flow(simple_processing, name="processing"),
        )

        agent_flow = agent.as_flow()
        assert isinstance(agent_flow, Flow)
        assert agent_flow.name == "agent:test_agent"

    @pytest.mark.asyncio
    async def test_flow_agent_basic_pipeline(self):
        """Test basic FlowAgent pipeline execution."""

        # Create a simple echo agent that just returns the input message
        async def echo_system_flow(stream):
            """System flow that passes context through unchanged."""
            async for context in stream:
                yield context

        async def echo_processing_flow(stream):
            """Processing flow that echoes the input message."""
            async for context in stream:
                # Extract input message from context
                input_data = AgentInput.from_context(context)

                # Create output
                output_data = AgentOutput(response=f"Echo: {input_data.message}")

                # Put output back in context
                updated_context = output_data.to_context(context)
                yield updated_context

        agent = FlowAgent(
            name="echo_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(echo_system_flow, name="echo_system"),
            processing_flow=Flow(echo_processing_flow, name="echo_processing"),
        )

        # Test the agent
        test_input = AgentInput(message="Hello, world!")
        agent_flow = agent.as_flow()

        # Create input stream
        async def input_stream():
            yield test_input

        # Execute and collect results
        results = []
        async for result in agent_flow(input_stream()):
            results.append(result)

        assert len(results) == 1
        assert isinstance(results[0], AgentOutput)
        assert results[0].response == "Echo: Hello, world!"

    @pytest.mark.asyncio
    async def test_flow_agent_system_prompt_integration(self):
        """Test FlowAgent with system prompt generation."""

        # Create a system flow that adds a system prompt to context
        async def system_prompt_flow(stream):
            async for context in stream:
                # Add system prompt to context
                from goldentooth_agent.core.context import ContextKey

                SYSTEM_PROMPT_KEY = ContextKey.create(
                    "agent.system_prompt", str, "System prompt"
                )

                updated_context = context.fork()
                updated_context.set(
                    SYSTEM_PROMPT_KEY.path, "You are a helpful assistant."
                )

                yield updated_context

        # Create processing flow that uses the system prompt
        async def prompt_aware_processing(stream):
            async for context in stream:
                from goldentooth_agent.core.context import ContextKey

                SYSTEM_PROMPT_KEY = ContextKey.create(
                    "agent.system_prompt", str, "System prompt"
                )

                # Get input and system prompt
                input_data = AgentInput.from_context(context)
                system_prompt = context.get(SYSTEM_PROMPT_KEY.path, "No system prompt")

                # Create response that includes system prompt info
                response = f"[{system_prompt}] Response to: {input_data.message}"
                output_data = AgentOutput(response=response)

                updated_context = output_data.to_context(context)
                yield updated_context

        agent = FlowAgent(
            name="prompt_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(system_prompt_flow, name="system_prompt"),
            processing_flow=Flow(prompt_aware_processing, name="prompt_processing"),
        )

        # Test the agent
        test_input = AgentInput(message="Hello!")
        agent_flow = agent.as_flow()

        async def input_stream():
            yield test_input

        results = []
        async for result in agent_flow(input_stream()):
            results.append(result)

        assert len(results) == 1
        expected_response = "[You are a helpful assistant.] Response to: Hello!"
        assert results[0].response == expected_response

    @pytest.mark.asyncio
    async def test_flow_agent_memory_integration(self):
        """Test FlowAgent with memory/conversation history using external memory store."""

        # External memory store (simulates database or session storage)
        conversation_memory = []

        # Create a memory-aware system flow
        async def memory_system_flow(stream):
            async for context in stream:
                from goldentooth_agent.core.context import ContextKey

                MESSAGES_KEY = ContextKey.create(
                    "agent.messages", list, "Message history"
                )

                # Get current input and add to memory
                input_data = AgentInput.from_context(context)
                conversation_memory.append(
                    {"role": "user", "content": input_data.message}
                )

                # Update context with current memory state
                updated_context = context.fork()
                updated_context.set(MESSAGES_KEY.path, conversation_memory.copy())

                yield updated_context

        # Create processing flow that uses message history
        async def memory_processing_flow(stream):
            async for context in stream:
                from goldentooth_agent.core.context import ContextKey

                MESSAGES_KEY = ContextKey.create(
                    "agent.messages", list, "Message history"
                )

                input_data = AgentInput.from_context(context)
                messages = context.get(MESSAGES_KEY.path, [])

                # Count only user messages
                user_message_count = len([m for m in messages if m["role"] == "user"])
                response = f"This is message #{user_message_count}. You said: {input_data.message}"

                # Add assistant response to memory
                conversation_memory.append({"role": "assistant", "content": response})

                output_data = AgentOutput(response=response)
                updated_context = output_data.to_context(context)

                yield updated_context

        agent = FlowAgent(
            name="memory_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(memory_system_flow, name="memory_system"),
            processing_flow=Flow(memory_processing_flow, name="memory_processing"),
        )

        # Test multiple interactions with persistent memory
        agent_flow = agent.as_flow()

        messages = ["Hello!", "How are you?", "Goodbye!"]

        for i, message in enumerate(messages):
            test_input = AgentInput(message=message)

            async def single_input(captured_input=test_input):
                yield captured_input

            async for result in agent_flow(single_input()):
                # Expected message count: user messages so far
                expected_message_count = i + 1
                expected = (
                    f"This is message #{expected_message_count}. You said: {message}"
                )
                assert result.response == expected

    def test_flow_agent_validation(self):
        """Test FlowAgent input/output validation."""

        async def simple_flow(stream):
            async for item in stream:
                yield item

        _ = FlowAgent(
            name="validator",
            input_schema=ChatInput,
            output_schema=ChatOutput,
            system_flow=Flow(simple_flow, name="system"),
            processing_flow=Flow(simple_flow, name="processing"),
        )

        # The agent should validate inputs match the input_schema
        # and outputs match the output_schema
        # This will be tested in the actual implementation

    @pytest.mark.asyncio
    async def test_flow_agent_error_handling(self):
        """Test FlowAgent error handling."""

        async def error_system_flow(stream):
            async for context in stream:
                yield context

        async def error_processing_flow(stream):
            async for _context in stream:
                # Need to yield something to make this an async generator
                if False:
                    yield None
                raise ValueError("Processing error")

        agent = FlowAgent(
            name="error_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(error_system_flow, name="error_system"),
            processing_flow=Flow(error_processing_flow, name="error_processing"),
        )

        test_input = AgentInput(message="test")
        agent_flow = agent.as_flow()

        async def input_stream():
            yield test_input

        # Should propagate the error
        with pytest.raises(ValueError, match="Processing error"):
            async for _result in agent_flow(input_stream()):
                pass

    @pytest.mark.asyncio
    async def test_flow_agent_composition(self):
        """Test composing FlowAgent with other flows."""

        # Create a simple agent
        async def simple_system(stream):
            async for context in stream:
                yield context

        async def simple_processing(stream):
            async for context in stream:
                input_data = AgentInput.from_context(context)
                output_data = AgentOutput(response=f"Processed: {input_data.message}")
                updated_context = output_data.to_context(context)
                yield updated_context

        agent = FlowAgent(
            name="simple_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="system"),
            processing_flow=Flow(simple_processing, name="processing"),
        )

        # Create a post-processing flow
        async def post_processor(stream):
            async for output in stream:
                # Add exclamation mark to response
                output.response += "!"
                yield output

        post_flow = Flow(post_processor, name="post_processor")

        # Compose agent >> post_processor
        composed_flow = agent.as_flow() >> post_flow

        test_input = AgentInput(message="Hello")

        async def input_stream():
            yield test_input

        results = []
        async for result in composed_flow(input_stream()):
            results.append(result)

        assert len(results) == 1
        assert results[0].response == "Processed: Hello!"

    @pytest.mark.asyncio
    async def test_flow_agent_multiple_inputs(self):
        """Test FlowAgent handling multiple inputs in sequence."""

        async def batch_system(stream):
            async for context in stream:
                yield context

        async def batch_processing(stream):
            async for context in stream:
                input_data = AgentInput.from_context(context)
                output_data = AgentOutput(response=f"Batch: {input_data.message}")
                updated_context = output_data.to_context(context)
                yield updated_context

        agent = FlowAgent(
            name="batch_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(batch_system, name="batch_system"),
            processing_flow=Flow(batch_processing, name="batch_processing"),
        )

        # Test with multiple inputs
        inputs = [
            AgentInput(message="First"),
            AgentInput(message="Second"),
            AgentInput(message="Third"),
        ]

        agent_flow = agent.as_flow()

        async def multi_input():
            for inp in inputs:
                yield inp

        results = []
        async for result in agent_flow(multi_input()):
            results.append(result)

        assert len(results) == 3
        assert results[0].response == "Batch: First"
        assert results[1].response == "Batch: Second"
        assert results[2].response == "Batch: Third"
