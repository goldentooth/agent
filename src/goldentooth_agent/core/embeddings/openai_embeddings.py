"""OpenAI embeddings service for high-quality vector representations."""

import os
from datetime import datetime
from typing import Any

from antidote import inject, injectable
from openai import AsyncOpenAI

from ..paths import Paths
from .document_chunker import DocumentChunk, DocumentChunker


@injectable
class OpenAIEmbeddingsService:
    """Service for creating and managing document embeddings using OpenAI."""

    def __init__(
        self,
        paths: Paths = inject.me(),
        document_chunker: DocumentChunker = inject.me(),
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
    ) -> None:
        """Initialize the OpenAI embeddings service.

        Args:
            paths: Paths service for data directory management
            document_chunker: Service for chunking documents
            model: OpenAI embedding model to use
            dimensions: Number of dimensions for embeddings
        """
        self.paths = paths
        self.document_chunker = document_chunker
        self.model = model
        self.dimensions = dimensions

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
            )

        self._client = AsyncOpenAI(api_key=api_key)

    async def create_embedding(self, text: str) -> list[float]:
        """Create an embedding for the given text using OpenAI.

        Args:
            text: Text content to embed

        Returns:
            List of embedding values (vector)

        Raises:
            ValueError: If embedding creation fails
        """
        try:
            # Clean and truncate text if needed
            cleaned_text = self._clean_text_for_embedding(text)

            # Create embedding using OpenAI API
            response = await self._client.embeddings.create(
                model=self.model,
                input=cleaned_text,
                dimensions=self.dimensions,
            )

            # Extract embedding vector
            embedding = response.data[0].embedding

            return embedding

        except Exception as e:
            raise ValueError(f"Failed to create OpenAI embedding: {e}") from e

    def _clean_text_for_embedding(self, text: str) -> str:
        """Clean and prepare text for embedding.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text suitable for embedding
        """
        # Remove excessive whitespace
        cleaned = " ".join(text.split())

        # Truncate if too long (OpenAI has token limits)
        # text-embedding-3-small has ~8k token limit, roughly 6k characters
        max_chars = 6000
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars] + "..."

        return cleaned

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
            "embedding_method": "openai",
            "model": self.model,
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

    async def embed_batch(
        self, texts: list[str], batch_size: int = 100
    ) -> list[list[float]]:
        """Create embeddings for a batch of texts efficiently.

        Args:
            texts: List of text strings to embed
            batch_size: Maximum number of texts to embed in one API call

        Returns:
            List of embedding vectors
        """
        embeddings = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            # Clean texts
            cleaned_batch = [self._clean_text_for_embedding(text) for text in batch]

            try:
                # Create embeddings for batch
                response = await self._client.embeddings.create(
                    model=self.model,
                    input=cleaned_batch,
                    dimensions=self.dimensions,
                )

                # Extract embeddings from response
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)

            except Exception:
                # Fall back to individual embedding creation for this batch
                for text in batch:
                    try:
                        embedding = await self.create_embedding(text)
                        embeddings.append(embedding)
                    except Exception:
                        # Create a zero vector as fallback
                        zero_embedding = [0.0] * self.dimensions
                        embeddings.append(zero_embedding)

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

        # Prepare texts for batch embedding
        chunk_texts = [chunk.content for chunk in chunks]

        # Create embeddings for all chunks in batches
        embeddings = await self.embed_batch(chunk_texts)

        # Get chunk summary
        chunk_summary = self.document_chunker.get_chunk_summary(chunks)

        # Create overall metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "total_chunks": len(chunks),
            "embedding_method": "openai",
            "model": self.model,
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
            "embedding_method": "openai",
            "model": self.model,
        }

        return {
            "embedding": embedding,
            "chunk": chunk,
            "metadata": metadata,
        }

    def get_embeddable_text_from_chunk(self, chunk: DocumentChunk) -> str:
        """Extract embeddable text from a document chunk.

        Args:
            chunk: Document chunk

        Returns:
            Text content suitable for embedding
        """
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

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the current embedding model.

        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "dimensions": self.dimensions,
            "provider": "openai",
            "max_tokens": 8192 if "3-small" in self.model else 8192,
            "approximate_max_chars": 6000,
        }
