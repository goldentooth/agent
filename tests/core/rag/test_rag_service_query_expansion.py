"""Tests for RAG service query expansion integration."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from goldentooth_agent.core.rag.query_expansion import (
    QueryExpansion,
    QueryExpansionEngine,
    QueryIntent,
    SearchStrategy,
)
from goldentooth_agent.core.rag.rag_service import RAGService


class TestRAGServiceQueryExpansion:
    """Test RAG service query expansion functionality."""

    @pytest.fixture
    def mock_dependencies(self) -> dict:
        """Create mock dependencies for RAG service."""
        mock_document_store = MagicMock()
        mock_embeddings_service = AsyncMock()
        mock_vector_store = AsyncMock()
        mock_claude_client = AsyncMock()
        mock_hybrid_search = AsyncMock()
        mock_chunk_fusion = MagicMock()
        mock_chunk_fusion.min_chunks_for_fusion = 2
        mock_query_expansion = MagicMock(spec=QueryExpansionEngine)

        return {
            "document_store": mock_document_store,
            "embeddings_service": mock_embeddings_service,
            "vector_store": mock_vector_store,
            "claude_client": mock_claude_client,
            "hybrid_search_engine": mock_hybrid_search,
            "chunk_fusion": mock_chunk_fusion,
            "query_expansion_engine": mock_query_expansion,
        }

    @pytest.fixture
    def rag_service(self, mock_dependencies: dict) -> RAGService:
        """Create RAG service with mocked dependencies."""
        return RAGService(**mock_dependencies)

    @pytest.fixture
    def mock_query_expansion(self) -> QueryExpansion:
        """Create mock query expansion."""
        return QueryExpansion(
            original_query="python programming tutorial",
            expanded_queries=[
                "python programming tutorial",
                "python development guide",
                "python coding tutorial",
                "python programming steps",
            ],
            intent=QueryIntent.PROCEDURAL,
            key_terms=["python", "programming", "tutorial"],
            synonyms={
                "python": ["py", "python3"],
                "programming": ["coding", "development"],
            },
            related_terms=["language", "scripting", "guide"],
            confidence=0.85,
            suggestions=["Include specific version if relevant"],
        )

    @pytest.fixture
    def mock_search_strategies(
        self, mock_query_expansion: QueryExpansion
    ) -> list[SearchStrategy]:
        """Create mock search strategies."""
        return [
            SearchStrategy(
                strategy_type="primary_strategy",
                queries=[mock_query_expansion.original_query],
                weights=[1.0],
                search_params={
                    "similarity_threshold": 0.1,
                    "boost_structured_content": True,
                },
                expected_intent=QueryIntent.PROCEDURAL,
            ),
            SearchStrategy(
                strategy_type="synonym_enhanced",
                queries=["python programming tutorial", "python development guide"],
                weights=[0.7, 0.5],
                search_params={"similarity_threshold": 0.1, "boost_synonyms": True},
                expected_intent=QueryIntent.PROCEDURAL,
            ),
            SearchStrategy(
                strategy_type="related_terms",
                queries=[
                    "python programming tutorial language",
                    "python programming tutorial scripting",
                ],
                weights=[0.6, 0.4],
                search_params={"similarity_threshold": 0.1, "expand_context": True},
                expected_intent=QueryIntent.PROCEDURAL,
            ),
        ]

    @pytest.fixture
    def mock_hybrid_results(self) -> list[dict]:
        """Create mock hybrid search results for different strategies."""
        return [
            # Primary strategy results
            {
                "retrieved_documents": [
                    {
                        "document_id": "doc1",
                        "chunk_id": "chunk1",
                        "content": "Python is a beginner-friendly programming language with simple syntax.",
                        "is_chunk": True,
                        "chunk_position": 0,
                        "chunk_type": "content",
                        "similarity": 0.9,
                        "combined_score": 0.88,
                        "metadata": {"title": "Python Tutorial"},
                    },
                    {
                        "document_id": "doc1",
                        "chunk_id": "chunk2",
                        "content": "Python programming tutorials cover variables, functions, and classes.",
                        "is_chunk": True,
                        "chunk_position": 1,
                        "chunk_type": "content",
                        "similarity": 0.85,
                        "combined_score": 0.84,
                        "metadata": {"title": "Python Tutorial"},
                    },
                ],
                "context": "Python tutorial context",
                "response": "Python tutorial response",
            },
            # Synonym strategy results
            {
                "retrieved_documents": [
                    {
                        "document_id": "doc2",
                        "chunk_id": "chunk3",
                        "content": "Python development involves writing clean, readable code.",
                        "is_chunk": True,
                        "chunk_position": 0,
                        "chunk_type": "content",
                        "similarity": 0.82,
                        "combined_score": 0.80,
                        "metadata": {"title": "Python Development"},
                    },
                ],
                "context": "Python development context",
                "response": "Python development response",
            },
            # Related terms strategy results
            {
                "retrieved_documents": [
                    {
                        "document_id": "doc3",
                        "chunk_id": "chunk4",
                        "content": "Python scripting language guide for automation tasks.",
                        "is_chunk": True,
                        "chunk_position": 0,
                        "chunk_type": "content",
                        "similarity": 0.78,
                        "combined_score": 0.76,
                        "metadata": {"title": "Python Scripting"},
                    },
                ],
                "context": "Python scripting context",
                "response": "Python scripting response",
            },
        ]

    @pytest.mark.asyncio
    async def test_enhanced_query_success(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_query_expansion: QueryExpansion,
        mock_search_strategies: list[SearchStrategy],
        mock_hybrid_results: list[dict],
    ) -> None:
        """Test successful enhanced query with expansion and fusion."""
        # Configure query expansion mock
        mock_dependencies["query_expansion_engine"].expand_query.return_value = (
            mock_query_expansion
        )
        mock_dependencies[
            "query_expansion_engine"
        ].create_search_strategies.return_value = mock_search_strategies

        # Configure hybrid search to return different results for each strategy
        async def mock_hybrid_query(**kwargs):
            query = kwargs.get("question", "")
            if "development" in query:
                return mock_hybrid_results[1]
            elif "scripting" in query:
                return mock_hybrid_results[2]
            else:
                return mock_hybrid_results[0]

        rag_service.hybrid_query = AsyncMock(side_effect=mock_hybrid_query)

        # Mock chunk fusion
        mock_dependencies["chunk_fusion"].fuse_chunks.return_value = []

        # Execute enhanced query
        result = await rag_service.enhanced_query(
            question="python programming tutorial",
            max_results=10,
            enable_expansion=True,
            enable_fusion=True,
            expansion_strategies=3,
        )

        # Verify structure
        assert "response" in result
        assert "context" in result
        assert "expanded_query" in result
        assert "merged_results" in result
        assert "metadata" in result

        # Check expansion metadata
        expansion_meta = result["expanded_query"]
        assert expansion_meta["original_query"] == "python programming tutorial"
        assert expansion_meta["intent"] == "procedural"
        assert expansion_meta["confidence"] == 0.85
        assert len(expansion_meta["expanded_queries"]) == 4

        # Check merged results
        merged = result["merged_results"]
        assert len(merged["documents"]) > 0
        assert "primary_strategy" in merged["strategy_performance"]

        # Check metadata
        metadata = result["metadata"]
        assert metadata["expansion_enabled"] is True
        assert metadata["fusion_enabled"] is True
        assert metadata["strategies_used"] == 3

    @pytest.mark.asyncio
    async def test_enhanced_query_expansion_disabled(
        self,
        rag_service: RAGService,
        mock_hybrid_results: list[dict],
    ) -> None:
        """Test enhanced query with expansion disabled."""
        # Mock hybrid query to return first result
        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_results[0])

        result = await rag_service.enhanced_query(
            question="python tutorial",
            enable_expansion=False,
        )

        assert result["expanded_query"] is None
        assert result["metadata"]["expansion_enabled"] is False
        assert result["metadata"]["strategies_used"] == 1

    @pytest.mark.asyncio
    async def test_enhanced_query_fusion_disabled(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_query_expansion: QueryExpansion,
        mock_search_strategies: list[SearchStrategy],
        mock_hybrid_results: list[dict],
    ) -> None:
        """Test enhanced query with fusion disabled."""
        # Configure mocks
        mock_dependencies["query_expansion_engine"].expand_query.return_value = (
            mock_query_expansion
        )
        mock_dependencies[
            "query_expansion_engine"
        ].create_search_strategies.return_value = mock_search_strategies[:1]
        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_results[0])

        result = await rag_service.enhanced_query(
            question="python tutorial",
            enable_fusion=False,
        )

        assert result["metadata"]["fusion_enabled"] is False
        # Should not call chunk fusion
        mock_dependencies["chunk_fusion"].fuse_chunks.assert_not_called()

    @pytest.mark.asyncio
    async def test_enhanced_query_auto_reformulation(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_query_expansion: QueryExpansion,
    ) -> None:
        """Test enhanced query with auto-reformulation for poor results."""
        # Configure expansion
        mock_dependencies["query_expansion_engine"].expand_query.return_value = (
            mock_query_expansion
        )

        # Mock create_search_strategies to return empty list (triggers reformulation)
        mock_dependencies[
            "query_expansion_engine"
        ].create_search_strategies.return_value = []

        # Mock poor initial results
        poor_result = {"retrieved_documents": [], "context": "", "response": ""}
        rag_service.hybrid_query = AsyncMock(return_value=poor_result)

        # Mock reformulation
        reformulated_queries = ["python tutorial guide", "learn python programming"]
        mock_dependencies["query_expansion_engine"].reformulate_query.return_value = (
            reformulated_queries
        )

        # Mock better results for reformulated query
        better_result = {
            "retrieved_documents": [
                {
                    "document_id": "doc1",
                    "chunk_id": "chunk1",
                    "content": "Learn Python programming step by step.",
                    "is_chunk": True,
                    "similarity": 0.8,
                    "combined_score": 0.8,
                }
            ],
            "context": "Better context",
            "response": "Better response",
        }

        # Return poor result first, then better result
        rag_service.hybrid_query = AsyncMock(side_effect=[poor_result, better_result])

        result = await rag_service.enhanced_query(
            question="python tutorial",
            auto_reformulate=True,
        )

        # Should show reformulation was attempted
        assert result["metadata"]["reformulation_attempted"] is True
        assert len(result["merged_results"]["documents"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_query_intelligence(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_query_expansion: QueryExpansion,
    ) -> None:
        """Test query intelligence analysis."""
        # Configure expansion and quality analysis
        mock_dependencies["query_expansion_engine"].expand_query.return_value = (
            mock_query_expansion
        )
        mock_dependencies[
            "query_expansion_engine"
        ].analyze_query_quality.return_value = {
            "overall_quality": 0.8,
            "metrics": {
                "length_score": 1.0,
                "specificity_score": 0.7,
                "clarity_score": 0.9,
                "technical_depth": 0.6,
            },
            "intent": "procedural",
            "improvements": ["Include specific Python version if relevant"],
        }

        # Mock reformulation suggestions
        mock_dependencies["query_expansion_engine"].reformulate_query.return_value = [
            "python programming guide",
            "learn python step by step",
        ]

        result = await rag_service.analyze_query_intelligence(
            question="python programming tutorial",
        )

        # Check structure
        assert "query_analysis" in result
        assert "expansion_analysis" in result
        assert "suggestions" in result
        assert "alternative_queries" in result

        # Check query analysis
        analysis = result["query_analysis"]
        assert analysis["overall_quality"] == 0.8
        assert analysis["intent"] == "procedural"

        # Check expansion analysis
        expansion = result["expansion_analysis"]
        assert expansion["confidence"] == 0.85
        assert expansion["intent"] == "procedural"
        assert len(expansion["expanded_queries"]) == 4

        # Check suggestions
        suggestions = result["suggestions"]
        assert "query_improvements" in suggestions
        assert "search_strategy" in suggestions

    @pytest.mark.asyncio
    async def test_analyze_query_intelligence_poor_quality(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
    ) -> None:
        """Test query intelligence analysis for poor quality query."""
        # Configure poor quality expansion
        poor_expansion = QueryExpansion(
            original_query="help",
            expanded_queries=["help"],
            intent=QueryIntent.GENERAL,
            key_terms=["help"],
            synonyms={},
            related_terms=[],
            confidence=0.2,
            suggestions=["Be more specific about what you need help with"],
        )

        poor_quality = {
            "overall_quality": 0.3,
            "metrics": {"length_score": 0.3, "specificity_score": 0.1},
            "intent": "general",
            "improvements": ["Add more specific terms", "Include context words"],
        }

        mock_dependencies["query_expansion_engine"].expand_query.return_value = (
            poor_expansion
        )
        mock_dependencies[
            "query_expansion_engine"
        ].analyze_query_quality.return_value = poor_quality

        result = await rag_service.analyze_query_intelligence(question="help")

        # Should identify poor quality and provide recommendations
        assert result["query_analysis"]["overall_quality"] == 0.3
        assert result["expansion_analysis"]["confidence"] == 0.2
        assert len(result["suggestions"]["query_improvements"]) > 0

    @pytest.mark.asyncio
    async def test_merge_strategy_results(
        self,
        rag_service: RAGService,
        mock_search_strategies: list[SearchStrategy],
        mock_hybrid_results: list[dict],
    ) -> None:
        """Test merging results from multiple search strategies."""
        # Flatten all documents from all results
        all_docs = []
        for result in mock_hybrid_results:
            all_docs.extend(result.get("retrieved_documents", []))

        merged = rag_service._merge_strategy_results(all_docs)

        # Should return merged list of documents
        assert isinstance(merged, list)

        # Should merge documents from all strategies (may deduplicate)
        assert len(merged) <= 4  # Total from all strategies (after dedup)

        # Verify documents have expected structure
        if merged:
            doc = merged[0]
            assert "chunk_id" in doc or "document_id" in doc

    @pytest.mark.asyncio
    async def test_build_enhanced_context(
        self,
        rag_service: RAGService,
        mock_query_expansion: QueryExpansion,
        mock_search_strategies: list[SearchStrategy],
        mock_hybrid_results: list[dict],
    ) -> None:
        """Test building enhanced context from expansion and results."""
        # Flatten all documents from hybrid results
        all_docs = []
        for result in mock_hybrid_results:
            all_docs.extend(result.get("retrieved_documents", []))

        merged_results = rag_service._merge_strategy_results(all_docs)

        context = rag_service._build_enhanced_context(
            documents=merged_results,
            fused_answers=[],
            expansion=mock_query_expansion,
            original_question="python programming tutorial",
        )

        # Should include expansion information
        assert "Query Analysis" in context
        assert "Intent: Procedural" in context
        assert "Key Terms:" in context

        # Should include document information
        assert "Source Documents" in context
        assert "Python is a beginner-friendly" in context

    @pytest.mark.asyncio
    async def test_generate_query_recommendations(
        self,
        rag_service: RAGService,
        mock_query_expansion: QueryExpansion,
    ) -> None:
        """Test query recommendation generation."""
        strategy_performance = {
            "primary": {"num_results": 5, "avg_relevance": 0.8},
            "synonym_enhanced": {"num_results": 3, "avg_relevance": 0.7},
            "related_terms": {"num_results": 1, "avg_relevance": 0.6},
        }

        recommendations = rag_service._generate_query_recommendations(
            expansion=mock_query_expansion,
            strategy_performance=strategy_performance,
        )

        assert "query_improvements" in recommendations
        assert "search_strategy" in recommendations
        assert "expansion_quality" in recommendations

        # Should provide specific recommendations based on performance
        strategy_recs = recommendations["search_strategy"]
        assert len(strategy_recs) > 0

    @pytest.mark.asyncio
    async def test_enhanced_query_error_handling(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
    ) -> None:
        """Test error handling in enhanced query."""
        # Configure expansion to raise error
        mock_dependencies["query_expansion_engine"].expand_query.side_effect = (
            Exception("Expansion error")
        )

        result = await rag_service.enhanced_query(
            question="test query",
            enable_expansion=True,
        )

        # Should gracefully handle error and fall back to basic search
        assert result["metadata"]["expansion_enabled"] is False
        assert result["metadata"]["error"] is True
        assert "Expansion error" in result["metadata"]["error_message"]

    @pytest.mark.asyncio
    async def test_enhanced_query_custom_domain_context(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_query_expansion: QueryExpansion,
        mock_search_strategies: list[SearchStrategy],
        mock_hybrid_results: list[dict],
    ) -> None:
        """Test enhanced query with custom domain context."""
        # Configure mocks
        mock_dependencies["query_expansion_engine"].expand_query.return_value = (
            mock_query_expansion
        )
        mock_dependencies[
            "query_expansion_engine"
        ].create_search_strategies.return_value = mock_search_strategies[:1]
        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_results[0])

        result = await rag_service.enhanced_query(
            question="kubernetes deployment",
            domain_context="kubernetes",
        )

        # Should pass domain context to expansion
        mock_dependencies["query_expansion_engine"].expand_query.assert_called_once()
        call_args = mock_dependencies["query_expansion_engine"].expand_query.call_args
        assert call_args[1]["domain_context"] == "kubernetes"

    @pytest.mark.asyncio
    async def test_enhanced_query_strategy_limits(
        self,
        rag_service: RAGService,
        mock_dependencies: dict,
        mock_query_expansion: QueryExpansion,
        mock_search_strategies: list[SearchStrategy],
        mock_hybrid_results: list[dict],
    ) -> None:
        """Test enhanced query respects strategy limits."""
        # Configure mocks
        mock_dependencies["query_expansion_engine"].expand_query.return_value = (
            mock_query_expansion
        )

        # Return only first 2 strategies when max_strategies=2 is requested
        def limit_strategies(expansion, max_strategies=None):
            if max_strategies is not None:
                return mock_search_strategies[:max_strategies]
            return mock_search_strategies

        mock_dependencies[
            "query_expansion_engine"
        ].create_search_strategies.side_effect = limit_strategies

        # Mock hybrid search
        rag_service.hybrid_query = AsyncMock(return_value=mock_hybrid_results[0])

        # Request only 2 strategies
        result = await rag_service.enhanced_query(
            question="test query",
            expansion_strategies=2,
        )

        # Should use only 2 strategies
        assert result["metadata"]["strategies_used"] == 2

        # Verify create_search_strategies was called with correct limit
        mock_dependencies[
            "query_expansion_engine"
        ].create_search_strategies.assert_called_once()
        call_args = mock_dependencies[
            "query_expansion_engine"
        ].create_search_strategies.call_args
        assert call_args[1]["max_strategies"] == 2
