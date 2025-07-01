# Agent Codebase

Agent Codebase module

## Background & Motivation

### Problem Statement

Describe the specific problem this module addresses and why it exists.

### Theoretical Foundation

#### Core Concepts

Explain the key concepts, algorithms, or design patterns used in this module.

#### Design Philosophy

Describe the design principles and architectural decisions.

### Technical Challenges Addressed

1. **Challenge 1**: Description of technical challenge and how it's solved
2. **Challenge 2**: Another challenge and solution approach

### Integration & Usage

Explain how this module fits into the larger system and typical usage patterns.

---

*This background file was generated as a template. Please customize it with specific details about the agent_codebase module's purpose, design decisions, and theoretical foundations.*

## Overview

- **Complexity**: Critical
- **Files**: 10 Python files
- **Lines of Code**: ~2474
- **Classes**: 22
- **Functions**: 100

## API Reference

### Classes

#### ContentFingerprint
Fingerprint for tracking content changes.

**Public Methods:**
- `has_content_changed(self, new_fingerprint: ContentFingerprint) -> bool` - Check if content has meaningfully changed
- `has_structure_changed(self, new_fingerprint: ContentFingerprint) -> bool` - Check if code structure has changed
- `needs_re_embedding(self, new_fingerprint: ContentFingerprint) -> bool` - Determine if re-embedding is needed

#### ChangeDetectionIndex
Index of content fingerprints for change detection.

**Public Methods:**
- `get_fingerprint(self, document_id: str) -> ContentFingerprint | None` - Get fingerprint for a document
- `update_fingerprint(self, fingerprint: ContentFingerprint) -> None` - Update fingerprint in index
- `remove_fingerprint(self, document_id: str) -> None` - Remove fingerprint from index
- `get_stale_documents(self, current_files: set[str]) -> list[str]` - Get document IDs for files that no longer exist

#### SmartChangeDetector
Detects meaningful changes to minimize unnecessary re-embedding.

    Strategy:
    1. Generate content fingerprints based on semantic content
    2. Compare against previous fingerprints to detect changes
    3. Skip re-embedding for cosmetic changes (whitespace, comments)
    4. Re-embed only when semantic content or structure changes

**Public Methods:**
- `analyze_document_changes(self, document: CodebaseDocument, file_path: Path) -> tuple[bool, ContentFingerprint]` - Analyze if a document needs re-embedding
- `update_fingerprint(self, fingerprint: ContentFingerprint) -> None` - Update fingerprint and save index
- `cleanup_stale_documents(self, current_files: set[str]) -> list[str]` - Remove fingerprints for files that no longer exist
- `get_indexing_stats(self) -> dict[str, Any]` - Get statistics about the change detection index

#### CodebaseRAGQuery
Query that combines codebase introspection with RAG capabilities.

#### CodebaseRAGResult
Combined result from codebase introspection and document RAG.

#### CodebaseRAGIntegration
Integration service that combines codebase introspection with document RAG.

    Mechanical integration process:
    1. Route queries to appropriate services based on content
    2. Execute parallel searches in codebase and document store
    3. Combine and rank results based on relevance
    4. Synthesize comprehensive answers using LLM
    5. Return unified response with source attribution

**Public Methods:**
- `async query(self, query: CodebaseRAGQuery) -> CodebaseRAGResult` - Execute a combined codebase and document query
- `async get_codebase_overview(self) -> dict[str, Any]` - Get comprehensive overview of the codebase for RAG context
- `async index_codebase_for_rag(self) -> dict[str, Any]` - Index the codebase for RAG queries

#### CodebaseDocumentExtractor
Extracts structured documents from codebase files.

    Mechanical extraction process:
    1. Walk directory tree finding relevant files
    2. Parse Python files using AST for structure
    3. Extract functions, classes, and module-level docs
    4. Read documentation files (README.md, README.bg.md)
    5. Generate structured CodebaseDocument objects

**Public Methods:**
- `async extract_from_path(self, root_path: Path, include_patterns: list[str] | None, exclude_patterns: list[str] | None) -> list[CodebaseDocument]` - Extract all documents from a directory tree

#### TokenUsageRecord
Record of token usage for an embedding operation.

#### TokenBudget
Token budget configuration and tracking.

#### TokenTracker
Tracks token usage and provides cost analysis for embedding operations.

    Features:
    1. Precise token counting using tiktoken
    2. Cost estimation based on model pricing
    3. Usage statistics and trends
    4. Budget monitoring and alerts
    5. Savings analysis from change detection

**Public Methods:**
- `count_tokens(self, text: str, model_name: str) -> int` - Count tokens in text using tiktoken
- `record_embedding_operation(self, content: str, content_hash: str, model_name: str, operation_type: str, document_type: str, module_path: str, codebase_name: str, was_cached: bool, change_reason: str) -> TokenUsageRecord` - Record token usage for an embedding operation
- `check_budget_status(self) -> dict[str, Any]` - Check current budget status and warnings
- `get_usage_statistics(self, days: int) -> dict[str, Any]` - Get comprehensive usage statistics
- `get_cost_breakdown(self, group_by: str, days: int) -> dict[str, Any]` - Get cost breakdown over time
- `export_usage_data(self, output_path: Path, format: str) -> None` - Export usage data for analysis

