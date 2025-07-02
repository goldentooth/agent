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

## CRITICAL GIT SAFETY RULES

### NEVER USE DESTRUCTIVE GIT COMMANDS

**ABSOLUTE PROHIBITION**: The following git commands are NEVER allowed and will destroy work:

❌ **FORBIDDEN COMMANDS:**
- `git reset` (any form - soft, mixed, hard)
- `git reset --hard`
- `git reset HEAD`
- `git checkout .` (discards changes)
- `git clean -f` (removes untracked files)
- `git rebase` without explicit user permission
- `git push --force` or `git push -f`

**SAFE ALTERNATIVES:**
✅ Use `git stash` to temporarily save changes
✅ Use `git add` and `git commit` to save progress
✅ Use `git checkout filename` only for single files with explicit intent
✅ Use `git status` to check what changes exist
✅ Use `git diff` to see what changes would be lost

**RATIONALE**: These commands can destroy hours of work instantly. In a single-user private project, there is NEVER a valid reason to use destructive reset commands when helping with development tasks.

## Pre-Commit Quality Policy

**MANDATORY**: All development tasks must complete with a successful run of quality checks to ensure code quality and prevent regressions.

### Automated Quality Check Script

We provide a dedicated QA script that overlaps with pre-commit hooks and provides enhanced feedback. See **[Command Reference](command-reference.md)** for full details on all available commands.

### Required Quality Checks

The QA script validates:

1. **Type Safety** - `mypy --strict` validation
2. **Test Coverage** - 85% minimum coverage requirement
3. **Mock Compliance** - Mock-to-real implementation synchronization
4. **Dead Code Detection** - No newly introduced unused code
5. **Code Formatting** - Black and isort compliance
6. **Linting** - Ruff quality checks
7. **Pre-commit Hooks** - All configured hooks must pass

### Required Static Analysis Tools (Mandatory)

**All developers must use these static analysis tools as part of the development workflow:**

#### Pre-commit Hooks (Automatically Enforced)
```bash
# Dictionary access pattern detection (prevents dict.attr errors)
scripts/check_dict_access.py --staged

# Type annotation completeness audit
scripts/audit_type_annotations.py

# Standard quality tools - see command-reference.md for details
poetry run poe typecheck    # mypy strict type checking
poetry run poe format       # black, isort, ruff auto-fixes
poetry run poe test-cov     # pytest with coverage validation
```

#### Development-Time Analysis (Run Regularly)
```bash
# Response handling consistency check
scripts/analyze_response_patterns.py

# Quality checks - see command-reference.md for all options
poetry run poe deadcode-diff  # Find newly introduced unused code
poetry run poe test-mocks     # Ensure mocks stay synchronized

# Dependency analysis
poetry run rg "from goldentooth_agent" src/ | cut -d: -f2 | sort | uniq -c
```

#### Integration Analysis (Before Major Changes)
```bash
# Comprehensive response pattern analysis
scripts/analyze_response_patterns.py > response_analysis.txt
# Review for consistency issues before implementing changes

# Full type annotation audit
scripts/audit_type_annotations.py > type_coverage.txt
# Ensure type safety baseline before major refactoring

# Architectural dependency review
find src/ -name "*.py" -exec wc -l {} \; | sort -nr | head -20
# Identify largest modules that may need attention
```

#### Quality Gate Enforcement
**Pre-commit hooks WILL PREVENT commits that:**
- Introduce dictionary attribute access patterns (`result.response` on dict objects)
- Add functions without return type annotations
- Fail type checking with mypy --strict
- Reduce test coverage below 85%
- Introduce new dead code
- Violate code formatting standards

**Development workflow MUST include:**
- Running `poetry run poe qa-check` before every commit
- Addressing all static analysis warnings
- Using enhanced error reporting for new exception handling
- Following response handling standards for new agent interfaces

### Code Formatting Commands

Apply all formatting transformations (requires `git add` afterwards). See **[Command Reference](command-reference.md)** for complete formatting commands.

```bash
# Most common formatting commands:
poetry run poe format        # Auto-format all files (comprehensive)
poetry run poe format-check  # Check all formatting without changes
```

### Individual Check Commands

For development and debugging, run individual checks. See **[Command Reference](command-reference.md)** for the complete list of available commands.

```bash
# Most common individual checks:
poetry run poe typecheck      # Type checking
poetry run poe test-cov-check # Coverage validation
poetry run poe test-mocks     # Mock compliance
```

## Pre-Development Investigation Protocol

**CRITICAL**: Always perform systematic investigation before implementing fixes or features. This prevents partial solutions and ensures comprehensive improvements.

### For Bug Fixes

#### 1. **Systematic Error Reproduction**
```bash
# Document the exact error
echo "Error: 'dict' object has no attribute 'response'" > bug_report.md
echo "Command: goldentooth-agent chat --agent rag" >> bug_report.md
echo "Stack trace: [paste full stack trace]" >> bug_report.md
```

