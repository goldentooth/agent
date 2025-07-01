# Debugging Tools Reference

This document provides a comprehensive reference for all debugging tools available in the Goldentooth Agent system.

## 🔧 Command Line Interface (CLI) Tools

### `goldentooth-agent debug health`

**Description**: Check system health and component status.

**Location**: `cli/commands/debug.py:54`

### `goldentooth-agent debug trace`

**Description**: Trace flow or agent execution for debugging.

**Location**: `cli/commands/debug.py:120`

### `goldentooth-agent debug profile`

**Description**: Profile command performance and resource usage.

**Location**: `cli/commands/debug.py:179`


## 🧩 Flow Engine Observability Tools

### Analysis Module

**File**: `flow_engine/observability/analysis.py`

**Classes**:
- `FlowNode`: Represents a node in a Flow composition graph
- `FlowEdge`: Represents an edge (connection) between Flow nodes
- `FlowGraph`: Represents a complete Flow composition as a directed graph
- `FlowAnalyzer`: Analyzer for Flow compositions and structures

**Functions**:
- `analyze_flow()`: Analyze a single Flow and return its graph representation
- `analyze_flow_composition()`: Analyze a composition of multiple flows
- `detect_flow_patterns()`: Detect common patterns in a flow graph
- `generate_flow_optimizations()`: Generate optimization suggestions for a flow graph
- `export_flow_analysis()`: Export comprehensive flow analysis to JSON file
- `get_flow_analyzer()`: Get the global flow analyzer instance
- `to_dict()`: Convert node to dictionary representation
- `to_dict()`: Convert edge to dictionary representation
- `complexity_score()`: Calculate total complexity score of the graph
- `depth()`: Calculate maximum depth of the graph
- `get_critical_path()`: Find the critical path (longest path) through the graph
- `find_cycles()`: Find cycles in the graph
- `to_dict()`: Convert graph to dictionary representation
- `analyze_flow()`: Analyze a single Flow and return its graph representation
- `analyze_composition()`: Analyze a composition of multiple flows
- `detect_patterns()`: Detect common patterns in the flow graph
- `generate_optimization_suggestions()`: Generate optimization suggestions for the flow graph
- `export_analysis()`: Export comprehensive flow analysis to JSON file
- `dfs()`: No description available

### Health Module

**File**: `flow_engine/observability/health.py`

**Classes**:
- `HealthStatus`: Health status levels
- `HealthCheck`: Individual health check definition
- `HealthCheckResult`: Result of a health check execution
- `SystemHealth`: Overall system health status
- `FlowHealthMonitor`: Health monitoring system for Flow applications
- `FlowConfigValidator`: Configuration validation for Flow systems

**Functions**:
- `health_check_stream()`: Create a flow that performs health checks during stream processing
- `get_health_monitor()`: Get the global health monitor instance
- `get_config_validator()`: Get the global configuration validator instance
- `validate_flow_configuration()`: Validate flow configuration
- `register_health_check()`: Register a custom health check
- `export_health_report()`: Export system health report to file
- `to_dict()`: Convert result to dictionary
- `healthy_checks()`: Get all healthy checks
- `warning_checks()`: Get all warning checks
- `critical_checks()`: Get all critical checks
- `to_dict()`: Convert to dictionary
- `register_check()`: Register a new health check
- `unregister_check()`: Unregister a health check
- `get_health_history()`: Get health check history for the specified number of hours
- `export_health_report()`: Export health report to JSON file
- `register_validator()`: Register a custom validator
- `set_config_schema()`: Set the configuration schema for validation
- `validate_config()`: Validate configuration against the schema
- `validate_flow_config()`: Validate configuration specific to a Flow
- `validate_positive_number()`: Validate that value is a positive number
- `validate_non_negative_number()`: Validate that value is a non-negative number
- `validate_string()`: Validate that value is a non-empty string
- `validate_boolean()`: Validate that value is a boolean

### Debugging Module

**File**: `flow_engine/observability/debugging.py`

**Classes**:
- `FlowExecutionContext`: Context information for a Flow execution
- `FlowDebugger`: Debugging system for Flow executions
- `FlowExecutionErrorWithContext`: Enhanced flow execution error with debugging context

**Functions**:
- `debug_stream()`: Create a flow that adds debugging capabilities to the pipeline
- `traced_flow()`: Wrap a flow with execution tracing and enhanced error reporting
- `get_flow_debugger()`: Get the global flow debugger instance
- `enable_flow_debugging()`: Enable flow debugging globally
- `disable_flow_debugging()`: Disable flow debugging globally
- `add_flow_breakpoint()`: Add a breakpoint for a specific flow
- `remove_flow_breakpoint()`: Remove a breakpoint for a flow
- `get_execution_trace()`: Get the current execution trace
- `export_execution_trace()`: Export execution trace to a JSON file
- `inspect_flow()`: Inspect a flow and return metadata about its structure
- `to_dict()`: Convert context to dictionary for serialization
- `enable_debugging()`: Enable debugging mode
- `disable_debugging()`: Disable debugging mode
- `add_breakpoint()`: Add a breakpoint for a specific flow
- `remove_breakpoint()`: Remove a breakpoint for a flow
- `print_execution_stack()`: Print the current execution stack
- `print_item_inspection()`: Print detailed inspection of the current item
- `get_execution_trace()`: Get the full execution trace
- `export_trace()`: Export execution trace to a JSON file
- `get_debug_info()`: Get comprehensive debug information
- `print_debug_info()`: Print comprehensive debug information

### Performance Module

**File**: `flow_engine/observability/performance.py`

**Classes**:
- `FlowMetrics`: Metrics collected for a Flow execution
- `PerformanceMonitor`: Performance monitoring system for Flow executions