#### IntrospectionQuery
Query for codebase introspection.

#### IntrospectionResult
Result from codebase introspection query.

**Public Methods:**
- `get_code_snippets(self) -> list[str]` - Extract code snippets from results
- `get_documentation_sections(self) -> list[str]` - Extract documentation sections from results

#### CodebaseComparison
Comparison between different codebases.

#### CodebaseIntrospectionService
High-level service for codebase introspection and analysis.

    Mechanical query processing:
    1. Parse natural language query into search terms
    2. Route to appropriate document types based on query intent
    3. Perform vector search across indexed documents
    4. Post-process results with ranking and filtering
    5. Return structured results with metadata

**Public Methods:**
- `async initialize(self) -> None` - Initialize the service and add default codebase
- `async index_current_codebase(self) -> dict[str, Any]` - Index the current Goldentooth Agent codebase
- `async add_external_codebase(self, name: str, path: Path, display_name: str | None, description: str) -> dict[str, Any]` - Add and index an external codebase for comparison
- `async query(self, query: IntrospectionQuery) -> IntrospectionResult` - Execute an introspection query
- `async compare_codebases(self, query: str, codebase_names: list[str]) -> CodebaseComparison` - Compare implementations across different codebases
- `async get_codebase_overview(self, codebase_name: str) -> dict[str, Any]` - Get comprehensive overview of a codebase
- `list_available_codebases(self) -> list[CodebaseInfo]` - List all available codebases

#### CodebaseInfo
Information about a codebase in the collection.

#### CodebaseCollection
Manages multiple codebases for introspection and comparison.

    Mechanically, this works by:
    1. Extracting documents from source files using AST parsing
    2. Chunking documents based on their type and content structure
    3. Embedding chunks using the existing vector store infrastructure
    4. Indexing for semantic and keyword search
    5. Providing query interfaces for introspection

**Public Methods:**
- `async add_codebase(self, name: str, root_path: Path, display_name: str | None, description: str, **kwargs: Any) -> None` - Add a codebase to the collection
- `async index_codebase(self, codebase_name: str, force_full_reindex: bool) -> dict[str, Any]` - Index a codebase by extracting and embedding all documents
- `async search(self, query: str, codebase_names: list[str] | None, document_types: list[CodebaseDocumentType] | None, limit: int) -> list[dict[str, Any]]` - Search across codebases with filtering
- `get_codebase_info(self, codebase_name: str) -> CodebaseInfo | None` - Get information about a specific codebase
- `list_codebases(self) -> list[CodebaseInfo]` - List all codebases in the collection

#### CachedEmbedding
Cached embedding with metadata.

#### EmbeddingCache
Local cache for embeddings to minimize token costs.

    Cache strategy:
    1. Use content hash as cache key
    2. Store embeddings in SQLite for persistence
    3. Include model name in cache key for model changes
    4. Track usage statistics for cache optimization
    5. Automatic cleanup of rarely used embeddings

**Public Methods:**
- `get_embedding(self, content_hash: str, model_name: str) -> list[float] | None` - Get cached embedding if available
- `store_embedding(self, content_hash: str, model_name: str, embedding: list[float]) -> None` - Store embedding in cache
- `get_cache_stats(self) -> dict[str, Any]` - Get cache statistics
- `clear_cache(self) -> None` - Clear all cached embeddings
- `remove_model_cache(self, model_name: str) -> int` - Remove all embeddings for a specific model

#### CachedEmbeddingService
Wrapper for embedding service that adds caching.

    Mechanical caching strategy:
    1. Generate content hash for input text
    2. Check cache for existing embedding
    3. If found, return cached embedding (saves API call)
    4. If not found, call actual embedding service
    5. Store result in cache for future use

**Public Methods:**
- `async embed_text(self, text: str, model_name: str) -> list[float]` - Get embedding for text with caching
- `get_cache_stats(self) -> dict[str, Any]` - Get cache statistics
- `clear_cache(self) -> None` - Clear embedding cache
- `estimate_cost_savings(self) -> dict[str, Any]` - Estimate cost savings from caching

#### DocumentSource
Source information for documents in the codebase collection.

#### CodebaseDocumentType
Types of documents in the codebase collection.

#### CodebaseDocument
A document extracted from the codebase for introspection.

**Public Methods:**
- `get_searchable_text(self) -> str` - Get text optimized for search indexing
- `get_chunk_size_hint(self) -> int` - Suggest chunk size based on document type

## Dependencies

### Internal Dependencies
- `goldentooth_agent.core.embeddings`
- `goldentooth_agent.core.rag.rag_service`

### External Dependencies
- `__future__`
- `antidote`
- `ast`
- `change_detection`
- `collection`
- `datetime`
- `enum`
- `extraction`
- `hashlib`
- `introspection`
- `json`
- `numpy`
- `pathlib`
- `pydantic`
- `schema`
- `source`
- `sqlite3`
- `token_tracking`
- `typing`

## Exports

This module exports the following symbols:

- `CodebaseCollection`
- `CodebaseDocument`
- `CodebaseDocumentType`
- `CodebaseIntrospectionService`
- `IntrospectionQuery`
- `IntrospectionResult`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
