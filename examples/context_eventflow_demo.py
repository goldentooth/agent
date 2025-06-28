#!/usr/bin/env python3
"""
Demonstration of the Context class with EventFlow integration.

This script shows how the Context system now integrates with the EventFlow
system to provide sophisticated event-driven context management.
"""

import asyncio
from typing import Any

from goldentooth_agent.core.context import Context


async def main() -> None:
    """Demonstrate Context with EventFlow integration."""
    print("🎯 Context EventFlow Integration Demo")
    print("=" * 40)

    # Create a context
    context = Context()

    print("\n1. Basic EventFlow subscriptions:")
    print("-" * 30)

    # Subscribe to changes using EventFlow
    user_events = context.subscribe_sync("user_name")
    config_events = context.subscribe_async("config_theme")

    # Set up event handlers
    user_changes = []
    config_changes = []

    user_events.on(lambda name: user_changes.append(f"User changed to: {name}"))
    await config_events.on(
        lambda theme: config_changes.append(f"Theme changed to: {theme}")
    )

    # Make changes
    context["user_name"] = "Alice"
    context["config_theme"] = "dark"
    context["user_name"] = "Bob"

    await asyncio.sleep(0.01)  # Let async handlers process

    print(f"User changes: {user_changes}")
    print(f"Config changes: {config_changes}")

    print("\n2. Global context change monitoring:")
    print("-" * 35)

    # Monitor all context changes
    global_events = context.global_changes_async()
    all_changes = []

    await global_events.on(
        lambda change: all_changes.append(
            f"{change['key']}: {change['old_value']} → {change['new_value']}"
        )
    )

    context["status"] = "active"
    context["priority"] = "high"
    context["status"] = "inactive"

    await asyncio.sleep(0.01)

    print("All context changes:")
    for change in all_changes[-3:]:  # Show last 3 changes
        print(f"  • {change}")

    print("\n3. Flow integration with operations:")
    print("-" * 35)

    # Use Flow operations on context changes
    numbers_flow = context.as_flow("counter", use_async=True)
    processed_flow = numbers_flow.filter(
        lambda x: isinstance(x, int) and x > 0
    ).map(  # Only positive integers
        lambda x: x * 2
    )  # Double them

    results = []

    async def collect_results():
        async def empty_stream():
            return
            yield  # unreachable

        count = 0
        async for result in processed_flow(empty_stream()):
            results.append(result)
            count += 1
            if count >= 3:
                break

    # Start collection
    collection_task = asyncio.create_task(collect_results())
    await asyncio.sleep(0.01)

    # Set various counter values
    context["counter"] = -1  # Filtered out (negative)
    context["counter"] = 5  # Becomes 10
    context["counter"] = "hi"  # Filtered out (not int)
    context["counter"] = 3  # Becomes 6
    context["counter"] = 0  # Filtered out (not > 0)
    context["counter"] = 7  # Becomes 14

    await collection_task
    print(f"Processed counter values: {results}")

    print("\n4. Context isolation with forks:")
    print("-" * 30)

    # Fork context for isolation
    forked = context.fork()

    # Set up separate event listeners
    original_events = []
    forked_events = []

    context.subscribe_sync("isolation_test").on(
        lambda v: original_events.append(f"Original: {v}")
    )
    forked.subscribe_sync("isolation_test").on(
        lambda v: forked_events.append(f"Forked: {v}")
    )

    # Make changes in each context
    context["isolation_test"] = "original_value"
    forked["isolation_test"] = "forked_value"

    print(f"Original context events: {original_events}")
    print(f"Forked context events: {forked_events}")

    print("\n5. Error handling:")
    print("-" * 15)

    # EventFlow gracefully handles handler errors
    error_events = context.subscribe_sync("error_test")

    success_count = 0
    error_count = 0

    def good_handler(value: Any) -> None:
        nonlocal success_count
        success_count += 1
        print(f"  ✓ Good handler processed: {value}")

    def bad_handler(value: Any) -> None:
        nonlocal error_count
        error_count += 1
        print(f"  💥 Bad handler received: {value} (will throw error)")
        raise ValueError("Handler error!")

    error_events.on(good_handler)
    error_events.on(bad_handler)

    # This won't crash the context despite the bad handler
    context["error_test"] = "test_value"

    print(f"  Results: {success_count} successful, {error_count} error handlers called")
    print("  Context operations continued normally despite handler errors!")

    print("\n6. Legacy compatibility:")
    print("-" * 20)

    # New EventFlow system also works on same key
    modern_events = []
    context.subscribe_sync("legacy_key").on(
        lambda v: modern_events.append(f"Modern: {v}")
    )

    context["legacy_key"] = "backwards_compatible"

    print(f"Modern EventFlow: {modern_events}")

    print("\n✨ Demo complete! Context now has full EventFlow integration.")
    print("🔗 Benefits:")
    print("  • Reactive context changes with Flow operations")
    print("  • Async and sync event handling")
    print("  • Context isolation in forks/merges")
    print("  • Graceful error handling")
    print("  • Full backward compatibility")


if __name__ == "__main__":
    asyncio.run(main())
