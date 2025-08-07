# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Goldentooth intelligent agent - a Rust application for managing a Raspberry Pi cluster infrastructure. The agent is designed to integrate with the broader Goldentooth ecosystem, providing intelligent automation and management capabilities for the cluster.

## Essential Commands

### Development Workflow
```bash
# Build and run
cargo run                              # Run development binary
cargo build                           # Development build
cargo build --release                 # Production build

# Testing
cargo test                            # Run all tests
cargo test --verbose                  # Run tests with detailed output
cargo test test_name                  # Run specific test
cargo test --test '*'                 # Run integration tests only

# Code Quality
cargo fmt --all                      # Format all code
cargo fmt --all -- --check          # Check formatting without changing files
cargo clippy                         # Run linter
cargo clippy -- -D warnings         # Run linter with warnings as errors
cargo clippy --all-targets --all-features -- -D warnings  # Full lint check

# Documentation
cargo doc                            # Generate documentation
cargo doc --no-deps --document-private-items --all-features  # Full documentation

# Security
cargo audit                          # Security audit (requires cargo-audit)

# Coverage (requires cargo-llvm-cov)
cargo llvm-cov --all-features --workspace --lcov --output-path lcov.info
```

### Cross-compilation for Raspberry Pi
```bash
# Install target
rustup target add aarch64-unknown-linux-gnu

# Build for Raspberry Pi (requires gcc-aarch64-linux-gnu)
export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc
cargo build --release --target aarch64-unknown-linux-gnu
```

### Pre-commit Setup
```bash
pre-commit install                   # Install git hooks (required for development)
pre-commit run --all-files          # Run all hooks manually
```

## Architecture and Technology Stack

### Core Dependencies
- **Async Runtime**: Tokio with multi-thread runtime for concurrent operations
- **HTTP Client**: reqwest with rustls-tls for secure cluster communication  
- **CLI Framework**: clap with derive features for command-line interface
- **Serialization**: serde with JSON support for data interchange
- **Error Handling**: thiserror for structured error types
- **Logging**: log crate for structured logging
- **Time Handling**: chrono for timestamp management

### Code Quality Configuration
- **Edition**: Rust 2024 edition
- **MSRV**: Minimum supported Rust version 1.70.0
- **Formatting**: 100 character line width, Unix line endings, 4-space indentation
- **Linting**: Clippy with warnings as errors, wildcard import warnings enabled
- **Testing**: Relaxed lint rules in tests (allows unwrap, expect, dbg!)

### GitHub Actions Integration
The project includes comprehensive CI/CD workflows:
- **CI Pipeline**: Multi-job testing, security auditing, documentation checks, cross-platform builds
- **Release Pipeline**: Automated releases for x86_64 and aarch64 Linux targets
- **Claude Integration**: Automated code review and @claude mention responses with Rust tooling
- **Version Management**: Automated version bumping on main branch commits

### Pre-commit Quality Gates
All commits are enforced with hooks for:
- Code formatting (rustfmt with edition 2024)
- Linting (cargo clippy with warnings as errors) 
- Compilation verification (cargo check)
- Test execution (cargo test)
- File hygiene (trailing whitespace, YAML/TOML validation, security checks)

## Development Context

This agent is part of the larger Goldentooth infrastructure project for Raspberry Pi cluster management. The codebase should integrate seamlessly with existing Goldentooth services and follow the established patterns for cluster communication, error handling, and logging.

The project is configured for deployment to ARM64 Raspberry Pi nodes, with cross-compilation support and release automation targeting both x86_64 and aarch64 Linux architectures.