"""
Embedding cache to further minimize token expenditure.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel, Field


class CachedEmbedding(BaseModel):
    """Cached embedding with metadata."""

    content_hash: str = Field(..., description="Hash of the content")
    embedding: list[float] = Field(..., description="Embedding vector")
    model_name: str = Field(..., description="Model used for embedding")
    created_at: str = Field(..., description="Creation timestamp")
    hit_count: int = Field(default=0, description="Number of cache hits")
    last_accessed: str = Field(..., description="Last access timestamp")


class EmbeddingCache:
    """
    Local cache for embeddings to minimize token costs.

    Cache strategy:
    1. Use content hash as cache key
    2. Store embeddings in SQLite for persistence
    3. Include model name in cache key for model changes
    4. Track usage statistics for cache optimization
    5. Automatic cleanup of rarely used embeddings
    """

    def __init__(self, cache_file: Path, max_cache_size: int = 10000) -> None:
        self.cache_file = cache_file
        self.max_cache_size = max_cache_size
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite cache database."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.cache_file) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS embeddings (
                    content_hash TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed TEXT NOT NULL,
                    PRIMARY KEY (content_hash, model_name)
                )
            """
            )

            # Index for efficient lookups
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_last_accessed
                ON embeddings(last_accessed)
            """
            )

            conn.commit()

    def get_embedding(self, content_hash: str, model_name: str) -> list[float] | None:
        """Get cached embedding if available."""
        from datetime import datetime

        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.cursor()

            # Look up embedding
            cursor.execute(
                """
                SELECT embedding FROM embeddings
                WHERE content_hash = ? AND model_name = ?
            """,
                (content_hash, model_name),
            )

            result = cursor.fetchone()
            if result:
                # Update access statistics
                now = datetime.now().isoformat()
                cursor.execute(
                    """
                    UPDATE embeddings
                    SET hit_count = hit_count + 1, last_accessed = ?
                    WHERE content_hash = ? AND model_name = ?
                """,
                    (now, content_hash, model_name),
                )

                conn.commit()

                # Deserialize embedding
                embedding_bytes = result[0]
                embedding_array = np.frombuffer(embedding_bytes, dtype=np.float32)
                return list(embedding_array.tolist())

        return None

    def store_embedding(
        self, content_hash: str, model_name: str, embedding: list[float]
    ) -> None:
        """Store embedding in cache."""
        from datetime import datetime

        # Convert to numpy array for efficient storage
        embedding_array = np.array(embedding, dtype=np.float32)
        embedding_bytes = embedding_array.tobytes()

        now = datetime.now().isoformat()

        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.cursor()

            # Store embedding (replace if exists)
            cursor.execute(
                """
                INSERT OR REPLACE INTO embeddings
                (content_hash, model_name, embedding, created_at, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, 0, ?)
            """,
                (content_hash, model_name, embedding_bytes, now, now),
            )

            conn.commit()

        # Cleanup if cache is too large
        self._cleanup_cache()

    def _cleanup_cache(self) -> None:
        """Remove least recently used embeddings if cache is too large."""
        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.cursor()

            # Check cache size
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            cache_size = cursor.fetchone()[0]

            if cache_size > self.max_cache_size:
                # Remove oldest embeddings beyond the limit
                items_to_remove = cache_size - self.max_cache_size

                cursor.execute(
                    """
                    DELETE FROM embeddings
                    WHERE (content_hash, model_name) IN (
                        SELECT content_hash, model_name FROM embeddings
                        ORDER BY last_accessed ASC
                        LIMIT ?
                    )
                """,
                    (items_to_remove,),
                )

                conn.commit()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.cursor()

            # Total entries
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            total_entries = cursor.fetchone()[0]

            # Total hits
            cursor.execute("SELECT SUM(hit_count) FROM embeddings")
            total_hits = cursor.fetchone()[0] or 0

            # Model distribution
            cursor.execute(
                """
                SELECT model_name, COUNT(*) FROM embeddings
                GROUP BY model_name
            """
            )
            model_distribution = dict(cursor.fetchall())

            # Cache file size
            cache_size_mb = (
                self.cache_file.stat().st_size / 1024 / 1024
                if self.cache_file.exists()
                else 0
            )

            return {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "hit_rate": total_hits / max(total_entries, 1),
                "model_distribution": model_distribution,
                "cache_size_mb": round(cache_size_mb, 2),
                "max_cache_size": self.max_cache_size,
            }

    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("DELETE FROM embeddings")
            conn.commit()

    def remove_model_cache(self, model_name: str) -> int:
        """Remove all embeddings for a specific model."""
        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embeddings WHERE model_name = ?", (model_name,))
            removed_count = cursor.rowcount
            conn.commit()
            return removed_count


class CachedEmbeddingService:
    """
    Wrapper for embedding service that adds caching.

    Mechanical caching strategy:
    1. Generate content hash for input text
    2. Check cache for existing embedding
    3. If found, return cached embedding (saves API call)
    4. If not found, call actual embedding service
    5. Store result in cache for future use
    """

    def __init__(
        self,
        embedding_service: Any,  # The actual embedding service
        cache_file: Path,
        max_cache_size: int = 10000,
    ) -> None:
        self.embedding_service = embedding_service
        self.cache = EmbeddingCache(cache_file, max_cache_size)

    async def embed_text(self, text: str, model_name: str = "default") -> list[float]:
        """Get embedding for text with caching."""
        import hashlib

        # Generate content hash
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        # Check cache first
        cached_embedding = self.cache.get_embedding(content_hash, model_name)
        if cached_embedding is not None:
            return cached_embedding

        # Cache miss - call actual embedding service
        embedding = await self._call_embedding_service(text, model_name)

        # Store in cache
        self.cache.store_embedding(content_hash, model_name, embedding)

        return embedding

    async def _call_embedding_service(self, text: str, model_name: str) -> list[float]:
        """Call the actual embedding service."""
        # This would be customized based on the actual embedding service interface
        if hasattr(self.embedding_service, "embed_text"):
            result = await self.embedding_service.embed_text(text)
            return list(result)
        elif hasattr(self.embedding_service, "get_embedding"):
            result = await self.embedding_service.get_embedding(text)
            return list(result)
        elif hasattr(self.embedding_service, "embed"):
            result = await self.embedding_service.embed(text)
            return list(result)
        else:
            # Fallback for OpenAI-style interface
            response = await self.embedding_service.create_embedding(text)
            return list(response.data[0].embedding)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_cache_stats()

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self.cache.clear_cache()

    def estimate_cost_savings(self) -> dict[str, Any]:
        """Estimate cost savings from caching."""
        stats = self.cache.get_cache_stats()

        # Rough cost estimates (adjust based on actual pricing)
        cost_per_token = 0.0001  # Example: $0.0001 per token
        avg_tokens_per_embedding = 100  # Average tokens per document

        total_hits = stats["total_hits"]
        cost_savings = total_hits * avg_tokens_per_embedding * cost_per_token

        return {
            "cache_hits": total_hits,
            "estimated_tokens_saved": total_hits * avg_tokens_per_embedding,
            "estimated_cost_savings_usd": round(cost_savings, 4),
            "hit_rate_percent": round(stats["hit_rate"] * 100, 2),
        }
