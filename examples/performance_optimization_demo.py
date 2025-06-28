#!/usr/bin/env python3
"""Performance Optimization Demo

Demonstrates the advanced performance optimization features:
- Async connection pooling
- Memory-efficient streaming
- Parallel execution with backpressure
- Intelligent caching with adaptive strategies
"""

import asyncio
import json
import time
from typing import Any

from goldentooth_agent.core.flow_agent import FlowIOSchema
from goldentooth_agent.core.tools import (  # Performance monitoring; HTTP client pooling; Streaming; Parallel execution; Intelligent caching; Tools
    CacheStrategy,
    FlowParallelExecutor,
    IntelligentCache,
    ParallelConfig,
    StreamingConfig,
    StreamProcessor,
    cached_flow,
    configure_http_pool,
    get_all_cache_stats,
    get_http_client,
    performance_monitor,
)


class DemoInput(FlowIOSchema):
    """Demo input schema."""

    text: str
    url: str | None = None
    process_count: int = 100


class DemoOutput(FlowIOSchema):
    """Demo output schema."""

    processed_items: int
    execution_time: float
    cache_stats: dict[str, Any]
    memory_stats: dict[str, Any]
    performance_stats: dict[str, Any]


async def demo_http_connection_pooling():
    """Demonstrate HTTP connection pooling with multiple pools."""
    print("🔗 HTTP Connection Pooling Demo")
    print("=" * 50)

    # Configure different pools for different types of requests
    configure_http_pool("api_pool", max_connections=50, timeout=10.0)
    configure_http_pool("scraping_pool", max_connections=20, timeout=30.0)

    # Use specific pools
    api_client = await get_http_client("api_pool")
    scraping_client = await get_http_client("scraping_pool")

    print(f"API client: {api_client}")
    print(f"Scraping client: {scraping_client}")

    # Make concurrent requests
    start_time = time.time()
    tasks = []

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers",
    ]

    for url in urls:
        task = api_client.get(url, timeout=5.0)
        tasks.append(task)

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    successful_requests = sum(1 for r in responses if not isinstance(r, Exception))
    elapsed = time.time() - start_time

    print(f"✅ Completed {successful_requests}/{len(urls)} requests in {elapsed:.2f}s")
    print()


async def demo_memory_efficient_streaming():
    """Demonstrate memory-efficient streaming with large datasets."""
    print("💾 Memory-Efficient Streaming Demo")
    print("=" * 50)

    # Create streaming configuration for memory optimization
    config = StreamingConfig(
        chunk_size=50,
        buffer_size=200,
        memory_threshold_mb=10,  # Low threshold for demo
        gc_interval=100,
    )

    processor = StreamProcessor(config)

    # Create large dataset simulation
    async def large_dataset():
        for i in range(1000):
            yield DemoInput(
                text=f"Item {i}: " + "x" * 100,  # Some text content
                process_count=i,
            )

    # Process with memory management
    start_time = time.time()
    processed_count = 0

    async for chunk in processor.chunk_stream(large_dataset(), chunk_size=50):
        # Simulate processing
        await asyncio.sleep(0.001)  # Small delay
        processed_count += len(chunk)

        if processed_count % 200 == 0:
            memory_stats = await processor.get_memory_stats()
            print(
                f"Processed {processed_count} items, Memory: {memory_stats['current_memory_bytes'] // 1024}KB"
            )

    elapsed = time.time() - start_time
    final_stats = await processor.get_memory_stats()

    print(f"✅ Processed {processed_count} items in {elapsed:.2f}s")
    print(f"📊 Memory stats: {json.dumps(final_stats, indent=2)}")
    print()


async def demo_parallel_execution():
    """Demonstrate parallel execution with backpressure control."""
    print("⚡ Parallel Execution Demo")
    print("=" * 50)

    # Configure parallel execution
    config = ParallelConfig(
        max_concurrent=5,
        batch_size=20,
        timeout=10.0,
        retry_attempts=2,
    )

    executor = FlowParallelExecutor(config)

    # Simulate work function
    @cached_flow(ttl=60.0)
    async def process_item(item: DemoInput) -> DemoOutput:
        # Simulate varying processing time
        delay = 0.1 + (hash(item.text) % 100) / 1000
        await asyncio.sleep(delay)

        return DemoOutput(
            processed_items=1,
            execution_time=delay,
            cache_stats={},
            memory_stats={},
            performance_stats={},
        )

    # Create input stream
    async def input_stream():
        for i in range(100):
            yield DemoInput(
                text=f"Parallel item {i}",
                process_count=i,
            )

    # Execute in parallel
    start_time = time.time()
    results = []

    async with executor.parallel_context():
        async for result in executor.parallel_flow_map(
            input_stream(),
            process_item,
            preserve_order=False,  # Better performance
        ):
            results.append(result)

    elapsed = time.time() - start_time
    performance_stats = await executor.get_performance_stats()

    print(f"✅ Processed {len(results)} items in {elapsed:.2f}s")
    print(f"📊 Performance stats: {json.dumps(performance_stats, indent=2)}")
    print()


