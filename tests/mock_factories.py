"""
Type-safe mock factories to prevent signature drift.
"""

from typing import Any
from unittest.mock import Mock

from .protocols import VectorStoreProtocol


class TypeSafeMockVectorStore:
    """Type-safe mock implementation of VectorStoreProtocol."""

    def __init__(self):
        self.documents: dict[str, dict[str, Any]] = {}
        self.call_log: list[tuple[str, str, int]] = []

    def store_document(
        self,
        store_type: str,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store a document and its embedding."""
        full_doc_id = f"{store_type}:{document_id}"
        # Generate a dummy embedding if empty list provided
        if not embedding:
            embedding = [0.1] * 1536  # Standard embedding size
        self.documents[full_doc_id] = {
            "text": content,
            "embedding": embedding,
            "metadata": metadata or {},
            "store_type": store_type,
        }
        self.call_log.append(("store_document", full_doc_id, len(content)))
        return full_doc_id

    def store_document_chunks(
        self,
        store_type: str,
        document_id: str,
        chunks: list[Any],
        embeddings: list[list[float]],
        document_metadata: dict[str, Any] | None = None,
    ) -> list[str]:
        """Store document chunks and their embeddings."""
        chunk_ids = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{store_type}:{document_id}:chunk_{i}"
            self.documents[chunk_id] = {
                "text": str(chunk),
                "embedding": embedding,
                "metadata": document_metadata or {},
                "store_type": store_type,
                "chunk_index": i,
            }
            chunk_ids.append(chunk_id)
            self.call_log.append(("store_chunk", chunk_id, len(str(chunk))))
        return chunk_ids

    async def add_document(
        self, text: str, document_id: str, source: Any, metadata: dict[str, Any]
    ) -> None:
        """Add a document to the vector store."""
        self.documents[document_id] = {
            "text": text,
            "source": source,
            "metadata": metadata,
        }
        self.call_log.append(("add_document", document_id, len(text)))

    async def search(
        self, query: str, limit: int = 10, metadata_filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Search for similar documents."""
        results = []
        for doc_id, doc_data in self.documents.items():
            if query.lower() in doc_data["text"].lower():
                results.append(
                    {
                        "document_id": doc_id,
                        "content": doc_data["text"],
                        "score": 0.8,
                        "metadata": doc_data.get("metadata", {}),
                    }
                )
        return results[:limit]

    def search_similar(
        self, 
        query_embedding: list[float], 
        limit: int = 10, 
        store_type: str | None = None,
        include_chunks: bool = False
    ) -> list[dict[str, Any]]:
        """Search for documents similar to the query embedding."""
        # Simple mock - return documents based on store_type filter
        results = []
        for doc_id, doc_data in self.documents.items():
            if store_type and doc_data.get("store_type") != store_type:
                continue
            results.append({
                "document_id": doc_id,
                "content": doc_data["text"],
                "score": 0.8,  # Mock similarity score
                "metadata": doc_data.get("metadata", {}),
            })
        return results[:limit]

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by ID."""
        return self.documents.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        return self.documents.pop(doc_id, None) is not None

    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        return {
            "document_count": len(self.documents),
            "total_size": sum(len(doc["text"]) for doc in self.documents.values()),
        }


def create_vector_store_mock() -> VectorStoreProtocol:
    """Create a type-safe vector store mock that implements the protocol."""
    return TypeSafeMockVectorStore()  # type: ignore[return-value]


def create_mock_with_spec(cls: type) -> Mock:
    """Create a mock with proper spec to prevent attribute errors."""
    return Mock(spec=cls)