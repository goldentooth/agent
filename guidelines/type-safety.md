# Type Safety Guidelines

This document defines the type safety standards and practices for the Goldentooth Agent project.

## Type Safety Philosophy

### Core Principles
- **Strict type checking**: Zero tolerance for type errors in production code
- **Complete annotations**: All functions, methods, and complex variables must be typed
- **Runtime safety**: Type annotations should reflect actual runtime behavior
- **Developer experience**: Types should aid understanding and prevent bugs

### Required Tools
- **mypy**: Static type checker configured in strict mode
- **Pylance**: VS Code language server for real-time type checking
- **typing**: Standard library typing module for type annotations

## Type Annotation Requirements

### Function Signatures
All functions must have complete type annotations:

```python
# ✅ Complete function annotation
def process_documents(
    documents: list[Document],
    max_count: int = 10,
    timeout: float | None = None
) -> ProcessingResult:
    """Process documents with type safety."""
    ...

# ✅ Async function annotation
async def fetch_data(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    """Fetch data asynchronously."""
    ...

# ❌ Missing annotations
def process_data(items, count=10):  # Type checker will complain
    ...
```

### Variable Annotations
Annotate variables when type is not obvious:

```python
# ✅ Required: Complex container types
results: list[ProcessingResult] = []
cache: dict[str, Any] = {}
queue: asyncio.Queue[Document] = asyncio.Queue()

# ✅ Required: Optional/Union types
config: Config | None = None
processor: DocumentProcessor | FileProcessor = choose_processor()

# ✅ Recommended: Simple types (for clarity)
count: int = 0
enabled: bool = True
name: str = "obvious_string"
```

### Class Annotations
```python
class DocumentProcessor:
    """Document processor with proper type annotations."""

    # Class variables
    DEFAULT_TIMEOUT: float = 30.0

    def __init__(
        self,
        config: ProcessorConfig,
        cache: Cache | None = None
    ) -> None:
        """Initialize processor with typed parameters."""
        self.config: ProcessorConfig = config
        self.cache: Cache = cache or MemoryCache()
        self._results: list[ProcessingResult] = []

    def process(self, document: Document) -> ProcessingResult:
        """Process a single document."""
        ...

    @property
    def status(self) -> ProcessorStatus:
        """Current processor status."""
        return self._status
```

## Generic Types and Type Variables

### Type Variable Definitions
```python
from typing import TypeVar, Generic, Callable

# ✅ Descriptive type variables
Input = TypeVar("Input")
Output = TypeVar("Output")
DocumentType = TypeVar("DocumentType", bound=BaseDocument)

# ✅ Constrained type variables
NumberType = TypeVar("NumberType", int, float)
SerializableType = TypeVar("SerializableType", str, int, float, bool, dict, list)

# ✅ Generic classes
class Processor(Generic[Input, Output]):
    """Generic processor for any input/output types."""

    def __init__(self, transform_fn: Callable[[Input], Output]) -> None:
        self.transform_fn = transform_fn

    def process(self, item: Input) -> Output:
        return self.transform_fn(item)

# ✅ Generic function
def map_items(items: list[Input], func: Callable[[Input], Output]) -> list[Output]:
    """Map function over list of items."""
    return [func(item) for item in items]
```

### Protocol Usage
```python
from typing import Protocol

class Processable(Protocol):
    """Protocol for objects that can be processed."""

    def get_id(self) -> str:
        """Get unique identifier."""
        ...

    def get_content(self) -> str:
        """Get processable content."""
        ...

class Serializable(Protocol):
    """Protocol for serializable objects."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        ...

def process_items(items: list[Processable]) -> list[ProcessingResult]:
    """Process any objects that conform to Processable protocol."""
    return [process_single(item) for item in items]
```

## Union Types and Optional

### Modern Union Syntax
```python
# ✅ Python 3.10+ union syntax (required)
def get_data(source: str | Path) -> dict[str, Any] | None:
    """Get data from string or Path source."""
    ...

# ✅ Multiple unions
def process_input(
    data: str | bytes | Path,
    format: Literal["json", "yaml", "toml"] = "json"
) -> dict[str, Any] | list[Any]:
    """Process input in various formats."""
    ...

# ✅ Optional is Union with None
def create_processor(config: Optional[ProcessorConfig] = None) -> DocumentProcessor:
    """Create processor with optional config."""
    if config is None:
        config = get_default_config()
    return DocumentProcessor(config)
```

### Type Guards
```python
from typing import TypeGuard

def is_document(obj: Any) -> TypeGuard[Document]:
    """Type guard to check if object is a Document."""
    return (
        hasattr(obj, 'id') and
        hasattr(obj, 'content') and
        hasattr(obj, 'metadata')
    )

def process_unknown_objects(objects: list[Any]) -> list[ProcessingResult]:
    """Process objects, filtering for Documents."""
    documents = [obj for obj in objects if is_document(obj)]
    return [process_document(doc) for doc in documents]
```

