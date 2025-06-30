# Embeddings

Embeddings module

## Overview

- **Complexity**: Critical
- **Files**: 8 Python files
- **Lines of Code**: ~3533
- **Classes**: 9
- **Functions**: 105

## API Reference

### Classes

#### DocumentChunk
Represents a chunk of a document with metadata.

#### DocumentChunker
Intelligently splits documents into meaningful chunks for better RAG retrieval.

**Public Methods:**
- `chunk_document()`
- `get_chunk_summary()`

#### HybridSearchEngine
Hybrid search engine combining semantic and keyword-based retrieval.

**Public Methods:**
- `hybrid_search()`
- `get_search_stats()`
- `update_hybrid_weights()`
- `update_bm25_parameters()`
- `explain_search_results()`

#### Chunk
Represents a chunk of content for embedding and search.

#### SearchResult
Represents a search result with relevance scoring.

**Public Methods:**
- `chunk_id()`
- `document_id()`
- `content()`

#### VectorStore
Hybrid vector store supporting both SQLite and compressed sidecar files.

**Public Methods:**
- `store_document()`
- `store_document_chunks()`
- `get_document_chunks()`
- `delete_document_chunks()`
- `search_similar()`
- `get_document()`
- `delete_document()`
- `list_documents()`
- `get_stats()`
- `get_all_sidecar_paths()`
- `count_sidecar_files()`
- `sync_sidecar_files()`
- `get_sidecar_metadata()`
- `store_chunk_relationships()`
- `get_chunk_relationships()`
- `get_related_chunks()`
- `delete_chunk_relationships()`
- `get_relationship_stats()`
- `analyze_chunk_network()`

#### EmbeddingsService
Service for creating and managing document embeddings using Anthropic.

**Public Methods:**
- `create_embedding()`
- `create_document_embedding()`
- `embed_batch()`
- `create_document_chunks_with_embeddings()`
- `create_chunk_embedding()`
- `get_embeddable_text_from_chunk()`
- `re_embed_document_with_chunks()`
- `should_use_chunking()`

#### ChunkRelationshipAnalyzer
Analyzes semantic relationships between document chunks.

**Public Methods:**
- `analyze_chunk_relationships()`
- `find_related_chunks()`
- `get_chunk_context_expansion()`

#### OpenAIEmbeddingsService
Service for creating and managing document embeddings using OpenAI.

**Public Methods:**
- `create_embedding()`
- `create_document_embedding()`
- `embed_batch()`
- `create_document_chunks_with_embeddings()`
- `create_chunk_embedding()`
- `get_embeddable_text_from_chunk()`
- `re_embed_document_with_chunks()`
- `should_use_chunking()`
- `get_model_info()`

## Dependencies

### External Dependencies
- `anthropic`
- `antidote`
- `collections`
- `dataclasses`
- `datetime`
- `document_chunker`
- `embeddings_service`
- `gzip`
- `hashlib`
- `json`
- `math`
- `numpy`
- `openai`
- `openai_embeddings`
- `os`
- `pathlib`
- `paths`
- `re`
- `sqlite3`
- `sqlite_vec`
- `struct`
- `typing`
- `vector_store`
- `zlib`

## Exports

This module exports the following symbols:

- `DocumentChunk`
- `DocumentChunker`
- `EmbeddingsService`
- `OpenAIEmbeddingsService`
- `VectorStore`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
