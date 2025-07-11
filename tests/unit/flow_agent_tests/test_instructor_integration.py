"""Tests for Instructor integration with FlowAgent for structured LLM output."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
from pydantic import BaseModel, Field

from context import Context, ContextKey
from flow import Flow
from flow_agent.instructor_integration import InstructorFlow, MockLLMClient
from flow_agent.schema import ContextFlowSchema


# Test schemas for Instructor integration
class TaskAnalysisInput(ContextFlowSchema):
    """Input schema for task analysis."""

    task_description: str = Field(..., description="Description of the task to analyze")
    context_info: str = Field(default="", description="Additional context information")


class TaskStep(BaseModel):
    """A single step in a task breakdown."""

    step_number: int = Field(..., description="Sequential number of the step")
    title: str = Field(..., description="Brief title of the step")
    description: str = Field(..., description="Detailed description of what to do")
    estimated_duration: str = Field(..., description="Estimated time to complete")


class TaskAnalysisOutput(ContextFlowSchema):
    """Output schema for task analysis with structured breakdown."""

    task_title: str = Field(..., description="Extracted title of the task")
    complexity: str = Field(..., description="Complexity level: low, medium, high")
    steps: list[TaskStep] = Field(..., description="Breakdown of task into steps")
    total_estimated_time: str = Field(
        ..., description="Total estimated completion time"
    )


class SimpleQuestionInput(ContextFlowSchema):
    """Input schema for simple questions."""

    question: str = Field(..., description="Question to answer")


class SimpleAnswerOutput(ContextFlowSchema):
    """Output schema for simple answers."""

    answer: str = Field(..., description="Answer to the question")
    confidence: float = Field(..., description="Confidence level 0.0-1.0")


class TestMockLLMClient:
    """Test the mock LLM client for testing purposes."""

    def test_mock_client_creation(self) -> None:
        """Test creating a mock LLM client."""
        client = MockLLMClient()
        assert client is not None

    def test_mock_client_with_responses(self) -> None:
        """Test mock client with predefined responses."""
        responses: dict[type[ContextFlowSchema], TaskAnalysisOutput] = {
            TaskAnalysisOutput: TaskAnalysisOutput(
                task_title="Test Task",
                complexity="medium",
                steps=[
                    TaskStep(
                        step_number=1,
                        title="First Step",
                        description="Do the first thing",
                        estimated_duration="30 minutes",
                    )
                ],
                total_estimated_time="30 minutes",
            )
        }

        client = MockLLMClient(mock_responses=responses)
        assert client.mock_responses == responses

    @pytest.mark.asyncio
    async def test_mock_client_completion(self) -> None:
        """Test mock client completion method."""
        # Test with predefined response
        mock_response = SimpleAnswerOutput(answer="42", confidence=0.95)
        client = MockLLMClient(mock_responses={SimpleAnswerOutput: mock_response})

        messages = [{"role": "user", "content": "What is the answer?"}]
        result = await client.create_completion(
            response_model=SimpleAnswerOutput,
            messages=messages,
        )

        assert result == mock_response
        assert result.answer == "42"
        assert result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_mock_client_default_response(self) -> None:
        """Test mock client creating default responses."""
        client = MockLLMClient()

        messages = [{"role": "user", "content": "What is the answer?"}]
        result = await client.create_completion(
            response_model=SimpleAnswerOutput,
            messages=messages,
        )

        # Should create a default response with mock values
        assert isinstance(result, SimpleAnswerOutput)
        assert result.answer == "mock_answer"
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_mock_client_type_validation_error(self) -> None:
        """Test mock client type validation error."""
        # Create a mock response of the wrong type
        wrong_response = SimpleQuestionInput(question="wrong type")
        client = MockLLMClient(mock_responses={SimpleAnswerOutput: wrong_response})

        messages = [{"role": "user", "content": "What is the answer?"}]

        with pytest.raises(
            ValueError, match="Mock response for .* is not of correct type"
        ):
            await client.create_completion(
                response_model=SimpleAnswerOutput,
                messages=messages,
            )


class TestInstructorFlow:
    """Test the InstructorFlow class."""

    def test_instructor_flow_creation(self) -> None:
        """Test basic InstructorFlow creation."""
        client = MockLLMClient()

        flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        assert flow.client == client
        assert flow.model == "gpt-4"
        assert flow.input_schema == SimpleQuestionInput
        assert flow.output_schema == SimpleAnswerOutput

    def test_instructor_flow_with_system_prompt(self) -> None:
        """Test InstructorFlow with system prompt."""
        client = MockLLMClient()
        system_prompt = "You are a helpful assistant."

        flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
            system_prompt=system_prompt,
        )

        assert flow.system_prompt == system_prompt

    def test_instructor_flow_to_flow_conversion(self) -> None:
        """Test converting InstructorFlow to a Flow."""
        # Setup mock response
        mock_response = SimpleAnswerOutput(answer="42", confidence=0.95)
        client = MockLLMClient(mock_responses={SimpleAnswerOutput: mock_response})

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        # Convert to Flow
        flow = instructor_flow.to_flow()
        assert isinstance(flow, Flow)
        assert flow.name == "instructor:gpt-4"

    def _create_task_analysis_mock_response(self) -> TaskAnalysisOutput:
        """Create mock response for task analysis testing."""
        return TaskAnalysisOutput(
            task_title="Build a Web App",
            complexity="high",
            steps=[
                TaskStep(
                    step_number=1,
                    title="Setup Project",
                    description="Initialize project structure",
                    estimated_duration="2 hours",
                ),
                TaskStep(
                    step_number=2,
                    title="Implement Backend",
                    description="Create API endpoints",
                    estimated_duration="8 hours",
                ),
            ],
            total_estimated_time="10 hours",
        )

    def _create_task_analysis_context(self) -> Context:
        """Create context with task analysis input data."""
        context = Context()
        input_data = TaskAnalysisInput(
            task_description="Build a web application for task management",
            context_info="Team of 2 developers, 2 week deadline",
        )
        return input_data.to_context(context)

    def _assert_task_analysis_output(self, output: TaskAnalysisOutput) -> None:
        """Assert task analysis output values."""
        assert output.task_title == "Build a Web App"
        assert output.complexity == "high"
        assert len(output.steps) == 2
        assert output.total_estimated_time == "10 hours"

    @pytest.mark.asyncio
    async def test_instructor_flow_execution_with_context(self) -> None:
        """Test executing InstructorFlow with context input."""
        mock_response = self._create_task_analysis_mock_response()
        client = MockLLMClient(mock_responses={TaskAnalysisOutput: mock_response})

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=TaskAnalysisInput,
            output_schema=TaskAnalysisOutput,
            system_prompt="You are a project management expert.",
        )

        context = self._create_task_analysis_context()
        flow = instructor_flow.to_flow()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        result_context = results[0]
        assert isinstance(result_context, Context)

        output = TaskAnalysisOutput.from_context(result_context)
        self._assert_task_analysis_output(output)

    @pytest.mark.asyncio
    async def test_instructor_flow_multiple_inputs(self) -> None:
        """Test InstructorFlow handling multiple inputs."""
        # Setup mock responses
        responses = [
            SimpleAnswerOutput(answer="Blue", confidence=0.9),
            SimpleAnswerOutput(answer="42", confidence=1.0),
            SimpleAnswerOutput(answer="Pizza", confidence=0.8),
        ]

        # Mock client that cycles through responses
        class CyclingMockClient:
            def __init__(self, responses: list[SimpleAnswerOutput]) -> None:
                super().__init__()
                self.responses = responses
                self.index = 0

            async def create_completion(
                self, *args: Any, **kwargs: Any
            ) -> SimpleAnswerOutput:
                response = self.responses[self.index % len(self.responses)]
                self.index += 1
                return response

        client = CyclingMockClient(responses)

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        # Create multiple questions
        questions = [
            SimpleQuestionInput(question="What is your favorite color?"),
            SimpleQuestionInput(question="What is the answer to everything?"),
            SimpleQuestionInput(question="What is the best food?"),
        ]

        # Convert to contexts
        contexts = []
        for question in questions:
            context = Context()
            context = question.to_context(context)
            contexts.append(context)

        # Execute flow
        flow = instructor_flow.to_flow()

        async def multi_context_stream() -> AsyncGenerator[Context, None]:
            for ctx in contexts:
                yield ctx

        results = []
        async for result in flow(multi_context_stream()):
            results.append(result)

        assert len(results) == 3

        # Check each result
        for i, result_context in enumerate(results):
            output = SimpleAnswerOutput.from_context(result_context)
            assert output.answer == responses[i].answer
            assert output.confidence == responses[i].confidence

    @pytest.mark.asyncio
    async def test_instructor_flow_error_handling(self) -> None:
        """Test InstructorFlow error handling."""

        class ErrorMockClient:
            async def create_completion(self, *args: Any, **kwargs: Any) -> Any:
                raise ValueError("Mock API error")

        client = ErrorMockClient()

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        context = Context()
        input_data = SimpleQuestionInput(question="This will fail")
        context = input_data.to_context(context)

        flow = instructor_flow.to_flow()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        # Should propagate the error
        with pytest.raises(ValueError, match="Mock API error"):
            async for _result in flow(context_stream()):
                pass

    def test_instructor_flow_system_prompt_integration(self) -> None:
        """Test that system prompt is properly integrated into the flow."""
        client = MockLLMClient()
        system_prompt = "You are a helpful coding assistant."

        flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
            system_prompt=system_prompt,
        )

        # Check that system prompt is stored
        assert flow.system_prompt == system_prompt

        # The actual integration test would verify that the system prompt
        # is used in the LLM call, but that would require a real LLM client
        # For now, we just verify it's stored correctly

    def _create_context_with_additional_data(self) -> Context:
        """Create context with additional data for preservation testing."""
        context = Context()
        input_data = SimpleQuestionInput(question="Test question")
        context = input_data.to_context(context)

        session_key = ContextKey[str]("session_id")
        user_key = ContextKey[str]("user_name")
        context.set(session_key.path, "session_123")
        context.set(user_key.path, "alice")
        return context

    def _assert_context_preservation(self, result_context: Context) -> None:
        """Assert that context data is preserved and output is added."""
        session_key = ContextKey[str]("session_id")
        user_key = ContextKey[str]("user_name")

        assert result_context.get(session_key.path) == "session_123"
        assert result_context.get(user_key.path) == "alice"

        output = SimpleAnswerOutput.from_context(result_context)
        assert output.answer == "Test answer"
        assert output.confidence == 0.85

    @pytest.mark.asyncio
    async def test_instructor_flow_context_preservation(self) -> None:
        """Test that InstructorFlow preserves context data through processing."""
        mock_response = SimpleAnswerOutput(answer="Test answer", confidence=0.85)
        client = MockLLMClient(mock_responses={SimpleAnswerOutput: mock_response})

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        context = self._create_context_with_additional_data()
        flow = instructor_flow.to_flow()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        self._assert_context_preservation(results[0])

    def test_instructor_flow_prompt_formatting(self) -> None:
        """Test that input data is properly formatted as prompts."""
        client = MockLLMClient()

        flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        # Test the prompt formatting method
        input_data = SimpleQuestionInput(question="What is the meaning of life?")
        formatted_prompt = flow._format_input_as_prompt(input_data)

        # Should format the input fields as a readable prompt
        assert "Question: What is the meaning of life?" in formatted_prompt
        assert (
            "Context Data" not in formatted_prompt
        )  # Should skip empty context fields

    def _create_complex_task_mock_response(self) -> TaskAnalysisOutput:
        """Create mock response for complex task testing."""
        return TaskAnalysisOutput(
            task_title="Complex Task",
            complexity="high",
            steps=[
                TaskStep(
                    step_number=1,
                    title="Analysis",
                    description="Analyze requirements",
                    estimated_duration="4 hours",
                )
            ],
            total_estimated_time="4 hours",
        )

    def _create_complex_input_context(self) -> Context:
        """Create context with complex input data."""
        context = Context()
        input_data = TaskAnalysisInput(
            task_description="Create a machine learning pipeline",
            context_info="Data science team, Python, 6 month timeline",
        )
        return input_data.to_context(context)

    def _assert_complex_task_output(self, output: TaskAnalysisOutput) -> None:
        """Assert complex task output values."""
        assert output.task_title == "Complex Task"
        assert output.complexity == "high"
        assert len(output.steps) == 1
        assert output.steps[0].title == "Analysis"

    @pytest.mark.asyncio
    async def test_instructor_flow_with_complex_input(self) -> None:
        """Test InstructorFlow with complex input schema."""
        mock_response = self._create_complex_task_mock_response()
        client = MockLLMClient(mock_responses={TaskAnalysisOutput: mock_response})

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=TaskAnalysisInput,
            output_schema=TaskAnalysisOutput,
        )

        context = self._create_complex_input_context()
        flow = instructor_flow.to_flow()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        result_context = results[0]

        output = TaskAnalysisOutput.from_context(result_context)
        self._assert_complex_task_output(output)


class TestUtilityFunctions:
    """Test utility functions in instructor integration."""

    @pytest.mark.asyncio
    async def test_create_instructor_flow_factory(self) -> None:
        """Test create_instructor_flow factory function."""
        from flow_agent.instructor_integration import create_instructor_flow

        client = MockLLMClient()

        flow = create_instructor_flow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
            system_prompt="You are helpful",
            temperature=0.5,
            max_retries=5,
        )

        assert isinstance(flow, Flow)
        assert flow.name == "instructor:gpt-4"

    @pytest.mark.asyncio
    async def test_create_system_prompt_flow(self) -> None:
        """Test create_system_prompt_flow utility."""
        from flow_agent.instructor_integration import (
            SYSTEM_PROMPT_KEY,
            create_system_prompt_flow,
        )

        system_prompt = "You are a helpful assistant."
        flow = create_system_prompt_flow(system_prompt)

        assert isinstance(flow, Flow)
        assert flow.name == "system_prompt"

        # Test execution
        context = Context()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        result_context = results[0]
        assert result_context.get(SYSTEM_PROMPT_KEY.path) == system_prompt

    @pytest.mark.asyncio
    async def test_create_model_config_flow(self) -> None:
        """Test create_model_config_flow utility."""
        from flow_agent.instructor_integration import (
            MAX_TOKENS_KEY,
            MODEL_NAME_KEY,
            TEMPERATURE_KEY,
            create_model_config_flow,
        )

        flow = create_model_config_flow(
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
        )

        assert isinstance(flow, Flow)
        assert flow.name == "model_config"

        # Test execution
        context = Context()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        result_context = results[0]
        assert result_context.get(MODEL_NAME_KEY.path) == "gpt-4"
        assert result_context.get(TEMPERATURE_KEY.path) == 0.7
        assert result_context.get(MAX_TOKENS_KEY.path) == 1000

    @pytest.mark.asyncio
    async def test_create_model_config_flow_no_max_tokens(self) -> None:
        """Test create_model_config_flow without max_tokens."""
        from flow_agent.instructor_integration import (
            MAX_TOKENS_KEY,
            MODEL_NAME_KEY,
            TEMPERATURE_KEY,
            create_model_config_flow,
        )

        flow = create_model_config_flow(
            model="gpt-3.5-turbo",
            temperature=0.2,
        )

        # Test execution
        context = Context()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        result_context = results[0]
        assert result_context.get(MODEL_NAME_KEY.path) == "gpt-3.5-turbo"
        assert result_context.get(TEMPERATURE_KEY.path) == 0.2
        # max_tokens should not be set
        assert result_context.get(MAX_TOKENS_KEY.path, "NOT_SET") == "NOT_SET"

    @pytest.mark.asyncio
    async def test_mock_client_complex_field_defaults(self) -> None:
        """Test mock client with complex field types."""

        class ComplexOutput(ContextFlowSchema):
            """Schema with complex field types."""

            boolean_field: bool = Field(..., description="Boolean field")
            int_field: int = Field(..., description="Integer field")
            float_field: float = Field(..., description="Float field")
            list_field: list[str] = Field(..., description="List field")
            dict_field: dict[str, str] = Field(..., description="Dict field")
            optional_field: str | None = Field(None, description="Optional field")

        client = MockLLMClient()

        messages = [{"role": "user", "content": "Test"}]
        result = await client.create_completion(
            response_model=ComplexOutput,
            messages=messages,
        )

        assert isinstance(result, ComplexOutput)
        assert result.boolean_field is True
        assert result.int_field == 0
        assert result.float_field == 0.0
        assert result.list_field == []
        assert result.dict_field == {}
        assert result.optional_field is None

    @pytest.mark.asyncio
    async def test_mock_client_creation_failure(self) -> None:
        """Test mock client when default instance creation fails."""

        class UncreatableOutput(ContextFlowSchema):
            """Schema that requires specific arguments."""

            required_field: str = Field(..., description="Required field")

        client = MockLLMClient()

        messages = [{"role": "user", "content": "Test"}]

        # Should still work because we generate defaults for required string fields
        result = await client.create_completion(
            response_model=UncreatableOutput,
            messages=messages,
        )

        assert isinstance(result, UncreatableOutput)
        assert result.required_field == "mock_required_field"

    @pytest.mark.asyncio
    async def test_mock_client_no_field_defaults(self) -> None:
        """Test mock client when schema can be created without field defaults."""

        class SimpleOutput(ContextFlowSchema):
            """Schema that can be created without arguments."""

            optional_field: str = "default_value"

        client = MockLLMClient()

        messages = [{"role": "user", "content": "Test"}]
        result = await client.create_completion(
            response_model=SimpleOutput,
            messages=messages,
        )

        assert isinstance(result, SimpleOutput)
        assert result.optional_field == "default_value"

    @pytest.mark.asyncio
    async def test_mock_client_unknown_field_type(self) -> None:
        """Test mock client with unknown field type."""
        from typing import Union

        class UnknownTypeOutput(ContextFlowSchema):
            """Schema with unknown field type."""

            unknown_field: Union[str, int, None] = Field(
                ..., description="Unknown field type"
            )

        client = MockLLMClient()

        messages = [{"role": "user", "content": "Test"}]
        result = await client.create_completion(
            response_model=UnknownTypeOutput,
            messages=messages,
        )

        assert isinstance(result, UnknownTypeOutput)
        assert result.unknown_field is None  # Should default to None for unknown types

    @pytest.mark.asyncio
    async def test_instructor_flow_input_extraction_error(self) -> None:
        """Test InstructorFlow when input extraction fails."""

        class NoInputClient:
            async def create_completion(
                self, *args: Any, **kwargs: Any
            ) -> SimpleAnswerOutput:
                return SimpleAnswerOutput(answer="test", confidence=1.0)

        client = NoInputClient()

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        # Create empty context without the input schema
        context = Context()

        flow = instructor_flow.to_flow()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        # Should raise error when input cannot be extracted
        with pytest.raises(
            ValueError, match="Failed to extract SimpleQuestionInput from context"
        ):
            async for _result in flow(context_stream()):
                pass

    @pytest.mark.asyncio
    async def test_instructor_flow_llm_type_error(self) -> None:
        """Test InstructorFlow when LLM returns wrong type."""

        class WrongTypeClient:
            async def create_completion(self, *args: Any, **kwargs: Any) -> str:
                # Return wrong type
                return "not a schema object"

        client = WrongTypeClient()

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        # Create context with input
        context = Context()
        input_data = SimpleQuestionInput(question="test")
        context = input_data.to_context(context)

        flow = instructor_flow.to_flow()

        async def context_stream() -> AsyncGenerator[Context, None]:
            yield context

        # Should raise error when LLM returns wrong type
        with pytest.raises(ValueError, match="Instructor returned incorrect type"):
            async for _result in flow(context_stream()):
                pass
