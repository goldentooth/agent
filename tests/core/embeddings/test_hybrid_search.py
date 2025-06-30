"""Tests for hybrid search engine functionality."""

from unittest.mock import AsyncMock, Mock

import pytest

from goldentooth_agent.core.embeddings.hybrid_search import HybridSearchEngine


class TestHybridSearchEngine:
    """Test the HybridSearchEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_vector_store = Mock()
        self.mock_embeddings_service = AsyncMock()

        # Create hybrid search engine
        self.search_engine = HybridSearchEngine(
            vector_store=self.mock_vector_store,
            embeddings_service=self.mock_embeddings_service,
        )

    def test_initialization(self):
        """Test that the search engine initializes correctly."""
        assert self.search_engine.vector_store == self.mock_vector_store
        assert self.search_engine.embeddings_service == self.mock_embeddings_service

        # Check default parameters
        assert self.search_engine.k1 == 1.5
        assert self.search_engine.b == 0.75
        assert self.search_engine.semantic_weight == 0.7
        assert self.search_engine.keyword_weight == 0.3

        # Check stop words are loaded
        assert len(self.search_engine.stop_words) > 0
        assert "the" in self.search_engine.stop_words
        assert "and" in self.search_engine.stop_words

    def test_tokenize(self):
        """Test text tokenization."""
        # Basic tokenization
        tokens = self.search_engine._tokenize("Hello world, this is a test!")
        expected = ["hello", "world", "test"]  # Stop words and short words removed
        assert tokens == expected

        # Empty text
        assert self.search_engine._tokenize("") == []
        assert self.search_engine._tokenize(None) == []

        # Text with special characters
        tokens = self.search_engine._tokenize("Python 3.11+ & machine-learning")
        assert "python" in tokens
        assert "machine" in tokens
        assert "learning" in tokens

        # Stop words filtering
        tokens = self.search_engine._tokenize("the quick brown fox")
        assert "the" not in tokens  # Stop word
        assert "quick" in tokens
        assert "brown" in tokens

        # Short token filtering
        tokens = self.search_engine._tokenize("a big elephant")
        assert "big" in tokens
        assert "elephant" in tokens

    @pytest.mark.asyncio
    async def test_get_semantic_results(self):
        """Test getting semantic search results."""
        # Mock embeddings service
        self.mock_embeddings_service.create_embedding.return_value = [0.1] * 1536

        # Mock vector store results
        mock_results = [
            {
                "doc_id": "test.doc1",
                "content": "Test document content",
                "similarity_score": 0.9,
                "store_type": "notes",
                "document_id": "doc1",
            },
            {
                "doc_id": "test.doc2",
                "content": "Another test document",
                "similarity_score": 0.8,
                "store_type": "notes",
                "document_id": "doc2",
            },
        ]
        self.mock_vector_store.search_similar.return_value = mock_results

        # Test semantic search
        results = await self.search_engine._get_semantic_results(
            query="test query",
            limit=10,
            store_type="notes",
            include_chunks=True,
            min_score=0.1,
        )

        # Verify results
        assert len(results) == 2
        assert all(r["search_method"] == "semantic" for r in results)
        assert all("semantic_score" in r for r in results)
        assert results[0]["semantic_score"] == 0.9
        assert results[1]["semantic_score"] == 0.8

        # Verify embeddings service was called
        self.mock_embeddings_service.create_embedding.assert_called_once_with(
            "test query"
        )

        # Verify vector store was called with correct parameters
        self.mock_vector_store.search_similar.assert_called_once()
        call_args = self.mock_vector_store.search_similar.call_args
        assert call_args[1]["limit"] == 10
        assert call_args[1]["store_type"] == "notes"
        assert call_args[1]["include_chunks"] is True
        # Note: similarity_threshold filtering is now done post-search

    def test_calculate_corpus_stats(self):
        """Test corpus statistics calculation."""
        # Test with simple documents
        documents = [
            "the quick brown fox jumps",
            "brown fox runs quickly",
            "quick running fox",
        ]

        self.search_engine._calculate_corpus_stats(documents)

        # Check corpus stats were calculated
        assert self.search_engine._corpus_stats is not None
        assert self.search_engine._term_frequencies is not None
        assert self.search_engine._document_lengths is not None

        stats = self.search_engine._corpus_stats
        assert stats["total_documents"] == 3
        assert "average_document_length" in stats
        assert "document_frequencies" in stats

        # Check term frequencies
        assert len(self.search_engine._term_frequencies) == 3
        assert len(self.search_engine._document_lengths) == 3

        # Check document frequencies
        doc_frequencies = stats["document_frequencies"]
        assert "fox" in doc_frequencies
        assert doc_frequencies["fox"] == 3  # Appears in all documents
        assert "quick" in doc_frequencies
        assert doc_frequencies["quick"] >= 1

    def test_calculate_bm25_scores(self):
        """Test BM25 score calculation."""
        # Set up corpus with words that won't be filtered out
        documents = [
            "python programming language tutorial",
            "java programming concepts explained",
            "machine learning with python",
        ]

        # Mock document corpus
        self.search_engine._document_corpus = {
            "doc1": {"content": documents[0]},
            "doc2": {"content": documents[1]},
            "doc3": {"content": documents[2]},
        }

        self.search_engine._calculate_corpus_stats(documents)

        # Test BM25 scoring with non-stop words
        scores = self.search_engine._calculate_bm25_scores("python programming")

        # Verify scores
        assert len(scores) == 3
        assert all(isinstance(score, tuple) for score in scores)
        assert all(len(score) == 2 for score in scores)

        # Scores should be sorted in descending order
        score_values = [score[1] for score in scores]
        assert score_values == sorted(score_values, reverse=True)

        # Check that we get some scores (not all zero)
        doc_ids_and_scores = dict(scores)
        total_score = sum(doc_ids_and_scores.values())
        assert total_score > 0  # At least some documents should have scores

        # Documents containing both terms should score highest
        assert (
            doc_ids_and_scores["doc1"] > 0
        )  # Contains both "python" and "programming"
        assert doc_ids_and_scores["doc3"] > 0  # Contains "python"
        assert doc_ids_and_scores["doc2"] > 0  # Contains "programming"

        # Doc1 should score highest (contains both terms)
        assert doc_ids_and_scores["doc1"] >= doc_ids_and_scores["doc2"]
        assert doc_ids_and_scores["doc1"] >= doc_ids_and_scores["doc3"]

    def test_calculate_document_bm25_score(self):
        """Test BM25 scoring for individual documents."""
        # Set up simple corpus
        documents = ["fox runs quickly", "quick brown fox"]
        self.search_engine._calculate_corpus_stats(documents)

        # Test scoring for first document
        score = self.search_engine._calculate_document_bm25_score(
            query_terms=["fox", "quick"], doc_index=0
        )

        assert score >= 0.0
        assert isinstance(score, float)

        # Test with non-existent terms
        score_empty = self.search_engine._calculate_document_bm25_score(
            query_terms=["nonexistent"], doc_index=0
        )

        assert score_empty == 0.0

    def test_calculate_exact_match_boost(self):
        """Test exact match boosting calculation."""
        result = {
            "content": "This is a test document with exact phrase matching",
            "title": "Test Document",
        }

        # Test exact phrase match
        boost = self.search_engine._calculate_exact_match_boost("exact phrase", result)
        assert boost == 0.2

        # Test partial match
        boost = self.search_engine._calculate_exact_match_boost("test document", result)
        assert boost >= 0.15  # Should get consecutive word match

        # Test no match
        boost = self.search_engine._calculate_exact_match_boost("no match here", result)
        assert boost == 0.0

    def test_calculate_title_match_boost(self):
        """Test title match boosting calculation."""
        result = {
            "title": "Python Programming Guide",
            "chunk_title": "Advanced Concepts",
            "document_id": "python-tutorial",
            "content": "Content here",
        }

        # Test title match
        boost = self.search_engine._calculate_title_match_boost("programming", result)
        assert boost == 0.15

        # Test chunk title match
        boost = self.search_engine._calculate_title_match_boost("concepts", result)
        assert boost == 0.1

        # Test document ID match
        boost = self.search_engine._calculate_title_match_boost("tutorial", result)
        assert boost == 0.05

        # Test multiple matches
        boost = self.search_engine._calculate_title_match_boost("python", result)
        assert boost == 0.2  # Both title and document ID match

    def test_get_doc_id(self):
        """Test document ID extraction."""
        # Test chunk result
        chunk_result = {
            "is_chunk": True,
            "chunk_id": "notes.doc1.section1",
            "store_type": "notes",
            "document_id": "doc1",
        }

        doc_id = self.search_engine._get_doc_id(chunk_result)
        assert doc_id == "notes.doc1.section1"

        # Test regular document result
        doc_result = {
            "is_chunk": False,
            "store_type": "github.repos",
            "document_id": "my-repo",
        }

        doc_id = self.search_engine._get_doc_id(doc_result)
        assert doc_id == "github.repos.my-repo"

        # Test result without chunk info
        simple_result = {
            "store_type": "notes",
            "document_id": "simple-doc",
        }

        doc_id = self.search_engine._get_doc_id(simple_result)
        assert doc_id == "notes.simple-doc"

    def test_combine_results(self):
        """Test combining semantic and keyword results."""
        # Mock semantic results
        semantic_results = [
            {
                "store_type": "notes",
                "document_id": "doc1",
                "content": "Semantic content",
                "semantic_score": 0.9,
                "similarity_score": 0.9,
            },
            {
                "store_type": "notes",
                "document_id": "doc2",
                "content": "Another semantic result",
                "semantic_score": 0.8,
                "similarity_score": 0.8,
            },
        ]

        # Mock keyword results
        keyword_results = [
            {
                "store_type": "notes",
                "document_id": "doc1",  # Same as semantic result
                "content": "Keyword content",
                "keyword_score": 0.7,
                "similarity_score": 0.7,
            },
            {
                "store_type": "notes",
                "document_id": "doc3",  # New result
                "content": "Keyword only result",
                "keyword_score": 0.6,
                "similarity_score": 0.6,
            },
        ]

        # Test combination
        combined = self.search_engine._combine_results(
            query="test query",
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            semantic_weight=0.7,
            keyword_weight=0.3,
            boost_exact_matches=False,
            boost_title_matches=False,
        )

        # Should have 3 unique documents
        assert len(combined) == 3

        # Check hybrid scores were calculated
        for result in combined:
            assert "hybrid_score" in result
            assert "scoring_breakdown" in result

            breakdown = result["scoring_breakdown"]
            assert "semantic_score" in breakdown
            assert "keyword_score" in breakdown
            assert "semantic_weight" in breakdown
            assert "keyword_weight" in breakdown

        # Find the overlapping document (doc1)
        doc1_result = next(r for r in combined if r["document_id"] == "doc1")
        assert doc1_result["semantic_score"] == 0.9
        assert doc1_result["keyword_score"] == 0.7

        # Hybrid score should be weighted combination
        expected_hybrid = (
            0.7 * 0.9 + 0.3 * 0.7
        )  # semantic_weight * semantic + keyword_weight * keyword
        assert abs(doc1_result["hybrid_score"] - expected_hybrid) < 0.001

    @pytest.mark.asyncio
    async def test_hybrid_search_integration(self):
        """Test the main hybrid search method."""
        # Mock semantic results
        semantic_results = [
            {
                "doc_id": "notes.doc1",
                "store_type": "notes",
                "document_id": "doc1",
                "content": "Python programming tutorial",
                "similarity_score": 0.9,
            }
        ]

        # Mock keyword results
        keyword_results = [
            {
                "doc_id": "notes.doc2",
                "store_type": "notes",
                "document_id": "doc2",
                "content": "Tutorial for python programming",
                "similarity_score": 0.8,
            }
        ]

        # Mock the component methods
        self.search_engine._get_semantic_results = AsyncMock(
            return_value=semantic_results
        )
        self.search_engine._get_keyword_results = AsyncMock(
            return_value=keyword_results
        )

        # Test hybrid search
        results = await self.search_engine.hybrid_search(
            query="python tutorial",
            max_results=5,
            semantic_weight=0.6,
            keyword_weight=0.4,
        )

        # Verify results
        assert len(results) <= 5
        assert all("hybrid_score" in r for r in results)
        assert all("scoring_breakdown" in r for r in results)

        # Results should be sorted by hybrid score
        scores = [r["hybrid_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_update_parameters(self):
        """Test parameter updating methods."""
        # Test hybrid weight updates
        self.search_engine.update_hybrid_weights(0.8, 0.2)
        assert self.search_engine.semantic_weight == 0.8
        assert self.search_engine.keyword_weight == 0.2

        # Test with zero total (should reset to defaults)
        self.search_engine.update_hybrid_weights(0.0, 0.0)
        assert self.search_engine.semantic_weight == 0.7
        assert self.search_engine.keyword_weight == 0.3

        # Test BM25 parameter updates
        self.search_engine.update_bm25_parameters(k1=2.0, b=0.5)
        assert self.search_engine.k1 == 2.0
        assert self.search_engine.b == 0.5

        # Test boundary conditions
        self.search_engine.update_bm25_parameters(k1=-1.0, b=2.0)
        assert self.search_engine.k1 == 0.0  # Should be clamped to 0
        assert self.search_engine.b == 1.0  # Should be clamped to 1

    def test_get_search_stats(self):
        """Test search statistics retrieval."""
        # Test with no corpus built
        stats = self.search_engine.get_search_stats()
        assert stats["corpus_built"] is False

        # Build a corpus
        documents = ["test document one", "test document two"]
        self.search_engine._calculate_corpus_stats(documents)

        # Test with corpus built
        stats = self.search_engine.get_search_stats()
        assert stats["corpus_built"] is True
        assert stats["total_documents"] == 2
        assert "average_document_length" in stats
        assert "unique_terms" in stats
        assert "bm25_parameters" in stats
        assert "hybrid_weights" in stats

        # Check parameter values
        assert stats["bm25_parameters"]["k1"] == self.search_engine.k1
        assert stats["bm25_parameters"]["b"] == self.search_engine.b
        assert (
            stats["hybrid_weights"]["semantic_weight"]
            == self.search_engine.semantic_weight
        )
        assert (
            stats["hybrid_weights"]["keyword_weight"]
            == self.search_engine.keyword_weight
        )

    @pytest.mark.asyncio
    async def test_explain_search_results(self):
        """Test search results explanation."""
        # Mock results with scoring breakdown
        results = [
            {
                "doc_id": "notes.doc1",
                "content": "Python programming tutorial for beginners",
                "hybrid_score": 0.85,
                "scoring_breakdown": {
                    "semantic_score": 0.9,
                    "keyword_score": 0.7,
                    "semantic_weight": 0.7,
                    "keyword_weight": 0.3,
                    "base_hybrid_score": 0.84,
                    "boosting_applied": 0.01,
                },
            }
        ]

        # Build simple corpus for stats
        self.search_engine._calculate_corpus_stats(["test document"])

        explanation = await self.search_engine.explain_search_results(
            query="python tutorial", results=results
        )

        # Verify explanation structure
        assert "query_analysis" in explanation
        assert "scoring_explanation" in explanation
        assert "top_results_analysis" in explanation
        assert "corpus_stats" in explanation

        # Check query analysis
        query_analysis = explanation["query_analysis"]
        assert query_analysis["query"] == "python tutorial"
        assert "query_tokens" in query_analysis
        assert "query_length" in query_analysis

        # Check scoring explanation
        scoring = explanation["scoring_explanation"]
        assert "hybrid_scoring" in scoring
        assert "semantic_scoring" in scoring
        assert "keyword_scoring" in scoring
        assert "boosting" in scoring

        # Check top results analysis
        top_results = explanation["top_results_analysis"]
        assert len(top_results) == 1
        assert top_results[0]["rank"] == 1
        assert "scores" in top_results[0]
        assert "search_methods" in top_results[0]

    def test_empty_inputs_handling(self):
        """Test handling of empty or invalid inputs."""
        # Test empty tokenization
        assert self.search_engine._tokenize("") == []
        assert self.search_engine._tokenize("   ") == []

        # Test with only stop words
        tokens = self.search_engine._tokenize("the and or but")
        assert tokens == []

        # Test empty corpus stats
        self.search_engine._calculate_corpus_stats([])
        assert self.search_engine._corpus_stats is None
        assert self.search_engine._term_frequencies is None
        assert self.search_engine._document_lengths is None

        # Test BM25 with empty corpus
        scores = self.search_engine._calculate_bm25_scores("test query")
        assert scores == []

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test very short documents
        documents = ["a", "is", "the"]  # All stop words/short words
        self.search_engine._document_corpus = {
            "doc1": {"content": documents[0]},
            "doc2": {"content": documents[1]},
            "doc3": {"content": documents[2]},
        }
        self.search_engine._calculate_corpus_stats(documents)

        # Should handle gracefully
        scores = self.search_engine._calculate_bm25_scores("test")
        assert isinstance(scores, list)

        # Test very long query with repeated words
        long_query = " ".join(["word"] * 100)
        tokens = self.search_engine._tokenize(long_query)
        assert len(tokens) == 100  # Each instance is tokenized separately

        # Test special characters in query
        special_query = "test@#$%^&*()query"
        tokens = self.search_engine._tokenize(special_query)
        assert "test" in tokens or "query" in tokens

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in async methods."""
        # Test semantic search with exception
        self.mock_embeddings_service.create_embedding.side_effect = Exception(
            "Embedding failed"
        )

        results = await self.search_engine._get_semantic_results(
            query="test", limit=5, store_type=None, include_chunks=True, min_score=0.1
        )

        assert results == []  # Should return empty list on error

        # Test keyword search with no corpus
        results = await self.search_engine._get_keyword_results(
            query="test", limit=5, store_type=None, include_chunks=True, min_score=0.0
        )

        assert results == []  # Should return empty list when no corpus
