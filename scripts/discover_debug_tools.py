#!/usr/bin/env python3
"""Discover and document available debugging tools in the codebase.

This script automatically scans the codebase for debugging capabilities and generates
comprehensive documentation about available tools and their usage patterns.
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def find_project_root() -> Path:
    """Find the project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root with pyproject.toml")


def scan_cli_commands(project_root: Path) -> dict[str, Any]:
    """Scan for CLI debug commands."""
    cli_debug_file = (
        project_root / "src" / "goldentooth_agent" / "cli" / "commands" / "debug.py"
    )

    if not cli_debug_file.exists():
        return {}

    commands = {}
    try:
        with open(cli_debug_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for @app.command decorators
                for decorator in node.decorator_list:
                    if (
                        isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Attribute)
                        and decorator.func.attr == "command"
                    ):

                        command_name = None
                        if decorator.args:
                            if isinstance(decorator.args[0], ast.Constant):
                                command_name = decorator.args[0].value

                        if command_name:
                            # Extract docstring
                            docstring = ast.get_docstring(node)
                            commands[command_name] = {
                                "function_name": node.name,
                                "description": docstring or "No description available",
                                "location": f"cli/commands/debug.py:{node.lineno}",
                            }
    except Exception as e:
        print(f"Error scanning CLI commands: {e}")

    return commands


def scan_flow_observability_tools(project_root: Path) -> dict[str, Any]:
    """Scan flow engine observability tools."""
    observability_dir = (
        project_root / "src" / "goldentooth_agent" / "flow_engine" / "observability"
    )

    if not observability_dir.exists():
        return {}

    tools = {}

    for py_file in observability_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        module_name = py_file.stem
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    classes.append(
                        {
                            "name": node.name,
                            "description": docstring or "No description available",
                            "line": node.lineno,
                        }
                    )
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):
                    docstring = ast.get_docstring(node)
                    functions.append(
                        {
                            "name": node.name,
                            "description": docstring or "No description available",
                            "line": node.lineno,
                        }
                    )

            if classes or functions:
                tools[module_name] = {
                    "file": f"flow_engine/observability/{py_file.name}",
                    "classes": classes,
                    "functions": functions,
                }
        except Exception as e:
            print(f"Error scanning {py_file}: {e}")

    return tools


