"""Tests for context_flow.integration ContextFlowCombinators class."""

from context_flow.integration import ContextFlowCombinators


class TestContextFlowCombinators:
    """Test cases for ContextFlowCombinators class and its methods."""

    def test_context_flow_combinators_class_exists(self) -> None:
        """Test that ContextFlowCombinators class exists and can be accessed."""
        assert hasattr(ContextFlowCombinators, "get_key")
        assert callable(getattr(ContextFlowCombinators, "get_key"))
        assert hasattr(ContextFlowCombinators, "set_key")
        assert callable(getattr(ContextFlowCombinators, "set_key"))
        assert hasattr(ContextFlowCombinators, "require_key")
        assert callable(getattr(ContextFlowCombinators, "require_key"))
        assert hasattr(ContextFlowCombinators, "optional_key")
        assert callable(getattr(ContextFlowCombinators, "optional_key"))
        assert hasattr(ContextFlowCombinators, "move_key")
        assert callable(getattr(ContextFlowCombinators, "move_key"))
        assert hasattr(ContextFlowCombinators, "copy_key")
        assert callable(getattr(ContextFlowCombinators, "copy_key"))
        assert hasattr(ContextFlowCombinators, "forget_key")
        assert callable(getattr(ContextFlowCombinators, "forget_key"))
