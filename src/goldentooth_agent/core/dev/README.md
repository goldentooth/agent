# Dev

Dev module

## Overview

- **Complexity**: Medium
- **Files**: 2 Python files
- **Lines of Code**: ~1193
- **Classes**: 4
- **Functions**: 44

## API Reference

### Classes

#### MetadataUpdateResult
Result of a metadata update operation.

#### SymbolInfo
Information about a symbol (class, function, constant).

#### ModuleAnalysis
Analysis result for a Python module.

#### ModuleMetadataGenerator
Generates and maintains README.meta.yaml files for Python modules.

**Public Methods:**
- `update_module_metadata()`
- `update_all_modules()`
- `validate_module_metadata()`
- `validate_all_metadata()`
- `update_changed_modules()`
- `update_for_pre_commit()`
- `validate_for_commit()`
- `check_metadata_freshness()`
- `check_staged_metadata_freshness()`
- `generate_commit_message_info()`
- `generate_readme_from_metadata()`
- `write_readme_from_metadata()`
- `update_all_readmes()`
- `check_readme_freshness()`
- `check_staged_readme_freshness()`

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
