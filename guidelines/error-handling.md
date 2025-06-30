# Error Handling Guidelines

This document defines error handling patterns, exception strategies, and async error handling best practices for the Goldentooth Agent project.

## Error Handling Philosophy

### Core Principles
- **Fail fast**: Detect and report errors as early as possible
- **Fail safe**: Graceful degradation when possible
- **Error context**: Preserve context and chain exceptions appropriately
- **User experience**: Provide meaningful error messages to users
- **Debugging support**: Include sufficient information for troubleshooting

### Error Categories
1. **Configuration errors**: Invalid configuration, missing settings
2. **Input validation errors**: Invalid user input, malformed data
3. **Service errors**: External service failures, network issues
4. **Processing errors**: Business logic failures, computation errors
5. **System errors**: Resource exhaustion, infrastructure failures

## Exception Hierarchy

### Project Exception Structure
```python
class GoldentoothError(Exception):
    """Base exception for Goldentooth Agent.
    
    All project-specific exceptions should inherit from this base class
    to enable consistent error handling and reporting.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: str | None = None,
        context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": str(self),
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

# Configuration-related exceptions
class ConfigurationError(GoldentoothError):
    """Raised when configuration is invalid or missing."""

class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid."""

# Input validation exceptions
class ValidationError(GoldentoothError):
    """Raised when input validation fails."""

class InvalidInputError(ValidationError):
    """Raised when input data is invalid."""

class InputFormatError(ValidationError):
    """Raised when input format is incorrect."""

# Service-related exceptions
class ServiceError(GoldentoothError):
    """Base exception for service-related errors."""

class ServiceUnavailableError(ServiceError):
    """Raised when external service is unavailable."""

class ServiceTimeoutError(ServiceError):
    """Raised when service operation times out."""

class AuthenticationError(ServiceError):
    """Raised when authentication fails."""

# Flow-related exceptions
class FlowError(GoldentoothError):
    """Base exception for flow-related errors."""

class FlowExecutionError(FlowError):
    """Raised when flow execution fails."""

class FlowConfigurationError(FlowError):
    """Raised when flow configuration is invalid."""

class FlowTimeoutError(FlowError):
    """Raised when flow execution times out."""

# RAG-related exceptions
class RAGError(GoldentoothError):
    """Base exception for RAG-related errors."""

class DocumentNotFoundError(RAGError):
    """Raised when document is not found."""

class EmbeddingError(RAGError):
    """Raised when embedding operation fails."""

class QueryExpansionError(RAGError):
    """Raised when query expansion fails."""

# LLM-related exceptions
class LLMError(GoldentoothError):
    """Base exception for LLM-related errors."""

class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""

class LLMQuotaExceededError(LLMError):
    """Raised when LLM quota is exceeded."""

class InvalidPromptError(LLMError):
    """Raised when prompt is invalid."""
```

## Error Handling Patterns

### Input Validation
```python
from typing import Any
from goldentooth_agent.core.validation import validate_input

def validate_document_input(raw_input: Any) -> Document:
    """Validate and convert raw input to Document.
    
    Args:
        raw_input: Raw input data from user
        
    Returns:
        Validated Document object
        
    Raises:
        InvalidInputError: If input is invalid
        InputFormatError: If input format is incorrect
    """
    # Type validation
    if not isinstance(raw_input, dict):
        raise InputFormatError(
            f"Expected dict input, got {type(raw_input).__name__}",
            context={"input_type": type(raw_input).__name__}
        )
    
    # Required field validation
    required_fields = ["content", "title"]
    missing_fields = [field for field in required_fields if field not in raw_input]
    if missing_fields:
        raise InvalidInputError(
            f"Missing required fields: {missing_fields}",
            context={"missing_fields": missing_fields, "provided_fields": list(raw_input.keys())}
        )
    
    # Content validation
    content = raw_input["content"]
    if not isinstance(content, str) or not content.strip():
        raise InvalidInputError(
            "Document content must be non-empty string",
            context={"content_type": type(content).__name__, "content_length": len(content) if isinstance(content, str) else 0}
        )
    
    # Size validation
    if len(content) > 1_000_000:  # 1MB limit
        raise InvalidInputError(
            f"Document content too large: {len(content)} chars (max: 1,000,000)",
            context={"content_size": len(content), "max_size": 1_000_000}
        )
    
    try:
        return Document(
            title=str(raw_input["title"]).strip(),
            content=content.strip(),
            metadata=raw_input.get("metadata", {})
        )
    except Exception as e:
        raise InvalidInputError(
            f"Failed to create Document: {e}",
            context={"original_error": str(e)}
        ) from e
```

