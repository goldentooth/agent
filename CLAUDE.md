# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Goldentooth intelligent agent - a **rebuilt from scratch** Rust application for managing a Raspberry Pi cluster infrastructure. The agent provides intelligent automation and management capabilities with a focus on **working software over perfect design**.

**CRITICAL DEVELOPMENT PHILOSOPHY**: This project prioritizes rapid feedback cycles, working end-to-end functionality, and user value over architectural perfection.

## Essential Commands

### Rapid Development Workflow

**Primary Development Loop** (< 30 seconds):
```bash
# The golden development cycle - keep this fast
cargo run -- ping allyrion          # Test basic cluster connectivity
cargo test integration              # Run integration tests against real cluster
cargo clippy && cargo test          # Quality gates
```

**Extended Development Tasks**:
```bash
# Development builds
cargo run                           # Run development binary with real cluster
cargo run -- --help                # Verify CLI interface works
cargo run -- status                # Test cluster status command
cargo run -- exec allyrion uptime  # Test SSH execution

# Testing strategy
cargo test unit                     # Unit tests (mocked)
cargo test integration             # Integration tests (real cluster)
cargo test --test cli_tests        # End-to-end CLI tests
```

### Code Quality (Keep Fast)
```bash
# Daily quality checks (< 60 seconds total)
cargo fmt                          # Format code
cargo clippy -- -D warnings       # Linter with warnings as errors
cargo test                         # All tests must pass
cargo build --release             # Verify release build

# Weekly quality checks
cargo audit                        # Security audit
cargo doc --document-private-items # Documentation check
```

## Development Principles

### 1. Working Software First
- `main.rs` must always contain a working CLI - never "Hello, world!"
- Every commit should maintain a working end-to-end flow
- Integration tests run against the real Goldentooth cluster
- Mock only when real cluster is unavailable

### 2. Bottom-Up Development
```
Week 1: CLI + Basic SSH → Working agent commands
Week 2: Simple character responses → Basic persona system
Week 3: Multi-character → Character interactions
Week N: Advanced features → Only after previous weeks prove valuable
```

### 3. Rapid Feedback Cycles
- Primary development loop: `cargo run -- ping allyrion` (< 5 seconds)
- Integration test suite: `cargo test integration` (< 30 seconds)
- Full quality gate: `cargo clippy && cargo test` (< 60 seconds)
- **If any step takes longer, optimize it immediately**

### 4. Real Integration Early
```bash
# Test against real cluster from day 1
goldentooth ping allyrion           # Use existing goldentooth CLI
ssh pi@allyrion uptime             # Direct SSH verification
goldentooth exec allyrion "ps aux" # Command execution verification
```

## Architecture Constraints

### Core Dependencies (Minimal)
- **CLI**: `clap` with derive features - simple command interface
- **SSH**: Direct `std::process::Command` execution initially
- **Error Handling**: `thiserror` for structured errors
- **Async**: `tokio` only when proven necessary, not by default
- **Serialization**: `serde` only for configuration files

### **FORBIDDEN** Dependencies Initially
- Complex HTTP client abstractions
- Heavy async trait abstractions
- ORM or complex data persistence
- Complex logging frameworks
- Heavyweight testing frameworks

Add dependencies only when current implementation proves insufficient.

### Code Organization
```
src/
├── main.rs              # Working CLI - never "Hello, world!"
├── lib.rs               # Minimal public API
├── cli/
│   ├── mod.rs
│   └── commands.rs      # Working commands that solve real problems
├── agent/
│   ├── mod.rs
│   ├── cluster.rs       # Direct SSH execution, simple and fast
│   └── simple_agent.rs  # Basic agent without personas initially
└── error.rs             # Simple error types, no over-engineering
```

### Testing Strategy

**Integration-First Testing**:
```rust
#[tokio::test]
async fn test_can_ping_cluster_node() {
    // Test against real goldentooth cluster
    let result = ping_node("allyrion").await;
    assert!(result.is_ok());
}

#[tokio::test]
async fn test_cli_status_command() {
    // Test actual CLI command
    let output = run_cli(&["status"]).await;
    assert!(output.contains("allyrion") && output.contains("healthy"));
}
```

**Unit testing** comes after integration tests prove the concept works.

### Character System (Phase 2+)

**DO NOT** implement complex persona system until basic agent provides user value.

When implementing personas:
1. Start with one simple character (Dr. Thorne)
2. Static personality - no evolution initially
3. Simple response generation - no complex trait systems
4. Focus on helpful responses to real cluster problems

```rust
// Simple persona trait - no complex abstractions
trait Persona {
    fn name(&self) -> &str;
    async fn respond(&self, input: &str, cluster_status: &ClusterStatus) -> String;
}

// Not this:
// Complex personality evolution, modifiers, relationship systems, etc.
```

## Development Workflow

### Daily Development (Weeks 1-2)
1. `cargo run -- ping allyrion` - verify basic connectivity
2. Add one new CLI command that solves a real problem
3. Write integration test for the new command
4. `cargo clippy && cargo test` - quality gates
5. Commit working software

### Weekly Development (Week 3+)
1. Review what users actually use vs. what we built
2. Remove unused features/abstractions
3. Add new features only based on real user requests
4. Optimize slow development feedback loops

### Crisis Development (When Things Break)
1. **Don't add abstractions** to fix problems
2. **Don't refactor** during crisis mode
3. **Fix the immediate problem** with minimal code
4. **Add tests** to prevent regression
5. **Refactor later** when things are stable

## Integration with Goldentooth Ecosystem

### Existing Tools Integration
- Use `goldentooth` CLI commands where possible
- Integrate with existing SSH patterns
- Respect existing node naming conventions
- Follow established cluster communication patterns

### Service Integration Priority
1. **Week 1**: SSH connectivity to nodes (allyrion, jast, etc.)
2. **Week 2**: Basic health checks via node_exporter
3. **Week 3**: Status queries to services (Consul, Nomad, etc.)
4. **Week N**: Advanced integrations only after basic value proven

## Troubleshooting Development Issues

### Long Build Times
- Profile with `cargo build --timings`
- Remove unnecessary dependencies
- Use `cargo check` for faster feedback
- Parallelize tests with `--test-threads`

### Flaky Tests
- Test against real cluster state, don't mock cluster
- Add retry logic for network operations
- Use proper async test timeouts
- Fix root cause, don't skip tests

### Complex Debugging
- Add `RUST_LOG=debug` support early
- Use `dbg!()` macro liberally in development
- Write reproduction tests for bugs
- Keep error messages actionable

## Success Metrics

### Week 1 Success
- `cargo run -- ping allyrion` works
- `cargo run -- status` shows cluster health
- Integration tests pass against real cluster
- Development cycle < 30 seconds

### Week 2 Success
- Users can query cluster status via agent
- Basic problem-solving commands work
- Agent provides more value than direct `goldentooth` CLI usage

### Long-term Success
- Users prefer agent over direct cluster tools
- Agent helps solve problems faster than manual investigation
- Character interactions are engaging and helpful
- System is reliable and fast

## Anti-Patterns to Avoid

Based on lessons learned from previous implementation:

1. **Don't build complex abstractions** before proving basic functionality
2. **Don't implement personality evolution** before static personas provide value
3. **Don't create complex async trait hierarchies** - use simple functions
4. **Don't mock everything** - integrate with real cluster early
5. **Don't write extensive documentation** before software works
6. **Don't optimize prematurely** - optimize feedback cycles instead

**Remember**: Working software that solves real problems beats perfect architecture that doesn't work.
