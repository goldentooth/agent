# Scripts

Scripts module

## Overview

- **Complexity**: High
- **Files**: 7 Python files
- **Lines of Code**: ~1098
- **Classes**: 0
- **Functions**: 18

## API Reference

### Functions

#### `def run_command(cmd: list[str]) -> tuple[bool, str]`
Run a command and return success status and output.

#### `def check_module_tests(module_name: str) -> dict[str, any]`
Check if tests pass for a specific module.

#### `def main()`
Check extraction readiness for all major modules.

#### `def create_package_structure(package_name: str) -> Path`
Create the new package directory structure.

#### `def move_module_files(source_module: str, target_package: Path) -> list[Path]`
Move files from core module to new package.

#### `def update_imports_in_file(file_path: Path, old_import: str, new_import: str)`
Update import statements in a Python file.

#### `def update_imports_across_codebase(old_module: str, new_package: str)`
Update all import statements across the codebase.

#### `def create_compatibility_shim(old_module: str, new_package: str)`
Create a compatibility shim in the old location.

#### `def move_tests(source_module: str, target_package: str) -> bool`
Move tests to match the new package structure.

#### `def run_tests_for_package(package_name: str) -> bool`
Run tests to verify the extraction worked.

#### `def extract_module(source_module: str, target_package: str)`
Extract a module into a new package.

#### `def main()`
Extract the flow module as a demonstration.

#### `async def migrate_embeddings()`
Main migration function.

#### `async def verify_migration()`
Verify the migration by testing a few embeddings.

#### `async def populate_vector_store()`
Populate vector store with OpenAI embeddings.

#### `def analyze_module(module_path: Path) -> dict[str, Any]`
Analyze a Python module to extract API surface.

#### `def create_readme_template(module_name: str, analysis: dict[str, Any]) -> str`
Create a standardized README template.

#### `def main()`
Generate README files for all major modules.

#### `def extract_symbols(file_path: Path) -> set[str]`
Extract all defined symbols from a Python file.

#### `def find_python_files(root_dir: Path) -> list[Path]`
Find all Python files in the project.

#### `def main()`
Main function to check for duplicate symbols.

#### `def main() -> int`
Main entry point for the pre-commit hook.

## Dependencies

### Internal Dependencies
- `goldentooth_agent.core.document_store`
- `goldentooth_agent.core.embeddings`
- `goldentooth_agent.core.embeddings.vector_store`
- `goldentooth_agent.core.paths`

### External Dependencies
- `ast`
- `asyncio`
- `collections`
- `datetime`
- `os`
- `pathlib`
- `shutil`
- `subprocess`
- `sys`
- `typing`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
