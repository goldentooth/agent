"""
Tests for instructor-powered agents with structured output capabilities.
"""

import asyncio
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent import AgentInput, FlowAgent
from goldentooth_agent.examples.instructor.agents import (
    create_code_reviewer_agent,
    create_data_extractor_agent,
    create_recipe_generator_agent,
    create_sentiment_analyzer_agent,
    create_task_planner_agent,
)
from goldentooth_agent.examples.instructor.schemas import (
    CodeAnalysis,
    Difficulty,
    PersonData,
    Recipe,
    Sentiment,
    SentimentAnalysis,
    TaskList,
)


async def async_list_to_stream(items: list) -> AsyncIterator:
    """Convert a list to an async iterator for testing."""
    for item in items:
        yield item


class TestDataExtractorAgent:
    """Test data extractor agent functionality."""

    def test_create_data_extractor_agent(self):
        """Test creating a data extractor agent."""
        agent = create_data_extractor_agent(
            name="test_extractor",
            model="claude-3-5-sonnet-20241022",
            api_key="test_key",
        )

        assert isinstance(agent, FlowAgent)
        assert agent.name == "test_extractor"
        assert agent.input_schema == AgentInput
        assert agent.output_schema == PersonData
        assert agent.system_flow is not None
        assert agent.processing_flow is not None

    def test_create_data_extractor_agent_defaults(self):
        """Test creating agent with default parameters."""
        agent = create_data_extractor_agent()

        assert agent.name == "data_extractor"
        assert agent.input_schema == AgentInput
        assert agent.output_schema == PersonData

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_data_extractor_system_flow(self, mock_client_class):
        """Test data extractor system flow."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        agent = create_data_extractor_agent(api_key="test_key")

        # Test system flow
        context = Context()
        contexts_out = []

        async for ctx in agent.system_flow(async_list_to_stream([context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        assert "system_prompt" in contexts_out[0]
        system_prompt = contexts_out[0].get("system_prompt")
        assert "data extraction specialist" in system_prompt

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_data_extractor_processing_flow_success(self, mock_client_class):
        """Test successful data extraction processing flow."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the Claude client response
        mock_person_data = PersonData(
            name="John Doe",
            age=30,
            occupation="Software Engineer",
            location="San Francisco",
            skills=["Python", "JavaScript"],
            contact_info={"email": "john@example.com"},
        )
        mock_client.create_completion = AsyncMock(return_value=mock_person_data)

        agent = create_data_extractor_agent(api_key="test_key")

        # Create input context
        context = Context()
        context.set("system_prompt", "Test system prompt")
        agent_input = AgentInput(
            message="John Doe is a 30-year-old software engineer from San Francisco"
        )
        input_context = agent_input.to_context(context)

        # Test processing flow
        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result_data = PersonData.from_context(contexts_out[0])
        assert result_data.name == "John Doe"
        assert result_data.age == 30
        assert result_data.occupation == "Software Engineer"

        # Verify API call
        mock_client.create_completion.assert_called_once()
        call_args = mock_client.create_completion.call_args
        assert call_args.kwargs["response_model"] == PersonData

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_data_extractor_processing_flow_error(self, mock_client_class):
        """Test error handling in data extraction processing flow."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_completion = AsyncMock(side_effect=Exception("API Error"))

        agent = create_data_extractor_agent(api_key="test_key")

        # Create input context
        context = Context()
        agent_input = AgentInput(message="Test message")
        input_context = agent_input.to_context(context)

        # Test processing flow with error
        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result_data = PersonData.from_context(contexts_out[0])
        assert result_data.name == "Error"
        assert "API Error" in result_data.contact_info["error"]


class TestSentimentAnalyzerAgent:
    """Test sentiment analyzer agent functionality."""

    def test_create_sentiment_analyzer_agent(self):
        """Test creating a sentiment analyzer agent."""
        agent = create_sentiment_analyzer_agent(
            name="test_sentiment",
            model="claude-3-5-sonnet-20241022",
            api_key="test_key",
        )

        assert isinstance(agent, FlowAgent)
        assert agent.name == "test_sentiment"
        assert agent.input_schema == AgentInput
        assert agent.output_schema == SentimentAnalysis

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_sentiment_analyzer_system_flow(self, mock_client_class):
        """Test sentiment analyzer system flow."""
        agent = create_sentiment_analyzer_agent()

        context = Context()
        contexts_out = []

        async for ctx in agent.system_flow(async_list_to_stream([context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        system_prompt = contexts_out[0].get("system_prompt")
        assert "sentiment analysis expert" in system_prompt

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_sentiment_analyzer_processing_flow_success(self, mock_client_class):
        """Test successful sentiment analysis processing flow."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_analysis = SentimentAnalysis(
            text="I love this product!",
            sentiment=Sentiment.POSITIVE,
            confidence=0.9,
            keywords=["love"],
            reasoning="Strong positive language",
        )
        mock_client.create_completion = AsyncMock(return_value=mock_analysis)

        agent = create_sentiment_analyzer_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="I love this product!")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = SentimentAnalysis.from_context(contexts_out[0])
        assert result.sentiment == Sentiment.POSITIVE
        assert result.confidence == 0.9

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_sentiment_analyzer_processing_flow_error(self, mock_client_class):
        """Test error handling in sentiment analysis."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_completion = AsyncMock(
            side_effect=Exception("Analysis failed")
        )

        agent = create_sentiment_analyzer_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="Test message")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = SentimentAnalysis.from_context(contexts_out[0])
        assert result.sentiment == Sentiment.NEUTRAL
        assert result.confidence == 0.0
        assert "Analysis failed" in result.reasoning


class TestTaskPlannerAgent:
    """Test task planner agent functionality."""

    def test_create_task_planner_agent(self):
        """Test creating a task planner agent."""
        agent = create_task_planner_agent(
            name="test_planner", model="claude-3-5-sonnet-20241022"
        )

        assert isinstance(agent, FlowAgent)
        assert agent.name == "test_planner"
        assert agent.input_schema == AgentInput
        assert agent.output_schema == TaskList

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_task_planner_system_flow(self, mock_client_class):
        """Test task planner system flow."""
        agent = create_task_planner_agent()

        context = Context()
        contexts_out = []

        async for ctx in agent.system_flow(async_list_to_stream([context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        system_prompt = contexts_out[0].get("system_prompt")
        assert "project management expert" in system_prompt

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_task_planner_processing_flow_success(self, mock_client_class):
        """Test successful task planning processing flow."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_task_list = TaskList(
            project_name="Build Website",
            tasks=[],
            total_estimated_time="2 weeks",
            suggested_order=[],
        )
        mock_client.create_completion = AsyncMock(return_value=mock_task_list)

        agent = create_task_planner_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="Build a personal website")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = TaskList.from_context(contexts_out[0])
        assert result.project_name == "Build Website"
        assert result.total_estimated_time == "2 weeks"

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_task_planner_processing_flow_error(self, mock_client_class):
        """Test error handling in task planning."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_completion = AsyncMock(
            side_effect=Exception("Planning failed")
        )

        agent = create_task_planner_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="Build something")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = TaskList.from_context(contexts_out[0])
        assert result.project_name == "Error"
        assert result.tasks == []


class TestCodeReviewerAgent:
    """Test code reviewer agent functionality."""

    def test_create_code_reviewer_agent(self):
        """Test creating a code reviewer agent."""
        agent = create_code_reviewer_agent(
            name="test_reviewer", model="claude-3-5-sonnet-20241022"
        )

        assert isinstance(agent, FlowAgent)
        assert agent.name == "test_reviewer"
        assert agent.input_schema == AgentInput
        assert agent.output_schema == CodeAnalysis

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_code_reviewer_system_flow(self, mock_client_class):
        """Test code reviewer system flow."""
        agent = create_code_reviewer_agent()

        context = Context()
        contexts_out = []

        async for ctx in agent.system_flow(async_list_to_stream([context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        system_prompt = contexts_out[0].get("system_prompt")
        assert "senior software engineer" in system_prompt

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_code_reviewer_processing_flow_success(self, mock_client_class):
        """Test successful code review processing flow."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_analysis = CodeAnalysis(
            language="python",
            overall_quality=8,
            issues=[],
            positive_aspects=["Good variable names"],
            summary="Well-written code",
        )
        mock_client.create_completion = AsyncMock(return_value=mock_analysis)

        agent = create_code_reviewer_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="def hello(): print('Hello, World!')")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = CodeAnalysis.from_context(contexts_out[0])
        assert result.language == "python"
        assert result.overall_quality == 8

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_code_reviewer_processing_flow_error(self, mock_client_class):
        """Test error handling in code review."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_completion = AsyncMock(
            side_effect=Exception("Review failed")
        )

        agent = create_code_reviewer_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="some code")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = CodeAnalysis.from_context(contexts_out[0])
        assert result.language == "unknown"
        assert result.overall_quality == 1
        assert "Review failed" in result.summary


class TestRecipeGeneratorAgent:
    """Test recipe generator agent functionality."""

    def test_create_recipe_generator_agent(self):
        """Test creating a recipe generator agent."""
        agent = create_recipe_generator_agent(
            name="test_chef", model="claude-3-5-sonnet-20241022"
        )

        assert isinstance(agent, FlowAgent)
        assert agent.name == "test_chef"
        assert agent.input_schema == AgentInput
        assert agent.output_schema == Recipe

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_recipe_generator_system_flow(self, mock_client_class):
        """Test recipe generator system flow."""
        agent = create_recipe_generator_agent()

        context = Context()
        contexts_out = []

        async for ctx in agent.system_flow(async_list_to_stream([context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        system_prompt = contexts_out[0].get("system_prompt")
        assert "professional chef" in system_prompt

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_recipe_generator_processing_flow_success(self, mock_client_class):
        """Test successful recipe generation processing flow."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_recipe = Recipe(
            name="Pasta Carbonara",
            description="Classic Italian pasta dish",
            difficulty=Difficulty.INTERMEDIATE,
            prep_time="10 min",
            cook_time="15 min",
            servings=4,
            ingredients=[],
            instructions=["Cook pasta", "Mix eggs and cheese"],
        )
        mock_client.create_completion = AsyncMock(return_value=mock_recipe)

        agent = create_recipe_generator_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="pasta carbonara")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = Recipe.from_context(contexts_out[0])
        assert result.name == "Pasta Carbonara"
        assert result.difficulty == Difficulty.INTERMEDIATE
        assert result.servings == 4

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    @pytest.mark.asyncio
    async def test_recipe_generator_processing_flow_error(self, mock_client_class):
        """Test error handling in recipe generation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_completion = AsyncMock(
            side_effect=Exception("Generation failed")
        )

        agent = create_recipe_generator_agent(api_key="test_key")

        context = Context()
        agent_input = AgentInput(message="something delicious")
        input_context = agent_input.to_context(context)

        contexts_out = []
        async for ctx in agent.processing_flow(async_list_to_stream([input_context])):
            contexts_out.append(ctx)

        assert len(contexts_out) == 1
        result = Recipe.from_context(contexts_out[0])
        assert result.name == "Error Recipe"
        assert result.difficulty == Difficulty.BEGINNER
        assert "Generation failed" in result.description


class TestAgentIntegration:
    """Test integration scenarios across multiple agents."""

    def test_all_agent_creation_functions_exist(self):
        """Test that all agent creation functions exist and are callable."""
        functions = [
            create_data_extractor_agent,
            create_sentiment_analyzer_agent,
            create_task_planner_agent,
            create_code_reviewer_agent,
            create_recipe_generator_agent,
        ]

        for func in functions:
            assert callable(func)
            # Test that each function can be called with no arguments
            agent = func()
            assert isinstance(agent, FlowAgent)

    def test_agent_names_and_schemas(self):
        """Test that agents have correct default names and schemas."""
        test_cases = [
            (create_data_extractor_agent, "data_extractor", PersonData),
            (create_sentiment_analyzer_agent, "sentiment_analyzer", SentimentAnalysis),
            (create_task_planner_agent, "task_planner", TaskList),
            (create_code_reviewer_agent, "code_reviewer", CodeAnalysis),
            (create_recipe_generator_agent, "recipe_generator", Recipe),
        ]

        for create_func, expected_name, expected_output_schema in test_cases:
            agent = create_func()
            assert agent.name == expected_name
            assert agent.input_schema == AgentInput
            assert agent.output_schema == expected_output_schema

    def test_agent_custom_parameters(self):
        """Test that agents accept custom parameters."""
        custom_name = "custom_agent"
        custom_model = "claude-3-5-haiku-20241022"
        custom_api_key = "sk-test-key"

        agent = create_data_extractor_agent(
            name=custom_name, model=custom_model, api_key=custom_api_key
        )

        assert agent.name == custom_name
        # Model and API key are used internally, so we can't directly test them
        # but we verify the agent was created successfully
        assert isinstance(agent, FlowAgent)

    @patch("goldentooth_agent.examples.instructor.agents.ClaudeFlowClient")
    def test_claude_client_initialization(self, mock_client_class):
        """Test that Claude client is initialized correctly."""
        test_api_key = "test-api-key"
        test_model = "claude-3-5-sonnet-20241022"

        create_data_extractor_agent(api_key=test_api_key, model=test_model)

        # Verify ClaudeFlowClient was called with correct parameters
        mock_client_class.assert_called_with(
            api_key=test_api_key, default_model=test_model
        )

    def test_flow_names(self):
        """Test that flows have appropriate names."""
        agent = create_data_extractor_agent(name="test_agent")

        assert agent.system_flow.name == "test_agent_system"
        assert agent.processing_flow.name == "test_agent_processing"

    @pytest.mark.asyncio
    async def test_streaming_error_handling(self):
        """Test error handling for unexpected streaming responses."""
        with patch(
            "goldentooth_agent.examples.instructor.agents.ClaudeFlowClient"
        ) as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock streaming response (not expected)
            async def mock_streaming_response():
                yield "chunk1"
                yield "chunk2"

            mock_client.create_completion = AsyncMock(
                return_value=mock_streaming_response()
            )

            agent = create_data_extractor_agent(api_key="test_key")

            context = Context()
            agent_input = AgentInput(message="test")
            input_context = agent_input.to_context(context)

            contexts_out = []
            async for ctx in agent.processing_flow(
                async_list_to_stream([input_context])
            ):
                contexts_out.append(ctx)

            # Should handle streaming error gracefully
            assert len(contexts_out) == 1
            result = PersonData.from_context(contexts_out[0])
            assert result.name == "Error"


class TestAgentImports:
    """Test imports and dependencies."""

    def test_all_imports_work(self):
        """Test that all imports work correctly."""
        from goldentooth_agent.examples.instructor.agents import (
            create_code_reviewer_agent,
            create_data_extractor_agent,
            create_recipe_generator_agent,
            create_sentiment_analyzer_agent,
            create_task_planner_agent,
        )

        # All imports should succeed
        assert create_data_extractor_agent is not None
        assert create_sentiment_analyzer_agent is not None
        assert create_task_planner_agent is not None
        assert create_code_reviewer_agent is not None
        assert create_recipe_generator_agent is not None

    def test_schema_imports(self):
        """Test that schema imports work correctly."""
        from goldentooth_agent.examples.instructor.schemas import (
            CodeAnalysis,
            PersonData,
            Recipe,
            SentimentAnalysis,
            TaskList,
        )

        # All schema imports should succeed
        assert PersonData is not None
        assert SentimentAnalysis is not None
        assert TaskList is not None
        assert CodeAnalysis is not None
        assert Recipe is not None

    def test_core_imports(self):
        """Test that core module imports work correctly."""
        from goldentooth_agent.core.context import Context
        from goldentooth_agent.core.flow_agent import AgentInput, FlowAgent
        from goldentooth_agent.core.llm import ClaudeFlowClient
        from goldentooth_agent.flow_engine import Flow

        # All core imports should succeed
        assert Context is not None
        assert AgentInput is not None
        assert FlowAgent is not None
        assert ClaudeFlowClient is not None
        assert Flow is not None

    def test_function_signatures(self):
        """Test that functions have expected signatures."""
        import inspect

        sig = inspect.signature(create_data_extractor_agent)
        params = list(sig.parameters.keys())

        # Should have expected parameters
        assert "name" in params
        assert "model" in params
        assert "api_key" in params

        # Should have proper defaults
        assert sig.parameters["name"].default == "data_extractor"
        assert sig.parameters["model"].default == "claude-3-5-sonnet-20241022"
        assert sig.parameters["api_key"].default is None
