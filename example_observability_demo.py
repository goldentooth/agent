#!/usr/bin/env python3
"""
Demonstration of the comprehensive Flow observability system.

This script shows how to use:
- Performance monitoring
- Flow debugging and tracing
- Health monitoring
- Flow composition analysis
- All features working together
"""

import asyncio
from goldentooth_agent.core.flow import (
    Flow,
    map_stream,
    filter_stream,
    batch_stream,
    # Performance monitoring
    monitored_stream,
    performance_stream,
    get_performance_summary,
    # Debugging
    debug_stream,
    traced_flow,
    inspect_flow,
    # Health monitoring
    check_system_health,
    HealthStatus,
    # Analysis
    analyze_flow,
    analyze_flow_composition,
    detect_flow_patterns,
    generate_flow_optimizations,
)
from goldentooth_agent.core.flow.combinators import compose


async def async_range(n: int):
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


async def main():
    print("🔍 Flow Observability System Demo")
    print("=" * 40)

    # 1. Performance Monitoring Demo
    print("\n📊 Performance Monitoring:")

    @monitored_stream("demo_pipeline")
    def create_monitored_flow():
        return map_stream(lambda x: x * 2)

    flow = create_monitored_flow
    input_stream = async_range(100)
    result = [item async for item in flow(input_stream)]

    print(f"✅ Processed {len(result)} items with monitoring")
    summary = get_performance_summary()
    print(f"📈 Performance Summary: {summary}")

    # 2. Flow Analysis Demo
    print("\n🔬 Flow Composition Analysis:")

    # Create a complex pipeline
    complex_pipeline = [
        map_stream(lambda x: x + 1),  # transformation
        filter_stream(lambda x: x > 5),  # filtering
        batch_stream(3),  # batching
    ]

    # Analyze the composition
    graph = analyze_flow_composition(complex_pipeline)
    print(f"📊 Flow Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    print(f"🧮 Complexity Score: {graph.complexity_score}")

    # Detect patterns
    patterns = detect_flow_patterns(graph)
    print(f"🎯 Detected Patterns: {len(patterns)} pattern(s)")
    for pattern in patterns:
        print(f"  - {pattern.get('pattern', 'unknown')} pattern")

    # Get optimization suggestions
    optimizations = generate_flow_optimizations(graph)
    print(f"⚡ Optimization Suggestions: {len(optimizations)}")
    for opt in optimizations:
        print(
            f"  - {opt.get('type', 'unknown')}: {opt.get('description', 'no description')}"
        )

    # 3. Flow Inspection Demo
    print("\n🔍 Flow Inspection:")

    test_flow = map_stream(lambda x: x**2)
    inspection = inspect_flow(test_flow)
    print(f"📋 Flow Name: {inspection['name']}")
    print(f"📋 Flow Type: {inspection['type']}")
    print(f"📋 Function: {inspection['function_name']}")
    print(f"📋 Is Async: {inspection['is_async']}")

    # 4. Health Monitoring Demo
    print("\n🏥 System Health Check:")

    health_status = await check_system_health()
    print(f"💚 System Status: {health_status.status.value}")
    print(f"🩺 Health Checks: {len(health_status.checks)} check(s)")
    for check in health_status.checks:
        status_icon = (
            "✅"
            if check.status == HealthStatus.HEALTHY
            else "⚠️" if check.status == HealthStatus.WARNING else "❌"
        )
        print(f"  {status_icon} {check.name}: {check.status.value}")

    # 5. Integrated Observability Demo
    print("\n🎯 Integrated Observability Pipeline:")

    # Create empty input for from_iterable
    async def empty_stream():
        yield None

    # Create a pipeline with comprehensive observability
    base_pipeline = (
        Flow.from_iterable(range(20)).map(lambda x: x * 3).filter(lambda x: x > 15)
    )

    # Add all observability features
    monitored_pipeline = compose(
        compose(
            compose(base_pipeline, performance_stream()),
            debug_stream(log_items=False),  # No logging to keep output clean
        ),
        batch_stream(5),
    )

    # Run with comprehensive monitoring
    result = await monitored_pipeline.to_list()(empty_stream())

    print(f"🎉 Pipeline completed! Processed {len(result)} batches")

    # Show comprehensive metrics
    final_summary = get_performance_summary()
    print(f"📈 Final Performance Summary:")
    print(
        f"  - Total flows monitored: {final_summary.get('total_flows_monitored', 'unknown')}"
    )
    if (
        "duration_ms" in final_summary
        and final_summary["duration_ms"].get("count", 0) > 0
    ):
        print(f"  - Average duration: {final_summary['duration_ms']['avg']:.2f}ms")
        print(f"  - Min duration: {final_summary['duration_ms']['min']:.2f}ms")
        print(f"  - Max duration: {final_summary['duration_ms']['max']:.2f}ms")

    print("\n✨ Observability Demo Complete!")
    print(
        "The Flow system now has comprehensive monitoring, debugging, health checks, and analysis capabilities!"
    )


if __name__ == "__main__":
    asyncio.run(main())
