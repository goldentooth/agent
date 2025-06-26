from __future__ import annotations
from antidote import inject
import asyncio
from loguru import logger
from typing import Awaitable, Callable, TypeVar
import logging

from .main import Thunk

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")

TA = TypeVar("TA")
TB = TypeVar("TB")
TC = TypeVar("TC")


async def run_fold(ctx: TIn, steps: list[Thunk[TIn, TIn]]) -> TIn:
    """Execute a list of thunks sequentially, threading the context through each step.

    This is a fold/reduce operation where each thunk receives the output of the
    previous thunk as its input. Useful for building sequential processing pipelines.

    Args:
        ctx: The initial context value
        steps: List of thunks to execute in order

    Returns:
        The final context value after all steps have been executed

    Example:
        increment = Thunk(lambda x: x + 1, name="inc")
        double = Thunk(lambda x: x * 2, name="double")
        result = await run_fold(5, [increment, double])  # Returns 12: (5+1)*2
    """
    for step in steps:
        ctx = await step(ctx)
    return ctx


def compose(first: Thunk[TA, TB], second: Thunk[TB, TC]) -> Thunk[TA, TC]:
    """Compose two thunks, where the output of the first is the input to the second."""

    async def _thunk(ctx: TA) -> TC:
        """Call the first thunk, then pass its result to the second thunk."""
        result = await first(ctx)
        return await second(result)

    return Thunk(_thunk, name=f"{first.name} ∘ {second.name}")


def filter(predicate: Callable[[TIn], bool]) -> Thunk[TIn, TIn | None]:
    """Create a thunk that filters contexts based on a predicate."""

    async def _thunk(ctx):
        """Thunk to filter contexts based on a predicate."""
        return ctx if predicate(ctx) else None

    return Thunk(_thunk, name=f"filter({predicate.__name__})")


def map(fn: Callable[[TB], TC]) -> Callable[[Thunk[TA, TB]], Thunk[TA, TC]]:
    """Decorator to map a function over the result of a thunk."""

    def wrapper(inner: Thunk[TA, TB]) -> Thunk[TA, TC]:
        """Wrap the inner thunk and apply the function to its result."""

        async def _thunk(ctx: TA) -> TC:
            """Call the inner thunk and apply the function to its result."""
            result = await inner(ctx)
            return fn(result)

        return Thunk(
            _thunk, name=f"{inner.name}.map({getattr(fn, '__name__', '<lambda>')})"
        )

    return wrapper


def flat_map(
    fn: Callable[[TB], Thunk[TA, TC]],
) -> Callable[[Thunk[TA, TB]], Thunk[TA, TC]]:
    """Decorator to flat-map a function over the result of a thunk."""

    def wrapper(inner: Thunk[TA, TB]) -> Thunk[TA, TC]:
        """Wrap the inner thunk and apply the function to its result, returning a new thunk."""

        async def _thunk(ctx: TA) -> TC:
            """Call the inner thunk, get the result, and apply the function to it."""
            result = await inner(ctx)
            return await fn(result)(ctx)

        return Thunk(
            _thunk, name=f"{inner.name}.flat_map({getattr(fn, '__name__', 'function')})"
        )

    return wrapper


def flat_map_ctx(
    fn: Callable[[TB, TA], Thunk[TA, TC]],
) -> Callable[[Thunk[TA, TB]], Thunk[TA, TC]]:
    """Decorator to flat-map a function over the result of a thunk, passing the context."""

    def wrapper(inner: Thunk[TA, TB]) -> Thunk[TA, TC]:
        """Wrap the inner thunk and apply the function to its result with context."""

        async def _thunk(ctx: TA) -> TC:
            """Call the inner thunk, get the result, and apply the function with context."""
            result = await inner(ctx)
            return await fn(result, ctx)(ctx)

        return Thunk(
            _thunk,
            name=f"{inner.name}.flat_map_ctx({getattr(fn, '__name__', 'function')})",
        )

    return wrapper


