# VS Code Setup for Goldentooth Agent

This document provides VS Code-specific configuration for optimal development experience with the Goldentooth Agent codebase.

## 🔧 Automatic Configuration

The `.vscode/` directory contains workspace-specific settings that will automatically configure VS Code when you open this project:

- **`settings.json`** - Pylance, linting, formatting, and testing configuration
- **`extensions.json`** - Recommended extensions for Python development

## 🚀 Key Features Configured

### **Pylance Configuration**
- **Strict type checking** for production code (`src/`)
- **Relaxed rules for tests** (`tests/`) including:
  - `reportPrivateUsage: "none"` - allows accessing private members in tests
  - Relaxed type checking for test fixtures and mocks
  - Reduced noise from common test patterns

### **Integrated Tooling**
- **MyPy** type checking with project-specific configuration
- **Ruff** linting with different rules for tests vs production
- **Black** code formatting with 88-character line length
- **Pytest** test discovery and execution
- **Bandit** security linting (excluding tests)

### **IntelliSense Enhancements**
- Function return type hints displayed inline
- Variable type hints for unclear assignments
- Improved auto-completion and import suggestions
- Call argument name hints for better readability

## 📦 Recommended Extensions

The following extensions will be automatically suggested when you open the project:

### **Essential**
- **Python** - Core Python language support
- **Pylint** - Additional linting
- **Black Formatter** - Code formatting
- **MyPy Type Checker** - Static type checking
- **Ruff** - Fast Python linter

### **Testing**
- **Test Adapter Converter** - Unified testing interface
- **Python Test Adapter** - Enhanced pytest integration

### **Productivity**
- **Git Graph** - Visual git history
- **GitLens** - Enhanced git integration
- **Markdown All in One** - Documentation editing

## 🎯 Type Checking Behavior

### **Production Code (`src/`)**
- **Strict mode** - All type errors are flagged
- **Private usage warnings** - Disabled (too noisy)
- **Complete type annotations** - Required for new code

### **Test Code (`tests/`)**
- **Relaxed mode** - Many rules disabled for practical testing
- **Private access allowed** - Can access `_private` members
- **Mock-friendly** - Reduced type checking for test doubles
- **Fixture-friendly** - Handles pytest fixtures gracefully

## 🔍 Troubleshooting

### **Issue: Pylance still shows private usage errors in tests**
1. Restart VS Code (`Ctrl+Shift+P` → "Developer: Reload Window")
2. Check that `.vscode/settings.json` is being applied
3. Verify you're working in the `tests/` directory

### **Issue: Type checking too strict/lenient**
- Production code: Modify `pyrightconfig.json` main environment
- Test code: Modify `pyrightconfig.json` tests environment or `.vscode/settings.json`

### **Issue: Extensions not auto-installing**
1. Open Command Palette (`Ctrl+Shift+P`)
2. Run "Extensions: Show Recommended Extensions"
3. Install the recommended extensions manually

## 🎨 Editor Appearance

The configuration sets up:
- **88-character ruler** line for Black compatibility
- **4-space indentation** for Python files
- **Auto-trimming whitespace** on save
- **Excluded directories** from search/file explorer (cache, old files)

## 🧪 Testing Integration

VS Code will automatically:
- **Discover tests** in the `tests/` directory
- **Provide test runner UI** in the sidebar
- **Show test results** inline with code
- **Support debugging** individual tests

Run tests with:
- **Test Explorer** (sidebar icon)
- **Command Palette**: "Python: Run All Tests"
- **Keyboard shortcut**: Configure in settings

## 📝 Additional Tips

1. **Use the Command Palette** (`Ctrl+Shift+P`) to access all Python features
2. **Enable auto-save** for better development experience
3. **Use integrated terminal** for poetry/poetry run commands
4. **Leverage IntelliSense** for type hints and documentation
5. **Check Problems panel** for linting and type errors

This configuration provides an optimal balance between strictness for production code and practicality for test development.