## Async Type Annotations

### Async Function Types
```python
from typing import Awaitable, AsyncIterator, AsyncGenerator
import asyncio

# ✅ Basic async function
async def fetch_document(doc_id: str) -> Document:
    """Fetch document asynchronously."""
    ...

# ✅ Async generator
async def document_stream(query: str) -> AsyncIterator[Document]:
    """Stream documents matching query."""
    async for doc in search_documents(query):
        yield doc

# ✅ Async context manager
class AsyncProcessor:
    async def __aenter__(self) -> AsyncProcessor:
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.cleanup()

# ✅ Async callback types
AsyncCallback = Callable[[Document], Awaitable[None]]
AsyncTransform = Callable[[Input], Awaitable[Output]]

async def process_with_callback(
    documents: list[Document],
    callback: AsyncCallback
) -> None:
    """Process documents with async callback."""
    for doc in documents:
        await callback(doc)
```

### Coroutine vs Awaitable
```python
from typing import Coroutine, Awaitable

# ✅ Use Awaitable for parameters (more general)
async def chain_operations(operation: Awaitable[Result]) -> ProcessedResult:
    """Chain async operations."""
    result = await operation
    return process_result(result)

# ✅ Use Coroutine for return types when specific
def create_fetch_operation(url: str) -> Coroutine[Any, Any, dict[str, Any]]:
    """Create coroutine for fetching data."""
    return _fetch_data_impl(url)
```

## Dependency Injection Types

### Antidote Integration
```python
from antidote import inject, injectable
from typing import Protocol

class DocumentStore(Protocol):
    """Protocol for document storage."""

    def store(self, document: Document) -> None: ...
    def retrieve(self, doc_id: str) -> Document | None: ...

@injectable
class FileDocumentStore:
    """File-based document store implementation."""

    def __init__(self, base_path: Path = inject.me()) -> None:
        self.base_path = base_path

    def store(self, document: Document) -> None:
        """Store document to file."""
        ...

    def retrieve(self, doc_id: str) -> Document | None:
        """Retrieve document from file."""
        ...

@injectable
class DocumentProcessor:
    """Document processor with injected dependencies."""

    def __init__(
        self,
        store: DocumentStore = inject.me(),
        config: ProcessorConfig = inject.me()
    ) -> None:
        self.store = store
        self.config = config
```

### Generic Injection Patterns
```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T], Protocol):
    """Generic repository protocol."""

    def save(self, entity: T) -> None: ...
    def find_by_id(self, entity_id: str) -> T | None: ...
    def find_all(self) -> list[T]: ...

@injectable
class DocumentRepository:
    """Document repository implementation."""

    def save(self, document: Document) -> None: ...
    def find_by_id(self, doc_id: str) -> Document | None: ...
    def find_all(self) -> list[Document]: ...

# The repository can be injected as Repository[Document]
@injectable
class DocumentService:
    def __init__(
        self,
        repository: Repository[Document] = inject.me()
    ) -> None:
        self.repository = repository
```

## Error Handling Types

### Exception Type Annotations
```python
from typing import NoReturn

class ProcessingError(Exception):
    """Base processing error."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause

def validate_input(data: Any) -> None:
    """Validate input data."""
    if not isinstance(data, dict):
        raise ProcessingError(f"Expected dict, got {type(data)}")

def critical_error(message: str) -> NoReturn:
    """Raise critical error and never return."""
    raise SystemError(message)

# ✅ Specific exception types in function signatures
def risky_operation() -> ProcessingResult:
    """Operation that may raise specific exceptions.

    Raises:
        ProcessingError: When processing fails
        ValueError: When input is invalid
        ConnectionError: When network fails
    """
    ...
```

### Result Types (Optional Pattern)
```python
from typing import Generic, TypeVar, Union
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

@dataclass(frozen=True)
class Success(Generic[T]):
    """Successful result container."""
    value: T

@dataclass(frozen=True)
class Failure(Generic[E]):
    """Failed result container."""
    error: E

Result = Union[Success[T], Failure[E]]

def safe_operation(data: str) -> Result[ProcessingResult, ProcessingError]:
    """Safe operation that returns Result type."""
    try:
        result = process_data(data)
        return Success(result)
    except ProcessingError as e:
        return Failure(e)

def handle_result(result: Result[ProcessingResult, ProcessingError]) -> None:
    """Handle result with type safety."""
    match result:
        case Success(value):
            print(f"Success: {value}")
        case Failure(error):
            print(f"Error: {error}")
```

## Literal Types and Enums

### Literal Types
```python
from typing import Literal

# ✅ Literal types for specific string values
ProcessorType = Literal["fast", "accurate", "balanced"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

def create_processor(
    processor_type: ProcessorType = "balanced"
) -> DocumentProcessor:
    """Create processor of specific type."""
    ...

def set_log_level(level: LogLevel) -> None:
    """Set logging level."""
    ...
```

