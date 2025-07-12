"""Flow execution framework for comprehensive testing of event-driven flows.

This module provides controlled execution environments for testing flows
with event integration, timing control, and verification capabilities.
"""

import asyncio
from typing import Any, AsyncGenerator, Callable, Optional, TypeVar, Union
from unittest.mock import patch

from flow import Flow
from flow_events.flow import AsyncEventFlow, SyncEventFlow
from flow_events.inject import get_async_event_emitter, get_sync_event_emitter

from .test_async_generators_fixtures import (
    AsyncGeneratorTester,
    create_empty_input_generator,
)
from .test_event_system_fixtures import (
    EventTestHarness,
    MockEventEmitter,
    MockEventListener,
)

T = TypeVar("T")
U = TypeVar("U")


class FlowTestExecutor:
    """Execute flows in controlled test environment with event system integration."""

    def __init__(self, use_isolated_emitters: bool = True) -> None:
        """Initialize flow executor.

        Args:
            use_isolated_emitters: If True, use isolated emitters for each test
        """
        super().__init__()
        self.use_isolated_emitters = use_isolated_emitters
        self.harness: Optional[EventTestHarness] = None
        self.generator_tester = AsyncGeneratorTester()
        self.execution_log: list[str] = []

        # Track active patches for cleanup
        self.active_patches: list[Any] = []

    def setup_isolated_environment(self) -> EventTestHarness:
        """Set up isolated event environment for testing."""
        if self.harness is None:
            # For flow integration tests, we need real emitters but isolated instances
            self.harness = EventTestHarness(
                use_real_emitters=True  # Always use real emitters for flow compatibility
            )

        if self.use_isolated_emitters:
            # Patch global emitters to use isolated ones - try multiple paths
            patch_paths = [
                "src.flow_events.flow.get_sync_event_emitter",
                "flow_events.flow.get_sync_event_emitter",
                "src.flow_events.inject.get_sync_event_emitter",
                "flow_events.inject.get_sync_event_emitter",
            ]
            async_patch_paths = [
                "src.flow_events.flow.get_async_event_emitter",
                "flow_events.flow.get_async_event_emitter",
                "src.flow_events.inject.get_async_event_emitter",
                "flow_events.inject.get_async_event_emitter",
            ]

            for path in patch_paths:
                try:
                    sync_patch = patch(path, return_value=self.harness.sync_emitter)
                    sync_patch.start()
                    self.active_patches.append(sync_patch)
                except Exception:
                    pass  # Path doesn't exist, skip

            for path in async_patch_paths:
                try:
                    async_patch = patch(path, return_value=self.harness.async_emitter)
                    async_patch.start()
                    self.active_patches.append(async_patch)
                except Exception:
                    pass  # Path doesn't exist, skip
            self.execution_log.append("isolated_environment_setup")

        return self.harness

    async def execute_with_events(
        self,
        flow: Flow[T, U],
        input_events: list[tuple[str, Any]],
        event_delay: float = 0.01,
    ) -> list[U]:
        """Execute flow with controlled event injection.

        Args:
            flow: The flow to execute
            input_events: List of (event_name, event_data) tuples to emit
            event_delay: Delay between event emissions

        Returns:
            List of items produced by the flow
        """
        harness = self.setup_isolated_environment()
        results: list[U] = []

        self.execution_log.append(f"execute_with_events: {len(input_events)} events")

        # Create task to emit events
        async def emit_events() -> None:
            await asyncio.sleep(0.02)  # Let flow start and register callbacks
            for event_name, event_data in input_events:
                # Emit to both sync and async emitters to support both flow types
                await harness.emit_async_event(event_name, event_data)
                harness.emit_sync_event(event_name, event_data)
                self.execution_log.append(f"emitted: {event_name} -> {event_data}")
                if event_delay > 0:
                    await asyncio.sleep(event_delay)

        # Start event emission task
        event_task = asyncio.create_task(emit_events())

        try:
            # Execute flow with empty input stream
            empty_input = create_empty_input_generator()

            # Use timing-based collection for event flows that don't end naturally
            results, duration = await self.generator_tester.collect_with_timing(
                flow(empty_input),
                max_duration=1.0,  # Give enough time for events to be processed
            )

            self.execution_log.append(
                f"flow_results: {len(results)} items in {duration:.3f}s"
            )

        finally:
            # Ensure event task completes or is cancelled
            if not event_task.done():
                event_task.cancel()
                try:
                    await event_task
                except asyncio.CancelledError:
                    pass

        return results

    async def execute_with_timing(
        self,
        flow: Flow[T, U],
        input_generator: AsyncGenerator[T, None],
        max_duration: float = 1.0,
    ) -> tuple[list[U], float]:
        """Execute flow with timing constraints.

        Args:
            flow: The flow to execute
            input_generator: Input stream for the flow
            max_duration: Maximum execution time

        Returns:
            Tuple of (results, actual_duration)
        """
        self.execution_log.append(f"execute_with_timing: max_duration={max_duration}")

        start_time = asyncio.get_event_loop().time()

        try:
            results = await self.generator_tester.collect_with_timing(
                flow(input_generator), max_duration
            )
            actual_duration = asyncio.get_event_loop().time() - start_time

            self.execution_log.append(
                f"timing_results: {len(results[0])} items in {actual_duration:.3f}s"
            )
            return results[0], actual_duration

        except Exception as e:
            actual_duration = asyncio.get_event_loop().time() - start_time
            self.execution_log.append(
                f"timing_exception: {e} after {actual_duration:.3f}s"
            )
            raise

    async def execute_with_input_stream(
        self, flow: Flow[T, U], input_items: list[T], input_delay: float = 0.01
    ) -> list[U]:
        """Execute flow with controlled input stream.

        Args:
            flow: The flow to execute
            input_items: Items to feed into the flow
            input_delay: Delay between input items

        Returns:
            List of items produced by the flow
        """
        self.execution_log.append(
            f"execute_with_input_stream: {len(input_items)} items"
        )

        # Create controlled input generator
        async def input_generator() -> AsyncGenerator[T, None]:
            for i, item in enumerate(input_items):
                if input_delay > 0 and i > 0:
                    await asyncio.sleep(input_delay)
                self.execution_log.append(f"input_item_{i}: {item}")
                yield item

        results = await self.generator_tester.collect_all_items(
            flow(input_generator()), max_items=len(input_items) * 2
        )

        self.execution_log.append(f"input_stream_results: {len(results)} items")
        return results

    def verify_event_emissions(
        self, expected_events: list[tuple[str, Any]], from_async: bool = True
    ) -> bool:
        """Verify that expected events were emitted.

        Args:
            expected_events: Expected (event_name, event_data) tuples
            from_async: Whether to check async or sync emitter

        Returns:
            True if all expected events were emitted
        """
        if self.harness is None:
            self.execution_log.append("verify_events: no harness")
            return False

        actual_events = self.harness.get_emitted_events(from_async=from_async)

        self.execution_log.append(
            f"verify_events: expected={len(expected_events)}, actual={len(actual_events)}"
        )

        if len(actual_events) != len(expected_events):
            return False

        for expected, actual in zip(expected_events, actual_events):
            if expected != actual:
                self.execution_log.append(
                    f"event_mismatch: expected={expected}, actual={actual}"
                )
                return False

        self.execution_log.append("verify_events: all_matched")
        return True

    async def test_event_flow_integration(
        self,
        event_name: str,
        flow_factory: Callable[[str], Flow[Any, Any]],
        test_data: list[Any],
        use_async: bool = True,
    ) -> dict[str, Any]:
        """Test complete event flow integration.

        Args:
            event_name: Name of the event to test
            flow_factory: Function that creates a flow for the event
            test_data: Data to emit as events
            use_async: Whether to use async event system

        Returns:
            Dict with test results and metrics
        """
        harness = self.setup_isolated_environment()
        flow = flow_factory(event_name)

        self.execution_log.append(
            f"test_integration: {event_name} with {len(test_data)} items"
        )

        # Set up event listener to track emissions
        listener = harness.create_listener(f"listener_{event_name}")
        if use_async:
            harness.register_async_listener(event_name, listener)
        else:
            harness.register_sync_listener(event_name, listener)

        # Execute flow and emit events concurrently
        async def emit_test_events() -> None:
            await asyncio.sleep(0.01)  # Let flow start
            for i, data in enumerate(test_data):
                if use_async:
                    await harness.emit_async_event(event_name, data)
                else:
                    harness.emit_sync_event(event_name, data)
                self.execution_log.append(f"emitted_test_event_{i}: {data}")
                await asyncio.sleep(0.01)

        # Start event emission
        event_task = asyncio.create_task(emit_test_events())

        try:
            # Execute flow
            empty_input = create_empty_input_generator()
            flow_results = await self.generator_tester.collect_all_items(
                flow(empty_input), max_items=len(test_data) * 2
            )

            # Wait for events to propagate
            await asyncio.sleep(0.1)

            # Ensure event task completes
            await event_task

        except Exception as e:
            if not event_task.done():
                event_task.cancel()
            raise

        return {
            "flow_results": flow_results,
            "listener_events": listener.received_events.copy(),
            "emitted_events": harness.get_emitted_events(
                event_name, from_async=use_async
            ),
            "execution_log": self.execution_log.copy(),
        }

    async def test_empty_stream_handling(self, flow: Flow[T, U]) -> list[U]:
        """Test flow behavior with empty input streams.

        Args:
            flow: The flow to test

        Returns:
            Results from flow execution (should be empty for most flows)
        """
        self.execution_log.append("test_empty_stream")

        empty_input = create_empty_input_generator()
        results = await self.generator_tester.collect_all_items(
            flow(empty_input), max_items=10  # Safety limit
        )

        self.execution_log.append(f"empty_stream_results: {len(results)} items")
        return results

    def get_execution_log(self) -> list[str]:
        """Get copy of execution log."""
        return self.execution_log.copy()

    def clear_log(self) -> None:
        """Clear execution log."""
        self.execution_log.clear()
        self.generator_tester.clear_log()

    def cleanup(self) -> None:
        """Clean up test environment."""
        # Stop all patches
        for patch_obj in self.active_patches:
            try:
                patch_obj.stop()
            except Exception:
                pass
        self.active_patches.clear()

        # Clean up harness
        if self.harness:
            self.harness.cleanup()
            self.harness = None

        self.execution_log.append("cleanup_completed")