### Configuration Validation
```python
from pathlib import Path
from typing import Any

def validate_configuration(config: dict[str, Any]) -> None:
    """Validate system configuration.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        MissingConfigurationError: If required config is missing
        InvalidConfigurationError: If config values are invalid
    """
    # Check required configuration
    required_keys = ["api_key", "data_dir", "model_name"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise MissingConfigurationError(
            f"Missing required configuration keys: {missing_keys}",
            context={"missing_keys": missing_keys, "available_keys": list(config.keys())}
        )
    
    # Validate API key
    api_key = config["api_key"]
    if not isinstance(api_key, str) or not api_key.strip():
        raise InvalidConfigurationError(
            "API key must be non-empty string",
            context={"api_key_type": type(api_key).__name__}
        )
    
    # Validate data directory
    data_dir = config["data_dir"]
    try:
        data_path = Path(data_dir)
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
        if not data_path.is_dir():
            raise InvalidConfigurationError(
                f"Data directory path is not a directory: {data_dir}",
                context={"data_dir": str(data_dir), "exists": data_path.exists()}
            )
    except Exception as e:
        raise InvalidConfigurationError(
            f"Invalid data directory: {e}",
            context={"data_dir": str(data_dir), "error": str(e)}
        ) from e
    
    # Validate model name
    model_name = config["model_name"]
    valid_models = ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    if model_name not in valid_models:
        raise InvalidConfigurationError(
            f"Invalid model name: {model_name}",
            context={"model_name": model_name, "valid_models": valid_models}
        )
```

### Service Error Handling
```python
import asyncio
from typing import Any, Callable, TypeVar

T = TypeVar("T")

async def with_retry(
    operation: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_exceptions: tuple[type[Exception], ...] = (ServiceError,)
) -> T:
    """Execute operation with exponential backoff retry.
    
    Args:
        operation: Async operation to execute
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay in seconds
        retry_exceptions: Exception types that trigger retries
        
    Returns:
        Result of the operation
        
    Raises:
        Last exception if all retries are exhausted
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except retry_exceptions as e:
            last_exception = e
            
            if attempt == max_retries:
                # Final attempt failed
                break
            
            # Calculate delay with exponential backoff
            delay = min(base_delay * (2 ** attempt), max_delay)
            
            logger.warning(
                f"Operation failed (attempt {attempt + 1}/{max_retries + 1}), "
                f"retrying in {delay:.1f}s: {e}",
                extra={
                    "attempt": attempt + 1,
                    "max_attempts": max_retries + 1,
                    "delay": delay,
                    "error": str(e)
                }
            )
            
            await asyncio.sleep(delay)
        except Exception as e:
            # Non-retryable exception
            raise e
    
    # All retries exhausted
    raise ServiceError(
        f"Operation failed after {max_retries + 1} attempts",
        context={
            "max_retries": max_retries,
            "last_error": str(last_exception),
            "last_error_type": type(last_exception).__name__
        }
    ) from last_exception

# Usage example
async def fetch_with_retry(url: str) -> dict[str, Any]:
    """Fetch data with automatic retry on service errors."""
    
    async def fetch_operation() -> dict[str, Any]:
        try:
            response = await http_client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            raise ServiceTimeoutError(f"Request to {url} timed out") from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                # Server error - retryable
                raise ServiceUnavailableError(f"Server error: {e.response.status_code}") from e
            else:
                # Client error - not retryable
                raise ServiceError(f"HTTP error: {e.response.status_code}") from e
    
    return await with_retry(
        fetch_operation,
        max_retries=3,
        retry_exceptions=(ServiceUnavailableError, ServiceTimeoutError)
    )
```

### Context Preservation
```python
def preserve_error_context(operation_name: str):
    """Decorator to preserve error context in operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except GoldentoothError:
                # Re-raise project exceptions as-is
                raise
            except Exception as e:
                # Wrap other exceptions with context
                raise FlowExecutionError(
                    f"Error in {operation_name}: {e}",
                    context={
                        "operation": operation_name,
                        "function": func.__name__,
                        "args_types": [type(arg).__name__ for arg in args],
                        "kwargs_keys": list(kwargs.keys()),
                        "original_error": str(e),
                        "original_error_type": type(e).__name__
                    }
                ) from e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except GoldentoothError:
                raise
            except Exception as e:
                raise FlowExecutionError(
                    f"Error in {operation_name}: {e}",
                    context={
                        "operation": operation_name,
                        "function": func.__name__,
                        "original_error": str(e)
                    }
                ) from e
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Usage
@preserve_error_context("document_processing")
async def process_document(document: Document) -> ProcessedDocument:
    """Process document with error context preservation."""
    # Processing logic that may raise various exceptions
    ...
```

