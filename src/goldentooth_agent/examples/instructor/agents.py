"""Instructor-powered agents with structured output capabilities."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent import AgentInput, FlowAgent
from goldentooth_agent.core.llm import ClaudeFlowClient
from goldentooth_agent.flow_engine import Flow

from .schemas import (
    CodeAnalysis,
    Difficulty,
    PersonData,
    Recipe,
    Sentiment,
    SentimentAnalysis,
    TaskList,
)


def create_data_extractor_agent(
    name: str = "data_extractor",
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
) -> FlowAgent:
    """Create an agent that extracts structured person data from text.

    Args:
        name: Agent name
        model: Claude model to use
        api_key: Anthropic API key

    Returns:
        FlowAgent that extracts PersonData from text input
    """
    claude_client = ClaudeFlowClient(api_key=api_key, default_model=model)

    async def system_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            context.set(
                "system_prompt",
                "You are a data extraction specialist. Extract structured information about people from the given text. "
                "Be accurate and only include information that is explicitly mentioned.",
            )
            yield context

    async def processing_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            try:
                input_data = AgentInput.from_context(context)
                system_msg = context.get("system_prompt", default=None)

                messages = [
                    {
                        "role": "user",
                        "content": f"Extract person information from: {input_data.message}",
                    }
                ]

                kwargs: dict[str, Any] = {}
                if system_msg:
                    kwargs["system"] = system_msg  # type: ignore[unreachable]

                result = await claude_client.create_completion(
                    response_model=PersonData,
                    messages=messages,
                    **kwargs,
                )

                # Ensure we have the correct type (not streaming)
                if isinstance(result, PersonData):
                    yield result.to_context(context)
                else:
                    raise RuntimeError("Unexpected streaming response")

            except Exception as e:
                error_result = PersonData(
                    name="Error",
                    contact_info={"error": str(e)},
                )
                yield error_result.to_context(context)

    return FlowAgent(
        name=name,
        input_schema=AgentInput,
        output_schema=PersonData,
        system_flow=Flow(system_flow, name=f"{name}_system"),
        processing_flow=Flow(processing_flow, name=f"{name}_processing"),
    )


def create_sentiment_analyzer_agent(
    name: str = "sentiment_analyzer",
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
) -> FlowAgent:
    """Create an agent that performs structured sentiment analysis.

    Args:
        name: Agent name
        model: Claude model to use
        api_key: Anthropic API key

    Returns:
        FlowAgent that analyzes sentiment with structured output
    """
    claude_client = ClaudeFlowClient(api_key=api_key, default_model=model)

    async def system_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            context.set(
                "system_prompt",
                "You are a sentiment analysis expert. Analyze the emotional tone of text and provide "
                "detailed, structured results including confidence scores and reasoning.",
            )
            yield context

    async def processing_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            try:
                input_data = AgentInput.from_context(context)
                system_msg = context.get("system_prompt", default=None)

                messages = [
                    {
                        "role": "user",
                        "content": f"Analyze the sentiment of: {input_data.message}",
                    }
                ]

                kwargs: dict[str, Any] = {}
                if system_msg:
                    kwargs["system"] = system_msg  # type: ignore[unreachable]

                result = await claude_client.create_completion(
                    response_model=SentimentAnalysis,
                    messages=messages,
                    **kwargs,
                )

                # Ensure we have the correct type (not streaming)
                if isinstance(result, SentimentAnalysis):
                    yield result.to_context(context)
                else:
                    raise RuntimeError("Unexpected streaming response")

            except Exception as e:
                error_result = SentimentAnalysis(
                    text=input_data.message if "input_data" in locals() else "Unknown",
                    sentiment=Sentiment.NEUTRAL,
                    confidence=0.0,
                    reasoning=f"Error occurred: {str(e)}",
                )
                yield error_result.to_context(context)

    return FlowAgent(
        name=name,
        input_schema=AgentInput,
        output_schema=SentimentAnalysis,
        system_flow=Flow(system_flow, name=f"{name}_system"),
        processing_flow=Flow(processing_flow, name=f"{name}_processing"),
    )


def create_task_planner_agent(
    name: str = "task_planner",
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
) -> FlowAgent:
    """Create an agent that breaks down projects into structured task lists.

    Args:
        name: Agent name
        model: Claude model to use
        api_key: Anthropic API key

    Returns:
        FlowAgent that creates structured task breakdowns
    """
    claude_client = ClaudeFlowClient(api_key=api_key, default_model=model)

    async def system_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            context.set(
                "system_prompt",
                "You are a project management expert. Break down projects into well-structured, "
                "actionable tasks with priorities and time estimates. Consider dependencies and logical ordering.",
            )
            yield context

    async def processing_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            try:
                input_data = AgentInput.from_context(context)
                system_msg = context.get("system_prompt", default=None)

                messages = [
                    {
                        "role": "user",
                        "content": f"Create a task breakdown for: {input_data.message}",
                    }
                ]

                kwargs: dict[str, Any] = {}
                if system_msg:
                    kwargs["system"] = system_msg  # type: ignore[unreachable]

                result = await claude_client.create_completion(
                    response_model=TaskList,
                    messages=messages,
                    **kwargs,
                )

                # Ensure we have the correct type (not streaming)
                if isinstance(result, TaskList):
                    yield result.to_context(context)
                else:
                    raise RuntimeError("Unexpected streaming response")

            except Exception:
                error_result = TaskList(
                    project_name="Error",
                    tasks=[],
                    total_estimated_time="Unknown",
                    suggested_order=[],
                )
                yield error_result.to_context(context)

    return FlowAgent(
        name=name,
        input_schema=AgentInput,
        output_schema=TaskList,
        system_flow=Flow(system_flow, name=f"{name}_system"),
        processing_flow=Flow(processing_flow, name=f"{name}_processing"),
    )


def create_code_reviewer_agent(
    name: str = "code_reviewer",
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
) -> FlowAgent:
    """Create an agent that performs structured code analysis and review.

    Args:
        name: Agent name
        model: Claude model to use
        api_key: Anthropic API key

    Returns:
        FlowAgent that analyzes code with structured output
    """
    claude_client = ClaudeFlowClient(api_key=api_key, default_model=model)

    async def system_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            context.set(
                "system_prompt",
                "You are a senior software engineer and code reviewer. Analyze code for quality, "
                "security, performance, and best practices. Provide specific, actionable feedback.",
            )
            yield context

    async def processing_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            try:
                input_data = AgentInput.from_context(context)
                system_msg = context.get("system_prompt", default=None)

                messages = [
                    {
                        "role": "user",
                        "content": f"Review this code:\n\n{input_data.message}",
                    }
                ]

                kwargs: dict[str, Any] = {}
                if system_msg:
                    kwargs["system"] = system_msg  # type: ignore[unreachable]

                result = await claude_client.create_completion(
                    response_model=CodeAnalysis,
                    messages=messages,
                    **kwargs,
                )

                # Ensure we have the correct type (not streaming)
                if isinstance(result, CodeAnalysis):
                    yield result.to_context(context)
                else:
                    raise RuntimeError("Unexpected streaming response")

            except Exception as e:
                error_result = CodeAnalysis(
                    language="unknown",
                    overall_quality=1,
                    summary=f"Error occurred during analysis: {str(e)}",
                )
                yield error_result.to_context(context)

    return FlowAgent(
        name=name,
        input_schema=AgentInput,
        output_schema=CodeAnalysis,
        system_flow=Flow(system_flow, name=f"{name}_system"),
        processing_flow=Flow(processing_flow, name=f"{name}_processing"),
    )


def create_recipe_generator_agent(
    name: str = "recipe_generator",
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
) -> FlowAgent:
    """Create an agent that generates structured recipes.

    Args:
        name: Agent name
        model: Claude model to use
        api_key: Anthropic API key

    Returns:
        FlowAgent that creates structured recipes
    """
    claude_client = ClaudeFlowClient(api_key=api_key, default_model=model)

    async def system_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            context.set(
                "system_prompt",
                "You are a professional chef and recipe developer. Create detailed, well-structured recipes "
                "with precise ingredients, clear instructions, and helpful tips.",
            )
            yield context

    async def processing_flow(stream: AsyncIterator[Context]) -> AsyncIterator[Context]:
        async for context in stream:
            try:
                input_data = AgentInput.from_context(context)
                system_msg = context.get("system_prompt", default=None)

                messages = [
                    {
                        "role": "user",
                        "content": f"Create a recipe for: {input_data.message}",
                    }
                ]

                kwargs: dict[str, Any] = {}
                if system_msg:
                    kwargs["system"] = system_msg  # type: ignore[unreachable]

                result = await claude_client.create_completion(
                    response_model=Recipe,
                    messages=messages,
                    **kwargs,
                )

                # Ensure we have the correct type (not streaming)
                if isinstance(result, Recipe):
                    yield result.to_context(context)
                else:
                    raise RuntimeError("Unexpected streaming response")

            except Exception as e:
                error_result = Recipe(
                    name="Error Recipe",
                    description=f"Error: {str(e)}",
                    difficulty=Difficulty.BEGINNER,
                    prep_time="0 min",
                    cook_time="0 min",
                    servings=1,
                    ingredients=[],
                    instructions=[],
                )
                yield error_result.to_context(context)

    return FlowAgent(
        name=name,
        input_schema=AgentInput,
        output_schema=Recipe,
        system_flow=Flow(system_flow, name=f"{name}_system"),
        processing_flow=Flow(processing_flow, name=f"{name}_processing"),
    )
