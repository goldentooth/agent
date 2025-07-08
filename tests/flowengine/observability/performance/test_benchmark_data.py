"""Test the benchmark_data fixture."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.mark.asyncio
async def test_benchmark_data_fixture(benchmark_data: dict[str, Any]) -> None:
    """Test benchmark_data fixture provides test data."""
    # Test datasets
    assert "small_dataset" in benchmark_data
    assert "medium_dataset" in benchmark_data
    assert "large_dataset" in benchmark_data
    assert "nested_data" in benchmark_data
    assert "string_data" in benchmark_data
    assert "mixed_data" in benchmark_data
    assert "performance_thresholds" in benchmark_data

    # Test dataset sizes
    assert len(benchmark_data["small_dataset"]) == 100
    assert len(benchmark_data["medium_dataset"]) == 1000
    assert len(benchmark_data["large_dataset"]) == 10000
    assert len(benchmark_data["nested_data"]) == 500
    assert len(benchmark_data["string_data"]) == 1000
    assert len(benchmark_data["mixed_data"]) == 500


@pytest.mark.asyncio
async def test_benchmark_nested_data(benchmark_data: dict[str, Any]) -> None:
    """Test benchmark_data nested data structure."""
    nested_data = benchmark_data["nested_data"]
    assert isinstance(nested_data[0], dict)
    assert "id" in nested_data[0]
    assert "value" in nested_data[0]
    assert nested_data[0]["value"] == nested_data[0]["id"] * 2


@pytest.mark.asyncio
async def test_benchmark_string_data(benchmark_data: dict[str, Any]) -> None:
    """Test benchmark_data string data structure."""
    string_data = benchmark_data["string_data"]
    assert isinstance(string_data[0], str)
    assert string_data[0] == "item_0"


@pytest.mark.asyncio
async def test_benchmark_mixed_data(benchmark_data: dict[str, Any]) -> None:
    """Test benchmark_data mixed data structure."""
    mixed_data = benchmark_data["mixed_data"]
    assert isinstance(mixed_data[0], int)
    assert isinstance(mixed_data[1], str)


@pytest.mark.asyncio
async def test_benchmark_performance_thresholds(benchmark_data: dict[str, Any]) -> None:
    """Test benchmark_data performance thresholds."""
    thresholds = benchmark_data["performance_thresholds"]
    assert "small_processing_time" in thresholds
    assert "medium_processing_time" in thresholds
    assert "large_processing_time" in thresholds
    assert "memory_limit_mb" in thresholds
    assert "max_cpu_usage_percent" in thresholds
