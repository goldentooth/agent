# Testing Standards

This document defines the testing standards and practices for the Goldentooth Agent project.

## Testing Philosophy

### Core Principles
- **Test-Driven Development (TDD)**: Write tests before implementation
- **Behavior-focused testing**: Test what the code does, not how it does it
- **Fast and reliable**: Tests should run quickly and consistently
- **Isolated**: Tests should not depend on external services or shared state

### Test-Driven Development Process
Follow the **Red-Green-Refactor** cycle:

1. **Red**: Write a failing test that defines a desired function or improvement
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve design while keeping tests green

#### TDD Implementation Steps
1. Write a failing test that defines a desired function or improvement
2. Run the test to confirm it fails as expected
3. Write minimal code to make the test pass
4. Run the test to confirm success
5. Refactor code to improve design while keeping tests green
6. Repeat the cycle for each new feature or bugfix

#### TDD Guidelines
- **Write tests before writing the implementation code**
- **Only write enough code to make the failing test pass**
- **Refactor code continuously while ensuring tests still pass**

### Coverage Requirements
- **Minimum overall coverage**: 85%
- **New code coverage**: 90%
- **Critical path coverage**: 100%
- **Public API coverage**: 100% of all public methods and functions
- **API coverage requirement**: We aim for 100% coverage of all API functionality. Do not write brittle tests that focus too much on implementation details; instead, ensure all functionality can be tested through module-level APIs. We want 100% coverage of every public API reachable from outside a given module.

### Testing Policies
- **NO EXCEPTIONS POLICY**: Under no circumstances should you mark any test type as "not applicable". Every project, regardless of size or complexity, MUST have unit tests, integration tests, AND end-to-end tests. If you believe a test type doesn't apply, you need the human to say exactly "I AUTHORIZE YOU TO SKIP WRITING TESTS THIS TIME"
- **Test output quality**: TEST OUTPUT MUST BE PRISTINE TO PASS
- **Error testing**: If the logs are supposed to contain errors, capture and test it.

## Test Organization

### Directory Structure
Tests mirror the source code structure exactly:

```
tests/
├── core/                       # Tests for src/goldentooth_agent/core/
│   ├── context/                # Context system tests
│   │   ├── test_context_basic.py
│   │   ├── test_context_computed.py
│   │   └── test_integration.py
│   ├── flow/                   # Flow system tests
│   ├── embeddings/             # Embeddings tests
│   ├── rag/                    # RAG system tests
│   └── ...
├── cli/                        # CLI tests
├── integration/                # Cross-module integration tests
└── conftest.py                 # Shared fixtures and configuration
```

### Test File Naming
- **Unit tests**: `test_<module_name>.py`
- **Integration tests**: `test_<feature>_integration.py`
- **End-to-end tests**: `test_<workflow>_e2e.py`
- **Performance tests**: `test_<feature>_performance.py`

## Test Categories

### Unit Tests
Test individual functions, methods, or classes in isolation.

```python
def test_document_processor_validates_input():
    """Unit test for input validation logic."""
    processor = DocumentProcessor()

    with pytest.raises(ValueError, match="cannot be empty"):
        processor.process([])

def test_context_key_creation():
    """Unit test for context key creation."""
    key = ContextKey.create("test.path", str, "Test description")

    assert key.path == "test.path"
    assert key.type == str
    assert key.description == "Test description"
```

### Integration Tests
Test interactions between multiple components.

```python
@pytest.mark.asyncio
async def test_rag_service_with_vector_store():
    """Integration test for RAG service and vector store."""
    # Setup
    vector_store = create_test_vector_store()
    rag_service = RAGService(vector_store=vector_store)

    # Test document storage and retrieval
    await rag_service.store_document("test content")
    results = await rag_service.query("test query")

    assert len(results) > 0
    assert "test content" in results[0].content
```

### End-to-End Tests
Test complete user workflows through the CLI or API.

```python
def test_chat_workflow_e2e(cli_runner):
    """End-to-end test of chat workflow."""
    result = cli_runner.invoke(
        main_app,
        ["chat", "--agent", "rag", "--message", "What is the project about?"]
    )

    assert result.exit_code == 0
    assert "goldentooth" in result.output.lower()
```

### Performance Tests
Test performance characteristics and benchmarks.

```python
@pytest.mark.benchmark
def test_vector_search_performance(benchmark, sample_vectors):
    """Benchmark vector search performance."""
    vector_store = create_test_vector_store(sample_vectors)
    query_vector = create_test_vector()

    result = benchmark(vector_store.search_similar, query_vector, limit=10)

    # Verify performance requirements
    assert benchmark.stats.mean < 0.1  # 100ms threshold
    assert len(result) == 10
```

## Test Implementation Patterns

