"""Tests for sample flows registration and functionality."""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator

import pytest

from flow.flow import Flow
from flow.registry import clear_registry, flow_registry, get_flow, list_flows
from flow_command.sample_flows import clear_sample_flows, register_sample_flows


class TestSampleFlowsRegistration:
    """Test sample flow registration and auto-registration."""

    def setup_method(self) -> None:
        """Clean registry before each test."""
        clear_registry()

    def teardown_method(self) -> None:
        """Clean registry after each test."""
        clear_registry()

    def test_register_sample_flows_creates_flows(self) -> None:
        """Sample flow registration should create flows in all categories."""
        register_sample_flows()

        # Check that flows were registered
        all_flows = list_flows()
        assert len(all_flows) > 0

        # Check specific flows exist
        expected_flows = [
            "uppercase",
            "lowercase",
            "reverse_text",
            "title_case",
            "square",
            "double",
            "add_one",
            "identity",
            "json_stringify",
            "json_parse",
            "random_number",
            "timestamp",
            "greeting",
            "list_length",
            "list_sum",
            "list_max",
            "list_min",
        ]

        for flow_name in expected_flows:
            assert flow_name in all_flows, f"Flow '{flow_name}' not registered"

    def test_register_sample_flows_creates_text_math_categories(self) -> None:
        """Sample flow registration should create text and math categories."""
        register_sample_flows()

        # Check text category
        text_flows = list_flows(category="text")
        assert "uppercase" in text_flows
        assert "lowercase" in text_flows
        assert "reverse_text" in text_flows
        assert "title_case" in text_flows
        assert "greeting" in text_flows

        # Check math category
        math_flows = list_flows(category="math")
        assert "square" in math_flows
        assert "double" in math_flows
        assert "add_one" in math_flows
        assert "list_sum" in math_flows
        assert "list_max" in math_flows
        assert "list_min" in math_flows

    def test_register_sample_flows_creates_other_categories(self) -> None:
        """Sample flow registration should create utility, data, and fun categories."""
        register_sample_flows()

        # Check utility category
        utility_flows = list_flows(category="utility")
        assert "identity" in utility_flows
        assert "timestamp" in utility_flows

        # Check data category
        data_flows = list_flows(category="data")
        assert "json_stringify" in data_flows
        assert "json_parse" in data_flows
        assert "list_length" in data_flows

        # Check fun category
        fun_flows = list_flows(category="fun")
        assert "random_number" in fun_flows

    def test_clear_sample_flows_removes_flows(self) -> None:
        """clear_sample_flows should remove all sample flows."""
        register_sample_flows()

        # Verify flows exist
        assert len(list_flows()) > 0

        # Clear sample flows
        clear_sample_flows()

        # Verify flows are cleared
        assert len(list_flows()) == 0

    def test_flow_retrieval_after_registration(self) -> None:
        """Flows should be retrievable after registration."""
        register_sample_flows()

        # Test retrieving specific flows
        uppercase_flow = get_flow("uppercase")
        assert uppercase_flow is not None
        assert isinstance(uppercase_flow, Flow)

        square_flow = get_flow("square")
        assert square_flow is not None
        assert isinstance(square_flow, Flow)

        # Test non-existent flow
        missing_flow = get_flow("nonexistent")
        assert missing_flow is None


