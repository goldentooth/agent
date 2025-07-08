"""Tests for ExtensionRegistry class."""

from typing import Any

import pytest

from flowengine.extensions import ExtensionRegistry, FlowExtension


class SimpleExtension(FlowExtension):
    """Simple extension for testing."""

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize simple extension."""
        super().__init__(
            name=name, version=version, description=description, enabled=enabled
        )
        self.init_calls = 0

    def on_flow_init(self, flow_class: type) -> None:
        """Track initialization calls."""
        self.init_calls += 1


class TestExtensionRegistry:
    """Test ExtensionRegistry functionality."""

    def test_registry_initialization(self) -> None:
        """Test registry initializes correctly."""
        registry = ExtensionRegistry()

        assert registry.extensions == {}
        assert registry.enabled_extensions == set()
        assert registry.list_extensions() == []

    def test_register_extension(self) -> None:
        """Test extension registration."""
        registry = ExtensionRegistry()
        ext = SimpleExtension("test_ext")

        registry.register_extension(ext)

        assert "test_ext" in registry.extensions
        assert registry.extensions["test_ext"] is ext
        assert "test_ext" in registry.enabled_extensions  # Should be enabled by default

    def test_register_duplicate_extension(self) -> None:
        """Test registering duplicate extension raises error."""
        registry = ExtensionRegistry()
        ext1 = SimpleExtension("test_ext")
        ext2 = SimpleExtension("test_ext")

        registry.register_extension(ext1)

        with pytest.raises(ValueError, match="Extension 'test_ext' already registered"):
            registry.register_extension(ext2)

    def test_unregister_extension(self) -> None:
        """Test extension unregistration."""
        registry = ExtensionRegistry()
        ext = SimpleExtension("test_ext")

        registry.register_extension(ext)
        registry.unregister_extension("test_ext")

        assert "test_ext" not in registry.extensions
        assert "test_ext" not in registry.enabled_extensions

    def test_unregister_nonexistent_extension(self) -> None:
        """Test unregistering nonexistent extension raises error."""
        registry = ExtensionRegistry()

        with pytest.raises(ValueError, match="Extension 'nonexistent' not found"):
            registry.unregister_extension("nonexistent")

    def test_enable_extension(self) -> None:
        """Test enabling an extension."""
        registry = ExtensionRegistry()
        ext = SimpleExtension("test_ext")
        ext.enabled = False  # Start disabled

        registry.register_extension(ext)
        assert "test_ext" not in registry.enabled_extensions

        registry.enable("test_ext")

        assert ext.enabled is True
        assert "test_ext" in registry.enabled_extensions

    def test_enable_nonexistent_extension(self) -> None:
        """Test enabling nonexistent extension raises error."""
        registry = ExtensionRegistry()

        with pytest.raises(ValueError, match="Extension 'nonexistent' not found"):
            registry.enable("nonexistent")

    def test_disable_extension(self) -> None:
        """Test disabling an extension."""
        registry = ExtensionRegistry()
        ext = SimpleExtension("test_ext")

        registry.register_extension(ext)
        assert "test_ext" in registry.enabled_extensions

        registry.disable("test_ext")

        assert ext.enabled is False
        assert "test_ext" not in registry.enabled_extensions

    def test_disable_nonexistent_extension(self) -> None:
        """Test disabling nonexistent extension raises error."""
        registry = ExtensionRegistry()

        with pytest.raises(ValueError, match="Extension 'nonexistent' not found"):
            registry.disable("nonexistent")

    def test_list_extensions(self) -> None:
        """Test listing extensions."""
        registry = ExtensionRegistry()

        # Add some extensions
        ext1 = SimpleExtension("ext1")
        ext1.enabled = True

        ext2 = SimpleExtension("ext2")
        ext2.enabled = False

        registry.register_extension(ext1)
        registry.register_extension(ext2)

        extensions = registry.list_extensions()

        assert len(extensions) == 2
        assert any(e["name"] == "ext1" and e["enabled"] is True for e in extensions)
        assert any(e["name"] == "ext2" and e["enabled"] is False for e in extensions)

    def test_list_extensions_with_descriptions(self) -> None:
        """Test listing extensions includes descriptions."""
        registry = ExtensionRegistry()

        class DescribedExtension(SimpleExtension):
            @property
            def description(self) -> str:
                return "Test extension with description"

        ext = DescribedExtension("described")
        registry.register_extension(ext)

        extensions = registry.list_extensions()

        assert len(extensions) == 1
        assert extensions[0]["name"] == "described"
        assert extensions[0]["description"] == "Test extension with description"


class TestExtensionRegistryLegacySupport:
    """Test legacy support in ExtensionRegistry."""

    def test_register_function_extension(self) -> None:
        """Test registering function-based extensions."""
        registry = ExtensionRegistry()

        def test_func(x: int) -> int:
            return x * 2

        registry.register_function_extension("double", test_func)

        retrieved = registry.get_function_extension("double")
        assert retrieved is not None
        assert retrieved is test_func
        assert retrieved(5) == 10

    def test_register_duplicate_function_extension(self) -> None:
        """Test registering duplicate function extension raises error."""
        registry = ExtensionRegistry()

        def func1() -> None:
            pass

        def func2() -> None:
            pass

        registry.register_function_extension("test", func1)

        with pytest.raises(
            ValueError, match="Function extension 'test' already registered"
        ):
            registry.register_function_extension("test", func2)

    def test_register_method_extension(self) -> None:
        """Test registering method extensions."""
        registry = ExtensionRegistry()

        def test_method(self: Any) -> str:
            return "test_method_result"

        registry.register_method_extension("test_method", test_method)

        # Methods are applied via extend_flow_class
        assert "test_method" in registry.get_method_extensions()

    def test_register_duplicate_method_extension(self) -> None:
        """Test registering duplicate method extension raises error."""
        registry = ExtensionRegistry()

        def method1(self: Any) -> None:
            pass

        def method2(self: Any) -> None:
            pass

        registry.register_method_extension("test", method1)

        with pytest.raises(
            ValueError, match="Method extension 'test' already registered"
        ):
            registry.register_method_extension("test", method2)

    def test_register_initialization_hook(self) -> None:
        """Test registering initialization hooks."""
        registry = ExtensionRegistry()

        hook_calls: list[type] = []

        def hook(flow_class: type) -> None:
            hook_calls.append(flow_class)

        registry.register_initialization_hook(hook)

        assert len(registry.get_initialization_hooks()) == 1

        # Test hook is called during extend_flow_class
        class TestFlow:
            pass

        registry.extend_flow_class(TestFlow)

        assert len(hook_calls) == 1
        assert hook_calls[0] is TestFlow

    def _create_test_registry(self) -> ExtensionRegistry:
        """Create a registry with test extensions."""
        registry = ExtensionRegistry()

        # Add FlowExtension
        ext = SimpleExtension("test_ext")

        class ExtWithMethods(SimpleExtension):
            def get_methods(self) -> dict[str, Any]:
                def ext_method(self: Any) -> str:
                    return "from_extension"

                return {"ext_method": ext_method}

        ext_with_methods = ExtWithMethods("methods_ext")
        registry.register_extension(ext)
        registry.register_extension(ext_with_methods)

        # Add legacy method extension
        def legacy_method(self: Any) -> str:
            return "from_legacy"

        registry.register_method_extension("legacy_method", legacy_method)

        # Add initialization hook
        def init_hook(flow_class: type) -> None:
            flow_class.hook_attribute = "from_hook"  # type: ignore[attr-defined]

        registry.register_initialization_hook(init_hook)

        return registry

    def test_extend_flow_class_comprehensive(self) -> None:
        """Test comprehensive flow class extension."""
        registry = self._create_test_registry()

        # Create and extend a flow class
        class TestFlow:
            pass

        registry.extend_flow_class(TestFlow)

        # Verify all extensions were applied
        assert hasattr(TestFlow, "ext_method")
        assert hasattr(TestFlow, "legacy_method")
        assert hasattr(TestFlow, "hook_attribute")

        # Verify methods work
        instance = TestFlow()
        assert getattr(TestFlow, "ext_method")(instance) == "from_extension"
        assert getattr(TestFlow, "legacy_method")(instance) == "from_legacy"
        assert getattr(TestFlow, "hook_attribute") == "from_hook"
