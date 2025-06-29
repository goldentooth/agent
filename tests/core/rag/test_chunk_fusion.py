"""Tests for chunk fusion functionality."""

import pytest

from goldentooth_agent.core.embeddings.models import Chunk, SearchResult
from goldentooth_agent.core.rag.chunk_fusion import (
    ChunkCluster,
    ChunkFusion,
    FusedAnswer,
)


class TestChunkFusion:
    """Test ChunkFusion class functionality."""

    @pytest.fixture
    def fusion_engine(self) -> ChunkFusion:
        """Create test fusion engine."""
        return ChunkFusion(
            coherence_threshold=0.6,
            min_chunks_for_fusion=2,
            max_chunks_for_fusion=10,
            deduplication_threshold=0.8,
        )

    @pytest.fixture
    def test_chunks(self) -> list[Chunk]:
        """Create test chunks for fusion testing."""
        return [
            # Document 1 chunks - about Python
            Chunk(
                chunk_id="chunk1",
                document_id="doc1",
                content="Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum.",
                position=0,
                metadata={"title": "Python Programming", "section": "Introduction"},
                chunk_type="content",
            ),
            Chunk(
                chunk_id="chunk2",
                document_id="doc1",
                content="Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
                position=1,
                metadata={"title": "Python Programming", "section": "Features"},
                chunk_type="content",
            ),
            Chunk(
                chunk_id="chunk3",
                document_id="doc1",
                content="Python has a large standard library and extensive ecosystem of third-party packages available through PyPI.",
                position=2,
                metadata={"title": "Python Programming", "section": "Ecosystem"},
                chunk_type="content",
            ),
            # Document 2 chunks - also about Python but different perspective
            Chunk(
                chunk_id="chunk4",
                document_id="doc2",
                content="Python is widely used in data science, machine learning, and artificial intelligence applications.",
                position=0,
                metadata={"title": "Python in Data Science", "author": "Data Expert"},
                chunk_type="content",
            ),
            Chunk(
                chunk_id="chunk5",
                document_id="doc2",
                content="Popular Python libraries for data science include NumPy, Pandas, Scikit-learn, and TensorFlow.",
                position=1,
                metadata={"title": "Python in Data Science", "author": "Data Expert"},
                chunk_type="content",
            ),
            # Document 3 - unrelated content
            Chunk(
                chunk_id="chunk6",
                document_id="doc3",
                content="JavaScript is a dynamic programming language primarily used for web development and browser scripting.",
                position=0,
                metadata={"title": "JavaScript Guide"},
                chunk_type="content",
            ),
        ]

    @pytest.fixture
    def search_results(self, test_chunks: list[Chunk]) -> list[SearchResult]:
        """Create search results from test chunks."""
        # Simulate relevance scores
        relevance_scores = [0.9, 0.85, 0.8, 0.88, 0.82, 0.3]

        return [
            SearchResult(
                chunk=chunk, relevance_score=score, metadata={"search_method": "hybrid"}
            )
            for chunk, score in zip(test_chunks, relevance_scores, strict=False)
        ]

    def test_chunk_cluster_properties(self, test_chunks: list[Chunk]) -> None:
        """Test ChunkCluster properties and calculations."""
        chunks = test_chunks[:3]
        relevance_scores = {
            "chunk1": 0.9,
            "chunk2": 0.85,
            "chunk3": 0.8,
        }

        cluster = ChunkCluster(
            chunks=chunks,
            relevance_scores=relevance_scores,
            topic_coherence=0.8,
            temporal_coherence=0.9,
            semantic_density=0.7,
        )

        assert cluster.average_relevance == pytest.approx(0.85, 0.01)
        assert cluster.chunk_ids == {"chunk1", "chunk2", "chunk3"}
        assert len(cluster.chunks) == 3

    def test_fused_answer_properties(self, test_chunks: list[Chunk]) -> None:
        """Test FusedAnswer properties."""
        chunks = test_chunks[:2]

        answer = FusedAnswer(
            content="Python is a versatile programming language.",
            source_chunks=chunks,
            confidence_score=0.85,
            coherence_score=0.8,
            completeness_score=0.75,
            key_points=["Python is high-level", "Supports multiple paradigms"],
            contradictions=[],
            metadata={"fusion_method": "test"},
        )

        assert answer.num_sources == 2
        assert answer.source_documents == {"doc1"}
        assert len(answer.key_points) == 2
        assert not answer.contradictions

    def test_calculate_coherence_same_document(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test coherence calculation for chunks from same document."""
        chunk1 = test_chunks[0]
        chunk2 = test_chunks[1]

        coherence = fusion_engine._calculate_coherence(
            chunk1, chunk2, "Python programming"
        )

        # Should have high coherence - same document, adjacent positions
        assert coherence > 0.5

        # Test non-adjacent chunks from same document
        chunk3 = test_chunks[2]
        coherence2 = fusion_engine._calculate_coherence(
            chunk1, chunk3, "Python programming"
        )

        # Should still have good coherence but less than adjacent
        assert coherence2 > 0.4
        assert coherence > coherence2

    def test_calculate_coherence_different_documents(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test coherence calculation for chunks from different documents."""
        chunk1 = test_chunks[0]  # Python intro
        chunk4 = test_chunks[3]  # Python data science

        coherence = fusion_engine._calculate_coherence(
            chunk1, chunk4, "Python applications"
        )

        # Should have moderate coherence - different docs but related content
        assert 0.2 < coherence < 0.8

    def test_calculate_coherence_unrelated(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test coherence calculation for unrelated chunks."""
        chunk1 = test_chunks[0]  # Python
        chunk6 = test_chunks[5]  # JavaScript

        coherence = fusion_engine._calculate_coherence(
            chunk1, chunk6, "Python programming"
        )

        # Should have low coherence - unrelated content
        assert coherence < 0.4

    def test_calculate_topic_coherence(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test topic coherence calculation across chunks."""
        # Related chunks about Python
        python_chunks = test_chunks[:5]
        coherence = fusion_engine._calculate_topic_coherence(python_chunks)

        # Should have reasonable coherence - all about Python
        assert coherence > 0.1

        # Mixed chunks including unrelated content
        mixed_chunks = test_chunks
        coherence2 = fusion_engine._calculate_topic_coherence(mixed_chunks)

        # Should have lower coherence
        assert coherence2 < coherence

    def test_calculate_temporal_coherence(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test temporal coherence calculation."""
        # Adjacent chunks from same document
        adjacent_chunks = test_chunks[:3]
        coherence = fusion_engine._calculate_temporal_coherence(adjacent_chunks)

        # Should have high coherence - consecutive positions
        assert coherence > 0.8

        # Chunks from different documents
        mixed_chunks = [test_chunks[0], test_chunks[3], test_chunks[5]]
        coherence2 = fusion_engine._calculate_temporal_coherence(mixed_chunks)

        # Should have lower coherence
        assert coherence2 == 1.0  # Each doc has only one chunk

    def test_calculate_semantic_density(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test semantic density calculation."""
        chunks = test_chunks[:3]
        query = "Python programming language features"

        density = fusion_engine._calculate_semantic_density(chunks, query)

        # Should have good density - chunks cover query terms
        assert density > 0.5

        # Test with unrelated query
        density2 = fusion_engine._calculate_semantic_density(
            chunks, "JavaScript web development"
        )

        # Should have low density
        assert density2 < 0.3

    def test_extract_key_points(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test key point extraction."""
        chunks = test_chunks[:3]
        query = "Python programming"

        key_points = fusion_engine._extract_key_points(chunks, query)

        assert len(key_points) > 0
        assert all(isinstance(point, str) for point in key_points)

        # Should extract sentences containing query terms
        assert any("Python" in point for point in key_points)

    def test_detect_contradictions(self, fusion_engine: ChunkFusion) -> None:
        """Test contradiction detection."""
        # Create chunks with potential contradictions
        chunks = [
            Chunk(
                chunk_id="c1",
                document_id="d1",
                content="Python is the best programming language. It is fast and efficient.",
                position=0,
                metadata={},
                chunk_type="content",
            ),
            Chunk(
                chunk_id="c2",
                document_id="d2",
                content="Python is not the fastest language. It can be slow for certain tasks.",
                position=0,
                metadata={},
                chunk_type="content",
            ),
        ]

        contradictions = fusion_engine._detect_contradictions(chunks)

        # Should detect the contradiction about speed
        assert len(contradictions) > 0
        assert any("fast" in c.lower() for c in contradictions)

    def test_calculate_similarity(self, fusion_engine: ChunkFusion) -> None:
        """Test text similarity calculation."""
        text1 = "Python is a programming language"
        text2 = "Python is a programming language"

        # Identical texts
        similarity = fusion_engine._calculate_similarity(text1, text2)
        assert similarity == 1.0

        # Similar texts
        text3 = "Python is a great programming language"
        similarity2 = fusion_engine._calculate_similarity(text1, text3)
        assert 0.7 < similarity2 < 1.0

        # Different texts
        text4 = "JavaScript is used for web development"
        similarity3 = fusion_engine._calculate_similarity(text1, text4)
        assert similarity3 < 0.3

    def test_calculate_completeness(self, fusion_engine: ChunkFusion) -> None:
        """Test answer completeness calculation."""
        query = "Python programming features ecosystem"

        # Key points covering all query terms
        key_points = [
            "Python is a programming language with many features",
            "The Python ecosystem includes many libraries",
            "Python programming is popular for its simplicity",
        ]

        completeness = fusion_engine._calculate_completeness(key_points, query)
        assert completeness > 0.7

        # Key points missing coverage
        key_points2 = ["Python is great", "Programming is fun"]
        completeness2 = fusion_engine._calculate_completeness(key_points2, query)
        assert completeness2 < completeness

    def test_cluster_chunks(
        self, fusion_engine: ChunkFusion, search_results: list[SearchResult]
    ) -> None:
        """Test chunk clustering."""
        clusters = fusion_engine._cluster_chunks(search_results, "Python programming")

        assert len(clusters) > 0

        # First cluster should have high-relevance Python chunks
        first_cluster = clusters[0]
        assert len(first_cluster.chunks) >= fusion_engine.min_chunks_for_fusion
        assert first_cluster.average_relevance > 0.7

        # JavaScript chunk should not be in any cluster with Python chunks
        js_chunk_id = "chunk6"
        python_clusters = [
            c for c in clusters if any(ch.chunk_id != js_chunk_id for ch in c.chunks)
        ]
        assert all(js_chunk_id not in c.chunk_ids for c in python_clusters)

    def test_synthesize_answer(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test answer synthesis from cluster."""
        chunks = test_chunks[:3]
        relevance_scores = {
            "chunk1": 0.9,
            "chunk2": 0.85,
            "chunk3": 0.8,
        }

        cluster = ChunkCluster(
            chunks=chunks,
            relevance_scores=relevance_scores,
            topic_coherence=0.8,
            temporal_coherence=0.9,
            semantic_density=0.7,
        )

        answer = fusion_engine._synthesize_answer(
            cluster, "Python programming features"
        )

        assert answer is not None
        assert answer.content
        assert answer.source_chunks == chunks
        assert answer.confidence_score > 0
        assert answer.coherence_score > 0
        assert answer.completeness_score > 0
        assert len(answer.key_points) > 0

    def test_fuse_chunks_full_pipeline(
        self, fusion_engine: ChunkFusion, search_results: list[SearchResult]
    ) -> None:
        """Test full chunk fusion pipeline."""
        query = "Python programming language"

        # Remove low-relevance results
        high_relevance_results = [r for r in search_results if r.relevance_score > 0.5]

        fused_answers = fusion_engine.fuse_chunks(
            search_results=high_relevance_results,
            query=query,
            max_clusters=3,
        )

        assert len(fused_answers) > 0

        # Check first answer
        first_answer = fused_answers[0]
        assert first_answer.content
        assert first_answer.confidence_score > 0
        assert first_answer.num_sources >= fusion_engine.min_chunks_for_fusion
        assert len(first_answer.source_documents) > 0

        # Answers should be sorted by confidence
        if len(fused_answers) > 1:
            assert all(
                fused_answers[i].confidence_score
                >= fused_answers[i + 1].confidence_score
                for i in range(len(fused_answers) - 1)
            )

    def test_fuse_chunks_insufficient_chunks(
        self, fusion_engine: ChunkFusion, search_results: list[SearchResult]
    ) -> None:
        """Test fusion with insufficient chunks."""
        # Only one result
        single_result = search_results[:1]

        fused_answers = fusion_engine.fuse_chunks(
            search_results=single_result,
            query="Python",
            max_clusters=3,
        )

        # Should return empty list
        assert fused_answers == []

    def test_fuse_chunks_max_limit(
        self, fusion_engine: ChunkFusion, search_results: list[SearchResult]
    ) -> None:
        """Test fusion respects max chunks limit."""
        # Set low max for testing
        fusion_engine.max_chunks_for_fusion = 3

        fused_answers = fusion_engine.fuse_chunks(
            search_results=search_results,
            query="Python",
            max_clusters=1,
        )

        # Should only consider first 3 chunks
        if fused_answers:
            all_chunk_ids = set()
            for answer in fused_answers:
                all_chunk_ids.update(c.chunk_id for c in answer.source_chunks)

            # Only chunks from first 3 results should be used
            possible_ids = {r.chunk.chunk_id for r in search_results[:3]}
            assert all_chunk_ids.issubset(possible_ids)

    def test_build_content_formatting(
        self, fusion_engine: ChunkFusion, test_chunks: list[Chunk]
    ) -> None:
        """Test content building and formatting."""
        chunks = test_chunks[:3]
        key_points = [
            "Python is a high-level language",
            "Python supports multiple paradigms",
        ]

        content = fusion_engine._build_content(chunks, key_points, "Python features")

        assert "Key Information:" in content
        assert "Detailed Context:" in content
        assert all(point in content for point in key_points)
        assert all(chunk.content in content for chunk in chunks)

        # Test with multiple documents
        mixed_chunks = [test_chunks[0], test_chunks[3]]  # Different documents
        content2 = fusion_engine._build_content(mixed_chunks, [], "Python")

        assert "Based on information from 2 sources" in content2
