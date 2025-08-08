# 🧞 Goldentooth Agent

**Status: Rebuilding from scratch** - Simple, practical agent for Goldentooth cluster management.

## What This Is

A command-line agent that makes managing the Goldentooth Raspberry Pi cluster easier and more conversational. Instead of remembering complex `goldentooth` CLI commands, you can:

```bash
# Simple cluster status
goldentooth-agent status

# Ask for help in natural language
goldentooth-agent chat "Why is allyrion using so much CPU?"

# Execute commands with intelligent context
goldentooth-agent fix "High memory usage on jast"
```

**Design Philosophy**: Working software that solves real problems > Perfect architecture that doesn't work.

## Quick Start

**Prerequisites:**
- Rust 1.70+
- SSH access to Goldentooth cluster nodes
- Working `goldentooth` CLI installation

**Get Running (< 2 minutes):**

```bash
# Clone and build
git clone <repository-url>
cd agent
cargo build

# Test cluster connectivity
cargo run -- ping allyrion

# Check cluster status
cargo run -- status

# Start interactive chat
cargo run -- chat
```

**Expected Output:**
```
$ cargo run -- ping allyrion
✓ allyrion.goldentooth.net: reachable (15ms)

$ cargo run -- status
Cluster Status:
├─ allyrion: healthy (uptime: 23d 4h)
├─ jast: healthy (uptime: 23d 4h)
├─ karstark: warning (high CPU: 85%)
└─ 10 other nodes: healthy
```

## Development

**Primary Development Loop** (< 30 seconds):
```bash
cargo run -- ping allyrion    # Test basic connectivity
cargo test integration        # Integration tests
cargo clippy && cargo test    # Quality gates
```

**Add New Command:**
```bash
# 1. Add command to src/cli/commands.rs
# 2. Write integration test in tests/integration/
# 3. cargo test && commit
```

**Character Development (Phase 2+):**
```bash
cargo run -- chat "Dr. Thorne, what's the cluster status?"
# Should respond in character with helpful analysis
```

## Commands

### Working Commands (Phase 1)
- `ping <node>` - Test node connectivity
- `status` - Show cluster health overview
- `exec <node> <command>` - Execute SSH command on node
- `logs <node> [service]` - Show service logs

### Planned Commands (Phase 2+)
- `chat <message>` - Interactive character conversations
- `ask <character> <question>` - Query specific personas
- `fix <problem>` - Automated problem resolution
- `explain <situation>` - Get detailed explanations

## Architecture

**Current Architecture (Simple & Working):**
```
src/
├── main.rs           # Working CLI interface
├── cli/              # Command parsing and execution
├── agent/            # Basic cluster communication
└── error.rs          # Simple error handling
```

**Future Architecture (After Phase 1 Success):**
```
src/
├── persona/          # Character system
├── knowledge/        # RAG integration
└── automation/       # Intelligent problem solving
```

## Integration with Goldentooth

**Uses existing infrastructure:**
- SSH keys for node authentication
- `goldentooth` CLI for complex operations
- Existing monitoring endpoints (node_exporter, etc.)
- Standard cluster networking

**Extends with new capabilities:**
- Natural language interaction
- Character-driven responses
- Intelligent problem diagnosis
- Automated remediation suggestions

## Testing

**Integration Tests (Primary):**
```bash
cargo test integration              # Test against real cluster
cargo test --test cli_tests         # End-to-end CLI testing
```

**Unit Tests (Secondary):**
```bash
cargo test unit                     # Component testing
```

**Manual Testing:**
```bash
# Test SSH connectivity
ssh pi@allyrion uptime

# Test goldentooth CLI integration
goldentooth ping allyrion

# Test agent commands
cargo run -- status
```

## Troubleshooting

**Common Issues:**

1. **"Connection refused"**: Check SSH keys and cluster network
   ```bash
   ssh pi@allyrion uptime  # Test direct SSH
   ```

2. **"Command not found"**: Ensure `goldentooth` CLI is installed
   ```bash
   which goldentooth
   goldentooth --version
   ```

3. **Build errors**: Check Rust version
   ```bash
   rustc --version  # Should be 1.70+
   ```

**Debug Mode:**
```bash
RUST_LOG=debug cargo run -- status
```

## Contributing

**For Contributors:**
1. Read `CLAUDE.md` for development philosophy
2. Start with integration tests - test against real cluster
3. Keep the development cycle fast (< 30 seconds)
4. Focus on user value over architectural perfection

**For Users:**
1. Try the basic commands first
2. Report what's helpful vs. what's confusing
3. Suggest new commands that would solve real problems
4. Test character interactions when available

## Release Strategy

**Phase 1 Release** (Week 1): Basic cluster commands working
**Phase 2 Release** (Week 2-3): Simple character system
**Phase 3+ Releases**: Advanced features based on user feedback

**Install from Release:**
```bash
# When releases are available
wget https://github.com/goldentooth/agent/releases/latest/goldentooth-agent
chmod +x goldentooth-agent
./goldentooth-agent --version
```

## Project Status

**Current Status**: Rebuilding from scratch with focus on working software
**Previous Implementation**: Over-engineered, complex abstractions, long feedback cycles
**New Approach**: Simple, practical, user-focused development

**Success Metrics:**
- Week 1: Basic commands work reliably
- Week 2: Users find agent more convenient than direct CLI
- Week 3+: Character system provides engaging, helpful interactions

This agent prioritizes **solving real cluster management problems** over implementing perfect theoretical architectures.
