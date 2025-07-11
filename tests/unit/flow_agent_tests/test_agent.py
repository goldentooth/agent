"""Tests for FlowAgent class with pipeline composition."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from pydantic import Field

from context import Context, ContextKey
from flow import Flow
from flow_agent.agent import FlowAgent
from flow_agent.schema import AgentInput, AgentOutput, ContextFlowSchema


# Test schemas
class ChatInput(ContextFlowSchema):
    """Input schema for chat agent."""

    message: str = Field(..., description="User message")
    user_id: str = Field(default="anonymous", description="User identifier")


class ChatOutput(ContextFlowSchema):
    """Output schema for chat agent."""

    response: str = Field(..., description="Agent response")
    confidence: float = Field(default=1.0, description="Response confidence")


class TestFlowAgent:
    """Test the FlowAgent class."""

    def test_flow_agent_creation(self) -> None:
        """Test basic FlowAgent creation."""

        # Create minimal flows for testing
        async def system_flow_impl(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def processing_flow_impl(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
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

    def test_flow_agent_to_flow_conversion(self) -> None:
        """Test converting FlowAgent to Flow."""

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def simple_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        agent = FlowAgent(
            name="test_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="system"),
            processing_flow=Flow(simple_processing, name="processing"),
        )

        agent_flow = agent.to_flow()
        assert isinstance(agent_flow, Flow)
        assert agent_flow.name == "agent:test_agent"

    @pytest.mark.asyncio
    async def test_flow_agent_run_method(self) -> None:
        """Test FlowAgent run method for single input processing."""

        # Create a simple echo agent
        async def echo_system_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """System flow that passes context through unchanged."""
            async for context in stream:
                yield context

        async def echo_processing_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
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

        # Test the run method
        test_input = AgentInput(message="Hello, world!")
        result = await agent.run(test_input)

        assert isinstance(result, AgentOutput)
        assert result.response == "Echo: Hello, world!"

    @pytest.mark.asyncio
    async def test_flow_agent_basic_pipeline(self) -> None:
        """Test basic FlowAgent pipeline execution."""

        # Create a simple echo agent that just returns the input message
        async def echo_system_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """System flow that passes context through unchanged."""
            async for context in stream:
                yield context

        async def echo_processing_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
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
        agent_flow = agent.to_flow()

        # Create input stream
        async def input_stream() -> AsyncGenerator[Any, None]:
            yield test_input

        # Execute and collect results
        results = []
        async for result in agent_flow(input_stream()):
            results.append(result)

        assert len(results) == 1
        assert isinstance(results[0], AgentOutput)
        assert results[0].response == "Echo: Hello, world!"

    @pytest.mark.asyncio
    async def test_flow_agent_system_prompt_integration(self) -> None:
        """Test FlowAgent with system prompt generation."""

        # Create a system flow that adds a system prompt to context
        async def system_prompt_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                # Add system prompt to context
                SYSTEM_PROMPT_KEY = ContextKey.create(
                    "agent.system_prompt", str, "System prompt"
                )

                updated_context = context.fork()
                updated_context.set(
                    SYSTEM_PROMPT_KEY.path, "You are a helpful assistant."
                )

                yield updated_context

        # Create processing flow that uses the system prompt
        async def prompt_aware_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
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
        agent_flow = agent.to_flow()

        async def input_stream() -> AsyncGenerator[Any, None]:
            yield test_input

        results = []
        async for result in agent_flow(input_stream()):
            results.append(result)

        assert len(results) == 1
        expected_response = "[You are a helpful assistant.] Response to: Hello!"
        assert results[0].response == expected_response  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_flow_agent_memory_integration(self) -> None:
        """Test FlowAgent with memory/conversation history using external memory store."""

        # External memory store (simulates database or session storage)
        conversation_memory = []

        # Create a memory-aware system flow
        async def memory_system_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
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
        async def memory_processing_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
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
        agent_flow = agent.to_flow()

        messages = ["Hello!", "How are you?", "Goodbye!"]

        for i, message in enumerate(messages):
            test_input = AgentInput(message=message)

            async def single_input(
                captured_input: Any = test_input,
            ) -> AsyncGenerator[Any, None]:
                yield captured_input

            async for result in agent_flow(single_input()):
                # Expected message count: user messages so far
                expected_message_count = i + 1
                expected = (
                    f"This is message #{expected_message_count}. You said: {message}"
                )
                assert result.response == expected  # type: ignore[attr-defined]

    def test_flow_agent_validation(self) -> None:
        """Test FlowAgent input/output validation."""

        async def simple_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
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
    async def test_flow_agent_error_handling(self) -> None:
        """Test FlowAgent error handling."""

        async def error_system_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def error_processing_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
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
        agent_flow = agent.to_flow()

        async def input_stream() -> AsyncGenerator[Any, None]:
            yield test_input

        # Should propagate the error
        with pytest.raises(ValueError, match="Processing error"):
            async for _result in agent_flow(input_stream()):
                pass

    @pytest.mark.asyncio
    async def test_flow_agent_run_error_handling(self) -> None:
        """Test FlowAgent run method error handling."""

        async def error_system_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def error_processing_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for _context in stream:
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

        # Should propagate the error through run method
        with pytest.raises(ValueError, match="Processing error"):
            await agent.run(test_input)

    @pytest.mark.asyncio
    async def test_flow_agent_composition(self) -> None:
        """Test composing FlowAgent with other flows."""

        # Create a simple agent
        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def simple_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
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
        async def post_processor(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for output in stream:
                # Add exclamation mark to response
                output.response += "!"
                yield output

        post_flow = Flow(post_processor, name="post_processor")

        # Compose agent >> post_processor
        composed_flow = agent.to_flow() >> post_flow

        test_input = AgentInput(message="Hello")

        async def input_stream() -> AsyncGenerator[Any, None]:
            yield test_input

        results = []
        async for result in composed_flow(input_stream()):
            results.append(result)

        assert len(results) == 1
        assert results[0].response == "Processed: Hello!"

    @pytest.mark.asyncio
    async def test_flow_agent_multiple_inputs(self) -> None:
        """Test FlowAgent handling multiple inputs in sequence."""

        async def batch_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def batch_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
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

        agent_flow = agent.to_flow()

        async def multi_input() -> AsyncGenerator[Any, None]:
            for inp in inputs:
                yield inp

        results = []
        async for result in agent_flow(multi_input()):
            results.append(result)

        assert len(results) == 3
        assert results[0].response == "Batch: First"  # type: ignore[attr-defined]
        assert results[1].response == "Batch: Second"  # type: ignore[attr-defined]
        assert results[2].response == "Batch: Third"  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_flow_agent_fallback_output_handling(self) -> None:
        """Test FlowAgent fallback when output schema is missing from context."""

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def empty_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """Processing flow that doesn't put output schema in context."""
            async for context in stream:
                # Just pass context through without adding output schema
                yield context

        agent = FlowAgent(
            name="fallback_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="system"),
            processing_flow=Flow(empty_processing, name="empty_processing"),
        )

        test_input = AgentInput(message="test")

        # Should create a fallback output when schema is missing from context
        result = await agent.run(test_input)
        assert isinstance(result, AgentOutput)
        # Fallback should create default AgentOutput
        assert result.response == ""  # Default empty string
        assert result.metadata == {}  # Default empty dict

    @pytest.mark.asyncio
    async def test_flow_agent_no_system_results(self) -> None:
        """Test FlowAgent when system flow produces no results."""

        async def empty_system_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """System flow that produces no results."""
            # Consume the stream but don't yield anything
            async for _ in stream:
                pass
            # Don't yield anything
            return
            yield  # Make it an async generator

        async def simple_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                input_data = AgentInput.from_context(context)
                output_data = AgentOutput(response=f"Processed: {input_data.message}")
                updated_context = output_data.to_context(context)
                yield updated_context

        agent = FlowAgent(
            name="empty_system_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(empty_system_flow, name="empty_system"),
            processing_flow=Flow(simple_processing, name="simple_processing"),
        )

        test_input = AgentInput(message="test")
        result = await agent.run(test_input)

        # Should still work with original context when system flow produces no results
        assert isinstance(result, AgentOutput)
        assert result.response == "Processed: test"

    @pytest.mark.asyncio
    async def test_flow_agent_no_processing_results(self) -> None:
        """Test FlowAgent when processing flow produces no results."""

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def empty_processing_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """Processing flow that produces no results."""
            # Consume the stream but don't yield anything
            async for _ in stream:
                pass
            # Don't yield anything
            return
            yield  # Make it an async generator

        agent = FlowAgent(
            name="empty_processing_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="simple_system"),
            processing_flow=Flow(empty_processing_flow, name="empty_processing"),
        )

        test_input = AgentInput(message="test")
        result = await agent.run(test_input)

        # Should create fallback output when processing flow produces no results
        assert isinstance(result, AgentOutput)
        assert result.response == ""  # Default fallback
        assert result.metadata == {}

    @pytest.mark.asyncio
    async def test_flow_agent_input_validation_and_conversion(self) -> None:
        """Test FlowAgent input validation and conversion."""

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def simple_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                input_data = AgentInput.from_context(context)
                output_data = AgentOutput(response=f"Validated: {input_data.message}")
                updated_context = output_data.to_context(context)
                yield updated_context

        agent = FlowAgent(
            name="validation_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="simple_system"),
            processing_flow=Flow(simple_processing, name="simple_processing"),
        )

        # Test with dict input that needs validation
        dict_input = {"message": "test dict input"}
        result = await agent.run(dict_input)  # type: ignore[arg-type]

        assert isinstance(result, AgentOutput)
        assert result.response == "Validated: test dict input"

    @pytest.mark.asyncio
    async def test_flow_agent_output_validation_and_conversion(self) -> None:
        """Test FlowAgent output validation and conversion."""

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def dict_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """Processing flow that puts dict in context instead of schema."""
            async for context in stream:
                input_data = AgentInput.from_context(context)
                # Put a dict in context that needs validation
                from context import ContextKey

                OUTPUT_KEY = ContextKey[dict[str, Any]]("agent_output")
                output_dict = {
                    "response": f"Dict: {input_data.message}",
                    "metadata": {"test": True},
                }
                context.set(OUTPUT_KEY.path, output_dict)
                # Don't put the schema in context - this will test validation
                yield context

        agent = FlowAgent(
            name="validation_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="simple_system"),
            processing_flow=Flow(dict_processing, name="dict_processing"),
        )

        test_input = AgentInput(message="test")
        result = await agent.run(test_input)

        # Should create fallback when output schema not in context
        assert isinstance(result, AgentOutput)
        assert result.response == ""  # Default fallback
        assert result.metadata == {}

    def _create_complex_output_schema(self) -> type[ContextFlowSchema]:
        """Create test schema with various field types."""
        from pydantic import Field

        class ComplexOutput(ContextFlowSchema):
            """Test schema with various field types."""

            str_field: str = Field(..., description="String field")
            int_field: int = Field(..., description="Integer field")
            float_field: float = Field(..., description="Float field")
            bool_field: bool = Field(..., description="Boolean field")
            list_field: list[str] = Field(..., description="List field")
            dict_field: dict[str, Any] = Field(..., description="Dict field")
            none_field: Any = Field(..., description="None field")

        return ComplexOutput

    def _assert_fallback_field_values(self, result: Any) -> None:
        """Assert fallback field values are correct."""
        assert result.str_field == ""
        assert result.int_field == 0
        assert result.float_field == 0.0
        assert result.bool_field is False
        assert result.list_field == []
        assert result.dict_field == {}
        assert result.none_field is None

    @pytest.mark.asyncio
    async def test_flow_agent_fallback_field_types(self) -> None:
        """Test FlowAgent fallback with different field types."""
        ComplexOutput = self._create_complex_output_schema()

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def no_output_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """Processing flow that doesn't put output schema in context."""
            async for context in stream:
                yield context

        agent = FlowAgent(
            name="fallback_agent",
            input_schema=AgentInput,
            output_schema=ComplexOutput,
            system_flow=Flow(simple_system, name="simple_system"),
            processing_flow=Flow(no_output_processing, name="no_output_processing"),
        )

        test_input = AgentInput(message="test")
        result = await agent.run(test_input)

        assert isinstance(result, ComplexOutput)
        self._assert_fallback_field_values(result)

    @pytest.mark.asyncio
    async def test_flow_agent_fallback_type_error(self) -> None:
        """Test FlowAgent fallback when schema cannot be created."""
        from pydantic import Field

        class UncreatableOutput(ContextFlowSchema):
            """Test schema that cannot be created with default values."""

            def __init__(self, **data: Any):
                # Force a TypeError when trying to create with default values
                if not data.get("special_field"):
                    raise TypeError("Cannot create without special_field")
                super().__init__(**data)

            special_field: str = Field(..., description="Special required field")

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def no_output_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """Processing flow that doesn't put output schema in context."""
            async for context in stream:
                # Just pass through without adding output schema
                yield context

        agent = FlowAgent(
            name="fallback_error_agent",
            input_schema=AgentInput,
            output_schema=UncreatableOutput,
            system_flow=Flow(simple_system, name="simple_system"),
            processing_flow=Flow(no_output_processing, name="no_output_processing"),
        )

        test_input = AgentInput(message="test")

        # Should raise error when fallback cannot be created
        with pytest.raises(
            ValueError,
            match="Output schema not found in context and cannot create fallback",
        ):
            await agent.run(test_input)

    @pytest.mark.asyncio
    async def test_flow_agent_output_validation_conversion(self) -> None:
        """Test FlowAgent output validation when context contains dict instead of schema."""

        async def simple_system(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for context in stream:
                yield context

        async def dict_output_processing(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            """Processing flow that puts dict data in context."""
            async for context in stream:
                # Create an AgentOutput from dict then put it in context
                # This will test the validation/conversion path
                output_dict = {
                    "response": "Converted response",
                    "metadata": {"converted": True},
                }
                # Put the dict in context, which will trigger validation
                output_schema = AgentOutput.model_validate(output_dict)
                context = output_schema.to_context(context)

                yield context

        agent = FlowAgent(
            name="validation_agent",
            input_schema=AgentInput,
            output_schema=AgentOutput,
            system_flow=Flow(simple_system, name="simple_system"),
            processing_flow=Flow(dict_output_processing, name="dict_output_processing"),
        )

        test_input = AgentInput(message="test")
        result = await agent.run(test_input)

        # Should convert dict to schema and validate
        assert isinstance(result, AgentOutput)
        assert result.response == "Converted response"
        assert result.metadata == {"converted": True}
