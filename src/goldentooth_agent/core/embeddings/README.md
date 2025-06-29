# Embeddings Module

## Overview
**Status**: 🔴 High Complexity | **Lines of Code**: 4187 | **Files**: 8

Brief description of the module's purpose and responsibilities.

## Key Components

### Classes (9)

#### `DocumentChunk`
- **File**: `document_chunker.py`
- **Methods**: 0 methods
- **Purpose**: Represents a chunk of a document with metadata....

#### `DocumentChunker`
- **File**: `document_chunker.py`
- **Methods**: 12 methods
- **Purpose**: Intelligently splits documents into meaningful chunks for better RAG retrieval....

#### `HybridSearchEngine`
- **File**: `hybrid_search.py`
- **Methods**: 12 methods
- **Purpose**: Hybrid search engine combining semantic and keyword-based retrieval....

#### `Chunk`
- **File**: `models.py`
- **Methods**: 2 methods
- **Purpose**: Represents a chunk of content for embedding and search....

#### `SearchResult`
- **File**: `models.py`
- **Methods**: 5 methods
- **Purpose**: Represents a search result with relevance scoring....

#### `VectorStore`
- **File**: `vector_store.py`
- **Methods**: 31 methods
- **Purpose**: Hybrid vector store supporting both SQLite and compressed sidecar files....

#### `EmbeddingsService`
- **File**: `embeddings_service.py`
- **Methods**: 5 methods
- **Purpose**: Service for creating and managing document embeddings using Anthropic....

#### `ChunkRelationshipAnalyzer`
- **File**: `chunk_relationships.py`
- **Methods**: 10 methods
- **Purpose**: Analyzes semantic relationships between document chunks....

#### `OpenAIEmbeddingsService`
- **File**: `openai_embeddings.py`
- **Methods**: 6 methods
- **Purpose**: Service for creating and managing document embeddings using OpenAI....

### Functions (34)

#### `chunk_document`
- **File**: `document_chunker.py`
- **Purpose**: Split a document into logical chunks based on its type and content.

Args:
    store_type: Type of d...

#### `get_chunk_summary`
- **File**: `document_chunker.py`
- **Purpose**: Generate a summary of chunks for a document.

Args:
    chunks: List of document chunks

Returns:
  ...

#### `get_search_stats`
- **File**: `hybrid_search.py`
- **Purpose**: Get statistics about the search corpus....

#### `update_hybrid_weights`
- **File**: `hybrid_search.py`
- **Purpose**: Update the weights for hybrid scoring.

Args:
    semantic_weight: Weight for semantic similarity (0...

#### `update_bm25_parameters`
- **File**: `hybrid_search.py`
- **Purpose**: Update BM25 parameters.

Args:
    k1: Term frequency saturation parameter (default: 1.5)
    b: Len...

#### `chunk_id`
- **File**: `models.py`
- **Purpose**: Get chunk ID for convenience....

#### `document_id`
- **File**: `models.py`
- **Purpose**: Get document ID for convenience....

#### `content`
- **File**: `models.py`
- **Purpose**: Get content for convenience....

#### `store_document`
- **File**: `vector_store.py`
- **Purpose**: Store a document and its embedding.

Args:
    store_type: Type of document store (e.g., "github.rep...

#### `store_document_chunks`
- **File**: `vector_store.py`
- **Purpose**: Store document chunks and their embeddings.

Args:
    store_type: Type of document store (e.g., "gi...

## Public API

### Main Exports
```python
# TODO: Document main exports
from goldentooth_agent.core.embeddings import (
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

```

### External Dependencies
```python
# Key external imports
# paths
# vector_store
# dataclasses
# antidote
# os
# anthropic
# pathlib
# sqlite_vec
# struct
```

## Testing

### Test Coverage
- **Test files**: Located in `tests/core/embeddings/`
- **Coverage target**: 85%+
- **Performance**: All tests <1s

### Running Tests
```bash
# Run all tests for this module
poetry run pytest tests/core/embeddings/

# Run with coverage
poetry run pytest tests/core/embeddings/ --cov=src/goldentooth_agent/core/embeddings/
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
