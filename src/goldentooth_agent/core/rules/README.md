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
- `async evaluate(self, ctx: TIn) -> TIn` - Evaluate the rules against the context and apply actions for matching rules
- `add_rule(self, rule: Rule[TIn]) -> None` - Add a new rule to the rule engine
- `as_flow(self) -> Flow[TIn, TIn]` - Convert the rule engine to a flow that evaluates the rules for each item in a stream

#### Rule
A rule that applies a condition to an input and executes an action if the condition is met.

    Rules are pure Flow-based components that evaluate conditions and apply transformations
    conditionally. They integrate seamlessly with the Flow system for stream processing.

**Public Methods:**
- `async apply(self, ctx: TIn) -> TIn` - Apply the rule to the given context
- `as_flow(self) -> Flow[TIn, TIn]` - Convert the rule to a flow that applies the rule to each item in a stream

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
