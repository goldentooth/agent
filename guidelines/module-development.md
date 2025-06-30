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
# 1. Start with module-specific tests
poetry run pytest tests/core/module_name/ -v

# 2. Read module documentation
cat src/goldentooth_agent/core/module_name/README.md

# 3. Understand current test coverage
poetry run pytest tests/core/module_name/ --cov=src/goldentooth_agent/core/module_name

# 4. Run type checking for module
poetry run mypy src/goldentooth_agent/core/module_name/

# 5. Make changes following TDD
# 6. Update module README.md if needed
# 7. Run full module test suite
# 8. Run integration tests if applicable
```

#### Post-Development Checklist
1. **Update module README.md** - Reflect any API or architectural changes
2. **Run full module tests** - Ensure no regressions
3. **Check type coverage** - Verify type annotations are complete
4. **Update module statistics** - File count, LOC, coverage metrics
5. **Consider refactoring needs** - Is the module approaching limits?

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
# Analyze module structure
def analyze_module_complexity(module_path: Path) -> dict[str, Any]:
    """Analyze module complexity for refactoring planning."""
    analysis = {
        "file_sizes": {},
        "class_counts": {},
        "method_counts": {},
        "dependency_graph": {},
        "test_coverage": {}
    }
    
    for py_file in module_path.glob("*.py"):
        # Analyze file complexity
        lines = len(py_file.read_text().splitlines())
        analysis["file_sizes"][py_file.name] = lines
        
        # Parse AST for classes and methods
        # ... complexity analysis
    
    return analysis
```

#### 2. Planning Phase
Create refactoring plan:
- **Identify boundaries**: Natural splitting points (classes, functionality)
- **Dependency analysis**: Understand what depends on what
- **Test coverage**: Ensure adequate tests before refactoring
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
# Ensure refactoring doesn't break functionality
poetry run pytest tests/core/rag/ -v

# Check performance impact
poetry run pytest tests/core/rag/ --benchmark

# Verify type safety
poetry run mypy src/goldentooth_agent/core/rag/

# Update documentation
# Edit src/goldentooth_agent/core/rag/README.md
```

### Extraction Patterns

#### Service Extraction
```python
# Extract specialized services from large classes
# Before: Everything in one class
class MonolithicProcessor:
    def validate_input(self): ...
    def transform_data(self): ...
    def enrich_data(self): ...
    def store_result(self): ...

# After: Focused services
@injectable
class InputValidator:
    def validate(self, data: RawData) -> ValidatedData: ...

@injectable  
class DataTransformer:
    def transform(self, data: ValidatedData) -> TransformedData: ...

@injectable
class DataEnricher:
    def enrich(self, data: TransformedData) -> EnrichedData: ...

@injectable
class ResultStore:
    def store(self, data: EnrichedData) -> StorageResult: ...

# Coordinator service
@injectable
class ProcessingCoordinator:
    def __init__(
        self,
        validator: InputValidator = inject.me(),
        transformer: DataTransformer = inject.me(),
        enricher: DataEnricher = inject.me(),
        store: ResultStore = inject.me()
    ) -> None:
        self.validator = validator
        self.transformer = transformer  
        self.enricher = enricher
        self.store = store
    
    async def process(self, raw_data: RawData) -> ProcessingResult:
        """Coordinate the processing pipeline."""
        validated = self.validator.validate(raw_data)
        transformed = self.transformer.transform(validated)
        enriched = self.enricher.enrich(transformed)
        result = self.store.store(enriched)
        return result
```

#### Utility Extraction
```python
# Extract utility functions to separate modules
# Before: Mixed in main service file
class DocumentProcessor:
    def process(self, doc): ...
    def _validate_document_format(self, doc): ...
    def _normalize_text(self, text): ...
    def _extract_metadata(self, doc): ...
    def _compute_hash(self, content): ...

# After: Utilities in separate modules
# utils/document_validation.py
def validate_document_format(document: Document) -> bool:
    """Validate document format and structure."""
    ...

# utils/text_processing.py  
def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    ...

# utils/metadata_extraction.py
def extract_metadata(document: Document) -> DocumentMetadata:
    """Extract metadata from document."""
    ...

# utils/hashing.py
def compute_content_hash(content: str) -> str:
    """Compute hash of document content."""
    ...

