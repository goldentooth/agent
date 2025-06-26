#!/usr/bin/env python3
"""
Demonstration of Flow ergonomic improvements.

This script showcases all the new developer experience enhancements:
- Fluent API methods
- Convenience constructors
- Decorator support
- Flow registry
- Debugging improvements
- Error handling helpers
"""

import asyncio
from goldentooth_agent.core.flow import (
    Flow,
    map_stream,
    filter_stream,
    # Registry functionality
    register_flow,
    get_flow,
    list_flows,
    search_flows,
    registered_flow,
    flow_registry,
)


async def async_range(n: int):
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


async def main():
    print("🧩 Flow Ergonomic Improvements Demo")
    print("=" * 50)

    # 1. Fluent API Demonstrations
    print("\n✨ 1. Fluent API Methods")
    print("-" * 25)

    # .collect() for ergonomic data collection
    simple_flow = map_stream(lambda x: x * 2)
    result = await simple_flow.collect()(async_range(5))
    print(f"📦 .collect(): {result}")

    # .preview() for development
    preview = await simple_flow.preview(async_range(20), limit=3)
    print(f"👁️  .preview(limit=3): {preview}")

    # .print() for debugging (chainable)
    print("🖨️  .print() output:")
    chained = simple_flow.print().map(lambda x: x + 1)

    # .with_fallback() for error handling
    empty_flow = Flow.from_iterable([]).filter(lambda x: x > 0)
    safe_flow = empty_flow.with_fallback("no items!")

    async def empty_stream():
        yield None

    fallback_result = await safe_flow.collect()(empty_stream())
    print(f"🛡️  .with_fallback(): {fallback_result}")

    # 2. Convenience Constructors
    print("\n🏗️  2. Convenience Constructors")
    print("-" * 30)

    # Identity flow
    identity = Flow.identity()
    identity_result = await identity.collect()(async_range(3))
    print(f"🔄 Flow.identity(): {identity_result}")

    # Pure value flow
    pure = Flow.pure("hello world")
    pure_result = await pure.collect()(empty_stream())
    print(f"💎 Flow.pure(): {pure_result}")

    # From thunk (sync)
    def multiply_by_3(x):
        return x * 3

    thunk_flow = Flow.from_thunk(multiply_by_3)
    thunk_result = await thunk_flow.collect()(async_range(4))
    print(f"🔧 Flow.from_thunk(sync): {thunk_result}")

    # From thunk (async)
    async def async_add_10(x):
        return x + 10

    async_thunk_flow = Flow.from_thunk(async_add_10)
    async_thunk_result = await async_thunk_flow.collect()(async_range(3))
    print(f"⚡ Flow.from_thunk(async): {async_thunk_result}")

    # 3. Decorator Support
    print("\n🎭 3. Decorator Support")
    print("-" * 22)

    # Sync function decorator
    @Flow.from_sync_fn
    def square(x):
        return x**2

    square_result = await square.collect()(async_range(5))
    print(f"📐 @Flow.from_sync_fn: {square_result}")

    # Async function decorator
    @Flow.from_value_fn
    async def async_cube(x):
        await asyncio.sleep(0)  # Simulate async work
        return x**3

    cube_result = await async_cube.collect()(async_range(4))
    print(f"📦 @Flow.from_value_fn: {cube_result}")

    # Event function decorator
    @Flow.from_event_fn
    async def split_number(n):
        for i in range(n):
            yield i

    split_result = await split_number.collect()(
        Flow.from_iterable([2, 3])(empty_stream())
    )
    print(f"🌊 @Flow.from_event_fn: {split_result}")

    # 4. Flow Registry
    print("\n🗂️  4. Flow Registry")
    print("-" * 18)

    # Register flows manually
    register_flow("my_doubler", simple_flow, "math")
    register_flow("my_squarer", square, "math")

    # Register using decorator
    @registered_flow("special_transform", "transforms")
    @Flow.from_sync_fn
    def reverse_and_negate(x):
        return -x

    # List registry contents
    print(f"📋 All flows: {list_flows()}")
    print(f"🧮 Math flows: {list_flows('math')}")
    print(f"🔄 Transform flows: {list_flows('transforms')}")

    # Search functionality
    search_results = search_flows("double")
    print(f"🔍 Search 'double': {search_results}")

    # Retrieve and use registered flow
    retrieved_flow = get_flow("my_squarer")
    if retrieved_flow:
        retrieved_result = await retrieved_flow.collect()(async_range(4))
        print(f"📤 Retrieved flow result: {retrieved_result}")

    # 5. Rich Representation
    print("\n🎨 5. Rich Representation")
    print("-" * 25)

    complex_flow = (
        Flow.from_iterable([1, 2, 3])
        .map(lambda x: x * 2)
        .filter(lambda x: x > 2)
        .with_fallback(0)
    )

    print(f"📝 Complex flow repr:")
    print(f"   {repr(complex_flow)}")

    # 6. Error Handling Enhancement
    print("\n🛡️  6. Error Handling Enhancement")
    print("-" * 32)

    # Type error prevention
    try:
        # This should raise a helpful error
        async for item in square:
            pass
    except TypeError as e:
        print(f"❌ Helpful error message: {e}")

    # 7. Complete Workflow Example
    print("\n🎯 7. Complete Development Workflow")
    print("-" * 35)

    # Build a data processing pipeline
    @registered_flow("normalize", "data")
    @Flow.from_sync_fn
    def normalize(x):
        return x / 10.0

    @registered_flow("categorize", "data")
    @Flow.from_sync_fn
    def categorize(x):
        if x < 0.5:
            return "small"
        elif x < 1.0:
            return "medium"
        else:
            return "large"

    # Compose pipeline
    data_pipeline = (
        Flow.from_iterable([1, 5, 12, 8, 15]).map(lambda x: x)  # identity for demo
        >> normalize
        >> categorize
        >> Flow.identity()
    )

    # Preview during development
    pipeline_preview = await data_pipeline.preview(empty_stream(), limit=3)
    print(f"🔬 Pipeline preview: {pipeline_preview}")

    # Add error handling
    robust_pipeline = data_pipeline.with_fallback("error")

    # Full execution
    final_result = await robust_pipeline.collect()(empty_stream())
    print(f"🎉 Final pipeline result: {final_result}")

    # Show registry state
    print(f"📊 Final registry state:")
    flow_registry.print_registry()

    print("\n✨ Ergonomics Demo Complete!")
    print("The Flow system is now much more delightful to use! 🎉")


if __name__ == "__main__":
    asyncio.run(main())
