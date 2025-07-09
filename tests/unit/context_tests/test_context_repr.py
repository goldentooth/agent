"""Tests for Context.__repr__ method."""

from context.main import Context


class TestContextRepr:
    """Test suite for Context.__repr__ method."""

    def test_repr_empty_context(self) -> None:
        """Test repr of empty context."""
        context = Context()

        result = repr(context)

        assert result == "<Context frames=1 keys=[]>"

    def test_repr_with_simple_keys(self) -> None:
        """Test repr with simple key-value pairs."""
        context = Context()

        context["key1"] = "value1"
        context["key2"] = "value2"

        result = repr(context)

        # Should show frame count and keys
        assert result.startswith("<Context frames=1 keys=")
        assert "'key1'" in result
        assert "'key2'" in result
        assert result.endswith(">")

    def test_repr_with_multiple_frames(self) -> None:
        """Test repr with multiple frames."""
        context = Context()

        context["base"] = "value"
        context.push_layer()
        context["layer"] = "value"
        context.push_layer()
        context["top"] = "value"

        result = repr(context)

        # Should show correct frame count
        assert result.startswith("<Context frames=3 keys=")
        assert "'base'" in result
        assert "'layer'" in result
        assert "'top'" in result

    def test_repr_with_computed_properties(self) -> None:
        """Test repr includes computed properties in keys."""
        context = Context()

        context["base"] = 10

        def compute_double(ctx: Context) -> int:
            base = ctx["base"]
            assert isinstance(base, int)
            return base * 2

        context.add_computed_property("double", compute_double)

        result = repr(context)

        # Should include computed property in keys
        assert "'base'" in result
        assert "'double'" in result

    def test_repr_return_type(self) -> None:
        """Test that repr returns a string."""
        context = Context()

        result = repr(context)

        assert isinstance(result, str)

    def test_repr_with_various_key_types(self) -> None:
        """Test repr with various key types and names."""
        context = Context()

        context["simple"] = "value"
        context["key_with_underscores"] = "value"
        context["key-with-dashes"] = "value"
        context["key with spaces"] = "value"
        context["123numeric"] = "value"

        result = repr(context)

        # Should include all keys
        assert "'simple'" in result
        assert "'key_with_underscores'" in result
        assert "'key-with-dashes'" in result
        assert "'key with spaces'" in result
        assert "'123numeric'" in result

    def test_repr_with_many_keys(self) -> None:
        """Test repr with many keys."""
        context = Context()

        # Add many keys
        for i in range(10):
            context[f"key{i}"] = f"value{i}"

        result = repr(context)

        # Should include all keys
        assert result.startswith("<Context frames=1 keys=")
        for i in range(10):
            assert f"'key{i}'" in result

    def test_repr_with_layered_overrides(self) -> None:
        """Test repr with layered key overrides."""
        context = Context()

        context["shared"] = "base"
        context["unique1"] = "value1"

        context.push_layer()
        context["shared"] = "override"
        context["unique2"] = "value2"

        result = repr(context)

        # Should show all unique keys, not duplicates
        assert result.startswith("<Context frames=2 keys=")
        assert "'shared'" in result
        assert "'unique1'" in result
        assert "'unique2'" in result

        # Should appear only once in the keys list
        assert result.count("'shared'") == 1

    def test_repr_format_consistency(self) -> None:
        """Test that repr format is consistent."""
        context = Context()

        context["test"] = "value"

        result = repr(context)

        # Should follow the expected format
        assert result.startswith("<Context frames=")
        assert " keys=" in result
        assert result.endswith(">")

    def test_repr_with_empty_frames(self) -> None:
        """Test repr with empty frames."""
        context = Context()

        # Push empty layers
        context.push_layer()
        context.push_layer()

        result = repr(context)

        # Should show correct frame count with empty keys
        assert result == "<Context frames=3 keys=[]>"

    def test_repr_with_mixed_frame_content(self) -> None:
        """Test repr with mixed frame content."""
        context = Context()

        # Base frame with data
        context["base"] = "value"

        # Empty frame
        context.push_layer()

        # Frame with data
        context.push_layer()
        context["top"] = "value"

        result = repr(context)

        # Should show correct frame count and all keys
        assert result.startswith("<Context frames=3 keys=")
        assert "'base'" in result
        assert "'top'" in result

    def test_repr_with_computed_and_regular_mix(self) -> None:
        """Test repr with mix of computed and regular properties."""
        context = Context()

        context["regular1"] = "value1"
        context["regular2"] = "value2"

        def compute_sum(ctx: Context) -> str:
            regular1 = ctx["regular1"]
            regular2 = ctx["regular2"]
            assert isinstance(regular1, str)
            assert isinstance(regular2, str)
            return regular1 + regular2

        context.add_computed_property("computed", compute_sum)

        result = repr(context)

        # Should include both regular and computed properties
        assert "'regular1'" in result
        assert "'regular2'" in result
        assert "'computed'" in result

    def test_repr_key_ordering(self) -> None:
        """Test that repr includes all keys regardless of order."""
        context = Context()

        # Add keys in specific order
        context["zebra"] = "value"
        context["alpha"] = "value"
        context["beta"] = "value"

        result = repr(context)

        # Should include all keys
        assert "'zebra'" in result
        assert "'alpha'" in result
        assert "'beta'" in result

    def test_repr_with_special_characters_in_keys(self) -> None:
        """Test repr with special characters in keys."""
        context = Context()

        context["key.with.dots"] = "value"
        context["key/with/slashes"] = "value"
        context["key@with@symbols"] = "value"
        context["key[with]brackets"] = "value"

        result = repr(context)

        # Should handle special characters correctly
        assert "'key.with.dots'" in result
        assert "'key/with/slashes'" in result
        assert "'key@with@symbols'" in result
        assert "'key[with]brackets'" in result

    def test_repr_frame_count_accuracy(self) -> None:
        """Test that frame count in repr is accurate."""
        context = Context()

        # Start with 1 frame
        result = repr(context)
        assert "frames=1" in result

        # Add frames
        context.push_layer()
        result = repr(context)
        assert "frames=2" in result

        context.push_layer()
        result = repr(context)
        assert "frames=3" in result

        # Remove frame
        context.pop_layer()
        result = repr(context)
        assert "frames=2" in result

    def test_repr_does_not_modify_context(self) -> None:
        """Test that repr doesn't modify the context state."""
        context = Context()

        context["test"] = "value"
        original_value = context["test"]

        # Call repr multiple times
        repr(context)
        repr(context)
        repr(context)

        # Verify state is unchanged
        assert context["test"] == original_value

    def test_repr_with_unicode_keys(self) -> None:
        """Test repr with unicode characters in keys."""
        context = Context()

        context["测试"] = "chinese"
        context["тест"] = "russian"
        context["🔑"] = "emoji"

        result = repr(context)

        # Should handle unicode correctly
        assert "'测试'" in result
        assert "'тест'" in result
        assert "'🔑'" in result

    def test_repr_consistent_across_calls(self) -> None:
        """Test that repr is consistent across multiple calls."""
        context = Context()

        context["stable"] = "value"

        result1 = repr(context)
        result2 = repr(context)
        result3 = repr(context)

        # Should be identical
        assert result1 == result2 == result3

    def test_repr_with_complex_key_structure(self) -> None:
        """Test repr with complex key structures."""
        context = Context()

        # Multiple frames with various keys
        context["base_config"] = "value"

        context.push_layer()
        context["layer_1_key"] = "value"
        context["override_key"] = "layer1"

        def compute_status(ctx: Context) -> str:
            return "active"

        context.add_computed_property("status", compute_status)

        result = repr(context)

        # Should include all unique keys
        assert "'base_config'" in result
        assert "'layer_1_key'" in result
        assert "'override_key'" in result
        assert "'status'" in result
        assert "frames=2" in result
