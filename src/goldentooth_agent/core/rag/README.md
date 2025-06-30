# Rag

Rag module

## Overview

- **Complexity**: Critical
- **Files**: 7 Python files
- **Lines of Code**: ~4559
- **Classes**: 13
- **Functions**: 109

## API Reference

### Classes

#### RAGService
Retrieval-Augmented Generation service for intelligent document querying.

**Public Methods:**
- `async query(self, question: str, max_results: int, store_type: str | None, include_metadata: bool, similarity_threshold: float, include_chunks: bool, chunk_types: list[str] | None, prioritize_chunks: bool) -> dict[str, Any]` - Answer a question using RAG with retrieved documents
- `async get_document_chunks_info(self, document_id: str, store_type: str) -> dict[str, Any]` - Get information about the chunks for a specific document
- `async summarize_documents(self, store_type: str | None, max_documents: int) -> dict[str, Any]` - Generate a summary of documents in the knowledge base
- `async get_document_insights(self, document_id: str, store_type: str) -> dict[str, Any]` - Get AI-generated insights about a specific document
- `async search_chunks_by_type(self, chunk_types: list[str], question: str | None, max_results: int, store_type: str | None) -> dict[str, Any]` - Search for chunks of specific types, optionally with semantic similarity
- `async get_document_chunk_summary(self, store_type: str, document_id: str, include_content_preview: bool) -> dict[str, Any]` - Get a summary of all chunks for a specific document
- `async compare_chunks(self, chunk_ids: list[str], comparison_question: str | None) -> dict[str, Any]` - Compare multiple chunks, optionally with a specific comparison question
- `async analyze_document_relationships(self, store_type: str, document_id: str, include_cross_document: bool) -> dict[str, Any]` - Analyze relationships between chunks in documents
- `async query_with_relationships(self, question: str, max_results: int, expand_with_related: bool, relationship_expansion_radius: int, include_relationship_context: bool, **kwargs) -> dict[str, Any]` - Enhanced query that leverages chunk relationships for better context
- `async get_chunk_relationship_insights(self, chunk_id: str) -> dict[str, Any]` - Get insights about a specific chunk's relationships
- `async hybrid_query(self, question: str, max_results: int, store_type: str, include_chunks: bool, semantic_weight: float, keyword_weight: float, min_semantic_score: float, min_keyword_score: float, boost_exact_matches: bool, boost_title_matches: bool, explain_results: bool) -> dict[str, Any]` - Enhanced query using hybrid search (semantic + keyword)
- `async compare_search_methods(self, question: str, max_results: int, store_type: str, include_chunks: bool) -> dict[str, Any]` - Compare results from different search methods
- `async tune_hybrid_search(self, test_queries: list[str], semantic_weights: list[float], keyword_weights: list[float]) -> dict[str, Any]` - Tune hybrid search parameters using test queries
- `async query_with_fusion(self, question: str, max_results: int, store_type: str | None, semantic_weight: float, keyword_weight: float, max_clusters: int, fusion_coherence_threshold: float, include_unfused: bool) -> dict[str, Any]` - Execute a hybrid query with intelligent chunk fusion
- `async analyze_fusion_quality(self, question: str, max_results: int, test_configurations: list[dict[str, float]] | None) -> dict[str, Any]` - Analyze and compare different fusion configurations
- `async enhanced_query(self, question: str, max_results: int, store_type: str | None, domain_context: str | None, enable_expansion: bool, enable_fusion: bool, expansion_strategies: int, auto_reformulate: bool) -> dict[str, Any]` - Enhanced query with intelligent expansion, multi-strategy search, and fusion
- `async analyze_query_intelligence(self, question: str, suggest_alternatives: bool, domain_context: str | None) -> dict[str, Any]` - Analyze query intelligence and provide enhancement suggestions

#### QueryIntent
Types of query intents for different search strategies.

#### QueryExpansion
Result of query expansion with enhanced terms and strategies.

**Public Methods:**
- `all_terms(self) -> set[str]` - Get all unique terms from expansion

#### SearchStrategy
Strategy for executing enhanced searches.

**Public Methods:**
- `primary_query(self) -> str` - Get the primary query with highest weight

#### QueryExpansionEngine
Advanced query expansion and semantic understanding engine.

**Public Methods:**
- `expand_query(self, query: str, domain_context: str | None, include_synonyms: bool, include_related: bool, max_expansions: int) -> QueryExpansion` - Expand a query with semantic understanding and enhancement
- `create_search_strategies(self, expansion: QueryExpansion, max_strategies: int) -> list[SearchStrategy]` - Create multiple search strategies from query expansion
- `analyze_query_quality(self, query: str) -> dict[str, Any]` - Analyze query quality and provide improvement suggestions
- `reformulate_query(self, original_query: str, search_results_count: int, search_quality_score: float) -> list[str]` - Reformulate query based on search performance

#### ChunkCluster
A cluster of related chunks that can be fused together.

**Public Methods:**
- `average_relevance(self) -> float` - Get average relevance score across all chunks
- `chunk_ids(self) -> set[str]` - Get set of chunk IDs in this cluster

#### FusedAnswer
A synthesized answer created from multiple chunks.

**Public Methods:**
- `num_sources(self) -> int` - Get number of source chunks used
- `source_documents(self) -> set[str]` - Get unique source document IDs

#### ChunkFusion
Intelligent chunk fusion for creating comprehensive answers from multiple chunks.

**Public Methods:**
- `fuse_chunks(self, search_results: list[SearchResult], query: str, max_clusters: int) -> list[FusedAnswer]` - Fuse multiple chunks into coherent answers

#### RAGInput
Input schema for RAG agent interactions.

#### RAGOutput
Output schema for RAG agent responses.

#### RAGAgent
RAG-powered agent using FlowAgent architecture.

**Public Methods:**
- `async process_question(self, question: str, conversation_history: list[dict[str, str]] | None, **kwargs: Any) -> RAGOutput` - Process a question and return a RAG response
- `as_flow(self) -> Flow[RAGInput, RAGOutput]` - Convert the RAG agent to a Flow for composition

#### SimpleRAGService
Simplified RAG service for reliable document-based question answering.

**Public Methods:**
- `async query(self, question: str, max_results: int, store_type: str | None, similarity_threshold: float, include_chunks: bool) -> dict[str, Any]` - Answer a question using simple RAG with retrieved documents
- `get_document_count(self) -> dict[str, int]` - Get count of documents in each store
- `get_stats(self) -> dict[str, Any]` - Get statistics about the RAG system

#### SimpleRAGAgent
Simplified RAG agent for document-based conversations.

**Public Methods:**
- `async process_question(self, question: str, conversation_history: list[dict[str, str]] | None, max_results: int, store_type: str | None) -> dict[str, Any]` - Process a question using the RAG service

### Functions

#### `def create_simple_rag_agent() -> SimpleRAGAgent`
Factory function to create a simple RAG agent with dependencies.

## Dependencies

### Internal Dependencies
- `goldentooth_agent.core.embeddings.models`

### External Dependencies
- `__future__`
- `antidote`
- `chunk_fusion`
- `collections`
- `context`
- `dataclasses`
- `datetime`
- `document_store`
- `embeddings`
- `enum`
- `flow_agent`
- `goldentooth_agent`
- `llm`
- `numpy`
- `pydantic`
- `query_expansion`
- `rag_agent`
- `rag_service`
- `re`
- `simple_rag_service`
- `typing`

## Exports

This module exports the following symbols:

- `RAGAgent`
- `RAGInput`
- `RAGOutput`
- `RAGService`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
