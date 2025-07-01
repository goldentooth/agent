# Commands

Commands module

## Background & Motivation

### Problem Statement

The commands module addresses the challenge of managing commands-related operations in a complex system architecture.

### Theoretical Foundation

#### Core Concepts

The module implements domain-specific concepts tailored to its functional requirements.

#### Design Philosophy

**Simplicity and Clarity**: Emphasizes straightforward implementations that are easy to understand and maintain.

### Technical Challenges Addressed

1. **Modularity**: Designing clean interfaces that promote reusability and testability
2. **Maintainability**: Structuring code for easy modification and extension
3. **Integration**: Seamlessly connecting with other system components

### Integration & Usage

The commands module integrates with the broader system through well-defined interfaces.

**Key Dependencies:**
- goldentooth_agent.cli.commands.agents: Provides essential functionality required by this module
- goldentooth_agent.cli.commands.chat: Provides essential functionality required by this module
- goldentooth_agent.cli.commands.flow: Provides essential functionality required by this module
- goldentooth_agent.cli.commands.tools: Provides essential functionality required by this module
- goldentooth_agent.core.context: Provides essential functionality required by this module

**Usage Patterns:**
- **Dependency Injection**: Services are provided through the Antidote DI container
- **Type-Safe Interfaces**: All public APIs use comprehensive type annotations
- **Error Propagation**: Exceptions are handled consistently with the system's error handling patterns

---

*This background file was generated using AI analysis of the commands module. Please review and customize as needed.*

## Overview

- **Complexity**: Critical
- **Files**: 16 Python files
- **Lines of Code**: ~6272
- **Classes**: 8
- **Functions**: 143

## API Reference

### Classes

#### CalculatorInput
Input schema for calculator tool.

#### CalculatorOutput
Output schema for calculator tool.

#### EchoInput
Input schema for echo tool.

#### EchoOutput
Output schema for echo tool.

#### TraceStep
Class for tracestep functionality.

#### TraceDataDict
Class for tracedatadict functionality.

#### PipelineStepConfig
Configuration for a pipeline step.

#### Pipeline
Pipeline orchestrator for chaining tools together.

**Public Methods:**
- `add_step(self, tool_name: str, input_mapping: dict[str, str] | None, static_input: dict[str, Any] | None, output_key: str | None) -> Pipeline` - Add a step to the pipeline
- `async execute(self, initial_input: dict[str, Any], console: Console | None) -> dict[str, Any]` - Execute the pipeline with the given input

### Functions

#### `def calculator_implementation(input_data: CalculatorInput) -> CalculatorOutput`
Calculate mathematical expressions safely.

#### `def echo_implementation(input_data: EchoInput) -> EchoOutput`
Echo back the input message.

#### `def get_available_tools() -> dict[str, FlowTool]`
Get a registry of available tools.

#### `def list_tools() -> None`
List all available tools and their descriptions.

#### `def run_tool(tool_name: Annotated[str, typer.Argument(help='Name of the tool to run')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: text, json')], expression: Annotated[str | None, typer.Option('--expression', help='Mathematical expression (for calculator)')], message: Annotated[str | None, typer.Option('--message', help='Message to echo (for echo tool)')]) -> None`
Run a specific tool with input data.

#### `async def run_tool_async(tool: FlowTool, input_dict: dict[str, ToolInputData], console: Console) -> ToolOutputData`
Run a tool asynchronously.

#### `def list_documents(store_type: str | None, limit: int | None) -> None`
List all documents in the knowledge base.

#### `def show_document(store_type: str, document_id: str, raw: bool) -> None`
Show details of a specific document.

#### `def show_paths() -> None`
Show file system paths for document stores.

#### `def show_stats() -> None`
Show statistics about the document store and vector database.

#### `def show_document_chunks(store_type: str, document_id: str, show_content: bool) -> None`
Show chunk information for a specific document.

#### `def manage_sidecar_files(action: str, show_paths: bool) -> None`
Manage .emb.gz sidecar embedding files.

