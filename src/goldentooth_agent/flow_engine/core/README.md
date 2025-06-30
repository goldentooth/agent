# Core

Core module

## Overview

- **Complexity**: Medium
- **Files**: 3 Python files
- **Lines of Code**: ~297
- **Classes**: 6
- **Functions**: 23

## API Reference

### Classes

#### Flow
Class for flow functionality.

**Public Methods:**
- `map(self, fn: Callable[[Output], Newput]) -> Flow[Input, Newput]` - Map a function over the output of the flow
- `filter(self, predicate: Callable[[Output], bool]) -> Flow[Input, Output]` - Filter the output of the flow based on a predicate
- `flat_map(self, fn: Callable[[Output], AsyncIterator[Newput]]) -> Flow[Input, Newput]` - Flat map a function over the output of the flow
- `for_each(self, fn: Callable[[Output], Awaitable[None]]) -> Callable[[AsyncIterator[Input]], Awaitable[None]]` - Consume the flow and apply a function to each item
- `to_list(self) -> Callable[[AsyncIterator[Input]], Awaitable[list[Output]]]` - Collect the output of the flow into a list
- `label(self, label: str) -> Flow[Input, Output]` - Label the flow for debugging purposes
- `collect(self) -> Callable[[AsyncIterator[Input]], Awaitable[list[Output]]]` - Ergonomic method to collect all items into a list
- `async preview(self, stream: AsyncIterator[Input], limit: int) -> list[Output]` - Preview the first few items from a flow for REPL/Jupyter development
- `print(self) -> Flow[Input, Output]` - Print flow information for debugging (chainable)
- `with_fallback(self, default: Output) -> Flow[Input, Output]` - Add a fallback value that's yielded if the flow produces no items
- `batch(self, size: int) -> Flow[Input, list[Output]]` - Batch the output into groups of the specified size
- `from_value_fn(fn: Callable[[Input], Awaitable[Output]] | None) -> Flow[Input, Output] | Callable[[Callable[[Input], Awaitable[Output]]], Flow[Input, Output]]` - Create a flow from an async function that takes an input and returns an output
- `from_sync_fn(fn: Callable[[Input], Output] | None) -> Flow[Input, Output] | Callable[[Callable[[Input], Output]], Flow[Input, Output]]` - Create a flow from a synchronous function that takes an input and returns an output
- `from_event_fn(fn: Callable[[Input], AsyncIterator[Output]] | None) -> Flow[Input, Output] | Callable[[Callable[[Input], AsyncIterator[Output]]], Flow[Input, Output]]` - Create a flow from an async function that returns an async iterator
- `from_iterable(iterable: list[Input]) -> Flow[None, Input]` - Create a flow from an iterable
- `from_emitter(register: Callable[[Callable[[Output], None]], None]) -> Flow[None, Output]` - Create a flow from an emitter that registers a callback to receive items
- `identity() -> Flow[Input, Input]` - Create an identity flow that passes items through unchanged
- `pure(value: Output) -> Flow[None, Output]` - Create a flow that yields a single pure value

#### FlowError
Base exception for all Flow-related errors.

#### FlowValidationError
Raised when flow validation fails (e.g., guard conditions, assertions).

#### FlowExecutionError
Raised when flow execution fails (e.g., all retries exhausted, circuit breaker open).

#### FlowTimeoutError
Raised when flow operations timeout.

#### FlowConfigurationError
Raised when flow is incorrectly configured (e.g., invalid parameters).

## Dependencies

### External Dependencies
- `__future__`
- `asyncio`
- `collections`
- `exceptions`
- `flow`
- `typing`

## Exports

This module exports the following symbols:

- `Flow`
- `FlowConfigurationError`
- `FlowError`
- `FlowExecutionError`
- `FlowTimeoutError`
- `FlowValidationError`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
