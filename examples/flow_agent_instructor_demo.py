#!/usr/bin/env python3

"""Example demonstrating Instructor integration with FlowAgent for structured LLM output.

This example shows how to:
1. Create input/output schemas for structured LLM interactions
2. Use InstructorFlow for type-safe LLM completions
3. Compose InstructorFlow with other flows in a pipeline
4. Handle complex nested data structures in LLM responses
5. Integrate with FlowAgent for complete agent workflows
"""

import asyncio

from pydantic import BaseModel, Field

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow import Flow
from goldentooth_agent.core.flow_agent import (
    AgentInput,
    AgentOutput,
    FlowAgent,
    FlowIOSchema,
    InstructorFlow,
    MockLLMClient,
    create_instructor_flow,
    create_system_prompt_flow,
)


# Define schemas for task planning
class TaskPlanningInput(FlowIOSchema):
    """Input schema for task planning requests."""

    goal: str = Field(..., description="The main goal or objective to achieve")
    constraints: str = Field(
        default="", description="Any constraints or limitations to consider"
    )
    timeline: str = Field(default="", description="Preferred timeline or deadline")
    resources: str = Field(
        default="", description="Available resources (people, tools, budget, etc.)"
    )


class TaskStep(BaseModel):
    """A single step in a task plan."""

    step_number: int = Field(
        ..., description="Sequential number of the step (1, 2, 3...)"
    )
    title: str = Field(..., description="Brief, actionable title of the step")
    description: str = Field(..., description="Detailed description of what to do")
    estimated_duration: str = Field(
        ..., description="Estimated time to complete this step"
    )
    dependencies: list[int] = Field(
        default_factory=list, description="Step numbers that must be completed first"
    )
    skills_required: list[str] = Field(
        default_factory=list, description="Skills or expertise needed for this step"
    )


class RiskAssessment(BaseModel):
    """Risk assessment for a task plan."""

    risk_level: str = Field(..., description="Overall risk level: low, medium, high")
    potential_blockers: list[str] = Field(
        default_factory=list,
        description="Things that could prevent successful completion",
    )
    mitigation_strategies: list[str] = Field(
        default_factory=list, description="Ways to reduce or handle the risks"
    )


class TaskPlanningOutput(FlowIOSchema):
    """Output schema for structured task planning."""

    plan_title: str = Field(..., description="Clear, descriptive title for the plan")
    overview: str = Field(..., description="High-level summary of the approach")
    steps: list[TaskStep] = Field(..., description="Detailed breakdown of steps")
    total_estimated_time: str = Field(
        ..., description="Total time estimate for all steps"
    )
    success_criteria: list[str] = Field(
        ..., description="Specific, measurable criteria for success"
    )
    risk_assessment: RiskAssessment = Field(
        ..., description="Analysis of risks and mitigation"
    )


# Define schemas for code review
class CodeReviewInput(FlowIOSchema):
    """Input schema for code review requests."""

    code: str = Field(..., description="The code to review")
    language: str = Field(
        ..., description="Programming language (e.g., Python, JavaScript)"
    )
    context: str = Field(
        default="", description="Additional context about the code's purpose"
    )


class CodeIssue(BaseModel):
    """A single code issue found during review."""

    issue_type: str = Field(
        ..., description="Type: bug, style, performance, security, etc."
    )
    severity: str = Field(
        ..., description="Severity level: low, medium, high, critical"
    )
    line_number: int = Field(default=0, description="Line number where issue occurs")
    description: str = Field(..., description="Clear description of the issue")
    suggestion: str = Field(..., description="Specific suggestion for improvement")


class CodeReviewOutput(FlowIOSchema):
    """Output schema for structured code review."""

    overall_quality: str = Field(
        ..., description="Overall code quality: excellent, good, fair, poor"
    )
    summary: str = Field(..., description="Brief summary of the review findings")
    issues: list[CodeIssue] = Field(
        default_factory=list, description="List of issues found in the code"
    )
    positive_aspects: list[str] = Field(
        default_factory=list, description="Things done well in the code"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="High-level recommendations for improvement"
    )


