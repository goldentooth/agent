# Coverage Analysis Quick Reference

This document provides instant access to coverage analysis commands and interpretation guidance for the goldentooth-agent project.

## 🚀 Quick Commands

### Find Files with Low/No Coverage
```bash
# Get top 10 files needing coverage attention
poetry run poe test-cov-targets

# Full coverage analysis with detailed output
poetry run poe test-cov-analyze

# Generate HTML report for line-by-line analysis
poetry run poe test-cov-report
```

### Validate Coverage Requirements
```bash
# Enforce 85% minimum coverage (fails if below threshold)
poetry run poe test-cov-check

# Basic coverage run with terminal output
poetry run poe test-cov
```

## 📊 Coverage Report Interpretation

### Priority Levels
- **🔴 Critical (0% coverage)**: Completely untested files - immediate attention required
- **🟠 High (1-49% coverage)**: Major testing gaps - high priority
- **🟡 Medium (50-84% coverage)**: Missing edge cases - medium priority
- **🟢 Good (85%+ coverage)**: Meets project standards

### Module Priority Focus
1. **core/** modules (highest priority - business logic)
2. **flow_engine/** modules (high priority - execution engine)
3. **cli/** modules (medium priority - user interface)
4. **examples/** modules (lowest priority - demonstration code)

## 🔍 Detailed Analysis Workflow

### Step 1: Identify Low Coverage Areas
```bash
poetry run poe test-cov-analyze
```
**Look for**: Files listed with coverage percentages below 85%

### Step 2: Visual Line-by-Line Analysis
```bash
poetry run poe test-cov-report
open htmlcov/index.html  # macOS
# or
python -m http.server 8000 --directory htmlcov  # Any platform
```
**Look for**: Red highlighted lines indicating uncovered code

### Step 3: Prioritize by Impact
Focus testing efforts on:
- Public API functions (exposed in `__init__.py`)
- Error handling paths
- Critical business logic
- Integration points between modules

### Step 4: Validate Improvements
```bash
poetry run poe test-cov-check
```
**Success**: Coverage meets 85% threshold across all modules

## 📁 Coverage Output Files

- `htmlcov/index.html` - Interactive HTML coverage report
- `htmlcov/` directory - Per-file coverage details
- Terminal output - Summary statistics and missing line numbers

## 🎯 Common Coverage Scenarios

### Scenario: New module with 0% coverage
```bash
# 1. Identify the module
poetry run poe test-cov-analyze | grep "0%"

# 2. Check if tests exist
ls tests/path/to/module/

# 3. Create tests if missing
# 4. Validate coverage improvement
poetry run poe test-cov-check
```

### Scenario: Module below 85% threshold
```bash
# 1. Generate detailed report
poetry run poe test-cov-report

# 2. Open HTML report
open htmlcov/index.html

# 3. Navigate to specific module
# 4. Identify uncovered lines (highlighted in red)
# 5. Add tests for uncovered code paths
```

### Scenario: Finding untested public APIs
```bash
# 1. List module's public API
grep -r "def " src/goldentooth_agent/path/to/module/

# 2. Check which functions lack coverage
poetry run poe test-cov-report
# Navigate to module in HTML report

# 3. Ensure all public functions are tested
```

## 🛠️ Advanced Coverage Analysis

### Custom Coverage Analysis Script
The project includes a custom analysis script at `scripts/coverage_analysis.py`:

```bash
# Direct script usage with options
python scripts/coverage_analysis.py --help
python scripts/coverage_analysis.py --limit=20  # Top 20 lowest coverage files
```

### Module-Specific Coverage
```bash
# Test specific module with coverage
pytest tests/core/specific_module/ --cov=goldentooth_agent.core.specific_module --cov-report=term-missing
```

### Coverage with Performance Timing
```bash
# Combine coverage with performance analysis
time poetry run poe test-cov-check
```

## 📈 Coverage Improvement Strategies

### 1. Test Public APIs First
- Focus on functions exposed in `__init__.py`
- Test happy path, error cases, edge cases
- Verify return values and side effects

### 2. Error Path Coverage
- Test exception handling
- Validate error messages
- Test recovery mechanisms

### 3. Integration Coverage
- Test module interactions
- Test dependency injection points
- Test configuration variations

### 4. Performance-Critical Path Coverage
- Test flow execution paths
- Test context management operations
- Test RAG query processing

## 🚨 Pre-Commit Coverage Checklist

Before committing code changes:

1. ✅ Run `poetry run poe test-cov-check` (must pass)
2. ✅ Check that new code has tests
3. ✅ Verify public APIs are covered
4. ✅ Test error handling paths
5. ✅ Review HTML coverage report for gaps

## 🔧 Troubleshooting Coverage Issues

### Coverage command fails
```bash
# Ensure dependencies are installed
poetry install

# Clear coverage cache
rm -rf .coverage htmlcov/

# Re-run coverage
poetry run poe test-cov-report
```

### HTML report not generated
```bash
# Check for write permissions
ls -la htmlcov/

# Force regenerate
rm -rf htmlcov/
poetry run poe test-cov-report
```

### Coverage percentage seems wrong
```bash
# Check coverage configuration
grep -A 10 "\[tool.coverage" pyproject.toml

# Verify source paths and exclusions
```

---

**Quick Start**: Run `poetry run poe test-cov-analyze` to immediately identify files needing coverage attention.