# Main service uses utilities
class DocumentProcessor:
    def __init__(self) -> None:
        self.validator = document_validation
        self.text_processor = text_processing
        self.metadata_extractor = metadata_extraction
        self.hasher = hashing
    
    def process(self, doc: Document) -> ProcessedDocument:
        """Process document using utility functions."""
        if not self.validator.validate_document_format(doc):
            raise ValueError("Invalid document format")
        
        normalized_text = self.text_processor.normalize_text(doc.content)
        metadata = self.metadata_extractor.extract_metadata(doc)
        content_hash = self.hasher.compute_content_hash(normalized_text)
        
        return ProcessedDocument(
            content=normalized_text,
            metadata=metadata,
            hash=content_hash
        )
```

## Module-Specific Patterns

### Flow Engine Development

#### Flow Composition Patterns
```python
# Follow established flow patterns
from goldentooth_agent.flow_engine.core import Flow
from goldentooth_agent.flow_engine.combinators import map_stream, filter_stream

# ✅ Good: Composable flows
async def document_processing_flow(
    stream: AsyncIterator[RawDocument]
) -> AsyncIterator[ProcessedDocument]:
    """Process documents following flow patterns."""
    async for raw_doc in stream:
        try:
            processed = await process_document(raw_doc)
            yield processed
        except ProcessingError as e:
            logger.warning(f"Failed to process {raw_doc.id}: {e}")
            continue

# Create flows using combinators
pipeline = (
    source_flow
    | filter_stream(lambda doc: doc.is_valid())
    | map_stream(process_document)
    | document_processing_flow
)
```

#### Error Handling in Flows
```python
from goldentooth_agent.flow_engine.core.exceptions import FlowExecutionError

async def safe_processing_flow(
    stream: AsyncIterator[Document]
) -> AsyncIterator[ProcessedDocument]:
    """Process documents with comprehensive error handling."""
    async for document in stream:
        try:
            # Main processing logic
            result = await complex_processing(document)
            yield result
        except ValidationError as e:
            # Skip invalid documents
            logger.info(f"Skipping invalid document {document.id}: {e}")
            continue
        except ProcessingError as e:
            # Log processing errors but continue
            logger.error(f"Processing failed for {document.id}: {e}")
            continue
        except Exception as e:
            # Unexpected errors stop the flow
            raise FlowExecutionError(
                f"Unexpected error processing {document.id}: {e}"
            ) from e
```

### RAG System Development

#### Query Expansion Patterns
```python
# Follow RAG service patterns for query expansion
from goldentooth_agent.core.rag.query_expansion import QueryExpansionEngine

@injectable
class CustomQueryExpander:
    """Custom query expansion following established patterns."""
    
    def __init__(
        self,
        base_expander: QueryExpansionEngine = inject.me(),
        llm_client: LLMClient = inject.me()
    ) -> None:
        self.base_expander = base_expander
        self.llm_client = llm_client
    
    async def expand_query(
        self, 
        query: str,
        domain_context: str | None = None
    ) -> QueryExpansion:
        """Expand query using domain-specific logic."""
        # Use base expander for standard expansion
        base_expansion = await self.base_expander.expand_query(query)
        
        # Add domain-specific expansions
        if domain_context:
            domain_expansions = await self._expand_for_domain(
                query, domain_context
            )
            base_expansion.expanded_queries.extend(domain_expansions)
        
        return base_expansion
```

#### Vector Search Integration
```python
# Follow vector store patterns
from goldentooth_agent.core.embeddings import VectorStore, EmbeddingsService

