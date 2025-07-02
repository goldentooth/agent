# Module Development Guidelines

This document provides guidelines for working with large modules, refactoring strategies, and module-specific development practices in the Goldentooth Agent project.

## Large Module Management

### Current High-Complexity Modules

The following modules exceed 1000 LOC and require special attention:

#### Core Flow Engine (`flow_engine/`) - 5K+ LOC
- **Purpose**: Flow composition and execution system
- **Key components**: Combinators, core flow engine, observability
- **Complexity factors**: Async generators, type safety, composition patterns
- **Development approach**: Read flow_engine/README.md before changes

#### RAG System (`core/rag/`) - 3K+ LOC
- **Purpose**: Retrieval-Augmented Generation with query expansion
- **Key components**: RAG service, query expansion, chunk fusion
- **Complexity factors**: Multiple search strategies, vector operations
- **Development approach**: Understand RAG patterns before modifications

#### Embeddings & Vector (`core/embeddings/`) - 2K+ LOC
- **Purpose**: Vector storage, hybrid search, document chunking
- **Key components**: Vector store, embeddings service, hybrid search
- **Complexity factors**: SQLite integration, performance optimization
- **Development approach**: Consider performance implications

#### Context Management (`core/context/`) - 2K+ LOC
- **Purpose**: Context management with snapshots and history
- **Key components**: Context, snapshots, history tracking, event integration
- **Complexity factors**: State management, event propagation
- **Development approach**: Understand state lifecycle

### Module Development Rules

#### Pre-Development Checklist
1. **Read module README.md** - Understand architecture and patterns
2. **Review recent changes** - Check git history for context
3. **Run module tests** - Ensure clean starting state
4. **Check dependencies** - Understand module relationships
5. **Plan the change** - Design before implementation

#### Development Process
```bash
# 1. Start with module tests: pytest tests/core/module_name/ -v
# 2. Read module documentation
# 3. Check test coverage and type checking
# 4. Make changes following TDD
# 5. Run full module test suite
# See command-reference.md for all available commands
```

#### Post-Development Checklist
1. **Update module README.md** - Reflect any API or architectural changes
2. **Run full module tests** - Ensure no regressions
3. **Check type coverage** - Verify type annotations are complete
4. **Consider refactoring needs** - Is the module approaching limits?

**Note**: Module metadata (README.meta.yaml) and documentation (README.md) are automatically managed by pre-commit hooks.

## Automated Module Management

### Overview
Module metadata and documentation are automatically updated by pre-commit hooks when Python files change. This ensures accurate documentation without manual maintenance.

### Developer Workflow
1. Make changes to Python files
2. Stage and commit normally
3. Pre-commit hooks automatically update module documentation

### Key Features
- **Automatic detection** of changed modules
- **Metadata generation** (file counts, symbols, dependencies)
- **README generation** from metadata
- **Symbol conflict prevention** across modules
- **Performance optimization** with selective processing

## Refactoring Strategies

### When to Refactor Large Modules

#### File Size Triggers
- **500+ lines**: Consider splitting into logical submodules
- **800+ lines**: Refactoring should be prioritized
- **1000+ lines**: Immediate refactoring required

#### Complexity Triggers
- **5+ classes per file**: Split into separate files
- **15+ methods per class**: Consider composition or delegation
- **Deep inheritance**: Prefer composition over inheritance
- **Circular dependencies**: Refactor to remove cycles

### Refactoring Approach

#### 1. Analysis Phase
```python
def analyze_module_complexity(module_path: Path) -> dict[str, Any]:
    """Analyze module complexity for refactoring planning."""
    analysis = {"file_sizes": {}, "class_counts": {}, "dependency_graph": {}}
    for py_file in module_path.glob("*.py"):
        analysis["file_sizes"][py_file.name] = len(py_file.read_text().splitlines())
    return analysis
```

#### 2. Planning Phase
- **Identify boundaries**: Natural splitting points (classes, functionality)
- **Dependency analysis**: What depends on what
- **Migration strategy**: How to split without breaking changes

