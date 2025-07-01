# Claude Code Hooks Configuration

This document provides the recommended Claude Code hooks configuration for optimal development experience with the Goldentooth Agent project.

## Quick Setup

Add this configuration to your Claude Code settings:

```json
{
  "hooks": {
    "after_edit": [
      "black {file}",
      "isort {file}",
      "ruff check --fix {file} || true",
      "goldentooth-agent dev quick-check {file} || true"
    ],
    "after_write": [
      "black {file}",
      "isort {file}"
    ]
  }
}
```

## What Each Hook Does

### `after_edit` Hooks
Run after you edit and save a file:

- **`black {file}`** - Formats Python code according to Black standards
- **`isort {file}`** - Sorts and organizes imports
- **`ruff check --fix {file} || true`** - Auto-fixes safe linting issues (never fails)
- **`goldentooth-agent dev quick-check {file} || true`** - Provides gentle development feedback

### `after_write` Hooks  
Run after you create new files:

- **`black {file}`** - Ensures new files are properly formatted
- **`isort {file}`** - Organizes imports in new files

## Benefits

### ✅ **Eliminates Pre-commit Friction**
- No more "fix formatting and try again" loops
- Pre-commit hooks focus on logic and types, not formatting
- Faster, smoother commit process

### ✅ **Instant Feedback**
- See formatting applied immediately as you work
- Quick suggestions for common issues
- Learn best practices through gentle reminders

### ✅ **Zero Mental Overhead**
- Formatting happens automatically
- No need to remember to run formatting tools
- Focus on coding, not code style

## Example Development Flow

```bash
# 1. Edit a file in Claude Code
vim src/cli/commands/debug.py

# After saving, you'll see:
💡 Quick feedback for debug.py:
  💡 CLI help text contains multiline/unicode - may not render well
     Consider: Simple help text + link to documentation
  ℹ️  These are suggestions - your work is automatically saved!

# 2. File is automatically formatted and ready to commit
git add . && git commit -m "Add debug command"
# ✅ No formatting issues - commit succeeds immediately
```

## Customization Options

### Minimal Configuration (Formatting Only)
```json
{
  "hooks": {
    "after_edit": ["black {file}", "isort {file}"]
  }
}
```

### Enhanced Configuration (With Feedback)
```json
{
  "hooks": {
    "after_edit": [
      "black {file}",
      "isort {file}",
      "ruff check --fix {file} || true",
      "goldentooth-agent dev quick-check {file} || true"
    ],
    "before_read": [
      "goldentooth-agent dev quick-check {file} || true"
    ]
  }
}
```

### Project-Specific Configuration
```json
{
  "hooks": {
    "after_edit": [
      "black {file}",
      "isort {file}",
      "ruff check --fix {file} || true"
    ],
    "after_write": [
      "black {file}",
      "isort {file}",
      "goldentooth-agent dev quick-check {file} || true"
    ]
  }
}
```

## Troubleshooting

### "Hook commands not found"
Ensure you're in the project directory with Poetry environment activated:
```bash
cd /path/to/goldentooth-agent
poetry shell
```

### "Hooks running too slowly"
Remove the quick-check hook if performance is an issue:
```json
{
  "hooks": {
    "after_edit": ["black {file}", "isort {file}"]
  }
}
```

### "Don't want automatic formatting"
Hooks are completely optional. You can:
- Use minimal configuration with just `black {file}`
- Disable hooks entirely
- Use project-specific configuration per repository

## Integration with Pre-commit

This configuration works alongside the project's optimized pre-commit hooks:

- **Claude Code hooks**: Handle formatting automatically during development
- **Pre-commit hooks**: Run in fail-fast mode with three phases:
  1. **Fast formatting/linting checks** (Black, isort, Ruff, MyPy) - fail immediately if issues found
  2. **Metadata and documentation updates** - auto-fix stale documentation
  3. **Expensive checks** (Sphinx, pytest) - only run if formatting passes
- **Result**: Much faster feedback loop with early failure detection

With `fail_fast: true`, pre-commit stops at the first failure, avoiding expensive Sphinx builds and test runs when there are simple formatting issues.

## Advanced Usage

### Conditional Hooks
```json
{
  "hooks": {
    "after_edit": [
      "test -f pyproject.toml && black {file} || echo 'Not a Python project'",
      "test -f pyproject.toml && isort {file} || true"
    ]
  }
}
```

### File Type Specific
```json
{
  "hooks": {
    "after_edit": [
      "if [[ {file} == *.py ]]; then black {file} && isort {file}; fi"
    ]
  }
}
```

This configuration provides a seamless development experience while maintaining code quality standards.