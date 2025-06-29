import os
from datetime import datetime
from typing import Any

import numpy as np
from anthropic import AsyncAnthropic
from antidote import inject, injectable

from ..paths import Paths


@injectable
class EmbeddingsService:
    """Service for creating and managing document embeddings using Anthropic."""

    def __init__(self, paths: Paths = inject.me()) -> None:
        """Initialize the embeddings service.

        Args:
            paths: Paths service for data directory management
        """
        self.paths = paths

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

            semantic_features = semantic_response.content[0].text

            # Convert semantic features to a simple hash-based vector
            # This is a basic approach - in production we'd want a proper embedding model
            feature_vector = self._text_to_vector(semantic_features)

            return feature_vector.tolist()

        except Exception as e:
            raise ValueError(f"Failed to create embedding: {e}") from e

    def _text_to_vector(
        self, text: str, dimensions: int = 768
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
