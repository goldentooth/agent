# Architecture Guidelines

This document defines the architectural principles and patterns for the Goldentooth Agent project.

## System Architecture Overview

### Core Design Principles
- **Functional composition**: Use flow-based architecture for data processing
- **Dependency injection**: Manage dependencies with Antidote DI container
- **Type safety**: Strict typing throughout the system
- **Modularity**: Clear separation of concerns between modules
- **Testability**: Design for easy testing and mocking
- **Interface consistency**: Standardized interfaces prevent runtime errors

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │   API Layer     │    │   Web Interface │
│   (Typer)       │    │   (Future)      │    │   (Future)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────────┐
         │                Application Layer                        │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
         │  │ Flow Agent  │ │ RAG Agent   │ │ Simple Agent    │    │
         │  └─────────────┘ └─────────────┘ └─────────────────┘    │
         └─────────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────────┐
         │                  Core Services                          │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
         │  │   Context   │ │   Flow      │ │   Embeddings    │    │
         │  │  Management │ │   Engine    │ │   & Vector      │    │
         │  └─────────────┘ └─────────────┘ └─────────────────┘    │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
         │  │    RAG      │ │   Document  │ │      LLM        │    │
         │  │   Service   │ │    Store    │ │    Clients      │    │
         │  └─────────────┘ └─────────────┘ └─────────────────┘    │
         └─────────────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────────────┐
         │                Infrastructure                           │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
         │  │   Paths     │ │    Event    │ │   Background    │    │
         │  │  Service    │ │   System    │ │     Loop        │    │
         │  └─────────────┘ └─────────────┘ └─────────────────┘    │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
         │  │    YAML     │ │   Named     │ │   Utilities     │    │
         │  │    Store    │ │  Registry   │ │                 │    │
         │  └─────────────┘ └─────────────┘ └─────────────────┘    │
         └─────────────────────────────────────────────────────────┘
```

## Module Organization

### Core Module Structure
```
src/goldentooth_agent/core/
├── context/           # Context management system
├── flow/              # Flow-based functional architecture
├── flow_agent/        # Agent framework built on flows
├── embeddings/        # Vector embeddings and search
├── rag/               # Retrieval-Augmented Generation
├── llm/               # LLM client abstractions
├── document_store/    # Document storage and retrieval
├── paths/             # Cross-platform path handling
├── background_loop/   # Async background processing
├── event/             # Event system
├── named_registry/    # Service registry
├── yaml_store/        # YAML-based configuration
└── util/              # Shared utilities
```

### Module Dependencies
```
        Utilities (util, paths, named_registry)
               ↑
        Infrastructure (yaml_store, event, background_loop)
               ↑
        Core Services (context, flow, embeddings, document_store)
               ↑
        Domain Services (rag, llm)
               ↑
        Application (flow_agent)
               ↑
        Interface (cli)
```

## Dependency Injection Architecture

### Service Definition Pattern
```python
from antidote import injectable, inject
from typing import Protocol

# 1. Define protocol for abstraction
class DocumentStore(Protocol):
    def store_document(self, doc: Document) -> None: ...
    def get_document(self, doc_id: str) -> Document | None: ...

# 2. Implement concrete service
@injectable
class YAMLDocumentStore:
    def __init__(self, paths: Paths = inject.me()) -> None:
        self.paths = paths

    def store_document(self, doc: Document) -> None:
        # Implementation
        ...

# 3. Use service with injection
@injectable
class DocumentProcessor:
    def __init__(
        self,
        store: DocumentStore = inject.me(),
        embeddings: EmbeddingsService = inject.me()
    ) -> None:
        self.store = store
        self.embeddings = embeddings
```

### Dependency Graph Management
- **Avoid circular dependencies**: Use protocols and interfaces
- **Keep dependencies explicit**: Use type annotations for clarity
- **Minimize dependency chains**: Limit depth of injection chains
- **Use factory patterns**: For complex object creation

```python
# ✅ Good: Clear, minimal dependencies
@injectable
class RAGService:
    def __init__(
        self,
        document_store: DocumentStore = inject.me(),
        vector_store: VectorStore = inject.me(),
        llm_client: LLMClient = inject.me()
    ) -> None:
        ...

# ❌ Avoid: Too many dependencies
@injectable
class GodService:
    def __init__(
        self,
        dep1: Service1 = inject.me(),
        dep2: Service2 = inject.me(),
        dep3: Service3 = inject.me(),
        dep4: Service4 = inject.me(),
        dep5: Service5 = inject.me(),
        # ... too many dependencies
    ) -> None:
        ...
