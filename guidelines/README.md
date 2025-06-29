# Development Guidelines

This directory contains comprehensive development guidelines for the Goldentooth Agent project. These guidelines ensure consistency, quality, and maintainability across the large codebase (25K+ lines of code).

## Directory Contents

- **[code-style.md](code-style.md)** - Comprehensive code style and formatting standards, including naming conventions, import organization, and file structure guidelines
- **[testing-standards.md](testing-standards.md)** - Testing philosophy, patterns, and requirements including TDD practices, test organization, and coverage standards
- **[type-safety.md](type-safety.md)** - Type annotation requirements, mypy configuration, and type safety best practices for maintaining strict type checking
- **[architecture.md](architecture.md)** - System architecture patterns, module organization, dependency injection guidelines, and design principles
- **[performance.md](performance.md)** - Performance standards, optimization guidelines, benchmarking practices, and critical performance targets
- **[documentation.md](documentation.md)** - Documentation standards for code, APIs, modules, and system components including README requirements
- **[module-development.md](module-development.md)** - Guidelines for working with large modules, refactoring strategies, and module-specific development practices
- **[error-handling.md](error-handling.md)** - Exception handling patterns, error propagation strategies, and async error handling best practices

## Usage

These guidelines are referenced by:
- Developers working on the codebase
- Code review processes
- CI/CD quality gates
- Claude Code (AI assistant) via CLAUDE.md for consistent development assistance

## Enforcement

Guidelines are enforced through:
- Pre-commit hooks (`poetry run poe test && poetry run poe typecheck`)
- CI/CD pipelines with quality gates
- Code review requirements
- Automated tooling (mypy, pytest, etc.)

## Updates

Guidelines should be updated when:
- New patterns emerge in the codebase
- Architecture decisions change
- Tool configurations are modified
- Best practices evolve

All guideline updates should be reviewed and approved before merging to ensure consistency across the development team.