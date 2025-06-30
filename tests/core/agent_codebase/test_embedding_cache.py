"""
Tests for embedding cache functionality.
"""

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock

import numpy as np
import pytest

from goldentooth_agent.core.agent_codebase.embedding_cache import (
    CachedEmbedding,
    CachedEmbeddingService,
    EmbeddingCache,
)


@pytest.fixture
def temp_cache_file() -> Generator[Path]:
    """Temporary cache file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir) / "test_cache.db"


@pytest.fixture
def embedding_cache(temp_cache_file: Path) -> EmbeddingCache:
    """Embedding cache instance for testing."""
    return EmbeddingCache(temp_cache_file, max_cache_size=5)


@pytest.fixture
def sample_embedding() -> list[float]:
    """Sample embedding vector."""
    return [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional vector


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for testing."""
    service = AsyncMock()
    service.embed_text = AsyncMock(return_value=[0.1, 0.2, 0.3])
    return service


class TestCachedEmbedding:
    """Test CachedEmbedding model."""

    def test_cached_embedding_creation(self, sample_embedding: list[float]):
        """Test creating a cached embedding."""
        cached = CachedEmbedding(
            content_hash="abc123",
            embedding=sample_embedding,
            model_name="test-model",
            created_at="2023-01-01T00:00:00",
            last_accessed="2023-01-01T00:00:00",
        )

        assert cached.content_hash == "abc123"
        assert cached.embedding == sample_embedding
        assert cached.model_name == "test-model"
        assert cached.hit_count == 0  # Default value

    def test_cached_embedding_with_hit_count(self, sample_embedding: list[float]):
        """Test cached embedding with custom hit count."""
        cached = CachedEmbedding(
            content_hash="abc123",
            embedding=sample_embedding,
            model_name="test-model",
            created_at="2023-01-01T00:00:00",
            hit_count=5,
            last_accessed="2023-01-01T00:00:00",
        )

        assert cached.hit_count == 5