#### 3. Execution Phase
```python
# Example: Splitting a large service class
# Before: Large monolithic service
class LargeRAGService:
    def __init__(self): ...
    def query(self): ...
    def expand_query(self): ...
    def search_documents(self): ...
    def rank_results(self): ...
    def fuse_chunks(self): ...
    def generate_response(self): ...
    # ... 20+ methods

# After: Composition-based approach
@injectable
class RAGService:
    """Main RAG service coordinating specialized components."""

    def __init__(
        self,
        query_expander: QueryExpander = inject.me(),
        document_searcher: DocumentSearcher = inject.me(),
        result_ranker: ResultRanker = inject.me(),
        chunk_fuser: ChunkFuser = inject.me(),
        response_generator: ResponseGenerator = inject.me()
    ) -> None:
        self.query_expander = query_expander
        self.document_searcher = document_searcher
        self.result_ranker = result_ranker
        self.chunk_fuser = chunk_fuser
        self.response_generator = response_generator

    async def query(self, question: str) -> RAGResponse:
        """Coordinate the RAG pipeline."""
        expanded = await self.query_expander.expand(question)
        documents = await self.document_searcher.search(expanded)
        ranked = await self.result_ranker.rank(documents)
        fused = await self.chunk_fuser.fuse(ranked)
        response = await self.response_generator.generate(question, fused)
        return response

@injectable
class QueryExpander:
    """Specialized component for query expansion."""
    def __init__(self, llm_client: LLMClient = inject.me()) -> None:
        self.llm_client = llm_client

    async def expand(self, query: str) -> ExpandedQuery:
        # Focused implementation
        ...
```

#### 4. Validation Phase
```bash
# See command-reference.md for all validation commands
poetry run pytest tests/core/rag/ -v
poetry run pytest tests/core/rag/ --benchmark
poetry run mypy src/goldentooth_agent/core/rag/
```

### Extraction Patterns

#### Service Extraction
```python
# Before: Monolithic processor
class MonolithicProcessor:
    def validate_input(self): ...
    def transform_data(self): ...
    def enrich_data(self): ...
    def store_result(self): ...

# After: Focused services with coordinator
@injectable
class ProcessingCoordinator:
    def __init__(self, validator: InputValidator = inject.me(), transformer: DataTransformer = inject.me()) -> None:
        self.validator = validator
        self.transformer = transformer

    async def process(self, raw_data: RawData) -> ProcessingResult:
        validated = self.validator.validate(raw_data)
        return self.transformer.transform(validated)
```

#### Utility Extraction
```python
# Before: Mixed in main service file
class DocumentProcessor:
    def process(self, doc): ...
    def _validate_document_format(self, doc): ...
    def _normalize_text(self, text): ...

# After: Utilities in separate modules
# utils/document_validation.py
def validate_document_format(document: Document) -> bool: ...

# Main service uses utilities
class DocumentProcessor:
    def __init__(self) -> None:
        self.validator = document_validation
    
    def process(self, doc: Document) -> ProcessedDocument:
        if not self.validator.validate_document_format(doc):
            raise ValueError("Invalid document format")
        # ... rest of processing
```

## Module-Specific Patterns

### Flow Engine Development

#### Flow Composition Patterns
```python
# Follow established flow patterns
from goldentooth_agent.flow_engine.core import Flow
from goldentooth_agent.flow_engine.combinators import map_stream, filter_stream

# Composable flows with error handling
async def document_processing_flow(
    stream: AsyncIterator[RawDocument]
) -> AsyncIterator[ProcessedDocument]:
    async for raw_doc in stream:
        try:
            yield await process_document(raw_doc)
        except ProcessingError as e:
            logger.warning(f"Failed to process {raw_doc.id}: {e}")

# Create pipelines using combinators
pipeline = source_flow | filter_stream(valid) | map_stream(process_document)
```

#### Error Handling in Flows
```python
from goldentooth_agent.flow_engine.core.exceptions import FlowExecutionError

async def safe_processing_flow(stream: AsyncIterator[Document]) -> AsyncIterator[ProcessedDocument]:
    async for document in stream:
        try:
            yield await complex_processing(document)
        except (ValidationError, ProcessingError) as e:
            logger.warning(f"Processing failed for {document.id}: {e}")
            continue
        except Exception as e:
            raise FlowExecutionError(f"Unexpected error: {e}") from e
```

### RAG System Development

#### Query Expansion Patterns
```python
from goldentooth_agent.core.rag.query_expansion import QueryExpansionEngine

@injectable
class CustomQueryExpander:
    def __init__(self, base_expander: QueryExpansionEngine = inject.me()) -> None:
        self.base_expander = base_expander

    async def expand_query(self, query: str, domain_context: str | None = None) -> QueryExpansion:
        base_expansion = await self.base_expander.expand_query(query)
        if domain_context:
            domain_expansions = await self._expand_for_domain(query, domain_context)
            base_expansion.expanded_queries.extend(domain_expansions)
        return base_expansion
```

