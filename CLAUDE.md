# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an experimental intelligent agent for a Pi Bramble. The project uses a modern Python package structure with CLI interface.

## Development Commands

### Running the Application
```bash
# Using the installed console script
goldentooth-agent

# Or using the short alias
gta

# Available commands:
goldentooth-agent status   # Show agent status
goldentooth-agent start    # Start the agent
goldentooth-agent stop     # Stop the agent
goldentooth-agent info     # Show detailed information
goldentooth-agent --help   # Show help
```

### Development Tools
```bash
# Install development dependencies
uv sync --group dev

# Run linting
ruff check .
ruff format .

# Run type checking
mypy .

# Run tests
pytest
```

### Python Version
Requires Python 3.11 or higher (specified in pyproject.toml:6)

## Project Structure

- `goldentooth_agent/` - Main package directory
  - `__init__.py` - Package initialization and version info
  - `main.py` - Core Agent class implementation
  - `cli.py` - Command-line interface using Typer and Rich
- `pyproject.toml` - Project configuration with modern Python tooling
- `README.md` - Basic project description
- `LICENSE` - Public domain license (Unlicense)

## Architecture Notes

The project uses a modern Python package structure with:
- **Core Agent Class**: `goldentooth_agent.main.Agent` - Main agent implementation with UUID-based identification
- **CLI Interface**: `goldentooth_agent.cli` - Rich command-line interface using Typer
- **Console Scripts**: Defined in pyproject.toml for easy installation (`goldentooth-agent` and `gta`)
- **Modern Tooling**: Configured with ruff, black, isort, mypy, pytest for development
- **Dependencies**: Uses typer for CLI and rich for beautiful console output

The project is designed for future expansion as an intelligent agent system for Raspberry Pi cluster computing.
