# Flow Engine Integrations

## Overview
**Status**: 🟡 Medium Complexity | **Lines of Code**: ~400 | **Files**: 3

This submodule handles integrations between Flow Engine and external systems, particularly addressing circular import issues through clean architectural patterns.

## Key Components

### Context Bridge
- **Purpose**: Provides clean integration with the Context system without circular imports
- **Pattern**: Protocol-based dependency inversion
- **Benefits**: Allows trampoline functionality while maintaining modularity

### Trampoline System
- **Purpose**: Enables trampoline-style execution patterns with context state management
- **Pattern**: Plugin registration and lazy loading
- **Benefits**: Continuous loops with clean exit conditions

## Circular Import Resolution

### Problem
The original circular dependency:
```
flow_engine.trampoline → core.context → core.context.flow_integration → core.flow → flow_engine
```

### Solution: Protocol-Based Inversion
1. **Abstract Interfaces**: Define protocols for Context and ContextKey
2. **Dependency Injection**: Inject concrete implementations at runtime
3. **Lazy Loading**: Use runtime imports where needed

### Example Usage
```python
from goldentooth_agent.flow_engine.integrations import ContextFlowBridge

# Create bridge with protocol-based interface
bridge = ContextFlowBridge()

# Register trampoline extensions
bridge.register_trampoline_support()
```

## Architecture Patterns

### Protocol Definitions
- `ContextProtocol`: Abstract interface for context objects
- `ContextKeyProtocol`: Abstract interface for typed context keys
- `FlowProtocol`: Abstract interface for flow objects

### Extension Registry
- Plugin system for adding context functionality
- Runtime registration of trampoline methods
- Clean separation of concerns

### Lazy Initialization
- Import modules only when needed
- Cache imported components for performance
- Graceful fallback when dependencies unavailable

## Integration Points

### Dependencies
- **Depends on**: `flow_engine.protocols`, `flow_engine.extensions`
- **Used by**: Context system (when available)

### Registration Flow
1. Flow Engine starts up
2. Context system detects Flow Engine availability
3. Context registers trampoline extensions via protocols
4. Trampoline functionality becomes available

## Known Issues

### Technical Debt
- [ ] Full trampoline integration pending
- [ ] Context bridge implementation needed
- [ ] Performance impact of lazy loading unknown

### Future Improvements
- [ ] Support for additional context providers
- [ ] Plugin system for other external integrations
- [ ] Optimized lazy loading with caching

## Development Notes

### Design Decisions
- Protocol-based design chosen over inheritance for flexibility
- Lazy loading preferred over eager imports for modularity
- Plugin registration enables extensibility without tight coupling

### Testing Strategy
- Mock context implementations for unit tests
- Integration tests with real context system
- Performance tests for lazy loading overhead