#### `def embed_documents(store_type: str | None, force: bool, dry_run: bool, use_chunks: bool) -> None`
Embed documents into the vector store for RAG.

#### `def search_documents(query: str, limit: int, store_type: str | None) -> None`
Search documents using semantic similarity.

#### `def search_chunks_by_type(chunk_types: str, question: str | None, max_results: int, store_type: str | None) -> None`
Search for chunks of specific types, optionally with semantic similarity.

#### `def show_chunk_summary(store_type: str, document_id: str, show_previews: bool) -> None`
Get a detailed summary of all chunks for a specific document.

#### `def ask_question(question: str, max_results: int, store_type: str | None, threshold: float, show_sources: bool, chunk_types: str | None, prioritize_chunks: bool) -> None`
Ask a question and get an AI-powered answer using RAG.

#### `def summarize_knowledge_base(store_type: str | None, max_docs: int) -> None`
Generate an AI summary of the knowledge base contents.

#### `def get_document_insights(store_type: str, document_id: str) -> None`
Get AI-generated insights about a specific document.

#### `def get_available_flows() -> dict[str, FlowType]`
Get a registry of available flows.

#### `def list_flows() -> None`
List all available flows.

#### `def exec_flow(flow_name: Annotated[str, typer.Argument(help='Name of the flow to execute')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: auto, json, text')]) -> None`
Execute a flow with input data.

#### `async def run_flow_async(flow: FlowType, input_dict: InputData, console: Console) -> StreamData`
Run a flow asynchronously.

#### `def describe_flow(flow_name: Annotated[str, typer.Argument(help='Name of the flow to describe')]) -> None`
Show detailed information about a flow.

#### `def index_codebase(codebase_name: str | None, force: bool) -> None`
Index a codebase for introspection queries.

    Mechanically, this:
    1. Extracts documents from Python files using AST parsing
    2. Processes README.md and README.bg.md files
    3. Chunks content based on document types
    4. Generates embeddings and stores in vector database
    5. Updates indexing statistics

#### `def query_codebase(query: str, limit: int, doc_type: str | None, include_source: bool, format_output: str) -> None`
Query the codebase using natural language.

    Mechanical query process:
    1. Parse query intent to determine search strategy
    2. Route to appropriate document types
    3. Perform vector similarity search
    4. Rank results by relevance
    5. Display formatted results

#### `def rag_query(query: str, codebase_weight: float, max_results: int, include_codebase: bool, include_documents: bool) -> None`
Query using combined codebase introspection and document RAG.

    Mechanical RAG process:
    1. Execute parallel searches in codebase and document store
    2. Combine results with weighted scoring
    3. Synthesize comprehensive answer using LLM
    4. Display unified response with source attribution

#### `def codebase_overview(codebase_name: str) -> None`
Get comprehensive overview of a codebase.

#### `def compare_codebases(query: str, codebases: str) -> None`
Compare implementations across different codebases.

#### `def add_codebase(name: str, path: str, display_name: str | None, description: str, index_now: bool) -> None`
Add an external codebase for comparison and analysis.

#### `def list_codebases() -> None`
List all available codebases.

#### `def token_analysis(days: int, show_breakdown: bool, export_path: str | None) -> None`
Analyze token usage and costs for embedding operations.

#### `def budget_management(daily_limit: int | None, monthly_limit: int | None, warning_threshold: float | None, reset_usage: bool) -> None`
Manage token budget and limits.

#### `def get_available_instructor_agents() -> dict[str, Any]`
Get available Instructor-powered agents.

#### `def list_instructor_agents() -> None`
List all available Instructor-powered agents.

#### `def run_instructor_agent(agent_name: Annotated[str, typer.Argument(help='Name of the Instructor agent to run')], text: Annotated[str | None, typer.Option('--text', help='Input text to analyze')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: json, rich')]) -> None`
Run an Instructor agent with structured output.

#### `def demo_instructor_agent(agent_name: Annotated[str | None, typer.Argument(help="Agent to demo (or 'all' for all agents)")]) -> None`
Run demonstration of Instructor agents with example inputs.

