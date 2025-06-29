"""Tests for Instructor integration with FlowAgent for structured LLM output."""

import pytest
from pydantic import BaseModel, Field

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent.instructor_integration import (
    InstructorFlow,
    MockLLMClient,
)
from goldentooth_agent.core.flow_agent.schema import FlowIOSchema
from goldentooth_agent.flow_engine import Flow


# Test schemas for Instructor integration
class TaskAnalysisInput(FlowIOSchema):
    """Input schema for task analysis."""

    task_description: str = Field(..., description="Description of the task to analyze")
    context_info: str = Field(default="", description="Additional context information")


class TaskStep(BaseModel):
    """A single step in a task breakdown."""

    step_number: int = Field(..., description="Sequential number of the step")
    title: str = Field(..., description="Brief title of the step")
    description: str = Field(..., description="Detailed description of what to do")
    estimated_duration: str = Field(..., description="Estimated time to complete")


class TaskAnalysisOutput(FlowIOSchema):
    """Output schema for task analysis with structured breakdown."""

    task_title: str = Field(..., description="Extracted title of the task")
    complexity: str = Field(..., description="Complexity level: low, medium, high")
    steps: list[TaskStep] = Field(..., description="Breakdown of task into steps")
    total_estimated_time: str = Field(
        ..., description="Total estimated completion time"
    )


class SimpleQuestionInput(FlowIOSchema):
    """Input schema for simple questions."""

    question: str = Field(..., description="Question to answer")


class SimpleAnswerOutput(FlowIOSchema):
    """Output schema for simple answers."""

    answer: str = Field(..., description="Answer to the question")
    confidence: float = Field(..., description="Confidence level 0.0-1.0")


class TestMockLLMClient:
    """Test the mock LLM client for testing purposes."""

    def test_mock_client_creation(self):
        """Test creating a mock LLM client."""
        client = MockLLMClient()
        assert client is not None

    def test_mock_client_with_responses(self):
        """Test mock client with predefined responses."""
        responses = {
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


class TestInstructorFlow:
    """Test the InstructorFlow class."""

    def test_instructor_flow_creation(self):
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

    def test_instructor_flow_with_system_prompt(self):
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

    @pytest.mark.asyncio
    async def test_instructor_flow_as_flow(self):
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
        flow = instructor_flow.as_flow()
        assert isinstance(flow, Flow)
        assert flow.name == "instructor:gpt-4"

    @pytest.mark.asyncio
    async def test_instructor_flow_execution_with_context(self):
        """Test executing InstructorFlow with context input."""
        # Setup mock response
        mock_response = TaskAnalysisOutput(
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

        client = MockLLMClient(mock_responses={TaskAnalysisOutput: mock_response})

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=TaskAnalysisInput,
            output_schema=TaskAnalysisOutput,
            system_prompt="You are a project management expert.",
        )

        # Create context with input data
        context = Context()
        input_data = TaskAnalysisInput(
            task_description="Build a web application for task management",
            context_info="Team of 2 developers, 2 week deadline",
        )
        context = input_data.to_context(context)

        # Execute flow
        flow = instructor_flow.as_flow()

        async def context_stream():
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        result_context = results[0]
        assert isinstance(result_context, Context)

        # Extract output from context
        output = TaskAnalysisOutput.from_context(result_context)
        assert output.task_title == "Build a Web App"
        assert output.complexity == "high"
        assert len(output.steps) == 2
        assert output.total_estimated_time == "10 hours"

    @pytest.mark.asyncio
    async def test_instructor_flow_multiple_inputs(self):
        """Test InstructorFlow handling multiple inputs."""
        # Setup mock responses
        responses = [
            SimpleAnswerOutput(answer="Blue", confidence=0.9),
            SimpleAnswerOutput(answer="42", confidence=1.0),
            SimpleAnswerOutput(answer="Pizza", confidence=0.8),
        ]

        # Mock client that cycles through responses
        class CyclingMockClient:
            def __init__(self, responses):
                self.responses = responses
                self.index = 0

            async def create_completion(self, *args, **kwargs):
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
        flow = instructor_flow.as_flow()

        async def multi_context_stream():
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
    async def test_instructor_flow_error_handling(self):
        """Test InstructorFlow error handling."""

        class ErrorMockClient:
            async def create_completion(self, *args, **kwargs):
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

        flow = instructor_flow.as_flow()

        async def context_stream():
            yield context

        # Should propagate the error
        with pytest.raises(ValueError, match="Mock API error"):
            async for _result in flow(context_stream()):
                pass

    def test_instructor_flow_system_prompt_integration(self):
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

    @pytest.mark.asyncio
    async def test_instructor_flow_context_preservation(self):
        """Test that InstructorFlow preserves context data through processing."""
        mock_response = SimpleAnswerOutput(answer="Test answer", confidence=0.85)
        client = MockLLMClient(mock_responses={SimpleAnswerOutput: mock_response})

        instructor_flow = InstructorFlow(
            client=client,
            model="gpt-4",
            input_schema=SimpleQuestionInput,
            output_schema=SimpleAnswerOutput,
        )

        # Create context with additional data
        context = Context()
        input_data = SimpleQuestionInput(question="Test question")
        context = input_data.to_context(context)

        # Add some additional context data that should be preserved
        from goldentooth_agent.core.context import ContextKey

        session_key = ContextKey[str]("session_id")
        user_key = ContextKey[str]("user_name")

        context.set(session_key.path, "session_123")
        context.set(user_key.path, "alice")

        # Execute flow
        flow = instructor_flow.as_flow()

        async def context_stream():
            yield context

        results = []
        async for result in flow(context_stream()):
            results.append(result)

        assert len(results) == 1
        result_context = results[0]

        # Check that additional context data is preserved
        assert result_context.get(session_key.path) == "session_123"
        assert result_context.get(user_key.path) == "alice"

        # Check that output was added to context
        output = SimpleAnswerOutput.from_context(result_context)
        assert output.answer == "Test answer"
        assert output.confidence == 0.85
