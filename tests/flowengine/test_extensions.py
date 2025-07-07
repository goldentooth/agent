"""Tests for flowengine.extensions module."""

from typing import Any, Callable

import pytest

from flowengine.extensions import FlowExtension


class MockExtension(FlowExtension):
    """Mock extension for testing."""

    def __init__(self, name: str = "mock", description: str = "") -> None:
        """Initialize mock extension."""
        super().__init__()
        self._name = name
        self._description = description
        self.init_called_with: list[type] = []

    @property
    def name(self) -> str:
        """Extension name."""
        return self._name

    @property
    def description(self) -> str:
        """Extension description."""
        return self._description

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
            FlowExtension()  # type: ignore

    def test_flow_extension_requires_name(self) -> None:
        """Test that subclasses must implement name property."""

        class IncompleteExtension(FlowExtension):
            def on_flow_init(self, flow_class: type) -> None:
                pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteExtension()  # type: ignore

    def test_flow_extension_requires_on_flow_init(self) -> None:
        """Test that subclasses must implement on_flow_init method."""

        class IncompleteExtension(FlowExtension):
            @property
            def name(self) -> str:
                return "incomplete"

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteExtension()  # type: ignore

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
