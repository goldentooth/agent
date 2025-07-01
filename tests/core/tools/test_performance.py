"""Tests for performance tools module."""

import pytest

from goldentooth_agent.core.tools import performance


class TestPerformanceTools:
    """Test core tools performance functionality."""

    def test_module_imports(self):
        """Test that performance module imports correctly."""
        assert performance is not None

    def test_module_attributes(self):
        """Test that expected attributes exist in module."""
        assert hasattr(performance, "__file__")
