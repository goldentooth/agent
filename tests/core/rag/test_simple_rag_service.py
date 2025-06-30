"""
Tests for simple RAG service functionality.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from goldentooth_agent.core.rag.simple_rag_service import SimpleRAGService


class TestSimpleRAGService:
    """Test suite for SimpleRAGService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

        # Mock dependencies
        self.mock_document_store = Mock()
        self.mock_embeddings_service = Mock()
        self.mock_vector_store = Mock()
        self.mock_claude_client = Mock()

        # Configure mock embeddings service
        self.mock_embeddings_service.create_embedding = AsyncMock(
            return_value=[0.1, 0.2, 0.3, 0.4, 0.5]
        )

        # Configure mock vector store
        self.mock_vector_store.search_similar = Mock(return_value=[])
        self.mock_vector_store.get_stats = Mock(return_value={"total_documents": 10})

        # Configure mock Claude client
        self.mock_claude_client.create_chat_completion = AsyncMock(
            return_value="This is a test response from Claude."
        )

        # Configure mock document store
        self.mock_document_store.get_document_count = Mock(
            return_value={"github.repos": 5, "notes": 3}
        )

        # Create service instance
        self.service = SimpleRAGService(
            document_store=self.mock_document_store,
            embeddings_service=self.mock_embeddings_service,
            vector_store=self.mock_vector_store,
            claude_client=self.mock_claude_client,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_service_initialization(self):
        """Test that SimpleRAGService initializes correctly."""
        assert self.service.document_store == self.mock_document_store
        assert self.service.embeddings_service == self.mock_embeddings_service
        assert self.service.vector_store == self.mock_vector_store
        assert self.service.claude_client == self.mock_claude_client

    def test_service_initialization_with_default_claude_client(self):
        """Test initialization with default Claude client."""
        service = SimpleRAGService(
            document_store=self.mock_document_store,
            embeddings_service=self.mock_embeddings_service,
            vector_store=self.mock_vector_store,
            claude_client=None,
        )

        assert service.claude_client is not None
        # The default client should be configured properly
        assert hasattr(service.claude_client, "create_chat_completion")

    @pytest.mark.asyncio
    async def test_query_with_no_results(self):
        """Test query when no documents are found."""
        question = "What is the meaning of life?"

        # Mock vector store to return no results
        self.mock_vector_store.search_similar.return_value = []

        result = await self.service.query(question)

        assert result["answer"].startswith("I couldn't find relevant information")
        assert result["question"] == question
        assert result["retrieved_documents"] == []
        assert result["metadata"]["total_results"] == 0
        assert result["metadata"]["chunks_found"] == 0
        assert result["metadata"]["full_docs_found"] == 0

    @pytest.mark.asyncio
    async def test_query_with_results(self):
        """Test query with successful document retrieval."""
        question = "How does Python work?"

        # Mock retrieved documents
        mock_docs = [
            {
                "document_id": "doc1",
                "content": "Python is a programming language that is interpreted.",
                "similarity_score": 0.8,
                "is_chunk": False,
                "store_type": "notes",
            },
            {
                "document_id": "chunk1",
                "content": "Python uses dynamic typing and garbage collection.",
                "similarity_score": 0.7,
                "is_chunk": True,
                "chunk_type": "paragraph",
            },
        ]

        self.mock_vector_store.search_similar.return_value = mock_docs

        result = await self.service.query(question, max_results=5)

        # Verify embeddings service was called
        self.mock_embeddings_service.create_embedding.assert_called_once_with(question)

        # Verify vector store search was called
        self.mock_vector_store.search_similar.assert_called_once_with(
            [0.1, 0.2, 0.3, 0.4, 0.5], limit=5, store_type=None, include_chunks=True
        )

        # Verify Claude client was called
        self.mock_claude_client.create_chat_completion.assert_called_once()

        # Verify result structure
        assert result["question"] == question
        assert result["answer"] == "This is a test response from Claude."
        assert result["retrieved_documents"] == mock_docs
        assert result["metadata"]["total_results"] == 2
        assert result["metadata"]["chunks_found"] == 1
        assert result["metadata"]["full_docs_found"] == 1
        assert result["metadata"]["similarity_threshold"] == 0.1
        assert result["metadata"]["embedding_dimensions"] == 5

    @pytest.mark.asyncio
    async def test_query_with_similarity_filtering(self):
        """Test query with similarity threshold filtering."""
        question = "Test question"

        # Mock documents with different similarity scores
        mock_docs = [
            {
                "document_id": "doc1",
                "content": "High similarity content",
                "similarity_score": 0.8,
                "is_chunk": False,
            },
            {
                "document_id": "doc2",
                "content": "Low similarity content",
                "similarity_score": 0.2,
                "is_chunk": False,
            },
        ]

        self.mock_vector_store.search_similar.return_value = mock_docs

        result = await self.service.query(question, similarity_threshold=0.5)

        # Only the high similarity document should remain
        assert len(result["retrieved_documents"]) == 1
        assert result["retrieved_documents"][0]["similarity_score"] == 0.8

    @pytest.mark.asyncio
    async def test_query_with_store_type_filter(self):
        """Test query with store type filtering."""
        question = "Test question"

        result = await self.service.query(
            question, store_type="github.repos", include_chunks=False
        )

        # Verify vector store was called with correct parameters
        self.mock_vector_store.search_similar.assert_called_once_with(
            [0.1, 0.2, 0.3, 0.4, 0.5],
            limit=5,
            store_type="github.repos",
            include_chunks=False,
        )

    @pytest.mark.asyncio
    async def test_query_error_handling(self):
        """Test query error handling."""
        question = "Test question"

        # Make embeddings service raise an exception
        self.mock_embeddings_service.create_embedding.side_effect = Exception(
            "API Error"
        )

        result = await self.service.query(question)

        assert "error" in result["answer"]
        assert result["metadata"]["error"] is True
        assert result["metadata"]["error_type"] == "Exception"
        assert result["metadata"]["error_message"] == "API Error"

    @pytest.mark.asyncio
    async def test_generate_answer_with_context(self):
        """Test answer generation with document context."""
        question = "What is Python?"
        documents = [
            {
                "document_id": "doc1",
                "content": "Python is a high-level programming language",
                "similarity_score": 0.9,
            },
            {
                "document_id": "doc2",
                "content": "Python supports multiple programming paradigms",
                "similarity_score": 0.8,
            },
        ]

        result = await self.service._generate_answer_with_context(question, documents)

        assert result == "This is a test response from Claude."

        # Verify Claude was called with proper context
        call_args = self.mock_claude_client.create_chat_completion.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 1
        assert question in messages[0]["content"]
        assert "doc1" in messages[0]["content"]
        assert "Python is a high-level programming language" in messages[0]["content"]

    @pytest.mark.asyncio
    async def test_generate_answer_with_long_content_truncation(self):
        """Test answer generation with content truncation."""
        question = "Test question"
        long_content = "x" * 600  # Longer than 500 character limit

        documents = [
            {"document_id": "doc1", "content": long_content, "similarity_score": 0.9}
        ]

        await self.service._generate_answer_with_context(question, documents)

        # Verify content was truncated
        call_args = self.mock_claude_client.create_chat_completion.call_args
        messages = call_args[1]["messages"]
        context = messages[0]["content"]

        # Should contain truncated content with "..."
        assert "..." in context
        assert (
            len([line for line in context.split("\n") if "x" in line][0]) <= 503
        )  # 500 + "..."

    @pytest.mark.asyncio
    async def test_generate_answer_claude_error_handling(self):
        """Test error handling in answer generation."""
        question = "Test question"
        documents = [
            {"document_id": "doc1", "content": "test", "similarity_score": 0.9}
        ]

        # Make Claude client raise an exception
        self.mock_claude_client.create_chat_completion.side_effect = Exception(
            "Claude Error"
        )

        result = await self.service._generate_answer_with_context(question, documents)

        assert "error generating the response" in result
        assert "Claude Error" in result

    def test_get_document_count(self):
        """Test getting document count."""
        result = self.service.get_document_count()

        assert result == {"github.repos": 5, "notes": 3}
        self.mock_document_store.get_document_count.assert_called_once()

    def test_get_stats(self):
        """Test getting RAG system statistics."""
        # Configure embeddings service attributes
        self.mock_embeddings_service.model = "text-embedding-3-small"
        self.mock_embeddings_service.dimensions = 1536

        result = self.service.get_stats()

        assert "document_counts" in result
        assert "vector_store_stats" in result
        assert "embeddings_service" in result

        assert result["document_counts"] == {"github.repos": 5, "notes": 3}
        assert result["vector_store_stats"] == {"total_documents": 10}
        assert result["embeddings_service"]["model"] == "text-embedding-3-small"
        assert result["embeddings_service"]["dimensions"] == 1536

    @pytest.mark.asyncio
    async def test_query_timing_metadata(self):
        """Test that query includes timing metadata."""
        question = "Test question"

        result = await self.service.query(question)

        assert "processing_time_ms" in result["metadata"]
        assert "query_timestamp" in result["metadata"]
        assert isinstance(result["metadata"]["processing_time_ms"], int)
        assert result["metadata"]["processing_time_ms"] >= 0

        # Verify timestamp format
        timestamp = result["metadata"]["query_timestamp"]
        datetime.fromisoformat(timestamp)  # Should not raise exception

    @pytest.mark.asyncio
    async def test_query_max_results_parameter(self):
        """Test that max_results parameter is properly passed through."""
        question = "Test question"
        max_results = 10

        await self.service.query(question, max_results=max_results)

        # Verify vector store was called with correct limit
        call_args = self.mock_vector_store.search_similar.call_args[1]
        assert call_args["limit"] == max_results

    @pytest.mark.asyncio
    async def test_query_document_limit_in_context(self):
        """Test that only top 5 documents are used for context generation."""
        question = "Test question"

        # Create 7 mock documents
        mock_docs = []
        for i in range(7):
            mock_docs.append(
                {
                    "document_id": f"doc{i}",
                    "content": f"Content {i}",
                    "similarity_score": 0.8,
                }
            )

        self.mock_vector_store.search_similar.return_value = mock_docs

        await self.service.query(question)

        # Verify Claude was called with context containing only 5 documents
        call_args = self.mock_claude_client.create_chat_completion.call_args
        messages = call_args[1]["messages"]
        context = messages[0]["content"]

        # Count document references in context
        doc_count = context.count("Document ")
        assert doc_count == 5
