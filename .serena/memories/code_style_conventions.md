# Code Style and Conventions

## Current Code Style
Based on the existing `main.py` file:

### Function Definitions
- Simple function definitions with no type hints
- Basic naming conventions (snake_case)
- No docstrings present in current code

### Code Structure
```python
def main():
    print("Hello from agent!")


if __name__ == "__main__":
    main()
```

## Conventions to Follow
Since this is a minimal project with no established conventions yet:

### Python Standards
- Follow PEP 8 style guidelines
- Use snake_case for function and variable names
- Use 4 spaces for indentation (standard Python)
- Add type hints for better code clarity
- Add docstrings for functions and classes
- Keep functions simple and focused

### Project Standards
- No specific linting or formatting tools configured yet
- No code quality tools (black, flake8, mypy, etc.) in use
- Standard Python project structure expected as it grows

## Recommendations
- Consider adding type hints: `def main() -> None:`
- Add docstrings for documentation
- Set up code formatting tools (black, ruff) when project grows
- Add linting tools (flake8, pylint, or ruff) for code quality