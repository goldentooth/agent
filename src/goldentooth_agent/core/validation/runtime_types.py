"""Runtime type validation decorators and utilities."""

import inspect
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, get_type_hints

logger = logging.getLogger(__name__)

T = TypeVar("T")


def validate_return_type(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to validate function return types at runtime.

    This helps catch type mismatches early during development,
    preventing issues like the dict/object attribute access error.

    Args:
        func: Function to wrap with type validation

    Returns:
        Wrapped function with runtime type checking
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)

        # Get type hints
        try:
            hints = get_type_hints(func)
        except Exception as e:
            # Skip validation if we can't get hints
            logger.debug(f"Could not get type hints for {func.__name__}: {e}")
            return result

        return_type = hints.get("return", Any)

        # Skip validation for Any
        if return_type is Any:
            return result

        # Validate return type
        if not isinstance(result, return_type):
            raise TypeError(
                f"{func.__name__} returned {type(result).__name__}, "
                f"expected {return_type}"
            )

        return result

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        result = await func(*args, **kwargs)

        try:
            hints = get_type_hints(func)
        except Exception as e:
            logger.debug(f"Could not get type hints for {func.__name__}: {e}")
            return result

        return_type = hints.get("return", Any)

        if return_type is not Any and not isinstance(result, return_type):
            raise TypeError(
                f"{func.__name__} returned {type(result).__name__}, "
                f"expected {return_type}"
            )

        return result

    return async_wrapper if inspect.iscoroutinefunction(func) else wrapper


def validate_dict_response(
    response: Any,
    required_keys: list[str] | None = None,
    optional_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Validate that a response is a dictionary with expected keys.

    Args:
        response: The response to validate
        required_keys: Keys that must be present
        optional_keys: Keys that may be present

    Returns:
        The validated dictionary

    Raises:
        TypeError: If response is not a dictionary
        KeyError: If required keys are missing
    """
    if not isinstance(response, dict):
        raise TypeError(f"Expected dict response, got {type(response).__name__}")

    if required_keys:
        missing_keys = [key for key in required_keys if key not in response]
        if missing_keys:
            raise KeyError(
                f"Response missing required keys: {missing_keys}. "
                f"Available keys: {list(response.keys())}"
            )

    # Log if unexpected keys are present (helps catch schema drift)
    if required_keys or optional_keys:
        expected_keys = set(required_keys or []) | set(optional_keys or [])
        unexpected_keys = set(response.keys()) - expected_keys
        if unexpected_keys:
            logger.warning(f"Response contains unexpected keys: {unexpected_keys}")

    return response