class TestSampleFlowsFunctionality:
    """Test that sample flows work correctly."""

    def setup_method(self) -> None:
        """Clean registry and register sample flows before each test."""
        clear_registry()
        register_sample_flows()

    def teardown_method(self) -> None:
        """Clean registry after each test."""
        clear_registry()

    @pytest.mark.asyncio
    async def test_uppercase_lowercase_flows(self) -> None:
        """Uppercase and lowercase flows should work correctly."""
        # Test uppercase
        uppercase_flow = get_flow("uppercase")
        assert uppercase_flow is not None

        async def create_text_stream() -> AsyncGenerator[str, None]:
            yield "hello world"

        result_stream = uppercase_flow(create_text_stream())
        results = [item async for item in result_stream]
        assert results == ["HELLO WORLD"]

        # Test lowercase
        lowercase_flow = get_flow("lowercase")
        assert lowercase_flow is not None

        async def create_upper_stream() -> AsyncGenerator[str, None]:
            yield "HELLO WORLD"

        result_stream = lowercase_flow(create_upper_stream())
        results = [item async for item in result_stream]
        assert results == ["hello world"]

    @pytest.mark.asyncio
    async def test_reverse_title_flows(self) -> None:
        """Reverse and title case flows should work correctly."""
        # Test reverse_text
        reverse_flow = get_flow("reverse_text")
        assert reverse_flow is not None

        async def create_normal_stream() -> AsyncGenerator[str, None]:
            yield "hello"

        result_stream = reverse_flow(create_normal_stream())
        results = [item async for item in result_stream]
        assert results == ["olleh"]

        # Test title_case
        title_flow = get_flow("title_case")
        assert title_flow is not None

        async def create_lower_stream() -> AsyncGenerator[str, None]:
            yield "hello world"

        result_stream = title_flow(create_lower_stream())
        results = [item async for item in result_stream]
        assert results == ["Hello World"]

    @pytest.mark.asyncio
    async def test_square_double_flows(self) -> None:
        """Square and double flows should work correctly."""
        # Test square
        square_flow = get_flow("square")
        assert square_flow is not None

        async def create_number_stream() -> AsyncGenerator[int, None]:
            yield 5

        result_stream = square_flow(create_number_stream())
        results = [item async for item in result_stream]
        assert results == [25]

        # Test double
        double_flow = get_flow("double")
        assert double_flow is not None

        async def create_double_stream() -> AsyncGenerator[int, None]:
            yield 7

        result_stream = double_flow(create_double_stream())
        results = [item async for item in result_stream]
        assert results == [14]

    @pytest.mark.asyncio
    async def test_add_one_flow(self) -> None:
        """Add one flow should work correctly."""
        add_one_flow = get_flow("add_one")
        assert add_one_flow is not None

        async def create_add_stream() -> AsyncGenerator[int, None]:
            yield 10

        result_stream = add_one_flow(create_add_stream())
        results = [item async for item in result_stream]
        assert results == [11]

    @pytest.mark.asyncio
    async def test_identity_flow(self) -> None:
        """Identity flow should work correctly."""
        identity_flow = get_flow("identity")
        assert identity_flow is not None

        async def create_identity_stream() -> AsyncGenerator[str, None]:
            yield "test_value"

        result_stream = identity_flow(create_identity_stream())
        results = [item async for item in result_stream]
        assert results == ["test_value"]

    @pytest.mark.asyncio
    async def test_json_stringify_flow(self) -> None:
        """JSON stringify flow should work correctly."""
        json_stringify_flow = get_flow("json_stringify")
        assert json_stringify_flow is not None

        test_data = {"key": "value", "number": 42}

        async def create_json_stream() -> AsyncGenerator[dict[str, Any], None]:
            yield test_data

        result_stream = json_stringify_flow(create_json_stream())
        results = [item async for item in result_stream]

        # Parse the JSON result to verify it's correct
        parsed_result = json.loads(results[0])
        assert parsed_result == test_data

    @pytest.mark.asyncio
    async def test_json_parse_flow(self) -> None:
        """JSON parse flow should work correctly."""
        json_parse_flow = get_flow("json_parse")
        assert json_parse_flow is not None

        json_string = '{"test": "value"}'

        async def create_parse_stream() -> AsyncGenerator[str, None]:
            yield json_string

        result_stream = json_parse_flow(create_parse_stream())
        results = [item async for item in result_stream]
        assert results == [{"test": "value"}]

    @pytest.mark.asyncio
    async def test_list_length_flow(self) -> None:
        """List length flow should work correctly."""
        test_list = [1, 2, 3, 4, 5]

        length_flow = get_flow("list_length")
        assert length_flow is not None

        async def create_list_stream() -> AsyncGenerator[list[int], None]:
            yield test_list

        result_stream = length_flow(create_list_stream())
        results = [item async for item in result_stream]
        assert results == [5]

    @pytest.mark.asyncio
    async def test_list_sum_flow(self) -> None:
        """List sum flow should work correctly."""
        test_list = [1, 2, 3, 4, 5]

        sum_flow = get_flow("list_sum")
        assert sum_flow is not None

        async def create_sum_stream() -> AsyncGenerator[list[int], None]:
            yield test_list

        result_stream = sum_flow(create_sum_stream())
        results = [item async for item in result_stream]
        assert results == [15]

    @pytest.mark.asyncio
    async def test_list_max_min_flows(self) -> None:
        """List max and min flows should work correctly."""
        test_list = [1, 2, 3, 4, 5]

        # Test list_max
        max_flow = get_flow("list_max")
        assert max_flow is not None

        async def create_max_stream() -> AsyncGenerator[list[int], None]:
            yield test_list

        result_stream = max_flow(create_max_stream())
        results = [item async for item in result_stream]
        assert results == [5]

        # Test list_min
        min_flow = get_flow("list_min")
        assert min_flow is not None

        async def create_min_stream() -> AsyncGenerator[list[int], None]:
            yield test_list

        result_stream = min_flow(create_min_stream())
        results = [item async for item in result_stream]
        assert results == [1]

    @pytest.mark.asyncio
    async def test_greeting_flow(self) -> None:
        """Greeting flow should work correctly."""
        greeting_flow = get_flow("greeting")
        assert greeting_flow is not None

        async def create_name_stream() -> AsyncGenerator[str, None]:
            yield "Alice"

        result_stream = greeting_flow(create_name_stream())
        results = [item async for item in result_stream]
        assert results == ["Hello, Alice!"]

    @pytest.mark.asyncio
    async def test_random_number_flow(self) -> None:
        """Random number flow should exist and be executable."""
        random_flow = get_flow("random_number")
        assert random_flow is not None

        async def create_random_stream() -> AsyncGenerator[None, None]:
            yield None

        result_stream = random_flow(create_random_stream())
        results = [item async for item in result_stream]
        assert len(results) == 1
        assert isinstance(results[0], int)
        assert 1 <= results[0] <= 100

    @pytest.mark.asyncio
    async def test_timestamp_flow(self) -> None:
        """Timestamp flow should exist and be executable."""
        timestamp_flow = get_flow("timestamp")
        assert timestamp_flow is not None

        async def create_timestamp_stream() -> AsyncGenerator[None, None]:
            yield None

        result_stream = timestamp_flow(create_timestamp_stream())
        results = [item async for item in result_stream]
        assert len(results) == 1
        assert isinstance(results[0], int)
        assert results[0] > 0