#### `async def run_instructor_agent_async(agent: Any, message: str, console: Console) -> FlowIOSchema`
Run an instructor agent asynchronously.

#### `def display_structured_result(console: Console, result: FlowIOSchema, agent_type: str) -> None`
Display structured result in a nice format.

#### `def get_available_agents() -> AgentRegistry`
Get a registry of available agents.

#### `def get_agent_metadata(agent_name: str, agent: FlowAgent) -> AgentMetadata`
Get metadata for an agent.

#### `def get_agent_description(agent_name: str) -> str`
Get a human-readable description for an agent.

#### `def list_agents() -> None`
List all available agents and their configurations.

#### `def describe_agent(agent_name: Annotated[str, typer.Argument(help='Name of the agent to describe')]) -> None`
Show detailed information about a specific agent.

#### `def run_agent(agent_name: Annotated[str, typer.Argument(help='Name of the agent to run')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: text, json')], message: Annotated[str | None, typer.Option('--message', help='Message to send (for message-based agents)')]) -> None`
Run a specific agent with input data.

#### `def test_agent(agent_name: Annotated[str, typer.Argument(help='Name of the agent to test')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data (uses default if not provided)')]) -> None`
Test an agent with sample input to verify it's working correctly.

#### `async def run_agent_async(agent: FlowAgent, input_dict: dict[str, Any], console: Console) -> AgentOutput`
Run an agent asynchronously.

#### `def initialize_system(sample_data: bool, embed: bool) -> None`
Initialize the Goldentooth Agent system with sample data.

#### `def show_system_status() -> None`
Show overall system status and configuration.

#### `async def process_rag_input(rag_agent: SimpleRAGAgent, question: str, conversation_history: list[dict[str, str]]) -> dict[str, Any]`
Process input through a RAG agent.

    Returns:
        Dictionary with keys: 'response', 'sources', 'confidence', 'suggestions', 'metadata'

#### `async def process_agent_input(agent: FlowAgent, input_data: AgentInput) -> AgentOutput`
Process input through a FlowAgent using the correct Flow pattern.

#### `def create_rag_agent() -> SimpleRAGAgent`
Create a simplified RAG agent for document-based conversations.

#### `def create_echo_agent() -> FlowAgent`
Create a simple echo agent for demonstration.

#### `def chat(agent: Annotated[str | None, typer.Option('--agent', '-a', help='Agent to chat with')], session: Annotated[str | None, typer.Option('--session', '-s', help='Session ID for context persistence')], stream: Annotated[bool, typer.Option('--stream', help='Enable streaming responses')], model: Annotated[str | None, typer.Option('--model', '-m', help='Model to use for responses')]) -> None`
Start an interactive chat session with the Goldentooth Agent.

    This command creates a conversational interface where users can interact
    with AI agents using the Flow-Context-Agent architecture.

#### `async def chat_loop(console: Console, agent_name: str | None, session_id: str | None, stream_enabled: bool, model_name: str | None) -> None`
Main chat interaction loop.

#### `def send(message: Annotated[str | None, typer.Argument(help='Message to send to the agent')], agent: Annotated[str | None, typer.Option('--agent', '-a', help='Agent to use')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: text, json')]) -> None`
Send a single message to an agent (UNIX pipe friendly).

    This command is designed for use in UNIX pipelines and scripts.

#### `async def process_single_message(message: str, agent_name: str | None, console: Console) -> AgentOutput`
Process a single message through an agent.

#### `def inspect_context(key: Annotated[str | None, typer.Option('--key', '-k', help='Specific key to inspect')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: rich, json, tree')], show_history: Annotated[bool, typer.Option('--history', help='Show context history')], show_computed: Annotated[bool, typer.Option('--computed', help='Show computed properties')]) -> None`
Inspect context state and structure.

#### `def set_context_value(key: Annotated[str, typer.Argument(help='Context key to set')], value: Annotated[str, typer.Argument(help='Value to set (JSON string or plain text)')], type_hint: Annotated[str | None, typer.Option('--type', help='Value type: str, int, float, bool, json')]) -> None`
Set a value in the context.

