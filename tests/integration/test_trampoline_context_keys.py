"""Tests for context_flow.trampoline context key constants."""

import pytest

from context.key import ContextKey


class TestShouldExitKey:
    """Test cases for SHOULD_EXIT_KEY constant."""

    def test_should_exit_key_import(self) -> None:
        """Test that SHOULD_EXIT_KEY can be imported from trampoline module."""
        # This test will fail until SHOULD_EXIT_KEY is implemented
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Verify it's a ContextKey instance
        assert isinstance(SHOULD_EXIT_KEY, ContextKey)

    def test_should_exit_key_path(self) -> None:
        """Test that SHOULD_EXIT_KEY has correct path."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Verify the key path follows the pattern
        assert SHOULD_EXIT_KEY.path == "flow.trampoline.should_exit"

    def test_should_exit_key_type(self) -> None:
        """Test that SHOULD_EXIT_KEY has correct type."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Verify the key stores boolean values
        assert SHOULD_EXIT_KEY.type_ is bool

    def test_should_exit_key_description(self) -> None:
        """Test that SHOULD_EXIT_KEY has proper description."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Verify it has documentation
        assert SHOULD_EXIT_KEY.description is not None
        assert len(SHOULD_EXIT_KEY.description.strip()) > 0
        assert "exit" in SHOULD_EXIT_KEY.description.lower()

    def test_should_exit_key_immutable(self) -> None:
        """Test that SHOULD_EXIT_KEY is immutable."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # ContextKey instances should be immutable
        original_path = SHOULD_EXIT_KEY.path
        original_type = SHOULD_EXIT_KEY.type_
        original_desc = SHOULD_EXIT_KEY.description

        # Verify attributes exist and haven't changed
        assert SHOULD_EXIT_KEY.path == original_path
        assert SHOULD_EXIT_KEY.type_ == original_type
        assert SHOULD_EXIT_KEY.description == original_desc

    def test_should_exit_key_context_integration(self) -> None:
        """Test that SHOULD_EXIT_KEY works with Context objects."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Create a context and test key usage
        context = Context()

        # Test setting value
        context[SHOULD_EXIT_KEY.path] = True
        assert context[SHOULD_EXIT_KEY.path] is True

        # Test getting value with default
        assert context.get(SHOULD_EXIT_KEY.path, False) is True

        # Test with False value
        context[SHOULD_EXIT_KEY.path] = False
        assert context[SHOULD_EXIT_KEY.path] is False

    def test_should_exit_key_default_behavior(self) -> None:
        """Test SHOULD_EXIT_KEY default behavior with Context."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Create empty context
        context = Context()

        # Test default value behavior
        assert context.get(SHOULD_EXIT_KEY.path, False) is False

        # Test that key doesn't exist initially
        with pytest.raises(KeyError):
            _ = context[SHOULD_EXIT_KEY.path]

    def test_should_exit_key_type_safety(self) -> None:
        """Test that SHOULD_EXIT_KEY enforces type safety."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_EXIT_KEY

        context = Context()

        # Test valid boolean values
        context[SHOULD_EXIT_KEY.path] = True
        assert context[SHOULD_EXIT_KEY.path] is True

        context[SHOULD_EXIT_KEY.path] = False
        assert context[SHOULD_EXIT_KEY.path] is False

        # The context key itself doesn't enforce type at runtime,
        # but the type annotation should be correct
        assert SHOULD_EXIT_KEY.type_ is bool

    def test_should_exit_key_string_representation(self) -> None:
        """Test SHOULD_EXIT_KEY string representation."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Test string representation (ContextKey.__str__ returns the path)
        str_repr = str(SHOULD_EXIT_KEY)
        assert str_repr == "flow.trampoline.should_exit"

    def test_should_exit_key_equality(self) -> None:
        """Test SHOULD_EXIT_KEY equality behavior."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Test identity
        assert SHOULD_EXIT_KEY is SHOULD_EXIT_KEY

        # Test equality with itself
        assert SHOULD_EXIT_KEY == SHOULD_EXIT_KEY

        # Test hash consistency
        assert hash(SHOULD_EXIT_KEY) == hash(SHOULD_EXIT_KEY)

    def test_should_exit_key_constant_pattern(self) -> None:
        """Test that SHOULD_EXIT_KEY follows expected constant patterns."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Test naming convention
        assert SHOULD_EXIT_KEY.path.startswith("flow.trampoline.")
        assert SHOULD_EXIT_KEY.path.endswith("should_exit")

        # Test type consistency
        assert SHOULD_EXIT_KEY.type_ is bool

        # Test documentation exists
        assert isinstance(SHOULD_EXIT_KEY.description, str)
        assert len(SHOULD_EXIT_KEY.description) > 0

    def test_should_exit_key_export_pattern(self) -> None:
        """Test that SHOULD_EXIT_KEY follows proper export patterns."""
        # Test direct import
        from context_flow.trampoline import SHOULD_EXIT_KEY

        assert SHOULD_EXIT_KEY is not None

        # Test module-level access
        import context_flow.trampoline as trampoline_module

        assert hasattr(trampoline_module, "SHOULD_EXIT_KEY")
        assert getattr(trampoline_module, "SHOULD_EXIT_KEY") is SHOULD_EXIT_KEY

    def test_should_exit_key_context_path_uniqueness(self) -> None:
        """Test that SHOULD_EXIT_KEY has a unique context path."""
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Verify the path is specific to trampoline exit functionality
        path = SHOULD_EXIT_KEY.path
        assert path == "flow.trampoline.should_exit"

        # Verify path components
        path_parts = path.split(".")
        assert len(path_parts) == 3
        assert path_parts[0] == "flow"
        assert path_parts[1] == "trampoline"
        assert path_parts[2] == "should_exit"

    def test_should_exit_key_functional_usage(self) -> None:
        """Test SHOULD_EXIT_KEY in functional programming patterns."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_EXIT_KEY

        # Test immutable context patterns
        context1 = Context()
        context1[SHOULD_EXIT_KEY.path] = False

        # Test context forking preserves values
        context2 = context1.fork()
        assert context2[SHOULD_EXIT_KEY.path] is False

        # Test that changes to one don't affect the other
        context2[SHOULD_EXIT_KEY.path] = True
        assert context1[SHOULD_EXIT_KEY.path] is False
        assert context2[SHOULD_EXIT_KEY.path] is True


class TestShouldBreakKey:
    """Test cases for SHOULD_BREAK_KEY constant."""

    def test_should_break_key_import(self) -> None:
        """Test that SHOULD_BREAK_KEY can be imported from trampoline module."""
        # This test will fail until SHOULD_BREAK_KEY is implemented
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Verify it's a ContextKey instance
        assert isinstance(SHOULD_BREAK_KEY, ContextKey)

    def test_should_break_key_path(self) -> None:
        """Test that SHOULD_BREAK_KEY has correct path."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Verify the key path follows the pattern
        assert SHOULD_BREAK_KEY.path == "flow.trampoline.should_break"

    def test_should_break_key_type(self) -> None:
        """Test that SHOULD_BREAK_KEY has correct type."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Verify the key stores boolean values
        assert SHOULD_BREAK_KEY.type_ is bool

    def test_should_break_key_description(self) -> None:
        """Test that SHOULD_BREAK_KEY has proper description."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Verify it has documentation
        assert SHOULD_BREAK_KEY.description is not None
        assert len(SHOULD_BREAK_KEY.description.strip()) > 0
        assert "break" in SHOULD_BREAK_KEY.description.lower()

    def test_should_break_key_immutable(self) -> None:
        """Test that SHOULD_BREAK_KEY is immutable."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # ContextKey instances should be immutable
        original_path = SHOULD_BREAK_KEY.path
        original_type = SHOULD_BREAK_KEY.type_
        original_desc = SHOULD_BREAK_KEY.description

        # Verify attributes exist and haven't changed
        assert SHOULD_BREAK_KEY.path == original_path
        assert SHOULD_BREAK_KEY.type_ == original_type
        assert SHOULD_BREAK_KEY.description == original_desc

    def test_should_break_key_context_integration(self) -> None:
        """Test that SHOULD_BREAK_KEY works with Context objects."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Create a context and test key usage
        context = Context()

        # Test setting value
        context[SHOULD_BREAK_KEY.path] = True
        assert context[SHOULD_BREAK_KEY.path] is True

        # Test getting value with default
        assert context.get(SHOULD_BREAK_KEY.path, False) is True

        # Test with False value
        context[SHOULD_BREAK_KEY.path] = False
        assert context[SHOULD_BREAK_KEY.path] is False

    def test_should_break_key_default_behavior(self) -> None:
        """Test SHOULD_BREAK_KEY default behavior with Context."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Create empty context
        context = Context()

        # Test default value behavior
        assert context.get(SHOULD_BREAK_KEY.path, False) is False

        # Test that key doesn't exist initially
        with pytest.raises(KeyError):
            _ = context[SHOULD_BREAK_KEY.path]

    def test_should_break_key_type_safety(self) -> None:
        """Test that SHOULD_BREAK_KEY enforces type safety."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_BREAK_KEY

        context = Context()

        # Test valid boolean values
        context[SHOULD_BREAK_KEY.path] = True
        assert context[SHOULD_BREAK_KEY.path] is True

        context[SHOULD_BREAK_KEY.path] = False
        assert context[SHOULD_BREAK_KEY.path] is False

        # The context key itself doesn't enforce type at runtime,
        # but the type annotation should be correct
        assert SHOULD_BREAK_KEY.type_ is bool

    def test_should_break_key_string_representation(self) -> None:
        """Test SHOULD_BREAK_KEY string representation."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Test string representation (ContextKey.__str__ returns the path)
        str_repr = str(SHOULD_BREAK_KEY)
        assert str_repr == "flow.trampoline.should_break"

    def test_should_break_key_equality(self) -> None:
        """Test SHOULD_BREAK_KEY equality behavior."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Test identity
        assert SHOULD_BREAK_KEY is SHOULD_BREAK_KEY

        # Test equality with itself
        assert SHOULD_BREAK_KEY == SHOULD_BREAK_KEY

        # Test hash consistency
        assert hash(SHOULD_BREAK_KEY) == hash(SHOULD_BREAK_KEY)

    def test_should_break_key_constant_pattern(self) -> None:
        """Test that SHOULD_BREAK_KEY follows expected constant patterns."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Test naming convention
        assert SHOULD_BREAK_KEY.path.startswith("flow.trampoline.")
        assert SHOULD_BREAK_KEY.path.endswith("should_break")

        # Test type consistency
        assert SHOULD_BREAK_KEY.type_ is bool

        # Test documentation exists
        assert isinstance(SHOULD_BREAK_KEY.description, str)
        assert len(SHOULD_BREAK_KEY.description) > 0

    def test_should_break_key_export_pattern(self) -> None:
        """Test that SHOULD_BREAK_KEY follows proper export patterns."""
        # Test direct import
        from context_flow.trampoline import SHOULD_BREAK_KEY

        assert SHOULD_BREAK_KEY is not None

        # Test module-level access
        import context_flow.trampoline as trampoline_module

        assert hasattr(trampoline_module, "SHOULD_BREAK_KEY")
        assert getattr(trampoline_module, "SHOULD_BREAK_KEY") is SHOULD_BREAK_KEY

    def test_should_break_key_context_path_uniqueness(self) -> None:
        """Test that SHOULD_BREAK_KEY has a unique context path."""
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Verify the path is specific to trampoline break functionality
        path = SHOULD_BREAK_KEY.path
        assert path == "flow.trampoline.should_break"

        # Verify path components
        path_parts = path.split(".")
        assert len(path_parts) == 3
        assert path_parts[0] == "flow"
        assert path_parts[1] == "trampoline"
        assert path_parts[2] == "should_break"

    def test_should_break_key_functional_usage(self) -> None:
        """Test SHOULD_BREAK_KEY in functional programming patterns."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_BREAK_KEY

        # Test immutable context patterns
        context1 = Context()
        context1[SHOULD_BREAK_KEY.path] = False

        # Test context forking preserves values
        context2 = context1.fork()
        assert context2[SHOULD_BREAK_KEY.path] is False

        # Test that changes to one don't affect the other
        context2[SHOULD_BREAK_KEY.path] = True
        assert context1[SHOULD_BREAK_KEY.path] is False
        assert context2[SHOULD_BREAK_KEY.path] is True

    def test_should_break_key_distinct_from_exit_key(self) -> None:
        """Test that SHOULD_BREAK_KEY is distinct from SHOULD_EXIT_KEY."""
        from context_flow.trampoline import SHOULD_BREAK_KEY, SHOULD_EXIT_KEY

        # Test they are different objects
        assert SHOULD_BREAK_KEY is not SHOULD_EXIT_KEY

        # Test they have different paths
        assert SHOULD_BREAK_KEY.path != SHOULD_EXIT_KEY.path
        assert SHOULD_BREAK_KEY.path == "flow.trampoline.should_break"
        assert SHOULD_EXIT_KEY.path == "flow.trampoline.should_exit"

        # Test they have different purposes but same type
        assert SHOULD_BREAK_KEY.type_ is bool
        assert SHOULD_EXIT_KEY.type_ is bool
        assert "break" in SHOULD_BREAK_KEY.description.lower()
        assert "exit" in SHOULD_EXIT_KEY.description.lower()


