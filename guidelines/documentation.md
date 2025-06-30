# Documentation Guidelines

This document defines the documentation standards and practices for the Goldentooth Agent project.

## Documentation Philosophy

### Core Principles
- **Documentation as code**: Documentation lives with code and evolves together
- **User-focused**: Write for the reader, not the writer
- **Maintain accuracy**: Keep documentation in sync with implementation
- **Progressive disclosure**: Start simple, provide depth when needed
- **Searchable and navigable**: Structure for easy discovery

### Documentation Types
1. **API Documentation**: Function/method signatures, parameters, return values
2. **Module Documentation**: README files explaining module purpose and structure  
3. **Architecture Documentation**: High-level system design and patterns
4. **User Documentation**: How to use the system (CLI, agents, workflows)
5. **Developer Documentation**: Contributing, setup, development workflow

## Module Documentation Standards

### README.md Requirements
Every module directory must contain a comprehensive README.md file with the following sections:

```markdown
# Module Name

Brief description of the module's purpose and primary responsibilities.

## Overview

Detailed explanation of what this module does, its role in the larger system,
and key concepts or patterns it implements.

## Architecture

High-level architecture diagram or description showing:
- Key components and their relationships
- Data flow patterns
- Integration points with other modules

## Key Components

### ComponentName
Description of the component, its responsibilities, and usage patterns.

```python
# Example usage
component = ComponentName(config)
result = component.process(data)
```

### AnotherComponent
...

## API Reference

### Public Functions

#### function_name(param1: Type, param2: Type) -> ReturnType
Description of what the function does.

**Parameters:**
- `param1`: Description of parameter
- `param2`: Description of parameter

**Returns:**
- Description of return value

**Raises:**
- `ExceptionType`: When this exception occurs

**Example:**
```python
result = function_name("value", 42)
```

### Classes

#### ClassName
Description of the class and its purpose.

**Methods:**
- `method_name()`: Brief description
- `another_method()`: Brief description

## Configuration

Description of any configuration options, environment variables, or settings.

```python
# Configuration example
config = {
    "setting1": "value",
    "setting2": 42
}
```

## Examples

Practical examples showing common usage patterns:

```python
# Basic usage
from goldentooth_agent.module import Component

component = Component()
result = component.process_data(input_data)
```

```python
# Advanced usage with configuration
component = Component(config={
    "advanced_option": True,
    "timeout": 30.0
})
```

## Testing

Information about testing the module:
- How to run tests
- Test data requirements
- Mock setup for dependencies

```bash
# Run module tests
poetry run pytest tests/module_name/

# Run specific test
poetry run pytest tests/module_name/test_component.py
```

## Dependencies

List of dependencies (both internal and external):

**Internal Dependencies:**
- `goldentooth_agent.core.context`: Context management
- `goldentooth_agent.core.flow`: Flow composition

**External Dependencies:**
- `anthropic`: Claude API client
- `numpy`: Numerical computations

## Performance Considerations

Performance characteristics and optimization notes:
- Expected performance benchmarks
- Memory usage patterns
- Scaling considerations
- Known bottlenecks

## Known Issues and Limitations

Current limitations and planned improvements:
- Issue descriptions
- Workarounds if available
- Plans for resolution

## Statistics

Automatically generated or manually maintained statistics:
- File count: X files
- Lines of code: ~X LOC
- Test coverage: X%
- Public API surface: X functions/classes

## Changelog

Recent significant changes to the module:
- Version/Date: Description of changes
- Version/Date: Description of changes
```

### Module README Update Requirements
- **Update trigger**: Any significant change to a Python file in the module
- **Content accuracy**: Ensure all information reflects current implementation
- **API completeness**: Document all public functions, classes, and methods
- **Example validity**: Verify all code examples work with current implementation

## Code Documentation Standards

### Function/Method Documentation
```python
def process_documents(
    documents: list[Document],
    config: ProcessingConfig | None = None,
    timeout: float = 30.0
) -> ProcessingResult:
    """Process a list of documents with optional configuration.
    
    This function processes documents using the configured strategy and
    returns a result containing processed documents and metadata.
    
    Args:
        documents: List of documents to process. Must not be empty.
        config: Optional processing configuration. Uses defaults if None.
        timeout: Maximum time to spend processing in seconds.
    
    Returns:
        ProcessingResult containing:
        - processed_documents: List of successfully processed documents
        - failed_documents: List of documents that failed processing
        - metadata: Processing statistics and timing information
    
    Raises:
        ValueError: If documents list is empty
        ProcessingError: If processing fails for all documents
        TimeoutError: If processing exceeds timeout
        
    Example:
        >>> docs = [Document(content="Hello"), Document(content="World")]
        >>> config = ProcessingConfig(strategy="fast")
        >>> result = process_documents(docs, config, timeout=60.0)
        >>> print(f"Processed {len(result.processed_documents)} documents")
        Processed 2 documents
        
    Note:
        This function is safe to call concurrently as it doesn't modify
        the input documents or maintain shared state.
    """
```