#### 2. **Codebase Investigation Strategy**
```bash
# Use Task agent for broad pattern discovery
# Example: "Search for all files handling agent responses"
# Example: "Find all occurrences of result.response in the codebase"

# Use specific tools for targeted analysis
poetry run rg "\.response" src/  # Find attribute access patterns
poetry run rg "result\[" src/   # Find dictionary access patterns
```

#### 3. **Root Cause Analysis Process**
1. **Identify the failure point** - Exact line and function where error occurs
2. **Trace data flow** - Follow the data from source to failure point
3. **Check type consistency** - Verify expected vs actual data types
4. **Find similar patterns** - Look for the same issue in other parts of codebase
5. **Assess scope** - Is this a local fix or a systemic issue?

#### 4. **Comprehensive Solution Planning**
```markdown
# Required sections for bug fix planning:

## Root Cause
- Specific technical reason for the failure
- Data type mismatches or interface inconsistencies

## Immediate Fix
- Minimum changes needed to resolve the error
- File-by-file changes with before/after examples

## Prevention Strategy
- How to prevent this category of error in the future
- Static analysis tools, runtime validation, etc.

## Improvement Opportunities
- Related technical debt that should be addressed
- System-wide improvements that would help

## Implementation Plan
1. Phase 1: Fix immediate issue
2. Phase 2: Add prevention mechanisms
3. Phase 3: Implement broader improvements
```

### For Feature Development

#### 1. **Architecture Investigation**
```bash
# Understand existing patterns
poetry run scripts/analyze_response_patterns.py  # Check response handling
poetry run scripts/audit_type_annotations.py     # Check type coverage

# Review related modules
find src/ -name "*.py" -path "*agent*" | head -10  # Find agent-related files
```

#### 2. **Integration Point Analysis**
- **Identify all touch points** - What existing code will this feature interact with?
- **Check interface consistency** - Do existing interfaces support this feature?
- **Assess compatibility** - Will this break existing functionality?
- **Plan migration path** - How to integrate without disruption?

#### 3. **Implementation Strategy**
```python
# Required: Plan before coding
"""
Feature: Enhanced Agent Response Handling

Touch Points:
- src/goldentooth_agent/cli/commands/chat.py (main interface)
- src/goldentooth_agent/core/rag/ (RAG agent implementation)
- tests/integration/ (response validation tests)

Interface Changes:
- All agents must return AgentResponse schema
- Chat command needs response.response -> response["response"] fixes
- Integration tests need schema validation

Migration Plan:
1. Create AgentResponse schema (new)
2. Update agents to support both dict and schema returns (compatible)
3. Update consumers to handle schema objects (breaking but controlled)
4. Remove dictionary support (cleanup)
"""
```

### Investigation Tools and Commands

#### Required Static Analysis Tools
```bash
# Type and interface analysis
poetry run poe typecheck                    # Check type consistency
scripts/audit_type_annotations.py           # Find missing type annotations
scripts/check_dict_access.py --staged       # Check for dict.attr patterns
scripts/analyze_response_patterns.py        # Find response handling inconsistencies

# Dependency and architecture analysis
poetry run rg "from.*import" src/ | grep -E "(agent|response)" # Find imports
poetry run rg "class.*Agent" src/          # Find all agent classes
poetry run rg "def.*response" src/         # Find response-handling functions
```

#### Development-Time Validation
```bash
# Before making changes - establish baseline
poetry run poe qa-check > baseline_qa.log

# During development - check incrementally
poetry run poe qa-fast                     # Quick feedback loop
poetry run poe typecheck                   # Type safety validation

# Before commit - comprehensive validation
poetry run poe qa-check                    # Full quality assurance
```

#### Research Commands for Complex Issues
```bash
# Pattern discovery across codebase
poetry run rg "response\." src/ -A 3 -B 3  # Context around response access
poetry run rg "result\[" src/ -A 2         # Dictionary access patterns
poetry run rg "return.*dict" src/ -A 1     # Functions returning dicts

# Dependency analysis
poetry run rg "from goldentooth_agent" src/ | cut -d: -f2 | sort | uniq -c
poetry run find src/ -name "*.py" -exec wc -l {} \; | sort -nr | head -20

# Test coverage analysis
poetry run pytest --cov-report=term-missing --cov=src/ tests/
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
poetry run poe test-mocks  # See command-reference.md for details
```

#### Dead Code Detection
```bash
poetry run poe deadcode-diff  # See command-reference.md for details
```

## Development Environment Setup

### Initial Setup

```bash
poetry install
poetry run poe precommit-install
poetry run poe qa  # See command-reference.md for all QA commands
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
  run: poetry run poe qa  # See command-reference.md
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

The `poetry run poe format` command applies all formatting transformations. See **[Command Reference](command-reference.md)** for detailed formatting options.

#### Formatting Operations:
1. **Black**: Python code formatting with 88-character line length
2. **isort**: Import sorting with Black-compatible configuration  
3. **Ruff**: Auto-fixable linting issues
4. **File Formatting**: Whitespace and line ending normalization

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

See **[Command Reference](command-reference.md)** for individual formatting commands.

### Format Checking

Check formatting compliance: `poetry run poe format-check`

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
