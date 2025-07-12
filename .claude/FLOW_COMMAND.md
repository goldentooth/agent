  Core Vision & Requirements

  The flow_command package will provide seamless integration between Typer/Click CLI and the Flow system, supporting
  both CLI and chat REPL contexts with consistent interfaces, comprehensive testing, and reliable async/sync
  operation bridging.

  Key Design Principles

  1. Universal Interface: Commands work identically in CLI and chat contexts
  2. Command Façade Pattern: Thin CLI wrappers around testable implementation functions
  3. Async/Sync Bridge: Transparent handling of async Flow operations in sync CLI contexts
  4. Comprehensive Testing: Unit and integration tests for all command variants
  5. Type Safety: Full generic type preservation from Flow system
  6. Rich Terminal: Advanced display with fallback support

  Proposed Package Structure

  src/flow_command/
  ├── __init__.py                 # Public API exports
  ├── core/
  │   ├── __init__.py
  │   ├── context.py             # Universal command context
  │   ├── bridge.py              # Async/sync execution bridge
  │   ├── exceptions.py          # Command-specific exceptions
  │   └── result.py              # Command result types
  ├── cli/
  │   ├── __init__.py
  │   ├── main.py                # CLI app and command registration
  │   ├── display.py             # Rich terminal display utilities
  │   └── commands/
  │       ├── __init__.py
  │       ├── flow_ops.py        # Flow operation commands (run, list, search)
  │       ├── flow_compose.py    # Flow composition commands
  │       └── flow_debug.py      # Flow debugging commands
  ├── chat/
  │   ├── __init__.py
  │   ├── handlers.py            # Chat command handlers (/flow commands)
  │   └── parser.py              # Chat command parsing
  ├── async_bridge/
  │   ├── __init__.py
  │   ├── loop_manager.py        # Relocated BackgroundEventLoop
  │   ├── execution.py           # Flow execution in sync contexts
  │   └── context_manager.py     # Async context management
  └── testing/
      ├── __init__.py
      ├── fixtures.py            # Test fixtures and utilities
      ├── mocks.py               # Mock objects for testing
      └── helpers.py             # Test helper functions

  Core Components Architecture

  1. Universal Command Context (core/context.py)

  @dataclass
  class FlowCommandContext:
      """Universal context for flow commands across CLI and chat interfaces."""
      # Input/Output
      input_data: Any = None
      output_format: Literal["text", "json", "table"] = "text"

      # Display configuration
      plain_output: bool = False
      interactive: bool = True
      record_svg: bool = False
      console: Console = field(default_factory=Console)

      # Flow-specific
      flow_registry: FlowRegistry = field(default_factory=lambda: flow_registry)
      execution_timeout: float = 30.0

      # Context identification
      source: Literal["cli", "chat", "test"] = "cli"
      user_id: Optional[str] = None

      @classmethod
      def from_cli(cls, **kwargs) -> FlowCommandContext:
          """Create context from CLI parameters."""

      @classmethod
      def from_chat(cls, **kwargs) -> FlowCommandContext:
          """Create context from chat interface."""

      @classmethod
      def from_test(cls, **kwargs) -> FlowCommandContext:
          """Create context for testing."""

  2. Async/Sync Bridge (async_bridge/)

  Relocated BackgroundEventLoop with Flow-specific optimizations:

  # async_bridge/loop_manager.py
  class FlowEventLoop(BackgroundEventLoop):
      """Flow-optimized background event loop with enhanced capabilities."""

      def execute_flow(self, flow: Flow[T, U], input_stream: AsyncIterable[T]) -> list[U]:
          """Execute a flow synchronously, returning collected results."""

      def execute_flow_streaming(self, flow: Flow[T, U], input_stream: AsyncIterable[T]) -> Iterator[U]:
          """Execute a flow with streaming output."""

      def execute_with_timeout(self, coroutine: Coroutine[Any, Any, T], timeout: float) -> T:
          """Execute coroutine with timeout handling."""

  # async_bridge/execution.py
  def run_flow_sync(
      flow: Flow[T, U],
      input_data: Iterable[T],
      context: FlowCommandContext
  ) -> FlowCommandResult[U]:
      """Execute flow synchronously in any context."""

  async def run_flow_async(
      flow: Flow[T, U],
      input_data: AsyncIterable[T],
      context: FlowCommandContext
  ) -> FlowCommandResult[U]:
      """Execute flow asynchronously when in async context."""

  3. Command Result System (core/result.py)

  @dataclass
  class FlowCommandResult(Generic[T]):
      """Structured result from flow command execution."""
      success: bool
      data: Optional[T] = None
      error: Optional[str] = None
      metadata: dict[str, Any] = field(default_factory=dict)
      execution_time: float = 0.0

      def to_display(self, context: FlowCommandContext) -> str:
          """Convert result to display format based on context."""

      def to_json(self) -> dict[str, Any]:
          """Convert result to JSON representation."""

  4. CLI Command Architecture (cli/commands/)

  Following the command façade pattern:

  # cli/commands/flow_ops.py
  @app.command("run")
  def flow_run_cli(
      flow_name: Annotated[str, typer.Argument(help="Name of flow to execute")],
      input_file: Annotated[Optional[Path], typer.Option("--input", "-i")] = None,
      output_format: Annotated[str, typer.Option("--format", "-f")] = "text",
      timeout: Annotated[float, typer.Option("--timeout", "-t")] = 30.0,
      plain: Annotated[bool, typer.Option("--plain", "-p")] = False,
      record: Annotated[bool, typer.Option("--record", "-r")] = False,
  ) -> None:
      """Execute a registered flow with input data."""
      # Create context
      context = FlowCommandContext.from_cli(
          output_format=output_format,
          plain_output=plain,
          record_svg=record,
          execution_timeout=timeout
      )

      # Execute implementation
      result = flow_run_implementation(flow_name, input_file, context)

      # Handle display and exit
      display = FlowDisplay(context)
      display.show_result(result)
      if not result.success:
          raise typer.Exit(1)

  def flow_run_implementation(
      flow_name: str,
      input_file: Optional[Path],
      context: FlowCommandContext
  ) -> FlowCommandResult[Any]:
      """Pure implementation function - easily testable."""
      # Business logic implementation
      flow = context.flow_registry.get_flow(flow_name)
      input_data = load_input_data(input_file)
      return run_flow_sync(flow, input_data, context)

  5. Chat Integration (chat/handlers.py)

  class FlowChatHandler:
      """Handler for /flow commands in chat interface."""

      def handle_flow_run(self, args: list[str], chat_context: ChatContext) -> ChatResponse:
          """Handle /flow run command in chat."""
          # Parse chat arguments to CLI-equivalent parameters
          parsed = parse_flow_command(args)

          # Create flow command context
          context = FlowCommandContext.from_chat(
              source="chat",
              user_id=chat_context.user_id,
              **parsed
          )

          # Execute same implementation as CLI
          result = flow_run_implementation(parsed.flow_name, parsed.input_file, context)

          # Convert to chat response
          return ChatResponse.from_flow_result(result)

  Testing Strategy

  1. Unit Testing Pattern

  # tests/unit/flow_command_tests/core/test_execution.py
  class TestFlowExecution:
      def test_flow_run_implementation_success(self) -> None:
          """Test successful flow execution."""
          context = FlowCommandContext.from_test()
          result = flow_run_implementation("test_flow", None, context)

          assert result.success is True
          assert result.data is not None
          assert result.error is None

      def test_flow_run_implementation_timeout(self) -> None:
          """Test flow execution timeout handling."""
          context = FlowCommandContext.from_test(execution_timeout=0.1)
          result = flow_run_implementation("slow_flow", None, context)

          assert result.success is False
          assert "timeout" in result.error.lower()

  2. CLI Integration Testing

  # tests/integration/flow_command_tests/cli/test_cli_integration.py
  class TestFlowCLI:
      def setup_method(self) -> None:
          self.runner = CliRunner()

      def test_flow_run_command_success(self) -> None:
          """Test successful flow run command."""
          result = self.runner.invoke(app, [
              "flow", "run", "test_flow",
              "--format", "json",
              "--plain"
          ])

          assert result.exit_code == 0
          output = json.loads(result.output)
          assert output["success"] is True

      def test_flow_run_command_timeout(self) -> None:
          """Test flow run command with timeout."""
          result = self.runner.invoke(app, [
              "flow", "run", "slow_flow",
              "--timeout", "0.1"
          ])

          assert result.exit_code == 1
          assert "timeout" in result.output.lower()

  3. Chat Integration Testing

  # tests/integration/flow_command_tests/chat/test_chat_integration.py
  class TestFlowChatIntegration:
      def test_flow_run_chat_command(self) -> None:
          """Test /flow run command in chat context."""
          handler = FlowChatHandler()
          chat_context = ChatContext(user_id="test_user")

          response = handler.handle_flow_run(
              ["run", "test_flow", "--format", "json"],
              chat_context
          )

          assert response.success is True
          assert response.data is not None

