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
- `map()`
- `filter()`
- `flat_map()`
- `for_each()`
- `to_list()`
- `label()`
- `collect()`
- `preview()`
- `print()`
- `with_fallback()`
- `batch()`
- `from_value_fn()`
- `from_sync_fn()`
- `from_event_fn()`
- `from_iterable()`
- `from_emitter()`
- `identity()`
- `pure()`

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
