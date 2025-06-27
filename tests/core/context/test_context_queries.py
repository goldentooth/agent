"""Tests for Context query and filtering capabilities."""

from __future__ import annotations

import pytest

from goldentooth_agent.core.context import Context


class TestContextQuerying:
    """Test suite for Context querying capabilities."""

    def test_query_basic(self) -> None:
        """Test basic querying functionality."""
        context = Context()

        context["name"] = "Alice"
        context["age"] = 30
        context["city"] = "New York"
        context["active"] = True

        # Query all
        all_results = context.query()
        assert len(all_results) == 4
        assert all_results["name"] == "Alice"
        assert all_results["age"] == 30

        # Query with no filters should return everything
        empty_query = context.query(None, None, None)
        assert empty_query == all_results

    def test_query_with_pattern(self) -> None:
        """Test querying with regex patterns."""
        context = Context()

        context["user_name"] = "Alice"
        context["user_age"] = 30
        context["admin_role"] = "manager"
        context["guest_access"] = False

        # Query keys starting with 'user'
        user_results = context.query(pattern=r"^user")
        assert len(user_results) == 2
        assert "user_name" in user_results
        assert "user_age" in user_results
        assert "admin_role" not in user_results

        # Query keys containing 'age'
        age_results = context.query(pattern=r"age")
        assert len(age_results) == 1
        assert "user_age" in age_results
        # Note: 'guest_access' doesn't contain 'age', it contains 'ess'

    def test_query_with_key_filter(self) -> None:
        """Test querying with key filters."""
        context = Context()

        context["short"] = "value1"
        context["medium_key"] = "value2"
        context["very_long_key_name"] = "value3"

        # Filter by key length
        short_keys = context.query(key_filter=lambda k: len(k) <= 6)
        assert len(short_keys) == 1
        assert "short" in short_keys

        long_keys = context.query(key_filter=lambda k: len(k) > 10)
        assert len(long_keys) == 1
        assert "very_long_key_name" in long_keys

    def test_query_with_value_filter(self) -> None:
        """Test querying with value filters."""
        context = Context()

        context["number1"] = 10
        context["number2"] = 25
        context["text"] = "hello"
        context["flag"] = True

        # Filter by value type (note: bool is a subclass of int in Python)
        numbers = context.query(value_filter=lambda v: isinstance(v, int))
        assert len(numbers) == 3  # number1, number2, and flag (bool is int subclass)
        assert "number1" in numbers
        assert "number2" in numbers
        assert "flag" in numbers  # bool is subclass of int

        # Filter by value range (excluding booleans)
        large_numbers = context.query(
            value_filter=lambda v: isinstance(v, int)
            and not isinstance(v, bool)
            and v > 20
        )
        assert len(large_numbers) == 1
        assert "number2" in large_numbers

    def test_query_with_computed_properties(self) -> None:
        """Test querying with computed properties."""
        context = Context()

        context["x"] = 5
        context["y"] = 10
        context.add_computed_property(
            "sum", lambda ctx: ctx.get("x", 0) + ctx.get("y", 0), ["x", "y"]
        )

        # Include computed properties
        with_computed = context.query(include_computed=True)
        assert len(with_computed) == 3
        assert "sum" in with_computed
        assert with_computed["sum"] == 15

        # Exclude computed properties
        without_computed = context.query(include_computed=False)
        assert len(without_computed) == 2
        assert "sum" not in without_computed

    def test_query_combined_filters(self) -> None:
        """Test querying with combined filters."""
        context = Context()

        context["user_score"] = 95
        context["admin_score"] = 87
        context["user_name"] = "Alice"
        context["admin_name"] = "Bob"

        # Combine pattern and value filter
        high_user_scores = context.query(
            pattern=r"^user", value_filter=lambda v: isinstance(v, int) and v > 90
        )
        assert len(high_user_scores) == 1
        assert "user_score" in high_user_scores
        assert high_user_scores["user_score"] == 95

    def test_find_keys(self) -> None:
        """Test finding keys by pattern."""
        context = Context()

        context["config_debug"] = True
        context["config_timeout"] = 30
        context["user_id"] = 123
        context["config_max_retries"] = 5

        config_keys = context.find_keys(r"^config")
        assert len(config_keys) == 3
        assert "config_debug" in config_keys
        assert "config_timeout" in config_keys
        assert "config_max_retries" in config_keys
        assert "user_id" not in config_keys

    def test_find_values(self) -> None:
        """Test finding values by predicate."""
        context = Context()

        context["small"] = 5
        context["medium"] = 50
        context["large"] = 500
        context["text"] = "hello"

        big_numbers = context.find_values(lambda v: isinstance(v, int) and v >= 50)
        assert len(big_numbers) == 2
        assert "medium" in big_numbers
        assert "large" in big_numbers
        assert "small" not in big_numbers

    def test_filter_by_type(self) -> None:
        """Test filtering by value type."""
        context = Context()

        context["count"] = 42
        context["name"] = "Alice"
        context["active"] = True
        context["score"] = 95.5
        context["items"] = [1, 2, 3]

        # Filter integers (note: bool is a subclass of int in Python)
        integers = context.filter_by_type(int)
        assert len(integers) == 2  # count and active (bool is int subclass)
        assert "count" in integers
        assert "active" in integers  # bool is subclass of int

        # Filter strings
        strings = context.filter_by_type(str)
        assert len(strings) == 1
        assert "name" in strings

        # Filter lists
        lists = context.filter_by_type(list)
        assert len(lists) == 1
        assert "items" in lists

        # Filter integers excluding booleans
        true_integers = context.query(
            value_filter=lambda v: isinstance(v, int) and not isinstance(v, bool)
        )
        assert len(true_integers) == 1
        assert "count" in true_integers
        assert "active" not in true_integers

    def test_search(self) -> None:
        """Test searching keys and values."""
        context = Context()

        context["user_name"] = "Alice Smith"
        context["admin_role"] = "Manager"
        context["user_email"] = "alice@example.com"
        context["config_timeout"] = 30

        # Search for 'user' (case insensitive by default)
        user_results = context.search("user")
        assert len(user_results) == 2
        assert "user_name" in user_results
        assert "user_email" in user_results

        # Search for 'alice' in values (case insensitive)
        alice_results = context.search("alice")
        assert len(alice_results) == 2  # user_name and user_email both contain 'alice'

        # Case sensitive search
        case_sensitive = context.search("Alice", case_sensitive=True)
        assert len(case_sensitive) == 1
        assert "user_name" in case_sensitive

        # Search for numbers (converted to string)
        number_results = context.search("30")
        assert len(number_results) == 1
        assert "config_timeout" in number_results


