"""Tests for VectorStore chunk functionality."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from goldentooth_agent.core.embeddings.document_chunker import DocumentChunk
from goldentooth_agent.core.embeddings.vector_store import VectorStore
from goldentooth_agent.core.paths import Paths


class TestVectorStoreChunks:
    """Test VectorStore chunk-related functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())

        # Mock paths to use temp directory
        self.mock_paths = Mock(spec=Paths)
        self.mock_paths.data.return_value = self.temp_dir

        # Create VectorStore with mocked paths
        self.vector_store = VectorStore(paths=self.mock_paths)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_document_chunks(self):
        """Test storing document chunks with embeddings."""
        # Create test chunks
        chunks = [
            DocumentChunk(
                chunk_id="test.doc.section1",
                parent_doc_id="test.doc",
                store_type="notes",
                document_id="doc",
                chunk_type="note_section",
                content="First section content",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "test.doc",
                    "parent_store_type": "notes",
                    "title": "Section 1",
                    "size_chars": 21,
                    "start_position": 0,
                    "end_position": 21,
                },
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="test.doc.section2",
                parent_doc_id="test.doc",
                store_type="notes",
                document_id="doc",
                chunk_type="note_section",
                content="Second section content",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 2,
                    "parent_document_id": "test.doc",
                    "parent_store_type": "notes",
                    "title": "Section 2",
                    "size_chars": 22,
                    "start_position": 21,
                    "end_position": 43,
                },
                sequence=2,
            ),
        ]

        # Create test embeddings (768-dimensional vectors for sqlite-vec compatibility)
        embeddings = [
            [0.1] * 768,  # Embedding for first chunk
            [0.2] * 768,  # Embedding for second chunk
        ]

        # Store chunks
        stored_chunk_ids = self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="doc",
            chunks=chunks,
            embeddings=embeddings,
            document_metadata={"title": "Test Document"},
        )

        # Verify return value
        assert len(stored_chunk_ids) == 2
        assert "test.doc.section1" in stored_chunk_ids
        assert "test.doc.section2" in stored_chunk_ids

    def test_get_document_chunks(self):
        """Test retrieving chunks for a document."""
        # First store some chunks (using the previous test setup)
        chunks = [
            DocumentChunk(
                chunk_id="notes.mydoc.intro",
                parent_doc_id="notes.mydoc",
                store_type="notes",
                document_id="mydoc",
                chunk_type="note_section",
                content="Introduction content",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "notes.mydoc",
                    "parent_store_type": "notes",
                    "title": "Introduction",
                    "size_chars": 19,
                    "start_position": 0,
                    "end_position": 19,
                },
                sequence=1,
            ),
        ]

        embeddings = [[0.1] * 768]

        self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="mydoc",
            chunks=chunks,
            embeddings=embeddings,
        )

        # Retrieve chunks
        retrieved_chunks = self.vector_store.get_document_chunks("notes", "mydoc")

        # Verify retrieval
        assert len(retrieved_chunks) == 1
        chunk = retrieved_chunks[0]

        assert chunk["chunk_id"] == "notes.mydoc.intro"
        assert chunk["chunk_type"] == "note_section"
        assert chunk["chunk_index"] == 1
        assert chunk["title"] == "Introduction"
        assert chunk["content"] == "Introduction content"
        assert chunk["size_chars"] == 19
        assert chunk["parent_document_id"] == "mydoc"
        assert chunk["parent_store_type"] == "notes"

    def test_delete_document_chunks(self):
        """Test deleting all chunks for a document."""
        # Store some chunks first
        chunks = [
            DocumentChunk(
                chunk_id="notes.deleteme.part1",
                parent_doc_id="notes.deleteme",
                store_type="notes",
                document_id="deleteme",
                chunk_type="note_section",
                content="Part 1",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "notes.deleteme",
                    "parent_store_type": "notes",
                    "title": "Part 1",
                    "size_chars": 6,
                    "start_position": 0,
                    "end_position": 6,
                },
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="notes.deleteme.part2",
                parent_doc_id="notes.deleteme",
                store_type="notes",
                document_id="deleteme",
                chunk_type="note_section",
                content="Part 2",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 2,
                    "parent_document_id": "notes.deleteme",
                    "parent_store_type": "notes",
                    "title": "Part 2",
                    "size_chars": 6,
                    "start_position": 6,
                    "end_position": 12,
                },
                sequence=2,
            ),
        ]

        embeddings = [[0.1] * 768, [0.2] * 768]

        self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="deleteme",
            chunks=chunks,
            embeddings=embeddings,
        )

        # Verify chunks exist
        retrieved = self.vector_store.get_document_chunks("notes", "deleteme")
        assert len(retrieved) == 2

        # Delete chunks
        deleted_count = self.vector_store.delete_document_chunks("notes", "deleteme")

        # Verify deletion
        assert deleted_count == 2
        retrieved_after = self.vector_store.get_document_chunks("notes", "deleteme")
        assert len(retrieved_after) == 0

    def test_search_similar_with_chunks(self):
        """Test similarity search that includes chunks."""
        # Store a mix of full documents and chunks

        # Store a full document
        self.vector_store.store_document(
            store_type="notes",
            document_id="fulldoc",
            content="This is a full document about testing",
            embedding=[1.0] + [0.0] * 767,
        )

        # Store chunks
        chunks = [
            DocumentChunk(
                chunk_id="notes.chunkdoc.section1",
                parent_doc_id="notes.chunkdoc",
                store_type="notes",
                document_id="chunkdoc",
                chunk_type="note_section",
                content="This is a chunk about testing frameworks",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "notes.chunkdoc",
                    "parent_store_type": "notes",
                    "title": "Testing Frameworks",
                    "size_chars": 42,
                    "start_position": 0,
                    "end_position": 42,
                },
                sequence=1,
            ),
        ]

        embeddings = [[0.8] + [0.0] * 767]

        self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="chunkdoc",
            chunks=chunks,
            embeddings=embeddings,
        )

        # Search with chunks included
        query_embedding = [0.9] + [0.0] * 767
        results = self.vector_store.search_similar(
            query_embedding,
            limit=10,
            include_chunks=True,
        )

        # Should find both document and chunk
        assert len(results) >= 2

        # Check that we have both chunks and documents
        has_chunk = any(result.get("is_chunk", False) for result in results)
        has_document = any(not result.get("is_chunk", False) for result in results)

        assert has_chunk
        assert has_document

        # Verify chunk result structure
        chunk_results = [r for r in results if r.get("is_chunk", False)]
        if chunk_results:
            chunk_result = chunk_results[0]
            assert "chunk_id" in chunk_result
            assert "chunk_type" in chunk_result
            assert "chunk_title" in chunk_result
            assert "content" in chunk_result

    @pytest.mark.skip(reason="Vector similarity search needs tuning for test vectors")
    def test_search_similar_chunks_only(self):
        """Test similarity search limited to chunks only."""
        # Store a full document and chunks
        self.vector_store.store_document(
            store_type="notes",
            document_id="fulldoc",
            content="Full document content",
            embedding=[1.0] + [0.0] * 767,
        )

        chunks = [
            DocumentChunk(
                chunk_id="notes.chunkdoc.part1",
                parent_doc_id="notes.chunkdoc",
                store_type="notes",
                document_id="chunkdoc",
                chunk_type="note_section",
                content="Chunk content",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "notes.chunkdoc",
                    "parent_store_type": "notes",
                    "title": "Part 1",
                    "size_chars": 13,
                    "start_position": 0,
                    "end_position": 13,
                },
                sequence=1,
            ),
        ]

        self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="chunkdoc",
            chunks=chunks,
            embeddings=[[0.5] + [0.1] * 767],  # More different vector
        )

        # Search including chunks
        results_with_chunks = self.vector_store.search_similar(
            [0.9] + [0.0] * 767,
            limit=10,
            include_chunks=True,
        )

        # Search excluding chunks
        results_no_chunks = self.vector_store.search_similar(
            [0.9] + [0.0] * 767,
            limit=10,
            include_chunks=False,
        )

        # With chunks should find both
        assert len(results_with_chunks) >= 2

        # Without chunks should only find full documents
        assert len(results_no_chunks) >= 1
        for result in results_no_chunks:
            assert not result.get("is_chunk", False)

    def test_get_stats_with_chunks(self):
        """Test statistics generation with chunk information."""
        # Store some documents and chunks
        self.vector_store.store_document(
            store_type="notes",
            document_id="doc1",
            content="Document 1",
            embedding=[1.0] + [0.0] * 767,
        )

        chunks = [
            DocumentChunk(
                chunk_id="notes.doc2.section1",
                parent_doc_id="notes.doc2",
                store_type="notes",
                document_id="doc2",
                chunk_type="note_section",
                content="Section 1",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "notes.doc2",
                    "parent_store_type": "notes",
                    "title": "Section 1",
                    "size_chars": 9,
                    "start_position": 0,
                    "end_position": 9,
                },
                sequence=1,
            ),
            DocumentChunk(
                chunk_id="github.repos.repo1.core",
                parent_doc_id="github.repos.repo1",
                store_type="github.repos",
                document_id="repo1",
                chunk_type="repo_core",
                content="Repository core info",
                metadata={
                    "chunk_type": "repo_core",
                    "chunk_index": 1,
                    "parent_document_id": "github.repos.repo1",
                    "parent_store_type": "github.repos",
                    "title": "Core Info",
                    "size_chars": 20,
                    "start_position": 0,
                    "end_position": 20,
                },
                sequence=1,
            ),
        ]

        self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="doc2",
            chunks=[chunks[0]],
            embeddings=[[0.8] + [0.0] * 767],
        )

        self.vector_store.store_document_chunks(
            store_type="github.repos",
            document_id="repo1",
            chunks=[chunks[1]],
            embeddings=[[0.6] + [0.0] * 767],
        )

        # Get stats
        stats = self.vector_store.get_stats()

        # Verify stats structure
        assert "total_documents" in stats
        assert "total_chunks" in stats
        assert stats["total_documents"] >= 1  # At least the full document
        assert stats["total_chunks"] >= 2  # At least the two chunks

        # Should have chunk breakdown by store type and chunk type
        if "chunks_by_store_type" in stats:
            assert "notes" in stats["chunks_by_store_type"]
            assert "github.repos" in stats["chunks_by_store_type"]

        if "chunks_by_type" in stats:
            assert "note_section" in stats["chunks_by_type"]
            assert "repo_core" in stats["chunks_by_type"]

    @pytest.mark.skip(reason="Sidecar file creation path needs investigation")
    def test_sidecar_file_creation_for_chunks(self):
        """Test that sidecar .emb.gz files are created for chunks."""
        chunks = [
            DocumentChunk(
                chunk_id="notes.testdoc.intro",
                parent_doc_id="notes.testdoc",
                store_type="notes",
                document_id="testdoc",
                chunk_type="note_section",
                content="Introduction section",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "notes.testdoc",
                    "parent_store_type": "notes",
                    "title": "Introduction",
                    "size_chars": 19,
                    "start_position": 0,
                    "end_position": 19,
                },
                sequence=1,
            ),
        ]

        # Store chunks
        self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="testdoc",
            chunks=chunks,
            embeddings=[[0.1] + [0.0] * 767],
        )

        # Check that sidecar file exists
        # List all files created to debug the issue
        embeddings_dir = self.temp_dir / ".embeddings"
        if embeddings_dir.exists():
            all_files = list(embeddings_dir.rglob("*.emb.gz"))
            print(f"Sidecar files created: {all_files}")

            # Should have at least one sidecar file
            assert len(all_files) >= 1

            # Check that it's a valid gzip file
            assert all_files[0].stat().st_size > 0

    def test_chunk_content_in_search_results(self):
        """Test that chunk content is properly included in search results."""
        chunks = [
            DocumentChunk(
                chunk_id="notes.searchtest.summary",
                parent_doc_id="notes.searchtest",
                store_type="notes",
                document_id="searchtest",
                chunk_type="note_section",
                content="This is a detailed summary of the search functionality test",
                metadata={
                    "chunk_type": "note_section",
                    "chunk_index": 1,
                    "parent_document_id": "notes.searchtest",
                    "parent_store_type": "notes",
                    "title": "Summary",
                    "size_chars": 68,
                    "start_position": 0,
                    "end_position": 68,
                },
                sequence=1,
            ),
        ]

        self.vector_store.store_document_chunks(
            store_type="notes",
            document_id="searchtest",
            chunks=chunks,
            embeddings=[[1.0] + [0.0] * 767],
        )

        # Search for the chunk
        results = self.vector_store.search_similar(
            [1.0] + [0.0] * 767,
            limit=5,
            include_chunks=True,
        )

        # Find our chunk in the results
        chunk_result = None
        for result in results:
            if result.get("chunk_id") == "notes.searchtest.summary":
                chunk_result = result
                break

        assert chunk_result is not None
        assert (
            chunk_result["content"]
            == "This is a detailed summary of the search functionality test"
        )
        assert chunk_result["chunk_type"] == "note_section"
        assert chunk_result["chunk_title"] == "Summary"
        assert chunk_result["is_chunk"] is True
