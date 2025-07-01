# Dead Code Detection Setup

This document describes the dead code detection tools and workflows available in the goldentooth-agent project.

## Available Tools

### 1. Vulture (Primary Tool)
Professional Python dead code detector integrated with pre-commit hooks.

**Commands:**
```bash
# High confidence check (80% threshold)
poetry run poe deadcode

# All potential issues (60% confidence)
poetry run poe deadcode-all

# Smart diff check (only NEW dead code)
poetry run poe deadcode-diff
```

### 2. Custom AST Analysis
Detailed analysis with file grouping and context.

```bash
# Comprehensive analysis with file organization
poetry run poe deadcode-report
```

## Pre-commit Integration

Dead code detection is integrated into pre-commit hooks to catch NEW dead code before it's committed.

### How It Works

1. **Baseline File**: `vulture_baseline.txt` contains known existing dead code
2. **Smart Diff**: Only reports NEW issues, ignoring baseline
3. **High Confidence**: Uses 80% confidence threshold to minimize false positives
4. **Non-blocking**: Existing dead code doesn't block commits

### Pre-commit Hook

The hook runs automatically on `git commit` and:
- ✅ **Passes**: If no new dead code is detected
- ❌ **Fails**: If new dead code is introduced
- ℹ️ **Informs**: About baseline issues that were fixed

## Configuration Files

### `vulture.ini`
Main vulture configuration with:
- Confidence thresholds
- Exclusion patterns for CLI commands, tests, etc.
- File and directory exclusions

### `vulture_baseline.txt`
Allowlist of existing dead code issues:
- 17 known issues (unused variables, unreachable code)
- Prevents regression while allowing cleanup
- Should be updated as issues are fixed

## Workflows

### Daily Development
```bash
# Quick check for obvious dead code
poetry run poe deadcode

# Check if you introduced new dead code
poetry run poe deadcode-diff
```

### Code Review/Cleanup
```bash
# See all potential issues
poetry run poe deadcode-all

# Get detailed analysis with file grouping
poetry run poe deadcode-report
```

### Fixing Dead Code
1. Identify issues with `poetry run poe deadcode`
2. Remove dead code or verify it's actually used
3. For CLI commands: Check if they're used via Typer decorators
4. Update `vulture_baseline.txt` if needed

## Understanding Results

### Confidence Levels
- **100%**: Definitely dead (unused variables, unreachable code)
- **80-99%**: Very likely dead (high confidence)
- **60-79%**: Possibly dead (requires manual review)

### Common False Positives
- **CLI commands**: May appear unused but called via decorators
- **Exception classes**: Imported but not instantiated
- **Protocol/Interface classes**: Used for type checking only
- **Plugin/Extension methods**: Called dynamically

### Priority Order
1. **100% confidence** - Clean up immediately
2. **Variables** over **functions** - Safer to remove
3. **Core modules** over **CLI modules** - More critical
4. **Unused imports** - Safe to remove

## Maintenance

### Updating Baseline
When dead code is fixed, update the baseline:

1. Run `poetry run poe deadcode-diff`
2. Note which baseline issues were fixed
3. Remove those lines from `vulture_baseline.txt`
4. Commit the updated baseline

### Adding Exclusions
To exclude specific patterns, update `vulture.ini`:

```ini
ignore_names = [
    "new_pattern_*",  # Add new exclusion patterns
    "*_my_special_case"
]
```

## Integration with CI/CD

The pre-commit hook ensures:
- No new dead code enters the codebase
- Existing technical debt doesn't block development
- Gradual cleanup of baseline issues over time

For CI/CD pipelines, add:
```bash
poetry run poe deadcode-diff
```

This provides zero-regression dead code detection without blocking deployments.
