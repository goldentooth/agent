# Type Safety Guidelines

Comprehensive type safety standards for the Goldentooth Agent project.

## Core Principles
- **Strict type checking**: Zero tolerance for type errors in production code
- **Complete annotations**: All functions, methods, and complex variables must be typed
- **Runtime safety**: Type annotations should reflect actual runtime behavior

### Required Tools
- **mypy**: Static type checker in strict mode
- **Pylance**: VS Code language server for real-time checking
- **typing**: Standard library typing module

## Critical Rules

### 1. Always Add Return Type Annotations
**Problem**: Most common mypy error - missing return types

```python
# ❌ Missing return type
def process_data(items):
    return {"count": len(items)}

# ✅ Complete annotation
def process_data(items: list[str]) -> dict[str, int]:
    return {"count": len(items)}

async def fetch_data(url: str) -> dict[str, Any]:
    """Async functions need return types too."""
    return await api_call(url)
```

**Rule**: Every function must have a return type annotation, even `-> None`.

### 2. Handle External Library Returns
**Problem**: External libraries often return `Any`

```python
# ❌ yaml.safe_load returns Any
def load_config() -> dict[str, str]:
    return yaml.safe_load(file_content)

# ✅ Cast or validate
def load_config() -> dict[str, str]:
    data = yaml.safe_load(file_content)
    assert isinstance(data, dict)
    return data
```

### 3. Annotate Variables When Type Unclear
```python
# ❌ mypy can't infer these
window = deque(maxlen=size)
results = {}

# ✅ Explicit annotations
window: deque[Item] = deque(maxlen=size)
results: dict[str, Any] = {}
```

### 4. Modern Union Syntax
```python
# ✅ Python 3.10+ union syntax (required)
def get_data(source: str | Path) -> dict[str, Any] | None:
    return load_from_source(source)

# ✅ Handle optional parameters
def process_data(value: str | None = None) -> str:
    return value or "default"
```

## Essential Patterns

### Generic Types
```python
from typing import TypeVar, Generic, Protocol

T = TypeVar("T")
Input = TypeVar("Input")
Output = TypeVar("Output")

class Processor(Generic[Input, Output]):
    def __init__(self, transform_fn: Callable[[Input], Output]) -> None:
        self.transform_fn = transform_fn

    def process(self, item: Input) -> Output:
        return self.transform_fn(item)
```

### Protocols
```python
class DocumentStore(Protocol):
    def store(self, document: Document) -> None: ...
    def retrieve(self, doc_id: str) -> Document | None: ...

# Use in dependency injection
@injectable
class DocumentProcessor:
    def __init__(self, store: DocumentStore = inject.me()) -> None:
        self.store = store
```

### Type Guards
```python
from typing import TypeGuard

def is_document(obj: Any) -> TypeGuard[Document]:
    return hasattr(obj, 'id') and hasattr(obj, 'content')

def process_unknown_objects(objects: list[Any]) -> list[ProcessingResult]:
    documents = [obj for obj in objects if is_document(obj)]
    return [process_document(doc) for doc in documents]
```

### Async Types
```python
from typing import AsyncIterator, Awaitable

async def fetch_document(doc_id: str) -> Document:
    return await api_call(doc_id)

async def document_stream(query: str) -> AsyncIterator[Document]:
    async for doc in search_documents(query):
        yield doc

# Async callbacks
AsyncCallback = Callable[[Document], Awaitable[None]]
```

### Common Error Solutions

```python
# ❌ Function argument type mismatches
def process_items(items: list[str]) -> None:
    pass
process_items(123)  # Wrong type

# ✅ Correct types
items: list[str] = ["a", "b", "c"]
process_items(items)

# ❌ Assignment type incompatibilities
result: str = 123
optional_value: str = None

# ✅ Compatible assignments
result: str = "hello"
optional_value: str | None = None
```

### Exception Types
```python
from typing import NoReturn

class ProcessingError(Exception):
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause

def critical_error(message: str) -> NoReturn:
    """Function that never returns."""
    raise SystemError(message)
```

### Literal Types and Enums
```python
from typing import Literal
from enum import Enum

ProcessorType = Literal["fast", "accurate", "balanced"]

class DocumentType(str, Enum):
    TEXT = "text"
    JSON = "json"
    YAML = "yaml"

def process_document(doc: Document, doc_type: DocumentType) -> ProcessingResult:
    match doc_type:
        case DocumentType.TEXT:
            return process_text_document(doc)
        case DocumentType.JSON:
            return process_json_document(doc)
```

## Mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
disallow_any_generics = true
disallow_untyped_defs = true
no_implicit_optional = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### Type Ignore Guidelines
```python
# ✅ Third-party library without types
import some_untyped_library  # type: ignore[import]

# ✅ With explanation
# mypy can't infer the type from this factory pattern
instance = factory.create()  # type: ignore[misc]

# ❌ Avoid: Broad ignores without explanation
some_function()  # type: ignore
```

## Runtime Validation

### Pydantic Models
```python
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str | None = None
    tags: list[str] = Field(default_factory=list)
    version: int = Field(ge=1)

class ProcessingConfig(BaseModel):
    max_workers: int = Field(ge=1, le=100)
    timeout: float = Field(gt=0, le=3600)
```

### TypedDict for Structured Data
```python
from typing import TypedDict, Required, NotRequired

class DocumentDict(TypedDict):
    id: Required[str]
    title: Required[str]
    content: Required[str]
    metadata: NotRequired[dict[str, Any]]
```

## Development Workflow

### Pre-commit Checklist
- [ ] All functions have return type annotations
- [ ] Variables with unclear types are annotated
- [ ] Function calls match expected signatures
- [ ] Union types used for optional values

### Performance Tips
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import-only type annotations
    from expensive_module import ComplexType

# Use string annotations for forward references
def process_data(data: "ComplexType") -> "HeavyClass":
    pass
```

### Error Targets
Prioritize fixing:
1. `[no-untyped-def]` - Missing return type annotations
2. `[arg-type]` - Function argument type mismatches  
3. `[assignment]` - Assignment type incompatibilities
4. `[var-annotated]` - Missing variable type annotations