## Async Error Handling

### Async Operation Patterns
```python
import asyncio
from typing import AsyncIterator

async def safe_async_iterator(
    source: AsyncIterator[T],
    error_handler: Callable[[Exception, T | None], None] | None = None
) -> AsyncIterator[T]:
    """Safely iterate over async iterator with error handling.
    
    Args:
        source: Source async iterator
        error_handler: Optional error handler for individual items
        
    Yields:
        Items from source iterator, skipping failed items
    """
    try:
        async for item in source:
            try:
                yield item
            except Exception as e:
                if error_handler:
                    error_handler(e, item)
                else:
                    logger.error(f"Error processing item {item}: {e}", exc_info=True)
                # Continue with next item
                continue
    except Exception as e:
        # Iterator itself failed
        if error_handler:
            error_handler(e, None)
        else:
            logger.error(f"Async iterator failed: {e}", exc_info=True)
        raise

async def gather_with_error_handling(
    *aws: Awaitable[T],
    return_exceptions: bool = True,
    error_handler: Callable[[Exception], None] | None = None
) -> list[T | Exception]:
    """Gather async operations with error handling.
    
    Args:
        *aws: Awaitable objects to gather
        return_exceptions: Whether to return exceptions instead of raising
        error_handler: Optional error handler for exceptions
        
    Returns:
        List of results or exceptions
    """
    results = await asyncio.gather(*aws, return_exceptions=return_exceptions)
    
    if error_handler:
        for result in results:
            if isinstance(result, Exception):
                error_handler(result)
    
    return results

# Usage example
async def process_documents_safely(
    documents: list[Document]
) -> list[ProcessedDocument]:
    """Process documents with comprehensive error handling."""
    
    def handle_processing_error(error: Exception, document: Document | None = None):
        """Handle individual document processing errors."""
        if document:
            logger.error(
                f"Failed to process document {document.id}: {error}",
                extra={"document_id": document.id, "error_type": type(error).__name__}
            )
        else:
            logger.error(f"Document processing error: {error}")
    
    # Process documents concurrently with error handling
    processing_tasks = [
        process_single_document(doc) for doc in documents
    ]
    
    results = await gather_with_error_handling(
        *processing_tasks,
        error_handler=handle_processing_error
    )
    
    # Filter out exceptions and return successful results
    successful_results = [
        result for result in results 
        if not isinstance(result, Exception)
    ]
    
    return successful_results
```

### Timeout Handling
```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def timeout_context(timeout: float, operation_name: str):
    """Context manager for timeout handling with meaningful errors.
    
    Args:
        timeout: Timeout in seconds
        operation_name: Name of operation for error messages
        
    Raises:
        ServiceTimeoutError: If operation times out
    """
    try:
        async with asyncio.timeout(timeout):
            yield
    except asyncio.TimeoutError as e:
        raise ServiceTimeoutError(
            f"Operation '{operation_name}' timed out after {timeout}s",
            context={"timeout": timeout, "operation": operation_name}
        ) from e

# Usage
async def fetch_data_with_timeout(url: str) -> dict[str, Any]:
    """Fetch data with timeout handling."""
    async with timeout_context(30.0, f"fetch_data({url})"):
        response = await http_client.get(url)
        return response.json()

async def process_with_per_item_timeout(
    items: list[T],
    processor: Callable[[T], Awaitable[R]],
    item_timeout: float = 10.0
) -> list[R]:
    """Process items with per-item timeout."""
    results = []
    
    for i, item in enumerate(items):
        try:
            async with timeout_context(item_timeout, f"process_item_{i}"):
                result = await processor(item)
                results.append(result)
        except ServiceTimeoutError as e:
            logger.warning(f"Item {i} processing timed out: {e}")
            # Continue with next item
            continue
    
    return results
```

## Error Recovery Strategies

