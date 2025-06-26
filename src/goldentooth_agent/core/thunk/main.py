from __future__ import annotations
from goldentooth_agent.core.util import maybe_await
import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    overload,
    TypeVar,
    NoReturn,
)

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")
TNew = TypeVar("TNew")


class Thunk(Generic[TIn, TOut]):
    """A composable async computation that transforms input contexts to output values.
    
    Thunks are the core abstraction for building modular, composable operations in
    the Goldentooth Agent framework. They wrap both synchronous and asynchronous
    functions in a uniform interface that enables functional composition patterns.
    
    Key features:
    - Uniform async interface (sync functions are auto-wrapped)
    - Functional composition via map, flat_map, chain, etc.
    - Control flow operations (repeat, while, conditional)
    - Error handling and recovery patterns
    - Metadata and naming for debugging/visualization
    
    Type Parameters:
        TIn: The input context type
        TOut: The output value type
        
    Example:
        # Create thunks from functions
        increment = Thunk(lambda x: x + 1, name="increment")
        double = Thunk(lambda x: x * 2, name="double")
        
        # Compose them into pipelines
        pipeline = increment.chain(double)  # or increment >> double
        result = await pipeline(5)  # Returns 12: (5 + 1) * 2
    """

    def __init__(
        self,
        fn: Callable[[TIn], Awaitable[TOut]] | Callable[[TIn], TOut],
        name: str,
        metadata: dict[str, Any] = {},
    ) -> None:
        """Initialize the thunk with a function."""
        if not callable(fn):
            raise TypeError("Thunk requires a callable")
        if not inspect.iscoroutinefunction(fn):
            # Wrap synchronous functions in an async wrapper so all thunks can be uniformly awaited.
            # This allows both sync and async functions to be used interchangeably in thunk composition.
            original_fn = fn  # Store reference to original function before reassignment

            async def _wrapper(ctx: TIn) -> TOut:
                """Wrap synchronous function to make it awaitable while preserving its behavior."""
                return original_fn(ctx)  # type: ignore

            fn = _wrapper
        self.fn = fn
        self.name = name or fn.__name__ or "<anonymous>"
        self.metadata: dict[str, Any] = metadata
        self.__name__ = self.name

    def __repr__(self):
        """Return a string representation of the thunk."""
        return f"<Thunk name={self.name} metadata={self.metadata}>"

    async def __call__(self, ctx: TIn) -> TOut:
        """Call the thunk with the given context."""
        return await self.fn(ctx)

    @classmethod
    def from_thunks(cls, *thunks) -> Thunk[TIn, TOut]:
        """Create a thunk that runs multiple thunks in sequence."""
        return compose_chain(*thunks)

    def map(self, fn: Callable[[TOut], TNew]) -> Thunk[TIn, TNew]:
        """Map a function over the result of the thunk."""

        async def _mapped(ctx: TIn) -> TNew:
            """Call the thunk and apply the function to its result."""
            return fn(await self(ctx))

        return Thunk(_mapped, name=f"{self.name}.map({fn.__name__})")

    def filter(self, predicate: Callable[[TOut], bool]) -> Thunk[TIn, TOut | None]:
        """Filter the result of the thunk based on a predicate."""

        async def _filtered(ctx: TIn) -> TOut | None:
            """Call the thunk and return the result if it matches the predicate."""
            result = await self(ctx)
            return result if predicate(result) else None

        return Thunk(_filtered, name=f"{self.name}.filter({predicate.__name__})")

    def flat_map(self, fn: Callable[[TOut], Thunk[TIn, TNew]]) -> Thunk[TIn, TNew]:
        """Apply a function that returns a thunk, then execute that thunk with the original context.
        
        This is the monadic bind operation for thunks. The function receives the result
        of this thunk and returns a new thunk, which is then executed with the original
        context. Useful for conditional or dynamic thunk composition.
        
        Args:
            fn: Function that takes this thunk's result and returns a new thunk
            
        Returns:
            A new thunk that executes both operations in sequence
            
        Example:
            def create_thunk(result):
                if result > 0:
                    return Thunk(lambda x: x * 2, name="double")
                else:
                    return Thunk(lambda x: x + 10, name="add_ten")
            
            base = Thunk(lambda x: x - 5, name="subtract")
            dynamic = base.flat_map(create_thunk)
            # Behavior depends on whether (input - 5) is positive
        """

        async def _flat(ctx: TIn) -> TNew:
            """Call the thunk, get the result, and apply the function to it."""
            return await fn(await self(ctx))(ctx)

        return Thunk(_flat, name=f"{self.name}.flat_map({fn.__name__})")

    def then(self, next_thunk: Thunk[TIn, TNew]) -> Thunk[TIn, TNew]:
        """Execute this thunk for side effects, then run the next thunk with the same context.
        
        The result of this thunk is discarded, making this useful for sequencing
        operations where you care about the side effects (like logging or state changes)
        but want to use the original context for the next operation.
        
        Args:
            next_thunk: The thunk to execute after this one
            
        Returns:
            A thunk that runs both operations but returns only the second result
            
        Example:
            log_thunk = Thunk(lambda x: print(f"Processing: {x}"), name="log")
            process_thunk = Thunk(lambda x: x * 2, name="double")
            
            pipeline = log_thunk.then(process_thunk)
            # Logs the input, then returns the doubled value
        """

        async def _thunk(ctx: TIn) -> TNew:
            """Call this thunk, then run the next thunk with the same context."""
            _ = await self(ctx)
            return await next_thunk(ctx)

        return Thunk(_thunk, name=f"{self.name}.then({next_thunk.name})")

    def flatten(self: Thunk[TIn, Thunk[TIn, TNew]]) -> Thunk[TIn, TNew]:
        """Collapse a thunk-of-thunks into a single thunk."""

        async def _flattened(ctx: TIn) -> TNew:
            """Call this thunk, which returns another thunk, and execute it."""
            inner = await self(ctx)
            return await inner(ctx)

        return Thunk(_flattened, name=f"{self.name}.flatten")

    @overload
    def repeat(self: Thunk[TIn, TIn], times: int) -> Thunk[TIn, TIn]: ...
    @overload
    def repeat(self: Thunk[TIn, TOut], times: int) -> NoReturn: ...

    def repeat(self, times: int):
        """Repeat this thunk a specified number of times.
        
        IMPORTANT: This method only works for thunks where input and output types are the same,
        since the output of each iteration becomes the input to the next iteration.
        
        Args:
            times: Number of times to repeat the thunk execution
            
        Returns:
            A thunk that applies this operation repeatedly
            
        Example:
            increment = Thunk(lambda x: x + 1, name="inc")
            add_five = increment.repeat(5)
            result = await add_five(10)  # Returns 15
        """
        from .combinators import repeat

        return repeat(times, self)  # type: ignore

    @overload
    def while_(
        self: Thunk[TIn, TIn], condition: Callable[[TIn], bool]
    ) -> Thunk[TIn, TIn]: ...
    @overload
    def while_(
        self: Thunk[TIn, TOut], condition: Callable[[TIn], bool]
    ) -> NoReturn: ...

    def while_(self, condition: Callable[[TIn], bool]):
        """Repeat this thunk while the condition remains true.
        
        IMPORTANT: This method only works for thunks where input and output types are the same,
        since each iteration's output becomes the next iteration's input.
        
        Args:
            condition: Function that takes the current context and returns True to continue
            
        Returns:
            A thunk that repeats this operation until the condition becomes False
            
        Example:
            increment = Thunk(lambda x: x + 1, name="inc")
            count_to_10 = increment.while_(lambda x: x < 10)
            result = await count_to_10(5)  # Returns 10
        """
        from .combinators import while_true

        return while_true(condition, self)  # type: ignore

    @overload
    def tap(self, fn: Callable[[TOut], None]) -> Thunk[TIn, TOut]: ...
    @overload
    def tap(self, fn: Callable[[TOut], Awaitable[None]]) -> Thunk[TIn, TOut]: ...

    def tap(self, fn: Callable) -> Thunk[TIn, TOut]:
        """Run a side-effect function with the result of the thunk."""

        async def _tapped(ctx: TIn) -> TOut:
            """Call this thunk, then run the side-effect function with its result."""
            result = await self(ctx)
            await maybe_await(fn, result)
            return result

        return Thunk(_tapped, name=f"{self.name}.tap({fn.__name__})")

    def chain(self, next_thunk: Thunk[TOut, TNew]) -> Thunk[TIn, TNew]:
        """Compose this thunk with another, where the output of this is the input to the other."""

        async def _chained(ctx: TIn) -> TNew:
            """Call this thunk, then pass its result to the next thunk."""
            intermediate = await self(ctx)
            return await next_thunk(intermediate)

        return Thunk(_chained, name=f"{self.name} → {next_thunk.name}")

    def label(self, name: str) -> Thunk[TIn, TOut]:
        """Add a debug label that prints when this thunk executes.
        
        Convenience method for adding print-based debugging to thunk pipelines.
        The label is printed to stdout when the thunk executes, then the
        original result is passed through unchanged.
        
        Args:
            name: The label to print when this thunk executes
            
        Returns:
            A thunk that prints the label and passes the result through
        """
        return self.tap(lambda _: print(f"[{name}]"))

    def __rshift__(self, other: Thunk[TOut, TNew]) -> Thunk[TIn, TNew]:
        """Operator overload for chaining thunks with >> syntax.
        
        Enables pipeline-style composition where the output of this thunk
        becomes the input to the next thunk. Equivalent to self.chain(other).
        
        Args:
            other: The thunk to execute after this one
            
        Returns:
            A composed thunk that executes both operations in sequence
            
        Example:
            increment = Thunk(lambda x: x + 1, name="inc")
            double = Thunk(lambda x: x * 2, name="double")
            pipeline = increment >> double  # Same as increment.chain(double)
        """
        return self.chain(other)

    def compose_chain(self, *thunks: Thunk[Any, Any]) -> Thunk[TIn, Any]:
        """Compose multiple thunks after this one."""
        return self.chain(compose_chain(*thunks))


