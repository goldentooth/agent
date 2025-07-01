"""Enhanced error reporting utilities for better debugging experience."""

from typing import Any


class DetailedAttributeError(AttributeError):
    """Enhanced AttributeError with context for better debugging."""

    def __init__(
        self, obj: Any, attr_name: str, context: dict[str, Any] | None = None
    ) -> None:
        """Initialize with detailed error information.

        Args:
            obj: The object that was accessed
            attr_name: The attribute name that was attempted
            context: Additional context information
        """
        self.obj_type = type(obj).__name__
        self.attr_name = attr_name
        self.context = context or {}

        # Get available attributes if possible
        available_attrs = []
        if hasattr(obj, "__dict__"):
            available_attrs = list(obj.__dict__.keys())
        elif isinstance(obj, dict):
            available_attrs = list(obj.keys())

        message = (
            f"'{self.obj_type}' object has no attribute '{attr_name}'\n"
            f"Object type: {self.obj_type}\n"
            f"Available attributes/keys: {available_attrs}\n"
            f"Context: {self.context}"
        )
        super().__init__(message)


_SENTINEL = object()


def safe_getattr(
    obj: Any, attr: str, default: Any = _SENTINEL, context: dict[str, Any] | None = None
) -> Any:
    """Safe attribute access with enhanced error reporting.

    Args:
        obj: Object to access attribute from
        attr: Attribute name to access
        default: Default value if attribute doesn't exist
        context: Additional context for error reporting

    Returns:
        The attribute value or default

    Raises:
        DetailedAttributeError: When attribute doesn't exist and no default
    """
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif default is not _SENTINEL:
        return default
    else:
        raise DetailedAttributeError(obj, attr, context)


def safe_dict_access(
    obj: dict[str, Any],
    key: str,
    default: Any = _SENTINEL,
    context: dict[str, Any] | None = None,
) -> Any:
    """Safe dictionary access with error reporting.

    Args:
        obj: Dictionary to access
        key: Key to look up
        default: Default value if key doesn't exist
        context: Additional context for error reporting

    Returns:
        The value or default

    Raises:
        DetailedAttributeError: When key doesn't exist and no default
    """
    if key in obj:
        return obj[key]
    elif default is not _SENTINEL:
        return default
    else:
        raise DetailedAttributeError(obj, key, context)
