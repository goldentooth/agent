# Mock Compliance Guidelines

**Problem**: Mock objects can drift from real implementations, causing tests to pass while production code fails. This "mock drift" is dangerous because it gives false confidence.

## The Mock Drift Problem

### What Happened
We encountered a test failure where:
1. `CodebaseCollection` was calling `vector_store.store_document(title=...)`
2. The real `VectorStore.store_document()` method doesn't have a `title` parameter
3. Our `MockVectorStore` was missing the `store_document` method entirely
4. Tests passed until production code tried to use the real interface

### Why It's Dangerous
- **False Security**: Tests pass but production fails
- **Silent Breakage**: Method signature changes don't break tests
- **Maintenance Burden**: Mocks become stale and unreliable
- **Type Safety Loss**: Mock interfaces diverge from reality

## Solution: Type-Safe Mock Framework

We've implemented a comprehensive solution with multiple safeguards:

### 1. Protocol-Based Interfaces (`tests/protocols.py`)

```python
@runtime_checkable
class VectorStoreProtocol(Protocol):
    def store_document(
        self,
        store_type: str,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str: ...
```

**Benefits:**
- Defines contracts that both real and mock implementations must follow
- Runtime checking ensures mocks actually implement the interface
- Type safety prevents signature drift

### 2. Type-Safe Mock Factory (`tests/mock_factories.py`)

```python
class TypeSafeMockVectorStore:
    """Type-safe mock implementation of VectorStoreProtocol."""

def create_vector_store_mock() -> VectorStoreProtocol:
    return TypeSafeMockVectorStore()
```

**Benefits:**
- Single source of truth for mock implementations
- Type annotations ensure signature compliance
- Centralized maintenance of mock behavior

### 3. Automated Compliance Testing (`tests/test_mock_compliance.py`)

```python
def test_store_document_signature_matches(self):
    """Test that store_document signatures match between real and mock."""
    real_sig = inspect.signature(VectorStore.store_document)
    mock_sig = inspect.signature(TypeSafeMockVectorStore.store_document)
    assert real_params == mock_params
```

**Benefits:**
- Automatically detects signature drift
- Runs as part of CI/CD pipeline
- Catches compliance issues before they reach production

## Implementation Guidelines

### 1. Creating New Mocks

**✅ DO:**
```python
# 1. Define protocol first
class ServiceProtocol(Protocol):
    def method(self, param: str) -> str: ...

# 2. Create type-safe mock
class TypeSafeMockService:
    def method(self, param: str) -> str:
        return f"mock-{param}"

# 3. Use factory function
def create_service_mock() -> ServiceProtocol:
    return TypeSafeMockService()
```

**❌ DON'T:**
```python
# Inline mock without type safety
class MockService:
    def some_method(self, wrong_params):  # No type hints
        pass
```

### 2. Updating Existing Mocks

**When real interface changes:**
1. Update the protocol definition
2. Update the mock implementation
3. Run compliance tests: `poetry run poe test-mocks`
4. Fix any signature mismatches

### 3. Test Organization

**Fixture Usage:**
```python
@pytest.fixture
def mock_service():
    """Use centralized mock factory."""
    from tests.mock_factories import create_service_mock
    return create_service_mock()
```

**Direct Usage:**
```python
def test_functionality():
    service = create_service_mock()
    result = service.method("test")
    assert result == "mock-test"
```

## Compliance Testing

### Running Mock Compliance Tests

```bash
# Test all mock compliance
poetry run poe test-mocks

# Include in quality assurance
poetry run poe qa  # Includes mock compliance
```

### Adding New Compliance Tests

When adding a new service with mocks:

1. **Add Protocol Test:**
```python
def test_new_service_mock_implements_protocol(self):
    mock = TypeSafeMockNewService()
    assert isinstance(mock, NewServiceProtocol)
```

2. **Add Signature Test:**
```python
def test_critical_method_signature_matches(self):
    real_sig = inspect.signature(RealService.critical_method)
    mock_sig = inspect.signature(TypeSafeMockService.critical_method)
    # Compare signatures...
```

3. **Add to CI/CD:**
```python
@pytest.mark.parametrize("method_name", ["method1", "method2"])
def test_method_signatures_compatible(self, method_name: str):
    # Automated signature checking
```

## Development Workflow

### Before Committing
```bash
poetry run poe qa  # See command-reference.md for all QA commands
```

### When Interface Changes
1. **Update real implementation**
2. **Update protocol** (if needed)
3. **Update mock implementation**
4. **Run compliance tests**
5. **Fix any test failures**

### When Adding New Dependencies
1. **Define protocol first**
2. **Create mock implementation**
3. **Add compliance tests**
4. **Use factory functions in fixtures**

## Benefits Achieved

### ✅ Prevented Issues
- **Mock drift detection**: Automatically catches signature mismatches
- **Type safety**: Compile-time checking of mock usage
- **Centralized maintenance**: Single place to update mock behavior
- **Regression prevention**: CI/CD catches compliance issues

### ✅ Development Improvements
- **Faster debugging**: Clear error messages when signatures don't match
- **Better documentation**: Protocols serve as interface documentation
- **Refactoring safety**: Mock compliance tests catch breaking changes
- **Team alignment**: Consistent mocking patterns across the codebase

## Tools Used

- **pytest-mock**: Enhanced mocking capabilities
- **typing.Protocol**: Runtime-checkable interfaces
- **inspect**: Signature comparison and validation
- **mypy**: Static type checking of mock implementations

## Commands Reference

See **[Command Reference](command-reference.md)** for all development commands. Key commands for mock compliance:

```bash
poetry run poe test-mocks  # Test mock compliance
poetry run poe qa          # All quality checks
```

## Migration Strategy

For existing codebases with mock drift issues:

1. **Audit current mocks** for compliance issues
2. **Define protocols** for key interfaces
3. **Create type-safe mocks** using the factory pattern
4. **Add compliance tests** for critical interfaces
5. **Migrate fixtures** to use centralized mock factories
6. **Run compliance checks** in CI/CD pipeline

This approach ensures mocks stay synchronized with real implementations, preventing the dangerous mock drift problem from recurring.
