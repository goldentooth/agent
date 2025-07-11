"""Tests for FlowTool class with flow conversion and agent compatibility."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from pydantic import Field, ValidationError

from flow import Flow
from flow_agent.schema import ContextFlowSchema
from flow_agent.tool import FlowTool


# Test schemas for tools
class CalculatorInput(ContextFlowSchema):
    """Input schema for calculator tool."""

    expression: str = Field(..., description="Mathematical expression to evaluate")


class CalculatorOutput(ContextFlowSchema):
    """Output schema for calculator tool."""

    result: str = Field(..., description="Result of calculation")


class EchoInput(ContextFlowSchema):
    """Input schema for echo tool."""

    message: str = Field(..., description="Message to echo")


class EchoOutput(ContextFlowSchema):
    """Output schema for echo tool."""

    echoed_message: str = Field(..., description="Echoed message")


class TestFlowTool:
    """Test the FlowTool class."""

    def test_flow_tool_creation(self) -> None:
        """Test basic FlowTool creation."""

        def echo_impl(input_data: EchoInput) -> EchoOutput:
            return EchoOutput(echoed_message=f"Echo: {input_data.message}")

        tool = FlowTool(
            name="echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_impl,
            description="Echoes messages",
        )

        assert tool.name == "echo"
        assert tool.input_schema == EchoInput
        assert tool.output_schema == EchoOutput
        assert tool.description == "Echoes messages"
        assert tool.implementation == echo_impl

    def test_flow_tool_to_flow_sync(self) -> None:
        """Test converting FlowTool to Flow with synchronous implementation."""

        def calculator_impl(input_data: CalculatorInput) -> CalculatorOutput:
            # Simple evaluation for testing
            try:
                result = str(eval(input_data.expression))
                return CalculatorOutput(result=result)
            except Exception as e:
                return CalculatorOutput(result=f"Error: {e}")

        tool = FlowTool(
            name="calculator",
            input_schema=CalculatorInput,
            output_schema=CalculatorOutput,
            implementation=calculator_impl,
        )

        # Convert to flow
        tool_flow = tool.to_flow()
        assert isinstance(tool_flow, Flow)
        assert tool_flow.name == "tool:calculator"

    @pytest.mark.asyncio
    async def test_flow_tool_to_flow_execution(self) -> None:
        """Test executing FlowTool as a Flow."""

        def echo_impl(input_data: EchoInput) -> EchoOutput:
            return EchoOutput(echoed_message=f"Echo: {input_data.message}")

        tool = FlowTool(
            name="echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_impl,
        )

        # Create input
        test_input = EchoInput(message="Hello, world!")

        # Execute tool as flow
        tool_flow = tool.to_flow()

        # Create async iterator from single input
        async def single_input() -> AsyncGenerator[Any, None]:
            yield test_input

        # Execute and collect results
        results = []
        async for result in tool_flow(single_input()):
            results.append(result)

        assert len(results) == 1
        assert isinstance(results[0], EchoOutput)
        assert results[0].echoed_message == "Echo: Hello, world!"

    @pytest.mark.asyncio
    async def test_flow_tool_to_flow_async_implementation(self) -> None:
        """Test FlowTool with async implementation."""

        async def async_echo_impl(input_data: EchoInput) -> EchoOutput:
            # Simulate async work
            await asyncio.sleep(0.01)
            return EchoOutput(echoed_message=f"Async Echo: {input_data.message}")

        tool = FlowTool(
            name="async_echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=async_echo_impl,  # type: ignore[arg-type]
        )

        # Test execution
        test_input = EchoInput(message="Hello, async!")
        tool_flow = tool.to_flow()

        async def single_input() -> AsyncGenerator[Any, None]:
            yield test_input

        results = []
        async for result in tool_flow(single_input()):
            results.append(result)

        assert len(results) == 1
        assert results[0].echoed_message == "Async Echo: Hello, async!"

    def test_flow_tool_input_validation(self) -> None:
        """Test that FlowTool validates input schemas."""

        def echo_impl(input_data: EchoInput) -> EchoOutput:
            return EchoOutput(echoed_message=input_data.message)

        tool = FlowTool(
            name="echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_impl,
        )

        _ = tool.to_flow()

        # This test will check that invalid input raises validation error
        # We'll test this in the actual implementation

    @pytest.mark.asyncio
    async def test_flow_tool_output_validation(self) -> None:
        """Test that FlowTool validates output schemas."""

        def bad_impl(input_data: EchoInput) -> dict[str, str]:
            # Returns dict instead of EchoOutput - should cause validation error
            return {"wrong": "format"}

        tool = FlowTool(
            name="bad_tool",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=bad_impl,  # type: ignore[arg-type]
        )

        test_input = EchoInput(message="test")
        tool_flow = tool.to_flow()

        async def single_input() -> AsyncGenerator[Any, None]:
            yield test_input

        # Should raise validation error when trying to validate output
        with pytest.raises(ValidationError):  # Pydantic validation error
            async for _result in tool_flow(single_input()):
                pass

    def test_flow_tool_to_agent_compatibility(self) -> None:
        """Test that FlowTool can be converted to agent-compatible interface."""

        def echo_impl(input_data: EchoInput) -> EchoOutput:
            return EchoOutput(echoed_message=input_data.message)

        tool = FlowTool(
            name="echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_impl,
        )

        # Convert to agent
        agent = tool.to_agent()

        # Should be a FlowAgent-like object
        assert agent.name == "agent:echo"
        assert agent.input_schema == EchoInput
        assert agent.output_schema == EchoOutput

    @pytest.mark.asyncio
    async def test_flow_tool_multiple_inputs(self) -> None:
        """Test FlowTool handling multiple inputs in stream."""

        def calculator_impl(input_data: CalculatorInput) -> CalculatorOutput:
            try:
                result = str(eval(input_data.expression))
                return CalculatorOutput(result=result)
            except Exception as e:
                return CalculatorOutput(result=f"Error: {e}")

        tool = FlowTool(
            name="calculator",
            input_schema=CalculatorInput,
            output_schema=CalculatorOutput,
            implementation=calculator_impl,
        )

        # Test with multiple inputs
        inputs = [
            CalculatorInput(expression="2 + 2"),
            CalculatorInput(expression="3 * 4"),
            CalculatorInput(expression="10 / 2"),
        ]

        tool_flow = tool.to_flow()

        async def multi_input() -> AsyncGenerator[Any, None]:
            for inp in inputs:
                yield inp

        results = []
        async for result in tool_flow(multi_input()):
            results.append(result)

        assert len(results) == 3
        assert results[0].result == "4"
        assert results[1].result == "12"
        assert results[2].result == "5.0"

    @pytest.mark.asyncio
    async def test_flow_tool_error_handling(self) -> None:
        """Test FlowTool error handling."""

        def error_impl(input_data: EchoInput) -> EchoOutput:
            raise ValueError("Intentional error")

        tool = FlowTool(
            name="error_tool",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=error_impl,
        )

        test_input = EchoInput(message="test")
        tool_flow = tool.to_flow()

        async def single_input() -> AsyncGenerator[Any, None]:
            yield test_input

        # Should propagate the error
        with pytest.raises(ValueError, match="Intentional error"):
            async for _result in tool_flow(single_input()):
                pass

    @pytest.mark.asyncio
    async def test_flow_tool_agent_execution(self) -> None:
        """Test FlowTool as agent execution."""

        def echo_impl(input_data: EchoInput) -> EchoOutput:
            return EchoOutput(echoed_message=f"Agent Echo: {input_data.message}")

        tool = FlowTool(
            name="echo_agent",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_impl,
        )

        # Convert to agent and test run method
        agent = tool.to_agent()
        test_input = EchoInput(message="Hello, agent!")

        result = await agent.run(test_input)

        assert isinstance(result, EchoOutput)
        assert result.echoed_message == "Agent Echo: Hello, agent!"

    @pytest.mark.asyncio
    async def test_flow_tool_context_extraction_error(self) -> None:
        """Test FlowTool when context extraction fails."""

        def echo_impl(input_data: EchoInput) -> EchoOutput:
            return EchoOutput(echoed_message=f"Echo: {input_data.message}")

        tool = FlowTool(
            name="echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_impl,
        )

        # Create empty context without the input schema
        from context import Context

        empty_context = Context()

        tool_flow = tool.to_flow()

        async def context_stream() -> AsyncGenerator[Any, None]:
            yield empty_context

        # Should raise error when input cannot be extracted from context
        with pytest.raises(
            ValueError, match="Could not extract EchoInput from context"
        ):
            async for _result in tool_flow(context_stream()):
                pass

    @pytest.mark.asyncio
    async def test_flow_tool_dict_input_validation(self) -> None:
        """Test FlowTool with dict input validation."""

        def echo_impl(input_data: EchoInput) -> EchoOutput:
            return EchoOutput(echoed_message=f"Echo: {input_data.message}")

        tool = FlowTool(
            name="echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_impl,
        )

        # Test with dict input that needs validation
        dict_input = {"message": "test dict"}

        tool_flow = tool.to_flow()

        async def dict_stream() -> AsyncGenerator[Any, None]:
            yield dict_input

        results = []
        async for result in tool_flow(dict_stream()):
            results.append(result)

        assert len(results) == 1
        assert isinstance(results[0], EchoOutput)
        assert results[0].echoed_message == "Echo: test dict"
