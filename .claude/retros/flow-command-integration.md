# Flow Command Integration Initiative

## Overview
Resolving duplicate flow command implementations and integrating the complete `flow_command` package with the main `goldentooth_agent` CLI.

## Current Status
- `flow_command` package is complete with comprehensive tests
- `goldentooth_agent` has stub flow commands that need to be replaced
- Missing `FlowDisplay` implementation
- CLI integration needs to use `flow_command.cli.app`

## TDD Implementation Plan

### Phase 1: Resolve Duplicates and Integration (CRITICAL)

#### Step 1: Implement Missing FlowDisplay Class
- [ ] Create `src/flow_command/cli/display.py` with Rich formatting
- [ ] Test driven development for all display methods
- [ ] Support text, JSON, table output formats
- [ ] Add SVG recording capabilities

#### Step 2: Replace Goldentooth Agent Flow Commands
- [ ] Update `src/goldentooth_agent/cli/main.py` to import `flow_command.cli.app`
- [ ] Remove stub `src/goldentooth_agent/cli/commands/flow.py`
- [ ] Update import in main.py to use `flow_command` instead
- [ ] Ensure tests pass after integration

#### Step 3: Integration Testing
- [ ] Create end-to-end CLI integration tests
- [ ] Test actual command execution through main CLI
- [ ] Verify flow commands work via `goldentooth-agent flow list/run/search`
- [ ] Add error handling and edge case tests

### Phase 2: Flow Registry Integration

#### Step 4: Connect to Real Flow Registry
- [ ] Implement flow registration mechanism
- [ ] Create sample flows for testing
- [ ] Add flow discovery and validation
- [ ] Test with actual flow execution

### Phase 3: Advanced Features

#### Step 5: Chat Integration
- [ ] Create chat command handlers
- [ ] Implement `/flow` commands for chat interface
- [ ] Add chat integration tests

## Technical Approach

### 1. Test-First Development
Every change will be preceded by a failing test:
- Write test for expected behavior
- Implement minimal code to pass test
- Refactor while keeping tests green

### 2. Incremental Integration
- Start with smallest possible changes
- Ensure each step works before proceeding
- Maintain all existing functionality

### 3. Comprehensive Validation
- All pre-commit hooks must pass
- 100% test coverage for new code
- Integration tests for complete workflows

## Risk Mitigation

### Breaking Changes
- Existing CLI interfaces must remain compatible
- All existing tests must continue to pass
- No functional regressions allowed

### Quality Gates
- Pre-commit hooks enforced at every step
- Code review for all changes
- Performance validation for flow execution

## Success Criteria

1. ✅ Single, unified flow command implementation
2. ✅ Complete CLI integration with `goldentooth-agent` command
3. ✅ Rich terminal display with multiple output formats
4. ✅ Comprehensive test coverage (unit + integration)
5. ✅ Working flow execution with real flows
6. ✅ Chat integration for `/flow` commands

## Dependencies

- Rich library for terminal display
- Typer for CLI framework
- Flow registry for flow discovery
- Existing test infrastructure

## Timeline

- **Phase 1** (Critical): 1-2 commits per step, immediate priority
- **Phase 2** (Integration): After Phase 1 complete
- **Phase 3** (Advanced): After core functionality validated

This approach ensures we maintain the highest quality standards while systematically resolving the integration issues and building toward full flow command functionality.
