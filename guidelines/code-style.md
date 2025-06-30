# Code Style Guidelines

This document defines the code style standards for the Goldentooth Agent project.

## File Organization

### File Size Limits
- **Preferred maximum**: 500 lines per file
- **Absolute maximum**: 1000 lines per file
- **Action required**: Start refactoring when approaching 800 lines

### Class Limits
- **Maximum classes per file**: 5
- **Maximum methods per class**: 15
- **Maximum function length**: 50 lines (preferred), 100 lines (absolute maximum)

### Module Structure
```python
"""Module docstring describing purpose and key components."""

from __future__ import annotations

# Standard library imports
import asyncio
import sys
from pathlib import Path
from typing import Any, Optional

# Third-party imports
import typer
from antidote import inject, injectable

# Local imports
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow import Flow

# Module-level constants
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3

# Type aliases
ProcessorFunction = Callable[[Input], Output]

# Main implementation
```

## Import Standards

### Import Order
1. **Future imports**: `from __future__ import annotations`
2. **Standard library**: Alphabetically ordered
3. **Third-party packages**: Alphabetically ordered
4. **Local imports**: Relative to project root, alphabetically ordered

### Import Style
```python
# ✅ Preferred: Specific imports
from pathlib import Path
from typing import Any, Optional, Union

# ✅ Acceptable: Module imports for frequently used items
import asyncio
import json

# ❌ Avoid: Star imports (except in __init__.py)
from module import *

# ✅ Type-only imports when needed
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from goldentooth_agent.core.context import Context
```

## Naming Conventions

### General Rules
- **Functions and variables**: `snake_case`
- **Classes and exceptions**: `PascalCase`
- **Constants**: `ALL_CAPS`
- **Private attributes**: `_leading_underscore`
- **Protected attributes**: `_single_underscore`
- **Internal/mangled**: `__double_underscore__` (rare, avoid unless necessary)

### Specific Patterns
```python
# Functions
def process_documents(documents: list[str]) -> ProcessedResult:
    ...

def _internal_helper(data: Any) -> None:
    ...

# Classes
class DocumentProcessor:
    ...

class FlowExecutionError(Exception):
    ...

# Constants
MAX_DOCUMENT_SIZE = 1024 * 1024
DEFAULT_CONFIG_PATH = Path("config.yaml")

# Variables
document_count = 0
processing_queue: asyncio.Queue[Document] = asyncio.Queue()
```

### Type Variables
```python
# ✅ Descriptive names when possible
Input = TypeVar("Input")
Output = TypeVar("Output")
DocumentType = TypeVar("DocumentType", bound=BaseDocument)

# ✅ Generic single letters when context is clear
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
```

## Code Formatting

### Line Length
- **Maximum line length**: 88 characters (Black default)
- **Docstring line length**: 72 characters
- **Comment line length**: 72 characters

### String Formatting
```python
# ✅ Preferred: f-strings for simple cases
message = f"Processing {count} documents"

# ✅ Acceptable: format() for complex cases
template = "User {user.name} processed {stats.count} items in {duration:.2f}s"
result = template.format(user=current_user, stats=process_stats, duration=elapsed)

# ❌ Avoid: % formatting (legacy)
message = "Processing %d documents" % count
```

### Function Definitions
```python
# ✅ Short signatures
def process_data(items: list[str], max_count: int = 10) -> dict[str, Any]:
    ...

# ✅ Long signatures - break after parameters
def complex_operation(
    input_data: ComplexInputType,
    configuration: ConfigType,
    timeout: float = 30.0,
    retries: int = 3,
) -> ComplexOutputType:
    ...
```

### List/Dict Formatting
```python
# ✅ Short lists - single line
items = ["apple", "banana", "cherry"]

# ✅ Long lists - multiline with trailing comma
long_items = [
    "first_very_long_item_name",
    "second_very_long_item_name", 
    "third_very_long_item_name",
]

# ✅ Dictionary formatting
config = {
    "timeout": 30.0,
    "retries": 3,
    "enabled": True,
}
```

## Documentation Standards

### Docstring Format
```python
def complex_operation(input_data: InputType, config: ConfigType) -> OutputType:
    """Brief one-line description of what the function does.

    More detailed explanation if needed. Focus on the 'why' and 'how',
    not just restating the function signature.

    Args:
        input_data: Description of the input parameter and its constraints
        config: Configuration object controlling behavior

    Returns:
        Description of the return value and its structure

    Raises:
        SpecificError: When this specific error condition occurs
        AnotherError: When this other condition is encountered

    Example:
        >>> result = complex_operation(my_data, default_config)
        >>> print(result.status)
        'completed'
    """
```