```

## Flow-Based Architecture

### Flow Design Principles
- **Immutability**: Flows don't modify input data
- **Composability**: Flows can be combined and chained
- **Type safety**: Strong typing for flow inputs/outputs
- **Async by default**: All flows are async generators
- **Error propagation**: Exceptions bubble up the flow chain

### Flow Implementation Pattern
```python
from goldentooth_agent.core.flow import Flow
from typing import AsyncIterator

async def transform_documents(
    stream: AsyncIterator[Document]
) -> AsyncIterator[ProcessedDocument]:
    """Transform documents in a flow."""
    async for document in stream:
        try:
            processed = await process_document(document)
            yield processed
        except ProcessingError as e:
            # Log error but continue processing
            logger.warning(f"Failed to process {document.id}: {e}")
            continue

# Create flow
document_transformer = Flow(transform_documents, name="document_transformer")

# Compose flows
processing_pipeline = (
    source_flow
    | document_transformer
    | validation_flow
    | storage_flow
)
```

### Flow Composition Patterns
```python
# Sequential composition
pipeline = flow1 | flow2 | flow3

# Parallel processing
parallel_results = parallel_stream(flow1, flow2, flow3)

# Conditional routing
routed = route_stream(
    condition=lambda x: x.type,
    routes={
        "type_a": flow_a,
        "type_b": flow_b,
        "default": default_flow
    }
)

# Error handling
safe_pipeline = flow_with_error_handling(
    main_flow=processing_flow,
    error_handler=lambda e, item: log_error(e, item)
)
```

## Context Management Architecture

### Context System Design
- **Layered contexts**: Support hierarchical context frames
- **Type-safe keys**: Strongly typed context keys with validation
- **Event integration**: Context changes trigger events
- **Snapshot support**: Save/restore context state
- **History tracking**: Track context changes over time

### Context Usage Patterns
```python
from goldentooth_agent.core.context import Context, ContextKey

# Define typed context keys
USER_ID = ContextKey.create("user.id", str, "Current user ID")
PROCESSING_CONFIG = ContextKey.create(
    "processing.config",
    ProcessingConfig,
    "Processing configuration"
)

# Use context in flows
async def process_with_context(
    stream: AsyncIterator[Document],
    context: Context
) -> AsyncIterator[ProcessedDocument]:
    """Process documents using context."""
    user_id = context[USER_ID]
    config = context[PROCESSING_CONFIG]

    async for document in stream:
        # Use context data in processing
        processed = await process_document(
            document,
            user_id=user_id,
            config=config
        )
        yield processed
```

## Interface Consistency Standards

### Mandatory Interface Requirements

**All agents and major service interfaces MUST conform to standardized patterns to prevent runtime errors and ensure maintainability.**

#### Agent Response Interface Standard
```python
# ✅ Required: All agents must implement this interface
from goldentooth_agent.core.schema import AgentResponse
from typing import Protocol

