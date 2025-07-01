# Debugging Guide - Quick Reference

This guide provides immediate access to all debugging tools and techniques in the Goldentooth Agent system.

## 🚨 I Have An Issue - Where Do I Start?

### Performance Problems
1. **Quick health check**: `goldentooth-agent debug health`
2. **Profile operation**: `goldentooth-agent debug profile [command] --iterations 10`
3. **Flow performance**: Use `monitored_stream()` combinator
4. **Memory analysis**: Check `PerformanceMonitor` in `flow_engine/observability/performance.py`

### Execution Problems
1. **Trace execution**: `goldentooth-agent debug trace --agent [type] "[query]" --verbose`
2. **Flow debugging**: Use `FlowDebugger` with breakpoints in `flow_engine/observability/debugging.py`
3. **Error context**: Check `DetailedAttributeError` in `core/util/error_reporting.py`

### System Problems
1. **Health validation**: `goldentooth-agent debug health --export health.json`
2. **Component status**: Use health checks in `flow_engine/observability/health.py`
3. **Configuration**: Validate setup with health checks

### Agent/Flow Issues
1. **Agent validation**: `goldentooth-agent debug health --component agents`
2. **Flow analysis**: Use flow composition analysis in `flow_engine/observability/analysis.py`
3. **Stream debugging**: Use observability combinators in `flow_engine/combinators/observability.py`

## 🛠️ Available Tools Matrix

| Problem Type | CLI Tool | Code Tool | Location | Output |
|--------------|----------|-----------|----------|---------|
| **System Health** | `debug health` | `HealthCheck` | `flow_engine/observability/health.py` | Status report |
| **Execution Flow** | `debug trace` | `FlowDebugger` | `flow_engine/observability/debugging.py` | Step-by-step trace |
| **Performance** | `debug profile` | `PerformanceMonitor` | `flow_engine/observability/performance.py` | Timing statistics |
| **Flow Analysis** | N/A | Flow analysis tools | `flow_engine/observability/analysis.py` | Flow composition analysis |
| **Error Context** | N/A | `DetailedAttributeError` | `core/util/error_reporting.py` | Enhanced error info |
| **Stream Monitoring** | N/A | Observability combinators | `flow_engine/combinators/observability.py` | Real-time metrics |

## 🔍 Tool Relationships

```
CLI Debug Commands (High-level, immediate access)
├── debug health → flow_engine/observability/health.py
├── debug trace → flow_engine/observability/debugging.py
└── debug profile → flow_engine/observability/performance.py

Flow-Level Debugging (Code integration)
├── FlowDebugger (interactive debugging with breakpoints)
├── PerformanceMonitor (metrics collection and analysis)
├── Flow analysis (composition and pattern detection)
└── Observability combinators (stream-level monitoring)

Error Enhancement (Automatic)
├── DetailedAttributeError (attribute access debugging)
├── DebugContext (operation tracking in dev/debugging.py)
└── Enhanced exception context throughout the system
```

## 🚀 Quick Start Commands

### Immediate Diagnosis
```bash
# System overview
goldentooth-agent debug health

# Test specific agent
goldentooth-agent debug trace --agent rag "test query" --verbose

# Performance baseline
goldentooth-agent debug profile chat --iterations 5
```

### Detailed Investigation
```bash
# Component-specific health
goldentooth-agent debug health --component agents --export agents_health.json

# Flow-specific tracing
goldentooth-agent debug trace --flow my_flow --input '{"test": "data"}' --verbose

# Performance comparison
goldentooth-agent debug profile "agents run rag" --iterations 20
```

## 📊 Using Advanced Tools

### Interactive Flow Debugging
```python
from goldentooth_agent.flow_engine.observability.debugging import FlowDebugger

debugger = FlowDebugger()
debugger.set_breakpoint("my_flow", condition=lambda x: x.id == "target")

# Execute with debugging
async for item in debugger.debug_stream(my_flow, input_stream):
    # Interactive debugging session
    pass
```

### Real-Time Performance Monitoring
```python
from goldentooth_agent.flow_engine.observability.performance import PerformanceMonitor
from goldentooth_agent.flow_engine.combinators.observability import monitored_stream

monitor = PerformanceMonitor()

# Automatic monitoring
async for item in monitored_stream(my_flow, monitor):
    # Automatic performance tracking
    pass

# Get statistics
stats = monitor.get_statistics()
print(f"Average duration: {stats['average_duration']:.3f}s")
```

### Enhanced Error Reporting
```python
from goldentooth_agent.core.util.error_reporting import DetailedAttributeError

try:
    value = response.attribute  # Might fail if response is dict
except AttributeError as e:
    # Enhanced error with debugging context
    enhanced = DetailedAttributeError(response, "attribute", {
        "expected_type": "object with .attribute",
        "suggestion": "Use response['attribute'] if dict"
    })
    raise enhanced from e
```

### Stream-Level Observability
```python
from goldentooth_agent.flow_engine.combinators.observability import (
    log_stream,
    trace_stream,
    metrics_stream,
    inspect_stream
)

# Multiple observability layers
debug_flow = (
    source_flow
    | log_stream(level="DEBUG", prefix="processing")
    | trace_stream(tracer=my_tracer)
    | inspect_stream(context={"stage": "main_processing"})
    | metrics_stream(emitter=metrics_emitter)
    | target_flow
)
```

## 🔧 Common Debugging Scenarios

### Scenario 1: "Agent returns wrong response format"
```bash
# 1. Check agent health
goldentooth-agent debug health --component agents

# 2. Trace execution to see response format
goldentooth-agent debug trace --agent rag "test query" --verbose

# 3. Check for dict vs object access issues
# Look for DetailedAttributeError in logs
```