class TestContextNestedOperations:
    """Test suite for nested context operations."""

    def test_get_nested_basic(self) -> None:
        """Test getting nested values."""
        context = Context()

        context["user"] = {
            "profile": {"name": "Alice", "age": 30},
            "settings": {"theme": "dark"},
        }

        assert context.get_nested("user.profile.name") == "Alice"
        assert context.get_nested("user.profile.age") == 30
        assert context.get_nested("user.settings.theme") == "dark"

    def test_get_nested_custom_delimiter(self) -> None:
        """Test getting nested values with custom delimiter."""
        context = Context()

        context["data"] = {"level1": {"level2": "value"}}

        assert context.get_nested("data/level1/level2", delimiter="/") == "value"

    def test_get_nested_missing_path(self) -> None:
        """Test getting nested values with missing paths."""
        context = Context()

        context["user"] = {"name": "Alice"}

        with pytest.raises(KeyError, match="Path 'user.profile.name' not found"):
            context.get_nested("user.profile.name")

        with pytest.raises(KeyError, match="nonexistent"):
            context.get_nested("nonexistent.path")

    def test_set_nested_basic(self) -> None:
        """Test setting nested values."""
        context = Context()

        context["user"] = {}
        context.set_nested("user.profile.name", "Alice")

        assert context["user"]["profile"]["name"] == "Alice"
        assert context.get_nested("user.profile.name") == "Alice"

    def test_set_nested_create_missing(self) -> None:
        """Test setting nested values with missing intermediate paths."""
        context = Context()

        # Should create missing structure by default
        context.set_nested("deep.nested.path.value", "test")

        assert context["deep"]["nested"]["path"]["value"] == "test"
        assert context.get_nested("deep.nested.path.value") == "test"

    def test_set_nested_no_create_missing(self) -> None:
        """Test setting nested values without creating missing paths."""
        context = Context()

        with pytest.raises(KeyError, match="does not exist"):
            context.set_nested("missing.path", "value", create_missing=False)

    def test_has_nested(self) -> None:
        """Test checking if nested paths exist."""
        context = Context()

        context["user"] = {"profile": {"name": "Alice"}}

        assert context.has_nested("user.profile.name")
        assert context.has_nested("user.profile")
        assert context.has_nested("user")
        assert not context.has_nested("user.profile.age")
        assert not context.has_nested("missing.path")

    def test_flatten_basic(self) -> None:
        """Test flattening nested dictionaries."""
        context = Context()

        context["simple"] = "value"
        context["nested"] = {"level1": {"level2": "deep_value"}, "other": "other_value"}

        flattened = context.flatten()

        assert flattened["simple"] == "value"
        assert flattened["nested.level1.level2"] == "deep_value"
        assert flattened["nested.other"] == "other_value"

    def test_flatten_max_depth(self) -> None:
        """Test flattening with maximum depth limit."""
        context = Context()

        context["deep"] = {"level1": {"level2": {"level3": "value"}}}

        # Flatten with max depth 1
        flattened = context.flatten(max_depth=1)

        assert "deep.level1" in flattened
        assert isinstance(flattened["deep.level1"], dict)
        assert flattened["deep.level1"]["level2"]["level3"] == "value"

    def test_flatten_custom_delimiter(self) -> None:
        """Test flattening with custom delimiter."""
        context = Context()

        context["nested"] = {"level1": {"level2": "value"}}

        flattened = context.flatten(delimiter="/")
        assert "nested/level1/level2" in flattened
        assert flattened["nested/level1/level2"] == "value"

    def test_deep_diff(self) -> None:
        """Test deep diffing between contexts."""
        context1 = Context()
        context2 = Context()

        context1["simple"] = "value1"
        context1["nested"] = {"level1": {"same": "unchanged", "different": "old_value"}}

        context2["simple"] = "value2"
        context2["nested"] = {"level1": {"same": "unchanged", "different": "new_value"}}
        context2["new_key"] = "new_value"

        diff = context1.deep_diff(context2)

        assert diff["simple"] == ("value1", "value2")
        assert diff["nested.level1.different"] == ("old_value", "new_value")
        assert diff["new_key"] == (None, "new_value")

        # 'nested.level1.same' should not be in diff (unchanged)
        assert "nested.level1.same" not in diff