### Class Documentation
```python
class DocumentProcessor:
    """Processes documents using configurable strategies.
    
    The DocumentProcessor provides a high-level interface for document
    processing with support for multiple strategies, error recovery,
    and performance monitoring.
    
    This class is thread-safe and can be used concurrently from multiple
    coroutines. It maintains internal state for caching and optimization
    but doesn't modify input data.
    
    Attributes:
        strategy: Current processing strategy name
        config: Processing configuration
        stats: Processing statistics (read-only)
        
    Example:
        Basic usage:
        >>> processor = DocumentProcessor()
        >>> result = await processor.process(document)
        
        With custom configuration:
        >>> config = ProcessingConfig(strategy="accurate", timeout=60.0)
        >>> processor = DocumentProcessor(config)
        >>> results = await processor.process_batch(documents)
        
    See Also:
        ProcessingConfig: Configuration options
        ProcessingResult: Return value structure
        ProcessingStrategy: Available processing strategies
    """
    
    def __init__(
        self, 
        config: ProcessingConfig | None = None,
        cache_size: int = 1000
    ) -> None:
        """Initialize the document processor.
        
        Args:
            config: Processing configuration. Uses defaults if None.
            cache_size: Maximum number of cached processing results.
                       Set to 0 to disable caching.
        """
```

### Inline Comments
```python
def complex_processing_function(data: InputData) -> OutputData:
    """Process complex data with multiple stages."""
    
    # Validate input data structure and content
    if not self._validate_input(data):
        raise ValueError("Invalid input data structure")
    
    # Apply preprocessing transformations
    # Note: Order matters here - normalization must come before tokenization
    normalized = self._normalize_data(data)
    tokenized = self._tokenize_data(normalized)
    
    # Main processing pipeline
    # Using parallel processing for performance on large datasets
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(self._process_chunk, chunk)
            for chunk in self._chunk_data(tokenized)
        ]
        
        processed_chunks = [
            future.result() for future in as_completed(futures)
        ]
    
    # Combine results and apply post-processing
    combined = self._combine_chunks(processed_chunks)
    
    # Final validation before returning
    if not self._validate_output(combined):
        logger.warning("Output validation failed, using fallback")
        return self._fallback_processing(data)
    
    return combined
```

## API Documentation Standards

### Public API Documentation
All public APIs must be documented with:
- Clear purpose description
- Complete parameter documentation
- Return value specification
- Exception documentation
- Usage examples
- Performance characteristics (if relevant)

### Internal API Documentation
Internal APIs should have:
- Brief purpose description
- Parameter types and meanings
- Any side effects or state changes
- Relationships to other internal components

### Protocol Documentation
```python
from typing import Protocol

class DocumentStore(Protocol):
    """Protocol for document storage implementations.
    
    This protocol defines the interface that all document store
    implementations must provide. It supports both synchronous
    and asynchronous operations for maximum flexibility.
    
    Implementations should be thread-safe and handle concurrent
    access gracefully.
    
    Example implementations:
    - FileDocumentStore: File-based storage
    - DatabaseDocumentStore: Database-backed storage
    - MemoryDocumentStore: In-memory storage for testing
    """
    
    def store_document(self, document: Document) -> None:
        """Store a document in the store.
        
        Args:
            document: Document to store. Must have valid ID.
            
        Raises:
            DocumentExistsError: If document with same ID exists
            StorageError: If storage operation fails
        """
        ...
    
    def get_document(self, document_id: str) -> Document | None:
        """Retrieve a document by ID.
        
        Args:
            document_id: Unique identifier for the document
            
        Returns:
            Document if found, None otherwise
            
        Raises:
            StorageError: If retrieval operation fails
        """
        ...
```

## Architecture Documentation

### System Architecture Documentation
```markdown
# System Architecture

## Overview
High-level description of the system architecture, key design decisions,
and architectural patterns used.

## Core Components

### Component Diagram
```mermaid
graph TD
    A[CLI Layer] --> B[Application Layer]
    B --> C[Core Services]
    C --> D[Infrastructure]
```

### Data Flow
Description of how data flows through the system:

1. **Input**: User request via CLI
2. **Processing**: Request routing and agent selection
3. **Execution**: Agent processes request using core services
4. **Output**: Response returned to user

## Design Patterns

### Dependency Injection
The system uses Antidote for dependency injection to:
- Manage component lifecycle
- Enable testing with mocks
- Support configuration injection

### Flow-Based Architecture
Processing is implemented using composable flows:
- Immutable data processing
- Async generators for streaming
- Type-safe composition

## Integration Points

### External Systems
- **Claude API**: LLM interactions
- **Vector Database**: Semantic search
- **File System**: Document storage

### Internal Modules
- **Context System**: Shared state management
- **Event System**: Cross-component communication
- **Background Processing**: Async task execution

## Quality Attributes

### Performance
- Target response times for operations
- Scalability characteristics
- Resource usage patterns

### Reliability
- Error handling strategies
- Failure recovery mechanisms
- Data consistency guarantees

### Security
- Input validation approach
- Authentication/authorization
- Secret management
```

## User Documentation

### CLI Documentation
```markdown
# CLI Reference

## Overview
The Goldentooth Agent CLI provides access to AI-powered document
processing and chat capabilities.

## Installation
```bash
pip install goldentooth-agent
```

## Quick Start
```bash
# Interactive chat with default agent
goldentooth-agent chat

