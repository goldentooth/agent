"""Tests for flowengine.protocols module."""

from typing import Any, Union

import pytest

from flowengine.protocols import ContextKeyProtocol, ContextProtocol, FlowProtocol


class TestContextKeyProtocol:
    """Test the ContextKeyProtocol."""

    def test_context_key_protocol_is_runtime_checkable(self) -> None:
        """ContextKeyProtocol should be runtime checkable."""

        # Create a concrete implementation
        class MockContextKey:
            def __init__(self, name: str, value_type: type[str]) -> None:
                super().__init__()
                self._name = name
                self._value_type = value_type

            @property
            def name(self) -> str:
                return self._name

            @property
            def value_type(self) -> type[str]:
                return self._value_type

        key = MockContextKey("test_key", str)
        assert isinstance(key, ContextKeyProtocol)

    def test_context_key_protocol_requires_name_property(self) -> None:
        """ContextKeyProtocol requires a name property."""

        class IncompleteKey:
            @property
            def value_type(self) -> type[str]:
                return str

        key = IncompleteKey()
        assert not isinstance(key, ContextKeyProtocol)

    def test_context_key_protocol_requires_value_type_property(self) -> None:
        """ContextKeyProtocol requires a value_type property."""

        class IncompleteKey:
            @property
            def name(self) -> str:
                return "test"

        key = IncompleteKey()
        assert not isinstance(key, ContextKeyProtocol)

    def test_context_key_protocol_with_different_types(self) -> None:
        """ContextKeyProtocol should work with different value types."""

        class IntKey:
            @property
            def name(self) -> str:
                return "int_key"

            @property
            def value_type(self) -> type[int]:
                return int

        class ListKey:
            @property
            def name(self) -> str:
                return "list_key"

            @property
            def value_type(self) -> type[list[str]]:
                return list

        int_key = IntKey()
        list_key = ListKey()

        assert isinstance(int_key, ContextKeyProtocol)
        assert isinstance(list_key, ContextKeyProtocol)


class TestContextProtocol:
    """Test the ContextProtocol."""

    def test_context_protocol_is_runtime_checkable(self) -> None:
        """ContextProtocol should be runtime checkable."""

        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self._data: dict[str, Any] = {}

            def get(self, key: ContextKeyProtocol[Any]) -> Any:
                return self._data[key.name]

            def set(self, key: ContextKeyProtocol[Any], value: Any) -> None:
                self._data[key.name] = value

            def contains(self, key: ContextKeyProtocol[Any]) -> bool:
                return key.name in self._data

        context = MockContext()
        assert isinstance(context, ContextProtocol)

    def test_context_protocol_requires_get_method(self) -> None:
        """ContextProtocol requires a get method."""

        class IncompleteContext:
            def set(self, key: ContextKeyProtocol[Any], value: Any) -> None:
                pass

            def contains(self, key: ContextKeyProtocol[Any]) -> bool:
                return False

        context = IncompleteContext()
        assert not isinstance(context, ContextProtocol)

    def test_context_protocol_requires_set_method(self) -> None:
        """ContextProtocol requires a set method."""

        class IncompleteContext:
            def get(self, key: ContextKeyProtocol[Any]) -> Any:
                return None

            def contains(self, key: ContextKeyProtocol[Any]) -> bool:
                return False

        context = IncompleteContext()
        assert not isinstance(context, ContextProtocol)

    def test_context_protocol_requires_contains_method(self) -> None:
        """ContextProtocol requires a contains method."""

        class IncompleteContext:
            def get(self, key: ContextKeyProtocol[Any]) -> Any:
                return None

            def set(self, key: ContextKeyProtocol[Any], value: Any) -> None:
                pass

        context = IncompleteContext()
        assert not isinstance(context, ContextProtocol)

    def test_context_protocol_complete_implementation(self) -> None:
        """Test a complete ContextProtocol implementation."""

        class MockKey:
            def __init__(self, name: str, value_type: type[Any]) -> None:
                super().__init__()
                self._name = name
                self._value_type = value_type

            @property
            def name(self) -> str:
                return self._name

            @property
            def value_type(self) -> type[Any]:
                return self._value_type

        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self._data: dict[str, Any] = {}

            def get(self, key: ContextKeyProtocol[Any]) -> Any:
                if key.name not in self._data:
                    raise KeyError(f"Key {key.name} not found")
                return self._data[key.name]

            def set(self, key: ContextKeyProtocol[Any], value: Any) -> None:
                self._data[key.name] = value

            def contains(self, key: ContextKeyProtocol[Any]) -> bool:
                return key.name in self._data

        # Test the implementation
        context = MockContext()
        key = MockKey("test_key", str)

        assert isinstance(context, ContextProtocol)
        assert isinstance(key, ContextKeyProtocol)

        # Initially key should not exist
        assert not context.contains(key)

        # Set a value
        context.set(key, "test_value")
        assert context.contains(key)
        assert context.get(key) == "test_value"