def thunk(
    *, name: str
) -> Callable[
    [Callable[[TIn], TOut] | Callable[[TIn], Awaitable[TOut]]], Thunk[TIn, TOut]
]:
    """Decorator to mark a function as a thunk with a specific name (e.g. "Slickback")."""

    def _decorator(
        fn: Callable[[TIn], TOut] | Callable[[TIn], Awaitable[TOut]],
    ) -> Thunk[TIn, TOut]:
        """Create a thunk with the given name."""
        return Thunk(fn, name=name)

    return _decorator


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")


@overload
def compose_chain(*thunks: tuple[Thunk[A, B], Thunk[B, C]]) -> Thunk[A, C]: ...
@overload
def compose_chain(
    *thunks: tuple[Thunk[A, B], Thunk[B, C], Thunk[C, D]]
) -> Thunk[A, D]: ...
@overload
def compose_chain(
    *thunks: tuple[Thunk[A, B], Thunk[B, C], Thunk[C, D], Thunk[D, E]]
) -> Thunk[A, E]: ...
@overload
def compose_chain(*thunks: Thunk[Any, Any]) -> Thunk[Any, Any]: ...


def compose_chain(*thunks) -> Thunk:
    """Compose multiple thunks in a chain, where the output of each is the input to the next."""
    names = [t.name for t in thunks]
    composed_name = " → ".join(names)

    async def _composed(ctx):
        """Run a series of thunks in sequence, passing the context through each."""
        value = await thunks[0](ctx)
        for thunk in thunks[1:]:
            value = await thunk(value)
        return value

    return Thunk(_composed, name=f"compose({composed_name})")
