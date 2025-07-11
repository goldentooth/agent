"""Flow-based Agent System - A unified framework for agents, tools, and user interactions."""

from .agent import FlowAgent
from .instructor_integration import (
    InstructorFlow,
    MockLLMClient,
    create_instructor_flow,
    create_model_config_flow,
    create_system_prompt_flow,
)
from .schema import AgentInput, AgentOutput, ContextFlowSchema
from .tool import FlowTool

__all__ = [
    "ContextFlowSchema",
    "AgentInput",
    "AgentOutput",
    "FlowTool",
    "FlowAgent",
    "InstructorFlow",
    "MockLLMClient",
    "create_instructor_flow",
    "create_system_prompt_flow",
    "create_model_config_flow",
]
