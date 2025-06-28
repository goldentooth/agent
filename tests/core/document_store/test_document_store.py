from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import pytest

from goldentooth_agent.core.document_store import DocumentStore
from goldentooth_agent.core.paths import Paths
from goldentooth_agent.core.schemas.github import GitHubOrg, GitHubRepo
from goldentooth_agent.core.schemas.goldentooth import GoldentoothNode, GoldentoothService
from goldentooth_agent.core.schemas.notes import Note


class TestDocumentStore:
    """Test suite for DocumentStore class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "test_data"
        
        # Mock the Paths dependency
        self.mock_paths = Mock(spec=Paths)
        self.mock_paths.data.return_value = self.data_path
        
        # Create the document store
        self.store = DocumentStore(self.mock_paths)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_store_initializes_with_correct_directory_structure(self):
        """Test that DocumentStore creates the correct directory structure."""
        # Verify that data() was called on paths
        self.mock_paths.data.assert_called_once()
        
        # Verify store properties exist
        assert hasattr(self.store, "github_orgs")
        assert hasattr(self.store, "github_repos")
        assert hasattr(self.store, "goldentooth_nodes")
        assert hasattr(self.store, "goldentooth_services")
        assert hasattr(self.store, "notes")
    
    def test_store_paths_are_correct(self):
        """Test that store paths are set up correctly."""
        paths = self.store.get_store_paths()
        
        expected_paths = {
            "github.orgs": self.data_path / "github" / "orgs",
            "github.repos": self.data_path / "github" / "repos", 
            "goldentooth.nodes": self.data_path / "goldentooth" / "nodes",
            "goldentooth.services": self.data_path / "goldentooth" / "services",
            "notes": self.data_path / "notes",
        }
        
        assert paths == expected_paths
    
    def test_list_all_documents_empty_stores(self):
        """Test list_all_documents with empty stores."""
        all_docs = self.store.list_all_documents()
        
        expected = {
            "github.orgs": [],
            "github.repos": [],
            "goldentooth.nodes": [],
            "goldentooth.services": [],
            "notes": [],
        }
        
        assert all_docs == expected
    
    def test_get_document_count_empty_stores(self):
        """Test get_document_count with empty stores."""
        counts = self.store.get_document_count()
        
        expected = {
            "github.orgs": 0,
            "github.repos": 0,
            "goldentooth.nodes": 0,
            "goldentooth.services": 0,
            "notes": 0,
        }
        
        assert counts == expected
    
    def test_save_and_load_github_org(self):
        """Test saving and loading a GitHub organization."""
        org = GitHubOrg(
            id="testorg",
            name="Test Organization",
            description="A test organization",
            url="https://github.com/testorg",
            public_repos=5,
            rag_include=True
        )
        
        # Save the org
        self.store.github_orgs.save("testorg", org)
        
        # Verify it exists
        assert self.store.document_exists("github.orgs", "testorg")
        
        # Load and verify
        loaded_org = self.store.github_orgs.load("testorg")
        assert loaded_org.id == "testorg"
        assert loaded_org.name == "Test Organization"
        assert loaded_org.public_repos == 5
    
    def test_save_and_load_github_repo(self):
        """Test saving and loading a GitHub repository."""
        repo = GitHubRepo(
            id="testorg/testrepo",
            name="testrepo",
            full_name="testorg/testrepo",
            description="A test repository",
            url="https://github.com/testorg/testrepo",
            clone_url="https://github.com/testorg/testrepo.git",
            language="Python",
            topics=["test", "demo"],
            stars=10,
            rag_include=True
        )
        
        # Save the repo
        self.store.github_repos.save("testorg_testrepo", repo)
        
        # Verify it exists
        assert self.store.document_exists("github.repos", "testorg_testrepo")
        
        # Load and verify
        loaded_repo = self.store.github_repos.load("testorg_testrepo")
        assert loaded_repo.id == "testorg/testrepo"
        assert loaded_repo.name == "testrepo"
        assert loaded_repo.language == "Python"
        assert loaded_repo.topics == ["test", "demo"]
    
    def test_save_and_load_goldentooth_node(self):
        """Test saving and loading a Goldentooth node."""
        node = GoldentoothNode(
            id="node1",
            name="Test Node",
            hostname="node1.goldentooth.local",
            ip_address="192.168.1.100",
            status="online",
            role="worker",
            services=["consul", "nomad"],
            rag_include=True
        )
        
        # Save the node
        self.store.goldentooth_nodes.save("node1", node)
        
        # Verify it exists
        assert self.store.document_exists("goldentooth.nodes", "node1")
        
        # Load and verify
        loaded_node = self.store.goldentooth_nodes.load("node1")
        assert loaded_node.id == "node1"
        assert loaded_node.name == "Test Node"
        assert loaded_node.hostname == "node1.goldentooth.local"
        assert loaded_node.services == ["consul", "nomad"]
    
    def test_save_and_load_goldentooth_service(self):
        """Test saving and loading a Goldentooth service."""
        service = GoldentoothService(
            id="consul",
            name="Consul",
            description="Service discovery and configuration",
            service_type="discovery",
            port=8500,
            endpoints=["http://consul.goldentooth.local:8500"],
            nodes=["node1", "node2"],
            status="running",
            rag_include=True
        )
        
        # Save the service
        self.store.goldentooth_services.save("consul", service)
        
        # Verify it exists
        assert self.store.document_exists("goldentooth.services", "consul")
        
        # Load and verify
        loaded_service = self.store.goldentooth_services.load("consul")
        assert loaded_service.id == "consul"
        assert loaded_service.name == "Consul"
        assert loaded_service.service_type == "discovery"
        assert loaded_service.port == 8500
    
    def test_save_and_load_note(self):
        """Test saving and loading a note."""
        note = Note(
            id="test-note",
            title="Test Note",
            content="This is a test note with **markdown** support.",
            category="testing",
            tags=["test", "demo"],
            status="active",
            priority="medium",
            rag_include=True
        )
        
        # Save the note
        self.store.notes.save("test-note", note)
        
        # Verify it exists
        assert self.store.document_exists("notes", "test-note")
        
        # Load and verify
        loaded_note = self.store.notes.load("test-note")
        assert loaded_note.id == "test-note"
        assert loaded_note.title == "Test Note"
        assert loaded_note.category == "testing"
        assert loaded_note.tags == ["test", "demo"]
    
    def test_list_all_documents_with_data(self):
        """Test list_all_documents with actual data."""
        # Add some test documents
        org = GitHubOrg(id="org1", url="https://github.com/org1")
        repo = GitHubRepo(id="org1/repo1", name="repo1", full_name="org1/repo1", 
                         url="https://github.com/org1/repo1", 
                         clone_url="https://github.com/org1/repo1.git")
        note = Note(id="note1", title="Note 1", content="Test content")
        
        self.store.github_orgs.save("org1", org)
        self.store.github_repos.save("repo1", repo) 
        self.store.notes.save("note1", note)
        
        all_docs = self.store.list_all_documents()
        
        assert "org1" in all_docs["github.orgs"]
        assert "repo1" in all_docs["github.repos"]
        assert "note1" in all_docs["notes"]
        assert all_docs["goldentooth.nodes"] == []
        assert all_docs["goldentooth.services"] == []
    
    def test_get_document_count_with_data(self):
        """Test get_document_count with actual data."""
        # Add test documents
        org = GitHubOrg(id="org1", url="https://github.com/org1")
        repo1 = GitHubRepo(id="org1/repo1", name="repo1", full_name="org1/repo1",
                          url="https://github.com/org1/repo1",
                          clone_url="https://github.com/org1/repo1.git")
        repo2 = GitHubRepo(id="org1/repo2", name="repo2", full_name="org1/repo2",
                          url="https://github.com/org1/repo2", 
                          clone_url="https://github.com/org1/repo2.git")
        
        self.store.github_orgs.save("org1", org)
        self.store.github_repos.save("repo1", repo1)
        self.store.github_repos.save("repo2", repo2)
        
        counts = self.store.get_document_count()
        
        assert counts["github.orgs"] == 1
        assert counts["github.repos"] == 2
        assert counts["goldentooth.nodes"] == 0
        assert counts["goldentooth.services"] == 0
        assert counts["notes"] == 0
    
    def test_document_exists_functionality(self):
        """Test document_exists method."""
        # Initially no documents exist
        assert not self.store.document_exists("github.orgs", "nonexistent")
        
        # Add a document
        org = GitHubOrg(id="testorg", url="https://github.com/testorg")
        self.store.github_orgs.save("testorg", org)
        
        # Now it should exist
        assert self.store.document_exists("github.orgs", "testorg")
        assert not self.store.document_exists("github.orgs", "other")
    
    def test_get_document_path(self):
        """Test get_document_path method."""
        path = self.store.get_document_path("github.orgs", "testorg")
        expected = self.data_path / "github" / "orgs" / "testorg.yaml"
        assert path == expected
    
    def test_delete_document(self):
        """Test delete_document method."""
        # Add a document
        org = GitHubOrg(id="testorg", url="https://github.com/testorg")
        self.store.github_orgs.save("testorg", org)
        
        # Verify it exists
        assert self.store.document_exists("github.orgs", "testorg")
        
        # Delete it
        self.store.delete_document("github.orgs", "testorg")
        
        # Verify it's gone
        assert not self.store.document_exists("github.orgs", "testorg")
    
    def test_invalid_store_type_raises_error(self):
        """Test that invalid store types raise ValueError."""
        with pytest.raises(ValueError, match="Invalid store type"):
            self.store.document_exists("invalid.store", "doc1")
        
        with pytest.raises(ValueError, match="Invalid store type"):
            self.store.get_document_path("invalid.store", "doc1")
        
        with pytest.raises(ValueError, match="Invalid store type"):
            self.store.delete_document("invalid.store", "doc1")
    
    def test_get_all_document_paths(self):
        """Test get_all_document_paths method."""
        # Add some documents
        org = GitHubOrg(id="org1", url="https://github.com/org1")
        note = Note(id="note1", title="Note 1", content="Test")
        
        self.store.github_orgs.save("org1", org)
        self.store.notes.save("note1", note)
        
        paths = self.store.get_all_document_paths()
        
        expected_paths = [
            self.data_path / "github" / "orgs" / "org1.yaml",
            self.data_path / "notes" / "note1.yaml",
        ]
        
        assert len(paths) == 2
        assert all(path in expected_paths for path in paths)
    
    def test_clear_all_documents(self):
        """Test clear_all_documents method."""
        # Add some documents
        org = GitHubOrg(id="org1", url="https://github.com/org1")
        repo = GitHubRepo(id="org1/repo1", name="repo1", full_name="org1/repo1",
                         url="https://github.com/org1/repo1",
                         clone_url="https://github.com/org1/repo1.git")
        note = Note(id="note1", title="Note 1", content="Test")
        
        self.store.github_orgs.save("org1", org)
        self.store.github_repos.save("repo1", repo)
        self.store.notes.save("note1", note)
        
        # Verify documents exist
        assert self.store.get_document_count()["github.orgs"] == 1
        assert self.store.get_document_count()["github.repos"] == 1  
        assert self.store.get_document_count()["notes"] == 1
        
        # Clear all documents
        deleted_counts = self.store.clear_all_documents()
        
        # Verify counts
        assert deleted_counts["github.orgs"] == 1
        assert deleted_counts["github.repos"] == 1
        assert deleted_counts["notes"] == 1
        assert deleted_counts["goldentooth.nodes"] == 0
        assert deleted_counts["goldentooth.services"] == 0
        
        # Verify stores are empty
        final_counts = self.store.get_document_count()
        for count in final_counts.values():
            assert count == 0