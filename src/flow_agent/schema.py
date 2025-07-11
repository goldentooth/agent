"""Agent-specific schemas for flow-based agent system.

This module re-exports the core agent schemas from context_flow for convenience
and provides any additional agent-specific schema definitions.
"""

from context_flow.schema import AgentInput, AgentOutput, ContextFlowSchema

# Re-export for convenience
__all__ = [
    "ContextFlowSchema",
    "AgentInput",
    "AgentOutput",
]
