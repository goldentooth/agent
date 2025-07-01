# Development Workflow Guidelines

This document establishes the standard development workflow for the Goldentooth Agent project, including quality gates and automated checks that must be run before committing code.

## Guidelines Reference Policy

**IMPORTANT**: When referring to project guidelines in conversations, "the guidelines" should be understood as referring to the guidelines files stored in the `guidelines/` directory and included from `CLAUDE.md`. These comprehensive guidelines cover all aspects of development including code style, testing, architecture, performance, documentation, and more.

## Project Characteristics

### Private Project Policy
This is a private project with a single user. Key implications:
- **No backward compatibility requirements**: We do not need to maintain backward compatibility or legacy code
- **Rapid iteration**: Our only responsibility is to ensure that the code always works on deployment
- **Version-controlled resources**: Any resources (e.g. RAG source documents) must be maintained within a version-controlled repository

## Pre-Commit Quality Policy

**MANDATORY**: All development tasks must complete with a successful run of quality checks to ensure code quality and prevent regressions.

### Automated Quality Check Script

We provide a dedicated QA script that overlaps with pre-commit hooks and provides enhanced feedback:

```bash
# Comprehensive quality check (recommended)
poetry run poe qa-check

# Alternative: Original poe task collection
poetry run poe qa

# Development variations:
poetry run poe qa-fast      # Skip slow tests for quick feedback
poetry run poe qa-verbose   # Detailed output for debugging
poetry run poe qa-fix       # Auto-fix formatting issues
```

### Required Quality Checks

The QA script validates:

1. **Type Safety** - `mypy --strict` validation
2. **Test Coverage** - 85% minimum coverage requirement
3. **Mock Compliance** - Mock-to-real implementation synchronization
4. **Dead Code Detection** - No newly introduced unused code
5. **Code Formatting** - Black and isort compliance
6. **Linting** - Ruff quality checks
7. **Pre-commit Hooks** - All configured hooks must pass

### Code Formatting Commands

Apply all formatting transformations (requires `git add` afterwards):

```bash
# Auto-format all files (comprehensive)
poetry run poe format

# Individual formatting tools:
poetry run poe format-black        # Apply Black formatting
poetry run poe format-isort        # Sort imports with isort
poetry run poe format-ruff         # Apply Ruff auto-fixes
poetry run poe format-files        # Fix whitespace, line endings, etc.

# Check formatting without changes:
poetry run poe format-check        # Check all formatting
poetry run poe format-black-check  # Check Black formatting only
poetry run poe format-isort-check  # Check import sorting only
poetry run poe format-ruff-check   # Check Ruff issues only
```

### Individual Check Commands

For development and debugging, you can run individual checks:

```bash
# Type checking
poetry run poe typecheck              # Source code only
poetry run poe typecheck-all          # Include tests

# Testing with coverage
poetry run poe test-cov-check         # Enforce 85% minimum coverage
poetry run poe test-cov-report        # Generate HTML + terminal reports

# Mock compliance
poetry run poe test-mocks             # Verify mock-to-real synchronization

# Dead code detection
poetry run poe deadcode-diff          # Check for new dead code only

# Pre-commit hooks
poetry run poe precommit-run          # All hooks on all files
poetry run poe precommit-run-hook     # Staged files only
```

## Task Completion Workflow

### For Development Tasks

When completing any development task, follow this workflow:

1. **Complete the implementation**
2. **Format code** (optional but recommended): `poetry run poe format`
3. **Add formatted files**: `git add <files>` (if formatting was applied)
4. **Run quality checks**: `poetry run poe qa-check`
5. **Fix any failures** before proceeding
6. **Commit changes** only after all checks pass

**Automatic Issue Detection**: The QA script provides immediate feedback on issues introduced by your changes, with specific guidance for resolution.

### For Bug Fixes

1. **Write failing test** that reproduces the bug
2. **Implement the fix**
3. **Verify test passes**
4. **Run quality checks**: `poetry run poe qa-check`
5. **Fix any regressions**
6. **Commit changes**

### For New Features

1. **Plan the feature** (use TodoWrite if complex)
2. **Write tests first** (TDD approach)
3. **Implement the feature**
4. **Update documentation** if needed
5. **Run quality checks**: `poetry run poe qa-check`
6. **Fix any issues**
7. **Commit changes**

## Quality Gate Details

### Type Safety Requirements

- **Zero type errors**: `mypy --strict` must pass completely
- **Complete annotations**: All functions, methods, and complex variables must be typed
- **No `Any` types**: Use specific types or `object` when necessary

### Test Coverage Requirements

- **Minimum 85% coverage**: Enforced automatically by `test-cov-check`
- **New code 90% coverage**: All new functionality should be well-tested
- **Public API 100% coverage**: All public interfaces must be tested

### Mock Compliance Requirements

- **Signature synchronization**: Mock objects must match real implementations
- **Protocol compliance**: Mocks must implement required protocols
- **Automated validation**: `test-mocks` must pass to prevent mock drift

### Dead Code Prevention

- **No new dead code**: `deadcode-diff` checks for newly introduced unused code
- **Baseline maintenance**: Intentional dead code is tracked in `vulture_baseline.txt`
- **Regular cleanup**: Dead code should be removed or marked as intentional

## Pre-Commit Hook Integration

### Automated Checks

The following checks run automatically on commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: vulture-diff
        name: Check for new dead code
        entry: python scripts/vulture_diff.py
        language: system
        types: [python]
        pass_filenames: false
```

### Hook Management

```bash
# Install hooks
poetry run poe precommit-install

# Update hooks
poetry run poe precommit-update

