"""Tests for flow.integrations package initialization."""

import flow.integrations


class TestFlowIntegrationsInit:
    """Test suite for flow.integrations package initialization."""

    def test_package_imports_successfully(self) -> None:
        """Test that the package can be imported without errors."""
        # The import statement above should succeed
        assert flow.integrations is not None

    def test_all_attribute_exists(self) -> None:
        """Test that __all__ attribute exists and is a list."""
        assert hasattr(flow.integrations, "__all__")
        assert isinstance(flow.integrations.__all__, list)

    def test_all_attribute_is_empty(self) -> None:
        """Test that __all__ is initially empty as expected."""
        assert flow.integrations.__all__ == []

    def test_package_has_docstring(self) -> None:
        """Test that the package has a docstring."""
        assert flow.integrations.__doc__ is not None
        assert "Integrations package for flow" in flow.integrations.__doc__

    def test_package_name(self) -> None:
        """Test that the package has correct name."""
        assert flow.integrations.__name__ == "flow.integrations"
