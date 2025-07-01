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

        # Generate debugging suggestions
        debugging_suggestions = self._generate_debugging_suggestions(
            obj, attr_name, available_attrs
        )

        message = (
            f"'{self.obj_type}' object has no attribute '{attr_name}'\n\n"
            f"🔍 DEBUGGING INFO:\n"
            f"• Object type: {self.obj_type}\n"
            f"• Available attributes/keys: {available_attrs}\n"
            f"• Context: {self.context}\n\n"
            f"🔧 DEBUGGING TOOLS:\n"
            f"{debugging_suggestions}\n\n"
            f"📚 See: guidelines/debugging-guide.md#attribute-errors"
        )
        super().__init__(message)

    def _generate_debugging_suggestions(
        self, obj: Any, attr_name: str, available_attrs: list[str]
    ) -> str:
        """Generate context-aware debugging suggestions."""
        suggestions = []

        # Dict vs object access detection
        if isinstance(obj, dict):
            suggestions.append(
                f"• Use obj['{attr_name}'] for dictionary access instead of obj.{attr_name}"
            )
            if attr_name in obj:
                suggestions.append(f"  ✓ Key '{attr_name}' exists in dictionary")
        else:
            suggestions.append(
                f"• Use obj.{attr_name} for object access (verify object has this attribute)"
            )
            if hasattr(obj, "__dict__") and attr_name in obj.__dict__:
                suggestions.append(
                    f"  ✓ Attribute '{attr_name}' exists in object.__dict__"
                )

        # Similar attribute suggestions
        similar_attrs = [
            attr
            for attr in available_attrs
            if attr_name.lower() in attr.lower() or attr.lower() in attr_name.lower()
        ]
        if similar_attrs:
            suggestions.append(f"• Similar attributes found: {similar_attrs}")

        # Debugging command suggestions
        suggestions.extend(
            [
                "",
                "🔍 INVESTIGATE WITH:",
                "• Trace execution: goldentooth-agent debug trace --agent [type] '[query]' --verbose",
                "• Check system health: goldentooth-agent debug health",
                "• Interactive debugging: Use FlowDebugger in flow_engine/observability/debugging.py",
                "• Object inspection: Use inspect_stream() combinator for runtime analysis",
            ]
        )

        return "\n".join(suggestions)


_SENTINEL = object()


def safe_getattr(
    obj: Any, attr: str, default: Any = _SENTINEL, context: dict[str, Any] | None = None
) -> Any:
    """Safe attribute access with enhanced error reporting.

    This function provides enhanced debugging context when attribute access fails,
    including suggestions for debugging tools and common fixes.

    Args:
        obj: Object to access attribute from
        attr: Attribute name to access
        default: Default value if attribute doesn't exist
        context: Additional context for error reporting

    Returns:
        The attribute value or default

    Raises:
        DetailedAttributeError: When attribute doesn't exist and no default.
                              The error includes debugging suggestions and tool recommendations.

    Example:
        >>> # Safe access with debugging context
        >>> value = safe_getattr(response, "response", context={
        ...     "operation": "agent_processing",
        ...     "expected_type": "AgentResponse object"
        ... })
    """
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif default is not _SENTINEL:
        return default
    else:
        enhanced_context = context or {}
        enhanced_context.update(
            {
                "access_method": "getattr",
                "suggestion": f"Consider using dict access response['{attr}'] if object is actually a dictionary",
            }
        )
        raise DetailedAttributeError(obj, attr, enhanced_context)


def safe_dict_access(
    obj: dict[str, Any],
    key: str,
    default: Any = _SENTINEL,
    context: dict[str, Any] | None = None,
) -> Any:
    """Safe dictionary access with enhanced error reporting.

    This function provides enhanced debugging context when dictionary access fails,
    including suggestions for debugging tools and common fixes.

    Args:
        obj: Dictionary to access
        key: Key to look up
        default: Default value if key doesn't exist
        context: Additional context for error reporting

    Returns:
        The value or default

    Raises:
        DetailedAttributeError: When key doesn't exist and no default.
                              The error includes debugging suggestions and tool recommendations.

    Example:
        >>> # Safe access with debugging context
        >>> value = safe_dict_access(response_dict, "response", context={
        ...     "operation": "agent_response_parsing",
        ...     "expected_keys": ["response", "sources", "metadata"]
        ... })
    """
    if key in obj:
        return obj[key]
    elif default is not _SENTINEL:
        return default
    else:
        enhanced_context = context or {}
        enhanced_context.update(
            {
                "access_method": "dict_access",
                "suggestion": f"Check if key should be '{key}' or verify dictionary structure",
                "available_keys": list(obj.keys()),
            }
        )
        raise DetailedAttributeError(obj, key, enhanced_context)