class Agent(Protocol):
    """Standard protocol for all agent implementations."""

    async def process_request(self, request: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Process user request and return standardized response.

        Args:
            request: User input/query string
            context: Optional context data for processing

        Returns:
            AgentResponse with standardized fields:
            - response: Main response text
            - sources: List of source documents/references
            - confidence: Float 0.0-1.0 indicating confidence
            - suggestions: List of follow-up suggestions
            - metadata: Additional processing metadata

        Raises:
            ValidationError: If request format is invalid
            ProcessingError: If processing fails
        """
        ...

# ✅ Implementation example
@injectable
class RAGAgent:
    """RAG agent implementing standard interface."""

    def __init__(
        self,
        rag_service: RAGService = inject.me(),
        llm_client: LLMClient = inject.me()
    ) -> None:
        self.rag_service = rag_service
        self.llm_client = llm_client

    async def process_request(self, request: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Process request using RAG pipeline."""
        # Retrieve relevant documents
        documents = await self.rag_service.query(request, max_results=10)

        # Generate response using LLM
        llm_response = await self.llm_client.generate(
            prompt=request,
            context=documents,
            metadata=context or {}
        )

        # Return standardized response
        return AgentResponse(
            response=llm_response.content,
            sources=[{"title": doc.title, "content": doc.content[:200]} for doc in documents],
            confidence=0.85,  # Based on retrieval quality
            suggestions=["Ask about specific details", "Try a more specific question"],
            metadata={
                "model": llm_response.model,
                "tokens_used": llm_response.usage.total_tokens,
                "retrieval_time": 0.2,
                "generation_time": 1.1
            }
        )
```

#### Service Interface Standards
```python
# ✅ Required: Use protocols for service interfaces
from typing import Protocol, runtime_checkable

@runtime_checkable
class DocumentStore(Protocol):
    """Standard protocol for document storage services."""

    async def store_document(self, document: Document) -> str:
        """Store document and return document ID."""
        ...

    async def get_document(self, document_id: str) -> Document | None:
        """Retrieve document by ID, return None if not found."""
        ...

    async def search_documents(self, query: str, limit: int = 10) -> list[Document]:
        """Search documents by text query."""
        ...

@runtime_checkable
class VectorStore(Protocol):
    """Standard protocol for vector storage services."""

    def store_embedding(
        self,
        document_id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Store document embedding."""
        ...

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 10,
        similarity_threshold: float = 0.0
    ) -> list[dict[str, Any]]:
        """Search for similar embeddings."""
        ...
```

#### Response Type Evolution Strategy
```python
# ✅ Migration pattern for legacy interfaces
class LegacyRAGAgent:
    """Legacy agent being migrated to standard interface."""

    def process(self, query: str) -> dict[str, Any]:
        """Legacy method returning dictionary (deprecated)."""
        # Keep existing implementation
        return {
            "response": "Generated text",
            "sources": [],
            "confidence": 0.8,
            "metadata": {"legacy": True}
        }

    async def process_request(self, request: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Standard interface implementation."""
        # Use legacy method internally
        legacy_result = self.process(request)

        # Convert to standard response
        return AgentResponse.from_dict(legacy_result)

# ✅ Graceful migration support
class AgentResponse(BaseModel):
    """Standard agent response schema."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentResponse":
        """Create AgentResponse from legacy dictionary format."""
        return cls(
            response=data.get("response", ""),
            sources=data.get("sources", []),
            confidence=data.get("confidence", 0.0),
            suggestions=data.get("suggestions", []),
            metadata=data.get("metadata", {})
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return self.model_dump()
```

### Interface Validation Requirements

#### Runtime Interface Checking
```python
# ✅ Validate interfaces at runtime during development
from goldentooth_agent.core.validation import validate_interface_compliance

@injectable
class ServiceRegistry:
    """Registry that validates service interface compliance."""

    def register_agent(self, name: str, agent: Any) -> None:
        """Register agent with interface validation."""
        # Validate agent implements required protocol
        if not isinstance(agent, Agent):
            raise InterfaceComplianceError(
                f"Agent {name} does not implement Agent protocol",
                context={
                    "agent_type": type(agent).__name__,
                    "required_methods": ["process_request"],
                    "available_methods": [m for m in dir(agent) if not m.startswith('_')],
                    "missing_methods": self._find_missing_methods(agent, Agent)
                }
            )

        self._agents[name] = agent

    def _find_missing_methods(self, obj: Any, protocol: type) -> list[str]:
        """Find methods missing from protocol implementation."""
        protocol_methods = set(protocol.__annotations__.keys())
        obj_methods = set(dir(obj))
        return list(protocol_methods - obj_methods)
```

#### Type Safety Enforcement
```python
# ✅ Enforce type safety in interface implementations
from typing import TypeGuard

def is_valid_agent_response(obj: Any) -> TypeGuard[AgentResponse]:
    """Type guard for AgentResponse validation."""
    if not isinstance(obj, AgentResponse):
        return False

    # Validate required fields
    required_fields = ["response", "sources", "confidence", "suggestions", "metadata"]
    for field in required_fields:
        if not hasattr(obj, field):
            return False

    # Validate field types
    if not isinstance(obj.response, str):
        return False
    if not isinstance(obj.sources, list):
        return False
    if not isinstance(obj.confidence, (int, float)) or not (0.0 <= obj.confidence <= 1.0):
        return False

    return True

# Usage in critical paths
async def process_agent_request(agent: Agent, request: str) -> AgentResponse:
    """Process request with response validation."""
    response = await agent.process_request(request)

    if not is_valid_agent_response(response):
        raise InterfaceComplianceError(
            "Agent returned invalid response format",
            context={
                "agent_type": type(agent).__name__,
                "response_type": type(response).__name__,
                "response_data": str(response)[:200]
            }
        )

    return response
```

## Agent Architecture

### Agent Design Pattern
```python
from goldentooth_agent.core.flow_agent import FlowAgent
from goldentooth_agent.core.flow_agent.schema import AgentRequest, AgentResponse

class DocumentProcessingAgent(FlowAgent[AgentRequest, AgentResponse]):
    """Agent for document processing tasks."""

    def __init__(
        self,
        rag_service: RAGService = inject.me(),
        llm_client: LLMClient = inject.me()
    ) -> None:
        super().__init__()
        self.rag_service = rag_service
        self.llm_client = llm_client

    async def process_request(
        self,
        request: AgentRequest,
        context: Context
    ) -> AgentResponse:
        """Process agent request."""
        # Retrieve relevant documents
        documents = await self.rag_service.query(
            request.query,
            max_results=10
        )

        # Generate response using LLM
        response = await self.llm_client.generate(
            prompt=request.query,
            context=documents,
            config=request.config
        )

        return AgentResponse(
            content=response.content,
            metadata=response.metadata,
            documents=documents
        )
```

### Agent Composition
```python
# Simple agent factory
@injectable
class AgentFactory:
    def create_rag_agent(self) -> RAGAgent:
        """Create RAG-enabled agent."""
        return RAGAgent()

    def create_flow_agent(self) -> FlowProcessingAgent:
        """Create flow-based processing agent."""
        return FlowProcessingAgent()

# Agent registry
@injectable
class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, FlowAgent] = {}

    def register(self, name: str, agent: FlowAgent) -> None:
        """Register agent with name."""
        self._agents[name] = agent

    def get(self, name: str) -> FlowAgent:
        """Get agent by name."""
        if name not in self._agents:
            raise ValueError(f"Unknown agent: {name}")
        return self._agents[name]
```

## Error Handling Architecture

### Exception Hierarchy
```python
# Base project exception
class GoldentoothError(Exception):
    """Base exception for Goldentooth Agent."""

# Module-specific exceptions
class FlowError(GoldentoothError):
    """Base exception for flow-related errors."""

class FlowExecutionError(FlowError):
    """Raised when flow execution fails."""

class FlowConfigurationError(FlowError):
    """Raised when flow configuration is invalid."""

# Service-specific exceptions
class RAGError(GoldentoothError):
    """Base exception for RAG-related errors."""

class DocumentNotFoundError(RAGError):
    """Raised when document is not found."""

class EmbeddingError(RAGError):
    """Raised when embedding operation fails."""
```

### Error Handling Strategies
```python
# 1. Fail fast for configuration errors
def validate_config(config: Config) -> None:
    """Validate configuration, fail fast on errors."""
    if not config.api_key:
        raise ConfigurationError("API key is required")

# 2. Graceful degradation for service errors
async def fetch_with_fallback(url: str) -> dict[str, Any]:
    """Fetch data with fallback strategy."""
    try:
        return await primary_service.fetch(url)
    except ServiceUnavailableError:
        logger.warning("Primary service unavailable, using fallback")
        return await fallback_service.fetch(url)

# 3. Error context preservation
async def process_document_safely(doc: Document) -> ProcessingResult:
    """Process document with error context."""
    try:
        return await process_document(doc)
    except ProcessingError as e:
        raise ProcessingError(
            f"Failed to process document {doc.id}: {e}"
        ) from e
```

## Performance Architecture

### Performance Design Patterns
- **Lazy loading**: Load resources only when needed
- **Caching strategies**: Cache expensive operations
- **Async patterns**: Use async/await for I/O operations
- **Resource pooling**: Pool expensive resources like connections
- **Streaming**: Process data streams without loading all into memory

### Caching Architecture
```python
from functools import lru_cache
import asyncio

# Sync caching
@lru_cache(maxsize=128)
def expensive_computation(data: str) -> Result:
    """Cache expensive synchronous operations."""
    return complex_calculation(data)

# Async caching
class AsyncCache:
    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], Awaitable[Any]]
    ) -> Any:
        """Get from cache or compute if not present."""
        if key in self._cache:
            return self._cache[key]

        # Ensure only one computation per key
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            if key not in self._cache:
                self._cache[key] = await compute_fn()
            return self._cache[key]
```

### Resource Management
```python
# Connection pooling
@injectable
class DatabasePool:
    def __init__(self, max_connections: int = 10) -> None:
        self._pool: asyncio.Queue[Connection] = asyncio.Queue(max_connections)
        self._initialize_pool()

    async def get_connection(self) -> Connection:
        """Get connection from pool."""
        return await self._pool.get()

    async def return_connection(self, conn: Connection) -> None:
        """Return connection to pool."""
        await self._pool.put(conn)

# Resource cleanup
class ResourceManager:
    def __init__(self) -> None:
        self._resources: list[AsyncResource] = []

    async def __aenter__(self) -> ResourceManager:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Clean up all managed resources."""
        for resource in reversed(self._resources):
            await resource.cleanup()
```

## Configuration Architecture

### Configuration Management
```python
from pydantic import BaseSettings, Field

class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(..., env="DATABASE_URL")
    max_connections: int = Field(10, env="DB_MAX_CONNECTIONS")
    timeout: float = Field(30.0, env="DB_TIMEOUT")

class LLMConfig(BaseSettings):
    """LLM configuration."""
    api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    model: str = Field("claude-3-sonnet-20240229", env="LLM_MODEL")
    max_tokens: int = Field(2000, env="LLM_MAX_TOKENS")

class AppConfig(BaseSettings):
    """Application configuration."""
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

# Configuration injection
@injectable
class ConfigProvider:
    def __init__(self) -> None:
        self.config = AppConfig()

    def get_database_config(self) -> DatabaseConfig:
        return self.config.database

    def get_llm_config(self) -> LLMConfig:
        return self.config.llm
```

## Testing Architecture

### Test Organization Strategy
- **Mirror source structure**: Tests match source code organization
- **Layered testing**: Unit → Integration → E2E
- **Mock external dependencies**: Use dependency injection for testing
- **Shared fixtures**: Reusable test data and mocks

### Dependency Injection in Tests
```python
import pytest
from antidote import world

@pytest.fixture
def test_world():
    """Provide isolated DI world for testing."""
    with world.test.clone(freeze=False) as test_world:
        yield test_world

@pytest.fixture
def mock_rag_service():
    """Provide mock RAG service."""
    mock = Mock(spec=RAGService)
    mock.query.return_value = []
    return mock

def test_agent_with_mocked_dependencies(test_world, mock_rag_service):
    """Test agent with mocked dependencies."""
    # Override dependency in test world
    test_world[RAGService] = mock_rag_service

    # Create and test agent
    agent = inject(DocumentProcessingAgent)
    result = agent.process_request(test_request)

    assert result is not None
    mock_rag_service.query.assert_called_once()
```

## Security Architecture

### Security Principles
- **Input validation**: Validate all external inputs
- **Least privilege**: Services access only what they need
- **Secure secrets**: Never store secrets in code
- **Error information**: Don't leak sensitive data in errors

### Security Implementation
```python
from goldentooth_agent.core.security import input_validation, secret_management

class SecureDocumentProcessor:
    def __init__(
        self,
        validator: InputValidator = inject.me(),
        secrets: SecretManager = inject.me()
    ) -> None:
        self.validator = validator
        self.secrets = secrets

    async def process_document(self, raw_input: str) -> ProcessedDocument:
        """Securely process document."""
        # Validate input
        validated_input = self.validator.validate_document_input(raw_input)

        # Get API key securely
        api_key = await self.secrets.get_secret("llm_api_key")

        # Process with validated input
        return await self._internal_process(validated_input, api_key)

    def _internal_process(
        self,
        input: ValidatedInput,
        api_key: str
    ) -> ProcessedDocument:
        """Internal processing with validated inputs."""
        # Safe to process validated input
        ...
```

## Monitoring and Observability

### Observability Architecture
- **Structured logging**: JSON logs with context
- **Metrics collection**: Performance and business metrics
- **Distributed tracing**: Track requests across components
- **Health checks**: System health monitoring

```python
import structlog
from goldentooth_agent.core.observability import MetricsCollector, HealthCheck

logger = structlog.get_logger()

@injectable
class ObservableService:
    def __init__(
        self,
        metrics: MetricsCollector = inject.me(),
        health: HealthCheck = inject.me()
    ) -> None:
        self.metrics = metrics
        self.health = health

    async def process_item(self, item: Item) -> ProcessedItem:
        """Process item with observability."""
        with self.metrics.timer("item_processing_duration"):
            logger.info("Processing item", item_id=item.id, item_type=item.type)

            try:
                result = await self._process_item_impl(item)
                self.metrics.increment("items_processed_success")
                return result
            except Exception as e:
                self.metrics.increment("items_processed_error")
                logger.error(
                    "Item processing failed",
                    item_id=item.id,
                    error=str(e),
                    exc_info=True
                )
                raise
```

This architecture provides a solid foundation for scalable, maintainable, and testable code while leveraging modern Python patterns and the specific needs of an AI agent system.