class TestEmbeddingCache:
    """Test EmbeddingCache functionality."""

    def test_cache_initialization(self, temp_cache_file: Path):
        """Test cache initialization creates database."""
        cache = EmbeddingCache(temp_cache_file, max_cache_size=100)

        assert cache.cache_file == temp_cache_file
        assert cache.max_cache_size == 100
        assert temp_cache_file.exists()

    def test_store_and_retrieve_embedding(
        self, embedding_cache: EmbeddingCache, sample_embedding: list[float]
    ):
        """Test storing and retrieving an embedding."""
        content_hash = "test_hash_123"
        model_name = "test-model"

        # Store embedding
        embedding_cache.store_embedding(content_hash, model_name, sample_embedding)

        # Retrieved embedding should match
        retrieved = embedding_cache.get_embedding(content_hash, model_name)
        assert retrieved is not None

        # Compare with tolerance for float precision
        np.testing.assert_array_almost_equal(retrieved, sample_embedding, decimal=5)

    def test_cache_miss(self, embedding_cache: EmbeddingCache):
        """Test cache miss returns None."""
        result = embedding_cache.get_embedding("nonexistent", "test-model")
        assert result is None

    def test_cache_hit_updates_statistics(
        self, embedding_cache: EmbeddingCache, sample_embedding: list[float]
    ):
        """Test that cache hits update access statistics."""
        content_hash = "test_hash_123"
        model_name = "test-model"

        # Store embedding
        embedding_cache.store_embedding(content_hash, model_name, sample_embedding)

        # First hit
        embedding_cache.get_embedding(content_hash, model_name)

        # Second hit
        embedding_cache.get_embedding(content_hash, model_name)

        # Check stats
        stats = embedding_cache.get_cache_stats()
        assert stats["total_hits"] == 2
        assert stats["total_entries"] == 1

    def test_cache_cleanup_when_oversized(
        self, temp_cache_file: Path, sample_embedding: list[float]
    ):
        """Test cache cleanup when max size is exceeded."""
        # Create cache with small max size
        cache = EmbeddingCache(temp_cache_file, max_cache_size=2)

        # Add more embeddings than max size
        for i in range(4):
            cache.store_embedding(f"hash_{i}", "model", sample_embedding)

        # Should only have max_cache_size entries
        stats = cache.get_cache_stats()
        assert stats["total_entries"] == 2

    def test_get_cache_stats(
        self, embedding_cache: EmbeddingCache, sample_embedding: list[float]
    ):
        """Test cache statistics."""
        # Add some embeddings
        embedding_cache.store_embedding("hash1", "model1", sample_embedding)
        embedding_cache.store_embedding("hash2", "model1", sample_embedding)
        embedding_cache.store_embedding("hash3", "model2", sample_embedding)

        # Generate some hits
        embedding_cache.get_embedding("hash1", "model1")
        embedding_cache.get_embedding("hash2", "model1")
        embedding_cache.get_embedding("hash1", "model1")  # Another hit on hash1

        stats = embedding_cache.get_cache_stats()

        assert stats["total_entries"] == 3
        assert stats["total_hits"] == 3
        assert stats["hit_rate"] == 1.0  # 3 hits / 3 entries
        assert stats["model_distribution"] == {"model1": 2, "model2": 1}
        assert stats["max_cache_size"] == 5
        assert "cache_size_mb" in stats

    def test_clear_cache(
        self, embedding_cache: EmbeddingCache, sample_embedding: list[float]
    ):
        """Test clearing all cached embeddings."""
        # Add some embeddings
        embedding_cache.store_embedding("hash1", "model1", sample_embedding)
        embedding_cache.store_embedding("hash2", "model2", sample_embedding)

        # Verify they exist
        assert embedding_cache.get_cache_stats()["total_entries"] == 2

        # Clear cache
        embedding_cache.clear_cache()

        # Verify cache is empty
        assert embedding_cache.get_cache_stats()["total_entries"] == 0
        assert embedding_cache.get_embedding("hash1", "model1") is None

    def test_remove_model_cache(
        self, embedding_cache: EmbeddingCache, sample_embedding: list[float]
    ):
        """Test removing embeddings for specific model."""
        # Add embeddings for different models
        embedding_cache.store_embedding("hash1", "model1", sample_embedding)
        embedding_cache.store_embedding("hash2", "model1", sample_embedding)
        embedding_cache.store_embedding("hash3", "model2", sample_embedding)

        # Remove model1 embeddings
        removed_count = embedding_cache.remove_model_cache("model1")

        assert removed_count == 2
        assert embedding_cache.get_embedding("hash1", "model1") is None
        assert embedding_cache.get_embedding("hash2", "model1") is None
        assert embedding_cache.get_embedding("hash3", "model2") is not None

    def test_replace_existing_embedding(self, embedding_cache: EmbeddingCache):
        """Test that storing an embedding with same hash/model replaces existing."""
        content_hash = "test_hash"
        model_name = "test-model"

        # Store first embedding
        first_embedding = [1.0, 2.0, 3.0]
        embedding_cache.store_embedding(content_hash, model_name, first_embedding)

        # Store second embedding with same hash/model
        second_embedding = [4.0, 5.0, 6.0]
        embedding_cache.store_embedding(content_hash, model_name, second_embedding)

        # Should get the second embedding
        retrieved = embedding_cache.get_embedding(content_hash, model_name)
        np.testing.assert_array_almost_equal(retrieved, second_embedding, decimal=5)

        # Should still have only one entry
        stats = embedding_cache.get_cache_stats()
        assert stats["total_entries"] == 1


