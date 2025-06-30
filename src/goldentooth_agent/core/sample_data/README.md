# Sample Data

Sample Data module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~93
- **Classes**: 0
- **Functions**: 1

## API Reference

### Functions

#### `def install_sample_data(paths: Paths) -> dict[str, Any]`
Install sample GitHub data for demonstration.

    Args:
        paths: Paths service for data directory management

    Returns:
        Dictionary with installation results

## Dependencies

### External Dependencies
- `document_store`
- `importlib`
- `installer`
- `paths`
- `schemas`
- `typing`

## Exports

This module exports the following symbols:

- `install_sample_data`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
