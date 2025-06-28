"""Structured output schemas for Instructor integration examples."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from goldentooth_agent.core.flow_agent import FlowIOSchema


# Sentiment Analysis Schema
class Sentiment(str, Enum):
    """Sentiment categories."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentAnalysis(FlowIOSchema):
    """Structured sentiment analysis result."""

    text: str = Field(..., description="The analyzed text")
    sentiment: Sentiment = Field(..., description="Overall sentiment classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    keywords: list[str] = Field(
        default_factory=list, description="Key emotional words found"
    )
    reasoning: str = Field(
        ..., description="Brief explanation of the sentiment classification"
    )


# Person Data Extraction Schema
class PersonData(FlowIOSchema):
    """Structured person information extraction."""

    name: str = Field(..., description="Full name of the person")
    age: int | None = Field(None, ge=0, le=150, description="Age if mentioned")
    occupation: str | None = Field(None, description="Job or profession if mentioned")
    location: str | None = Field(
        None, description="City, state, or country if mentioned"
    )
    skills: list[str] = Field(
        default_factory=list, description="Mentioned skills or abilities"
    )
    contact_info: dict[str, str] = Field(
        default_factory=dict, description="Email, phone, etc."
    )


# Task Planning Schema
class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    """Individual task item."""

    title: str = Field(..., description="Brief task title")
    description: str = Field(..., description="Detailed task description")
    priority: Priority = Field(..., description="Task priority level")
    estimated_time: str = Field(
        ..., description="Estimated time to complete (e.g., '2 hours', '1 day')"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Tasks that must be completed first"
    )


class TaskList(FlowIOSchema):
    """Structured task breakdown and planning."""

    project_name: str = Field(..., description="Name or title of the project")
    tasks: list[Task] = Field(..., description="List of tasks to complete")
    total_estimated_time: str = Field(..., description="Total estimated project time")
    suggested_order: list[str] = Field(
        ..., description="Recommended task execution order (task titles)"
    )


# Code Analysis Schema
class Severity(str, Enum):
    """Issue severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CodeIssue(BaseModel):
    """Individual code issue or suggestion."""

    line_number: int | None = Field(None, description="Line number if applicable")
    severity: Severity = Field(..., description="Issue severity level")
    category: str = Field(
        ..., description="Type of issue (e.g., 'security', 'performance', 'style')"
    )
    message: str = Field(..., description="Description of the issue")
    suggestion: str = Field(..., description="Recommended fix or improvement")


class CodeAnalysis(FlowIOSchema):
    """Structured code review and analysis."""

    language: str = Field(..., description="Programming language detected")
    overall_quality: int = Field(
        ..., ge=1, le=10, description="Overall code quality score (1-10)"
    )
    issues: list[CodeIssue] = Field(
        default_factory=list, description="Found issues and suggestions"
    )
    positive_aspects: list[str] = Field(
        default_factory=list, description="Good practices observed"
    )
    summary: str = Field(..., description="Overall analysis summary")


# Recipe Generation Schema
class Difficulty(str, Enum):
    """Recipe difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Ingredient(BaseModel):
    """Recipe ingredient with amount."""

    name: str = Field(..., description="Ingredient name")
    amount: str = Field(..., description="Amount needed (e.g., '2 cups', '1 tsp')")
    notes: str | None = Field(
        None, description="Additional notes (e.g., 'finely chopped')"
    )


class Recipe(FlowIOSchema):
    """Structured recipe with ingredients and instructions."""

    name: str = Field(..., description="Recipe name")
    description: str = Field(..., description="Brief recipe description")
    difficulty: Difficulty = Field(..., description="Recipe difficulty level")
    prep_time: str = Field(..., description="Preparation time")
    cook_time: str = Field(..., description="Cooking time")
    servings: int = Field(..., ge=1, description="Number of servings")
    ingredients: list[Ingredient] = Field(
        ..., description="List of ingredients with amounts"
    )
    instructions: list[str] = Field(
        ..., description="Step-by-step cooking instructions"
    )
    tips: list[str] = Field(default_factory=list, description="Helpful cooking tips")


# General Analysis Result Schema
class AnalysisResult(FlowIOSchema):
    """Generic structured analysis result."""

    input_type: str = Field(..., description="Type of input analyzed")
    key_findings: list[str] = Field(..., description="Main discoveries or insights")
    metrics: dict[str, float] = Field(
        default_factory=dict, description="Quantitative metrics"
    )
    categories: list[str] = Field(
        default_factory=list, description="Relevant categories or tags"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Suggested actions"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence in analysis"
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional context information"
    )