#### Vector Search Integration
```python
@injectable
class EnhancedVectorSearch:
    def __init__(self, vector_store: VectorStore = inject.me(), embeddings_service: EmbeddingsService = inject.me()) -> None:
        self.vector_store = vector_store
        self.embeddings_service = embeddings_service

    async def search_with_metadata_filtering(self, query: str, metadata_filters: dict[str, Any], limit: int = 10) -> list[dict[str, Any]]:
        query_embedding = await self.embeddings_service.create_embedding(query)
        candidates = self.vector_store.search_similar(query_embedding, limit=limit * 2)
        return [r for r in candidates if self._matches_metadata_filters(r, metadata_filters)][:limit]
```

### Context System Development

#### Context Integration Patterns
```python
from goldentooth_agent.core.context import Context, ContextKey

PROCESSING_CONFIG = ContextKey.create("processing.config", ProcessingConfig, "Processing config")
USER_PREFERENCES = ContextKey.create("user.preferences", UserPreferences, "User preferences")

async def context_aware_processing(documents: list[Document], context: Context) -> list[ProcessedDocument]:
    config, preferences = context[PROCESSING_CONFIG], context[USER_PREFERENCES]
    return [await process_document_with_context(doc, config=config, preferences=preferences) for doc in documents]
```

#### Event Integration
```python
from goldentooth_agent.core.event import EventFlow

async def context_monitoring_flow(context: Context) -> AsyncIterator[ContextChangeEvent]:
    async for change_event in context.subscribe_async():
        yield ContextChangeEvent(
            key=change_event.key,
            old_value=change_event.old_value,
            new_value=change_event.new_value,
            timestamp=change_event.timestamp
        )
```

## Testing Large Modules

### Module-Specific Testing Strategies

#### Flow Engine Testing
```python
@pytest.mark.asyncio
async def test_document_processing_flow():
    documents = [create_test_document("doc1", "content1"), create_test_document("doc2", "content2")]
    results = [result async for result in document_processing_flow(async_iter(documents))]
    assert len(results) == 2 and all(isinstance(r, ProcessedDocument) for r in results)
```

#### RAG System Testing
```python
@pytest.mark.asyncio
async def test_rag_service_integration():
    mock_vector_store = Mock(spec=VectorStore)
    mock_vector_store.search_similar.return_value = [{"content": "test content", "similarity": 0.9}]
    
    mock_llm_client = AsyncMock(spec=LLMClient)
    mock_llm_client.generate.return_value = LLMResponse(content="Generated response")
    
    rag_service = RAGService(vector_store=mock_vector_store, llm_client=mock_llm_client)
    result = await rag_service.query("test question")
    
    assert result.response == "Generated response"
    mock_vector_store.search_similar.assert_called_once()
    mock_llm_client.generate.assert_called_once()
```

### Integration Testing
```python
@pytest.mark.integration
async def test_rag_flow_integration():
    vector_store = create_test_vector_store()
    rag_service = RAGService(vector_store=vector_store)
    
    async def rag_flow(queries: AsyncIterator[str]) -> AsyncIterator[RAGResponse]:
        async for query in queries:
            yield await rag_service.query(query)
    
    test_queries = ["question 1", "question 2"]
    responses = [response async for response in rag_flow(async_iter(test_queries))]
    assert len(responses) == 2 and all(isinstance(r, RAGResponse) for r in responses)
```

## Module Boundaries and Dependencies

### Dependency Management

#### Acceptable Dependencies
```python
# ✅ Good: Clear dependency hierarchy
# Lower level modules
from goldentooth_agent.core.util import maybe_await
from goldentooth_agent.core.paths import Paths

# Same level modules (with clear interfaces)
from goldentooth_agent.core.embeddings import VectorStore
from goldentooth_agent.core.document_store import DocumentStore

# Higher level coordination
from goldentooth_agent.core.rag import RAGService
```

#### Problematic Dependencies
```python
# ❌ Avoid: Circular dependencies
# flow_agent imports rag, rag imports flow_agent

# ❌ Avoid: Deep dependency chains
# cli -> agent -> rag -> embeddings -> vector -> context -> flow

# ❌ Avoid: Implementation coupling
from goldentooth_agent.core.rag.rag_service import RAGService._internal_method
```

### Interface Design
```python
from typing import Protocol

class SearchProvider(Protocol):
    async def search(self, query: str) -> list[SearchResult]: ...
    def configure(self, config: SearchConfig) -> None: ...

class DocumentProvider(Protocol):
    async def get_documents(self, filters: dict) -> list[Document]: ...
    async def store_document(self, doc: Document) -> None: ...

# Modules depend on protocols, not implementations
class RAGOrchestrator:
    def __init__(self, search_provider: SearchProvider, document_provider: DocumentProvider) -> None:
        self.search_provider = search_provider
        self.document_provider = document_provider
```

This comprehensive approach to module development ensures that large, complex modules remain maintainable and can evolve without becoming unwieldy monoliths.