class TestCachedEmbeddingService:
    """Test CachedEmbeddingService functionality."""

    def test_service_initialization(
        self, mock_embedding_service, temp_cache_file: Path
    ):
        """Test service initialization."""
        service = CachedEmbeddingService(
            embedding_service=mock_embedding_service,
            cache_file=temp_cache_file,
            max_cache_size=100,
        )

        assert service.embedding_service == mock_embedding_service
        assert service.cache.cache_file == temp_cache_file
        assert service.cache.max_cache_size == 100

    @pytest.mark.asyncio
    async def test_embed_text_cache_miss(
        self, mock_embedding_service, temp_cache_file: Path
    ):
        """Test embedding text with cache miss."""
        service = CachedEmbeddingService(
            embedding_service=mock_embedding_service, cache_file=temp_cache_file
        )

        text = "Hello world"
        model_name = "test-model"
        expected_embedding = [0.1, 0.2, 0.3]
        mock_embedding_service.embed_text.return_value = expected_embedding

        result = await service.embed_text(text, model_name)

        assert result == expected_embedding
        mock_embedding_service.embed_text.assert_called_once_with(text)

        # Should be cached now
        import hashlib

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cached = service.cache.get_embedding(content_hash, model_name)
        np.testing.assert_array_almost_equal(cached, expected_embedding, decimal=5)

    @pytest.mark.asyncio
    async def test_embed_text_cache_hit(
        self, mock_embedding_service, temp_cache_file: Path
    ):
        """Test embedding text with cache hit."""
        service = CachedEmbeddingService(
            embedding_service=mock_embedding_service, cache_file=temp_cache_file
        )

        text = "Hello world"
        model_name = "test-model"
        expected_embedding = [0.1, 0.2, 0.3]

        # Pre-populate cache
        import hashlib

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        service.cache.store_embedding(content_hash, model_name, expected_embedding)

        result = await service.embed_text(text, model_name)

        np.testing.assert_array_almost_equal(result, expected_embedding, decimal=5)
        # Should not have called the actual service
        mock_embedding_service.embed_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_different_embedding_service_interfaces(self, temp_cache_file: Path):
        """Test different embedding service interface patterns."""
        # Test get_embedding interface
        service1 = Mock()
        service1.get_embedding = AsyncMock(return_value=[1.0, 2.0])
        # Remove other interface methods to force fallback to get_embedding
        if hasattr(service1, "embed_text"):
            delattr(service1, "embed_text")

        cached_service1 = CachedEmbeddingService(service1, temp_cache_file)
        result1 = await cached_service1.embed_text("test", "model")
        assert result1 == [1.0, 2.0]
        service1.get_embedding.assert_called_once_with("test")

        # Test embed interface
        service2 = Mock()
        service2.embed = AsyncMock(return_value=[3.0, 4.0])
        # Remove other interface methods to force fallback to embed
        if hasattr(service2, "embed_text"):
            delattr(service2, "embed_text")
        if hasattr(service2, "get_embedding"):
            delattr(service2, "get_embedding")

        cached_service2 = CachedEmbeddingService(service2, temp_cache_file)
        result2 = await cached_service2.embed_text("test2", "model")
        assert result2 == [3.0, 4.0]
        service2.embed.assert_called_once_with("test2")

    @pytest.mark.asyncio
    async def test_openai_style_embedding_service(self, temp_cache_file: Path):
        """Test OpenAI-style embedding service interface."""
        # Mock OpenAI-style response
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = [0.5, 0.6, 0.7]

        service = AsyncMock()
        service.create_embedding = AsyncMock(return_value=mock_response)
        # Remove other interface methods
        if hasattr(service, "embed_text"):
            delattr(service, "embed_text")
        if hasattr(service, "get_embedding"):
            delattr(service, "get_embedding")
        if hasattr(service, "embed"):
            delattr(service, "embed")

        cached_service = CachedEmbeddingService(service, temp_cache_file)
        result = await cached_service.embed_text("test", "model")

        assert result == [0.5, 0.6, 0.7]
        service.create_embedding.assert_called_once_with("test")

    def test_get_cache_stats(self, mock_embedding_service, temp_cache_file: Path):
        """Test getting cache statistics."""
        service = CachedEmbeddingService(
            embedding_service=mock_embedding_service, cache_file=temp_cache_file
        )

        stats = service.get_cache_stats()

        assert "total_entries" in stats
        assert "total_hits" in stats
        assert "hit_rate" in stats

    def test_clear_cache(self, mock_embedding_service, temp_cache_file: Path):
        """Test clearing the cache."""
        service = CachedEmbeddingService(
            embedding_service=mock_embedding_service, cache_file=temp_cache_file
        )

        # Add some data to cache first
        service.cache.store_embedding("hash", "model", [1.0, 2.0])
        assert service.get_cache_stats()["total_entries"] == 1

        # Clear cache
        service.clear_cache()

        assert service.get_cache_stats()["total_entries"] == 0

    def test_estimate_cost_savings(self, mock_embedding_service, temp_cache_file: Path):
        """Test cost savings estimation."""
        service = CachedEmbeddingService(
            embedding_service=mock_embedding_service, cache_file=temp_cache_file
        )

        # Add some cache hits
        service.cache.store_embedding("hash1", "model", [1.0, 2.0])
        service.cache.store_embedding("hash2", "model", [3.0, 4.0])

        # Simulate cache hits
        service.cache.get_embedding("hash1", "model")
        service.cache.get_embedding("hash2", "model")
        service.cache.get_embedding("hash1", "model")  # Another hit

        savings = service.estimate_cost_savings()

        assert savings["cache_hits"] == 3
        assert savings["estimated_tokens_saved"] == 300  # 3 hits * 100 tokens
        assert savings["estimated_cost_savings_usd"] == 0.03  # 300 * 0.0001
        assert "hit_rate_percent" in savings
