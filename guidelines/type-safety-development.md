# Type Safety Development Guidelines

This document provides specific guidelines to prevent common type errors identified through mypy analysis.

## 🎯 Critical Rules (Always Follow)

### 1. **Always Add Return Type Annotations**
**Problem**: 34 `[no-untyped-def]` errors - the most common issue

```python
# ❌ Bad - Missing return type
def process_data(items):
    return {"count": len(items)}

def setup_connection():
    # This function doesn't return anything
    pass

# ✅ Good - Always specify return type
def process_data(items: list[str]) -> dict[str, int]:
    return {"count": len(items)}

def setup_connection() -> None:
    # Explicitly mark functions that don't return
    pass

async def async_process() -> list[str]:
    # Include async functions
    return []
```

**Rule**: Every function and method must have a return type annotation, even if it's `-> None`.

### 2. **Always Annotate Variable Types When Unclear**
**Problem**: 9 `[var-annotated]` errors

```python
# ❌ Bad - mypy can't infer complex types
window = deque(maxlen=size)
validation_errors = []
results = {}

# ✅ Good - Explicit type annotations
window: deque[Item] = deque(maxlen=size)
validation_errors: list[ValidationError] = []
results: dict[str, Any] = {}

# ✅ Also good - Type is clear from assignment
items = ["a", "b", "c"]  # list[str] is obvious
count = 0  # int is obvious
```

**Rule**: If mypy can't infer the type, add an explicit annotation.

### 3. **Ensure Function Arguments Match Expected Types**
**Problem**: 25 `[arg-type]` errors and 10 `[call-arg]` errors

```python
# ❌ Bad - Type mismatches
def process_items(items: list[str]) -> None:
    pass

process_items(123)  # Wrong type
process_items()     # Missing required argument

# ✅ Good - Correct types and arguments
items: list[str] = ["a", "b", "c"]
process_items(items)

# ✅ Handle optional arguments properly
def process_with_default(items: list[str], count: int = 10) -> None:
    pass

process_with_default(items)  # Uses default
process_with_default(items, 5)  # Explicit count
```

**Rule**: Always ensure function calls match the expected signature.

### 4. **Handle Assignment Type Compatibility**
**Problem**: 21 `[assignment]` errors

```python
# ❌ Bad - Incompatible assignments
result: str = 123
optional_value: str = None  # Should be str | None

# ✅ Good - Compatible types
result: str = "hello"
optional_value: str | None = None

# ✅ Proper Optional handling
def get_value() -> str | None:
    return None

value = get_value()
if value is not None:
    # Now mypy knows value is str
    processed = value.upper()
```

**Rule**: Ensure assignments are type-compatible. Use union types for optional values.

## 📋 Development Patterns

### Pattern 1: **Initialize Collections with Type Hints**

```python
# ✅ Preferred - Explicit typing for empty collections
results: list[ProcessResult] = []
cache: dict[str, CacheEntry] = {}
errors: set[str] = set()

# ✅ Alternative - Use factory functions when type is complex
from collections import defaultdict
groups: defaultdict[str, list[Item]] = defaultdict(list)
```

### Pattern 2: **Handle Async Return Types**

```python
# ✅ Correct async typing
async def fetch_data() -> list[DataItem]:
    return await api_call()

async def process_stream() -> AsyncIterator[Result]:
    async for item in stream:
        yield process_item(item)
```

### Pattern 3: **Proper Exception Handling**

```python
# ✅ Maintain type safety in exception handling
def safe_operation() -> Result | None:
    try:
        return perform_operation()
    except SpecificError:
        return None  # Explicit return for error case
```

### Pattern 4: **Generic Function Typing**

```python
from typing import TypeVar

T = TypeVar("T")

# ✅ Proper generic function
def identity(value: T) -> T:
    return value

# ✅ Bounded type variables for constraints
Numeric = TypeVar("Numeric", int, float)

def add_numbers(a: Numeric, b: Numeric) -> Numeric:
    return a + b
```

## 🚫 Common Anti-Patterns to Avoid

### 1. **Avoid `Any` Unless Necessary**
```python
# ❌ Avoid when possible
def process_data(data: Any) -> Any:
    return data

# ✅ Be specific when you can
def process_user_data(data: UserData) -> ProcessedData:
    return transform(data)

# ✅ Use `Any` only for truly dynamic cases
def handle_json_response(response: dict[str, Any]) -> None:
    # JSON can contain any types
    pass
```

### 2. **Don't Use Bare `except:`**
```python
# ❌ Bad - Catches everything, unclear types
try:
    result = risky_operation()
except:
    result = None

# ✅ Good - Specific exceptions, clear types
try:
    result = risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Operation failed: {e}")
    result = None
```

### 3. **Avoid Untyped Lambda Functions in Complex Cases**
```python
# ❌ Can cause type inference issues
items.map(lambda x: x.process().value)

# ✅ Clearer with explicit function
def extract_value(item: Item) -> str:
    return item.process().value

items.map(extract_value)
```

## 🔧 Pre-commit Checklist

Before committing code, ensure:

- [ ] All functions have return type annotations
- [ ] All variables with unclear types are annotated
- [ ] No `[no-untyped-def]` errors in your changes
- [ ] No `[var-annotated]` errors in your changes
- [ ] Function calls match expected signatures
- [ ] Union types are used for optional values

## 🛠️ IDE Configuration

Configure your IDE to show type hints:

### VS Code
```json
{
    "python.analysis.typeCheckingMode": "strict",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.inlayHints.functionReturnTypes": true,
    "python.analysis.inlayHints.variableTypes": true
}
```

### PyCharm
- Enable: Settings → Editor → Code Style → Python → Type hints → Show type hints

## 📊 Current Error Targets

Based on our codebase analysis, prioritize fixing:

1. **34 `[no-untyped-def]`** - Missing return type annotations (highest priority)
2. **25 `[arg-type]`** - Function argument type mismatches
3. **21 `[assignment]`** - Assignment type incompatibilities
4. **11 `[no-untyped-call]`** - Calls to untyped functions
5. **9 `[var-annotated]`** - Missing variable type annotations

These represent ~70% of current type errors and are preventable with proper development practices.

## 🎯 Success Metrics

- New code should introduce **zero** `[no-untyped-def]` errors
- Aim for **<5** total type errors per PR
- Maintain 100% return type annotation coverage for new functions
- Use explicit typing for all new collection initializations

Following these guidelines will prevent the vast majority of type errors and maintain the codebase's type safety standards.
