"""Common fixtures and helpers for basic flow combinator tests."""


# Helper functions to replace lambdas and eliminate type: ignore comments
def increment(x: int) -> int:
    """Add 1 to the input."""
    return x + 1


def double(x: int) -> int:
    """Multiply input by 2."""
    return x * 2


def identity(x: int) -> int:
    """Return input unchanged."""
    return x


def int_to_str(x: int) -> str:
    """Convert integer to string."""
    return str(x)


def str_length(s: str) -> int:
    """Get length of string."""
    return len(s)


def is_even(x: int) -> bool:
    """Check if number is even."""
    return x % 2 == 0


def always_true(x: int) -> bool:
    """Always return True."""
    return True


def length_and_upper(s: str) -> str:
    """Transform string to UPPER:length format."""
    return f"{s.upper()}:{len(s)}"


def is_positive(x: int) -> bool:
    """Check if number is positive."""
    return x > 0


def is_non_zero(x: int) -> bool:
    """Check if number is non-zero."""
    return x != 0


def is_zero(x: int) -> bool:
    """Check if number is zero."""
    return x == 0


def equals_five(x: int) -> bool:
    """Check if number equals 5."""
    return x == 5
