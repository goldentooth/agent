"""
Agent codebase introspection system.

This module provides introspection capabilities for the agent to analyze its own codebase
structure, documentation, and behavior patterns.
"""

from .collection import CodebaseCollection
from .introspection import CodebaseIntrospectionService, IntrospectionQuery, IntrospectionResult
from .schema import CodebaseDocument, CodebaseDocumentType

__all__ = [
    "CodebaseCollection",
    "CodebaseIntrospectionService",
    "IntrospectionQuery",
    "IntrospectionResult",
    "CodebaseDocument",
    "CodebaseDocumentType",
]