## Current Implementation Status

### ✅ COMPLETED - Phase 1: Foundation
- [x] Core architecture (core/, async_bridge/) - **DONE**
- [x] Universal context and result systems - **DONE**
- [x] BackgroundEventLoop relocated to async_bridge/loop_manager.py - **DONE**
- [x] Comprehensive testing infrastructure - **DONE**

### ✅ COMPLETED - Phase 2: Flow Operations
- [x] Basic flow commands (list, search, run) - **DONE**
- [x] CLI façades with implementation separation - **DONE**
- [x] Comprehensive unit tests for all implementations - **DONE**
- [x] CLI integration tests - **DONE**

### ✅ COMPLETED - Phase 3: CLI Registration & Integration

**CURRENT STATUS:** CLI integration is now complete! All critical issues resolved:

#### Priority 1: CLI Registration & Integration ✅ COMPLETED
- [x] **CRITICAL**: Integrate flow_command with goldentooth_agent CLI
- [x] Register flow_command.cli.app with main goldentooth_agent CLI
- [x] Resolve duplicate flow command implementations
- [x] Add CLI integration tests that test actual command execution

**BREAKTHROUGH:** The `flow_command` package is now fully integrated with the main CLI!
Users can now execute `goldentooth-agent flow list/run/search` with complete functionality.

