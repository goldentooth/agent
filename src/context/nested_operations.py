"""Nested operations helper functions for Context system."""

from typing import Any, Callable, cast

# Type aliases
ContextValue = Any
ContextData = dict[str, Any]


def traverse_nested_path(
    initial_value: ContextValue,
    path_parts: list[str],
    full_path: str,
) -> ContextValue:
    """Traverse a nested path starting from an initial value.

    Args:
        initial_value: The starting value
        path_parts: List of path components to traverse (excluding the first)
        full_path: The full path string for error messages

    Returns:
        The value at the end of the path

    Raises:
        KeyError: If the path cannot be traversed
    """
    current = initial_value

    for part in path_parts:
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(
                    f"Path '{full_path}' not found - missing '{part}' in {current}"
                )
            current = current[part]  # pyright: ignore[reportUnknownVariableType]
        elif hasattr(current, part):  # pyright: ignore[reportUnknownArgumentType]
            current = getattr(  # pyright: ignore[reportUnknownArgumentType]
                current, part  # pyright: ignore[reportUnknownArgumentType]
            )
        else:
            raise KeyError(
                f"Path '{full_path}' not found - '{part}' not accessible in {type(current)}"  # pyright: ignore[reportUnknownArgumentType]
            )

    return current  # pyright: ignore[reportUnknownVariableType]


def set_nested_value(
    get_func: Callable[[str], ContextValue],
    set_func: Callable[[str, ContextValue], None],
    path: str,
    value: ContextValue,
    delimiter: str = ".",
    create_missing: bool = True,
) -> None:
    """Set a nested value using getter/setter functions.

    Args:
        get_func: Function to get a value by key
        set_func: Function to set a value by key
        path: Dot-separated path to set
        value: Value to set
        delimiter: Path delimiter
        create_missing: Whether to create missing intermediate dictionaries

    Raises:
        KeyError: If path cannot be set
    """
    parts = path.split(delimiter)

    if len(parts) == 1:
        # Simple case - just set the value
        set_func(parts[0], value)
        return

    # Navigate to parent and set final key
    try:
        current_value = get_func(parts[0])
    except (KeyError, AttributeError):
        current_value = None

    if current_value is None:
        if not create_missing:
            raise KeyError(f"Cannot set '{path}' - '{parts[0]}' does not exist")
        current_dict: ContextData = {}
        set_func(parts[0], current_dict)
        current_value = current_dict

    # Navigate through intermediate parts
    for part in parts[1:-1]:
        if not isinstance(current_value, dict):
            if not create_missing:
                raise KeyError(f"Cannot set '{path}' - '{part}' is not a dictionary")
            # Cannot replace non-dict with dict, this is an error condition
            raise KeyError(f"Cannot set '{path}' - parent is not a dictionary")

        if part not in current_value:
            if not create_missing:
                raise KeyError(f"Cannot set '{path}' - '{part}' does not exist")
            current_value[part] = {}

        current_value = current_value[  # pyright: ignore[reportUnknownVariableType]
            part
        ]

    # Set final value
    if not isinstance(current_value, dict):
        raise KeyError(f"Cannot set '{path}' - parent is not a dictionary")

    current_value[parts[-1]] = value


def flatten_dict_recursive(
    obj: ContextData,
    delimiter: str = ".",
    max_depth: int | None = None,
    prefix: str = "",
    depth: int = 0,
) -> ContextData:
    """Recursively flatten a dictionary.

    Args:
        obj: Dictionary to flatten
        delimiter: Delimiter for keys
        max_depth: Maximum depth to flatten
        prefix: Current key prefix
        depth: Current depth

    Returns:
        Flattened dictionary
    """
    items: ContextData = {}

    for key, value in obj.items():
        new_key = f"{prefix}{delimiter}{key}" if prefix else key

        if isinstance(value, dict) and (max_depth is None or depth < max_depth):
            # Handle empty dictionaries
            if not value:
                items[new_key] = value
            else:
                # Type assertion for pyright
                typed_value = cast(ContextData, value)
                items.update(
                    flatten_dict_recursive(
                        typed_value,
                        delimiter,
                        max_depth,
                        new_key,
                        depth + 1,
                    )
                )
        else:
            items[new_key] = value

    return items
