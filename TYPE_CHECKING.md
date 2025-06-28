# Type Checking Strategy

This document outlines the type checking configuration and strategy for the Goldentooth Agent project.

## Current Configuration

The project uses both **MyPy** and **Pyright/Pylance** for comprehensive type checking.

### MyPy Configuration (pyproject.toml)

We use a strict MyPy configuration with the following key settings:

```toml
[tool.mypy]
strict = true                    # Enable all strict checks
python_version = "3.13"
show_error_codes = true
pretty = true

# Disallow untyped code
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_untyped_decorators = true
disallow_any_generics = true
disallow_any_unimported = true
disallow_subclassing_any = true

# None and Optional handling
no_implicit_optional = true
strict_optional = true

# Miscellaneous strictness
strict_equality = true
extra_checks = true
check_untyped_defs = true
strict_concatenate = true
enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool"]
```

### Pyright Configuration (pyrightconfig.json)

We use Pyright in strict mode for additional type checking, especially for VS Code users with Pylance.

## Gradual Adoption Strategy

Some strict settings are currently disabled to avoid overwhelming amounts of type errors:

### Currently Disabled (but planned for future)

- `disallow_any_expr = false` - Would flag expressions containing Any types (853 errors)
- `disallow_any_explicit = false` - Would flag explicit Any usage (174 errors, down from 182)
- `disallow_any_decorated = false` - Would flag Any in decorated functions

Progress on `disallow_any_explicit`:
- Created type aliases for legitimate Any usage in 4 core files
- Documented migration strategy in EXPLICIT_ANY_MIGRATION.md
- Ready for gradual adoption across remaining modules

### Planned Improvements

1. **Phase 1**: Fix specific high-impact type issues
   - Schema type annotations
   - Flow generic parameters
   - Context key typing

2. **Phase 2**: Enable `disallow_any_explicit`
   - Replace explicit Any with more specific types where possible
   - Add proper generic type parameters

3. **Phase 3**: Enable `disallow_any_expr`
   - Remove Any from expressions
   - Improve type inference

## Running Type Checks

### MyPy (Primary)
```bash
poetry run poe typecheck        # Type check source code only
poetry run poe typecheck-all    # Type check source + tests
```

### Pyright (Additional validation)
```bash
pyright src/                    # Run pyright directly
```

### VS Code Integration
Pylance (based on Pyright) will automatically show type errors in VS Code when `pyrightconfig.json` is present.

## Common Type Issues and Solutions

### Schema Type Issues
**Problem**: Generic schema types cause type checker confusion
**Solution**: Use specific type parameters and casts where necessary

```python
# Before
field_type = type(field_value) if field_value is not None else Any
context_key = ContextKey.create(key_name, field_type, description)

# After
field_type = type(field_value) if field_value is not None else Any
context_key = ContextKey.create(key_name, cast(type[Any], field_type), description)
```

### Flow Type Parameters
**Problem**: Flow[Any, Any] loses type information
**Solution**: Use proper generic type parameters where possible

### Context Key Types
**Problem**: Context keys with dynamic types
**Solution**: Use TypeVar bounds and proper type guards

## Contributing Guidelines

When adding new code:

1. **Always add complete type annotations** for all functions and methods
2. **Avoid Any types** unless absolutely necessary
3. **Use generic type parameters** instead of Any where possible
4. **Test with both MyPy and Pylance** before submitting PRs
5. **Document any necessary type: ignore comments**

## Error Codes Reference

Key MyPy error codes to watch for:

- `[misc]` - Various type issues (enabled by strict mode)
- `[explicit-any]` - Explicit Any usage (when enabled)
- `[no-any-return]` - Functions returning Any
- `[ignore-without-code]` - type: ignore without error code
- `[redundant-expr]` - Redundant expressions
- `[truthy-bool]` - Truthy bool checks

## Future Goals

The long-term goal is to achieve:
- Zero MyPy errors with all strict settings enabled
- Minimal use of Any types
- Complete type safety across the codebase
- Excellent IDE support with comprehensive type information
