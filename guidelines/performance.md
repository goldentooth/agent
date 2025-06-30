# Performance Guidelines

This document defines performance standards, optimization strategies, and benchmarking practices for the Goldentooth Agent project.

## Performance Standards

### Critical Performance Targets

#### Core Operations
- **Vector search**: <100ms for typical queries (1-10 documents)
- **Flow execution**: <50ms overhead per flow stage  
- **Context operations**: <10ms for get/set operations
- **Document processing**: <500ms per document (text)
- **Embedding generation**: <200ms per document

#### System Performance
- **Test suite**: <60s for full test run
- **Application startup**: <5s cold start
- **Memory usage**: <512MB for typical workloads
- **Response time**: <2s for interactive chat responses

#### Scalability Targets
- **Concurrent requests**: Handle 10+ concurrent operations
- **Document corpus**: Support 10K+ documents efficiently  
- **Vector database**: Sub-linear search performance
- **Flow composition**: Support 10+ stage pipelines

### Performance Monitoring

#### Key Metrics
```python
from goldentooth_agent.core.observability import MetricsCollector

@injectable
class PerformanceMonitor:
    def __init__(self, metrics: MetricsCollector = inject.me()) -> None:
        self.metrics = metrics
    
    def track_operation(self, operation_name: str):
        """Context manager for tracking operation performance."""
        return self.metrics.timer(f"{operation_name}_duration")
    
    def track_throughput(self, operation_name: str, count: int):
        """Track operation throughput."""
        self.metrics.histogram(f"{operation_name}_throughput", count)
    
    def track_memory_usage(self, component: str):
        """Track memory usage for component."""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.metrics.gauge(f"{component}_memory_mb", memory_mb)
```

## Optimization Strategies

### Caching Strategies

#### Multi-Level Caching
```python
from functools import lru_cache
import asyncio
from typing import Any, Callable, Awaitable

class CacheManager:
    """Multi-level cache management."""
    
    def __init__(self) -> None:
        self._memory_cache: dict[str, Any] = {}
        self._locks: dict[str, asyncio.Lock] = {}
    
    # Level 1: Function-level caching
    @lru_cache(maxsize=256)
    def cached_computation(self, input_data: str) -> str:
        """Cache expensive synchronous computations."""
        return expensive_computation(input_data)
    
    # Level 2: Async operation caching
    async def cached_async_operation(
        self, 
        key: str, 
        operation: Callable[[], Awaitable[Any]],
        ttl: int = 300
    ) -> Any:
        """Cache async operations with TTL."""
        if key in self._memory_cache:
            cached_value, timestamp = self._memory_cache[key]
            if time.time() - timestamp < ttl:
                return cached_value
        
        # Prevent cache stampede
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        
        async with self._locks[key]:
            if key not in self._memory_cache:
                result = await operation()
                self._memory_cache[key] = (result, time.time())
                return result
            return self._memory_cache[key][0]
```

#### Vector Search Caching
```python
@injectable
class CachedVectorStore:
    """Vector store with intelligent caching."""
    
    def __init__(
        self,
        vector_store: VectorStore = inject.me(),
        cache_size: int = 1000
    ) -> None:
        self.vector_store = vector_store
        self._search_cache: dict[str, list[dict]] = {}
        self._cache_size = cache_size
    
    async def search_similar_cached(
        self,
        query_embedding: list[float],
        limit: int = 10,
        **kwargs
    ) -> list[dict]:
        """Search with embedding cache."""
        # Create cache key from embedding and parameters
        cache_key = self._create_cache_key(query_embedding, limit, kwargs)
        
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]
        
        # Perform search
        results = self.vector_store.search_similar(
            query_embedding, limit=limit, **kwargs
        )
        
        # Cache results (with LRU eviction)
        if len(self._search_cache) >= self._cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self._search_cache))
            del self._search_cache[oldest_key]
        
        self._search_cache[cache_key] = results
        return results
    
    def _create_cache_key(
        self, 
        embedding: list[float], 
        limit: int, 
        kwargs: dict
    ) -> str:
        """Create cache key from embedding and parameters."""
        # Hash embedding for key (approximate matching could be added)
        import hashlib
        embedding_hash = hashlib.md5(str(embedding).encode()).hexdigest()[:16]
        params_hash = hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()[:8]
        return f"{embedding_hash}_{limit}_{params_hash}"
```

### Async Optimization Patterns

