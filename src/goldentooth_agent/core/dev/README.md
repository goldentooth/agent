# Dev

Dev module

## Overview

- **Complexity**: Medium
- **Files**: 2 Python files
- **Lines of Code**: ~1244
- **Classes**: 5
- **Functions**: 42

## API Reference

### Classes

#### MetadataUpdateResult
Result of a metadata update operation.

#### MethodInfo
Information about a class method.

#### SymbolInfo
Information about a symbol (class, function, constant).

#### ModuleAnalysis
Analysis result for a Python module.

#### ModuleMetadataGenerator
Generates and maintains README.meta.yaml files for Python modules.

**Public Methods:**
- `update_module_metadata(self, module_path: Path, force: bool, dry_run: bool) -> MetadataUpdateResult` - Update README.meta.yaml for a single module
- `update_all_modules(self, project_root: Path, force: bool, dry_run: bool) -> list[MetadataUpdateResult]` - Update README.meta.yaml for all modules in the project
- `validate_module_metadata(self, module_path: Path) -> list[str]` - Validate README.meta.yaml against actual module content
- `validate_all_metadata(self, project_root: Path) -> dict[Path, list[str]]` - Validate all README.meta.yaml files in the project
- `update_changed_modules(self, project_root: Path, since_commit: str, force: bool, dry_run: bool) -> list[MetadataUpdateResult]` - Update README.meta.yaml for modules that have changed since the specified commit
- `update_for_pre_commit(self, project_root: Path) -> list[MetadataUpdateResult]` - Update metadata for modules with staged changes (optimized for pre-commit)
- `validate_for_commit(self, project_root: Path) -> list[str]` - Validate metadata for modules that will be committed
- `check_metadata_freshness(self, project_root: Path) -> list[str]` - Check that README.meta.yaml files are newer than their corresponding Python files
- `check_staged_metadata_freshness(self, project_root: Path) -> list[str]` - Check metadata freshness only for modules with staged changes
- `generate_commit_message_info(self, project_root: Path) -> str | None` - Generate information about metadata changes for commit messages
- `generate_readme_from_metadata(self, module_path: Path) -> str` - Generate README.md content from README.meta.yaml
- `write_readme_from_metadata(self, module_path: Path) -> bool` - Generate and write README.md from README.meta.yaml
- `update_all_readmes(self, project_root: Path) -> list[Path]` - Generate README.md files for all modules that have metadata
- `check_readme_freshness(self, project_root: Path) -> list[str]` - Check that README.md files are newer than their corresponding README.meta.yaml files
- `check_staged_readme_freshness(self, project_root: Path) -> list[str]` - Check README freshness only for modules with staged changes

## Dependencies

### External Dependencies
- `antidote`
- `ast`
- `dataclasses`
- `metadata_generator`
- `pathlib`
- `subprocess`
- `typing`
- `yaml`

## Exports

This module exports the following symbols:

- `MetadataUpdateResult`
- `ModuleMetadataGenerator`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
