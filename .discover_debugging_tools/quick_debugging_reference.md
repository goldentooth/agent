# Quick Debugging Reference Card

## 🚨 Common Problems → Tools

🏥 **System Health Problems**
- CLI: goldentooth-agent debug health
- Code: HealthCheck for component validation

🔍 **Execution/Runtime Issues**
- CLI: goldentooth-agent debug trace
- Code: FlowDebugger for interactive debugging
- Code: trace_stream() combinator

⚡ **Performance Problems**
- CLI: goldentooth-agent debug profile
- Code: PerformanceMonitor for detailed analysis
- Code: metrics_stream() combinator

🤖 **Agent-Specific Issues**
- CLI: goldentooth-agent debug trace --agent [type]

🌊 **Flow Execution Issues**
- CLI: goldentooth-agent debug trace --flow [name]
- Code: FlowDebugger with breakpoints

📝 **Attribute Access Errors**
- Auto: DetailedAttributeError with debugging hints

⚙️ **Configuration Issues**
- CLI: goldentooth-agent debug health

## 🎯 Quick Debugging Workflow

1. **System Check**: `goldentooth-agent debug health`
2. **Trace Issue**: `goldentooth-agent debug trace --verbose`
3. **Profile Performance**: `goldentooth-agent debug profile [command]`
4. **Deep Analysis**: Use FlowDebugger, PerformanceMonitor
5. **Follow Error Hints**: Enhanced error messages guide next steps

## 📚 Complete References

- [Debugging Guide](guidelines/debugging-guide.md) - Comprehensive debugging documentation
- [Tool Reference](#debugging-tools-reference) - Complete tool catalog
- [CLI Help](README.md#debugging--development) - Command examples