#### Concurrent Processing
```python
import asyncio
from typing import AsyncIterator, TypeVar

T = TypeVar("T")
R = TypeVar("R")

async def process_concurrently(
    items: list[T],
    processor: Callable[[T], Awaitable[R]],
    max_concurrency: int = 10
) -> list[R]:
    """Process items concurrently with controlled concurrency."""
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def process_with_semaphore(item: T) -> R:
        async with semaphore:
            return await processor(item)
    
    tasks = [process_with_semaphore(item) for item in items]
    return await asyncio.gather(*tasks)

async def stream_process_concurrently(
    stream: AsyncIterator[T],
    processor: Callable[[T], Awaitable[R]],
    max_concurrency: int = 10,
    buffer_size: int = 100
) -> AsyncIterator[R]:
    """Process stream concurrently with backpressure control."""
    semaphore = asyncio.Semaphore(max_concurrency)
    result_queue: asyncio.Queue[R] = asyncio.Queue(buffer_size)
    
    async def process_item(item: T) -> None:
        async with semaphore:
            result = await processor(item)
            await result_queue.put(result)
    
    async def producer():
        async for item in stream:
            asyncio.create_task(process_item(item))
        await result_queue.put(None)  # Sentinel
    
    producer_task = asyncio.create_task(producer())
    
    try:
        while True:
            result = await result_queue.get()
            if result is None:  # Sentinel received
                break
            yield result
    finally:
        producer_task.cancel()
        try:
            await producer_task
        except asyncio.CancelledError:
            pass
```

#### Resource Pool Management
```python
@injectable
class ResourcePool:
    """Generic resource pool for expensive objects."""
    
    def __init__(
        self,
        factory: Callable[[], Awaitable[T]],
        max_size: int = 10,
        min_size: int = 2
    ) -> None:
        self.factory = factory
        self.max_size = max_size
        self.min_size = min_size
        self._pool: asyncio.Queue[T] = asyncio.Queue(max_size)
        self._current_size = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> T:
        """Acquire resource from pool."""
        try:
            # Try to get from pool without waiting
            return self._pool.get_nowait()
        except asyncio.QueueEmpty:
            # Create new resource if under max size
            async with self._lock:
                if self._current_size < self.max_size:
                    self._current_size += 1
                    return await self.factory()
            
            # Wait for resource to become available
            return await self._pool.get()
    
    async def release(self, resource: T) -> None:
        """Release resource back to pool."""
        try:
            self._pool.put_nowait(resource)
        except asyncio.QueueFull:
            # Pool is full, clean up resource
            if hasattr(resource, 'cleanup'):
                await resource.cleanup()
            async with self._lock:
                self._current_size -= 1
```

### Memory Optimization

#### Streaming Data Processing
```python
async def process_large_dataset_streaming(
    data_source: AsyncIterator[RawData],
    batch_size: int = 100
) -> AsyncIterator[ProcessedData]:
    """Process large dataset in streaming fashion."""
    batch = []
    
    async for item in data_source:
        batch.append(item)
        
        if len(batch) >= batch_size:
            # Process batch and yield results
            processed_batch = await process_batch(batch)
            for result in processed_batch:
                yield result
            
            # Clear batch to free memory
            batch.clear()
    
    # Process remaining items
    if batch:
        processed_batch = await process_batch(batch)
        for result in processed_batch:
            yield result

async def memory_efficient_vector_search(
    query: str,
    document_store: DocumentStore,
    vector_store: VectorStore,
    chunk_size: int = 1000
) -> AsyncIterator[SearchResult]:
    """Memory-efficient vector search over large corpora."""
    # Get query embedding
    query_embedding = await get_embedding(query)
    
    # Search in chunks to limit memory usage
    offset = 0
    while True:
        # Get chunk of document IDs
        doc_ids = await document_store.get_document_ids(
            offset=offset, 
            limit=chunk_size
        )
        
        if not doc_ids:
            break
        
        # Search within this chunk
        chunk_results = await vector_store.search_similar_in_subset(
            query_embedding,
            document_subset=doc_ids,
            limit=10
        )
        
        for result in chunk_results:
            yield result
        
        offset += chunk_size
```

#### Memory Monitoring
```python
import tracemalloc
import psutil
from contextlib import asynccontextmanager

class MemoryTracker:
    """Track memory usage for performance optimization."""
    
    @asynccontextmanager
    async def track_memory(self, operation_name: str):
        """Track memory usage during operation."""
        # Start tracing
        tracemalloc.start()
        process = psutil.Process()
        start_memory = process.memory_info().rss
        
        try:
            yield
        finally:
            # Get final memory usage
            end_memory = process.memory_info().rss
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Log memory usage
            memory_delta = (end_memory - start_memory) / 1024 / 1024  # MB
            peak_memory = peak / 1024 / 1024  # MB
            
            logger.info(
                "Memory usage",
                operation=operation_name,
                memory_delta_mb=memory_delta,
                peak_memory_mb=peak_memory
            )

# Usage
memory_tracker = MemoryTracker()

async def expensive_operation():
    async with memory_tracker.track_memory("document_processing"):
        # Memory-intensive operation
        results = await process_large_document_set()
        return results
```

### Flow Performance Optimization