#### `def export_context(format: Annotated[str, typer.Option('--format', '-f', help='Export format: json, yaml')], output: Annotated[str | None, typer.Option('--output', '-o', help='Output file (default: stdout)')]) -> None`
Export context to file or stdout.

#### `def create_demo_context() -> Context`
Create a demo context with sample data.

#### `def show_key_details(console: Console, key: str, value: ContextValue, format: str) -> None`
Show details for a specific context key.

#### `def show_context_overview(console: Console, context: Context, format: str, show_history: bool, show_computed: bool) -> None`
Show overview of entire context.

#### `def export_context_as_json(context: Context) -> str`
Export context as JSON string.

#### `def parse_value(value_str: str, type_hint: str | None) -> ParsedValue`
Parse a value string based on type hint.

#### `def list_context_keys() -> None`
List all available context keys.

#### `def system_health(component: Annotated[str | None, typer.Option('--component', help='Specific component to check: flows, tools, agents, all')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: rich, json')], export: Annotated[str | None, typer.Option('--export', help='Export health report to file')]) -> None`
Check system health and component status.

#### `def trace_execution(flow: Annotated[str | None, typer.Option('--flow', help='Flow name to trace')], agent: Annotated[str | None, typer.Option('--agent', help='Agent name to trace')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data')], verbose: Annotated[bool, typer.Option('--verbose', help='Enable verbose output')]) -> None`
Trace flow or agent execution for debugging.

#### `def profile_performance(command: Annotated[str, typer.Argument(help="Command to profile (e.g., 'agents run echo')")], iterations: Annotated[int, typer.Option('--iterations', '-n', help='Number of iterations')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data')]) -> None`
Profile command performance and resource usage.

#### `def run_health_checks(component: str | None, console: Console) -> HealthStatus`
Run comprehensive health checks.

#### `def check_tools_health() -> dict[str, Any]`
Check tools component health.

#### `def check_flows_health() -> dict[str, Any]`
Check flows component health.

#### `def check_agents_health() -> dict[str, Any]`
Check agents component health.

#### `def display_health_results(console: Console, health_data: HealthStatus) -> None`
Display health check results in rich format.

#### `async def run_trace_execution(flow: str | None, agent: str | None, input_data: str, verbose: bool, console: Console) -> dict[str, Any]`
Run execution tracing.

#### `def display_trace_results(console: Console, trace_data: dict[str, Any], verbose: bool) -> None`
Display trace execution results.

#### `def run_performance_profiling(command_type: str, subcommand: str, target: str | None, iterations: int, input_data: str | None, console: Console) -> dict[str, Any]`
Run performance profiling.

#### `def display_profile_results(console: Console, profile_data: dict[str, Any]) -> None`
Display performance profiling results.

#### `def create_sample_pipelines() -> dict[str, Pipeline]`
Create sample pipeline configurations.

#### `def list_pipelines() -> None`
List all available pipeline configurations.

#### `def describe_pipeline(pipeline_name: Annotated[str, typer.Argument(help='Name of the pipeline to describe')]) -> None`
Show detailed information about a specific pipeline.

#### `def run_pipeline(pipeline_name: Annotated[str, typer.Argument(help='Name of the pipeline to run')], input_data: Annotated[str | None, typer.Option('--input', help='JSON input data')], format: Annotated[str, typer.Option('--format', '-f', help='Output format: summary, json, full')]) -> None`
Execute a pipeline with input data.

#### `def create_pipeline(name: Annotated[str, typer.Argument(help='Name for the new pipeline')], config_file: Annotated[str | None, typer.Option('--config', help='JSON config file path')]) -> None`
Create a new pipeline from configuration.

#### `def update_module_metadata(module_path: Annotated[str, typer.Argument(help='Path to the module directory to update')], force: Annotated[bool, typer.Option('--force', '-f', help='Force update even if no changes detected')], dry_run: Annotated[bool, typer.Option('--dry-run', '-n', help='Show what would be updated without making changes')]) -> None`
Update README.meta.yaml for a specific module.

