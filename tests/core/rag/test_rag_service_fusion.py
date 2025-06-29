"""Tests for RAG service chunk fusion integration."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from goldentooth_agent.core.embeddings.models import Chunk
from goldentooth_agent.core.rag.chunk_fusion import ChunkFusion, FusedAnswer
from goldentooth_agent.core.rag.rag_service import RAGService


class TestRAGServiceFusion:
    """Test RAG service chunk fusion functionality."""

    @pytest.fixture
    def mock_dependencies(self) -> dict:
        """Create mock dependencies for RAG service."""
        mock_document_store = MagicMock()
        mock_embeddings_service = AsyncMock()
        mock_vector_store = AsyncMock()
        mock_claude_client = AsyncMock()
        mock_hybrid_search = AsyncMock()
        mock_chunk_fusion = MagicMock(spec=ChunkFusion)

        # Configure chunk fusion mock
        mock_chunk_fusion.min_chunks_for_fusion = 2
        mock_chunk_fusion.max_chunks_for_fusion = 10
        mock_chunk_fusion.coherence_threshold = 0.6

        return {
            "document_store": mock_document_store,
            "embeddings_service": mock_embeddings_service,
            "vector_store": mock_vector_store,
            "claude_client": mock_claude_client,
            "hybrid_search_engine": mock_hybrid_search,
            "chunk_fusion": mock_chunk_fusion,
        }

    @pytest.fixture
    def rag_service(self, mock_dependencies: dict) -> RAGService:
        """Create RAG service with mocked dependencies."""
        return RAGService(**mock_dependencies)

    @pytest.fixture
    def mock_hybrid_result(self) -> dict:
        """Create mock hybrid search result."""
        return {
            "retrieved_documents": [
                {
                    "document_id": "doc1",
                    "chunk_id": "chunk1",
                    "content": "Python is a versatile programming language.",
                    "is_chunk": True,
                    "chunk_position": 0,
                    "chunk_type": "content",
                    "similarity": 0.9,
                    "combined_score": 0.88,
                    "metadata": {"title": "Python Guide"},
                    "search_method": "hybrid",
                    "explanation": "High semantic and keyword match",
                },
                {
                    "document_id": "doc1",
                    "chunk_id": "chunk2",
                    "content": "Python is used for web development, data science, and AI.",
                    "is_chunk": True,
                    "chunk_position": 1,
                    "chunk_type": "content",
                    "similarity": 0.85,
                    "combined_score": 0.84,
                    "metadata": {"title": "Python Guide"},
                    "search_method": "hybrid",
                    "explanation": "Good semantic match",
                },
                {
                    "document_id": "doc2",
                    "chunk_id": "chunk3",
                    "content": "Python's simplicity makes it ideal for beginners.",
                    "is_chunk": True,
                    "chunk_position": 0,
                    "chunk_type": "content",
                    "similarity": 0.82,
                    "combined_score": 0.80,
                    "metadata": {"title": "Learning Python"},
                    "search_method": "hybrid",
                    "explanation": "Relevant content match",
                },
            ],
            "context": "Test context",
            "response": "Test response",
        }

    @pytest.fixture
    def mock_fused_answers(self) -> list[FusedAnswer]:
        """Create mock fused answers."""
        chunk1 = Chunk(
            chunk_id="chunk1",
            document_id="doc1",
            content="Python is versatile.",
            position=0,
            metadata={},
            chunk_type="content",
        )
        chunk2 = Chunk(
            chunk_id="chunk2",
            document_id="doc1",
            content="Python for web and data science.",
            position=1,
            metadata={},
            chunk_type="content",
        )

        answer1 = FusedAnswer(
            content="Python is a versatile language used for web development and data science.",
            source_chunks=[chunk1, chunk2],
            confidence_score=0.85,
            coherence_score=0.8,
            completeness_score=0.75,
            key_points=["Python is versatile", "Used for web and data science"],
            contradictions=[],
            metadata={"fusion_method": "coherent_clustering"},
        )

        return [answer1]

    @pytest.mark.asyncio
    async def test_query_with_fusion_success(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_hybrid_result: dict,
        mock_fused_answers: list[FusedAnswer],
    ) -> None:
        """Test successful query with fusion."""
        # Configure mocks
        mock_dependencies["hybrid_search_engine"].search.return_value = (
            mock_hybrid_result
        )
        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_result)
        mock_dependencies["chunk_fusion"].fuse_chunks.return_value = mock_fused_answers
        rag_service._generate_response = AsyncMock(
            return_value="Fused response about Python"
        )

        # Execute query
        result = await rag_service.query_with_fusion(
            question="What is Python used for?",
            max_results=10,
            semantic_weight=0.7,
            keyword_weight=0.3,
            fusion_coherence_threshold=0.6,
        )

        # Verify result structure
        assert "response" in result
        assert "context" in result
        assert "fused_answers" in result
        assert "unfused_results" in result
        assert "metadata" in result

        # Check fused answers
        assert len(result["fused_answers"]) == 1
        fused = result["fused_answers"][0]
        assert fused["confidence_score"] == 0.85
        assert fused["coherence_score"] == 0.8
        assert fused["completeness_score"] == 0.75
        assert len(fused["key_points"]) == 2
        assert fused["num_sources"] == 2

        # Check metadata
        metadata = result["metadata"]
        assert metadata["fusion_attempted"] is True
        assert metadata["num_fused_answers"] == 1
        assert "fusion_settings" in metadata
        assert "search_settings" in metadata

    @pytest.mark.asyncio
    async def test_query_with_fusion_no_results(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
    ) -> None:
        """Test query with fusion when no results found."""
        # Configure empty hybrid result
        empty_result = {
            "retrieved_documents": [],
            "context": "",
            "response": "",
        }
        rag_service.hybrid_query = AsyncMock(return_value=empty_result)

        result = await rag_service.query_with_fusion(
            question="Unknown query",
            max_results=10,
        )

        assert result["fused_answers"] == []
        assert result["unfused_results"] == []
        assert result["context"] == "No relevant documents found."
        assert result["metadata"]["fusion_attempted"] is False
        assert result["metadata"]["reason"] == "No documents retrieved"

    @pytest.mark.asyncio
    async def test_query_with_fusion_insufficient_chunks(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
    ) -> None:
        """Test query with fusion when insufficient chunks for fusion."""
        # Configure result with only one chunk
        single_chunk_result = {
            "retrieved_documents": [
                {
                    "document_id": "doc1",
                    "chunk_id": "chunk1",
                    "content": "Single chunk content.",
                    "is_chunk": True,
                    "chunk_position": 0,
                    "chunk_type": "content",
                    "similarity": 0.9,
                    "combined_score": 0.9,
                },
            ],
        }
        rag_service.hybrid_query = AsyncMock(return_value=single_chunk_result)
        mock_dependencies["chunk_fusion"].fuse_chunks.return_value = []

        result = await rag_service.query_with_fusion(
            question="Test query",
            max_results=10,
            include_unfused=True,
        )

        # Should have no fused answers but should include unfused results
        assert result["fused_answers"] == []
        assert len(result["unfused_results"]) == 1
        assert result["metadata"]["fusion_attempted"] is True
        assert result["metadata"]["num_chunks_retrieved"] == 1

    @pytest.mark.asyncio
    async def test_query_with_fusion_with_unfused(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_hybrid_result: dict,
        mock_fused_answers: list[FusedAnswer],
    ) -> None:
        """Test query with fusion including unfused results."""
        # Add more chunks to hybrid result
        extra_chunk = {
            "document_id": "doc3",
            "chunk_id": "chunk4",
            "content": "Extra unfused content about Python.",
            "is_chunk": True,
            "chunk_position": 0,
            "chunk_type": "content",
            "similarity": 0.7,
            "combined_score": 0.68,
        }
        mock_hybrid_result["retrieved_documents"].append(extra_chunk)

        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_result)
        mock_dependencies["chunk_fusion"].fuse_chunks.return_value = mock_fused_answers
        rag_service._generate_response = AsyncMock(return_value="Response")

        result = await rag_service.query_with_fusion(
            question="Python features",
            include_unfused=True,
        )

        # Should have both fused and unfused results
        assert len(result["fused_answers"]) == 1
        assert len(result["unfused_results"]) > 0

        # Check unfused result format
        unfused = result["unfused_results"][0]
        assert "chunk_id" in unfused
        assert "document_id" in unfused
        assert "content" in unfused
        assert "relevance_score" in unfused
        assert "chunk_type" in unfused

    @pytest.mark.asyncio
    async def test_query_with_fusion_custom_threshold(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_hybrid_result: dict,
    ) -> None:
        """Test query with custom fusion coherence threshold."""
        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_result)
        mock_dependencies["chunk_fusion"].fuse_chunks.return_value = []

        # Custom threshold
        custom_threshold = 0.8

        await rag_service.query_with_fusion(
            question="Test",
            fusion_coherence_threshold=custom_threshold,
        )

        # Verify threshold was updated
        assert mock_dependencies["chunk_fusion"].coherence_threshold == custom_threshold

    @pytest.mark.asyncio
    async def test_query_with_fusion_error_handling(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
    ) -> None:
        """Test error handling in query with fusion."""
        # Configure mock to raise error
        rag_service.hybrid_query = AsyncMock(side_effect=Exception("Test error"))

        result = await rag_service.query_with_fusion(
            question="Test query",
        )

        assert result["response"] == ""
        assert "Error during fusion query" in result["context"]
        assert result["fused_answers"] == []
        assert result["unfused_results"] == []
        assert result["metadata"]["error"] is True
        assert "Test error" in result["metadata"]["error_message"]

    @pytest.mark.asyncio
    async def test_analyze_fusion_quality(
        self,
        rag_service: RAGService,
    ) -> None:
        """Test fusion quality analysis."""

        # Mock query_with_fusion to return different results for different configs
        async def mock_fusion_query(**kwargs):
            threshold = kwargs.get("fusion_coherence_threshold", 0.6)

            # Simulate different quality based on threshold
            if threshold <= 0.5:
                num_answers = 3
                avg_confidence = 0.7
            elif threshold <= 0.7:
                num_answers = 2
                avg_confidence = 0.8
            else:
                num_answers = 1
                avg_confidence = 0.85

            return {
                "fused_answers": [
                    {
                        "confidence_score": avg_confidence,
                        "coherence_score": 0.75,
                        "completeness_score": 0.7,
                        "num_sources": 3,
                        "key_points": ["point1", "point2"],
                        "contradictions": [],
                    }
                    for _ in range(num_answers)
                ],
            }

        rag_service.query_with_fusion = AsyncMock(side_effect=mock_fusion_query)

        result = await rag_service.analyze_fusion_quality(
            question="Test question",
            max_results=10,
        )

        assert "configurations_tested" in result
        assert result["configurations_tested"] == 4
        assert "results" in result
        assert "best_configuration" in result
        assert "recommendations" in result

        # Check that all configurations were tested
        assert len(result["results"]) == 4

        # Verify best configuration selection
        best_config = result["best_configuration"]
        assert "coherence_threshold" in best_config
        assert "max_clusters" in best_config

    @pytest.mark.asyncio
    async def test_analyze_fusion_quality_custom_configs(
        self,
        rag_service: RAGService,
    ) -> None:
        """Test fusion quality analysis with custom configurations."""
        custom_configs = [
            {"coherence_threshold": 0.4, "max_clusters": 2},
            {"coherence_threshold": 0.9, "max_clusters": 5},
        ]

        # Mock simple response
        rag_service.query_with_fusion = AsyncMock(
            return_value={
                "fused_answers": [
                    {
                        "confidence_score": 0.8,
                        "coherence_score": 0.7,
                        "completeness_score": 0.75,
                        "num_sources": 2,
                        "key_points": [],
                        "contradictions": [],
                    }
                ],
            }
        )

        result = await rag_service.analyze_fusion_quality(
            question="Test",
            test_configurations=custom_configs,
        )

        assert result["configurations_tested"] == 2
        assert len(result["results"]) == 2

    def test_generate_fusion_recommendations(self, rag_service: RAGService) -> None:
        """Test fusion recommendation generation."""
        # Test with low scores
        results_low = [
            {
                "metrics": {
                    "avg_confidence": 0.3,
                    "avg_coherence": 0.4,
                    "avg_completeness": 0.5,
                    "num_fused_answers": 1,
                    "has_contradictions": False,
                }
            }
        ]

        recommendations = rag_service._generate_fusion_recommendations(results_low)

        assert len(recommendations) > 0
        assert any("coherence threshold lower" in r for r in recommendations)
        assert any(
            "coherence suggests chunks may be from disparate" in r
            for r in recommendations
        )
        assert any("completeness scores" in r for r in recommendations)

        # Test with contradictions
        results_contradictions = [
            {
                "metrics": {
                    "avg_confidence": 0.8,
                    "avg_coherence": 0.8,
                    "avg_completeness": 0.8,
                    "num_fused_answers": 3,
                    "has_contradictions": True,
                }
            }
        ]

        recommendations2 = rag_service._generate_fusion_recommendations(
            results_contradictions
        )
        assert any("Contradictions detected" in r for r in recommendations2)

    @pytest.mark.asyncio
    async def test_query_with_fusion_context_building(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_hybrid_result: dict,
        mock_fused_answers: list[FusedAnswer],
    ) -> None:
        """Test context building in fusion query."""
        # Add contradictions to mock answer
        mock_fused_answers[0].contradictions = ["Speed claims differ"]

        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_result)
        mock_dependencies["chunk_fusion"].fuse_chunks.return_value = mock_fused_answers
        rag_service._generate_response = AsyncMock(return_value="Response")

        result = await rag_service.query_with_fusion(
            question="Python performance",
        )

        context = result["context"]

        # Check context structure
        assert "=== Synthesized Answers ===" in context
        assert "Answer 1 (Confidence: 0.85):" in context
        assert "Based on 2 chunks from 1 documents" in context
        assert "Potential Contradictions:" in context
        assert "Speed claims differ" in context