### 🚧 NEXT PHASE - Flow Registry Integration
- [ ] Connect flow_command to actual Flow registry with real flows
- [ ] Implement flow registration mechanism
- [ ] Add flow discovery and validation
- [ ] Create sample flows for testing

#### Priority 3: Rich Terminal Display
- [ ] Complete FlowDisplay implementation with Rich formatting
- [ ] Add SVG recording capabilities
- [ ] Implement progress bars for long-running flows
- [ ] Add table/JSON/text output formatting

#### Priority 4: Chat Integration
- [ ] Create chat command handlers (/flow commands)
- [ ] Implement chat command parsing
- [ ] Add chat integration tests
- [ ] Cross-context compatibility testing

### 🔮 FUTURE - Phase 4: Advanced Features
1. Flow composition commands (compose, validate)
2. Advanced debugging capabilities (debug, trace, monitor)
3. Performance optimization and monitoring
4. Real-time flow execution status

  Migration Strategy for BackgroundEventLoop

  The BackgroundEventLoop should be relocated to flow_command/async_bridge/loop_manager.py with the following
  enhancements:

  1. Flow-specific optimizations for stream processing
  2. Enhanced timeout handling for long-running flows
  3. Resource management for flow execution contexts
  4. Monitoring integration with flow observability system

  This architecture provides a robust, testable, and extensible foundation for seamless Flow/Typer integration that
  works consistently across CLI, chat, and testing contexts while maintaining the high quality standards required by
  the guidelines.
