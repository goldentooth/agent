# Rag Module

## Overview
**Status**: 🔴 High Complexity | **Lines of Code**: 5031 | **Files**: 7

Brief description of the module's purpose and responsibilities.

## Key Components

### Classes (13)

#### `RAGService`
- **File**: `rag_service.py`
- **Methods**: 16 methods
- **Purpose**: Retrieval-Augmented Generation service for intelligent document querying....

#### `QueryIntent`
- **File**: `query_expansion.py`
- **Methods**: 0 methods
- **Purpose**: Types of query intents for different search strategies....

#### `QueryExpansion`
- **File**: `query_expansion.py`
- **Methods**: 1 methods
- **Purpose**: Result of query expansion with enhanced terms and strategies....

#### `SearchStrategy`
- **File**: `query_expansion.py`
- **Methods**: 1 methods
- **Purpose**: Strategy for executing enhanced searches....

#### `QueryExpansionEngine`
- **File**: `query_expansion.py`
- **Methods**: 31 methods
- **Purpose**: Advanced query expansion and semantic understanding engine....

#### `ChunkCluster`
- **File**: `chunk_fusion.py`
- **Methods**: 2 methods
- **Purpose**: A cluster of related chunks that can be fused together....

#### `FusedAnswer`
- **File**: `chunk_fusion.py`
- **Methods**: 2 methods
- **Purpose**: A synthesized answer created from multiple chunks....

#### `ChunkFusion`
- **File**: `chunk_fusion.py`
- **Methods**: 14 methods
- **Purpose**: Intelligent chunk fusion for creating comprehensive answers from multiple chunks....

#### `RAGInput`
- **File**: `rag_agent.py`
- **Methods**: 0 methods
- **Purpose**: Input schema for RAG agent interactions....

#### `RAGOutput`
- **File**: `rag_agent.py`
- **Methods**: 0 methods
- **Purpose**: Output schema for RAG agent responses....

### Functions (15)

#### `all_terms`
- **File**: `query_expansion.py`
- **Purpose**: Get all unique terms from expansion....

#### `primary_query`
- **File**: `query_expansion.py`
- **Purpose**: Get the primary query with highest weight....

#### `expand_query`
- **File**: `query_expansion.py`
- **Purpose**: Expand a query with semantic understanding and enhancement.

Args:
    query: Original query string
...

#### `create_search_strategies`
- **File**: `query_expansion.py`
- **Purpose**: Create multiple search strategies from query expansion.

Args:
    expansion: Query expansion result...

#### `analyze_query_quality`
- **File**: `query_expansion.py`
- **Purpose**: Analyze query quality and provide improvement suggestions.

Args:
    query: Query to analyze

R...

#### `reformulate_query`
- **File**: `query_expansion.py`
- **Purpose**: Reformulate query based on search performance.

Args:
    original_query: Original query that perfor...

#### `average_relevance`
- **File**: `chunk_fusion.py`
- **Purpose**: Get average relevance score across all chunks....

#### `chunk_ids`
- **File**: `chunk_fusion.py`
- **Purpose**: Get set of chunk IDs in this cluster....

#### `num_sources`
- **File**: `chunk_fusion.py`
- **Purpose**: Get number of source chunks used....

#### `source_documents`
- **File**: `chunk_fusion.py`
- **Purpose**: Get unique source document IDs....

## Public API

### Main Exports
```python
# TODO: Document main exports
from goldentooth_agent.core.rag import (
    # Add main classes and functions here
)
```

### Usage Examples
```python
# TODO: Add usage examples
```

## Dependencies

### Internal Dependencies
```python
# Key internal imports
# goldentooth_agent.core.embeddings.models
```

### External Dependencies
```python
# Key external imports
# llm.claude_client
# paths
# dataclasses
# antidote
# document_store
# simple_rag_service
# context
# query_expansion
# rag_agent
```

## Testing

### Test Coverage
- **Test files**: Located in `tests/core/rag/`
- **Coverage target**: 85%+
- **Performance**: All tests <1s

### Running Tests
```bash
# Run all tests for this module
poetry run pytest tests/core/rag/

# Run with coverage
poetry run pytest tests/core/rag/ --cov=src/goldentooth_agent/core/rag/
```

## Known Issues

### Technical Debt
- [ ] TODO: Document known issues
- [ ] TODO: Type safety concerns
- [ ] TODO: Performance bottlenecks

### Future Improvements
- [ ] TODO: Planned enhancements
- [ ] TODO: Refactoring needs

## Development Notes

### Architecture Decisions
- TODO: Document key design decisions
- TODO: Explain complex interactions

### Performance Considerations
- TODO: Document performance requirements
- TODO: Known bottlenecks and optimizations

## Related Modules

### Dependencies
- **Depends on**: TODO: List module dependencies
- **Used by**: TODO: List modules that use this one

### Integration Points
- TODO: Document how this module integrates with others