def scan_observability_combinators(project_root: Path) -> dict[str, Any]:
    """Scan observability combinators."""
    combinators_file = (
        project_root
        / "src"
        / "goldentooth_agent"
        / "flow_engine"
        / "combinators"
        / "observability.py"
    )

    if not combinators_file.exists():
        return {}

    combinators = {}
    try:
        with open(combinators_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                docstring = ast.get_docstring(node)
                combinators[node.name] = {
                    "description": docstring or "No description available",
                    "location": f"flow_engine/combinators/observability.py:{node.lineno}",
                }
    except Exception as e:
        print(f"Error scanning observability combinators: {e}")

    return combinators


def scan_error_reporting_tools(project_root: Path) -> dict[str, Any]:
    """Scan error reporting and enhancement tools."""
    error_reporting_file = (
        project_root
        / "src"
        / "goldentooth_agent"
        / "core"
        / "util"
        / "error_reporting.py"
    )

    if not error_reporting_file.exists():
        return {}

    tools = {}
    try:
        with open(error_reporting_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                tools[node.name] = {
                    "type": "class",
                    "description": docstring or "No description available",
                    "location": f"core/util/error_reporting.py:{node.lineno}",
                }
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                docstring = ast.get_docstring(node)
                tools[node.name] = {
                    "type": "function",
                    "description": docstring or "No description available",
                    "location": f"core/util/error_reporting.py:{node.lineno}",
                }
    except Exception as e:
        print(f"Error scanning error reporting tools: {e}")

    return tools


def scan_dev_debugging_tools(project_root: Path) -> dict[str, Any]:
    """Scan development debugging utilities."""
    dev_debugging_file = (
        project_root / "src" / "goldentooth_agent" / "dev" / "debugging.py"
    )

    if not dev_debugging_file.exists():
        return {}

    tools = {}
    try:
        with open(dev_debugging_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                tools[node.name] = {
                    "type": "class",
                    "description": docstring or "No description available",
                    "location": f"dev/debugging.py:{node.lineno}",
                }
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                docstring = ast.get_docstring(node)
                tools[node.name] = {
                    "type": "function",
                    "description": docstring or "No description available",
                    "location": f"dev/debugging.py:{node.lineno}",
                }
    except Exception as e:
        print(f"Error scanning dev debugging tools: {e}")

    return tools


def scan_analysis_scripts(project_root: Path) -> dict[str, Any]:
    """Scan analysis and debugging scripts."""
    scripts_dir = project_root / "scripts"

    if not scripts_dir.exists():
        return {}

    scripts = {}
    for script_file in scripts_dir.glob("*.py"):
        if script_file.name == "__init__.py":
            continue

        try:
            with open(script_file) as f:
                content = f.read()
                tree = ast.parse(content)

            # Get module docstring
            docstring = ast.get_docstring(tree)

            # Look for main function or script purpose
            purpose = docstring or "Analysis/debugging script"

            scripts[script_file.name] = {
                "description": purpose,
                "location": f"scripts/{script_file.name}",
                "executable": True,
            }
        except Exception as e:
            print(f"Error scanning script {script_file}: {e}")

    return scripts


def generate_problem_to_tool_mapping(all_tools: dict[str, Any]) -> dict[str, list[str]]:
    """Generate mapping from problem types to relevant tools."""
    mapping = defaultdict(list)

    # CLI tools
    cli_commands = all_tools.get("cli_commands", {})
    if "health" in cli_commands:
        mapping["system_issues"].append("CLI: goldentooth-agent debug health")
        mapping["configuration_problems"].append("CLI: goldentooth-agent debug health")
    if "trace" in cli_commands:
        mapping["execution_problems"].append("CLI: goldentooth-agent debug trace")
        mapping["agent_issues"].append(
            "CLI: goldentooth-agent debug trace --agent [type]"
        )
        mapping["flow_issues"].append(
            "CLI: goldentooth-agent debug trace --flow [name]"
        )
    if "profile" in cli_commands:
        mapping["performance_issues"].append("CLI: goldentooth-agent debug profile")
        mapping["slow_operations"].append("CLI: goldentooth-agent debug profile")

    # Flow observability tools
    flow_tools = all_tools.get("flow_observability", {})
    if "debugging" in flow_tools:
        mapping["execution_problems"].append(
            "Code: FlowDebugger for interactive debugging"
        )
        mapping["flow_issues"].append("Code: FlowDebugger with breakpoints")
    if "performance" in flow_tools:
        mapping["performance_issues"].append(
            "Code: PerformanceMonitor for detailed analysis"
        )
        mapping["slow_operations"].append("Code: PerformanceMonitor with metrics")
    if "health" in flow_tools:
        mapping["system_issues"].append("Code: HealthCheck for component validation")

    # Observability combinators
    combinators = all_tools.get("observability_combinators", {})
    for combinator_name in combinators:
        if "log" in combinator_name:
            mapping["debugging_output"].append(f"Code: {combinator_name}() combinator")
        elif "trace" in combinator_name:
            mapping["execution_problems"].append(
                f"Code: {combinator_name}() combinator"
            )
        elif "monitor" in combinator_name or "metrics" in combinator_name:
            mapping["performance_issues"].append(
                f"Code: {combinator_name}() combinator"
            )
        elif "inspect" in combinator_name:
            mapping["object_inspection"].append(f"Code: {combinator_name}() combinator")

    # Error reporting tools
    error_tools = all_tools.get("error_reporting", {})
    if "DetailedAttributeError" in error_tools:
        mapping["attribute_errors"].append(
            "Auto: DetailedAttributeError with debugging hints"
        )
        mapping["dict_vs_object_issues"].append("Auto: DetailedAttributeError analysis")

    # Development tools
    dev_tools = all_tools.get("dev_debugging", {})
    if "DebugContext" in dev_tools:
        mapping["operation_tracking"].append(
            "Code: DebugContext for operation monitoring"
        )

    return dict(mapping)


def generate_tool_reference(all_tools: dict[str, Any]) -> str:
    """Generate comprehensive tool reference documentation."""

    reference = """# Debugging Tools Reference

This document provides a comprehensive reference for all debugging tools available in the Goldentooth Agent system.

## 🔧 Command Line Interface (CLI) Tools

"""

    # CLI Commands
    cli_commands = all_tools.get("cli_commands", {})
    if cli_commands:
        for cmd_name, cmd_info in cli_commands.items():
            reference += f"### `goldentooth-agent debug {cmd_name}`\n\n"
            reference += (
                f"**Description**: {cmd_info['description'].split('.')[0]}.\n\n"
            )
            reference += f"**Location**: `{cmd_info['location']}`\n\n"

    reference += "\n## 🧩 Flow Engine Observability Tools\n\n"

    # Flow observability tools
    flow_tools = all_tools.get("flow_observability", {})
    for module_name, module_info in flow_tools.items():
        reference += f"### {module_name.title()} Module\n\n"
        reference += f"**File**: `{module_info['file']}`\n\n"

        if module_info.get("classes"):
            reference += "**Classes**:\n"
            for cls in module_info["classes"]:
                reference += f"- `{cls['name']}`: {cls['description'].split('.')[0]}\n"

        if module_info.get("functions"):
            reference += "\n**Functions**:\n"
            for func in module_info["functions"]:
                reference += (
                    f"- `{func['name']}()`: {func['description'].split('.')[0]}\n"
                )

        reference += "\n"

    reference += "\n## 🔍 Observability Combinators\n\n"

    # Observability combinators
    combinators = all_tools.get("observability_combinators", {})
    if combinators:
        reference += "**File**: `flow_engine/combinators/observability.py`\n\n"
        for combinator_name, combinator_info in combinators.items():
            reference += f"- `{combinator_name}()`: {combinator_info['description'].split('.')[0]}\n"

    reference += "\n## 🚨 Error Reporting & Enhancement\n\n"

    # Error reporting tools
    error_tools = all_tools.get("error_reporting", {})
    if error_tools:
        reference += "**File**: `core/util/error_reporting.py`\n\n"
        for tool_name, tool_info in error_tools.items():
            reference += f"- `{tool_name}` ({tool_info['type']}): {tool_info['description'].split('.')[0]}\n"

    reference += "\n## 🛠️ Development Utilities\n\n"

    # Development debugging tools
    dev_tools = all_tools.get("dev_debugging", {})
    if dev_tools:
        reference += "**File**: `dev/debugging.py`\n\n"
        for tool_name, tool_info in dev_tools.items():
            reference += f"- `{tool_name}` ({tool_info['type']}): {tool_info['description'].split('.')[0]}\n"

    reference += "\n## 📊 Analysis Scripts\n\n"

    # Analysis scripts
    scripts = all_tools.get("analysis_scripts", {})
    if scripts:
        for script_name, script_info in scripts.items():
            reference += f"### `{script_name}`\n\n"
            reference += (
                f"**Description**: {script_info['description'].split('.')[0]}\n\n"
            )
            reference += f"**Usage**: `poetry run python scripts/{script_name}`\n\n"

    return reference


def generate_quick_reference_card(all_tools: dict[str, Any]) -> str:
    """Generate a quick reference card for common debugging scenarios."""

    problem_mapping = generate_problem_to_tool_mapping(all_tools)

    card = """# Quick Debugging Reference Card

## 🚨 Common Problems → Tools

"""

    problem_descriptions = {
        "system_issues": "🏥 **System Health Problems**",
        "execution_problems": "🔍 **Execution/Runtime Issues**",
        "performance_issues": "⚡ **Performance Problems**",
        "agent_issues": "🤖 **Agent-Specific Issues**",
        "flow_issues": "🌊 **Flow Execution Issues**",
        "attribute_errors": "📝 **Attribute Access Errors**",
        "configuration_problems": "⚙️ **Configuration Issues**",
    }

    for problem_type, description in problem_descriptions.items():
        if problem_type in problem_mapping:
            card += f"{description}\n"
            for tool in problem_mapping[problem_type]:
                card += f"- {tool}\n"
            card += "\n"

    card += """## 🎯 Quick Debugging Workflow

1. **System Check**: `goldentooth-agent debug health`
2. **Trace Issue**: `goldentooth-agent debug trace --verbose`
3. **Profile Performance**: `goldentooth-agent debug profile [command]`
4. **Deep Analysis**: Use FlowDebugger, PerformanceMonitor
5. **Follow Error Hints**: Enhanced error messages guide next steps

## 📚 Complete References

- [Debugging Guide](guidelines/debugging-guide.md) - Comprehensive debugging documentation
- [Tool Reference](#debugging-tools-reference) - Complete tool catalog
- [CLI Help](README.md#debugging--development) - Command examples

"""

    return card


def main():
    """Discover debugging tools and generate documentation."""
    try:
        project_root = find_project_root()
        print(f"Scanning project: {project_root}")

        # Discover all tools
        all_tools = {
            "cli_commands": scan_cli_commands(project_root),
            "flow_observability": scan_flow_observability_tools(project_root),
            "observability_combinators": scan_observability_combinators(project_root),
            "error_reporting": scan_error_reporting_tools(project_root),
            "dev_debugging": scan_dev_debugging_tools(project_root),
            "analysis_scripts": scan_analysis_scripts(project_root),
        }

        # Generate documentation
        tool_reference = generate_tool_reference(all_tools)
        quick_reference = generate_quick_reference_card(all_tools)

        # Write outputs
        output_dir = project_root / ".discover_debugging_tools"
        output_dir.mkdir(exist_ok=True)

        # Write tool reference
        with open(output_dir / "debugging_tools_reference.md", "w") as f:
            f.write(tool_reference)

        # Write quick reference
        with open(output_dir / "quick_debugging_reference.md", "w") as f:
            f.write(quick_reference)

        # Write raw data as JSON
        with open(output_dir / "debugging_tools_data.json", "w") as f:
            json.dump(all_tools, f, indent=2)

        print("\n✅ Discovery complete!")
        print(f"📊 Found {len(all_tools['cli_commands'])} CLI commands")
        print(f"🧩 Found {len(all_tools['flow_observability'])} observability modules")
        print(
            f"🔍 Found {len(all_tools['observability_combinators'])} observability combinators"
        )
        print(f"🚨 Found {len(all_tools['error_reporting'])} error reporting tools")
        print(f"🛠️ Found {len(all_tools['dev_debugging'])} development debugging tools")
        print(f"📊 Found {len(all_tools['analysis_scripts'])} analysis scripts")

        print("\n📝 Documentation generated:")
        print(f"  - {output_dir / 'debugging_tools_reference.md'}")
        print(f"  - {output_dir / 'quick_debugging_reference.md'}")
        print(f"  - {output_dir / 'debugging_tools_data.json'}")

        # Show sample from quick reference
        print("\n🎯 Quick Reference Preview:")
        print("=" * 50)
        print(
            quick_reference[:500] + "..."
            if len(quick_reference) > 500
            else quick_reference
        )

    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