# RAG-powered document chat
goldentooth-agent chat --agent rag

# Single message mode
goldentooth-agent send "What is the project about?" --agent rag
```

## Commands

### chat
Start an interactive chat session.

**Usage:**
```bash
goldentooth-agent chat [OPTIONS]
```

**Options:**
- `--agent TEXT`: Agent type to use (default: "simple")
- `--config PATH`: Path to configuration file
- `--debug`: Enable debug logging

**Examples:**
```bash
# Use RAG agent for document-aware chat
goldentooth-agent chat --agent rag

# Chat with debug logging
goldentooth-agent chat --debug
```

### send
Send a single message and get response.

**Usage:**
```bash
goldentooth-agent send MESSAGE [OPTIONS]
```

**Arguments:**
- `MESSAGE`: Message to send to the agent

**Options:**
- `--agent TEXT`: Agent type to use
- `--output FORMAT`: Output format (text, json)

**Examples:**
```bash
# Send single message
goldentooth-agent send "Explain the architecture"

# Get JSON response
goldentooth-agent send "List features" --output json
```

## Configuration

### Configuration File
Create a `.goldentooth.yaml` file:

```yaml
agents:
  default: "rag"
  
rag:
  max_results: 10
  similarity_threshold: 0.1
  
llm:
  model: "claude-3-sonnet-20240229"
  max_tokens: 2000
```

### Environment Variables
- `ANTHROPIC_API_KEY`: Claude API key (required)
- `GOLDENTOOTH_CONFIG`: Path to configuration file
- `GOLDENTOOTH_DATA_DIR`: Data directory path
```

## Development Documentation

### Contributing Guide
```markdown
# Contributing to Goldentooth Agent

## Development Setup
1. Clone the repository
2. Install dependencies: `poetry install`
3. Set up pre-commit hooks: `pre-commit install`

## Development Workflow
1. Create feature branch
2. Write tests first (TDD)
3. Implement functionality
4. Update documentation
5. Run quality checks
6. Submit pull request

## Quality Standards
- Test coverage ≥ 85%
- All type checks pass
- Documentation is updated
- Performance requirements met

## Testing
```bash
# Run all tests
poetry run poe test

# Run specific test suite
poetry run pytest tests/core/

# Run with coverage
poetry run poe test-cov
```

## Code Review Checklist
- [ ] Tests cover new functionality
- [ ] Documentation is updated
- [ ] Type annotations are complete
- [ ] Performance is acceptable
- [ ] Error handling is appropriate
```

## Documentation Maintenance

### Automated Documentation
```python
def update_module_statistics(module_path: Path) -> dict[str, Any]:
    """Update module statistics in README."""
    stats = {
        "file_count": len(list(module_path.glob("*.py"))),
        "line_count": count_lines_of_code(module_path),
        "test_coverage": get_test_coverage(module_path),
        "public_api_count": count_public_api_elements(module_path)
    }
    return stats

def validate_documentation_examples():
    """Validate that documentation examples work."""
    # Extract and execute code examples from docstrings
    # Report any that fail to execute correctly
    pass
```

### Documentation Review Process
1. **Automated checks**: Verify examples execute correctly
2. **Accuracy review**: Ensure information matches implementation
3. **Clarity review**: Check for user-friendly language
4. **Completeness review**: Verify all public APIs are documented
5. **Link validation**: Check all internal/external links work

### Documentation Tools
- **Sphinx**: For comprehensive documentation sites
- **mkdocs**: For markdown-based documentation
- **docstring-parser**: For extracting API documentation
- **mermaid**: For diagrams and flowcharts
- **plantuml**: For complex architectural diagrams

## Documentation Anti-Patterns

### Common Issues to Avoid
```python
# ❌ Don't just restate the code
def get_user_name(user_id: str) -> str:
    """Gets the user name."""  # Not helpful!
    return database.get_user(user_id).name

# ✅ Explain the purpose and context
def get_user_name(user_id: str) -> str:
    """Retrieve the display name for a user.
    
    This function fetches the user's preferred display name
    from the database. If the user has not set a display name,
    it falls back to their username.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        User's display name or username if no display name set
        
    Raises:
        UserNotFoundError: If user_id doesn't exist
    """

# ❌ Don't write obvious comments
user_count = user_count + 1  # Increment user count

# ✅ Explain why, not what
user_count += 1  # Track total users for billing purposes

# ❌ Don't document internal implementation details
def process_data(data):
    """Uses algorithm X with parameter Y to process data."""
    
# ✅ Document behavior and interface
def process_data(data):
    """Transform raw data into structured format.
    
    Normalizes, validates, and enriches the input data
    according to the configured processing rules.
    """
```

### Outdated Documentation
- **Symptoms**: Examples that don't work, incorrect API signatures
- **Prevention**: Include documentation updates in definition of done
- **Detection**: Automated testing of documentation examples
- **Resolution**: Regular documentation audit and cleanup

This documentation framework ensures comprehensive, accurate, and maintainable documentation that serves both users and developers effectively.