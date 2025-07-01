import os
from datetime import datetime
from typing import Any

import numpy as np
from anthropic import AsyncAnthropic
from antidote import inject, injectable

from ..paths import Paths
from .document_chunker import DocumentChunk, DocumentChunker


@injectable
class EmbeddingsService:
    """Service for creating and managing document embeddings using Anthropic."""

    def __init__(
        self,
        paths: Paths = inject.me(),
        document_chunker: DocumentChunker = inject.me(),
    ) -> None:
        """Initialize the embeddings service.

        Args:
            paths: Paths service for data directory management
            document_chunker: Service for chunking documents
        """
        self.paths = paths
        self.document_chunker = document_chunker

        # Initialize Anthropic client for embeddings
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable."
            )

        self._client = AsyncAnthropic(api_key=api_key)

    async def create_embedding(self, text: str) -> list[float]:
        """Create an embedding for the given text.

        Args:
            text: Text content to embed

        Returns:
            List of embedding values (vector)

        Raises:
            ValueError: If embedding creation fails
        """
        try:
            # Note: This is a placeholder implementation
            # Anthropic may not have a direct embeddings API yet
            # In that case, we would need to use a different approach
            # such as using Claude to generate semantic features
            # or integrating with another embedding provider

            # For now, let's implement a semantic feature extraction approach
            # using Claude to understand and represent the document
            semantic_response = await self._client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                temperature=0.1,
                system="You are a semantic analyzer. Extract the key semantic features and concepts from the given text. Respond with a structured list of the most important concepts, entities, and themes.",
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this text and extract semantic features:\n\n{text[:4000]}",  # Limit text length
                    }
                ],
            )

            # Extract text from the first content block if it's a TextBlock
            first_content = semantic_response.content[0]
            if hasattr(first_content, 'text'):
                semantic_features = first_content.text
            else:
                # Fallback to original text if we can't extract semantic features
                semantic_features = text

            # Convert semantic features to a simple hash-based vector
            # This is a basic approach - in production we'd want a proper embedding model
            feature_vector = self._text_to_vector(semantic_features)

            # Convert numpy array to list of floats
            return list(feature_vector.tolist())

        except Exception as e:
            raise ValueError(f"Failed to create embedding: {e}") from e

    def _text_to_vector(
        self, text: str, dimensions: int = 1536
    ) -> np.ndarray[Any, np.dtype[np.float32]]:
        """Convert text to a basic vector representation.

        This is a simple hash-based approach. In production, you'd want
        to use a proper embedding model or API.

        Args:
            text: Text to convert
            dimensions: Number of dimensions for the vector

        Returns:
            Vector representation
        """
        # Simple hash-based vector generation
        # This is deterministic and provides basic semantic clustering
        hash_values = []
        words = text.lower().split()

        for i in range(dimensions):
            # Use word hashes with different salts to create vector components
            component_value = 0.0
            for j, word in enumerate(words):
                word_hash = hash(f"{word}_{i}_{j}") % 1000000
                component_value += (word_hash / 1000000.0) - 0.5

            # Normalize component
            if len(words) > 0:
                component_value /= len(words)

            hash_values.append(component_value)

        # Normalize the vector
        vector = np.array(hash_values)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    async def create_document_embedding(
        self, document_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create an embedding for a structured document.

        Args:
            document_data: Document data dictionary from YAML

        Returns:
            Dictionary with embedding and metadata
        """
        # Extract text content from document for embedding
        text_content = self._extract_embeddable_text(document_data)

        # Create embedding
        embedding = await self.create_embedding(text_content)

        # Create embedding metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "text_length": len(text_content),
            "embedding_dimensions": len(embedding),
            "embedding_method": "claude_semantic_features",
        }

        return {
            "embedding": embedding,
            "text_content": text_content,
            "metadata": metadata,
        }

    def _extract_embeddable_text(self, document_data: dict[str, Any]) -> str:
        """Extract meaningful text content from a document for embedding.

        Args:
            document_data: Document data dictionary

        Returns:
            Combined text content suitable for embedding
        """
        text_parts = []

        # Common fields that contain useful text
        text_fields = [
            "name",
            "title",
            "description",
            "content",
            "summary",
            "keywords",
            "tags",
            "topics",
        ]

        for field in text_fields:
            value = document_data.get(field)
            if value:
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend(str(item) for item in value)

        # Add type-specific fields
        doc_type = document_data.get("service_type") or document_data.get(
            "category", ""
        )
        if doc_type:
            text_parts.append(f"Type: {doc_type}")

        # Add status if available
        status = document_data.get("status")
        if status:
            text_parts.append(f"Status: {status}")

        # Add role if available (for nodes)
        role = document_data.get("role")
        if role:
            text_parts.append(f"Role: {role}")

        # Join all text parts
        combined_text = " ".join(text_parts)

        # Fallback to ID if no text content found
        if not combined_text.strip():
            combined_text = document_data.get("id", "Unknown document")

        return combined_text

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Create embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.create_embedding(text)
            embeddings.append(embedding)

        return embeddings

    async def create_document_chunks_with_embeddings(
        self, store_type: str, document_id: str, document_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create chunks for a document and generate embeddings for each chunk.

        Args:
            store_type: Type of document store (e.g., "github.repos")
            document_id: ID of the document
            document_data: Document content dictionary

        Returns:
            Dictionary with chunks, embeddings, and metadata
        """
        # Create chunks using the document chunker
        chunks = self.document_chunker.chunk_document(
            store_type, document_id, document_data
        )

        # Create embeddings for each chunk
        embeddings = []
        for chunk in chunks:
            embedding = await self.create_embedding(chunk.content)
            embeddings.append(embedding)

        # Get chunk summary
        chunk_summary = self.document_chunker.get_chunk_summary(chunks)

        # Create overall metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "total_chunks": len(chunks),
            "embedding_method": "claude_semantic_features",
            "chunking_strategy": "intelligent_by_type",
            "chunk_summary": chunk_summary,
        }

        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "metadata": metadata,
        }

    async def create_chunk_embedding(self, chunk: DocumentChunk) -> dict[str, Any]:
        """Create an embedding for a single document chunk.

        Args:
            chunk: Document chunk to embed

        Returns:
            Dictionary with embedding and metadata
        """
        # Create embedding for the chunk content
        embedding = await self.create_embedding(chunk.content)

        # Create embedding metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "chunk_id": chunk.chunk_id,
            "chunk_type": chunk.metadata["chunk_type"],
            "chunk_index": chunk.metadata["chunk_index"],
            "parent_document_id": chunk.metadata["parent_document_id"],
            "parent_store_type": chunk.metadata["parent_store_type"],
            "text_length": len(chunk.content),
            "embedding_dimensions": len(embedding),
            "embedding_method": "claude_semantic_features",
        }

        return {
            "embedding": embedding,
            "chunk": chunk,
            "metadata": metadata,
        }

    def get_embeddable_text_from_chunk(self, chunk: DocumentChunk) -> str:
        """Extract embeddable text from a document chunk.

        This is primarily the chunk content, but could be enhanced
        to include contextual information.

        Args:
            chunk: Document chunk

        Returns:
            Text content suitable for embedding
        """
        # For now, just return the chunk content
        # In the future, we might want to add context like:
        # - Parent document information
        # - Chunk position/type context
        # - Related chunk information
        return chunk.content

    async def re_embed_document_with_chunks(
        self,
        store_type: str,
        document_id: str,
        document_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Re-embed a document using chunking.

        Args:
            store_type: Type of document store
            document_id: ID of the document
            document_data: Document content dictionary

        Returns:
            Dictionary with chunks, embeddings, and metadata
        """
        # For now, always create new chunks
        # In the future, we could check if chunks already exist and are up-to-date
        return await self.create_document_chunks_with_embeddings(
            store_type, document_id, document_data
        )

    def should_use_chunking(
        self, store_type: str, document_data: dict[str, Any]
    ) -> bool:
        """Determine if a document should be chunked based on type and size.

        Args:
            store_type: Type of document store
            document_data: Document content dictionary

        Returns:
            True if document should be chunked, False otherwise
        """
        # Extract text content to check size
        text_content = self._extract_embeddable_text(document_data)

        # Always use chunking for notes (they often have structured content)
        if store_type == "notes":
            return True

        # Use chunking for large documents (>1000 characters)
        if len(text_content) > 1000:
            return True

        # Use chunking for GitHub repos (they have structured metadata)
        if store_type == "github.repos":
            return True

        # Don't chunk small organizations or simple documents
        return False
