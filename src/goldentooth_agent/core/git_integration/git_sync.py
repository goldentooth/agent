"""Git integration for syncing knowledge base data to repository."""

import subprocess
from datetime import datetime
from pathlib import Path

from antidote import inject, injectable

from ..document_store import DocumentStore
from ..embeddings import VectorStore
from ..paths import Paths


@injectable
class GitDataSync:
    """Service for syncing knowledge base data to a Git repository."""

    def __init__(
        self,
        document_store: DocumentStore = inject.me(),
        vector_store: VectorStore = inject.me(),
        paths: Paths = inject.me(),
    ) -> None:
        """Initialize Git sync service.

        Args:
            document_store: Document store instance
            vector_store: Vector store instance for embeddings
            paths: Paths service for data directory
        """
        self.document_store = document_store
        self.vector_store = vector_store
        self.paths = paths
        self.data_dir = paths.data()

    def setup_git_repository(
        self, repo_path: Path, remote_url: str | None = None
    ) -> dict[str, any]:
        """Set up a Git repository for knowledge base data.

        Args:
            repo_path: Path where the Git repository should be created
            remote_url: Optional remote repository URL

        Returns:
            Dictionary with setup results
        """
        try:
            repo_path.mkdir(parents=True, exist_ok=True)

            # Initialize Git repository if it doesn't exist
            if not (repo_path / ".git").exists():
                subprocess.run(["git", "init"], cwd=repo_path, check=True)

                # Create .gitignore for vector database
                gitignore_content = """# Vector database (too large for Git)
embeddings.db
embeddings.db-*

# Cache files
*.pyc
__pycache__/
.DS_Store

# Temporary files
*.tmp
*.bak
"""
                (repo_path / ".gitignore").write_text(gitignore_content)

                # Create README
                readme_content = f"""# Goldentooth Knowledge Base

This repository contains the knowledge base data for the Goldentooth Agent system.

## Structure

- `github/orgs/` - GitHub organization metadata
- `github/repos/` - GitHub repository metadata
- `goldentooth/nodes/` - Infrastructure node configurations
- `goldentooth/services/` - Service definitions
- `notes/` - Documentation and notes

## Usage

This data is automatically synced from the Goldentooth Agent system.
Vector embeddings are stored separately and not included in this repository.

Last updated: {datetime.now().isoformat()}
"""

                (repo_path / "README.md").write_text(readme_content)

            # Add remote if provided
            if remote_url:
                try:
                    subprocess.run(
                        ["git", "remote", "add", "origin", remote_url],
                        cwd=repo_path,
                        check=True,
                    )
                except subprocess.CalledProcessError:
                    # Remote might already exist
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", remote_url],
                        cwd=repo_path,
                        check=True,
                    )

            return {
                "success": True,
                "repo_path": str(repo_path),
                "remote_url": remote_url,
                "message": "Git repository set up successfully",
            }

        except Exception as e:
            return {"success": False, "error": str(e), "repo_path": str(repo_path)}

    def sync_to_git(
        self,
        repo_path: Path,
        commit_message: str | None = None,
        push_to_remote: bool = False,
    ) -> dict[str, any]:
        """Sync current knowledge base data to Git repository.

        Args:
            repo_path: Path to the Git repository
            commit_message: Custom commit message
            push_to_remote: Whether to push to remote repository

        Returns:
            Dictionary with sync results
        """
        try:
            if not repo_path.exists() or not (repo_path / ".git").exists():
                return {
                    "success": False,
                    "error": "Git repository not found. Run setup-git-repo first.",
                }

            # Copy YAML files to Git repository
            copied_files = self._copy_yaml_files(repo_path)

            if not copied_files:
                return {
                    "success": True,
                    "message": "No changes to sync",
                    "files_copied": 0,
                }

            # Git add all changes
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )

            if not result.stdout.strip():
                return {
                    "success": True,
                    "message": "No changes to commit",
                    "files_copied": len(copied_files),
                }

            # Create commit
            if not commit_message:
                timestamp = datetime.now().isoformat()
                commit_message = f"Sync knowledge base data - {timestamp}"

            subprocess.run(
                ["git", "commit", "-m", commit_message], cwd=repo_path, check=True
            )

            # Push to remote if requested
            if push_to_remote:
                try:
                    subprocess.run(
                        ["git", "push", "origin", "main"], cwd=repo_path, check=True
                    )
                    pushed = True
                except subprocess.CalledProcessError as e:
                    # Try pushing to master if main fails
                    try:
                        subprocess.run(
                            ["git", "push", "origin", "master"],
                            cwd=repo_path,
                            check=True,
                        )
                        pushed = True
                    except subprocess.CalledProcessError:
                        pushed = False
                        push_error = str(e)
            else:
                pushed = False
                push_error = None

            return {
                "success": True,
                "files_copied": len(copied_files),
                "files_changed": (
                    result.stdout.strip().split("\n") if result.stdout.strip() else []
                ),
                "commit_message": commit_message,
                "pushed": pushed,
                "push_error": push_error,
                "repo_path": str(repo_path),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "repo_path": str(repo_path)}

    def _copy_yaml_files(self, repo_path: Path) -> list[Path]:
        """Copy YAML and embedding files from data directory to Git repository.

        Args:
            repo_path: Destination Git repository path

        Returns:
            List of copied file paths
        """
        copied_files = []

        # First, ensure all embeddings are synced to sidecar files
        self.vector_store.sync_sidecar_files()

        # Get all document store paths
        store_paths = self.document_store.get_store_paths()

        for store_type, source_dir in store_paths.items():
            if not source_dir.exists():
                continue

            # Create corresponding directory in Git repo
            if store_type.startswith("github."):
                # github.orgs -> github/orgs, github.repos -> github/repos
                dest_dir = repo_path / "github" / store_type.split(".", 1)[1]
            elif store_type.startswith("goldentooth."):
                # goldentooth.nodes -> goldentooth/nodes
                dest_dir = repo_path / "goldentooth" / store_type.split(".", 1)[1]
            else:
                # notes -> notes
                dest_dir = repo_path / store_type

            dest_dir.mkdir(parents=True, exist_ok=True)

            # Copy all YAML files
            for yaml_file in source_dir.glob("*.yaml"):
                dest_file = dest_dir / yaml_file.name
                dest_file.write_text(yaml_file.read_text())
                copied_files.append(dest_file)

            # Copy corresponding .emb.gz files
            for emb_file in source_dir.glob("*.emb.gz"):
                dest_file = dest_dir / emb_file.name
                dest_file.write_bytes(emb_file.read_bytes())
                copied_files.append(dest_file)

        # Copy embedding metadata
        metadata_source = self.paths.data() / ".embeddings" / "metadata.json"
        if metadata_source.exists():
            metadata_dest = repo_path / ".embeddings"
            metadata_dest.mkdir(parents=True, exist_ok=True)
            (metadata_dest / "metadata.json").write_text(metadata_source.read_text())
            copied_files.append(metadata_dest / "metadata.json")

        return copied_files

    def get_git_status(self, repo_path: Path) -> dict[str, any]:
        """Get Git repository status.

        Args:
            repo_path: Path to Git repository

        Returns:
            Dictionary with Git status information
        """
        try:
            if not repo_path.exists() or not (repo_path / ".git").exists():
                return {"exists": False, "error": "Git repository not found"}

            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            current_branch = branch_result.stdout.strip()

            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )

            # Count changes
            status_lines = (
                status_result.stdout.strip().split("\n")
                if status_result.stdout.strip()
                else []
            )
            modified_files = [
                line
                for line in status_lines
                if line.startswith(" M") or line.startswith("M ")
            ]
            new_files = [line for line in status_lines if line.startswith("??")]

            # Get last commit info
            try:
                log_result = subprocess.run(
                    ["git", "log", "-1", "--pretty=format:%H|%s|%ai"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                )
                if log_result.stdout:
                    commit_hash, commit_message, commit_date = log_result.stdout.split(
                        "|", 2
                    )
                else:
                    commit_hash = commit_message = commit_date = None
            except Exception:
                commit_hash = commit_message = commit_date = None

            # Check for remote
            try:
                remote_result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                )
                remote_url = (
                    remote_result.stdout.strip()
                    if remote_result.returncode == 0
                    else None
                )
            except Exception:
                remote_url = None

            return {
                "exists": True,
                "current_branch": current_branch,
                "modified_files": len(modified_files),
                "new_files": len(new_files),
                "total_changes": len(status_lines),
                "last_commit_hash": commit_hash,
                "last_commit_message": commit_message,
                "last_commit_date": commit_date,
                "remote_url": remote_url,
                "repo_path": str(repo_path),
            }

        except Exception as e:
            return {"exists": False, "error": str(e), "repo_path": str(repo_path)}