### Test Structure (AAA Pattern)
```python
def test_feature():
    """Test description following AAA pattern."""
    # Arrange - Set up test data and dependencies
    processor = DocumentProcessor(config=test_config)
    documents = create_test_documents(count=5)

    # Act - Execute the code under test
    result = processor.process(documents)

    # Assert - Verify the results
    assert result.status == "completed"
    assert len(result.processed_documents) == 5
    assert all(doc.is_processed for doc in result.processed_documents)
```

### Fixture Usage
```python
@pytest.fixture
def test_config():
    """Provide test configuration."""
    return Config(
        timeout=10.0,
        max_retries=2,
        debug=True
    )

@pytest.fixture
def mock_vector_store():
    """Provide mock vector store for testing."""
    store = Mock(spec=VectorStore)
    store.search_similar.return_value = []
    return store

def test_with_fixtures(test_config, mock_vector_store):
    """Test using fixtures."""
    service = RAGService(
        config=test_config,
        vector_store=mock_vector_store
    )

    result = service.query("test")

    assert result is not None
    mock_vector_store.search_similar.assert_called_once()
```

### Async Test Patterns
```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async operations properly."""
    async with create_test_client() as client:
        result = await client.fetch_data("test_id")

        assert result.status == "success"

@pytest.mark.asyncio
async def test_async_error_handling():
    """Test async error handling."""
    client = create_failing_client()

    with pytest.raises(ClientError, match="connection failed"):
        await client.fetch_data("invalid_id")
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input_data,expected", [
    ("simple text", "SIMPLE TEXT"),
    ("MiXeD CaSe", "MIXED CASE"),
    ("", ""),
    ("123 numbers", "123 NUMBERS"),
])
def test_text_transformation(input_data, expected):
    """Test text transformation with various inputs."""
    result = transform_text(input_data)
    assert result == expected

@pytest.mark.parametrize("agent_type", ["rag", "simple", "flow"])
@pytest.mark.asyncio
async def test_agent_creation(agent_type):
    """Test creation of different agent types."""
    agent = await create_agent(agent_type)

    assert agent.type == agent_type
    assert agent.is_ready()
```

## Mock and Stub Patterns

### Service Mocking
```python
def test_service_with_external_dependency(mocker):
    """Test service that depends on external API."""
    # Mock the external service
    mock_api = mocker.patch('module.external_api')
    mock_api.fetch_data.return_value = {"status": "success"}

    # Test the service
    service = MyService()
    result = service.process_with_external_data("test_id")

    assert result.success is True
    mock_api.fetch_data.assert_called_once_with("test_id")
```

### Dependency Injection Testing
```python
def test_with_dependency_injection():
    """Test component with dependency injection."""
    # Create test world with mocked dependencies
    with world.test.clone(freeze=False) as test_world:
        mock_service = Mock(spec=ExternalService)
        test_world[ExternalService] = mock_service

        # Test the component
        component = inject(MyComponent)
        result = component.do_work()

        assert result is not None
        mock_service.process.assert_called()
```

### Async Mocking
```python
@pytest.mark.asyncio
async def test_async_service(mocker):
    """Test async service with mocked dependencies."""
    # Mock async dependency
    mock_async_service = AsyncMock()
    mock_async_service.fetch_data.return_value = {"data": "test"}

    mocker.patch('module.AsyncService', return_value=mock_async_service)

    # Test
    service = MyAsyncService()
    result = await service.process()

    assert result.data == "test"
    mock_async_service.fetch_data.assert_awaited_once()
```

## Test Data Management

### Test Data Creation
```python
def create_test_document(title="Test Document", content="Test content"):
    """Factory function for creating test documents."""
    return Document(
        id=f"test_{uuid.uuid4()}",
        title=title,
        content=content,
        created_at=datetime.now(),
        metadata={"test": True}
    )

@pytest.fixture
def sample_documents():
    """Provide sample documents for testing."""
    return [
        create_test_document("Doc 1", "Content about Python"),
        create_test_document("Doc 2", "Content about testing"),
        create_test_document("Doc 3", "Content about AI"),
    ]
```

### Database Testing
```python
@pytest.fixture
def test_db():
    """Provide isolated test database."""
    # Create temporary database
    db_path = ":memory:"  # SQLite in-memory database
    db = Database(db_path)
    db.initialize()

    yield db

    # Cleanup
    db.close()

def test_document_storage(test_db):
    """Test document storage in database."""
    document = create_test_document()

    test_db.store_document(document)
    retrieved = test_db.get_document(document.id)

    assert retrieved.title == document.title
    assert retrieved.content == document.content
```

