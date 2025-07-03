"""Aggregation combinators for collecting and grouping stream operations.

This module provides combinators for batching, chunking, scanning, grouping,
and other aggregation patterns for stream processing.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TypeVar

from flowengine.flow import Flow

Input = TypeVar("Input")


def batch_stream(size: int) -> Flow[Input, list[Input]]:
    """Create a flow that batches stream items into lists of specified size.

    Args:
        size: Number of items per batch

    Returns:
        Flow that batches items into lists of the specified size
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[list[Input], None]:
        """Batch stream items into lists."""
        batch: list[Input] = []
        async for item in stream:
            batch.append(item)
            if len(batch) >= size:
                yield batch
                batch = []

        # Yield remaining items if any
        if batch:
            yield batch

    return Flow(_flow, name=f"batch({size})")


def chunk_stream(size: int) -> Flow[Input, list[Input]]:
    """Create a flow that groups items into fixed-size chunks.

    Similar to batch_stream but emphasizes the chunking concept.

    Args:
        size: Number of items per chunk

    Returns:
        A flow that yields lists of items
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[list[Input], None]:
        """Group items into fixed-size chunks."""
        chunk: list[Input] = []
        async for item in stream:
            chunk.append(item)
            if len(chunk) >= size:
                yield chunk
                chunk = []

        # Yield remaining items if any
        if chunk:
            yield chunk

    return Flow(_flow, name=f"chunk({size})")
