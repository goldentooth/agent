"""Tests for FlowExtension base class."""

from typing import Any

import pytest

from flowengine.extensions import FlowExtension


class TestFlowExtension:
    """Test FlowExtension base class functionality."""

    def test_flow_extension_creation(self):
        """Test FlowExtension can be created with basic properties."""
        extension = FlowExtension(
            name="test_extension",
            version="1.0.0",
            description="Test extension",
            enabled=True,
        )

        assert extension.name == "test_extension"
        assert extension.version == "1.0.0"
        assert extension.description == "Test extension"
        assert extension.enabled is True

    def test_flow_extension_disabled_by_default(self):
        """Test FlowExtension is disabled by default."""
        extension = FlowExtension(
            name="test_extension", version="1.0.0", description="Test extension"
        )

        assert extension.enabled is False

    def test_flow_extension_install_method(self):
        """Test FlowExtension install method."""
        extension = FlowExtension(
            name="test_extension", version="1.0.0", description="Test extension"
        )

        # Should not raise exception
        extension.install()

    def test_flow_extension_uninstall_method(self):
        """Test FlowExtension uninstall method."""
        extension = FlowExtension(
            name="test_extension", version="1.0.0", description="Test extension"
        )

        # Should not raise exception
        extension.uninstall()

    def test_flow_extension_configure_method(self):
        """Test FlowExtension configure method."""
        extension = FlowExtension(
            name="test_extension", version="1.0.0", description="Test extension"
        )

        config = {"setting1": "value1", "setting2": 42}

        # Should not raise exception
        extension.configure(config)

    def test_flow_extension_get_info_method(self):
        """Test FlowExtension get_info method."""
        extension = FlowExtension(
            name="test_extension",
            version="1.0.0",
            description="Test extension",
            enabled=True,
        )

        info = extension.get_info()

        assert isinstance(info, dict)
        assert info["name"] == "test_extension"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Test extension"
        assert info["enabled"] is True

    def test_flow_extension_get_info_includes_all_properties(self):
        """Test FlowExtension get_info includes all required properties."""
        extension = FlowExtension(
            name="advanced_extension",
            version="2.1.0",
            description="Advanced test extension",
            enabled=False,
        )

        info = extension.get_info()

        required_keys = {"name", "version", "description", "enabled"}
        assert required_keys.issubset(info.keys())

    def test_flow_extension_repr(self):
        """Test FlowExtension string representation."""
        extension = FlowExtension(
            name="repr_test", version="0.1.0", description="Test repr", enabled=True
        )

        repr_str = repr(extension)
        assert "FlowExtension" in repr_str
        assert "repr_test" in repr_str
        assert "0.1.0" in repr_str