# Run manually
poetry run poe precommit-run
```

## Failure Resolution

### Common Issues and Solutions

#### Type Errors
```bash
# Run type check to see errors
poetry run poe typecheck

# Common fixes:
# - Add missing return type annotations: def func() -> ReturnType:
# - Add variable annotations: var: Type = value
# - Import missing types: from typing import Optional, Union
# - Fix generic types: list[str] instead of list
```

#### Coverage Failures
```bash
# See detailed coverage report
poetry run poe test-cov-report

# Open HTML report
open htmlcov/index.html

# Common fixes:
# - Add tests for uncovered functions
# - Test error conditions and edge cases
# - Remove dead code that can't be tested
```

#### Mock Compliance Failures
```bash
# Run mock compliance tests
poetry run poe test-mocks

# Common fixes:
# - Update mock method signatures to match real implementations
# - Add missing methods to mock classes
# - Update protocol definitions when interfaces change
```

#### Dead Code Detection
```bash
# Check for new dead code
poetry run poe deadcode-diff

# Common fixes:
# - Remove unused functions/variables
# - Mark intentional dead code with comments
# - Update vulture baseline if needed
```

## Development Environment Setup

### Initial Setup

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run poe precommit-install

# Verify setup
poetry run poe qa
```

### IDE Configuration

Ensure your IDE is configured for:

- **Type checking**: Enable mypy integration
- **Auto-formatting**: Black, isort integration
- **Import optimization**: Remove unused imports
- **Test discovery**: Pytest integration

## Continuous Integration

### CI/CD Pipeline

The same quality checks run in CI/CD:

```yaml
# .github/workflows/test.yml
- name: Run quality checks
  run: poetry run poe qa
```

### Branch Protection

Main branch is protected and requires:

- ✅ All quality checks passing
- ✅ Up-to-date with main branch
- ✅ Review approval (if applicable)

## Documentation Updates

### When to Update Guidelines

Update this workflow when:

- **New quality tools** are added
- **Quality thresholds** change
- **Workflow steps** are modified
- **Common issues** emerge that need documentation

### Keeping Guidelines Current

- **Review quarterly**: Ensure guidelines match current practices
- **Update after tool changes**: When upgrading linters, type checkers, etc.
- **Document new patterns**: Capture solutions to recurring issues

## Automated Quality Benefits

The dedicated QA script (`scripts/qa_check.py`) provides several advantages over running individual commands:

### Enhanced Feedback
- **Detailed error reporting** with actionable guidance
- **Comprehensive summary** showing all issues at once
- **Auto-fix capabilities** for formatting and style issues
- **Fast mode** for quick development iteration

### Issue Detection
- **Immediate feedback** on problems introduced by changes
- **Specific guidance** linking to relevant documentation
- **Time tracking** to understand check duration
- **Exit codes** for automation and CI/CD integration

### Development Integration
- **IDE-friendly output** with clear error messages
- **Incremental checking** with fast mode for development
- **Auto-fixing** of common style and formatting issues
- **Comprehensive reporting** for code review preparation

## Summary

The development workflow prioritizes quality through automated checks and clear standards. By running `poetry run poe qa-check` before every commit, we maintain:

- **Type safety** through strict mypy checking
- **Test reliability** through coverage requirements
- **Mock consistency** through compliance testing
- **Code cleanliness** through dead code detection
- **Style consistency** through automated formatting

This workflow prevents regressions, improves code quality, and maintains the health of our large codebase (25K+ lines of code).

## Code Formatting System

### Comprehensive Formatting Command

The `poetry run poe format` command applies all formatting transformations that pre-commit hooks would apply:

#### Formatting Operations Applied:
1. **Black**: Python code formatting with 88-character line length
2. **isort**: Import sorting with Black-compatible configuration
3. **Ruff**: Auto-fixable linting issues (unused imports, syntax improvements)
4. **File Formatting**: Whitespace and line ending normalization
   - Remove trailing whitespace from all lines
   - Ensure files end with exactly one newline
   - Normalize line endings to Unix style (`\n`)
   - Process text files: `.py`, `.md`, `.yaml`, `.json`, `.toml`, etc.

#### Usage Workflow:
```bash
# 1. Apply all formatting
poetry run poe format

# 2. Review changes
git diff

# 3. Stage formatted files
git add <modified-files>

# 4. Run quality checks
poetry run poe qa-check

# 5. Commit if all checks pass
git commit -m "Apply code formatting and implement feature"
```

### Selective Formatting

For granular control, individual formatting tools can be run separately:

```bash
# Python code formatting only
poetry run poe format-black

# Import sorting only
poetry run poe format-isort

# Linting auto-fixes only
poetry run poe format-ruff

# Whitespace and line endings only
poetry run poe format-files
```

### Format Checking

Check formatting compliance without making changes:

```bash
# Check all formatting standards
poetry run poe format-check

# Returns exit code 0 if compliant, 1 if changes needed
# Useful for CI/CD and automated workflows
```

### Integration with Quality Assurance

The formatting system integrates with the QA workflow:

- **`qa-fix` command**: Includes automatic formatting as part of issue resolution
- **Pre-commit hooks**: Automatically apply formatting during commit process
- **CI/CD validation**: Format-check ensures consistent formatting in repository

### File Coverage

The formatting system processes:

- **Source code**: `src/` directory (all Python files)
- **Test code**: `tests/` directory (all Python files)
- **Scripts**: `scripts/` directory (Python and shell scripts)
- **Documentation**: Markdown, YAML, TOML, and text files
- **Configuration files**: Root-level config files

**Excluded**: `old/`, `docs/`, `.git/`, `__pycache__/`, build artifacts, and binary files (matches pre-commit exclusions)
