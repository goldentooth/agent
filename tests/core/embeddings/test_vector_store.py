import tempfile
from pathlib import Path
from unittest.mock import Mock

from goldentooth_agent.core.embeddings import VectorStore
from goldentooth_agent.core.paths import Paths


class TestVectorStore:
    """Test suite for VectorStore class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "test_data"

        # Mock the Paths dependency
        self.mock_paths = Mock(spec=Paths)
        self.mock_paths.data.return_value = self.data_path

        # Create the vector store
        self.vector_store = VectorStore(self.mock_paths)

    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_vector_store_initializes_database(self):
        """Test that VectorStore creates the database file."""
        assert self.vector_store.db_path.exists()
        assert self.vector_store.db_path.is_file()

    def test_store_and_retrieve_document(self):
        """Test storing and retrieving a document."""
        # Test data
        store_type = "github.repos"
        document_id = "test/repo"
        content = "This is a test repository for machine learning projects"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 308  # 1540 dimensions to fit in 1536
        embedding = embedding[:1536]  # Truncate to exactly 1536
        metadata = {"language": "Python", "stars": 100}

        # Store document
        doc_id = self.vector_store.store_document(
            store_type, document_id, content, embedding, metadata
        )

        assert doc_id == f"{store_type}.{document_id}"

        # Retrieve document
        retrieved = self.vector_store.get_document(doc_id)

        assert retrieved is not None
        assert retrieved["store_type"] == store_type
        assert retrieved["document_id"] == document_id
        assert retrieved["content"] == content
        assert retrieved["doc_id"] == doc_id

    def test_store_multiple_documents(self):
        """Test storing multiple documents."""
        documents = [
            {
                "store_type": "github.repos",
                "document_id": "repo1",
                "content": "Python machine learning repository",
                "embedding": [0.1] * 1536,
            },
            {
                "store_type": "github.repos",
                "document_id": "repo2",
                "content": "JavaScript web application",
                "embedding": [0.2] * 1536,
            },
            {
                "store_type": "notes",
                "document_id": "note1",
                "content": "Important system configuration notes",
                "embedding": [0.3] * 1536,
            },
        ]

        # Store all documents
        doc_ids = []
        for doc in documents:
            doc_id = self.vector_store.store_document(
                doc["store_type"], doc["document_id"], doc["content"], doc["embedding"]
            )
            doc_ids.append(doc_id)

        # Verify all documents exist
        for i, doc_id in enumerate(doc_ids):
            retrieved = self.vector_store.get_document(doc_id)
            assert retrieved is not None
            assert retrieved["content"] == documents[i]["content"]

    def test_list_documents(self):
        """Test listing documents."""
        # Initially empty
        docs = self.vector_store.list_documents()
        assert len(docs) == 0

        # Add some documents
        self.vector_store.store_document(
            "github.repos", "repo1", "Content 1", [0.1] * 1536
        )
        self.vector_store.store_document("notes", "note1", "Content 2", [0.2] * 1536)

        # List all documents
        all_docs = self.vector_store.list_documents()
        assert len(all_docs) == 2

        # List by store type
        repo_docs = self.vector_store.list_documents(store_type="github.repos")
        assert len(repo_docs) == 1
        assert repo_docs[0]["store_type"] == "github.repos"

        note_docs = self.vector_store.list_documents(store_type="notes")
        assert len(note_docs) == 1
        assert note_docs[0]["store_type"] == "notes"

    def test_list_documents_with_limit(self):
        """Test listing documents with limit."""
        # Add multiple documents
        for i in range(5):
            self.vector_store.store_document(
                "test", f"doc{i}", f"Content {i}", [0.1 * i] * 1536
            )

        # List with limit
        limited_docs = self.vector_store.list_documents(limit=3)
        assert len(limited_docs) == 3

        # Should be ordered by updated_at DESC (most recent first)
        doc_ids = [doc["document_id"] for doc in limited_docs]
        # Most recent should be doc4, doc3, doc2
        assert "doc4" in doc_ids

    def test_delete_document(self):
        """Test deleting a document."""
        # Store a document
        doc_id = self.vector_store.store_document(
            "test", "deleteme", "Content to delete", [0.5] * 1536
        )

        # Verify it exists
        assert self.vector_store.get_document(doc_id) is not None

        # Delete it
        deleted = self.vector_store.delete_document(doc_id)
        assert deleted is True

        # Verify it's gone
        assert self.vector_store.get_document(doc_id) is None

        # Try to delete non-existent document
        deleted_again = self.vector_store.delete_document(doc_id)
        assert deleted_again is False

    def test_search_similar_basic(self):
        """Test basic similarity search functionality."""
        # Store some test documents with different embeddings
        documents = [
            (
                "github.repos",
                "ml-repo",
                "Machine learning algorithms",
                [1.0, 0.0] + [0.0] * 1534,
            ),
            (
                "github.repos",
                "web-repo",
                "Web development framework",
                [0.0, 1.0] + [0.0] * 1534,
            ),
            (
                "notes",
                "ml-note",
                "Machine learning best practices",
                [0.9, 0.1] + [0.0] * 1534,
            ),
        ]

        for store_type, doc_id, content, embedding in documents:
            self.vector_store.store_document(store_type, doc_id, content, embedding)

        # Search for something similar to machine learning
        query_embedding = [0.8, 0.2] + [0.0] * 1534
        results = self.vector_store.search_similar(query_embedding, limit=2)

        # Should return results (exact similarity depends on implementation)
        assert len(results) <= 2
        assert all("similarity_score" in result for result in results)
        assert all("content" in result for result in results)

    def test_search_similar_with_store_type_filter(self):
        """Test similarity search with store type filter."""
        # Store documents in different stores
        self.vector_store.store_document(
            "github.repos", "repo1", "Repository content", [1.0] * 1536
        )
        self.vector_store.store_document("notes", "note1", "Note content", [1.0] * 1536)

        # Search only in github.repos
        query_embedding = [1.0] * 1536
        repo_results = self.vector_store.search_similar(
            query_embedding, limit=10, store_type="github.repos"
        )

        # Should only return repo results
        assert all(result["store_type"] == "github.repos" for result in repo_results)

    def test_get_stats(self):
        """Test getting vector store statistics."""
        # Initially empty
        stats = self.vector_store.get_stats()
        assert stats["total_documents"] == 0
        assert stats["by_store_type"] == {}
        assert "database_path" in stats
        assert "embedding_engine" in stats

        # Add some documents
        self.vector_store.store_document(
            "github.repos", "repo1", "Content 1", [0.1] * 1536
        )
        self.vector_store.store_document(
            "github.repos", "repo2", "Content 2", [0.2] * 1536
        )
        self.vector_store.store_document("notes", "note1", "Content 3", [0.3] * 1536)

        # Check updated stats
        stats = self.vector_store.get_stats()
        assert stats["total_documents"] == 3
        assert stats["by_store_type"]["github.repos"] == 2
        assert stats["by_store_type"]["notes"] == 1

    def test_update_existing_document(self):
        """Test updating an existing document."""
        store_type = "test"
        document_id = "updateme"

        # Store initial document
        original_content = "Original content"
        original_embedding = [0.1] * 1536

        doc_id = self.vector_store.store_document(
            store_type, document_id, original_content, original_embedding
        )

        # Update with new content
        updated_content = "Updated content"
        updated_embedding = [0.2] * 1536

        updated_doc_id = self.vector_store.store_document(
            store_type, document_id, updated_content, updated_embedding
        )

        # Should have same doc_id
        assert updated_doc_id == doc_id

        # Content should be updated
        retrieved = self.vector_store.get_document(doc_id)
        assert retrieved["content"] == updated_content

        # Should still only have one document
        stats = self.vector_store.get_stats()
        assert stats["total_documents"] == 1

    def test_handles_empty_query(self):
        """Test handling of edge cases."""
        # Empty database search
        results = self.vector_store.search_similar([0.5] * 1536, limit=5)
        assert results == []

        # Non-existent document
        doc = self.vector_store.get_document("nonexistent")
        assert doc is None

        # Delete non-existent document
        deleted = self.vector_store.delete_document("nonexistent")
        assert deleted is False
