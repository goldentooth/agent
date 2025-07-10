"""Search and query operations helper functions for Context system."""

import re
from typing import Any, Callable, Iterator

# Type aliases
ContextValue = Any
ContextData = dict[str, Any]
ValuePredicate = Callable[[Any], bool]


def query_context(
    keys_iter: Iterator[str],
    get_func: Callable[[str], ContextValue],
    is_computed_func: Callable[[str], bool],
    pattern: str | None = None,
    key_filter: Callable[[str], bool] | None = None,
    value_filter: ValuePredicate | None = None,
    include_computed: bool = True,
) -> ContextData:
    """Query the context with flexible filtering options.

    Args:
        keys_iter: Iterator of context keys
        get_func: Function to get value by key
        is_computed_func: Function to check if key is computed property
        pattern: Regex pattern to match against context keys
        key_filter: Function to filter keys based on custom logic
        value_filter: Function to filter values
        include_computed: Whether to include computed properties in results

    Returns:
        Dictionary of filtered key-value pairs
    """
    result: ContextData = {}

    # Compile regex pattern if provided
    compiled_pattern = None
    if pattern is not None:
        try:
            compiled_pattern = re.compile(pattern)
        except re.error:
            # Invalid regex pattern, return empty result
            return result

    # Iterate through all context keys
    for key in keys_iter:
        # Skip computed properties if not included
        if not include_computed and is_computed_func(key):
            continue

        # Apply pattern filter
        if compiled_pattern is not None and not compiled_pattern.search(key):
            continue

        # Apply key filter
        if key_filter is not None and not key_filter(key):
            continue

        # Get value and apply value filter
        try:
            value = get_func(key)
            if value_filter is not None and not value_filter(value):
                continue

            # Key passed all filters, include in result
            result[key] = value
        except Exception:
            # Skip keys that can't be accessed
            continue

    return result


def find_keys_by_pattern(
    keys_iter: Iterator[str],
    pattern: str,
) -> list[str]:
    """Find all keys matching a regex pattern.

    Args:
        keys_iter: Iterator of context keys
        pattern: Regex pattern to match against keys

    Returns:
        List of matching keys
    """
    try:
        regex = re.compile(pattern)
        return [key for key in keys_iter if regex.search(key)]
    except re.error:
        # Invalid regex pattern, return empty list
        return []


def search_context(
    keys_iter: Iterator[str],
    getitem_func: Callable[[str], ContextValue],
    search_term: str,
    case_sensitive: bool = False,
) -> ContextData:
    """Search for keys or values containing a term.

    Args:
        keys_iter: Iterator of context keys
        getitem_func: Function to get value by key (like __getitem__)
        search_term: Term to search for
        case_sensitive: Whether search should be case sensitive

    Returns:
        Dictionary of matching key-value pairs
    """
    if not case_sensitive:
        search_term = search_term.lower()

    def matches_search(key: str, value: ContextValue) -> bool:
        # Check key
        key_match = search_term in (key if case_sensitive else key.lower())

        # Check value (convert to string)
        try:
            value_str = str(value)
            if not case_sensitive:
                value_str = value_str.lower()
            value_match = search_term in value_str
        except Exception:
            value_match = False

        return key_match or value_match

    results: ContextData = {}
    for key in keys_iter:
        try:
            value = getitem_func(key)
            if matches_search(key, value):
                results[key] = value
        except Exception:
            continue

    return results
