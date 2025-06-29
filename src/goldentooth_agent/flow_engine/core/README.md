# Flow Engine Core

## Overview
**Status**: 🟢 Low Complexity | **Lines of Code**: ~400 | **Files**: 4

The core submodule contains the fundamental Flow class and related infrastructure. This is the foundation of the entire Flow Engine system.

## Key Components

### Classes (3)

#### `Flow`
- **File**: `flow.py`
- **Methods**: 15+ methods including map, filter, flat_map, compose
- **Purpose**: Core Flow class for composable stream processing

#### `FlowFactory`
- **File**: `factory.py`
- **Methods**: 6 factory methods
- **Purpose**: Factory methods for creating Flow instances from various sources

#### Exception Classes
- **File**: `exceptions.py`
- **Purpose**: Flow-specific exception hierarchy for error handling

### Functions (8)

#### Flow Factory Methods
- **from_value_fn**: Create Flow from single value function
- **from_sync_fn**: Create Flow from synchronous function
- **from_event_fn**: Create Flow from event-based function
- **from_iterable**: Create Flow from iterable
- **from_emitter**: Create Flow from event emitter

## Public API

### Main Exports
```python
from goldentooth_agent.flow_engine.core import (
    Flow,
    FlowError,
    FlowValidationError,
    FlowExecutionError,
    FlowTimeoutError,
    FlowConfigurationError,
    FlowFactory,
)
```

### Usage Examples
```python
# Basic Flow creation
flow = Flow(my_async_function, name="data_processor")

# Factory methods
numbers_flow = Flow.from_iterable([1, 2, 3, 4, 5])
double_flow = Flow.from_sync_fn(lambda x: x * 2)

# Composition
pipeline = numbers_flow >> double_flow >> Flow.from_sync_fn(str)

# Execution
result = await pipeline.to_list()  # ['2', '4', '6', '8', '10']
```

## Dependencies

### Internal Dependencies
```python
# goldentooth_agent.flow_engine.protocols
# goldentooth_agent.flow_engine.extensions
```

### External Dependencies
```python
# typing, collections.abc, asyncio
```

## Testing

### Test Coverage
- **Test files**: Located in `tests/flow_engine/core/`
- **Coverage target**: 95%+
- **Performance**: All tests <100ms

### Running Tests
```bash
# Run all core tests
poetry run pytest tests/flow_engine/core/ -v

# Run specific test files
poetry run pytest tests/flow_engine/core/test_flow.py -v
poetry run pytest tests/flow_engine/core/test_factory.py -v
```

## Known Issues

### Technical Debt
- [ ] Flow metadata system could be more robust
- [ ] Factory methods could support more input types
- [ ] Error messages could be more descriptive

### Future Improvements
- [ ] Add Flow validation decorators
- [ ] Support for typed Flow generics
- [ ] Performance optimizations for common patterns

## Development Notes

### Architecture Decisions
- Generic Flow class supports any input/output types
- Factory pattern separates creation from core functionality
- Exception hierarchy provides clear error categorization

### Performance Considerations
- Flow creation is lightweight (no eager evaluation)
- Stream processing is lazy by default
- Memory usage scales with stream size, not Flow complexity

## Related Modules

### Dependencies
- **Depends on**: protocols, extensions
- **Used by**: All other Flow Engine submodules

### Integration Points
- All combinators operate on Flow instances
- Observability tools monitor Flow execution
- Registry system catalogs Flow instances