def guard(predicate: Callable[[TIn], bool]) -> Thunk[TIn, TIn]:
    """Create a thunk that raises an exception if the predicate is not met."""

    async def _thunk(ctx: TIn) -> TIn:
        """Check the predicate and return the context if it passes."""
        if predicate(ctx):
            return ctx
        raise StopIteration("Guard failed")

    return Thunk(_thunk, name=f"guard({predicate.__name__})")


def log_ctx(
    name: str, *, prefix: str = "", level: int = logging.DEBUG
) -> Thunk[TIn, TIn]:
    """Create a thunk that logs the context value and returns it unchanged.

    Useful for debugging thunk pipelines by observing intermediate values
    without affecting the data flow.

    Args:
        name: Name for the thunk (used in pipeline visualization)
        prefix: Optional prefix to add before the logged context
        level: Logging level (defaults to DEBUG)
    """

    @inject  # Uses dependency injection to access the logger
    async def _thunk(ctx: TIn) -> TIn:
        """Log the context value and pass it through unchanged."""
        logger.log(level, f"{prefix}{ctx}")
        return ctx

    return Thunk(
        _thunk,
        name=f"log_ctx({name})",
        metadata={
            "prefix": prefix,
            "level": level,
        },
    )


def identity() -> Thunk[TIn, TIn]:
    """Create a thunk that returns the context unchanged."""

    async def _thunk(ctx: TIn) -> TIn:
        """Return the context unchanged."""
        return ctx

    return Thunk(_thunk, name="identity")


def if_then(
    predicate: Callable[[TIn], bool],
    if_thunk: Thunk[TIn, TOut],
    else_thunk: Thunk[TIn, TOut] = identity(),
) -> Thunk[TIn, TOut]:
    """Create a thunk that conditionally executes one of two thunks based on a predicate."""

    @inject
    async def _thunk(ctx: TIn) -> TOut:
        """Execute if_thunk if predicate is True, else execute else_thunk."""
        pred_result = predicate(ctx)
        if pred_result:
            return await if_thunk(ctx)
        else:
            return await else_thunk(ctx)

    return Thunk(
        _thunk,
        name=f"if_else({predicate.__name__}, {if_thunk.name}, {else_thunk.name})",
    )


def tap(
    fn: Callable[[TOut], Awaitable[None]],
) -> Callable[[Thunk[TIn, TOut]], Thunk[TIn, TOut]]:
    """Decorator to apply a function to the result of a thunk without changing the result."""

    def wrapper(inner: Thunk[TIn, TOut]) -> Thunk[TIn, TOut]:
        """Wrap the inner thunk and apply the function to its result."""

        async def _thunk(ctx: TIn) -> TOut:
            """Call the inner thunk, get the result, and apply the function to it."""
            result = await inner(ctx)
            await fn(result)
            return result

        return Thunk(
            _thunk, name=f"{inner.name}.tap({getattr(fn, '__name__', 'function')})"
        )

    return wrapper


def delay(seconds: float) -> Thunk[TIn, TIn]:
    """Create a thunk that delays execution for a given number of seconds."""

    async def _thunk(ctx: TIn) -> TIn:
        """Delay execution for the specified number of seconds."""
        await asyncio.sleep(seconds)
        return ctx

    return Thunk(_thunk, name=f"delay({seconds})")


def recover(
    handler: Callable[[Exception, TIn], Awaitable[TOut]],
) -> Callable[[Thunk[TIn, TOut]], Thunk[TIn, TOut]]:
    """Decorator to handle exceptions in a thunk and return a fallback value."""

    def wrapper(inner: Thunk[TIn, TOut]) -> Thunk[TIn, TOut]:
        """Wrap the inner thunk and handle exceptions with a handler."""

        async def _thunk(ctx: TIn) -> TOut:
            """Call the inner thunk and handle exceptions with the handler."""
            try:
                return await inner(ctx)
            except Exception as e:
                result = await handler(e, ctx)
                return result

        return Thunk(
            _thunk,
            name=f"{inner.name}.recover({getattr(handler, '__name__', 'handler')})",
        )

    return wrapper


