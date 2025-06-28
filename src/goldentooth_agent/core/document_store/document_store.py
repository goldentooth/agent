from pathlib import Path
from typing import Any, Dict, Generic, List, TypeVar

from antidote import inject, injectable

from ..paths import Paths
from ..schemas import (
    GitHubOrgAdapter,
    GitHubRepoAdapter,
    GoldentoothNodeAdapter, 
    GoldentoothServiceAdapter,
    NoteAdapter,
)
from ..yaml_store import YamlStore, YamlStoreAdapter

T = TypeVar("T")


@injectable
class DocumentStore:
    """Centralized document store managing all knowledge base YAML documents."""
    
    def __init__(self, paths: Paths = inject.me()) -> None:
        """Initialize the document store with platform-appropriate data directory."""
        self.paths = paths
        self.data_dir = paths.data()
        
        # Initialize stores for each document type
        self._github_orgs: YamlStore = YamlStore(
            self.data_dir / "github" / "orgs", GitHubOrgAdapter
        )
        self._github_repos: YamlStore = YamlStore(
            self.data_dir / "github" / "repos", GitHubRepoAdapter
        )
        self._goldentooth_nodes: YamlStore = YamlStore(
            self.data_dir / "goldentooth" / "nodes", GoldentoothNodeAdapter
        )
        self._goldentooth_services: YamlStore = YamlStore(
            self.data_dir / "goldentooth" / "services", GoldentoothServiceAdapter
        )
        self._notes: YamlStore = YamlStore(
            self.data_dir / "notes", NoteAdapter
        )
    
    # GitHub Organization Management
    @property
    def github_orgs(self) -> YamlStore:
        """Access to GitHub organizations store."""
        return self._github_orgs
    
    # GitHub Repository Management  
    @property
    def github_repos(self) -> YamlStore:
        """Access to GitHub repositories store."""
        return self._github_repos
    
    # Goldentooth Node Management
    @property
    def goldentooth_nodes(self) -> YamlStore:
        """Access to Goldentooth nodes store."""
        return self._goldentooth_nodes
    
    # Goldentooth Service Management
    @property
    def goldentooth_services(self) -> YamlStore:
        """Access to Goldentooth services store."""
        return self._goldentooth_services
    
    # Notes Management
    @property
    def notes(self) -> YamlStore:
        """Access to notes store."""
        return self._notes
    
    def list_all_documents(self) -> Dict[str, List[str]]:
        """List all documents across all stores.
        
        Returns:
            Dictionary mapping store type to list of document IDs
        """
        return {
            "github.orgs": self.github_orgs.list(),
            "github.repos": self.github_repos.list(),
            "goldentooth.nodes": self.goldentooth_nodes.list(),
            "goldentooth.services": self.goldentooth_services.list(),
            "notes": self.notes.list(),
        }
    
    def get_document_count(self) -> Dict[str, int]:
        """Get count of documents in each store.
        
        Returns:
            Dictionary mapping store type to document count
        """
        return {
            store_type: len(documents)
            for store_type, documents in self.list_all_documents().items()
        }
    
    def get_store_paths(self) -> Dict[str, Path]:
        """Get the file system paths for each document store.
        
        Returns:
            Dictionary mapping store type to directory path
        """
        return {
            "github.orgs": self._github_orgs.directory,
            "github.repos": self._github_repos.directory,
            "goldentooth.nodes": self._goldentooth_nodes.directory,
            "goldentooth.services": self._goldentooth_services.directory,
            "notes": self._notes.directory,
        }
    
    def document_exists(self, store_type: str, document_id: str) -> bool:
        """Check if a document exists in a specific store.
        
        Args:
            store_type: Type of store (e.g., "github.orgs", "notes")
            document_id: ID of the document
            
        Returns:
            True if document exists, False otherwise
            
        Raises:
            ValueError: If store_type is invalid
        """
        store = self._get_store_by_type(store_type)
        return store.exists(document_id)
    
    def get_document_path(self, store_type: str, document_id: str) -> Path:
        """Get the file system path for a specific document.
        
        Args:
            store_type: Type of store
            document_id: ID of the document
            
        Returns:
            Path to the YAML file
            
        Raises:
            ValueError: If store_type is invalid
        """
        store = self._get_store_by_type(store_type)
        return store.directory / f"{document_id}.yaml"
    
    def delete_document(self, store_type: str, document_id: str) -> None:
        """Delete a document from a specific store.
        
        Args:
            store_type: Type of store
            document_id: ID of the document to delete
            
        Raises:
            ValueError: If store_type is invalid
        """
        store = self._get_store_by_type(store_type)
        store.delete(document_id)
    
    def _get_store_by_type(self, store_type: str) -> YamlStore:
        """Get a store instance by its type string.
        
        Args:
            store_type: Type of store
            
        Returns:
            YamlStore instance
            
        Raises:
            ValueError: If store_type is invalid
        """
        store_map = {
            "github.orgs": self._github_orgs,
            "github.repos": self._github_repos,
            "goldentooth.nodes": self._goldentooth_nodes,
            "goldentooth.services": self._goldentooth_services,
            "notes": self._notes,
        }
        
        if store_type not in store_map:
            valid_types = ", ".join(store_map.keys())
            raise ValueError(f"Invalid store type '{store_type}'. Valid types: {valid_types}")
        
        return store_map[store_type]
    
    def get_all_document_paths(self) -> List[Path]:
        """Get paths to all YAML documents across all stores.
        
        Returns:
            List of paths to all YAML files
        """
        paths = []
        for store_type, document_ids in self.list_all_documents().items():
            for document_id in document_ids:
                paths.append(self.get_document_path(store_type, document_id))
        return paths
    
    def clear_all_documents(self) -> Dict[str, int]:
        """Clear all documents from all stores (for testing/reset).
        
        Returns:
            Dictionary mapping store type to number of documents deleted
        """
        deleted_counts = {}
        
        for store_type, document_ids in self.list_all_documents().items():
            count = len(document_ids)
            for document_id in document_ids:
                self.delete_document(store_type, document_id)
            deleted_counts[store_type] = count
        
        return deleted_counts