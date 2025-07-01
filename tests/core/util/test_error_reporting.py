"""Tests for enhanced error reporting utilities."""

import pytest

from goldentooth_agent.core.util.error_reporting import (
    DetailedAttributeError,
    safe_dict_access,
    safe_getattr,
)


class TestDetailedAttributeError:
    """Test the enhanced AttributeError class."""

    def test_dict_object_error_message(self) -> None:
        """Test error message for dictionary object."""
        test_dict = {"response": "test", "metadata": {"key": "value"}}

        error = DetailedAttributeError(test_dict, "response", {"line": 42})

        assert "dict" in str(error)
        assert "response" in str(error)
        assert "['response', 'metadata']" in str(error)
        assert "line" in str(error)

    def test_object_error_message(self) -> None:
        """Test error message for regular object."""

        class TestObject:
            def __init__(self) -> None:
                self.real_attr = "value"

        obj = TestObject()
        error = DetailedAttributeError(obj, "missing_attr")

        assert "TestObject" in str(error)
        assert "missing_attr" in str(error)
        assert "['real_attr']" in str(error)

    def test_no_dict_object(self) -> None:
        """Test error message for object without __dict__."""

        error = DetailedAttributeError(42, "missing_attr")

        assert "int" in str(error)
        assert "missing_attr" in str(error)
        assert "[]" in str(error)  # Empty attributes list


class TestSafeGetattr:
    """Test the safe_getattr function."""

    def test_existing_attribute(self) -> None:
        """Test accessing existing attribute."""

        class TestObj:
            attr = "value"

        obj = TestObj()
        result = safe_getattr(obj, "attr")

        assert result == "value"

    def test_missing_attribute_with_default(self) -> None:
        """Test accessing missing attribute with default."""

        class TestObj:
            pass

        obj = TestObj()
        result = safe_getattr(obj, "missing", "default")

        assert result == "default"

    def test_missing_attribute_no_default(self) -> None:
        """Test accessing missing attribute without default raises DetailedAttributeError."""

        class TestObj:
            pass

        obj = TestObj()

        with pytest.raises(DetailedAttributeError) as exc_info:
            safe_getattr(obj, "missing")

        error = exc_info.value
        assert error.obj_type == "TestObj"
        assert error.attr_name == "missing"

    def test_with_context(self) -> None:
        """Test error includes context information."""

        obj = object()
        context = {"function": "process_response", "line": 123}

        with pytest.raises(DetailedAttributeError) as exc_info:
            safe_getattr(obj, "attr", context=context)

        assert exc_info.value.context == context


class TestSafeDictAccess:
    """Test the safe_dict_access function."""

    def test_existing_key(self) -> None:
        """Test accessing existing dictionary key."""
        test_dict = {"key": "value"}
        result = safe_dict_access(test_dict, "key")

        assert result == "value"

    def test_missing_key_with_default(self) -> None:
        """Test accessing missing key with default."""
        test_dict = {"key": "value"}
        result = safe_dict_access(test_dict, "missing", "default")

        assert result == "default"

    def test_missing_key_no_default(self) -> None:
        """Test accessing missing key without default raises DetailedAttributeError."""
        test_dict = {"key": "value"}

        with pytest.raises(DetailedAttributeError) as exc_info:
            safe_dict_access(test_dict, "missing")

        error = exc_info.value
        assert error.obj_type == "dict"
        assert error.attr_name == "missing"
        assert "['key']" in str(error)

    def test_rag_response_example(self) -> None:
        """Test with actual RAG response structure."""
        # This mimics the actual error case
        rag_response = {
            "response": "This is the answer",
            "sources": [{"doc": "test.md", "score": 0.9}],
            "confidence": 0.85,
        }

        # Safe access works
        response_text = safe_dict_access(rag_response, "response")
        assert response_text == "This is the answer"

        # Missing key with default
        suggestions = safe_dict_access(rag_response, "suggestions", [])
        assert suggestions == []

        # This would fail with standard dict.attribute access
        with pytest.raises(AttributeError):
            _ = rag_response.response  # type: ignore