class TestFlowProtocol:
    """Test the FlowProtocol."""

    def test_flow_protocol_is_runtime_checkable(self) -> None:
        """FlowProtocol should be runtime checkable."""

        class MockFlow:
            def __init__(self, name: str) -> None:
                super().__init__()
                self._name = name

            @property
            def name(self) -> str:
                return self._name

            def __call__(self, stream: Any) -> Any:
                return stream

        flow = MockFlow("test_flow")
        assert isinstance(flow, FlowProtocol)

    def test_flow_protocol_requires_name_property(self) -> None:
        """FlowProtocol requires a name property."""

        class IncompleteFlow:
            def __call__(self, stream: Any) -> Any:
                return stream

        flow = IncompleteFlow()
        assert not isinstance(flow, FlowProtocol)

    def test_flow_protocol_requires_call_method(self) -> None:
        """FlowProtocol requires a __call__ method."""

        class IncompleteFlow:
            @property
            def name(self) -> str:
                return "test"

        flow = IncompleteFlow()
        assert not isinstance(flow, FlowProtocol)

    def test_flow_protocol_complete_implementation(self) -> None:
        """Test a complete FlowProtocol implementation."""

        class MockFlow:
            def __init__(self, name: str) -> None:
                super().__init__()
                self._name = name

            @property
            def name(self) -> str:
                return self._name

            def __call__(self, stream: list[Union[int, float]]) -> list[int]:
                # Simple transformation for testing
                result: list[int] = []
                for item in stream:
                    result.append(int(item) * 2)
                return result

        flow = MockFlow("double_flow")

        assert isinstance(flow, FlowProtocol)
        assert flow.name == "double_flow"

        # Test the call method
        result = flow([1, 2, 3])
        assert result == [2, 4, 6]


class TestProtocolInteraction:
    """Test protocol interactions and integration."""

    def test_protocols_work_together(self) -> None:
        """Test that protocols can work together in a system."""

        class StringKey:
            @property
            def name(self) -> str:
                return "string_value"

            @property
            def value_type(self) -> type[str]:
                return str

        class SimpleContext:
            def __init__(self) -> None:
                super().__init__()
                self._data: dict[str, Any] = {}

            def get(self, key: ContextKeyProtocol[Any]) -> Any:
                return self._data[key.name]

            def set(self, key: ContextKeyProtocol[Any], value: Any) -> None:
                self._data[key.name] = value

            def contains(self, key: ContextKeyProtocol[Any]) -> bool:
                return key.name in self._data

        class ContextAwareFlow:
            def __init__(self, name: str, context: ContextProtocol) -> None:
                super().__init__()
                self._name = name
                self._context = context

            @property
            def name(self) -> str:
                return self._name

            def __call__(self, stream: Any) -> Any:
                # Use context in flow execution
                key = StringKey()
                if self._context.contains(key):
                    prefix = self._context.get(key)
                    return f"{prefix}: {stream}"
                return str(stream)

        # Set up the system
        context = SimpleContext()
        key = StringKey()
        flow = ContextAwareFlow("context_flow", context)

        # Verify protocol compliance
        assert isinstance(key, ContextKeyProtocol)
        assert isinstance(context, ContextProtocol)
        assert isinstance(flow, FlowProtocol)

        # Test without context value
        result = flow("test")
        assert result == "test"

        # Test with context value
        context.set(key, "PREFIX")
        result = flow("test")
        assert result == "PREFIX: test"

    def test_protocol_type_safety(self) -> None:
        """Test that protocols maintain type safety expectations."""

        class TypedKey:
            def __init__(self, name: str, value_type: type[Any]) -> None:
                super().__init__()
                self._name = name
                self._value_type = value_type

            @property
            def name(self) -> str:
                return self._name

            @property
            def value_type(self) -> type[Any]:
                return self._value_type

        # Test with different typed keys
        str_key = TypedKey("str_key", str)
        int_key = TypedKey("int_key", int)
        list_key = TypedKey("list_key", list)

        assert isinstance(str_key, ContextKeyProtocol)
        assert isinstance(int_key, ContextKeyProtocol)
        assert isinstance(list_key, ContextKeyProtocol)

        assert str_key.value_type == str
        assert int_key.value_type == int
        assert list_key.value_type == list


class TestProtocolErrorHandling:
    """Test error handling with protocols."""

    def test_missing_protocol_methods_detected(self) -> None:
        """Test that missing protocol methods are properly detected."""

        class BadFlow:
            # Missing both name property and __call__ method
            pass

        class PartialFlow:
            # Has name but missing __call__
            @property
            def name(self) -> str:
                return "partial"

        class AnotherPartialFlow:
            # Has __call__ but missing name
            def __call__(self, stream: Any) -> Any:
                return stream

        bad_flow = BadFlow()
        partial_flow = PartialFlow()
        another_partial_flow = AnotherPartialFlow()

        assert not isinstance(bad_flow, FlowProtocol)
        assert not isinstance(partial_flow, FlowProtocol)
        assert not isinstance(another_partial_flow, FlowProtocol)

    def test_context_error_handling(self) -> None:
        """Test context protocol error handling."""

        class MockKey:
            @property
            def name(self) -> str:
                return "test_key"

            @property
            def value_type(self) -> type[str]:
                return str

        class ErrorContext:
            def get(self, _key: ContextKeyProtocol[Any]) -> Any:
                raise KeyError("Key not found")

            def set(self, _key: ContextKeyProtocol[Any], _value: Any) -> None:
                pass

            def contains(self, _key: ContextKeyProtocol[Any]) -> bool:
                return False

        context = ErrorContext()
        key = MockKey()

        assert isinstance(context, ContextProtocol)
        assert isinstance(key, ContextKeyProtocol)

        # Test that error propagates
        with pytest.raises(KeyError, match="Key not found"):
            context.get(key)
