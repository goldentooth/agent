"""Tests for git sync service."""

import pytest

from goldentooth_agent.core.git_integration import git_sync


class TestGitSync:
    """Test git sync functionality."""

    def test_module_imports(self):
        """Test that git_sync module imports correctly."""
        assert git_sync is not None

    def test_module_attributes(self):
        """Test that expected attributes exist in module."""
        assert hasattr(git_sync, "__file__")
