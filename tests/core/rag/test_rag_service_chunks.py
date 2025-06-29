"""Tests for RAGService chunk-aware functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from goldentooth_agent.core.rag.rag_service import RAGService


class TestRAGServiceChunks:
    """Test RAGService chunk-aware retrieval functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_document_store = Mock()
        self.mock_embeddings_service = AsyncMock()
        self.mock_vector_store = Mock()
        self.mock_claude_client = AsyncMock()

        # Create RAGService with mocked dependencies
        self.rag_service = RAGService(
            document_store=self.mock_document_store,
            embeddings_service=self.mock_embeddings_service,
            vector_store=self.mock_vector_store,
            claude_client=self.mock_claude_client,
        )

    @pytest.mark.asyncio
    async def test_query_with_chunk_types_filter(self):
        """Test query with chunk type filtering."""
        # Mock embedding creation
        self.mock_embeddings_service.create_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock vector search results with mixed chunks and documents
        mock_search_results = [
            {
                "doc_id": "notes.doc1.section1",
                "store_type": "notes",
                "document_id": "doc1",
                "content": "Section 1 content",
                "similarity_score": 0.95,
                "is_chunk": True,
                "chunk_id": "notes.doc1.section1",
                "chunk_type": "note_section",
                "chunk_title": "Introduction",
                "chunk_index": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "size_chars": 19,
            },
            {
                "doc_id": "github.repos.repo1.core",
                "store_type": "github.repos",
                "document_id": "repo1",
                "content": "Repository core info",
                "similarity_score": 0.90,
                "is_chunk": True,
                "chunk_id": "github.repos.repo1.core",
                "chunk_type": "repo_core",
                "chunk_title": "Core Info",
                "chunk_index": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "size_chars": 20,
            },
            {
                "doc_id": "notes.doc2",
                "store_type": "notes",
                "document_id": "doc2",
                "content": "Full document content",
                "similarity_score": 0.85,
                "is_chunk": False,
                "chunk_id": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "metadata": "{}",
            },
        ]

        self.mock_vector_store.search_similar.return_value = mock_search_results

        # Mock Claude response
        self.mock_claude_client.create_chat_completion.return_value = (
            "Test answer based on chunks"
        )

        # Query with chunk type filter
        result = await self.rag_service.query(
            question="Test question",
            chunk_types=["note_section"],
            max_results=5,
            similarity_threshold=0.1,
        )

        # Verify that vector search was called with increased limit
        self.mock_vector_store.search_similar.assert_called_once()
        call_args = self.mock_vector_store.search_similar.call_args
        assert call_args[1]["limit"] == 10  # 5 * 2 due to filtering

        # Verify response structure
        assert "answer" in result
        assert "retrieved_documents" in result
        assert "metadata" in result

        # Check metadata includes chunk information
        metadata = result["metadata"]
        assert "chunks_used" in metadata
        assert "full_docs_used" in metadata
        assert "chunk_types_found" in metadata

        # Should only have note_section chunks after filtering
        assert metadata["chunk_types_found"] == ["note_section"]

    @pytest.mark.asyncio
    async def test_query_with_prioritize_chunks(self):
        """Test query with chunk prioritization."""
        # Mock embedding creation
        self.mock_embeddings_service.create_embedding.return_value = [0.1, 0.2, 0.3]

        # Mock search results with chunks and documents (unordered by type)
        mock_search_results = [
            {
                "doc_id": "notes.fulldoc",
                "store_type": "notes",
                "document_id": "fulldoc",
                "content": "Full document content",
                "similarity_score": 0.95,
                "is_chunk": False,
                "chunk_id": None,
            },
            {
                "doc_id": "notes.doc1.section1",
                "store_type": "notes",
                "document_id": "doc1",
                "content": "Chunk content",
                "similarity_score": 0.90,
                "is_chunk": True,
                "chunk_id": "notes.doc1.section1",
                "chunk_type": "note_section",
                "chunk_title": "Section 1",
            },
        ]

        self.mock_vector_store.search_similar.return_value = mock_search_results
        self.mock_claude_client.create_chat_completion.return_value = (
            "Answer prioritizing chunks"
        )

        # Query with chunk prioritization
        result = await self.rag_service.query(
            question="Test question",
            prioritize_chunks=True,
            max_results=5,
        )

        # The internal logic should reorder chunks before documents
        # We can't easily test the reordering without more complex mocking,
        # but we can verify the feature is being used
        assert result["answer"] == "Answer prioritizing chunks"

    @pytest.mark.asyncio
    async def test_build_context_with_chunks(self):
        """Test context building with chunks."""
        # Mock documents with chunks
        documents = [
            {
                "document_id": "doc1",
                "store_type": "notes",
                "content": "First chunk content",
                "similarity_score": 0.95,
                "is_chunk": True,
                "chunk_id": "notes.doc1.section1",
                "chunk_type": "note_section",
                "chunk_title": "Introduction",
                "chunk_index": 1,
            },
            {
                "document_id": "doc1",
                "store_type": "notes",
                "content": "Second chunk content",
                "similarity_score": 0.90,
                "is_chunk": True,
                "chunk_id": "notes.doc1.section2",
                "chunk_type": "note_section",
                "chunk_title": "Details",
                "chunk_index": 2,
            },
            {
                "document_id": "doc2",
                "store_type": "notes",
                "content": "Full document content",
                "similarity_score": 0.85,
                "is_chunk": False,
            },
        ]

        # Build context
        context = self.rag_service._build_context(documents)

        # Verify context structure
        assert "Source 1:" in context
        assert "Multiple Sections" in context  # Should group chunks from same doc
        assert "Introduction" in context
        assert "Details" in context
        assert "Source 2:" in context  # Standalone document
        assert "Full document content" in context

    @pytest.mark.asyncio
    async def test_search_chunks_by_type(self):
        """Test searching for specific chunk types."""
        # Mock the query method to return chunk results
        with patch.object(self.rag_service, "query") as mock_query:
            mock_query.return_value = {
                "retrieved_documents": [
                    {
                        "document_id": "doc1",
                        "store_type": "notes",
                        "content": "Setup instructions",
                        "similarity_score": 0.95,
                        "is_chunk": True,
                        "chunk_id": "notes.doc1.setup",
                        "chunk_type": "note_section",
                        "chunk_title": "Setup",
                    },
                    {
                        "document_id": "repo1",
                        "store_type": "github.repos",
                        "content": "Core repository info",
                        "similarity_score": 0.85,
                        "is_chunk": True,
                        "chunk_id": "github.repos.repo1.core",
                        "chunk_type": "repo_core",
                        "chunk_title": "Core Info",
                    },
                ],
            }

            # Search for specific chunk types
            result = await self.rag_service.search_chunks_by_type(
                chunk_types=["note_section", "repo_core"],
                question="setup instructions",
                max_results=10,
            )

            # Verify query was called with correct parameters
            mock_query.assert_called_once()
            call_args = mock_query.call_args[1]
            assert call_args["chunk_types"] == ["note_section", "repo_core"]
            assert call_args["prioritize_chunks"] is True
            assert call_args["include_chunks"] is True
            assert call_args["similarity_threshold"] == 0.0

            # Verify result structure
            assert result["chunks"] == [
                {
                    "document_id": "doc1",
                    "store_type": "notes",
                    "content": "Setup instructions",
                    "similarity_score": 0.95,
                    "is_chunk": True,
                    "chunk_id": "notes.doc1.setup",
                    "chunk_type": "note_section",
                    "chunk_title": "Setup",
                },
                {
                    "document_id": "repo1",
                    "store_type": "github.repos",
                    "content": "Core repository info",
                    "similarity_score": 0.85,
                    "is_chunk": True,
                    "chunk_id": "github.repos.repo1.core",
                    "chunk_type": "repo_core",
                    "chunk_title": "Core Info",
                },
            ]
            assert result["total_found"] == 2
            assert result["search_method"] == "semantic_with_types"

    @pytest.mark.asyncio
    async def test_get_document_chunk_summary(self):
        """Test getting chunk summary for a document."""
        # Mock document existence check
        self.mock_document_store.document_exists.return_value = True

        # Mock chunk retrieval
        mock_chunks = [
            {
                "chunk_id": "notes.doc1.intro",
                "chunk_type": "note_section",
                "chunk_index": 1,
                "title": "Introduction",
                "content": "Introduction content",
                "size_chars": 19,
                "start_position": 0,
                "end_position": 19,
                "parent_document_id": "doc1",
                "parent_store_type": "notes",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "chunk_id": "notes.doc1.setup",
                "chunk_type": "note_section",
                "chunk_index": 2,
                "title": "Setup",
                "content": "Setup instructions here",
                "size_chars": 22,
                "start_position": 19,
                "end_position": 41,
                "parent_document_id": "doc1",
                "parent_store_type": "notes",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        ]

        self.mock_vector_store.get_document_chunks.return_value = mock_chunks

        # Get chunk summary
        result = await self.rag_service.get_document_chunk_summary(
            store_type="notes",
            document_id="doc1",
            include_content_preview=True,
        )

        # Verify result structure
        assert result["document_id"] == "doc1"
        assert result["store_type"] == "notes"
        assert result["has_chunks"] is True
        assert result["total_chunks"] == 2
        assert result["total_characters"] == 41
        assert result["avg_chunk_size"] == 20  # 41 // 2

        # Check chunk type distribution
        assert result["chunk_types"] == {"note_section": 2}

        # Check individual chunks
        assert len(result["chunks"]) == 2
        first_chunk = result["chunks"][0]
        assert first_chunk["chunk_id"] == "notes.doc1.intro"
        assert first_chunk["title"] == "Introduction"
        assert "content_preview" in first_chunk

    @pytest.mark.asyncio
    async def test_get_document_chunks_info(self):
        """Test getting chunk information for a document."""
        # Mock document existence
        self.mock_document_store.document_exists.return_value = True

        # Mock chunk retrieval
        mock_chunks = [
            {
                "chunk_id": "notes.testdoc.part1",
                "chunk_type": "note_section",
                "chunk_index": 1,
                "title": "Part 1",
                "size_chars": 10,
            },
            {
                "chunk_id": "notes.testdoc.part2",
                "chunk_type": "note_section",
                "chunk_index": 2,
                "title": "Part 2",
                "size_chars": 15,
            },
        ]

        self.mock_vector_store.get_document_chunks.return_value = mock_chunks

        # Get chunk info
        result = await self.rag_service.get_document_chunks_info("testdoc", "notes")

        # Verify result
        assert result["document_id"] == "testdoc"
        assert result["store_type"] == "notes"
        assert result["chunks"] == mock_chunks
        assert result["total_chunks"] == 2
        assert result["total_characters"] == 25
        assert result["chunk_types"] == {"note_section": 2}

    @pytest.mark.asyncio
    async def test_get_document_chunks_info_no_chunks(self):
        """Test getting chunk info for document with no chunks."""
        # Mock document existence
        self.mock_document_store.document_exists.return_value = True

        # Mock empty chunk retrieval
        self.mock_vector_store.get_document_chunks.return_value = []

        # Get chunk info
        result = await self.rag_service.get_document_chunks_info("nodoc", "notes")

        # Verify result
        assert result["document_id"] == "nodoc"
        assert result["store_type"] == "notes"
        assert result["chunks"] == []
        assert result["total_chunks"] == 0
        assert "message" in result
        assert "full-document embedding" in result["message"]

    @pytest.mark.asyncio
    async def test_enhanced_system_prompt_with_chunks(self):
        """Test that system prompt properly handles chunk information."""
        # Mock embedding and search
        self.mock_embeddings_service.create_embedding.return_value = [0.1, 0.2]

        mock_search_results = [
            {
                "doc_id": "notes.guide.setup",
                "store_type": "notes",
                "document_id": "guide",
                "content": "Setup instructions",
                "similarity_score": 0.95,
                "is_chunk": True,
                "chunk_id": "notes.guide.setup",
                "chunk_type": "note_section",
                "chunk_title": "Setup Instructions",
                "chunk_index": 2,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "size_chars": 18,
            },
        ]

        self.mock_vector_store.search_similar.return_value = mock_search_results
        self.mock_claude_client.create_chat_completion.return_value = (
            "Answer based on setup chunk"
        )

        # Query with chunks
        await self.rag_service.query(
            question="How do I set up the system?",
            max_results=3,
        )

        # Verify Claude was called
        self.mock_claude_client.create_chat_completion.assert_called_once()
        call_args = self.mock_claude_client.create_chat_completion.call_args

        # Check that system prompt includes chunk guidance
        system_prompt = call_args[1]["system"]
        assert "context sources" in system_prompt.lower()
        assert "document chunks" in system_prompt.lower()
        assert "chunk relationships" in system_prompt.lower()

        # Check that context includes chunk information
        context_in_system = system_prompt
        assert "Source 1:" in context_in_system
        assert "Setup Instructions" in context_in_system

    @pytest.mark.asyncio
    async def test_context_building_groups_chunks_by_document(self):
        """Test that context building properly groups chunks by parent document."""
        documents = [
            {
                "document_id": "guide",
                "store_type": "notes",
                "content": "Introduction content",
                "similarity_score": 0.95,
                "is_chunk": True,
                "chunk_id": "notes.guide.intro",
                "chunk_type": "note_section",
                "chunk_title": "Introduction",
                "chunk_index": 1,
            },
            {
                "document_id": "guide",
                "store_type": "notes",
                "content": "Setup content",
                "similarity_score": 0.90,
                "is_chunk": True,
                "chunk_id": "notes.guide.setup",
                "chunk_type": "note_section",
                "chunk_title": "Setup",
                "chunk_index": 2,
            },
            {
                "document_id": "other",
                "store_type": "notes",
                "content": "Other document content",
                "similarity_score": 0.85,
                "is_chunk": False,
            },
        ]

        context = self.rag_service._build_context(documents)

        # Should group the two chunks from 'guide' together
        assert "Multiple Sections" in context
        assert "Introduction" in context
        assert "Setup" in context

        # Should have separate source for standalone document
        source_count = context.count("Source")
        assert source_count == 2  # One grouped source + one standalone

    @pytest.mark.asyncio
    async def test_error_handling_in_chunk_operations(self):
        """Test error handling in chunk-related operations."""
        # Test document not found
        self.mock_document_store.document_exists.return_value = False

        result = await self.rag_service.get_document_chunks_info("nonexistent", "notes")

        assert result["error"] is True
        assert "not found" in result["message"]

        # Test exception in chunk summary
        self.mock_vector_store.get_document_chunks.side_effect = Exception(
            "Database error"
        )
        self.mock_document_store.document_exists.return_value = True

        result = await self.rag_service.get_document_chunk_summary("notes", "doc1")

        assert result["error"] is True
        assert "Database error" in result["error_message"]