class EventFlowTestBuilder:
    """Builder for creating comprehensive event flow tests."""

    def __init__(self) -> None:
        """Initialize test builder."""
        super().__init__()
        self.executor = FlowTestExecutor()
        self.test_scenarios: list[dict[str, Any]] = []

    def add_event_source_test(
        self, event_name: str, test_events: list[Any], use_async: bool = True
    ) -> "EventFlowTestBuilder":
        """Add event source test scenario."""
        self.test_scenarios.append(
            {
                "type": "event_source",
                "event_name": event_name,
                "test_events": test_events,
                "use_async": use_async,
            }
        )
        return self

    def add_event_sink_test(
        self, event_name: str, input_data: list[Any], use_async: bool = True
    ) -> "EventFlowTestBuilder":
        """Add event sink test scenario."""
        self.test_scenarios.append(
            {
                "type": "event_sink",
                "event_name": event_name,
                "input_data": input_data,
                "use_async": use_async,
            }
        )
        return self

    def add_bridge_test(
        self,
        source_event: str,
        target_event: str,
        test_events: list[Any],
        use_async: bool = True,
    ) -> "EventFlowTestBuilder":
        """Add event bridge test scenario."""
        self.test_scenarios.append(
            {
                "type": "event_bridge",
                "source_event": source_event,
                "target_event": target_event,
                "test_events": test_events,
                "use_async": use_async,
            }
        )
        return self

    def add_filter_test(
        self,
        event_name: str,
        predicate: Callable[[Any], bool],
        test_events: list[Any],
        use_async: bool = True,
    ) -> "EventFlowTestBuilder":
        """Add event filter test scenario."""
        self.test_scenarios.append(
            {
                "type": "event_filter",
                "event_name": event_name,
                "predicate": predicate,
                "test_events": test_events,
                "use_async": use_async,
            }
        )
        return self

    def add_transform_test(
        self,
        event_name: str,
        transformer: Callable[[Any], Any],
        test_events: list[Any],
        use_async: bool = True,
    ) -> "EventFlowTestBuilder":
        """Add event transform test scenario."""
        self.test_scenarios.append(
            {
                "type": "event_transform",
                "event_name": event_name,
                "transformer": transformer,
                "test_events": test_events,
                "use_async": use_async,
            }
        )
        return self

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all configured test scenarios.

        Returns:
            Comprehensive test results
        """
        results: dict[str, Any] = {
            "total_scenarios": len(self.test_scenarios),
            "passed": 0,
            "failed": 0,
            "scenarios": [],
        }

        for i, scenario in enumerate(self.test_scenarios):
            try:
                scenario_result = await self._run_scenario(scenario)
                scenario_result["passed"] = True
                results["passed"] += 1
            except Exception as e:
                scenario_result = {
                    "scenario": scenario,
                    "passed": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
                results["failed"] += 1

            results["scenarios"].append(scenario_result)

        return results

    async def _run_scenario(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Run a single test scenario."""
        scenario_type = scenario["type"]

        if scenario_type == "event_source":
            return await self._run_event_source_test(scenario)
        elif scenario_type == "event_sink":
            return await self._run_event_sink_test(scenario)
        elif scenario_type == "event_bridge":
            return await self._run_bridge_test(scenario)
        elif scenario_type == "event_filter":
            return await self._run_filter_test(scenario)
        elif scenario_type == "event_transform":
            return await self._run_transform_test(scenario)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

    async def _run_event_source_test(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Run event source test scenario."""
        from flow_events.flow_integration import event_source

        flow = event_source(scenario["event_name"], scenario["use_async"])

        result = await self.executor.test_event_flow_integration(
            scenario["event_name"],
            lambda name: flow,
            scenario["test_events"],
            scenario["use_async"],
        )

        return {"scenario": scenario, "result": result}

    async def _run_event_sink_test(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Run event sink test scenario."""
        from flow_events.flow_integration import event_sink

        flow: Flow[Any, Any] = event_sink(scenario["event_name"], scenario["use_async"])

        results = await self.executor.execute_with_input_stream(
            flow, scenario["input_data"]
        )

        return {
            "scenario": scenario,
            "flow_results": results,
            "emitted_events": (
                self.executor.harness.get_emitted_events(
                    scenario["event_name"], from_async=scenario["use_async"]
                )
                if self.executor.harness
                else []
            ),
        }

    async def _run_bridge_test(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Run event bridge test scenario."""
        from flow_events.flow_integration import event_bridge

        flow = event_bridge(
            scenario["source_event"], scenario["target_event"], scenario["use_async"]
        )

        result = await self.executor.execute_with_events(
            flow,
            [(scenario["source_event"], event) for event in scenario["test_events"]],
        )

        return {"scenario": scenario, "bridge_results": result}

    async def _run_filter_test(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Run event filter test scenario."""
        from flow_events.flow_integration import event_filter

        flow = event_filter(
            scenario["event_name"], scenario["predicate"], scenario["use_async"]
        )

        result = await self.executor.test_event_flow_integration(
            scenario["event_name"],
            lambda name: flow,
            scenario["test_events"],
            scenario["use_async"],
        )

        return {"scenario": scenario, "result": result}

    async def _run_transform_test(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """Run event transform test scenario."""
        from flow_events.flow_integration import event_transform

        flow = event_transform(
            scenario["event_name"], scenario["transformer"], scenario["use_async"]
        )

        result = await self.executor.test_event_flow_integration(
            scenario["event_name"],
            lambda name: flow,
            scenario["test_events"],
            scenario["use_async"],
        )

        return {"scenario": scenario, "result": result}

    def cleanup(self) -> None:
        """Clean up test builder resources."""
        self.executor.cleanup()
        self.test_scenarios.clear()
