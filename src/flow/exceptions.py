"""Custom exceptions for the Flow system."""


class FlowError(Exception):
    """Base exception for all Flow-related errors."""

    pass


class FlowValidationError(FlowError):
    """Raised when flow validation fails (e.g., guard conditions, assertions)."""

    pass


class FlowExecutionError(FlowError):
    """Raised when flow execution fails (e.g., all retries exhausted, circuit breaker open)."""

    pass


class FlowTimeoutError(FlowError):
    """Raised when flow operations timeout."""

    pass


class FlowConfigurationError(FlowError):
    """Raised when flow is incorrectly configured (e.g., invalid parameters)."""

    pass