#### `def update_all_modules(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')], force: Annotated[bool, typer.Option('--force', '-f', help='Force update even if no changes detected')], dry_run: Annotated[bool, typer.Option('--dry-run', '-n', help='Show what would be updated without making changes')]) -> None`
Update README.meta.yaml for all modules in the project.

#### `def update_changed_modules(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')], since_commit: Annotated[str, typer.Option('--since', '-s', help='Compare against this commit (default: HEAD)')], force: Annotated[bool, typer.Option('--force', '-f', help='Force update even if no changes detected')], dry_run: Annotated[bool, typer.Option('--dry-run', '-n', help='Show what would be updated without making changes')]) -> None`
Update README.meta.yaml for modules that have changed since the specified commit.

#### `def pre_commit_update(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')]) -> None`
Update metadata for modules with staged changes (optimized for pre-commit).

#### `def validate_for_commit(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')]) -> None`
Validate metadata for modules that will be committed.

#### `def check_metadata_freshness(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')], staged_only: Annotated[bool, typer.Option('--staged-only', '-s', help='Only check modules with staged changes')]) -> None`
Check that README.meta.yaml files are newer than their Python files.

#### `def check_freshness_for_commit(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')]) -> None`
Check metadata freshness for modules that will be committed (pre-commit hook).

#### `def commit_message_info(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')]) -> None`
Generate commit message information about metadata changes.

#### `def validate_metadata(module_path: Annotated[str | None, typer.Argument(help='Path to module to validate (or all if not specified)')], project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory')]) -> None`
Validate README.meta.yaml files against actual module content.

#### `def generate_readme(module_path: Annotated[str | None, typer.Argument(help='Path to the module directory (optional - generates all if not provided)')], project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current, used when generating all)')]) -> None`
Generate README.md from README.meta.yaml for a specific module or all modules.

#### `def generate_readme_for_commit(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')]) -> None`
Generate README.md files for modules with staged changes (pre-commit hook).

#### `def check_readme_freshness(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')], staged_only: Annotated[bool, typer.Option('--staged-only', '-s', help='Only check modules with staged changes')]) -> None`
Check that README.md files are newer than their README.meta.yaml files.

#### `def check_readme_freshness_for_commit(project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current)')]) -> None`
Check README freshness for modules that will be committed (pre-commit hook).

#### `def check_background_files(project_root: Annotated[str, typer.Option('--project-root', '-p', help='Project root directory (defaults to current directory)')]) -> None`
Check for missing README.bg.md files in modules.

#### `def check_background_files_for_commit(project_root: Annotated[str, typer.Option('--project-root', '-p', help='Project root directory (defaults to current directory)')]) -> None`
Check for missing README.bg.md files in modules with staged changes (pre-commit hook).

#### `def generate_background_file(module_path: Annotated[str | None, typer.Argument(help='Path to the module directory (optional - generates for all modules if not provided)')], project_root: Annotated[str | None, typer.Option('--root', '-r', help='Project root directory (defaults to current, used when generating all)')], force: Annotated[bool, typer.Option('--force', '-f', help='Overwrite existing README.bg.md files')], ai_powered: Annotated[bool, typer.Option('--ai', help='Use AI to analyze modules and generate comprehensive backgrounds')], template_only: Annotated[bool, typer.Option('--template-only', help='Generate templates without AI analysis')]) -> None`
Generate README.bg.md files for a specific module or all modules with optional AI assistance.

#### `def sync_organization(org_name: str, repos: bool, embed: bool) -> None`
Sync a GitHub organization and its repositories.

#### `def sync_user_repos(username: str | None, max_repos: int | None, embed: bool) -> None`
Sync repositories for a user (or authenticated user).

#### `def list_user_organizations() -> None`
List organizations for the authenticated user.

#### `def show_rate_limit() -> None`
Show GitHub API rate limit status.

#### `def show_github_status() -> None`
Show status of synced GitHub data.

#### `def demo_flows(scenario: Annotated[str | None, typer.Option('--scenario', help='Specific scenario: stream_processing, error_handling, composition')], interactive: Annotated[bool, typer.Option('--interactive/--no-interactive', help='Enable interactive mode')]) -> None`
Interactive demonstration of the flow system.

