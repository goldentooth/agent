"""Tests for embeddings data models."""

import pytest

from goldentooth_agent.core.embeddings.models import Chunk, SearchResult


class TestChunk:
    """Test the Chunk data model."""

    def test_chunk_creation(self):
        """Test creating a Chunk with all fields."""
        metadata = {"source": "test.py", "author": "dev"}
        chunk = Chunk(
            chunk_id="chunk_001",
            document_id="doc_001",
            content="This is test content",
            position=0,
            metadata=metadata,
            chunk_type="code",
        )

        assert chunk.chunk_id == "chunk_001"
        assert chunk.document_id == "doc_001"
        assert chunk.content == "This is test content"
        assert chunk.position == 0
        assert chunk.metadata == metadata
        assert chunk.chunk_type == "code"

    def test_chunk_str_representation(self):
        """Test string representation of Chunk."""
        chunk = Chunk(
            chunk_id="chunk_001",
            document_id="doc_001",
            content="This is test content",
            position=5,
            metadata={},
            chunk_type="text",
        )

        str_repr = str(chunk)
        assert "Chunk(chunk_001, pos=5, type=text)" == str_repr

    def test_chunk_repr_representation(self):
        """Test detailed representation of Chunk."""
        chunk = Chunk(
            chunk_id="chunk_001",
            document_id="doc_001",
            content="This is test content",
            position=5,
            metadata={},
            chunk_type="text",
        )

        repr_str = repr(chunk)
        expected = (
            "Chunk(chunk_id='chunk_001', document_id='doc_001', "
            "position=5, chunk_type='text', content_length=20)"
        )
        assert repr_str == expected

    def test_chunk_empty_content(self):
        """Test Chunk with empty content."""
        chunk = Chunk(
            chunk_id="empty_chunk",
            document_id="doc_001",
            content="",
            position=0,
            metadata={},
            chunk_type="empty",
        )

        assert chunk.content == ""
        assert len(chunk.content) == 0
        repr_str = repr(chunk)
        assert "content_length=0" in repr_str

    def test_chunk_large_content(self):
        """Test Chunk with large content."""
        large_content = "x" * 10000  # 10k characters
        chunk = Chunk(
            chunk_id="large_chunk",
            document_id="doc_001",
            content=large_content,
            position=0,
            metadata={},
            chunk_type="large",
        )

        assert len(chunk.content) == 10000
        repr_str = repr(chunk)
        assert "content_length=10000" in repr_str

    def test_chunk_complex_metadata(self):
        """Test Chunk with complex metadata."""
        metadata = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "number": 42,
            "boolean": True,
            "null": None,
        }
        chunk = Chunk(
            chunk_id="complex_chunk",
            document_id="doc_001",
            content="Complex metadata test",
            position=0,
            metadata=metadata,
            chunk_type="complex",
        )

        assert chunk.metadata == metadata
        assert chunk.metadata["nested"]["key"] == "value"
        assert chunk.metadata["list"] == [1, 2, 3]


class TestSearchResult:
    """Test the SearchResult data model."""

    def create_test_chunk(self) -> Chunk:
        """Create a test chunk for SearchResult tests."""
        return Chunk(
            chunk_id="test_chunk",
            document_id="test_doc",
            content="Test content",
            position=0,
            metadata={"type": "test"},
            chunk_type="test",
        )

    def test_search_result_creation_minimal(self):
        """Test creating SearchResult with minimal fields."""
        chunk = self.create_test_chunk()
        result = SearchResult(chunk=chunk, relevance_score=0.85)

        assert result.chunk == chunk
        assert result.relevance_score == 0.85
        assert result.metadata is None

    def test_search_result_creation_with_metadata(self):
        """Test creating SearchResult with metadata."""
        chunk = self.create_test_chunk()
        metadata = {"search_type": "semantic", "algorithm": "cosine"}
        result = SearchResult(chunk=chunk, relevance_score=0.92, metadata=metadata)

        assert result.chunk == chunk
        assert result.relevance_score == 0.92
        assert result.metadata == metadata

    def test_search_result_str_representation(self):
        """Test string representation of SearchResult."""
        chunk = self.create_test_chunk()
        result = SearchResult(chunk=chunk, relevance_score=0.876543)

        str_repr = str(result)
        assert str_repr == "SearchResult(chunk=test_chunk, score=0.877)"

    def test_search_result_repr_representation(self):
        """Test detailed representation of SearchResult."""
        chunk = self.create_test_chunk()
        metadata = {"test": True}
        result = SearchResult(chunk=chunk, relevance_score=0.85, metadata=metadata)

        repr_str = repr(result)
        # Should contain chunk repr, score, and metadata
        assert "SearchResult(chunk=" in repr_str
        assert "relevance_score=0.85" in repr_str
        assert "metadata={'test': True}" in repr_str

    def test_search_result_convenience_properties(self):
        """Test convenience properties for accessing chunk data."""
        chunk = Chunk(
            chunk_id="convenience_chunk",
            document_id="convenience_doc",
            content="Convenience test content",
            position=42,
            metadata={"convenience": True},
            chunk_type="convenience",
        )
        result = SearchResult(chunk=chunk, relevance_score=0.95)

        # Test convenience properties
        assert result.chunk_id == "convenience_chunk"
        assert result.document_id == "convenience_doc"
        assert result.content == "Convenience test content"

        # Verify these match the chunk properties
        assert result.chunk_id == chunk.chunk_id
        assert result.document_id == chunk.document_id
        assert result.content == chunk.content

    def test_search_result_zero_relevance_score(self):
        """Test SearchResult with zero relevance score."""
        chunk = self.create_test_chunk()
        result = SearchResult(chunk=chunk, relevance_score=0.0)

        assert result.relevance_score == 0.0
        str_repr = str(result)
        assert "score=0.000" in str_repr

    def test_search_result_perfect_relevance_score(self):
        """Test SearchResult with perfect relevance score."""
        chunk = self.create_test_chunk()
        result = SearchResult(chunk=chunk, relevance_score=1.0)

        assert result.relevance_score == 1.0
        str_repr = str(result)
        assert "score=1.000" in str_repr

    def test_search_result_negative_relevance_score(self):
        """Test SearchResult with negative relevance score."""
        chunk = self.create_test_chunk()
        result = SearchResult(chunk=chunk, relevance_score=-0.25)

        assert result.relevance_score == -0.25
        str_repr = str(result)
        assert "score=-0.250" in str_repr

    def test_search_result_equality(self):
        """Test SearchResult equality (via dataclass)."""
        chunk1 = Chunk("id1", "doc1", "content1", 0, {}, "type1")
        chunk2 = Chunk("id1", "doc1", "content1", 0, {}, "type1")  # Same as chunk1
        chunk3 = Chunk("id2", "doc1", "content1", 0, {}, "type1")  # Different ID

        result1 = SearchResult(chunk1, 0.8)
        result2 = SearchResult(chunk2, 0.8)  # Same chunk, same score
        result3 = SearchResult(chunk1, 0.9)  # Same chunk, different score
        result4 = SearchResult(chunk3, 0.8)  # Different chunk, same score

        assert result1 == result2  # Same chunk and score
        assert result1 != result3  # Different score
        assert result1 != result4  # Different chunk

    def test_search_result_with_empty_metadata(self):
        """Test SearchResult with empty metadata dict."""
        chunk = self.create_test_chunk()
        result = SearchResult(chunk=chunk, relevance_score=0.75, metadata={})

        assert result.metadata == {}
        repr_str = repr(result)
        assert "metadata={}" in repr_str