class TestShouldSkipKey:
    """Test cases for SHOULD_SKIP_KEY constant."""

    def test_should_skip_key_import(self) -> None:
        """Test that SHOULD_SKIP_KEY can be imported from trampoline module."""
        # This test will fail until SHOULD_SKIP_KEY is implemented
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Verify it's a ContextKey instance
        assert isinstance(SHOULD_SKIP_KEY, ContextKey)

    def test_should_skip_key_path(self) -> None:
        """Test that SHOULD_SKIP_KEY has correct path."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Verify the key path follows the pattern
        assert SHOULD_SKIP_KEY.path == "flow.trampoline.should_skip"

    def test_should_skip_key_type(self) -> None:
        """Test that SHOULD_SKIP_KEY has correct type."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Verify the key stores boolean values
        assert SHOULD_SKIP_KEY.type_ is bool

    def test_should_skip_key_description(self) -> None:
        """Test that SHOULD_SKIP_KEY has proper description."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Verify it has documentation
        assert SHOULD_SKIP_KEY.description is not None
        assert len(SHOULD_SKIP_KEY.description.strip()) > 0
        assert "skip" in SHOULD_SKIP_KEY.description.lower()

    def test_should_skip_key_immutable(self) -> None:
        """Test that SHOULD_SKIP_KEY is immutable."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # ContextKey instances should be immutable
        original_path = SHOULD_SKIP_KEY.path
        original_type = SHOULD_SKIP_KEY.type_
        original_desc = SHOULD_SKIP_KEY.description

        # Verify attributes exist and haven't changed
        assert SHOULD_SKIP_KEY.path == original_path
        assert SHOULD_SKIP_KEY.type_ == original_type
        assert SHOULD_SKIP_KEY.description == original_desc

    def test_should_skip_key_context_integration(self) -> None:
        """Test that SHOULD_SKIP_KEY works with Context objects."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Create a context and test key usage
        context = Context()

        # Test setting value
        context[SHOULD_SKIP_KEY.path] = True
        assert context[SHOULD_SKIP_KEY.path] is True

        # Test getting value with default
        assert context.get(SHOULD_SKIP_KEY.path, False) is True

        # Test with False value
        context[SHOULD_SKIP_KEY.path] = False
        assert context[SHOULD_SKIP_KEY.path] is False

    def test_should_skip_key_default_behavior(self) -> None:
        """Test SHOULD_SKIP_KEY default behavior with Context."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Create empty context
        context = Context()

        # Test default value behavior
        assert context.get(SHOULD_SKIP_KEY.path, False) is False

        # Test that key doesn't exist initially
        with pytest.raises(KeyError):
            _ = context[SHOULD_SKIP_KEY.path]

    def test_should_skip_key_type_safety(self) -> None:
        """Test that SHOULD_SKIP_KEY enforces type safety."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_SKIP_KEY

        context = Context()

        # Test valid boolean values
        context[SHOULD_SKIP_KEY.path] = True
        assert context[SHOULD_SKIP_KEY.path] is True

        context[SHOULD_SKIP_KEY.path] = False
        assert context[SHOULD_SKIP_KEY.path] is False

        # The context key itself doesn't enforce type at runtime,
        # but the type annotation should be correct
        assert SHOULD_SKIP_KEY.type_ is bool

    def test_should_skip_key_string_representation(self) -> None:
        """Test SHOULD_SKIP_KEY string representation."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Test string representation (ContextKey.__str__ returns the path)
        str_repr = str(SHOULD_SKIP_KEY)
        assert str_repr == "flow.trampoline.should_skip"

    def test_should_skip_key_equality(self) -> None:
        """Test SHOULD_SKIP_KEY equality behavior."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Test identity
        assert SHOULD_SKIP_KEY is SHOULD_SKIP_KEY

        # Test equality with itself
        assert SHOULD_SKIP_KEY == SHOULD_SKIP_KEY

        # Test hash consistency
        assert hash(SHOULD_SKIP_KEY) == hash(SHOULD_SKIP_KEY)

    def test_should_skip_key_constant_pattern(self) -> None:
        """Test that SHOULD_SKIP_KEY follows expected constant patterns."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Test naming convention
        assert SHOULD_SKIP_KEY.path.startswith("flow.trampoline.")
        assert SHOULD_SKIP_KEY.path.endswith("should_skip")

        # Test type consistency
        assert SHOULD_SKIP_KEY.type_ is bool

        # Test documentation exists
        assert isinstance(SHOULD_SKIP_KEY.description, str)
        assert len(SHOULD_SKIP_KEY.description) > 0

    def test_should_skip_key_export_pattern(self) -> None:
        """Test that SHOULD_SKIP_KEY follows proper export patterns."""
        # Test direct import
        from context_flow.trampoline import SHOULD_SKIP_KEY

        assert SHOULD_SKIP_KEY is not None

        # Test module-level access
        import context_flow.trampoline as trampoline_module

        assert hasattr(trampoline_module, "SHOULD_SKIP_KEY")
        assert getattr(trampoline_module, "SHOULD_SKIP_KEY") is SHOULD_SKIP_KEY

    def test_should_skip_key_context_path_uniqueness(self) -> None:
        """Test that SHOULD_SKIP_KEY has a unique context path."""
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Verify the path is specific to trampoline skip functionality
        path = SHOULD_SKIP_KEY.path
        assert path == "flow.trampoline.should_skip"

        # Verify path components
        path_parts = path.split(".")
        assert len(path_parts) == 3
        assert path_parts[0] == "flow"
        assert path_parts[1] == "trampoline"
        assert path_parts[2] == "should_skip"

    def test_should_skip_key_functional_usage(self) -> None:
        """Test SHOULD_SKIP_KEY in functional programming patterns."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Test immutable context patterns
        context1 = Context()
        context1[SHOULD_SKIP_KEY.path] = False

        # Test context forking preserves values
        context2 = context1.fork()
        assert context2[SHOULD_SKIP_KEY.path] is False

        # Test that changes to one don't affect the other
        context2[SHOULD_SKIP_KEY.path] = True
        assert context1[SHOULD_SKIP_KEY.path] is False
        assert context2[SHOULD_SKIP_KEY.path] is True

    def test_should_skip_key_distinct_from_other_keys(self) -> None:
        """Test that SHOULD_SKIP_KEY is distinct from other control keys."""
        from context_flow.trampoline import (
            SHOULD_BREAK_KEY,
            SHOULD_EXIT_KEY,
            SHOULD_SKIP_KEY,
        )

        # Test they are different objects
        assert SHOULD_SKIP_KEY is not SHOULD_EXIT_KEY
        assert SHOULD_SKIP_KEY is not SHOULD_BREAK_KEY

        # Test they have different paths
        assert SHOULD_SKIP_KEY.path != SHOULD_EXIT_KEY.path
        assert SHOULD_SKIP_KEY.path != SHOULD_BREAK_KEY.path
        assert SHOULD_SKIP_KEY.path == "flow.trampoline.should_skip"
        assert SHOULD_EXIT_KEY.path == "flow.trampoline.should_exit"
        assert SHOULD_BREAK_KEY.path == "flow.trampoline.should_break"

        # Test they have different purposes but same type
        assert SHOULD_SKIP_KEY.type_ is bool
        assert SHOULD_EXIT_KEY.type_ is bool
        assert SHOULD_BREAK_KEY.type_ is bool
        assert "skip" in SHOULD_SKIP_KEY.description.lower()
        assert "exit" in SHOULD_EXIT_KEY.description.lower()
        assert "break" in SHOULD_BREAK_KEY.description.lower()

    def test_should_skip_key_semantic_usage(self) -> None:
        """Test SHOULD_SKIP_KEY semantic usage patterns."""
        from context.main import Context
        from context_flow.trampoline import SHOULD_SKIP_KEY

        # Test typical skip patterns
        context = Context()

        # Test maintenance mode pattern
        context[SHOULD_SKIP_KEY.path] = True
        assert context.get(SHOULD_SKIP_KEY.path, False) is True

        # Test normal operation pattern
        context[SHOULD_SKIP_KEY.path] = False
        assert context.get(SHOULD_SKIP_KEY.path, False) is False

        # Test conditional skip logic
        def should_skip_operation(ctx: Context) -> bool:
            return bool(ctx.get(SHOULD_SKIP_KEY.path, False))

        context[SHOULD_SKIP_KEY.path] = True
        assert should_skip_operation(context) is True

        context[SHOULD_SKIP_KEY.path] = False
        assert should_skip_operation(context) is False

    def test_all_trampoline_keys_complete_set(self) -> None:
        """Test that all three trampoline control keys form a complete set."""
        from context_flow.trampoline import (
            SHOULD_BREAK_KEY,
            SHOULD_EXIT_KEY,
            SHOULD_SKIP_KEY,
        )

        # Test we have all three keys
        all_keys = [SHOULD_EXIT_KEY, SHOULD_BREAK_KEY, SHOULD_SKIP_KEY]
        assert len(all_keys) == 3

        # Test all have same type
        for key in all_keys:
            assert key.type_ is bool

        # Test all have trampoline namespace
        for key in all_keys:
            assert key.path.startswith("flow.trampoline.")

        # Test all paths are unique
        paths = [key.path for key in all_keys]
        assert len(set(paths)) == 3

        # Test specific paths
        expected_paths = {
            "flow.trampoline.should_exit",
            "flow.trampoline.should_break",
            "flow.trampoline.should_skip",
        }
        actual_paths = set(paths)
        assert actual_paths == expected_paths
