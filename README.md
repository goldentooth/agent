# 🧞 Goldentooth Agent

An intelligent agent for Goldentooth cluster management, built in Rust.

## Overview

The Goldentooth Agent is a Rust-based intelligent automation system designed to manage and orchestrate operations across the Goldentooth Raspberry Pi cluster infrastructure. It provides autonomous decision-making capabilities and seamless integration with the broader Goldentooth ecosystem.

## Features

- **Cluster Management**: Intelligent monitoring and management of Raspberry Pi cluster nodes
- **Async Operations**: Built on Tokio for high-performance concurrent operations
- **Secure Communication**: HTTP client with rustls-tls for secure cluster communication
- **Cross-Platform**: Supports both x86_64 and ARM64 architectures
- **CLI Interface**: Command-line interface built with clap
- **Structured Logging**: Comprehensive logging with the log crate
- **Error Handling**: Robust error handling with thiserror

## Quick Start

### Prerequisites

- Rust 1.70.0 or later
- For ARM64 builds: `gcc-aarch64-linux-gnu`

### Installation

```bash
# Clone the repository
git clone https://github.com/goldentooth/agent.git
cd agent

# Install pre-commit hooks
pre-commit install

# Build the project
cargo build --release
```

### Running

```bash
# Run in development mode
cargo run

# Run the release binary
./target/release/goldentooth-agent
```

## Development

### Building

```bash
# Development build
cargo build

# Release build
cargo build --release

# Cross-compile for Raspberry Pi
cargo build --release --target aarch64-unknown-linux-gnu
```

### Testing

```bash
# Run all tests
cargo test

# Run with verbose output
cargo test --verbose

# Run specific test
cargo test test_name
```

### Code Quality

```bash
# Format code
cargo fmt

# Run linter
cargo clippy

# Run all quality checks
cargo fmt --check && cargo clippy -- -D warnings && cargo test
```

## Architecture

The agent is built using modern Rust patterns with:

- **Tokio**: Async runtime for concurrent operations
- **Reqwest**: HTTP client for cluster communication
- **Serde**: JSON serialization/deserialization
- **Clap**: Command-line argument parsing
- **Thiserror**: Structured error handling

## Integration

This agent integrates with the broader Goldentooth infrastructure:

- **Cluster Nodes**: Direct communication with Raspberry Pi nodes
- **Service Discovery**: Integration with Consul service mesh
- **Monitoring**: Metrics and logging integration
- **Orchestration**: Works alongside Nomad and Kubernetes workloads

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install pre-commit hooks: `pre-commit install`
4. Make your changes
5. Ensure all tests pass: `cargo test`
6. Ensure code quality: `cargo fmt && cargo clippy`
7. Create a pull request

## CI/CD

The project includes comprehensive GitHub Actions workflows:

- **CI**: Automated testing, linting, and security audits
- **Release**: Automated releases with cross-platform binaries
- **Code Review**: Automated Claude-powered code reviews

## License

This project is released under the Unlicense - see the project files for details.

## Related Projects

Part of the Goldentooth ecosystem:
- [goldentooth/mcp-server](https://github.com/goldentooth/mcp-server) - MCP server for cluster management