class TestSampleFlowsEdgeCases:
    """Test edge cases and error handling for sample flows."""

    def setup_method(self) -> None:
        """Clean registry and register sample flows before each test."""
        clear_registry()
        register_sample_flows()

    def teardown_method(self) -> None:
        """Clean registry after each test."""
        clear_registry()

    @pytest.mark.asyncio
    async def test_json_parse_invalid_json(self) -> None:
        """JSON parse flow should handle invalid JSON gracefully."""
        json_parse_flow = get_flow("json_parse")
        assert json_parse_flow is not None

        async def create_invalid_json_stream() -> AsyncGenerator[str, None]:
            yield "invalid json"

        result_stream = json_parse_flow(create_invalid_json_stream())

        # Should raise an exception for invalid JSON
        with pytest.raises(json.JSONDecodeError):
            [item async for item in result_stream]

    @pytest.mark.asyncio
    async def test_list_operations_empty_list(self) -> None:
        """List operations should handle empty lists appropriately."""
        empty_list: list[int] = []

        # Test list_length with empty list
        length_flow = get_flow("list_length")
        assert length_flow is not None

        async def create_empty_stream() -> AsyncGenerator[list[int], None]:
            yield empty_list

        result_stream = length_flow(create_empty_stream())
        results = [item async for item in result_stream]
        assert results == [0]

        # Test list_sum with empty list
        sum_flow = get_flow("list_sum")
        assert sum_flow is not None

        async def create_empty_sum_stream() -> AsyncGenerator[list[int], None]:
            yield empty_list

        result_stream = sum_flow(create_empty_sum_stream())
        results = [item async for item in result_stream]
        assert results == [0]

    @pytest.mark.asyncio
    async def test_list_max_min_empty_list(self) -> None:
        """List max/min should handle empty lists with appropriate errors."""
        empty_list: list[int] = []

        # Test list_max with empty list - should raise ValueError
        max_flow = get_flow("list_max")
        assert max_flow is not None

        async def create_empty_max_stream() -> AsyncGenerator[list[int], None]:
            yield empty_list

        result_stream = max_flow(create_empty_max_stream())

        with pytest.raises(ValueError):
            [item async for item in result_stream]

        # Test list_min with empty list - should raise ValueError
        min_flow = get_flow("list_min")
        assert min_flow is not None

        async def create_empty_min_stream() -> AsyncGenerator[list[int], None]:
            yield empty_list

        result_stream = min_flow(create_empty_min_stream())

        with pytest.raises(ValueError):
            [item async for item in result_stream]
