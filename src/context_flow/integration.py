"""Context-Flow integration core module.

This module provides the core integration between Context and Flow systems,
including exception classes, combinators, and decorator functions.
"""

__all__ = [
    "ContextFlowError",
    "MissingRequiredKeyError",
    "ContextTypeMismatchError",
]


class ContextFlowError(Exception):
    """Base exception for Context-Flow integration errors."""

    pass


class MissingRequiredKeyError(ContextFlowError):
    """Raised when a required context key is missing."""

    pass


class ContextTypeMismatchError(ContextFlowError):
    """Raised when a context key has the wrong type."""

    pass