### Fallback Patterns
```python
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")

async def with_fallback(
    primary_operation: Callable[[], Awaitable[T]],
    fallback_operation: Callable[[], Awaitable[T]],
    fallback_exceptions: tuple[type[Exception], ...] = (ServiceError,)
) -> T:
    """Execute operation with fallback on specific exceptions.
    
    Args:
        primary_operation: Primary operation to try
        fallback_operation: Fallback operation if primary fails
        fallback_exceptions: Exception types that trigger fallback
        
    Returns:
        Result from primary or fallback operation
    """
    try:
        return await primary_operation()
    except fallback_exceptions as e:
        logger.warning(
            f"Primary operation failed, using fallback: {e}",
            extra={"error_type": type(e).__name__, "error": str(e)}
        )
        try:
            return await fallback_operation()
        except Exception as fallback_error:
            # Both operations failed
            raise ServiceError(
                "Both primary and fallback operations failed",
                context={
                    "primary_error": str(e),
                    "fallback_error": str(fallback_error),
                    "primary_error_type": type(e).__name__,
                    "fallback_error_type": type(fallback_error).__name__
                }
            ) from e

# Usage example
async def search_documents_with_fallback(query: str) -> list[Document]:
    """Search documents with fallback to simple search."""
    
    async def vector_search():
        return await vector_store.search_similar(query, limit=10)
    
    async def keyword_search():
        return await document_store.search_by_keywords(query, limit=10)
    
    return await with_fallback(
        vector_search,
        keyword_search,
        fallback_exceptions=(EmbeddingError, ServiceUnavailableError)
    )
```

### Circuit Breaker Pattern
```python
import time
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3

class CircuitBreaker:
    """Circuit breaker for service resilience."""
    
    def __init__(self, config: CircuitBreakerConfig = CircuitBreakerConfig()):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
    
    async def call(self, operation: Callable[[], Awaitable[T]]) -> T:
        """Execute operation through circuit breaker."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise ServiceUnavailableError(
                    "Circuit breaker is OPEN - service is unavailable",
                    context={
                        "state": self.state.value,
                        "failure_count": self.failure_count,
                        "last_failure": self.last_failure_time
                    }
                )
        
        try:
            result = await operation()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
llm_circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30.0
))

async def call_llm_with_circuit_breaker(prompt: str) -> str:
    """Call LLM with circuit breaker protection."""
    async def llm_operation():
        response = await llm_client.generate(prompt)
        return response.content
    
    return await llm_circuit_breaker.call(llm_operation)
```

## Error Reporting and Monitoring

### Structured Error Logging
```python
import structlog
from typing import Any

logger = structlog.get_logger()

class ErrorReporter:
    """Centralized error reporting and monitoring."""
    
    def __init__(self) -> None:
        self.error_counts: dict[str, int] = {}
    
    def report_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
        severity: str = "error"
    ) -> None:
        """Report error with structured logging."""
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        error_data = {
            "error_type": error_type,
            "error_message": str(error),
            "error_count": self.error_counts[error_type],
            "severity": severity
        }
        
        if context:
            error_data.update(context)
        
        if isinstance(error, GoldentoothError):
            error_data.update({
                "error_code": error.error_code,
                "error_context": error.context,
                "timestamp": error.timestamp.isoformat()
            })
        
        # Log with appropriate level
        if severity == "critical":
            logger.critical("Critical error occurred", **error_data)
        elif severity == "error":
            logger.error("Error occurred", **error_data, exc_info=error)
        elif severity == "warning":
            logger.warning("Warning condition", **error_data)
        
        # Send to monitoring system if configured
        self._send_to_monitoring(error_data)
    
    def _send_to_monitoring(self, error_data: dict[str, Any]) -> None:
        """Send error data to monitoring system."""
        # Implementation would send to metrics/monitoring system
        # e.g., Prometheus, DataDog, etc.
        pass
    
    def get_error_summary(self) -> dict[str, int]:
        """Get summary of error counts."""
        return self.error_counts.copy()

# Global error reporter
error_reporter = ErrorReporter()

def report_error(error: Exception, **context):
    """Convenience function for error reporting."""
    error_reporter.report_error(error, context)
```

### Health Check Integration
```python
from goldentooth_agent.core.observability.health import HealthCheck

async def error_rate_health_check() -> bool:
    """Health check based on error rates."""
    total_errors = sum(error_reporter.get_error_summary().values())
    
    # Consider system healthy if fewer than 10 errors in recent window
    return total_errors < 10

# Register health check
health_monitor.register_check(
    "error_rate",
    "Monitor system error rates",
    error_rate_health_check,
    critical=True
)
```

This comprehensive error handling framework ensures robust, debuggable, and maintainable error management throughout the system.