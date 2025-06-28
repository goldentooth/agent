"""Instructor integration examples and structured output schemas."""

from .agents import (
    create_code_reviewer_agent,
    create_data_extractor_agent,
    create_recipe_generator_agent,
    create_sentiment_analyzer_agent,
    create_task_planner_agent,
)
from .schemas import (
    AnalysisResult,
    CodeAnalysis,
    PersonData,
    Recipe,
    SentimentAnalysis,
    TaskList,
)

__all__ = [
    # Schemas
    "AnalysisResult",
    "CodeAnalysis",
    "PersonData",
    "Recipe",
    "SentimentAnalysis",
    "TaskList",
    # Agent Factories
    "create_data_extractor_agent",
    "create_code_reviewer_agent",
    "create_task_planner_agent",
    "create_sentiment_analyzer_agent",
    "create_recipe_generator_agent",
]