async def demo_intelligent_caching():
    """Demonstrate intelligent caching with adaptive strategies."""
    print("🧠 Intelligent Caching Demo")
    print("=" * 50)

    # Create adaptive cache
    cache = IntelligentCache(
        max_size=100,
        strategy=CacheStrategy.ADAPTIVE,
        max_memory_mb=5,
    )

    # Create cache decorator
    @cached_flow(cache=cache, ttl=30.0)
    async def expensive_operation(input_data: DemoInput) -> DemoOutput:
        # Simulate expensive computation
        await asyncio.sleep(0.1)

        return DemoOutput(
            processed_items=1,
            execution_time=0.1,
            cache_stats={},
            memory_stats={},
            performance_stats={},
        )

    # Test caching performance
    start_time = time.time()

    # First pass - cache misses
    print("🔄 First pass (cache misses)...")
    for i in range(50):
        item = DemoInput(text=f"Cache test {i % 10}", process_count=i)
        await expensive_operation(item)

    miss_time = time.time() - start_time
    miss_stats = await cache.get_stats()

    # Second pass - cache hits
    print("⚡ Second pass (cache hits)...")
    start_time = time.time()

    for i in range(50):
        item = DemoInput(text=f"Cache test {i % 10}", process_count=i)
        await expensive_operation(item)

    hit_time = time.time() - start_time
    hit_stats = await cache.get_stats()

    print(f"✅ First pass: {miss_time:.2f}s, Second pass: {hit_time:.2f}s")
    print(f"📊 Speedup: {miss_time / hit_time:.1f}x faster")
    print(f"📈 Hit rate: {hit_stats['hit_rate']:.1%}")
    print(f"🎯 Cache strategy: {hit_stats['current_adaptive_strategy']}")
    print()


async def demo_combined_optimization():
    """Demonstrate all optimization features working together."""
    print("🚀 Combined Optimization Demo")
    print("=" * 50)

    # Configure all systems
    configure_http_pool("demo_pool", max_connections=20)

    parallel_executor = FlowParallelExecutor(
        ParallelConfig(
            max_concurrent=5,
            batch_size=10,
        )
    )

    # Simulate a complex workflow with multiple optimization layers
    @cached_flow(ttl=60.0)
    async def analyze_text(text: str) -> dict[str, Any]:
        # Use text analysis tool (which uses caching internally)
        from goldentooth_agent.core.tools.ai_tools import (
            TextAnalysisInput,
            text_analysis_implementation,
        )

        input_data = TextAnalysisInput(text=text)
        result = await text_analysis_implementation(input_data)

        return result.model_dump()

    # Create workflow
    async def workflow_item(item: DemoInput) -> DemoOutput:
        start_time = time.time()

        # Analyze text in parallel
        analysis_result = await analyze_text(item.text)

        # Simulate additional processing
        await asyncio.sleep(0.01)

        execution_time = time.time() - start_time

        return DemoOutput(
            processed_items=1,
            execution_time=execution_time,
            cache_stats=analysis_result,
            memory_stats={},
            performance_stats={},
        )

    # Create large input stream
    async def workflow_input():
        texts = [
            "This is a sample text for analysis with various complexity levels.",
            "Short text.",
            "A much longer piece of text that contains multiple sentences and various linguistic elements that will be analyzed for sentiment, readability, and other metrics that the text analysis tool provides.",
            "Another sample with different characteristics and patterns.",
            "Final test text with unique properties.",
        ]

        for i in range(100):
            yield DemoInput(
                text=texts[i % len(texts)],
                process_count=i,
            )

    # Execute optimized workflow
    start_time = time.time()
    results = []

    async with parallel_executor.parallel_context():
        async for result in parallel_executor.parallel_flow_map(
            workflow_input(),
            workflow_item,
            preserve_order=False,
        ):
            results.append(result)

    total_time = time.time() - start_time

    # Get comprehensive stats
    cache_stats = await get_all_cache_stats()
    performance_stats = await performance_monitor.get_stats()
    parallel_stats = await parallel_executor.get_performance_stats()

    print(f"✅ Completed {len(results)} complex operations in {total_time:.2f}s")
    print(f"📊 Throughput: {len(results) / total_time:.1f} ops/sec")
    print(f"💾 Cache performance: {json.dumps(cache_stats, indent=2)}")
    print(f"⚡ Parallel performance: {json.dumps(parallel_stats, indent=2)}")
    print()


async def main():
    """Run all performance optimization demos."""
    print("🎯 Goldentooth Agent - Performance Optimization Demo")
    print("=" * 60)
    print()

    demos = [
        demo_http_connection_pooling,
        demo_memory_efficient_streaming,
        demo_parallel_execution,
        demo_intelligent_caching,
        demo_combined_optimization,
    ]

    for demo in demos:
        try:
            await demo()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            print()

    print("🎉 All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
