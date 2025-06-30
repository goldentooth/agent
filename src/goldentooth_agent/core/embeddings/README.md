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
- `chunk_document(self, store_type: str, document_id: str, document_data: dict[str, Any]) -> list[DocumentChunk]` - Split a document into logical chunks based on its type and content
- `get_chunk_summary(self, chunks: list[DocumentChunk]) -> dict[str, Any]` - Generate a summary of chunks for a document

#### HybridSearchEngine
Hybrid search engine combining semantic and keyword-based retrieval.

**Public Methods:**
- `async hybrid_search(self, query: str, max_results: int, store_type: str, include_chunks: bool, semantic_weight: float, keyword_weight: float, min_semantic_score: float, min_keyword_score: float, boost_exact_matches: bool, boost_title_matches: bool) -> list[dict[str, Any]]` - Perform hybrid search combining semantic and keyword scoring
- `get_search_stats(self) -> dict[str, Any]` - Get statistics about the search corpus
- `update_hybrid_weights(self, semantic_weight: float, keyword_weight: float) -> None` - Update the weights for hybrid scoring
- `update_bm25_parameters(self, k1: float, b: float) -> None` - Update BM25 parameters
- `async explain_search_results(self, query: str, results: list[dict[str, Any]]) -> dict[str, Any]` - Provide detailed explanation of how search results were scored

#### Chunk
Represents a chunk of content for embedding and search.

#### SearchResult
Represents a search result with relevance scoring.

**Public Methods:**
- `chunk_id(self) -> str` - Get chunk ID for convenience
- `document_id(self) -> str` - Get document ID for convenience
- `content(self) -> str` - Get content for convenience

#### VectorStore
Hybrid vector store supporting both SQLite and compressed sidecar files.

**Public Methods:**
- `store_document(self, store_type: str, document_id: str, content: str, embedding: list[float], metadata: dict[str, Any] | None) -> str` - Store a document and its embedding
- `store_document_chunks(self, store_type: str, document_id: str, chunks: list[Any], embeddings: list[list[float]], document_metadata: dict[str, Any] | None) -> list[str]` - Store document chunks and their embeddings
- `get_document_chunks(self, store_type: str, document_id: str) -> list[dict[str, Any]]` - Get all chunks for a document
- `delete_document_chunks(self, store_type: str, document_id: str) -> int` - Delete all chunks for a document
- `search_similar(self, query_embedding: list[float], limit: int, store_type: str | None, include_chunks: bool) -> list[dict[str, Any]]` - Search for documents similar to the query embedding
- `get_document(self, doc_id: str) -> dict[str, Any] | None` - Get a document by its ID
- `delete_document(self, doc_id: str) -> bool` - Delete a document and its embedding
- `list_documents(self, store_type: str | None, limit: int | None) -> list[dict[str, Any]]` - List all documents in the store
- `get_stats(self) -> dict[str, Any]` - Get statistics about the vector store
- `get_all_sidecar_paths(self) -> list[Path]` - Get paths to all sidecar embedding files
- `count_sidecar_files(self) -> int` - Count the number of sidecar embedding files
- `sync_sidecar_files(self) -> dict[str, Any]` - Sync all embeddings to sidecar files
- `get_sidecar_metadata(self) -> dict[str, Any]` - Get metadata about sidecar files
- `store_chunk_relationships(self, relationships: list[dict[str, Any]]) -> int` - Store chunk relationships in the database
- `get_chunk_relationships(self, chunk_id: str, relationship_types: list[str], min_strength: float, limit: int) -> list[dict[str, Any]]` - Get chunk relationships from the database
- `get_related_chunks(self, chunk_id: str, max_related: int, min_strength: float, relationship_types: list[str]) -> list[dict[str, Any]]` - Get chunks related to a specific chunk
- `delete_chunk_relationships(self, chunk_id: str, relationship_type: str) -> int` - Delete chunk relationships
- `get_relationship_stats(self) -> dict[str, Any]` - Get statistics about chunk relationships
- `analyze_chunk_network(self) -> dict[str, Any]` - Analyze the chunk relationship network structure

#### EmbeddingsService
Service for creating and managing document embeddings using Anthropic.

**Public Methods:**
- `async create_embedding(self, text: str) -> list[float]` - Create an embedding for the given text
- `async create_document_embedding(self, document_data: dict[str, Any]) -> dict[str, Any]` - Create an embedding for a structured document
- `async embed_batch(self, texts: list[str]) -> list[list[float]]` - Create embeddings for a batch of texts
- `async create_document_chunks_with_embeddings(self, store_type: str, document_id: str, document_data: dict[str, Any]) -> dict[str, Any]` - Create chunks for a document and generate embeddings for each chunk
- `async create_chunk_embedding(self, chunk: DocumentChunk) -> dict[str, Any]` - Create an embedding for a single document chunk
- `get_embeddable_text_from_chunk(self, chunk: DocumentChunk) -> str` - Extract embeddable text from a document chunk
- `async re_embed_document_with_chunks(self, store_type: str, document_id: str, document_data: dict[str, Any], force_rechunk: bool) -> dict[str, Any]` - Re-embed a document using chunking, optionally forcing re-chunking
- `should_use_chunking(self, store_type: str, document_data: dict[str, Any]) -> bool` - Determine if a document should be chunked based on type and size

#### ChunkRelationshipAnalyzer
Analyzes semantic relationships between document chunks.

**Public Methods:**
- `async analyze_chunk_relationships(self, chunks: list[DocumentChunk], chunk_embeddings: list[list[float]], include_cross_document: bool) -> dict[str, Any]` - Analyze relationships between chunks
- `async find_related_chunks(self, target_chunk_id: str, relationship_data: dict[str, Any], max_related: int, min_strength: float) -> list[dict[str, Any]]` - Find chunks related to a target chunk
- `get_chunk_context_expansion(self, chunk_ids: list[str], relationship_data: dict[str, Any], expansion_radius: int) -> set[str]` - Expand a set of chunks to include related chunks

#### OpenAIEmbeddingsService
Service for creating and managing document embeddings using OpenAI.

**Public Methods:**
- `async create_embedding(self, text: str) -> list[float]` - Create an embedding for the given text using OpenAI
- `async create_document_embedding(self, document_data: dict[str, Any]) -> dict[str, Any]` - Create an embedding for a structured document
- `async embed_batch(self, texts: list[str], batch_size: int) -> list[list[float]]` - Create embeddings for a batch of texts efficiently
- `async create_document_chunks_with_embeddings(self, store_type: str, document_id: str, document_data: dict[str, Any]) -> dict[str, Any]` - Create chunks for a document and generate embeddings for each chunk
- `async create_chunk_embedding(self, chunk: DocumentChunk) -> dict[str, Any]` - Create an embedding for a single document chunk
- `get_embeddable_text_from_chunk(self, chunk: DocumentChunk) -> str` - Extract embeddable text from a document chunk
- `async re_embed_document_with_chunks(self, store_type: str, document_id: str, document_data: dict[str, Any], force_rechunk: bool) -> dict[str, Any]` - Re-embed a document using chunking, optionally forcing re-chunking
- `should_use_chunking(self, store_type: str, document_data: dict[str, Any]) -> bool` - Determine if a document should be chunked based on type and size
- `get_model_info(self) -> dict[str, Any]` - Get information about the current embedding model

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