#### Flow Composition Optimization
```python
from goldentooth_agent.core.flow import Flow

# ✅ Efficient: Combine operations in single flow
async def optimized_processing_flow(
    stream: AsyncIterator[Document]
) -> AsyncIterator[ProcessedDocument]:
    """Combined processing flow for efficiency."""
    async for document in stream:
        # Combine multiple operations to reduce overhead
        validated = validate_document(document)
        if not validated:
            continue
            
        transformed = transform_document(document)
        enriched = enrich_document(transformed)
        processed = finalize_processing(enriched)
        
        yield processed

# ❌ Inefficient: Multiple small flows with overhead
def inefficient_flows():
    return (
        validation_flow |
        transformation_flow |
        enrichment_flow |
        finalization_flow
    )
```

#### Batch Processing in Flows
```python
async def batch_processing_flow(
    stream: AsyncIterator[Document],
    batch_size: int = 50
) -> AsyncIterator[ProcessedDocument]:
    """Process documents in batches for efficiency."""
    batch = []
    
    async for document in stream:
        batch.append(document)
        
        if len(batch) >= batch_size:
            # Process entire batch efficiently
            processed_batch = await process_document_batch(batch)
            for processed_doc in processed_batch:
                yield processed_doc
            batch.clear()
    
    # Process remaining documents
    if batch:
        processed_batch = await process_document_batch(batch)
        for processed_doc in processed_batch:
            yield processed_doc
```

## Benchmarking and Profiling

### Performance Testing Framework
```python
import time
import pytest
from typing import Callable, Any

class PerformanceBenchmark:
    """Framework for performance testing."""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.metrics: dict[str, float] = {}
    
    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        return self._timer_context(operation_name)
    
    @contextmanager
    def _timer_context(self, operation_name: str):
        """Time an operation and store result."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.metrics[operation_name] = duration
    
    def assert_performance(
        self, 
        operation_name: str, 
        max_duration: float
    ) -> None:
        """Assert operation meets performance requirement."""
        actual_duration = self.metrics.get(operation_name)
        if actual_duration is None:
            raise ValueError(f"No timing data for {operation_name}")
        
        assert actual_duration <= max_duration, (
            f"{operation_name} took {actual_duration:.3f}s, "
            f"expected <= {max_duration:.3f}s"
        )

# Usage in tests
@pytest.mark.benchmark
def test_vector_search_performance():
    """Benchmark vector search performance."""
    benchmark = PerformanceBenchmark("vector_search")
    
    # Setup
    vector_store = create_test_vector_store(size=10000)
    query_vector = create_test_vector()
    
    # Benchmark
    with benchmark.time_operation("search"):
        results = vector_store.search_similar(query_vector, limit=10)
    
    # Assertions
    benchmark.assert_performance("search", max_duration=0.1)  # 100ms
    assert len(results) == 10
```

### Profiling Integration
```python
import cProfile
import pstats
from functools import wraps

def profile_performance(output_file: str | None = None):
    """Decorator to profile function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.disable()
                
                if output_file:
                    profiler.dump_stats(output_file)
                else:
                    # Print top 20 functions
                    stats = pstats.Stats(profiler)
                    stats.sort_stats('cumulative')
                    stats.print_stats(20)
        
        return wrapper
    return decorator

# Usage
@profile_performance("document_processing.prof")
def process_documents_with_profiling(documents):
    """Process documents with performance profiling."""
    return process_documents(documents)
```

### Memory Profiling
```python
from memory_profiler import profile
import tracemalloc

@profile  # Line-by-line memory profiling
def memory_intensive_function():
    """Function with memory profiling."""
    large_list = [i for i in range(1000000)]
    processed = [x * 2 for x in large_list]
    return sum(processed)

class MemoryProfiler:
    """Custom memory profiler for async operations."""
    
    def __init__(self) -> None:
        self.snapshots: list[tracemalloc.Snapshot] = []
    
    def take_snapshot(self, label: str) -> None:
        """Take memory snapshot with label."""
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        snapshot = tracemalloc.take_snapshot()
        snapshot.label = label  # type: ignore
        self.snapshots.append(snapshot)
    
    def compare_snapshots(self, start_label: str, end_label: str) -> None:
        """Compare two snapshots and report differences."""
        start_snapshot = next(
            s for s in self.snapshots 
            if getattr(s, 'label', '') == start_label
        )
        end_snapshot = next(
            s for s in self.snapshots 
            if getattr(s, 'label', '') == end_label
        )
        
        top_stats = end_snapshot.compare_to(start_snapshot, 'lineno')
        
        print(f"Memory comparison: {start_label} -> {end_label}")
        for stat in top_stats[:10]:
            print(stat)
```

## Performance Monitoring in Production