class TestContextQueryingWithComputedProperties:
    """Test querying with computed properties."""

    def test_query_computed_properties(self) -> None:
        """Test querying computed properties specifically."""
        context = Context()

        context["x"] = 10
        context["y"] = 20
        context.add_computed_property(
            "sum", lambda ctx: ctx.get("x", 0) + ctx.get("y", 0), ["x", "y"]
        )
        context.add_computed_property(
            "product", lambda ctx: ctx.get("x", 0) * ctx.get("y", 0), ["x", "y"]
        )

        # Query only computed properties
        computed_only = context.query(
            key_filter=lambda k: context.is_computed_property(k), include_computed=True
        )

        assert len(computed_only) == 2
        assert "sum" in computed_only
        assert "product" in computed_only
        assert computed_only["sum"] == 30
        assert computed_only["product"] == 200

    def test_search_in_computed_values(self) -> None:
        """Test searching within computed property values."""
        context = Context()

        context["first_name"] = "Alice"
        context["last_name"] = "Smith"
        context.add_computed_property(
            "full_name",
            lambda ctx: f"{ctx.get('first_name', '')} {ctx.get('last_name', '')}",
            ["first_name", "last_name"],
        )

        # Search for 'Alice' should find it in the computed full_name
        results = context.search("Alice Smith")
        assert "full_name" in results
        assert results["full_name"] == "Alice Smith"

    def test_nested_operations_with_computed(self) -> None:
        """Test nested operations work with computed properties."""
        context = Context()

        context["user"] = {"first": "Alice", "last": "Smith"}

        # Create computed property that generates nested structure
        context.add_computed_property(
            "user_info",
            lambda ctx: {
                "profile": {
                    "full_name": f"{ctx.get_nested('user.first')} {ctx.get_nested('user.last')}",
                    "initials": f"{ctx.get_nested('user.first')[0]}{ctx.get_nested('user.last')[0]}",
                }
            },
            ["user"],
        )

        # Test that computed nested structures work
        user_info = context["user_info"]
        assert user_info["profile"]["full_name"] == "Alice Smith"
        assert user_info["profile"]["initials"] == "AS"
