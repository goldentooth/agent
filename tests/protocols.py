"""
Test protocols to ensure mock signature compliance.
"""

from typing import Any, Protocol, runtime_checkable
from collections.abc import Awaitable


@runtime_checkable
class VectorStoreProtocol(Protocol):
    """Protocol defining the VectorStore interface for testing."""

    def store_document(
        self,
        store_type: str,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store a document and its embedding."""
        ...

    def store_document_chunks(
        self,
        store_type: str,
        document_id: str,
        chunks: list[Any],
        embeddings: list[list[float]],
        document_metadata: dict[str, Any] | None = None,
    ) -> list[str]:
        """Store document chunks and their embeddings."""
        ...

    async def add_document(
        self, text: str, document_id: str, source: Any, metadata: dict[str, Any]
    ) -> None:
        """Add a document to the vector store."""
        ...

    async def search(
        self, query: str, limit: int = 10, metadata_filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Search for similar documents."""
        ...

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by ID."""
        ...

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        ...