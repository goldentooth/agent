# Rules

Rules module

## Overview

- **Complexity**: Medium
- **Files**: 3 Python files
- **Lines of Code**: ~101
- **Classes**: 2
- **Functions**: 8

## API Reference

### Classes

#### RuleEngine
A rule engine that evaluates a list of rules against a context and applies actions based on matching conditions.

    The RuleEngine is pure Flow-based and processes rules in priority order. It can be converted
    to a Flow for stream processing or used directly for single context evaluation.

**Public Methods:**
- `evaluate()`
- `add_rule()`
- `as_flow()`

#### Rule
A rule that applies a condition to an input and executes an action if the condition is met.

    Rules are pure Flow-based components that evaluate conditions and apply transformations
    conditionally. They integrate seamlessly with the Flow system for stream processing.

**Public Methods:**
- `apply()`
- `as_flow()`

## Dependencies

### External Dependencies
- `collections`
- `dataclasses`
- `goldentooth_agent`
- `rule`
- `rule_engine`
- `typing`

## Exports

This module exports the following symbols:

- `Rule`
- `RuleEngine`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
