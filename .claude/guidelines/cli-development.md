# CLI Development Guidelines

## Overview

These guidelines establish the standards and patterns for developing CLI commands in the Goldentooth Agent project. All CLI development must follow these principles to ensure consistency, testability, and maintainability.

## Core Principles

### 1. Integration Testing Requirement
- **MANDATORY**: Every command must have an integration test that actually executes it
- Tests must validate command output, exit codes, and side effects
- Mock backends for commands that invoke agents, make network requests, etc.
- Use `typer.testing.CliRunner` for consistent testing patterns
- Integration tests should cover both success and failure scenarios

### 2. Modern Typer Integration
- Use **Annotated[]** syntax for all parameter definitions
- Leverage type hints for automatic validation and help generation
- Follow Typer best practices for async commands
- Example pattern:
```python
from typing import Annotated
import typer

def command(
    input_file: Annotated[Path, typer.Option("--input", "-i", help="Input file path")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "text",
) -> None:
    """Command description here."""
    # Implementation calls separate function
    result = execute_command_logic(input_file, verbose, format)
    # Handle output/display
```

### 3. Command Façade Pattern
- Command functions must be minimal façades that delegate to separate implementation functions
- Implementation functions take the same arguments as command functions
- This enables comprehensive unit testing without CLI framework overhead
- Pattern:
```python
def command_cli(param1: str, param2: bool) -> None:
    """CLI command façade."""
    result = command_implementation(param1, param2)
    display_result(result)

def command_implementation(param1: str, param2: bool) -> CommandResult:
    """Actual command logic - easily unit testable."""
    # Implementation here
    return CommandResult(...)
```

### 4. Rich Terminal Interface
- Use Rich for all terminal output (tables, panels, progress bars, etc.)
- Include tasteful use of:
  - **Spinners** for long operations
  - **Colored text** for status indicators
  - **Emoji** for visual appeal (when appropriate)
  - **Progress bars** for multi-step operations
  - **Tables** for structured data
  - **Panels** for grouped information
- Provide `--no-color` / `--plain` options to disable rich formatting
- Support `NO_COLOR` environment variable
- Ensure output is still functional in basic terminals

### 5. SVG Output Recording
- Leverage Rich's built-in SVG export capabilities
- Provide `--record` option for commands to generate SVG demos
- Example implementation:
```python
from rich.console import Console
from rich.terminal_theme import DIMMED_MONOKAI

console = Console(record=True)
# Execute command with rich output
if record:
    console.save_svg("command_demo.svg", theme=DIMMED_MONOKAI)
```

### 6. Textual Interface Compatibility
- Design commands with potential Textual TUI integration in mind
- Separate display logic from business logic
- Use structured data types for command results
- Consider future rich terminal interfaces

### 7. Universal Command Pattern
- Commands should be executable from both CLI and chat interface
- Design commands as information processors, not CLI-specific tools
- Use common data structures and interfaces
- Pattern:
```python
@dataclass
class CommandContext:
    """Universal command context."""
    input_data: Any
    output_format: str
    interactive: bool
    user_id: Optional[str] = None

def universal_command(ctx: CommandContext) -> CommandResult:
    """Command logic that works in any interface."""
    # Implementation
```

## Implementation Standards

### File Structure
```
src/goldentooth_agent/cli/
├── __init__.py
├── main.py                 # Main CLI app
├── commands/
│   ├── __init__.py
│   ├── chat.py            # Chat commands
│   ├── agents.py          # Agent management
│   ├── tools.py           # Tool execution
│   └── ...
├── core/
│   ├── __init__.py
│   ├── display.py         # Rich display utilities
│   ├── context.py         # Command context
│   └── exceptions.py      # CLI exceptions
└── testing/
    ├── __init__.py
    ├── fixtures.py        # Test fixtures
    └── helpers.py         # Test helpers
```

### Test Structure
```
tests/
├── unit/
│   └── cli/
│       ├── commands/
│       │   ├── test_chat.py
│       │   └── test_agents.py
│       └── core/
│           └── test_display.py
└── integration/
    └── cli/
        ├── test_cli_integration.py
        └── commands/
            ├── test_chat_integration.py
            └── test_agents_integration.py
```

### Dependencies
- **Typer**: Modern CLI framework
- **Rich**: Terminal formatting and display
- **Textual**: Future TUI interface support
- **Pytest**: Testing framework
- **Pytest-asyncio**: Async test support

## Command Categories

### 1. Interactive Commands
- `chat` - Interactive chat interface
- `demo` - Interactive demonstrations
- Should support both CLI and TUI modes

### 2. Execution Commands
- `agents run` - Execute agents
- `tools run` - Execute tools
- `flow exec` - Execute flows
- Must support JSON input/output

### 3. Management Commands
- `agents list` - List available agents
- `tools list` - List available tools
- `flow list` - List available flows
- Should use Rich tables for output

### 4. Development Commands
- `debug` - Debugging utilities
- `dev` - Development tools
- Should provide verbose output options

### 5. Setup Commands
- `setup init` - Initialize system
- `docs` - Documentation management
- Should be idempotent

### 6. Integration Commands
- `github` - GitHub integration
- `git_sync` - Git synchronization
- Should handle authentication gracefully

## Migration Strategy

### Phase 1: Foundation
1. Create new CLI structure in `src/goldentooth_agent/cli/`
2. Set up testing framework
3. Create base display utilities
4. Establish command patterns

### Phase 2: Core Commands
1. Migrate essential commands (chat, agents, tools)
2. Implement comprehensive tests
3. Add rich terminal interfaces
4. Ensure universal command compatibility

### Phase 3: Advanced Features
1. Add SVG recording capabilities
2. Implement Textual integration
3. Add advanced display features
4. Optimize performance

### Phase 4: Complete Migration
1. Migrate remaining commands
2. Update documentation
3. Add demonstration SVGs
4. Final testing and validation

## Quality Gates

### Pre-commit Requirements
- All CLI commands must pass integration tests
- Rich output must be testable with `--plain` mode
- Command façades must be minimal
- Type hints must be comprehensive
- Documentation must be complete

### Testing Requirements
- Unit tests for all command implementation functions
- Integration tests for all CLI commands
- Mock external dependencies appropriately
- Test both success and failure scenarios
- Validate output formatting and content

### Documentation Requirements
- All commands must have clear docstrings
- Help text must be comprehensive
- Examples must be provided
- SVG demos for complex commands
- Migration notes for changed commands

## Future Considerations

### Textual Integration
- Commands should be designed with TUI compatibility in mind
- Separate business logic from display logic
- Use structured data types for results
- Consider real-time updates and interactions

### Chat Integration
- Commands should work in both CLI and chat contexts
- Use common interfaces and data structures
- Handle authentication and context appropriately
- Support both synchronous and asynchronous execution

### Performance
- Optimize startup time for CLI commands
- Use lazy loading for expensive imports
- Cache results where appropriate
- Provide progress feedback for long operations

## Enforcement

These guidelines are mandatory for all CLI development. Violations will result in:
- Code rejection and mandatory rework
- Extended review cycles
- Removal of CLI command integration

Excellence through consistency. No exceptions.