async def demonstrate_instructor_basics():
    """Demonstrate basic InstructorFlow usage."""
    print("🎯 Basic Instructor Integration Demo")
    print("=" * 45)

    # Create mock responses for demonstration
    mock_plan = TaskPlanningOutput(
        plan_title="Launch Personal Blog Website",
        overview="Create and deploy a personal blog using modern web technologies with focus on performance and SEO.",
        steps=[
            TaskStep(
                step_number=1,
                title="Setup Development Environment",
                description="Install Node.js, create project structure, initialize git repository",
                estimated_duration="2 hours",
                dependencies=[],
                skills_required=["Basic command line", "Git basics"],
            ),
            TaskStep(
                step_number=2,
                title="Design and Create Content Structure",
                description="Design site layout, create initial blog posts, setup content management",
                estimated_duration="8 hours",
                dependencies=[1],
                skills_required=["Web design", "Content writing"],
            ),
            TaskStep(
                step_number=3,
                title="Implement Frontend",
                description="Build responsive UI components, implement blog functionality, optimize for mobile",
                estimated_duration="12 hours",
                dependencies=[2],
                skills_required=[
                    "HTML/CSS",
                    "JavaScript",
                    "React or similar framework",
                ],
            ),
            TaskStep(
                step_number=4,
                title="Deploy and Launch",
                description="Configure hosting, setup CI/CD pipeline, perform final testing and launch",
                estimated_duration="4 hours",
                dependencies=[3],
                skills_required=["DevOps basics", "Hosting platforms"],
            ),
        ],
        total_estimated_time="26 hours (about 1 week part-time)",
        success_criteria=[
            "Website loads in under 3 seconds",
            "Mobile-responsive design works on all devices",
            "At least 5 high-quality blog posts published",
            "SEO optimized with proper meta tags",
            "Analytics tracking implemented",
        ],
        risk_assessment=RiskAssessment(
            risk_level="medium",
            potential_blockers=[
                "Limited web development experience",
                "Content creation taking longer than expected",
                "Hosting or deployment issues",
            ],
            mitigation_strategies=[
                "Follow online tutorials and documentation",
                "Prepare content outline before development",
                "Use proven hosting platforms like Netlify or Vercel",
                "Have backup deployment options ready",
            ],
        ),
    )

    # Create mock client with predefined response
    mock_client = MockLLMClient(mock_responses={TaskPlanningOutput: mock_plan})

    # Create InstructorFlow
    instructor_flow = InstructorFlow(
        client=mock_client,
        model="gpt-4",
        input_schema=TaskPlanningInput,
        output_schema=TaskPlanningOutput,
        system_prompt="You are an expert project manager and consultant. Create detailed, actionable plans that consider real-world constraints and risks.",
    )

    # Test input
    planning_input = TaskPlanningInput(
        goal="Create a personal blog website",
        constraints="Limited budget, working part-time on weekends",
        timeline="Launch within 1 month",
        resources="Personal computer, basic web development knowledge",
    )

    # Convert to context and execute
    context = Context()
    context = planning_input.to_context(context)

    flow = instructor_flow.as_flow()

    async def single_context_stream():
        yield context

    print("Input Goal:", planning_input.goal)
    print("Timeline:", planning_input.timeline)
    print("Resources:", planning_input.resources)
    print()

    async for result_context in flow(single_context_stream()):
        output = TaskPlanningOutput.from_context(result_context)

        print(f"📋 Plan: {output.plan_title}")
        print(f"📝 Overview: {output.overview}")
        print(f"⏱️  Total Time: {output.total_estimated_time}")
        print()

        print("📌 Steps:")
        for step in output.steps:
            deps = (
                f" (depends on: {', '.join(map(str, step.dependencies))})"
                if step.dependencies
                else ""
            )
            print(f"  {step.step_number}. {step.title}{deps}")
            print(f"     Duration: {step.estimated_duration}")
            print(f"     Skills: {', '.join(step.skills_required)}")
            print()

        print("✅ Success Criteria:")
        for criterion in output.success_criteria:
            print(f"  • {criterion}")
        print()

        print(f"⚠️  Risk Assessment ({output.risk_assessment.risk_level} risk):")
        print("  Potential Blockers:")
        for blocker in output.risk_assessment.potential_blockers:
            print(f"    • {blocker}")
        print("  Mitigation Strategies:")
        for strategy in output.risk_assessment.mitigation_strategies:
            print(f"    • {strategy}")


