# Rag

Rag module

## Overview

- **Complexity**: Critical
- **Files**: 7 Python files
- **Lines of Code**: ~4558
- **Classes**: 13
- **Functions**: 109

## API Reference

### Classes

#### RAGService
Retrieval-Augmented Generation service for intelligent document querying.

**Public Methods:**
- `query()`
- `get_document_chunks_info()`
- `summarize_documents()`
- `get_document_insights()`
- `search_chunks_by_type()`
- `get_document_chunk_summary()`
- `compare_chunks()`
- `analyze_document_relationships()`
- `query_with_relationships()`
- `get_chunk_relationship_insights()`
- `hybrid_query()`
- `compare_search_methods()`
- `tune_hybrid_search()`
- `query_with_fusion()`
- `analyze_fusion_quality()`
- `enhanced_query()`
- `analyze_query_intelligence()`

#### QueryIntent
Types of query intents for different search strategies.

#### QueryExpansion
Result of query expansion with enhanced terms and strategies.

**Public Methods:**
- `all_terms()`

#### SearchStrategy
Strategy for executing enhanced searches.

**Public Methods:**
- `primary_query()`

#### QueryExpansionEngine
Advanced query expansion and semantic understanding engine.

**Public Methods:**
- `expand_query()`
- `create_search_strategies()`
- `analyze_query_quality()`
- `reformulate_query()`

#### ChunkCluster
A cluster of related chunks that can be fused together.

**Public Methods:**
- `average_relevance()`
- `chunk_ids()`

#### FusedAnswer
A synthesized answer created from multiple chunks.

**Public Methods:**
- `num_sources()`
- `source_documents()`

#### ChunkFusion
Intelligent chunk fusion for creating comprehensive answers from multiple chunks.

**Public Methods:**
- `fuse_chunks()`

#### RAGInput
Input schema for RAG agent interactions.

#### RAGOutput
Output schema for RAG agent responses.

#### RAGAgent
RAG-powered agent using FlowAgent architecture.

**Public Methods:**
- `process_question()`
- `as_flow()`

#### SimpleRAGService
Simplified RAG service for reliable document-based question answering.

**Public Methods:**
- `query()`
- `get_document_count()`
- `get_stats()`

#### SimpleRAGAgent
Simplified RAG agent for document-based conversations.

**Public Methods:**
- `process_question()`

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