### Real-time Performance Metrics
```python
@injectable
class ProductionPerformanceMonitor:
    """Monitor performance in production environment."""
    
    def __init__(self, metrics: MetricsCollector = inject.me()) -> None:
        self.metrics = metrics
        self._operation_times: dict[str, list[float]] = {}
    
    def record_operation_time(self, operation: str, duration: float) -> None:
        """Record operation timing."""
        self.metrics.histogram(f"{operation}_duration", duration)
        
        # Track recent times for alerting
        if operation not in self._operation_times:
            self._operation_times[operation] = []
        
        times = self._operation_times[operation]
        times.append(duration)
        
        # Keep only recent measurements
        if len(times) > 100:
            times.pop(0)
        
        # Check for performance degradation
        if len(times) >= 10:
            recent_avg = sum(times[-10:]) / 10
            overall_avg = sum(times) / len(times)
            
            if recent_avg > overall_avg * 1.5:  # 50% slower
                self._alert_performance_degradation(operation, recent_avg, overall_avg)
    
    def _alert_performance_degradation(
        self, 
        operation: str, 
        recent_avg: float, 
        overall_avg: float
    ) -> None:
        """Alert on performance degradation."""
        logger.warning(
            "Performance degradation detected",
            operation=operation,
            recent_avg=recent_avg,
            overall_avg=overall_avg,
            degradation_factor=recent_avg / overall_avg
        )
        
        self.metrics.increment("performance_alerts", tags={"operation": operation})
```

### Performance Alerting
```python
class PerformanceAlerter:
    """Alert on performance issues."""
    
    def __init__(self) -> None:
        self.thresholds = {
            "vector_search": 0.1,  # 100ms
            "document_processing": 0.5,  # 500ms
            "flow_execution": 0.05,  # 50ms
            "context_operation": 0.01,  # 10ms
        }
    
    def check_operation_performance(
        self, 
        operation: str, 
        duration: float
    ) -> None:
        """Check if operation meets performance requirements."""
        threshold = self.thresholds.get(operation)
        if threshold and duration > threshold:
            self._send_alert(operation, duration, threshold)
    
    def _send_alert(
        self, 
        operation: str, 
        actual: float, 
        expected: float
    ) -> None:
        """Send performance alert."""
        logger.error(
            "Performance threshold exceeded",
            operation=operation,
            actual_duration=actual,
            expected_duration=expected,
            slowdown_factor=actual / expected
        )
        
        # Send to monitoring system
        # metrics.increment("performance_violations")
```

## Anti-Patterns and Common Issues

### Performance Anti-Patterns
```python
# ❌ Anti-pattern: N+1 queries
async def inefficient_document_loading(document_ids: list[str]) -> list[Document]:
    """Inefficient: One query per document."""
    documents = []
    for doc_id in document_ids:
        doc = await document_store.get_document(doc_id)  # N+1 queries!
        documents.append(doc)
    return documents

# ✅ Efficient: Batch loading
async def efficient_document_loading(document_ids: list[str]) -> list[Document]:
    """Efficient: Single batch query."""
    return await document_store.get_documents_batch(document_ids)

# ❌ Anti-pattern: Blocking async operations
async def blocking_operation():
    """Inefficient: Blocking the event loop."""
    time.sleep(1)  # Blocks event loop!
    return "done"

# ✅ Efficient: Non-blocking async operations
async def non_blocking_operation():
    """Efficient: Non-blocking async operation."""
    await asyncio.sleep(1)  # Doesn't block event loop
    return "done"

# ❌ Anti-pattern: Inefficient memory usage
def memory_inefficient_processing(large_dataset: list[Data]) -> list[Result]:
    """Inefficient: Loads everything into memory."""
    # Creates multiple large intermediate lists
    filtered = [item for item in large_dataset if item.is_valid()]
    transformed = [transform(item) for item in filtered]
    processed = [process(item) for item in transformed]
    return processed

# ✅ Efficient: Generator-based processing
def memory_efficient_processing(large_dataset: list[Data]) -> Iterator[Result]:
    """Efficient: Generator-based streaming processing."""
    for item in large_dataset:
        if item.is_valid():
            transformed = transform(item)
            processed = process(transformed)
            yield processed
```

### Common Performance Issues
1. **Synchronous operations in async code**
2. **Missing connection pooling**  
3. **Inefficient database queries**
4. **Memory leaks from circular references**
5. **Blocking I/O operations**
6. **Excessive object creation**
7. **Missing caching for expensive operations**
8. **Poor error handling causing retries**

### Performance Debugging Checklist
- [ ] Profile slow operations with cProfile
- [ ] Monitor memory usage with tracemalloc
- [ ] Check for N+1 query patterns
- [ ] Verify async operations are non-blocking
- [ ] Review database query efficiency
- [ ] Check cache hit rates
- [ ] Monitor resource pool utilization
- [ ] Verify proper connection management
- [ ] Check for memory leaks
- [ ] Review error handling and retry logic