### File System Testing
```python
@pytest.fixture
def temp_directory(tmp_path):
    """Provide temporary directory for file tests."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()

    # Create test files
    (test_dir / "test.txt").write_text("test content")
    (test_dir / "config.yaml").write_text("key: value")

    return test_dir

def test_file_processing(temp_directory):
    """Test file processing with temporary files."""
    processor = FileProcessor(temp_directory)

    result = processor.process_all_files()

    assert len(result) == 2
    assert "test.txt" in [f.name for f in result]
```

## Error Testing

### Exception Testing
```python
def test_error_conditions():
    """Test various error conditions."""
    processor = DocumentProcessor()

    # Test specific exception types
    with pytest.raises(ValueError, match="empty document"):
        processor.process("")

    with pytest.raises(ConfigurationError):
        processor.configure(invalid_config)

    # Test exception chaining
    with pytest.raises(ProcessingError) as exc_info:
        processor.process_invalid_data()

    assert exc_info.value.__cause__ is not None
```

### Async Error Testing
```python
@pytest.mark.asyncio
async def test_async_error_handling():
    """Test async error handling."""
    service = AsyncService()

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(service.slow_operation(), timeout=0.1)

    with pytest.raises(ConnectionError):
        await service.connect_to_invalid_endpoint()
```

## Test Configuration

### pytest Configuration
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/goldentooth_agent",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
    "benchmark: marks tests as performance benchmarks",
]
asyncio_mode = "auto"
```

### Test Environment
```python
# conftest.py
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "test_data"

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up clean test environment."""
    # Set test environment variables
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Disable external API calls
    monkeypatch.setenv("DISABLE_EXTERNAL_APIS", "true")

@pytest.fixture
def clean_registry():
    """Provide clean service registry for each test."""
    registry = ServiceRegistry()
    yield registry
    registry.clear()
```

## Performance Testing

### Benchmark Tests
```python
import pytest

@pytest.mark.benchmark(group="search")
def test_vector_search_benchmark(benchmark):
    """Benchmark vector search performance."""
    vector_store = create_large_vector_store()
    query = create_test_vector()

    result = benchmark(vector_store.search_similar, query, limit=10)

    assert len(result) == 10
    # Benchmark automatically captures timing statistics

@pytest.mark.benchmark(group="processing", min_rounds=5)
def test_document_processing_benchmark(benchmark):
    """Benchmark document processing with minimum rounds."""
    documents = create_test_documents(count=100)
    processor = DocumentProcessor()

    result = benchmark(processor.process_batch, documents)

    assert len(result) == 100
```

### Memory Usage Testing
```python
import tracemalloc

def test_memory_usage():
    """Test memory usage of operations."""
    tracemalloc.start()

    # Perform memory-intensive operation
    large_data = create_large_dataset()
    processor = MemoryEfficientProcessor()
    result = processor.process(large_data)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Assert memory usage is within acceptable limits
    assert peak < 100 * 1024 * 1024  # 100MB limit
    assert result is not None
```

## Test Quality Guidelines

### Test Characteristics
- **Fast**: Unit tests < 100ms, integration tests < 1s
- **Isolated**: No dependencies on external services or shared state
- **Repeatable**: Same results every time
- **Self-validating**: Clear pass/fail criteria
- **Timely**: Written before or with implementation

### Common Anti-patterns
```python
# ❌ Don't test implementation details
def test_internal_method_calls(mocker):
    service = MyService()
    spy = mocker.spy(service, '_internal_method')

    service.public_method()

    spy.assert_called_once()  # Too brittle!

# ✅ Test behavior instead
def test_public_method_behavior():
    service = MyService()

    result = service.public_method()

    assert result.status == "completed"
    assert result.data is not None

# ❌ Don't write overly complex tests
def test_complex_scenario():
    # 50 lines of setup...
    # Multiple assertions testing different things...
    # This should be split into multiple tests

# ✅ Write focused, simple tests
def test_single_behavior():
    # Simple setup
    service = MyService()

    # Single action
    result = service.do_one_thing()

    # Clear assertion
    assert result.success is True
```

### Test Maintenance
- **Review test failures promptly**: Don't ignore flaky tests
- **Refactor tests with code**: Keep tests aligned with implementation
- **Remove obsolete tests**: Delete tests for removed functionality
- **Update test data**: Keep test data relevant and realistic
- **Document complex test scenarios**: Explain why complex tests are necessary

## Continuous Integration

### Test Execution Strategy
```bash
# Fast test subset for development
poetry run pytest tests/unit/ -x --ff

# Full test suite for CI
poetry run pytest --cov=src/goldentooth_agent --cov-fail-under=85

# Performance regression tests
poetry run pytest tests/performance/ --benchmark-only

# Integration tests with external dependencies
poetry run pytest tests/integration/ --slow
```

### Quality Gates
- All tests must pass
- Code coverage ≥ 85%
- No new test warnings or errors
- Performance benchmarks within acceptable ranges
- Type checking passes (mypy)
```
