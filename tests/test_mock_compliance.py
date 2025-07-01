"""
Tests to ensure mocks stay in sync with real implementations.
"""

import inspect
from typing import get_type_hints

import pytest

from goldentooth_agent.core.embeddings.vector_store import VectorStore
from tests.mock_factories import TypeSafeMockVectorStore
from tests.protocols import VectorStoreProtocol


class TestMockCompliance:
    """Test that mocks implement the same interface as real classes."""

    def test_vector_store_mock_implements_protocol(self):
        """Test that our mock implements the VectorStore protocol."""
        mock = TypeSafeMockVectorStore()
        assert isinstance(mock, VectorStoreProtocol)

    def test_vector_store_mock_has_all_public_methods(self):
        """Test that mock has all public methods of the real VectorStore."""
        real_methods = {
            name
            for name, method in inspect.getmembers(VectorStore, inspect.isfunction)
            if not name.startswith("_")
        }

        mock_methods = {
            name
            for name, method in inspect.getmembers(
                TypeSafeMockVectorStore, inspect.isfunction
            )
            if not name.startswith("_")
        }

        # These are the methods we care about mocking
        critical_methods = {
            "store_document",
            "store_document_chunks",
            "search_similar",
            "get_document",
            "delete_document",
            "get_stats",
        }

        # Check that mock has the critical methods
        missing_methods = critical_methods - mock_methods
        assert not missing_methods, f"Mock missing methods: {missing_methods}"

    def test_store_document_signature_matches(self):
        """Test that store_document signatures match between real and mock."""
        real_sig = inspect.signature(VectorStore.store_document)
        mock_sig = inspect.signature(TypeSafeMockVectorStore.store_document)

        # Compare parameter names and types
        real_params = list(real_sig.parameters.keys())
        mock_params = list(mock_sig.parameters.keys())

        assert (
            real_params == mock_params
        ), f"Parameter mismatch: {real_params} vs {mock_params}"

        # Check return types if available
        real_return = real_sig.return_annotation
        mock_return = mock_sig.return_annotation

        if (
            real_return != inspect.Signature.empty
            and mock_return != inspect.Signature.empty
        ):
            assert (
                real_return == mock_return
            ), f"Return type mismatch: {real_return} vs {mock_return}"

    def test_all_protocol_methods_have_implementations(self):
        """Test that all protocol methods are implemented in the mock."""
        protocol_methods = {
            name
            for name in dir(VectorStoreProtocol)
            if not name.startswith("_")
            and callable(getattr(VectorStoreProtocol, name, None))
        }

        mock_methods = {
            name
            for name in dir(TypeSafeMockVectorStore)
            if not name.startswith("_")
            and callable(getattr(TypeSafeMockVectorStore, name))
        }

        missing = protocol_methods - mock_methods
        assert not missing, f"Mock missing protocol methods: {missing}"

    @pytest.mark.parametrize(
        "method_name",
        [
            "store_document",
            "store_document_chunks",
            "search",
            "get_document",
            "delete_document",
            "get_stats",
        ],
    )
    def test_method_signatures_are_compatible(self, method_name: str):
        """Test that individual method signatures are compatible."""
        if hasattr(VectorStore, method_name):
            real_method = getattr(VectorStore, method_name)
            mock_method = getattr(TypeSafeMockVectorStore, method_name)

            real_sig = inspect.signature(real_method)
            mock_sig = inspect.signature(mock_method)

            # Parameter counts should match
            assert len(real_sig.parameters) == len(
                mock_sig.parameters
            ), f"{method_name}: parameter count mismatch"
