#!/usr/bin/env python3
"""
Generate README.md files for all major modules.
Provides LLM-friendly documentation to improve development efficiency.
"""

import ast
import sys
from pathlib import Path
from typing import Any


def analyze_module(module_path: Path) -> dict[str, Any]:
    """Analyze a Python module to extract API surface."""

    classes = []
    functions = []
    imports = []

    for py_file in module_path.glob("**/*.py"):
        if py_file.name.startswith("test_"):
            continue

        try:
            content = py_file.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(
                        {
                            "name": node.name,
                            "file": str(py_file.relative_to(module_path)),
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                            "docstring": ast.get_docstring(node) or "",
                        }
                    )
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):
                    functions.append(
                        {
                            "name": node.name,
                            "file": str(py_file.relative_to(module_path)),
                            "docstring": ast.get_docstring(node) or "",
                        }
                    )
                elif isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception as e:
            print(f"Error analyzing {py_file}: {e}")

    # Count lines of code
    total_lines = sum(
        len(py_file.read_text().splitlines())
        for py_file in module_path.glob("**/*.py")
        if not py_file.name.startswith("test_")
    )

    return {
        "classes": classes,
        "functions": functions,
        "imports": list(set(imports)),
        "total_lines": total_lines,
        "file_count": len(list(module_path.glob("**/*.py"))),
    }


def create_readme_template(module_name: str, analysis: dict[str, Any]) -> str:
    """Create a standardized README template."""

    complexity_score = (
        "🟢 Low"
        if analysis["total_lines"] < 500
        else "🟡 Medium" if analysis["total_lines"] < 1500 else "🔴 High"
    )

    template = f"""# {module_name.title()} Module

## Overview
**Status**: {complexity_score} Complexity | **Lines of Code**: {analysis["total_lines"]} | **Files**: {analysis["file_count"]}

Brief description of the module's purpose and responsibilities.

## Key Components

### Classes ({len(analysis["classes"])})
"""

    for cls in analysis["classes"][:10]:  # Show top 10 classes
        template += f"""
#### `{cls["name"]}`
- **File**: `{cls["file"]}`
- **Methods**: {len(cls["methods"])} methods
- **Purpose**: {cls["docstring"][:100]}...
"""

    template += f"""
### Functions ({len(analysis["functions"])})
"""

    for func in analysis["functions"][:10]:  # Show top 10 functions
        template += f"""
#### `{func["name"]}`
- **File**: `{func["file"]}`
- **Purpose**: {func["docstring"][:100]}...
"""

    template += f"""
## Public API

### Main Exports
```python
# TODO: Document main exports
from goldentooth_agent.core.{module_name} import (
    # Add main classes and functions here
)
```

### Usage Examples
```python
# TODO: Add usage examples
```

## Dependencies

### Internal Dependencies
```python
# Key internal imports
{chr(10).join(f"# {imp}" for imp in analysis["imports"][:10] if "goldentooth_agent" in imp)}
```

### External Dependencies
```python
# Key external imports
{chr(10).join(f"# {imp}" for imp in analysis["imports"][:10] if "goldentooth_agent" not in imp and not imp.startswith("typing"))}
```

## Testing

### Test Coverage
- **Test files**: Located in `tests/core/{module_name}/`
- **Coverage target**: 85%+
- **Performance**: All tests <1s

### Running Tests
```bash
# Run all tests for this module
poetry run pytest tests/core/{module_name}/

# Run with coverage
poetry run pytest tests/core/{module_name}/ --cov=src/goldentooth_agent/core/{module_name}/
```

## Known Issues

### Technical Debt
- [ ] TODO: Document known issues
- [ ] TODO: Type safety concerns
- [ ] TODO: Performance bottlenecks

### Future Improvements
- [ ] TODO: Planned enhancements
- [ ] TODO: Refactoring needs

## Development Notes

### Architecture Decisions
- TODO: Document key design decisions
- TODO: Explain complex interactions

### Performance Considerations
- TODO: Document performance requirements
- TODO: Known bottlenecks and optimizations

## Related Modules

### Dependencies
- **Depends on**: TODO: List module dependencies
- **Used by**: TODO: List modules that use this one

### Integration Points
- TODO: Document how this module integrates with others
"""

    return template


def main():
    """Generate README files for all major modules."""

    src_path = Path("src/goldentooth_agent/core")

    if not src_path.exists():
        print(f"Source path {src_path} does not exist")
        sys.exit(1)

    modules_to_document = [
        "flow",
        "rag",
        "embeddings",
        "context",
        "flow_agent",
        "llm",
        "document_store",
        "background_loop",
        "util",
        "paths",
    ]

    for module_name in modules_to_document:
        module_path = src_path / module_name

        if not module_path.exists():
            print(f"Module {module_name} does not exist at {module_path}")
            continue

        print(f"Analyzing module: {module_name}")
        analysis = analyze_module(module_path)

        readme_content = create_readme_template(module_name, analysis)
        readme_path = module_path / "README.md"

        if readme_path.exists():
            print(f"README.md already exists for {module_name}, skipping...")
            continue

        readme_path.write_text(readme_content)
        print(f"Created README.md for {module_name}")


if __name__ == "__main__":
    main()