def memoize(fn: Callable[[TIn], Awaitable[TOut]]) -> Thunk[TIn, TOut]:
    """Create a thunk that caches function results based on input context.

    Uses a simple in-memory dictionary cache with context values as keys.
    Cache is bound to this specific memoized instance and persists for its lifetime.

    WARNING: The cache grows unbounded and may cause memory leaks for long-running
    processes with many unique inputs. Consider using a more sophisticated cache
    with size limits or TTL for production use.

    Args:
        fn: The async function to memoize

    Returns:
        A thunk that caches results keyed by context value
    """
    cache = {}  # Simple unbounded cache - consider LRU cache for production

    async def _thunk(ctx: TIn) -> TOut:
        """Check cache first, compute and store result if cache miss."""
        if ctx in cache:
            return cache[ctx]
        result = await fn(ctx)
        cache[ctx] = result
        return result

    return Thunk(_thunk, name=f"memoize({fn.__name__})")


def while_true(
    condition: Callable[[TIn], bool], body: Thunk[TIn, TIn]
) -> Thunk[TIn, TIn]:
    """Create a thunk that repeatedly executes the body thunk while the condition is true."""

    async def _thunk(ctx: TIn) -> TIn:
        """Execute the body thunk repeatedly while the condition is true."""
        while condition(ctx):
            ctx = await body(ctx)
        return ctx

    return Thunk(_thunk, name=f"while_true({condition.__name__}, {body.name})")


def repeat(times: int, body: Thunk[TIn, TIn]) -> Thunk[TIn, TIn]:
    """Create a thunk that executes the body thunk a specified number of times."""

    async def _thunk(ctx: TIn) -> TIn:
        """Execute the body thunk the specified number of times."""
        for _ in range(times):
            ctx = await body(ctx)
        return ctx

    return Thunk(_thunk, name=f"repeat({times}, {body.name})")


def retry(n: int, thunk: Thunk[TIn, TOut]) -> Thunk[TIn, TOut]:
    """Create a thunk that retries the given thunk a specified number of times on failure."""

    async def _thunk(ctx: TIn) -> TOut:
        """Retry the thunk up to n times, raising the last exception if all attempts fail."""
        for i in range(n):
            try:
                return await thunk(ctx)
            except Exception as e:
                if i == n - 1:
                    raise e
        raise RuntimeError("Retry failed after {} attempts".format(n))

    return Thunk(_thunk, name=f"retry({n}, {thunk.name})")


def switch(
    selector: Callable[[TIn], str],
    cases: dict[str, Thunk[TIn, TOut]],
    default: Thunk[TIn, TOut] | None = None,
) -> Thunk[TIn, TOut]:
    """Create a thunk that selects a case based on the selector function."""

    async def _thunk(ctx: TIn) -> TOut:
        """Select a case based on the key returned by the selector function."""
        key = selector(ctx)
        if key in cases:
            return await cases[key](ctx)
        elif default:
            return await default(ctx)
        raise KeyError(f"No case for key: {key}")

    return Thunk(
        _thunk,
        name=f"switch({selector.__name__}, {list(cases.keys())}, {default.name if default else 'None'})",
    )


def race(thunks: list[Thunk[TIn, TOut]]) -> Thunk[TIn, TOut]:
    """Create a thunk that runs a list of thunks and returns the result of the first successful one."""

    async def _thunk(ctx: TIn) -> TOut:
        """Run each thunk in the list and return the result of the first one that succeeds."""
        last_exc = None
        for thunk in thunks:
            try:
                return await thunk(ctx)
            except Exception as e:
                last_exc = e
        if last_exc:
            raise last_exc
        raise RuntimeError("All thunks failed")

    return Thunk(
        _thunk, name="race({})".format(", ".join(thunk.name for thunk in thunks))
    )
