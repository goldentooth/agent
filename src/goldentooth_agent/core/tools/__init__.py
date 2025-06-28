"""Core tool implementations for Goldentooth Agent.

This module provides the foundational tool library including:
- Web Tools: HTTP client, web scraping, API integration
- File Tools: File I/O, document processing, data transformation
- AI Tools: Text processing, image analysis, embedding generation
- System Tools: Process execution, monitoring, database access
- Performance Tools: Optimization, caching, parallelization, streaming

All tools follow the FlowTool pattern and can be used as flows or converted to agents.
"""

# Import modules without star imports to avoid TypeVar conflicts
from . import (
    ai_tools,
    cache,
    file_tools,
    parallel,
    performance,
    streaming,
    system_tools,
    web_tools,
)

# Import specific classes and functions we want to expose
from .ai_tools import TextAnalysisTool, TextSummaryTool
from .cache import (
    CacheMetrics,
    CacheStrategy,
    FlowCacheManager,
    IntelligentCache,
    SmartCacheDecorator,
    cached_flow,
    cached_llm,
    cached_tool,
    clear_all_caches,
    flow_cache,
    flow_cache_manager,
    get_all_cache_stats,
    llm_cache,
    tool_cache,
)
from .file_tools import FileReadTool, FileWriteTool, JsonProcessTool
from .parallel import (
    FlowParallelExecutor,
    ParallelConfig,
    ParallelExecutor,
    WorkerPool,
    default_parallel_executor,
    parallel_batch_process,
    parallel_map,
)
from .performance import (
    ResourcePool,
    async_cache,
    configure_http_pool,
    get_http_client,
    parallel_execute,
    performance_monitor,
)
from .streaming import (
    BackpressureController,
    MemoryMonitor,
    StreamingConfig,
    StreamProcessor,
    create_memory_efficient_flow_stream,
    process_large_dataset,
)
from .system_tools import ProcessExecuteTool, SystemInfoTool
from .web_tools import HttpRequestTool, JsonApiTool, WebScrapeTool

__all__ = [
    # Web Tools
    "HttpRequestTool",
    "WebScrapeTool",
    "JsonApiTool",
    # File Tools
    "FileReadTool",
    "FileWriteTool",
    "JsonProcessTool",
    # AI Tools
    "TextAnalysisTool",
    "TextSummaryTool",
    # System Tools
    "ProcessExecuteTool",
    "SystemInfoTool",
    # Performance Optimization
    "performance_monitor",
    "async_cache",
    "parallel_execute",
    "get_http_client",
    "configure_http_pool",
    "ResourcePool",
    # Streaming
    "StreamProcessor",
    "StreamingConfig",
    "MemoryMonitor",
    "BackpressureController",
    "create_memory_efficient_flow_stream",
    "process_large_dataset",
    # Parallel Execution
    "ParallelExecutor",
    "FlowParallelExecutor",
    "WorkerPool",
    "ParallelConfig",
    "parallel_map",
    "parallel_batch_process",
    "default_parallel_executor",
    # Caching
    "IntelligentCache",
    "CacheStrategy",
    "CacheMetrics",
    "SmartCacheDecorator",
    "cached_flow",
    "cached_tool",
    "cached_llm",
    "flow_cache",
    "tool_cache",
    "llm_cache",
    "FlowCacheManager",
    "flow_cache_manager",
    "get_all_cache_stats",
    "clear_all_caches",
]
