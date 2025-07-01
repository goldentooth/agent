"""Tests for Claude client."""

import pytest

from goldentooth_agent.core.llm import claude_client


class TestClaudeClient:
    """Test Claude client functionality."""

    def test_module_imports(self):
        """Test that claude_client module imports correctly."""
        assert claude_client is not None

    def test_module_attributes(self):
        """Test that expected attributes exist in module."""
        assert hasattr(claude_client, "__file__")
