"""Tests for agent response schema."""

import pytest

from goldentooth_agent.core.schema import agent_response


class TestAgentResponse:
    """Test agent response schema functionality."""

    def test_module_imports(self):
        """Test that agent_response module imports correctly."""
        assert agent_response is not None

    def test_module_attributes(self):
        """Test that expected attributes exist in module."""
        assert hasattr(agent_response, "__file__")
