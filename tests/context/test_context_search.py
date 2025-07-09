"""Tests for Context.search method."""

from context.main import Context


class TestContextSearch:
    """Test suite for Context.search method."""

    def test_search_empty_context(self) -> None:
        """Test search on empty context."""
        context = Context()

        result = context.search("anything")

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_search_no_matches(self) -> None:
        """Test search with term that matches nothing."""
        context = Context()

        context["key1"] = "value1"
        context["key2"] = "value2"

        result = context.search("nonexistent")

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_search_key_match_case_insensitive(self) -> None:
        """Test search matching keys (case insensitive by default)."""
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
        assert user_results["user_name"] == "Alice Smith"
        assert user_results["user_email"] == "alice@example.com"

    def test_search_value_match_case_insensitive(self) -> None:
        """Test search matching values (case insensitive by default)."""
        context = Context()

        context["user_name"] = "Alice Smith"
        context["admin_role"] = "Manager"
        context["user_email"] = "alice@example.com"

        # Search for 'alice' in values (case insensitive)
        alice_results = context.search("alice")

        assert len(alice_results) == 2  # user_name and user_email both contain 'alice'
        assert "user_name" in alice_results
        assert "user_email" in alice_results

    def test_search_case_sensitive(self) -> None:
        """Test case sensitive search."""
        context = Context()

        context["user_name"] = "Alice Smith"
        context["admin_role"] = "Manager"
        context["user_email"] = "alice@example.com"

        # Case sensitive search
        case_sensitive = context.search("Alice", case_sensitive=True)

        assert len(case_sensitive) == 1
        assert "user_name" in case_sensitive
        assert case_sensitive["user_name"] == "Alice Smith"

        # Should not match lowercase 'alice' in email
        case_sensitive_lower = context.search("alice", case_sensitive=True)
        assert len(case_sensitive_lower) == 1
        assert "user_email" in case_sensitive_lower

    def test_search_numeric_values(self) -> None:
        """Test search for numeric values (converted to string)."""
        context = Context()

        context["config_timeout"] = 30
        context["max_users"] = 100
        context["version"] = 1.5

        # Search for numbers (converted to string)
        number_results = context.search("30")
        assert len(number_results) == 1
        assert "config_timeout" in number_results

        # Search for part of a number
        partial_results = context.search("10")
        assert len(partial_results) == 1
        assert "max_users" in partial_results

        # Search for decimal
        decimal_results = context.search("1.5")
        assert len(decimal_results) == 1
        assert "version" in decimal_results

    def test_search_boolean_values(self) -> None:
        """Test search for boolean values."""
        context = Context()

        context["is_active"] = True
        context["is_admin"] = False

        # Search for boolean values
        true_results = context.search("True")
        assert len(true_results) == 1
        assert "is_active" in true_results

        false_results = context.search("False")
        assert len(false_results) == 1
        assert "is_admin" in false_results

    def test_search_list_values(self) -> None:
        """Test search in list values."""
        context = Context()

        context["tags"] = ["python", "testing", "context"]
        context["numbers"] = [1, 2, 3]

        # Search for content in list representation
        python_results = context.search("python")
        assert len(python_results) == 1
        assert "tags" in python_results

        # Search for numbers in list
        number_results = context.search("2")
        assert len(number_results) == 1
        assert "numbers" in number_results

    def test_search_dict_values(self) -> None:
        """Test search in dict values."""
        context = Context()

        context["user_info"] = {"name": "Alice", "age": 30}
        context["settings"] = {"debug": True, "timeout": 60}

        # Search for content in dict representation
        alice_results = context.search("Alice")
        assert len(alice_results) == 1
        assert "user_info" in alice_results

        # Search for key in dict representation
        debug_results = context.search("debug")
        assert len(debug_results) == 1
        assert "settings" in debug_results

    def test_search_none_values(self) -> None:
        """Test search with None values."""
        context = Context()

        context["empty_value"] = None
        context["real_value"] = "test"

        # Search for None representation
        none_results = context.search("None")
        assert len(none_results) == 1
        assert "empty_value" in none_results

    def test_search_exception_handling(self) -> None:
        """Test search handles exceptions gracefully."""
        context = Context()

        # Custom object that might cause issues when converted to string
        class ProblematicClass:
            def __str__(self) -> str:
                raise ValueError("Cannot convert to string")

        context["normal_key"] = "normal_value"
        context["problematic_key"] = ProblematicClass()

        # Search should not crash and should return normal results
        results = context.search("normal")
        assert len(results) == 1
        assert "normal_key" in results

    def test_search_empty_string(self) -> None:
        """Test search with empty string."""
        context = Context()

        context["key1"] = "value1"
        context["key2"] = ""

        # Search for empty string
        empty_results = context.search("")
        # Empty string should match everything since it's contained in all strings
        assert len(empty_results) == 2

    def test_search_with_computed_properties(self) -> None:
        """Test search includes computed properties."""
        context = Context()

        context["base_value"] = 10

        # Add computed property
        def double_value(ctx: Context) -> int:
            base_val = ctx["base_value"]
            assert isinstance(base_val, int)
            return base_val * 2

        context.add_computed_property("computed_double", double_value)

        # Search should find computed value
        results = context.search("20")
        assert len(results) == 1
        assert "computed_double" in results
        assert results["computed_double"] == 20

    def test_search_layered_context(self) -> None:
        """Test search works with layered context."""
        context = Context()

        context["base_key"] = "base_value"

        # Push layer and add more data
        context.push_layer()
        context["layer_key"] = "layer_value"

        # Search should find both base and layer values
        results = context.search("value")
        assert len(results) == 2
        assert "base_key" in results
        assert "layer_key" in results

    def test_search_return_type(self) -> None:
        """Test search returns ContextData type."""
        context = Context()

        context["test_key"] = "test_value"

        results = context.search("test")

        # Should return a dictionary
        assert isinstance(results, dict)
        assert len(results) == 1
        assert results["test_key"] == "test_value"

    def test_search_partial_matches(self) -> None:
        """Test search finds partial matches in keys and values."""
        context = Context()

        context["user_profile"] = "user data here"
        context["profile_settings"] = "configuration"

        # Partial match in key
        user_results = context.search("user")
        assert "user_profile" in user_results

        # Partial match in value
        data_results = context.search("data")
        assert "user_profile" in data_results

        # Partial match in both key and value
        profile_results = context.search("profile")
        assert len(profile_results) == 2
        assert "user_profile" in profile_results
        assert "profile_settings" in profile_results