#### `def demo_context(scenario: Annotated[str | None, typer.Option('--scenario', help='Specific scenario: time_travel, computed_properties, queries')], interactive: Annotated[bool, typer.Option('--interactive/--no-interactive', help='Enable interactive mode')]) -> None`
Interactive demonstration of the context system.

#### `def demo_agents(scenario: Annotated[str | None, typer.Option('--scenario', help='Specific scenario: creation, collaboration, pipelines')], interactive: Annotated[bool, typer.Option('--interactive/--no-interactive', help='Enable interactive mode')]) -> None`
Interactive demonstration of the agent system.

#### `def run_interactive_flow_tutorial(console: Console, interactive: bool) -> None`
Run the interactive flow tutorial.

#### `def run_flow_scenario(console: Console, scenario: str, interactive: bool) -> None`
Run a specific flow scenario.

#### `def demo_stream_processing(console: Console, interactive: bool) -> None`
Demonstrate stream processing capabilities.

#### `async def demo_live_stream_processing(console: Console) -> None`
Demonstrate live stream processing.

#### `def demo_error_handling(console: Console, interactive: bool) -> None`
Demonstrate error handling in flows.

#### `async def demo_live_error_handling(console: Console) -> None`
Demonstrate live error handling.

#### `def demo_flow_composition(console: Console, interactive: bool) -> None`
Demonstrate flow composition.

#### `async def demo_live_composition(console: Console) -> None`
Demonstrate live flow composition.

#### `def run_interactive_context_tutorial(console: Console, interactive: bool) -> None`
Run the interactive context tutorial.

#### `def demo_basic_context_operations(console: Console, interactive: bool) -> None`
Demonstrate basic context operations.

#### `def run_context_scenario(console: Console, scenario: str, interactive: bool) -> None`
Run a specific context scenario.

#### `def run_interactive_agent_tutorial(console: Console, interactive: bool) -> None`
Run the interactive agent tutorial.

#### `def demo_agent_basics(console: Console, interactive: bool) -> None`
Demonstrate basic agent operations.

#### `async def demo_agent_interaction(console: Console) -> None`
Demonstrate agent interaction.

#### `def run_agent_scenario(console: Console, scenario: str, interactive: bool) -> None`
Run a specific agent scenario.

#### `def setup_git_repository(repo_path: str, remote_url: str | None) -> None`
Set up a Git repository for knowledge base data.

#### `def sync_to_git(repo_path: str, message: str | None, push: bool) -> None`
Sync knowledge base data to Git repository.

#### `def show_git_status(repo_path: str) -> None`
Show Git repository status.

#### `def auto_sync_after_github_sync(repo_path: str, org_name: str | None, push: bool) -> None`
Sync GitHub data and automatically commit to Git repository.

## Dependencies

### Internal Dependencies
- `goldentooth_agent.cli.commands.agents`
- `goldentooth_agent.cli.commands.chat`
- `goldentooth_agent.cli.commands.flow`
- `goldentooth_agent.cli.commands.tools`
- `goldentooth_agent.core.agent_codebase`
- `goldentooth_agent.core.agent_codebase.rag_integration`
- `goldentooth_agent.core.context`
- `goldentooth_agent.core.dev.metadata_generator`
- `goldentooth_agent.core.flow_agent`
- `goldentooth_agent.core.llm`
- `goldentooth_agent.core.tools`

### External Dependencies
- `__future__`
- `antidote`
- `asyncio`
- `collections`
- `core`
- `goldentooth_agent`
- `json`
- `math`
- `pathlib`
- `rich`
- `sys`
- `time`
- `typer`
- `typing`
- `yaml`

## Exports

This module exports the following symbols:

- `agents`
- `chat`
- `codebase`
- `context`
- `debug`
- `demo`
- `dev`
- `docs`
- `flow`
- `git_sync`
- `github`
- `instructor`
- `pipeline`
- `setup`
- `tools`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
