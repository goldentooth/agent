# Explicit Any Migration Guide

This document tracks the progress and strategy for enabling `disallow_any_explicit = true` in mypy configuration.

## Current Status

**Setting**: `disallow_any_explicit = false`
**Remaining Errors**: 174 (down from 182)
**Files Fixed**: 4 files completely migrated

## Fixed Files

These files have been successfully migrated to handle explicit Any properly:

1. **yaml_store/adapter.py** - Used type alias with `# type: ignore[explicit-any]`
2. **util/maybe_await.py** - Used generics and type ignore for necessary Any usage
3. **context/frame.py** - Used type aliases with type ignore comments
4. **context/history_tracker.py** - Used type aliases with type ignore comments

## Migration Strategy

### Phase 1: Type Aliases (COMPLETED for small files)
For legitimate uses of Any (like contexts that can store arbitrary values), use type aliases:

```python
# Type alias for context data - contexts can store any type of value
ContextData = dict[str, Any]  # type: ignore[explicit-any]
ContextValue = Any  # type: ignore[explicit-any]
```

### Phase 2: Generic Type Parameters (IN PROGRESS)
Replace `Flow[Any, Any]` with proper generic type parameters where possible:

```python
# Before
def get_flow(name: str) -> Flow[Any, Any] | None:

# After
from typing import TypeVar
I = TypeVar("I")
O = TypeVar("O")
def get_flow(name: str) -> Flow[I, O] | None:
```

### Phase 3: Protocol Types
For complex cases, use Protocol types to define expected interfaces:

```python
# Instead of dict[str, Any]
from typing import Protocol

class ConfigData(Protocol):
    """Expected structure of configuration data."""
    pass
```

## Remaining Work by Module

### High Priority (Core Infrastructure)
- **context/main.py**: 34 errors - Core context implementation
- **flow/registry.py**: 8 errors - Flow registration system
- **background_loop/main.py**: 2 errors - Async execution

### Medium Priority (Flow System)
- **flow/main.py**: 1 error - Flow base class
- **flow/combinators.py**: 14 errors - Flow combination logic
- **flow/performance.py**: 12 errors - Performance monitoring
- **flow/analysis.py**: 25 errors - Flow analysis tools
- **flow/health.py**: 19 errors - Health checking
- **flow/debugging.py**: 15 errors - Debug tools

### Lower Priority (Extensions)
- **event/flow.py**: 12 errors - Event flow integration
- **paths/flow_integration.py**: 6 errors - Path flow utilities
- **flow_agent/***: ~15 errors total - Agent system

## Recommended Approach

1. **Start with leaf modules** - Fix modules with fewer dependencies first
2. **Use type aliases** - Create meaningful type aliases for common patterns
3. **Add type ignores judiciously** - Only for truly dynamic cases
4. **Document why** - Always explain why Any is necessary in comments
5. **Test incrementally** - Enable setting temporarily to test progress

## Common Patterns

### Pattern 1: Dynamic Data Structures
```python
# Type alias with documentation
JsonData = dict[str, Any]  # type: ignore[explicit-any]  # JSON can contain arbitrary types
```

### Pattern 2: Generic Functions
```python
T = TypeVar("T")
async def process(func: Callable[..., T]) -> T:  # type: ignore[explicit-any]
    # ... implementation
```

### Pattern 3: Plugin/Registry Systems
```python
# Use base types or protocols instead of Any
PluginRegistry = dict[str, BasePlugin]  # Instead of dict[str, Any]
```

## Testing Strategy

1. Enable setting temporarily: `disallow_any_explicit = true`
2. Run: `poetry run mypy src/goldentooth_agent/core/MODULE --strict`
3. Fix errors in that module
4. Run tests: `poetry run poe test`
5. Commit when module is complete

## Goal

Eventually enable `disallow_any_explicit = true` permanently to ensure:
- Better type safety
- Improved IDE support
- Clearer API contracts
- Easier refactoring

## Progress Tracking

- [x] Initial assessment (182 errors)
- [x] Fix easy wins (4 files, 8 errors fixed)
- [ ] Fix core infrastructure modules
- [ ] Fix flow system modules
- [ ] Fix extension modules
- [ ] Enable setting permanently