### Scenario 2: "Flow execution is slow"
```bash
# 1. Profile the flow
goldentooth-agent debug profile "flow exec my_flow" --iterations 10

# 2. Use advanced monitoring in code
# Add monitored_stream() combinator

# 3. Check for bottlenecks
# Use PerformanceMonitor for detailed analysis
```

### Scenario 3: "Random failures in agent execution"
```bash
# 1. Health check for intermittent issues
goldentooth-agent debug health --export baseline_health.json

# 2. Multiple trace runs to catch failures
for i in {1..10}; do
  goldentooth-agent debug trace --agent rag "test $i" --verbose
done

# 3. Use FlowDebugger with conditions
# Set breakpoints for failure conditions
```

### Scenario 4: "Memory usage growing over time"
```python
# Use memory tracking in PerformanceMonitor
from goldentooth_agent.flow_engine.observability.performance import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.enable_memory_tracking()

# Monitor long-running operations
async for item in monitored_stream(long_running_flow, monitor):
    if monitor.get_memory_usage() > threshold:
        print("Memory usage high, investigating...")
        break
```

## 🎯 Error-Specific Debugging

### AttributeError: 'dict' object has no attribute 'response'
**Immediate action:**
1. Use `DetailedAttributeError` for enhanced context
2. Check if object should be dict access: `obj["response"]`
3. Validate response types in agent interfaces

**Prevention:**
- Use type hints: `-> AgentResponse` instead of `-> dict[str, Any]`
- Use `AgentResponse.from_dict()` for conversion
- Enable static analysis with `scripts/check_dict_access.py`

### Flow execution hangs or times out
**Investigation:**
1. Use `trace_stream()` to identify where execution stops
2. Set breakpoints with `FlowDebugger` at suspected points
3. Check for deadlocks in async operations
4. Profile with `benchmark_stream()` for timing analysis

**Tools:**
```python
# Add timeout monitoring
from goldentooth_agent.flow_engine.combinators.observability import timeout_stream

safe_flow = flow | timeout_stream(max_duration=30.0)
```

### Performance degradation
**Analysis workflow:**
1. Baseline measurement: `debug profile` before changes
2. Comparison testing: `debug profile` after changes
3. Statistical analysis: Use `benchmark_stream()` with multiple runs
4. Memory profiling: Enable memory tracking in `PerformanceMonitor`

## 📁 File Locations Quick Reference

### CLI Commands
- **Main CLI**: `src/goldentooth_agent/cli/main.py`
- **Debug commands**: `src/goldentooth_agent/cli/commands/debug.py`

### Core Debugging Infrastructure
- **Flow debugging**: `src/goldentooth_agent/flow_engine/observability/debugging.py`
- **Performance monitoring**: `src/goldentooth_agent/flow_engine/observability/performance.py`
- **Health checks**: `src/goldentooth_agent/flow_engine/observability/health.py`
- **Flow analysis**: `src/goldentooth_agent/flow_engine/observability/analysis.py`

### Observability Combinators
- **Stream observability**: `src/goldentooth_agent/flow_engine/combinators/observability.py`

### Error Enhancement
- **Enhanced errors**: `src/goldentooth_agent/core/util/error_reporting.py`
- **Debug context**: `src/goldentooth_agent/dev/debugging.py`

### Examples and Documentation
- **Performance examples**: `examples/performance_optimization_demo.py`
- **Testing utilities**: `tests/flow_engine/observability/`

## 🎓 Advanced Debugging Patterns

### Custom Debugging Flows
```python
# Create debugging-enhanced flows
def create_debug_flow(base_flow, debug_level="INFO"):
    return (
        base_flow
        | log_stream(level=debug_level)
        | inspect_stream(context={"debug_mode": True})
        | metrics_stream(emitter=debug_metrics)
    )

# Use conditional debugging
def debug_on_condition(flow, condition):
    def debug_wrapper(stream):
        async for item in stream:
            if condition(item):
                # Enable debugging for this item
                debug_item = await debug_single_item(item, flow)
                yield debug_item
            else:
                yield await flow.process_single(item)
    return debug_wrapper
```

### Production Debugging
```python
# Safe production debugging with sampling
class ProductionDebugger:
    def __init__(self, sample_rate=0.01):
        self.sample_rate = sample_rate
        self.monitor = PerformanceMonitor()

    def should_debug(self):
        return random.random() < self.sample_rate

    async def debug_stream(self, flow, stream):
        async for item in stream:
            if self.should_debug():
                # Safe debugging with monitoring
                with self.monitor.timer("debug_operation"):
                    debug_info = await self.collect_debug_info(item)
                    yield (item, debug_info)
            else:
                yield (item, None)
```

## 📞 Getting Help

### When You're Stuck
1. **Check this guide first** - Most common issues are covered
2. **Run health check**: `goldentooth-agent debug health --export status.json`
3. **Collect trace data**: `goldentooth-agent debug trace` for the failing operation
4. **Performance baseline**: `goldentooth-agent debug profile` to identify timing issues

### Reporting Issues
Include this debugging information:
- System health report: `goldentooth-agent debug health --export health.json`
- Execution trace: `goldentooth-agent debug trace --verbose` output
- Performance profile: `goldentooth-agent debug profile` results
- Error context: Full exception details with enhanced error reporting

### Additional Resources
- **Guidelines**: All files in `guidelines/` directory
- **Examples**: `examples/` directory for usage patterns
- **Tests**: `tests/` directory for testing patterns
- **Module docs**: `README.md` files in each module directory

This debugging guide ensures you can quickly identify and resolve issues using the comprehensive debugging infrastructure built into the Goldentooth Agent system.
