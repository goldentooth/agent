# Command Reference

Quick reference for all development commands in the Goldentooth Agent project.

## Quality Assurance

### Comprehensive Checks
```bash
# Recommended: Full quality check with enhanced feedback
poetry run poe qa-check

# Alternative: Original task collection  
poetry run poe qa

# Development variations
poetry run poe qa-fast      # Skip slow tests for quick feedback
poetry run poe qa-verbose   # Detailed output for debugging
poetry run poe qa-fix       # Auto-fix formatting issues
```

### Individual Quality Checks
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
```

## Code Formatting

### Apply Formatting
```bash
# Comprehensive formatting (recommended)
poetry run poe format

# Individual formatting tools
poetry run poe format-black        # Apply Black formatting
poetry run poe format-isort        # Sort imports with isort
poetry run poe format-ruff         # Apply Ruff auto-fixes
poetry run poe format-files        # Fix whitespace, line endings
```

### Check Formatting
```bash
# Check all formatting standards
poetry run poe format-check

# Individual format checks
poetry run poe format-black-check  # Check Black formatting only
poetry run poe format-isort-check  # Check import sorting only
poetry run poe format-ruff-check   # Check Ruff issues only
```

## Pre-commit Hooks

```bash
# Setup and management
poetry run poe precommit-install   # Install hooks
poetry run poe precommit-update    # Update hooks

# Manual execution
poetry run poe precommit-run       # All hooks on all files
poetry run poe precommit-run-hook  # Staged files only
```

## Testing

### Basic Testing
```bash
poetry run poe test                # Run all tests
poetry run pytest                 # Direct pytest
```

### Development Testing
```bash
# Fast feedback during development
poetry run pytest tests/unit/ -x --ff

# Coverage testing
poetry run pytest --cov=src/goldentooth_agent --cov-fail-under=85

# Specialized test suites
poetry run pytest tests/performance/ --benchmark-only
poetry run pytest tests/integration/ --slow
```

## Common Workflows

### Before Committing
```bash
# Standard workflow
poetry run poe qa-check

# With auto-fixing
poetry run poe qa-fix
```

### Development Iteration
```bash
# Quick feedback loop
poetry run poe qa-fast

# Type safety focus
poetry run poe typecheck
```

### Full Validation
```bash
# Comprehensive check
poetry run poe qa-check

# Include manual pre-commit validation
poetry run poe precommit-run
```

## Error Resolution

### Type Errors
```bash
poetry run poe typecheck           # Identify type issues
poetry run poe format              # Fix formatting first
```

### Test Failures
```bash
poetry run poe test-cov-report     # Detailed coverage analysis
poetry run poe test-mocks          # Check mock synchronization
```

### Mock Compliance Issues
```bash
poetry run poe test-mocks          # Verify mock signatures match real implementations
```

### Performance Issues
```bash
poetry run pytest tests/performance/ --benchmark-only
```

## CI/CD Commands

Commands used in automated pipelines:

```bash
# Standard CI pipeline
poetry run poe qa                  # All quality checks
poetry run poe typecheck-all       # Type check including tests
poetry run poe test-cov-check      # Coverage enforcement
```