### Class Documentation
```python
class DocumentProcessor:
    """Processes documents using configurable strategies.
    
    This class provides a high-level interface for document processing
    with support for multiple processing strategies and error recovery.
    
    Attributes:
        strategy: The current processing strategy
        config: Configuration controlling processor behavior
        
    Example:
        >>> processor = DocumentProcessor(strategy="fast")
        >>> result = processor.process(documents)
    """
    
    def __init__(self, strategy: str = "default") -> None:
        """Initialize the processor with the specified strategy.
        
        Args:
            strategy: Processing strategy ("fast", "accurate", "default")
        """
```

### Comment Guidelines
```python
# ✅ Explain why, not what
# Use exponential backoff to handle rate limiting gracefully
await asyncio.sleep(2 ** retry_count)

# ✅ Warn about non-obvious behavior  
# Note: This modifies the input list in-place
items.sort(key=lambda x: x.priority)

# ❌ Avoid stating the obvious
# Increment counter by 1
counter += 1
```

## Error Handling Style

### Exception Patterns
```python
# ✅ Specific exceptions
class DocumentProcessingError(Exception):
    """Raised when document processing fails."""

# ✅ Preserve exception chains
try:
    result = risky_operation()
except SpecificError as e:
    raise DocumentProcessingError(f"Failed to process document: {e}") from e

# ✅ Early returns for error conditions
def validate_input(data: InputType) -> None:
    if not data:
        raise ValueError("Input data cannot be empty")
    
    if not data.is_valid():
        raise ValueError(f"Invalid input data: {data.validation_errors}")
```

## Async Code Style

### Async Function Patterns
```python
# ✅ Clear async function names
async def fetch_document(document_id: str) -> Document:
    ...

async def process_documents_concurrently(documents: list[Document]) -> list[Result]:
    ...

# ✅ Proper async context management
async def safe_operation():
    async with aiofiles.open(file_path) as f:
        content = await f.read()
        return process_content(content)
```

### Async Error Handling
```python
# ✅ Proper async exception handling
async def safe_async_operation():
    try:
        return await async_operation()
    except asyncio.TimeoutError:
        logger.warning("Operation timed out, retrying...")
        raise
    except Exception as e:
        logger.error(f"Async operation failed: {e}")
        raise ProcessingError(f"Operation failed: {e}") from e
```

## Code Organization Patterns

### Class Organization
```python
class ExampleClass:
    """Class docstring."""
    
    # Class variables
    DEFAULT_TIMEOUT = 30.0
    
    def __init__(self, config: Config) -> None:
        """Initialize instance."""
        # Instance variables
        self.config = config
        self._cache: dict[str, Any] = {}
    
    # Public methods
    def public_method(self) -> Result:
        """Public method docstring."""
        ...
    
    # Private methods
    def _private_method(self) -> None:
        """Private method docstring."""
        ...
    
    # Properties
    @property
    def status(self) -> str:
        """Current status of the instance."""
        return self._status
    
    # Special methods
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config!r})"
```

### Module Organization
```python
# Module constants at top
DEFAULT_CONFIG = {"timeout": 30.0}

# Type definitions
ProcessorType = Callable[[Input], Output]

# Exception classes
class ModuleError(Exception):
    """Base exception for this module."""

# Main classes
class PrimaryClass:
    """Main functionality class."""

# Helper functions
def helper_function() -> None:
    """Module-level helper function."""

# Module initialization (if needed)
def initialize_module() -> None:
    """Initialize module state."""
```

## Tools and Automation

### Required Tools
- **Black**: Code formatting (`black .`)
- **isort**: Import sorting (`isort .`)
- **mypy**: Type checking (`mypy src/`)
- **ruff**: Linting (`ruff check .`)

### Pre-commit Checks
```bash
# Format code
black .
isort .

# Check types
poetry run poe typecheck

# Run linter
ruff check .

# Run tests
poetry run poe test
```

### Editor Configuration
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.ruff]
line-length = 88
target-version = "py311"
```

## Anti-Patterns to Avoid

### Code Smells
```python
# ❌ Avoid: God classes (too many responsibilities)
class EverythingProcessor:
    def process_documents(self): ...
    def send_emails(self): ...
    def backup_database(self): ...
    def generate_reports(self): ...

# ❌ Avoid: Magic numbers
timeout = 86400  # What is this number?

# ✅ Use named constants
SECONDS_PER_DAY = 86400
timeout = SECONDS_PER_DAY

# ❌ Avoid: Deeply nested conditions
if condition1:
    if condition2:
        if condition3:
            if condition4:
                # Too deep!
                
# ✅ Use early returns
if not condition1:
    return early_result
if not condition2:
    return other_result
# Main logic here
```

### Common Mistakes
```python
# ❌ Avoid: Mutable default arguments
def process_items(items: list[str] = []):  # Bug!
    ...

# ✅ Use None and create new instances
def process_items(items: list[str] | None = None):
    if items is None:
        items = []

# ❌ Avoid: Bare except clauses
try:
    risky_operation()
except:  # Too broad!
    pass

# ✅ Catch specific exceptions
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Expected error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```