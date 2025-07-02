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
6. **Debugging Documentation**: Error scenarios, troubleshooting, common issues

## Module Documentation Standards

### README.md Requirements
**ENFORCED RULE**: Every Python module or submodule should have a comprehensive README.md describing the contents of the module, usage examples, key components, dependencies, file count, lines-of-code and other statistics, test coverage statistics, etc. This file should be updated for accuracy whenever a Python file contained in the module is touched. The README.md must always contain a full specification of the public API.

Every module directory must contain a comprehensive README.md file with the following sections:

```markdown
# Module Name
Brief description of purpose and responsibilities.

## Overview
Detailed explanation of module's role in the larger system.

## Key Components
### ComponentName
Description and usage patterns.

## API Reference
#### function_name(param1: Type, param2: Type) -> ReturnType
Description, parameters, returns, exceptions.

## Examples
```python
from goldentooth_agent.module import Component
component = Component()
result = component.process_data(input_data)
```

## Testing
```bash
poetry run pytest tests/module_name/  # See command-reference.md
```

## Dependencies
**Internal:** Core modules used
**External:** Third-party packages

## Statistics
- File count, LOC, test coverage, API surface
```

### Module README Update Requirements
- **Update trigger**: Any significant change to a Python file in the module
- **Content accuracy**: Ensure all information reflects current implementation
- **API completeness**: Document all public functions, classes, and methods
- **Example validity**: Verify all code examples work with current implementation

### Module Metadata Requirements (README.meta.yaml)

**AUTOMATED MANAGEMENT**: README.meta.yaml files are automatically generated and maintained by pre-commit hooks.

#### Required Structure
```yaml
module_name: Flow Engine Core
complexity: Low  # Low, Medium, High, Critical
file_count: 4
loc: ~400
test_coverage: High
class_count: 4
function_count: 16

internal_dependencies:
  - goldentooth_agent.flow_engine.protocols

external_dependencies:
  - typing
  - asyncio

symbols:
  - Flow
  - FlowError
  - FlowFactory

exports:
  - Flow
  - FlowError
  - FlowFactory
```

#### Field Definitions

**Basic Metadata:** module_name, complexity, file_count, loc, test_coverage, class_count, function_count
**Dependencies:** internal_dependencies, external_dependencies  
**Symbol Tracking:** symbols (all defined), exports (from `__init__.py`)

Examples automatically generated for each module type by pre-commit hooks.

#### Maintenance
Automatically updated by pre-commit hooks when modules change.


**Automation Opportunities:**
```python
def validate_module_metadata(module_path: Path) -> list[str]:
    """Validate README.meta.yaml against actual module content."""
    errors = []

    meta_file = module_path / "README.meta.yaml"
    if not meta_file.exists():
        errors.append(f"Missing README.meta.yaml in {module_path}")
        return errors

    with open(meta_file) as f:
        metadata = yaml.safe_load(f)

    # Validate file count
    actual_files = len(list(module_path.glob("*.py")))
    declared_files = metadata.get("file_count", 0)
    if abs(actual_files - declared_files) > 1:
        errors.append(
            f"File count mismatch: declared {declared_files}, "
            f"actual {actual_files}"
        )

    # Validate symbols exist
    init_file = module_path / "__init__.py"
    if init_file.exists():
        # Parse __init__.py and verify exports
        # ... implementation

    return errors

```

This metadata system enables:
- **Dependency tracking**: Understand module relationships
- **Complexity assessment**: Identify modules needing attention
- **API surface documentation**: Track what each module exports
- **Automated validation**: Verify metadata accuracy against actual code

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
class DocumentStore(Protocol):
    """Protocol for document storage implementations.
    
    Implementations should be thread-safe and handle concurrent access.
    """
    
    def store_document(self, document: Document) -> None:
        """Store a document. Args, returns, raises documented."""
        ...
        
    def get_document(self, document_id: str) -> Document | None:
        """Retrieve document by ID. Returns None if not found."""
        ...
```

## Architecture Documentation

### System Architecture Documentation
```markdown
# System Architecture

## Overview
High-level system description, key design decisions, and patterns.

## Core Components
Component diagram and data flow description.

## Design Patterns
- **Dependency Injection**: Antidote for component lifecycle
- **Flow-Based**: Composable async processing flows

## Integration Points
**External:** Claude API, Vector Database, File System
**Internal:** Context, Event, and Background Processing systems

## Quality Attributes
**Performance:** Response times, scalability
**Reliability:** Error handling, recovery
**Security:** Input validation, secret management
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
1. Clone repository
2. `poetry install`
3. `pre-commit install`

## Workflow
1. Create feature branch, write tests first (TDD)
2. Implement functionality, update documentation
3. Run quality checks, submit pull request

## Quality Standards
Test coverage ≥ 85%, type checks pass, documentation updated

## Testing
See command-reference.md for all test commands
```

## Documentation Maintenance

### Automated Documentation
Module statistics and documentation examples are automatically validated by pre-commit hooks.

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

## Debugging Documentation Standards

**All complex functions must include debugging information in docstrings:**
- Common issues and solutions
- Debugging steps and recovery strategies
- Error scenarios with symptoms and fixes

**Module README troubleshooting:**
Each module README must include a troubleshooting section covering:
- Common AttributeError/KeyError patterns
- Performance debugging steps
- Development tool usage

See **[Debugging Guide](debugging-guide.md)** for comprehensive debugging documentation.

## Documentation Anti-Patterns

**Avoid:**
- Restating code without explanation
- Obvious comments (increment counter vs why incrementing)
- Documenting implementation details vs behavior

**Best Practices:**
- Explain purpose and context
- Focus on 'why' not 'what'
- Document interface and behavior
- Keep examples current and tested
