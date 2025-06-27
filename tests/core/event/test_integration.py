"""Integration tests for event flows with the broader Flow system."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from goldentooth_agent.core.event.flow import (
    AsyncEventFlow,
    SyncEventFlow,
    event_filter,
    event_sink,
    event_source,
    event_transform,
)
from goldentooth_agent.core.flow.main import Flow


class TestEventFlowIntegrationWithFlowSystem:
    """Integration tests demonstrating event flows working with the Flow system."""

    @pytest.mark.asyncio
    async def test_event_source_with_flow_chaining(self) -> None:
        """Test event source integrated with Flow chaining operations."""
        # Create an event source flow
        source_flow = event_source("integration_test", use_async=True)

        # Chain it with standard Flow operations
        processing_flow = (
            source_flow.map(lambda x: f"processed_{x}")
            .filter(lambda x: "important" in x)
            .map(lambda x: x.upper())
        )

        # Set up the event emitter to send events
        event_emitter = AsyncEventFlow[str]("integration_test")

        # Collect processed results
        results = []

        async def collect_results() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for result in processing_flow(empty_stream()):
                results.append(result)
                count += 1
                if count >= 2:  # Stop after getting 2 matching events
                    break

        # Start collection
        collection_task = asyncio.create_task(collect_results())
        await asyncio.sleep(0.01)

        # Emit various events
        event_emitter.emit("regular_data")
        event_emitter.emit("important_data")
        event_emitter.emit("more_data")
        event_emitter.emit("very_important_info")

        await collection_task

        # Should only get events with "important" in them, processed and uppercased
        assert results == ["PROCESSED_IMPORTANT_DATA", "PROCESSED_VERY_IMPORTANT_INFO"]

    @pytest.mark.asyncio
    async def test_flow_to_event_sink_integration(self) -> None:
        """Test standard Flow operations feeding into event sink."""
        # Create a standard Flow that generates data
        data_flow = Flow.from_iterable(["item1", "item2", "item3"])

        # Transform the data
        processed_flow = data_flow.map(lambda x: f"processed_{x}")

        # Feed into event sink
        sink_flow = event_sink("flow_to_event", use_async=True)
        combined_flow = processed_flow >> sink_flow

        # Set up event listener to capture emitted events
        event_listener = AsyncEventFlow[str]("flow_to_event")
        captured_events = []

        async def event_handler(data: str) -> None:
            captured_events.append(data)

        await event_listener.on(event_handler)

        # Run the combined flow
        results = []

        async def empty_input_stream():
            return
            yield  # unreachable

        async for item in combined_flow(empty_input_stream()):
            results.append(item)

        # Give async handlers time to process
        await asyncio.sleep(0.01)

        # Verify both the flow output and the emitted events
        expected = ["processed_item1", "processed_item2", "processed_item3"]
        assert results == expected
        assert captured_events == expected

    @pytest.mark.asyncio
    async def test_event_bridge_pattern(self) -> None:
        """Test bridging events between different event names using flows."""
        # Create source and target event flows
        source_event = SyncEventFlow[dict[str, Any]]("source_events")
        target_event = AsyncEventFlow[str]("target_events")

        # Create a flow that bridges and transforms events
        source_flow = source_event.as_flow()

        # Transform complex data to simple string and emit to target
        async def bridge_transform(stream: AsyncIterator[None]) -> AsyncIterator[str]:
            async def empty_stream():
                return
                yield  # unreachable

            async for event_data in source_flow(empty_stream()):
                # Transform dict to string representation
                transformed = f"{event_data['type']}:{event_data['value']}"
                target_event.emit(transformed)
                yield transformed

        bridge_flow = Flow(bridge_transform, name="event_bridge")

        # Set up target event listener
        target_received = []

        async def target_handler(data: str) -> None:
            target_received.append(data)

        await target_event.on(target_handler)

        # Start the bridge
        bridge_results = []

        async def run_bridge() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for result in bridge_flow(empty_stream()):
                bridge_results.append(result)
                count += 1
                if count >= 3:
                    break

        bridge_task = asyncio.create_task(run_bridge())
        await asyncio.sleep(0.01)

        # Emit source events
        source_event.emit({"type": "user", "value": "login"})
        source_event.emit({"type": "system", "value": "startup"})
        source_event.emit({"type": "user", "value": "logout"})

        await bridge_task
        await asyncio.sleep(0.01)  # Let target handlers process

        expected = ["user:login", "system:startup", "user:logout"]
        assert bridge_results == expected
        assert target_received == expected

    @pytest.mark.asyncio
    async def test_complex_event_flow_pipeline(self) -> None:
        """Test a complex pipeline combining multiple event flow patterns."""
        # Step 1: Data source flow
        input_data = [
            {"id": 1, "category": "urgent", "message": "Critical alert"},
            {"id": 2, "category": "info", "message": "Status update"},
            {"id": 3, "category": "urgent", "message": "System failure"},
            {"id": 4, "category": "debug", "message": "Debug info"},
            {"id": 5, "category": "urgent", "message": "Security breach"},
        ]

        data_flow = Flow.from_iterable(input_data)

        # Step 2: Filter and emit urgent messages as events
        urgent_sink = event_sink("urgent_messages", use_async=True)
        urgent_flow = (
            data_flow.filter(lambda x: x["category"] == "urgent") >> urgent_sink
        )

        # Set up event listener to capture emitted urgent events
        urgent_event_listener = AsyncEventFlow[dict[str, Any]]("urgent_messages")
        captured_urgent_events = []

        async def urgent_event_handler(data: dict[str, Any]) -> None:
            captured_urgent_events.append(data)

        await urgent_event_listener.on(urgent_event_handler)

        # Process the data through the urgent flow
        urgent_passthrough = []

        async def data_input_stream():
            for item in input_data:
                yield item

        async for item in urgent_flow(data_input_stream()):
            urgent_passthrough.append(item)

        # Give async handlers time to process
        await asyncio.sleep(0.1)

        # Verify results
        assert len(urgent_passthrough) == 3  # 3 urgent messages passed through
        assert all(item["category"] == "urgent" for item in urgent_passthrough)

        # Verify events were emitted
        assert len(captured_urgent_events) == 3
        assert all(event["category"] == "urgent" for event in captured_urgent_events)

        # Verify we got the expected urgent messages
        urgent_ids = {item["id"] for item in urgent_passthrough}
        assert urgent_ids == {1, 3, 5}  # Only urgent messages

        # Verify events match the passthrough data
        event_ids = {event["id"] for event in captured_urgent_events}
        assert event_ids == urgent_ids

    @pytest.mark.asyncio
    async def test_event_flow_with_error_recovery(self) -> None:
        """Test event flows with error handling and recovery patterns."""
        # Create an event flow that might receive bad data
        error_prone_flow = AsyncEventFlow[str]("error_prone")

        # Create a processing flow that handles errors gracefully
        async def safe_processor(stream: AsyncIterator[None]) -> AsyncIterator[str]:
            base_flow = error_prone_flow.as_flow()

            async def empty_stream():
                return
                yield  # unreachable

            async for data in base_flow(empty_stream()):
                try:
                    # Simulate processing that might fail
                    if data == "error":
                        raise ValueError("Processing error")
                    elif data.startswith("warn"):
                        # Handle warnings differently
                        yield f"WARNING: {data}"
                    else:
                        # Normal processing
                        yield f"PROCESSED: {data}"
                except ValueError:
                    # Recover from errors by yielding error message
                    yield f"ERROR_RECOVERED: {data}"

        safe_flow = Flow(safe_processor, name="safe_processor")

        # Collect results
        results = []

        async def collect_results() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for result in safe_flow(empty_stream()):
                results.append(result)
                count += 1
                if count >= 4:  # Wait for all test events
                    break

        collection_task = asyncio.create_task(collect_results())
        await asyncio.sleep(0.01)

        # Emit various types of data including problematic ones
        error_prone_flow.emit("good_data")
        error_prone_flow.emit("error")  # This will cause an error
        error_prone_flow.emit("warn_something")
        error_prone_flow.emit("more_good_data")

        await collection_task

        expected = [
            "PROCESSED: good_data",
            "ERROR_RECOVERED: error",
            "WARNING: warn_something",
            "PROCESSED: more_good_data",
        ]
        assert results == expected

    @pytest.mark.asyncio
    async def test_multi_consumer_event_pattern(self) -> None:
        """Test multiple consumers listening to the same event source."""
        # Create a shared event source
        shared_source = SyncEventFlow[int]("shared_numbers")

        # Create multiple consumer flows with different processing
        even_filter = event_filter(
            "shared_numbers", lambda x: x % 2 == 0, use_async=False
        )
        odd_filter = event_filter(
            "shared_numbers", lambda x: x % 2 == 1, use_async=False
        )
        square_transform = event_transform(
            "shared_numbers", lambda x: x**2, use_async=False
        )

        # Collect results from each consumer
        even_results = []
        odd_results = []
        square_results = []

        async def collect_even() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for num in even_filter(empty_stream()):
                even_results.append(num)
                count += 1
                if count >= 2:  # Stop after getting enough even numbers (2, 4)
                    break

        async def collect_odd() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for num in odd_filter(empty_stream()):
                odd_results.append(num)
                count += 1
                if count >= 3:  # Stop after getting enough odd numbers (1, 3, 5)
                    break

        async def collect_squares() -> None:
            async def empty_stream():
                return
                yield  # unreachable

            count = 0
            async for num in square_transform(empty_stream()):
                square_results.append(num)
                count += 1
                if count >= 5:  # Get squares for all numbers
                    break

        # Start all consumers
        even_task = asyncio.create_task(collect_even())
        odd_task = asyncio.create_task(collect_odd())
        square_task = asyncio.create_task(collect_squares())

        await asyncio.sleep(0.01)  # Let consumers set up

        # Emit numbers
        for i in range(1, 6):  # 1, 2, 3, 4, 5
            shared_source.emit(i)

        # Wait for all consumers to finish
        await asyncio.gather(even_task, odd_task, square_task)

        # Verify each consumer got what it expected
        assert even_results == [2, 4]  # Only even numbers
        assert odd_results == [1, 3, 5]  # Only odd numbers
        assert square_results == [1, 4, 9, 16, 25]  # All numbers squared
