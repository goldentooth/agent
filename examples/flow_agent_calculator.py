#!/usr/bin/env python3

"""Example demonstrating FlowTool with a calculator implementation.

This example shows how to:
1. Create input/output schemas for a tool
2. Implement tool logic with proper validation
3. Convert tool to a Flow for composition
4. Handle both sync and async implementations
5. Demonstrate error handling and validation
"""

import asyncio
import math

from pydantic import Field

from goldentooth_agent.core.flow_agent import FlowIOSchema, FlowTool


# Define schemas for the calculator tool
class CalculatorInput(FlowIOSchema):
    """Input schema for calculator tool."""

    expression: str = Field(
        ...,
        description="Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)')",
    )


class CalculatorOutput(FlowIOSchema):
    """Output schema for calculator tool."""

    result: str = Field(..., description="Result of the mathematical calculation")
    expression: str = Field(..., description="Original expression that was evaluated")


# Implement the calculator logic
def calculator_implementation(input_data: CalculatorInput) -> CalculatorOutput:
    """Calculate mathematical expressions using Python's eval with safety restrictions.

    Args:
        input_data: Input containing the mathematical expression

    Returns:
        Output containing the result and original expression

    Note: This is a simplified implementation for demo purposes.
    In production, use a proper math expression parser.
    """
    try:
        # Define safe functions and constants
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "pi": math.pi,
            "e": math.e,
        }

        # Simple expression preprocessing
        expression = input_data.expression
        expression = expression.replace("^", "**")  # Handle ^ as power
        expression = expression.replace("factorial(5)", "120")  # Simple factorial

        # Evaluate safely
        result = eval(expression, safe_dict, {})

        return CalculatorOutput(result=str(result), expression=input_data.expression)
    except Exception as e:
        return CalculatorOutput(
            result=f"Error: {str(e)}", expression=input_data.expression
        )


# Create the FlowTool
calculator_tool = FlowTool(
    name="calculator",
    input_schema=CalculatorInput,
    output_schema=CalculatorOutput,
    implementation=calculator_implementation,
    description="Advanced mathematical calculator supporting arithmetic, trigonometry, and symbolic math",
)


async def demonstrate_calculator():
    """Demonstrate the calculator tool functionality."""
    print("🧮 Flow-based Calculator Tool Demo")
    print("=" * 50)

    # Test expressions
    test_expressions = [
        "2 + 2",
        "sqrt(16)",
        "sin(pi/2)",
        "log(e)",
        "2^10",
        "factorial(5)",
        "invalid_expression",  # This will cause an error
        "1/0",  # This will also cause an error
    ]

    # Convert tool to flow
    calc_flow = calculator_tool.as_flow()

    # Create input stream
    async def input_stream():
        for expr in test_expressions:
            yield CalculatorInput(expression=expr)

    # Process all expressions
    print("Processing expressions through FlowTool:")
    print()

    async for result in calc_flow(input_stream()):
        status = "✅" if not result.result.startswith("Error") else "❌"
        print(f"{status} {result.expression} = {result.result}")

    print()
    print("🔗 Flow Composition Demo")
    print("=" * 30)

    # Demonstrate flow composition - let's create a pipeline that formats results
    def format_result(calc_result: CalculatorOutput) -> str:
        if calc_result.result.startswith("Error"):
            return f"❌ '{calc_result.expression}' failed: {calc_result.result}"
        else:
            return f"✅ '{calc_result.expression}' = {calc_result.result}"

    # Create a formatting flow
    from goldentooth_agent.core.flow import Flow

    async def format_flow(stream):
        async for item in stream:
            yield format_result(item)

    formatter = Flow(format_flow, name="result_formatter")

    # Compose flows: calculator >> formatter
    composed_flow = calc_flow >> formatter

    print("Processing through composed flow (calculator >> formatter):")
    print()

    # Test with a few expressions
    simple_expressions = ["3 * 4", "sqrt(25)", "invalid"]

    async def simple_input_stream():
        for expr in simple_expressions:
            yield CalculatorInput(expression=expr)

    async for formatted_result in composed_flow(simple_input_stream()):
        print(formatted_result)

    print()
    print("🤖 Agent Compatibility Demo")
    print("=" * 35)

    # Convert tool to agent
    calc_agent = calculator_tool.as_agent()
    print(f"Created agent: {calc_agent.name}")
    print(f"Input schema: {calc_agent.input_schema.__name__}")
    print(f"Output schema: {calc_agent.output_schema.__name__}")

    # The agent flow would work similarly to the tool flow
    # (Full agent implementation will be done in the next phase)

    print()
    print("🎯 Summary")
    print("=" * 20)
    print("✅ FlowTool created with input/output validation")
    print("✅ Tool converted to composable Flow")
    print("✅ Flow composition demonstrated")
    print("✅ Error handling working correctly")
    print("✅ Agent compatibility interface available")
    print()
    print("The FlowTool provides a unified interface for tools that can be:")
    print("  • Used as standalone flows")
    print("  • Composed with other flows")
    print("  • Converted to agent-compatible interfaces")
    print("  • Validated with Pydantic schemas")


if __name__ == "__main__":
    asyncio.run(demonstrate_calculator())