async def demonstrate_flow_composition():
    """Demonstrate composing InstructorFlow with other flows."""
    print("\n🔗 Flow Composition Demo")
    print("=" * 30)

    # Create mock response for code review
    mock_review = CodeReviewOutput(
        overall_quality="good",
        summary="Well-structured code with some opportunities for improvement",
        issues=[
            CodeIssue(
                issue_type="style",
                severity="medium",
                line_number=15,
                description="Variable name 'data' is too generic",
                suggestion="Use more descriptive name like 'user_profiles' or 'customer_data'",
            ),
            CodeIssue(
                issue_type="performance",
                severity="low",
                line_number=28,
                description="Nested loop could be optimized",
                suggestion="Consider using a dictionary lookup or set intersection for better performance",
            ),
        ],
        positive_aspects=[
            "Clear function names and structure",
            "Good error handling",
            "Appropriate use of type hints",
        ],
        recommendations=[
            "Add docstrings to all functions",
            "Consider adding unit tests",
            "Use more descriptive variable names",
        ],
    )

    mock_client = MockLLMClient(mock_responses={CodeReviewOutput: mock_review})

    # Create system prompt flow
    system_flow = create_system_prompt_flow(
        "You are a senior software engineer conducting a thorough code review. "
        "Focus on code quality, best practices, potential bugs, and performance improvements."
    )

    # Create instructor flow for code review
    instructor_flow = InstructorFlow(
        client=mock_client,
        model="gpt-4",
        input_schema=CodeReviewInput,
        output_schema=CodeReviewOutput,
    )

    # Create a formatting flow that processes the review output
    async def format_review_flow(stream):
        async for context in stream:
            review = CodeReviewOutput.from_context(context)

            # Create a formatted report
            report_lines = [
                f"Code Review Report - Quality: {review.overall_quality.upper()}",
                "=" * 50,
                f"Summary: {review.summary}",
                "",
                "Issues Found:",
            ]

            for issue in review.issues:
                report_lines.extend(
                    [
                        f"  🔍 {issue.issue_type.title()} (Line {issue.line_number}) - {issue.severity.upper()}",
                        f"     Problem: {issue.description}",
                        f"     Fix: {issue.suggestion}",
                        "",
                    ]
                )

            report_lines.extend(
                [
                    "Positive Aspects:",
                    *[f"  ✅ {aspect}" for aspect in review.positive_aspects],
                    "",
                    "Recommendations:",
                    *[f"  📝 {rec}" for rec in review.recommendations],
                ]
            )

            # Add formatted report back to context
            context.set("formatted_report", "\n".join(report_lines))
            yield context

    formatter_flow = Flow(format_review_flow, name="review_formatter")

    # Compose the flows: system_prompt >> instructor >> formatter
    composed_flow = system_flow >> instructor_flow.as_flow() >> formatter_flow

    # Test with sample code
    code_input = CodeReviewInput(
        code="""
def process_data(data):
    results = []
    for item in data:
        for value in item.values():
            if value > 0:
                results.append(value * 2)
    return results

def main():
    data = [{'a': 1, 'b': 2}, {'c': 3, 'd': -1}]
    processed = process_data(data)
    print(processed)
""",
        language="Python",
        context="Function to process nested data structures and filter positive values",
    )

    context = Context()
    context = code_input.to_context(context)

    async def code_stream():
        yield context

    print("Reviewing Python code with composed flow pipeline...")
    print()

    async for result_context in composed_flow(code_stream()):
        report = result_context.get("formatted_report")
        print(report)


async def demonstrate_agent_integration():
    """Demonstrate full FlowAgent integration with InstructorFlow."""
    print("\n🤖 FlowAgent + Instructor Integration Demo")
    print("=" * 45)

    # Create mock response
    mock_output = AgentOutput(
        response="I've successfully analyzed your task and created a structured plan. The plan includes 4 main steps with risk assessment and success criteria.",
        metadata={
            "model": "gpt-4",
            "processing_time": "2.3s",
            "confidence": 0.92,
            "structured_output": True,
        },
    )

    mock_client = MockLLMClient(mock_responses={AgentOutput: mock_output})

    # Create system flow that sets up the agent context
    async def agent_system_flow(stream):
        async for context in stream:
            # Add agent-specific configuration
            context.set("agent_mode", "task_planning")
            context.set("response_format", "structured")
            context.set("agent_persona", "expert_consultant")
            yield context

    system_flow = Flow(agent_system_flow, name="agent_system")

    # Create processing flow using InstructorFlow
    processing_flow = create_instructor_flow(
        client=mock_client,
        model="gpt-4",
        input_schema=AgentInput,
        output_schema=AgentOutput,
        system_prompt="You are an AI assistant that helps with task planning and project management.",
    )

    # Create FlowAgent with instructor-powered processing
    planning_agent = FlowAgent(
        name="task_planning_agent",
        input_schema=AgentInput,
        output_schema=AgentOutput,
        system_flow=system_flow,
        processing_flow=processing_flow,
    )

    # Test agent execution
    agent_input = AgentInput(
        message="Help me plan a project to learn machine learning in 3 months",
        context_data={
            "user_background": "Software engineer with Python experience",
            "available_time": "10 hours per week",
            "preferred_style": "hands-on projects",
        },
    )

    # Execute agent
    agent_flow = planning_agent.as_flow()

    async def agent_input_stream():
        yield agent_input

    print("Agent Input:", agent_input.message)
    print("Context:", agent_input.context_data)
    print()

    async for result in agent_flow(agent_input_stream()):
        print("Agent Response:", result.response)
        print()
        print("Metadata:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")

    print()
    print("🎯 Summary")
    print("=" * 20)
    print("✅ InstructorFlow provides structured LLM output with type safety")
    print("✅ Seamless integration with Flow composition system")
    print("✅ Compatible with FlowAgent for complete agent workflows")
    print("✅ Mock client enables testing without API calls")
    print("✅ Rich schema validation with Pydantic models")


async def main():
    """Run all demonstration examples."""
    await demonstrate_instructor_basics()
    await demonstrate_flow_composition()
    await demonstrate_agent_integration()


if __name__ == "__main__":
    asyncio.run(main())
