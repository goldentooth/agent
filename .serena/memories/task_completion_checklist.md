# Task Completion Checklist

## What to Do When a Task is Completed

Since this is a minimal project with no testing, linting, or formatting tools configured yet, the completion checklist is basic:

### Current Requirements
1. **Test the code manually**
   ```bash
   python main.py
   ```

2. **Check for syntax errors**
   ```bash
   python -m py_compile main.py
   ```

3. **Verify git status**
   ```bash
   git status
   ```

### Future Requirements (when tools are added)
When the project grows, consider adding:

1. **Run tests** (when testing framework is added)
   ```bash
   python -m pytest  # or similar
   ```

2. **Run linting** (when linter is added)
   ```bash
   ruff check .  # or flake8, pylint
   ```

3. **Run formatting** (when formatter is added)
   ```bash
   black .  # or ruff format
   ```

4. **Type checking** (when mypy is added)
   ```bash
   mypy .
   ```

## Notes
- No automated testing framework currently set up
- No CI/CD pipelines configured
- No pre-commit hooks installed
- Manual testing is currently the only verification method