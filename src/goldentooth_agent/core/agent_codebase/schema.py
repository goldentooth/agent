"""
Schema definitions for codebase introspection documents.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CodebaseDocumentType(str, Enum):
    """Types of documents in the codebase collection."""

    MODULE_API = "module_api"
    MODULE_BACKGROUND = "module_background"
    SOURCE_CODE = "source_code"
    FUNCTION_DEFINITION = "function_definition"
    CLASS_DEFINITION = "class_definition"
    TEST_CODE = "test_code"
    EXAMPLE_CODE = "example_code"
    CONFIGURATION = "configuration"
    ARCHITECTURE_OVERVIEW = "architecture_overview"


class CodebaseDocument(BaseModel):
    """A document extracted from the codebase for introspection."""

    # Core identification
    document_id: str = Field(..., description="Unique identifier for this document")
    document_type: CodebaseDocumentType = Field(..., description="Type of document")

    # Content
    title: str = Field(..., description="Human-readable title")
    content: str = Field(..., description="Full text content")
    summary: str = Field(default="", description="Brief summary of content")

    # Source information
    file_path: str = Field(..., description="Path to source file")
    line_start: int = Field(default=0, description="Starting line number")
    line_end: int = Field(default=0, description="Ending line number")

    # Metadata
    module_path: str = Field(
        ..., description="Python module path (e.g., 'goldentooth_agent.core.flow')"
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    dependencies: list[str] = Field(
        default_factory=list, description="Dependencies/imports"
    )

    # Code-specific metadata
    signature: str = Field(default="", description="Function/class signature")
    docstring: str = Field(default="", description="Docstring content")
    complexity_score: float = Field(default=0.0, description="Complexity metric (0-1)")

    # Relationships
    related_documents: list[str] = Field(
        default_factory=list, description="Related document IDs"
    )

    # Additional structured data
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    def get_searchable_text(self) -> str:
        """Get text optimized for search indexing."""
        parts = [
            self.title,
            self.summary,
            self.content,
            self.docstring,
            " ".join(self.tags),
            self.module_path,
        ]
        return "\n".join(part for part in parts if part)

    def get_chunk_size_hint(self) -> int:
        """Suggest chunk size based on document type."""
        type_hints = {
            CodebaseDocumentType.MODULE_API: 2000,
            CodebaseDocumentType.MODULE_BACKGROUND: 3000,
            CodebaseDocumentType.SOURCE_CODE: 1000,
            CodebaseDocumentType.FUNCTION_DEFINITION: 800,
            CodebaseDocumentType.CLASS_DEFINITION: 1500,
            CodebaseDocumentType.TEST_CODE: 1000,
            CodebaseDocumentType.EXAMPLE_CODE: 1200,
            CodebaseDocumentType.CONFIGURATION: 800,
            CodebaseDocumentType.ARCHITECTURE_OVERVIEW: 4000,
        }
        return type_hints.get(self.document_type, 1000)
