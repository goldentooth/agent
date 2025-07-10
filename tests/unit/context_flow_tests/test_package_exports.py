"""Tests for context_flow package exports."""

from __future__ import annotations


class TestContextFlowPackageExports:
    """Test cases for context_flow package exports."""

    def test_bridge_imports(self) -> None:
        """Test that bridge functionality can be imported from context_flow package."""
        from context_flow import (
            ContextFlowBridge,
            get_context_bridge,
            initialize_context_integration,
        )

        # Should be able to import bridge functionality
        assert ContextFlowBridge is not None
        assert get_context_bridge is not None
        assert initialize_context_integration is not None

    def test_trampoline_imports(self) -> None:
        """Test that trampoline functionality can be imported from context_flow package."""
        from context_flow import (
            FlagCombinators,
            TrampolineFlowCombinators,
            extend_flow_with_trampoline,
        )

        # Should be able to import trampoline functionality
        assert FlagCombinators is not None
        assert TrampolineFlowCombinators is not None
        assert extend_flow_with_trampoline is not None

    def test_integration_imports(self) -> None:
        """Test that integration functionality can be imported from context_flow package."""
        from context_flow import ContextFlowCombinators

        # Should be able to import integration functionality
        assert ContextFlowCombinators is not None

    def test_package_version(self) -> None:
        """Test that package version is available."""
        import context_flow

        # Should have version attribute
        assert hasattr(context_flow, "__version__")
        assert context_flow.__version__ == "0.1.0"

    def test_all_exports_available(self) -> None:
        """Test that all exports listed in __all__ are available."""
        import context_flow

        # Check that __all__ exists and contains expected exports
        assert hasattr(context_flow, "__all__")
        all_exports = context_flow.__all__

        expected_exports = {
            "ContextFlowBridge",
            "get_context_bridge",
            "initialize_context_integration",
            "FlagCombinators",
            "TrampolineFlowCombinators",
            "extend_flow_with_trampoline",
            "ContextFlowCombinators",
        }

        # All expected exports should be in __all__
        for export in expected_exports:
            assert export in all_exports

        # All exports in __all__ should be available as module attributes
        for export in all_exports:
            assert hasattr(context_flow, export)

    def test_bridge_functionality_basic(self) -> None:
        """Test basic bridge functionality works after import."""
        from context_flow import ContextFlowBridge, initialize_context_integration

        # Should be able to create bridge instance
        bridge = ContextFlowBridge()
        assert bridge is not None

        # Should be able to initialize context integration
        initialize_context_integration()  # Should not raise error