**Functions**:
- `monitored_stream()`: Decorator to add performance monitoring to a Flow
- `performance_stream()`: Create a flow that adds performance monitoring to the pipeline
- `benchmark_stream()`: Benchmark a Flow's performance over multiple iterations
- `get_performance_monitor()`: Get the global performance monitor instance
- `enable_memory_tracking()`: Enable memory tracking for all monitored flows
- `get_performance_summary()`: Get summary of all performance metrics
- `export_performance_metrics()`: Export all performance metrics to a JSON file
- `duration_ms()`: Total execution duration in milliseconds
- `throughput_items_per_sec()`: Items processed per second
- `yield_rate()`: Ratio of items yielded to items processed
- `to_dict()`: Convert metrics to dictionary for serialization
- `enable_memory_tracking()`: Enable memory usage tracking (requires psutil)
- `start_monitoring()`: Start monitoring a flow execution
- `record_item_processed()`: Record that an item was processed
- `record_item_yielded()`: Record that an item was yielded
- `record_error()`: Record an error during execution
- `record_memory_usage()`: Record current memory usage
- `finish_monitoring()`: Finish monitoring and return final metrics
- `get_summary_stats()`: Get summary statistics across all monitored flows
- `export_metrics()`: Export all metrics to a JSON file
- `decorator()`: No description available
- `benchmark_func()`: No description available
- `stats()`: No description available


## 🔍 Observability Combinators

**File**: `flow_engine/combinators/observability.py`

- `log_stream()`: Create a flow that logs each stream item and passes it through unchanged
- `trace_stream()`: Create a flow that provides detailed tracing of stream processing
- `metrics_stream()`: Create a flow that emits metrics for stream processing
- `inspect_stream()`: Create a flow that inspects stream items with context metadata
- `materialize_stream()`: Create a flow that converts items and errors into notification objects

## 🚨 Error Reporting & Enhancement

**File**: `core/util/error_reporting.py`

- `DetailedAttributeError` (class): Enhanced AttributeError with context for better debugging
- `safe_getattr` (function): Safe attribute access with enhanced error reporting
- `safe_dict_access` (function): Safe dictionary access with enhanced error reporting

## 🛠️ Development Utilities

**File**: `dev/debugging.py`

- `DebugStats` (class): Statistics collected during debug context
- `DebugContext` (class): Context manager for enhanced debugging information
- `debug_operation` (function): Context manager for tracking operation execution
- `log_function_call` (function): Log a function call with arguments (safely)
- `add_metadata` (function): Add additional metadata during execution

## 📊 Analysis Scripts

### `check_extraction_readiness.py`

**Description**: Check if modules are ready for extraction by verifying tests pass

**Usage**: `poetry run python scripts/check_extraction_readiness.py`

### `extract_flow_module.py`

**Description**: Extract the flow module into a separate package

**Usage**: `poetry run python scripts/extract_flow_module.py`

### `check_dict_access.py`

**Description**: Check for potentially unsafe dictionary attribute access patterns

**Usage**: `poetry run python scripts/check_dict_access.py`

### `audit_type_annotations.py`

**Description**: Audit and fix missing type annotations in the codebase

**Usage**: `poetry run python scripts/audit_type_annotations.py`

### `check_claude_guidelines.py`

**Description**: Check that CLAUDE

**Usage**: `poetry run python scripts/check_claude_guidelines.py`

### `migrate_to_openai_embeddings.py`

**Description**: Migrate existing embeddings to use OpenAI embeddings instead of Claude-based embeddings

**Usage**: `poetry run python scripts/migrate_to_openai_embeddings.py`

### `analyze_response_patterns.py`

**Description**: Analyze response handling patterns in the codebase

**Usage**: `poetry run python scripts/analyze_response_patterns.py`

### `vulture_diff.py`

**Description**: Smart vulture runner that only reports NEW dead code issues

**Usage**: `poetry run python scripts/vulture_diff.py`

### `simple_population.py`

**Description**: Simple script to populate vector store with OpenAI embeddings

**Usage**: `poetry run python scripts/simple_population.py`

### `format_files.py`

**Description**: File formatting script that replicates pre-commit hooks for formatting

**Usage**: `poetry run python scripts/format_files.py`

### `show_module_sizes.py`

**Description**: Show the line counts of Python files in src/goldentooth_agent directory

**Usage**: `poetry run python scripts/show_module_sizes.py`

### `test_structure_validator.py`

**Description**: Test structure validation script

**Usage**: `poetry run python scripts/test_structure_validator.py`

### `find_orphaned_code.py`

**Description**: Script to find potentially orphaned functions and classes in the goldentooth-agent codebase

**Usage**: `poetry run python scripts/find_orphaned_code.py`

### `analyze_complexity.py`

**Description**: Analyze code complexity metrics for the goldentooth_agent codebase

**Usage**: `poetry run python scripts/analyze_complexity.py`

### `create_module_docs.py`

**Description**: Generate README

**Usage**: `poetry run python scripts/create_module_docs.py`

### `discover_debug_tools.py`

**Description**: Discover and document available debugging tools in the codebase

**Usage**: `poetry run python scripts/discover_debug_tools.py`

### `qa_check.py`

**Description**: Quality assurance check script - overlaps with pre-commit hooks for automated quality validation

**Usage**: `poetry run python scripts/qa_check.py`

### `check-symbol-duplicates.py`

**Description**: Check for duplicate symbol definitions across Python files

**Usage**: `poetry run python scripts/check-symbol-duplicates.py`

### `update-metadata.py`

**Description**: Pre-commit hook script to update README

**Usage**: `poetry run python scripts/update-metadata.py`

### `coverage_analysis.py`

**Description**: Coverage analysis script to identify modules/files with lowest coverage

**Usage**: `poetry run python scripts/coverage_analysis.py`