### Enum Usage
```python
from enum import Enum, auto

class ProcessingStatus(Enum):
    """Processing status enumeration."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()

class DocumentType(str, Enum):
    """Document type with string values."""
    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"

def process_document(
    document: Document,
    doc_type: DocumentType
) -> ProcessingResult:
    """Process document based on type."""
    match doc_type:
        case DocumentType.TEXT:
            return process_text_document(document)
        case DocumentType.JSON:
            return process_json_document(document)
        case _:
            raise ValueError(f"Unsupported document type: {doc_type}")
```

## Mypy Configuration

### Strict Configuration
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Module-specific overrides
[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = false
disallow_untyped_defs = false  # More lenient for test files

[[tool.mypy.overrides]]
module = "third_party_package.*"
ignore_missing_imports = true
```

### Type Ignore Guidelines
```python
# ✅ Acceptable: Third-party library without types
import some_untyped_library  # type: ignore[import]

# ✅ Acceptable: Complex cases that mypy can't understand
result = complex_operation()  # type: ignore[attr-defined]

# ✅ With explanation comment
# mypy can't infer the type from this complex factory pattern
instance = factory.create()  # type: ignore[misc]

# ❌ Avoid: Broad type ignores without explanation
some_function()  # type: ignore

# ❌ Avoid: Ignoring errors that should be fixed
def untyped_function(x):  # type: ignore
    return x
```

## Runtime Type Checking

### Pydantic Integration
```python
from pydantic import BaseModel, Field, validator
from typing import Any

class DocumentMetadata(BaseModel):
    """Document metadata with runtime validation."""

    title: str = Field(..., min_length=1, max_length=200)
    author: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    version: int = Field(ge=1)

    @validator('tags')
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tag format."""
        for tag in v:
            if not tag.isalnum():
                raise ValueError(f"Invalid tag: {tag}")
        return v

class ProcessingConfig(BaseModel):
    """Processing configuration with validation."""

    max_workers: int = Field(ge=1, le=100)
    timeout: float = Field(gt=0, le=3600)
    retry_attempts: int = Field(ge=0, le=10)

    class Config:
        validate_assignment = True
        extra = "forbid"
```

### TypedDict Usage
```python
from typing import TypedDict, Required, NotRequired

class DocumentDict(TypedDict):
    """Typed dictionary for document data."""
    id: Required[str]
    title: Required[str]
    content: Required[str]
    metadata: NotRequired[dict[str, Any]]
    created_at: Required[str]  # ISO format string

def process_document_dict(doc: DocumentDict) -> ProcessingResult:
    """Process document from dictionary."""
    # Type checker knows all required fields are present
    return ProcessingResult(
        document_id=doc["id"],
        title=doc["title"],
        processed_content=process_content(doc["content"])
    )
```

## Type Checking Workflow

### Development Process
1. **Write type annotations** as you write code
2. **Run mypy frequently** during development
3. **Fix type errors immediately** - don't accumulate them
4. **Use type guards** for runtime type checking when needed
5. **Leverage IDE support** (Pylance) for real-time feedback

### Pre-commit Checklist
```bash
# 1. Run type checker
poetry run mypy src/

# 2. Check for type coverage gaps
poetry run mypy --html-report mypy-report src/

# 3. Verify no type: ignore additions without justification
git diff | grep "type: ignore"

# 4. Run tests to ensure types match runtime behavior
poetry run pytest
```

### Common Type Errors and Solutions

```python
# ❌ Error: Incompatible return value type
def get_document(doc_id: str) -> Document:
    result = database.query(doc_id)
    return result  # Error: result might be None

# ✅ Solution: Handle None case
def get_document(doc_id: str) -> Document:
    result = database.query(doc_id)
    if result is None:
        raise DocumentNotFoundError(f"Document {doc_id} not found")
    return result

# ❌ Error: Argument has incompatible type
def process_items(items: list[Document]) -> None:
    pass

process_items(["string", "items"])  # Error: list[str] not list[Document]

# ✅ Solution: Use proper types
documents = [Document(content=item) for item in ["string", "items"]]
process_items(documents)

# ❌ Error: Item has no attribute
def get_title(obj: Any) -> str:
    return obj.title  # Error: Any has no attribute 'title'

# ✅ Solution: Use protocol or type guard
def get_title(obj: HasTitle) -> str:
    return obj.title
```

## Performance Considerations

### Type Checking Performance
- **Use TYPE_CHECKING** for import-only type annotations
- **Avoid complex union types** in hot paths
- **Cache type checks** when doing runtime validation
- **Profile type checking time** for large modules

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # These imports only happen during type checking
    from expensive_module import ComplexType
    from another_module import HeavyClass

# Use string annotations for forward references
def process_data(data: "ComplexType") -> "HeavyClass":
    """Function with forward-referenced types."""
    ...
```