@injectable
class EnhancedVectorSearch:
    """Enhanced vector search following established patterns."""
    
    def __init__(
        self,
        vector_store: VectorStore = inject.me(),
        embeddings_service: EmbeddingsService = inject.me()
    ) -> None:
        self.vector_store = vector_store
        self.embeddings_service = embeddings_service
    
    async def search_with_metadata_filtering(
        self,
        query: str,
        metadata_filters: dict[str, Any],
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search with metadata filtering."""
        # Generate query embedding
        query_embedding = await self.embeddings_service.create_embedding(query)
        
        # Perform vector search
        candidates = self.vector_store.search_similar(
            query_embedding,
            limit=limit * 2  # Get more candidates for filtering
        )
        
        # Apply metadata filters
        filtered_results = [
            result for result in candidates
            if self._matches_metadata_filters(result, metadata_filters)
        ]
        
        return filtered_results[:limit]
```

### Context System Development

#### Context Integration Patterns
```python
# Follow context system patterns
from goldentooth_agent.core.context import Context, ContextKey

# Define typed context keys
PROCESSING_CONFIG = ContextKey.create(
    "processing.config",
    ProcessingConfig,
    "Current processing configuration"
)

USER_PREFERENCES = ContextKey.create(
    "user.preferences", 
    UserPreferences,
    "User preferences for processing"
)

async def context_aware_processing(
    documents: list[Document],
    context: Context
) -> list[ProcessedDocument]:
    """Process documents using context information."""
    # Get configuration from context
    config = context[PROCESSING_CONFIG]
    preferences = context[USER_PREFERENCES]
    
    # Process with context-aware logic
    results = []
    for document in documents:
        processed = await process_document_with_context(
            document, 
            config=config,
            preferences=preferences
        )
        results.append(processed)
    
    return results
```

#### Event Integration
```python
# Follow event system patterns for context changes
from goldentooth_agent.core.event import EventFlow

async def context_monitoring_flow(
    context: Context
) -> AsyncIterator[ContextChangeEvent]:
    """Monitor context changes and emit events."""
    # Subscribe to context changes
    async for change_event in context.subscribe_async():
        # Process change event
        processed_event = ContextChangeEvent(
            key=change_event.key,
            old_value=change_event.old_value,
            new_value=change_event.new_value,
            timestamp=change_event.timestamp
        )
        
        yield processed_event
```

## Testing Large Modules

### Module-Specific Testing Strategies

#### Flow Engine Testing
```python
# Test flows with proper async patterns
@pytest.mark.asyncio
async def test_document_processing_flow():
    """Test document processing flow."""
    # Create test data
    documents = [
        create_test_document("doc1", "content1"),
        create_test_document("doc2", "content2"),
    ]
    
    # Create flow and test
    flow = document_processing_flow
    results = []
    
    async for result in flow(async_iter(documents)):
        results.append(result)
    
    assert len(results) == 2
    assert all(isinstance(r, ProcessedDocument) for r in results)
```

#### RAG System Testing
```python
# Test RAG components with mocked dependencies
@pytest.mark.asyncio
async def test_rag_service_integration():
    """Test RAG service with mocked dependencies."""
    # Setup mocks
    mock_vector_store = Mock(spec=VectorStore)
    mock_vector_store.search_similar.return_value = [
        {"content": "test content", "similarity": 0.9}
    ]
    
    mock_llm_client = AsyncMock(spec=LLMClient)
    mock_llm_client.generate.return_value = LLMResponse(
        content="Generated response"
    )
    
    # Test service
    rag_service = RAGService(
        vector_store=mock_vector_store,
        llm_client=mock_llm_client
    )
    
    result = await rag_service.query("test question")
    
    assert result.response == "Generated response"
    mock_vector_store.search_similar.assert_called_once()
    mock_llm_client.generate.assert_called_once()
```

### Integration Testing
```python
# Test module integration points
@pytest.mark.integration
async def test_rag_flow_integration():
    """Test RAG system integration with flow engine."""
    # Setup real components
    vector_store = create_test_vector_store()
    rag_service = RAGService(vector_store=vector_store)
    
    # Create flow using RAG service
    async def rag_flow(queries: AsyncIterator[str]) -> AsyncIterator[RAGResponse]:
        async for query in queries:
            response = await rag_service.query(query)
            yield response
    
    # Test flow
    test_queries = ["question 1", "question 2"]
    responses = []
    
    async for response in rag_flow(async_iter(test_queries)):
        responses.append(response)
    
    assert len(responses) == 2
    assert all(isinstance(r, RAGResponse) for r in responses)
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
# Design clean interfaces between modules
from typing import Protocol

class SearchProvider(Protocol):
    """Interface for search providers."""
    
    async def search(self, query: str) -> list[SearchResult]: ...
    def configure(self, config: SearchConfig) -> None: ...

class DocumentProvider(Protocol):
    """Interface for document providers."""
    
    async def get_documents(self, filters: dict) -> list[Document]: ...
    async def store_document(self, doc: Document) -> None: ...

# Modules depend on protocols, not implementations
class RAGOrchestrator:
    def __init__(
        self,
        search_provider: SearchProvider,
        document_provider: DocumentProvider
    ) -> None:
        self.search_provider = search_provider
        self.document_provider = document_provider
```

This comprehensive approach to module development ensures that large, complex modules remain maintainable and can evolve without becoming unwieldy monoliths.