# Agent

Agent module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~76
- **Classes**: 0
- **Functions**: 2

## API Reference

### Functions

#### `async def test_basic_rag()`
Test basic RAG components.

#### `async def test_interactive_rag()`
Test the RAG system with multiple queries.

## Dependencies

### Internal Dependencies
- `goldentooth_agent.core.embeddings`
- `goldentooth_agent.core.paths`
- `goldentooth_agent.core.rag.simple_rag_agent`

### External Dependencies
- `asyncio`
- `pathlib`
- `sys`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
