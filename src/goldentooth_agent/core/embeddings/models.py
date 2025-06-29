"""Data models for embeddings and search functionality."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Chunk:
    """Represents a chunk of content for embedding and search."""

    chunk_id: str
    document_id: str
    content: str
    position: int
    metadata: dict[str, Any]
    chunk_type: str

    def __str__(self) -> str:
        """String representation of chunk."""
        return f"Chunk({self.chunk_id}, pos={self.position}, type={self.chunk_type})"

    def __repr__(self) -> str:
        """Detailed representation of chunk."""
        return (
            f"Chunk(chunk_id='{self.chunk_id}', document_id='{self.document_id}', "
            f"position={self.position}, chunk_type='{self.chunk_type}', "
            f"content_length={len(self.content)})"
        )


@dataclass
class SearchResult:
    """Represents a search result with relevance scoring."""

    chunk: Chunk
    relevance_score: float
    metadata: dict[str, Any] | None = None

    def __str__(self) -> str:
        """String representation of search result."""
        return f"SearchResult(chunk={self.chunk.chunk_id}, score={self.relevance_score:.3f})"

    def __repr__(self) -> str:
        """Detailed representation of search result."""
        return (
            f"SearchResult(chunk={self.chunk!r}, relevance_score={self.relevance_score}, "
            f"metadata={self.metadata})"
        )

    @property
    def chunk_id(self) -> str:
        """Get chunk ID for convenience."""
        return self.chunk.chunk_id

    @property
    def document_id(self) -> str:
        """Get document ID for convenience."""
        return self.chunk.document_id

    @property
    def content(self) -> str:
        """Get content for convenience."""
        return self.chunk.content
