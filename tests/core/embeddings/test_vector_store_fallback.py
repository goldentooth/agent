"""Tests for VectorStore fallback table handling and consistency."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from goldentooth_agent.core.embeddings import VectorStore
from goldentooth_agent.core.paths import Paths


class TestVectorStoreFallback:
    """Test VectorStore fallback behavior and vec0/fallback consistency."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "test_data"

        # Mock the Paths dependency
        self.mock_paths = Mock(spec=Paths)
        self.mock_paths.data.return_value = self.data_path

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_fallback_mode_forced(self):
        """Test vector store operations when forced to use fallback table."""
        # Create vector store that will use fallback
        vector_store = VectorStore(self.mock_paths)

        # Force fallback by making vec0 operations fail
        with patch(
            "sqlite_vec.serialize_float32",
            side_effect=sqlite3.OperationalError("vec0 not available"),
        ):
            # Test document storage
            doc_id = vector_store.store_document(
                store_type="test",
                document_id="fallback_doc",
                content="Test document for fallback",
                embedding=[0.1] * 1536,
                metadata={"test": True},
            )

            assert doc_id == "test.fallback_doc"

            # Test document retrieval
            retrieved = vector_store.get_document(doc_id)
            assert retrieved is not None
            assert retrieved["content"] == "Test document for fallback"

            # Test search functionality
            results = vector_store.search_similar([0.1] * 1536, limit=5)
            assert len(results) == 1
            assert results[0]["doc_id"] == doc_id

    def test_vec0_vs_fallback_consistency(self):
        """Test that vec0 and fallback tables produce consistent results."""
        # Test data
        test_docs = [
            {
                "store_type": "test",
                "document_id": "doc1",
                "content": "Machine learning with Python",
                "embedding": [1.0, 0.0] + [0.0] * 1534,
            },
            {
                "store_type": "test",
                "document_id": "doc2",
                "content": "Web development with JavaScript",
                "embedding": [0.0, 1.0] + [0.0] * 1534,
            },
        ]

        # Store in vec0 mode (if available)
        vec0_store = VectorStore(self.mock_paths)
        vec0_results = []

        try:
            for doc in test_docs:
                vec0_store.store_document(**doc)

            # Search with vec0
            query_embedding = [0.8, 0.2] + [0.0] * 1534
            vec0_results = vec0_store.search_similar(query_embedding, limit=10)
        except sqlite3.OperationalError:
            # vec0 not available, skip comparison
            pytest.skip("sqlite-vec extension not available for comparison")

        # Create fresh store for fallback mode
        fallback_store = VectorStore(self.mock_paths)

        # Force fallback mode
        with patch(
            "sqlite_vec.serialize_float32",
            side_effect=sqlite3.OperationalError("Forced fallback"),
        ):
            for doc in test_docs:
                fallback_store.store_document(**doc)

            # Search with fallback
            fallback_results = fallback_store.search_similar(query_embedding, limit=10)

        # Compare results (if vec0 was available)
        if vec0_results:
            assert len(vec0_results) == len(fallback_results)

            # Results should have same documents (order may differ slightly)
            vec0_doc_ids = {r["doc_id"] for r in vec0_results}
            fallback_doc_ids = {r["doc_id"] for r in fallback_results}
            assert vec0_doc_ids == fallback_doc_ids

            # Similarity scores should be reasonably close (within 10%)
            for vec0_r, fallback_r in zip(vec0_results, fallback_results, strict=False):
                if vec0_r["doc_id"] == fallback_r["doc_id"]:
                    score_diff = abs(
                        vec0_r["similarity_score"] - fallback_r["similarity_score"]
                    )
                    assert (
                        score_diff < 0.1
                    ), f"Similarity scores too different: {vec0_r['similarity_score']} vs {fallback_r['similarity_score']}"

    def test_schema_migration_fallback_table(self):
        """Test schema migration for fallback table."""
        # Create vector store to trigger table creation
        vector_store = VectorStore(self.mock_paths)

        # Check that fallback table has proper schema
        with vector_store._get_connection() as conn:
            # Force table creation by attempting an operation that will fail
            with patch(
                "sqlite_vec.serialize_float32",
                side_effect=sqlite3.OperationalError("No vec0"),
            ):
                vector_store.store_document(
                    "test", "migration_test", "Test content", [0.1] * 1536
                )

            # Verify fallback table schema
            cursor = conn.execute("PRAGMA table_info(embeddings_fallback)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}

            # Check required columns exist
            required_columns = {
                "id": "INTEGER",
                "doc_id": "TEXT",
                "store_type": "TEXT",
                "document_id": "TEXT",
                "content_preview": "TEXT",
                "embedding": "BLOB",
                "chunk_id": "TEXT",
                "is_chunk": "INTEGER",
                "created_at": "TEXT",
            }

            for col_name, col_type in required_columns.items():
                assert col_name in columns, f"Missing column: {col_name}"

    def test_mixed_storage_scenarios(self):
        """Test scenarios where data might exist in both tables."""
        vector_store = VectorStore(self.mock_paths)

        # First store with vec0 (if available)
        doc1_id = "test.mixed_doc1"
        try:
            vector_store.store_document(
                "test", "mixed_doc1", "Content in vec0", [0.1] * 1536
            )
            vec0_available = True
        except sqlite3.OperationalError:
            vec0_available = False

        # Then force fallback for another document
        with patch(
            "sqlite_vec.serialize_float32",
            side_effect=sqlite3.OperationalError("Forced fallback"),
        ):
            doc2_id = vector_store.store_document(
                "test", "mixed_doc2", "Content in fallback", [0.2] * 1536
            )

        # Both documents should be retrievable
        doc1 = vector_store.get_document(doc1_id)
        doc2 = vector_store.get_document(doc2_id)

        if vec0_available:
            assert doc1 is not None
            assert doc1["content"] == "Content in vec0"

        assert doc2 is not None
        assert doc2["content"] == "Content in fallback"

        # Search should find both documents
        results = vector_store.search_similar([0.15] * 1536, limit=10)
        found_ids = {r["doc_id"] for r in results}

        expected_ids = {doc2_id}
        if vec0_available:
            expected_ids.add(doc1_id)

        assert expected_ids.issubset(found_ids)

    def test_fallback_chunk_storage(self):
        """Test chunk storage in fallback mode."""
        from goldentooth_agent.core.embeddings.document_chunker import DocumentChunk

        vector_store = VectorStore(self.mock_paths)

        # Create test chunks
        chunks = [
            DocumentChunk(
                chunk_id="test.doc.chunk1",
                parent_doc_id="test.doc",
                store_type="test",
                document_id="doc",
                chunk_type="section",
                content="First chunk content",
                metadata={
                    "chunk_type": "section",
                    "chunk_index": 1,
                    "parent_document_id": "test.doc",
                    "parent_store_type": "test",
                    "title": "Test Section",
                    "size_chars": 19,
                    "start_position": 0,
                    "end_position": 19,
                },
                sequence=1,
            )
        ]

        embeddings = [[0.3] * 1536]

        # Force fallback mode
        with patch(
            "sqlite_vec.serialize_float32",
            side_effect=sqlite3.OperationalError("Forced fallback"),
        ):
            chunk_ids = vector_store.store_document_chunks(
                "test", "doc", chunks, embeddings, {"title": "Test Doc"}
            )

            assert len(chunk_ids) == 1
            assert "test.doc.chunk1" in chunk_ids

            # Retrieve chunks
            retrieved_chunks = vector_store.get_document_chunks("test", "doc")
            assert len(retrieved_chunks) == 1
            assert retrieved_chunks[0]["chunk_id"] == "test.doc.chunk1"
            assert retrieved_chunks[0]["content"] == "First chunk content"

    def test_stats_consistency_both_tables(self):
        """Test that stats are consistent between vec0 and fallback tables."""
        vector_store = VectorStore(self.mock_paths)

        # Store some test data in each table if possible
        test_docs = 3

        # Try to store in vec0 first
        vec0_docs = 0
        try:
            for i in range(test_docs):
                vector_store.store_document(
                    "test", f"vec0_doc{i}", f"Content {i}", [float(i)] * 1536
                )
                vec0_docs += 1
        except sqlite3.OperationalError:
            pass

        # Store in fallback
        fallback_docs = 0
        with patch(
            "sqlite_vec.serialize_float32",
            side_effect=sqlite3.OperationalError("Forced fallback"),
        ):
            for i in range(test_docs):
                vector_store.store_document(
                    "test",
                    f"fallback_doc{i}",
                    f"Fallback content {i}",
                    [float(i + 0.1)] * 1536,
                )
                fallback_docs += 1

        # Get stats
        stats = vector_store.get_stats()

        # Total should include both tables
        expected_total = vec0_docs + fallback_docs
        assert stats["total_documents"] == expected_total

        # Should have breakdown by store type
        assert "by_store_type" in stats
        assert stats["by_store_type"]["test"] == expected_total
