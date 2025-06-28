"""Sample data installer for demonstrating the RAG system."""

import importlib.resources
from pathlib import Path
from typing import Dict, Any

from ..document_store import DocumentStore
from ..paths import Paths
from ..yaml_store import YamlStore
from ..schemas import GitHubOrgAdapter, GitHubRepoAdapter, NoteAdapter


def install_sample_data(paths: Paths) -> Dict[str, Any]:
    """Install sample GitHub data for demonstration.
    
    Args:
        paths: Paths service for data directory management
        
    Returns:
        Dictionary with installation results
    """
    try:
        # Get the sample data directory from the package
        sample_data_package = "goldentooth_agent.data.sample_github"
        
        # Initialize document store
        document_store = DocumentStore(paths)
        
        installed_counts = {
            "github.orgs": 0,
            "github.repos": 0,  
            "notes": 0,
        }
        
        # Install GitHub organizations
        try:
            org_files = importlib.resources.files(sample_data_package).joinpath("github/orgs")
            if org_files.is_dir():
                for yaml_file in org_files.iterdir():
                    if yaml_file.name.endswith(".yaml"):
                        content = yaml_file.read_text()
                        org_id = yaml_file.stem
                        
                        # Parse and save the organization
                        import yaml
                        org_data = yaml.safe_load(content)
                        org = GitHubOrgAdapter.from_dict(org_data)
                        document_store.github_orgs.save(org_id, org)
                        installed_counts["github.orgs"] += 1
        except Exception as e:
            print(f"Warning: Could not install GitHub orgs sample data: {e}")
        
        # Install GitHub repositories
        try:
            repo_files = importlib.resources.files(sample_data_package).joinpath("github/repos")
            if repo_files.is_dir():
                for yaml_file in repo_files.iterdir():
                    if yaml_file.name.endswith(".yaml"):
                        content = yaml_file.read_text()
                        repo_id = yaml_file.stem
                        
                        # Parse and save the repository
                        import yaml
                        repo_data = yaml.safe_load(content)
                        repo = GitHubRepoAdapter.from_dict(repo_data)
                        document_store.github_repos.save(repo_id, repo)
                        installed_counts["github.repos"] += 1
        except Exception as e:
            print(f"Warning: Could not install GitHub repos sample data: {e}")
        
        # Install notes
        try:
            note_files = importlib.resources.files(sample_data_package).joinpath("notes")
            if note_files.is_dir():
                for yaml_file in note_files.iterdir():
                    if yaml_file.name.endswith(".yaml"):
                        content = yaml_file.read_text()
                        note_id = yaml_file.stem
                        
                        # Parse and save the note
                        import yaml
                        note_data = yaml.safe_load(content)
                        note = NoteAdapter.from_dict(note_data)
                        document_store.notes.save(note_id, note)
                        installed_counts["notes"] += 1
        except Exception as e:
            print(f"Warning: Could not install notes sample data: {e}")
        
        total_installed = sum(installed_counts.values())
        
        return {
            "success": True,
            "total_installed": total_installed,
            "installed_counts": installed_counts,
            "data_directory": str(paths.data()),
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_installed": 0,
            "installed_counts": {},
        }