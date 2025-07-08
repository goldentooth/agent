"""Tests for flowengine.extensions module."""

from typing import Any, Callable

import pytest

from flowengine.extensions import FlowExtension


class MockExtension(FlowExtension):
    """Mock extension for testing."""

    def __init__(
        self,
        name: str = "mock",
        version: str = "1.0.0",
        description: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize mock extension."""
        super().__init__(
            name=name, version=version, description=description, enabled=enabled
        )
        self.init_called_with: list[type] = []

    def on_flow_init(self, flow_class: type) -> None:
        """Track calls to on_flow_init."""
        self.init_called_with.append(flow_class)

    def get_methods(self) -> dict[str, Callable[..., Any]]:
        """Return test methods."""

        def test_method(self: Any) -> str:
            return "test_method_result"

        return {"test_method": test_method}


class TestFlowExtension:
    """Test FlowExtension base class."""

    def test_flow_extension_is_abstract(self) -> None:
        """Test that FlowExtension cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            FlowExtension("test")  # type: ignore[abstract]

    def test_flow_extension_requires_on_flow_init(self) -> None:
        """Test that subclasses must implement on_flow_init method."""

        class IncompleteExtension(FlowExtension):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteExtension("incomplete")  # type: ignore[abstract]

    def test_flow_extension_creation(self) -> None:
        """Test FlowExtension can be created with basic properties."""
        extension = MockExtension(
            name="test_extension",
            version="1.0.0",
            description="Test extension",
            enabled=True,
        )

        assert extension.name == "test_extension"
        assert extension.version == "1.0.0"
        assert extension.description == "Test extension"
        assert extension.enabled is True

    def test_flow_extension_enabled_by_default(self) -> None:
        """Test FlowExtension is enabled by default."""
        extension = MockExtension(name="test_extension", description="Test extension")

        assert extension.enabled is True

    def test_extension_enabled_property(self) -> None:
        """Test enabled property management."""
        ext = MockExtension()

        # Default should be enabled
        assert ext.enabled is True

        # Should be settable
        ext.enabled = False
        assert ext.enabled is False

        ext.enabled = True
        assert ext.enabled is True

    def test_extension_name_and_description(self) -> None:
        """Test name and description properties."""
        ext = MockExtension(name="test_ext", description="Test extension")

        assert ext.name == "test_ext"
        assert ext.description == "Test extension"

        # Test default description
        ext_no_desc = MockExtension(name="no_desc")
        assert ext_no_desc.description == ""

    def test_extension_on_flow_init(self) -> None:
        """Test on_flow_init is called correctly."""
        ext = MockExtension()

        class MockFlow:
            pass

        ext.on_flow_init(MockFlow)

        assert len(ext.init_called_with) == 1
        assert ext.init_called_with[0] is MockFlow

    def test_extension_get_methods(self) -> None:
        """Test get_methods returns correct methods."""
        ext = MockExtension()
        methods = ext.get_methods()

        assert isinstance(methods, dict)
        assert "test_method" in methods
        assert callable(methods["test_method"])

        # Test method execution
        class MockSelf:
            pass

        result = methods["test_method"](MockSelf())
        assert result == "test_method_result"

    def test_extension_config_management(self) -> None:
        """Test configuration get/set methods."""
        ext = MockExtension()

        # Default config should be empty
        assert ext.get_config() == {}

        # Set config
        config = {"key1": "value1", "key2": 42}
        ext.set_config(config)

        # Get config should return a copy
        retrieved = ext.get_config()
        assert retrieved == config
        assert retrieved is not config  # Should be a copy

        # Modifying retrieved should not affect internal config
        retrieved["key3"] = "value3"
        assert ext.get_config() == {"key1": "value1", "key2": 42}

        # Modifying original should not affect internal config
        config["key4"] = "value4"
        assert ext.get_config() == {"key1": "value1", "key2": 42}

    def test_flow_extension_install_method(self) -> None:
        """Test FlowExtension install method."""
        extension = MockExtension(name="test_extension", description="Test extension")

        # Should not raise exception
        extension.install()

    def test_flow_extension_uninstall_method(self) -> None:
        """Test FlowExtension uninstall method."""
        extension = MockExtension(name="test_extension", description="Test extension")

        # Should not raise exception
        extension.uninstall()

    def test_flow_extension_configure_method(self) -> None:
        """Test FlowExtension configure method."""
        extension = MockExtension(name="test_extension", description="Test extension")

        config = {"setting1": "value1", "setting2": 42}

        # Should not raise exception and should set config
        extension.configure(config)
        assert extension.get_config() == config

    def test_flow_extension_get_info_method(self) -> None:
        """Test FlowExtension get_info method."""
        extension = MockExtension(
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

    def test_flow_extension_get_info_includes_all_properties(self) -> None:
        """Test FlowExtension get_info includes all required properties."""
        extension = MockExtension(
            name="advanced_extension",
            version="2.1.0",
            description="Advanced test extension",
            enabled=False,
        )

        info = extension.get_info()

        required_keys = {"name", "version", "description", "enabled"}
        assert required_keys.issubset(info.keys())

    def test_flow_extension_repr(self) -> None:
        """Test FlowExtension string representation."""
        extension = MockExtension(
            name="repr_test", version="0.1.0", description="Test repr", enabled=True
        )

        repr_str = repr(extension)
        assert "FlowExtension" in repr_str
        assert "repr_test" in repr_str
        assert "0.1.0" in repr_str


class TestExtensionUtilities:
    """Test module-level extension utility functions."""

    def test_install_extension_function(self) -> None:
        """Test install_extension utility function."""
        # Clear any existing extensions
        from flowengine.extensions import (
            get_global_registry,
            install_extension,
            list_extensions,
        )

        registry = get_global_registry()
        registry.extensions.clear()
        registry.enabled_extensions.clear()

        ext = MockExtension(name="test_install")
        install_extension(ext)

        extensions = list_extensions()
        assert len(extensions) == 1
        assert extensions[0]["name"] == "test_install"
        assert extensions[0]["enabled"] is True

    def test_uninstall_extension_function(self) -> None:
        """Test uninstall_extension utility function."""
        # Clear any existing extensions
        from flowengine.extensions import (
            get_global_registry,
            install_extension,
            list_extensions,
            uninstall_extension,
        )

        registry = get_global_registry()
        registry.extensions.clear()
        registry.enabled_extensions.clear()

        ext = MockExtension(name="test_uninstall")
        install_extension(ext)
        assert len(list_extensions()) == 1

        uninstall_extension("test_uninstall")
        assert len(list_extensions()) == 0

    def test_uninstall_nonexistent_extension_raises_error(self) -> None:
        """Test uninstall_extension raises error for nonexistent extension."""
        from flowengine.extensions import uninstall_extension

        with pytest.raises(ValueError, match="Extension 'nonexistent' not found"):
            uninstall_extension("nonexistent")

    def test_enable_extension_function(self) -> None:
        """Test enable_extension utility function."""
        # Clear any existing extensions
        from flowengine.extensions import (
            enable_extension,
            get_global_registry,
            install_extension,
        )

        registry = get_global_registry()
        registry.extensions.clear()
        registry.enabled_extensions.clear()

        ext = MockExtension(name="test_enable", enabled=False)
        install_extension(ext)
        assert ext.enabled is False

        enable_extension("test_enable")
        assert ext.enabled is True

    def test_enable_nonexistent_extension_raises_error(self) -> None:
        """Test enable_extension raises error for nonexistent extension."""
        from flowengine.extensions import enable_extension

        with pytest.raises(ValueError, match="Extension 'nonexistent' not found"):
            enable_extension("nonexistent")

    def test_disable_extension_function(self) -> None:
        """Test disable_extension utility function."""
        # Clear any existing extensions
        from flowengine.extensions import (
            disable_extension,
            get_global_registry,
            install_extension,
        )

        registry = get_global_registry()
        registry.extensions.clear()
        registry.enabled_extensions.clear()

        ext = MockExtension(name="test_disable", enabled=True)
        install_extension(ext)
        assert ext.enabled is True

        disable_extension("test_disable")
        assert ext.enabled is False

    def test_disable_nonexistent_extension_raises_error(self) -> None:
        """Test disable_extension raises error for nonexistent extension."""
        from flowengine.extensions import disable_extension

        with pytest.raises(ValueError, match="Extension 'nonexistent' not found"):
            disable_extension("nonexistent")

    def test_list_extensions_function(self) -> None:
        """Test list_extensions utility function."""
        # Clear any existing extensions
        from flowengine.extensions import (
            get_global_registry,
            install_extension,
            list_extensions,
        )

        registry = get_global_registry()
        registry.extensions.clear()
        registry.enabled_extensions.clear()

        ext1 = MockExtension(
            name="ext1", version="1.0.0", description="First extension"
        )
        ext2 = MockExtension(
            name="ext2", version="2.0.0", description="Second extension"
        )

        install_extension(ext1)
        install_extension(ext2)

        extensions = list_extensions()
        assert len(extensions) == 2

        # Check that all expected fields are present
        for ext_info in extensions:
            assert "name" in ext_info
            assert "version" in ext_info
            assert "description" in ext_info
            assert "enabled" in ext_info

    def test_get_extension_info_function(self) -> None:
        """Test get_extension_info utility function."""
        # Clear any existing extensions
        from flowengine.extensions import (
            get_extension_info,
            get_global_registry,
            install_extension,
        )

        registry = get_global_registry()
        registry.extensions.clear()
        registry.enabled_extensions.clear()

        ext = MockExtension(
            name="test_info",
            version="1.2.3",
            description="Test extension for info",
            enabled=True,
        )
        install_extension(ext)

        info = get_extension_info("test_info")
        assert info["name"] == "test_info"
        assert info["version"] == "1.2.3"
        assert info["description"] == "Test extension for info"
        assert info["enabled"] is True

    def test_get_extension_info_nonexistent_raises_error(self) -> None:
        """Test get_extension_info raises error for nonexistent extension."""
        from flowengine.extensions import get_extension_info

        with pytest.raises(ValueError, match="Extension 'nonexistent' not found"):
            get_extension_info("nonexistent")
