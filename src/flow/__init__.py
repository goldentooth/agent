"""
flow - A functional reactive stream processing library.

The flow provides type-safe, composable stream processing with comprehensive
functional programming patterns. Built for high-performance async iterator processing
with strict type checking and comprehensive error handling.

Key Features:
    * **Type-safe composition**: Full generic type preservation through transformations
    * **Functional patterns**: Identity, pure values, and monadic operations
    * **Static factory methods**: Multiple ways to create flows from various sources
    * **Async streaming**: Built on async iterators for efficient stream processing
    * **Comprehensive testing**: 150+ test cases with 100% coverage

Example:
    >>> from flow import Flow
    >>>
    >>> # Create flows from functions
    >>> double_flow = Flow.from_sync_fn(lambda x: x * 2)
    >>> filter_even = Flow.identity().filter(lambda x: x % 2 == 0)
    >>>
    >>> # Compose flows with >> operator
    >>> pipeline = double_flow >> filter_even
    >>>
    >>> # Process async streams
    >>> async def number_stream():
    ...     for i in range(5):
    ...         yield i
    >>>
    >>> result = pipeline(number_stream())
    >>> items = [item async for item in result]  # [0, 2, 4, 6, 8]
"""

from . import exceptions, observability
from .exceptions import (
    FlowConfigurationError,
    FlowError,
    FlowExecutionError,
    FlowTimeoutError,
    FlowValidationError,
)
from .flow import Flow

__version__ = "0.0.1"
__all__ = [
    "Flow",
    "FlowError",
    "FlowValidationError",
    "FlowExecutionError",
    "FlowTimeoutError",
    "FlowConfigurationError",
    "exceptions",
    "observability",
]
