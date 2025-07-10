# Context System Migration Plan

## Migration Overview

This document outlines the complete migration of the Context system from `old/goldentooth_agent/core/context/` to `src/context/`. The migration will be done function by function, method by method, with each getting its own commit and 100% test coverage.

**Total Scope:**
- **11 files** (9 core + 2 integration)
- **~150+ functions/methods** requiring individual commits
- **15+ test files** to be migrated/updated
- **3 separate packages** to be created

## Target Package Structure

```
src/
├── context/                    # Core Context package (no Flow dependencies)
│   ├── __init__.py
│   ├── symbol.py
│   ├── key.py
│   ├── frame.py
│   ├── dependency_graph.py
│   ├── history_tracker.py
│   ├── snapshot_manager.py
│   └── main.py
├── context_flow/              # Context-Flow integration package
│   ├── __init__.py
│   ├── integration.py         # From flow_integration.py
│   ├── trampoline.py         # From flow_engine/trampoline.py
│   └── bridge.py             # From flow_engine/integrations/context_bridge.py
└── tests/
    └── unit/
        ├── context_tests/
        └── context_flow_tests/
```

## Migration Order (By Dependency)

### Phase 1: Core Context Package (No Dependencies)
<ALREADY COMPLETED>

### Phase 2: Context-Flow Integration Package

#### 11. Context-Flow Bridge (`src/context_flow/bridge.py`)

##### 11.1 Utility Functions
- **Commit 147**: `initialize_context_integration` function
- **Commit 148**: `get_context_bridge` function

##### 11.2 ContextFlowBridge Class
- **Commit 149**: `ContextFlowBridge.__init__` method
- **Commit 150**: `ContextFlowBridge.ensure_context_keys` method
- **Commit 151**: `ContextFlowBridge.get_trampoline_key` method
- **Commit 152**: `ContextFlowBridge.register_trampoline_support` method
- **Commit 153**: `ContextFlowBridge._create_set_exit_method` method
- **Commit 154**: `ContextFlowBridge._create_set_break_method` method
- **Commit 155**: `ContextFlowBridge._create_set_skip_method` method
- **Commit 156**: `ContextFlowBridge._create_check_exit_method` method
- **Commit 157**: `ContextFlowBridge._create_check_break_method` method
- **Commit 158**: `ContextFlowBridge._create_check_skip_method` method

#### 12. Context-Flow Package Integration
- **Commit 159**: `src/context_flow/__init__.py` - Flow integration exports

### Phase 3: Final Integration and Documentation

#### 13. Root Package Integration
- **Commit 160**: Update `src/__init__.py` to include context packages
- **Commit 161**: Update README.md with Context migration notes
- **Commit 162**: Update relevant documentation in `docs/`

## Testing Strategy

### Test Migration Approach
Each commit will include:
1. **Function/method implementation**
2. **Unit tests** for that specific function/method
3. **Type checking** validation
4. **Pre-commit hook** validation

### Test Structure
```
tests/
├── context/
│   ├── test_symbol.py
│   ├── test_key.py
│   ├── test_frame.py
│   ├── test_dependency_graph.py
│   ├── test_history_tracker.py
│   ├── test_snapshot_manager.py
│   └── test_main.py
├── context_flow/
│   ├── test_integration.py
│   ├── test_trampoline.py
│   └── test_bridge.py
└── integration/
    └── test_context_flow_integration.py
```

### Test Coverage Requirements
- **100%** line coverage for each function/method
- **100%** branch coverage for conditional logic
- **Edge case** testing for error conditions
- **Type safety** validation with mypy
- **Integration** testing between components

## Migration Execution Order

### Daily Execution Plan (Estimated)

**Week 1 (Days 1-7): Core Foundation**
- Days 1-2: Commits 1-29 (Symbol, Key, Frame, DependencyGraph)
- Days 3-4: Commits 30-47 (History, Snapshot)
- Days 5-7: Commits 48-70 (Context core methods)

**Week 2 (Days 8-14): Context Main Class**
- Days 8-9: Commits 71-90 (Context management methods)
- Days 10-11: Commits 91-109 (Context utility methods)
- Days 12-14: Commits 110-117 (Core package integration)

**Week 3 (Days 15-21): Flow Integration**
- Days 15-16: Commits 118-128 (Flow combinators)
- Days 17-18: Commits 129-146 (Trampoline system)
- Days 19-21: Commits 147-159 (Bridge system)

**Week 4 (Days 22-23): Final Integration**
- Days 22-23: Commits 160-162 (Documentation and final integration)

## Risk Assessment

### High Risk Areas
1. **Circular Dependencies**: Context and Flow systems have complex interdependencies
2. **Event System Integration**: Async event handling requires careful coordination
3. **Type System Complexity**: Generic types and protocols need careful migration
4. **State Management**: Snapshot and history systems have complex state interactions

### Mitigation Strategies
1. **Dependency Isolation**: Keep core Context package Flow-independent
2. **Incremental Testing**: Test each function individually before integration
3. **Type Validation**: Run mypy after each commit
4. **Integration Testing**: Test Context-Flow integration thoroughly

## Success Criteria

### Per-Commit Success Criteria
- [ ] Function/method implements original functionality
- [ ] Unit tests achieve 100% coverage
- [ ] Type checking passes with mypy
- [ ] Pre-commit hooks pass
- [ ] Integration tests pass (where applicable)

### Overall Success Criteria
- [ ] All 162 commits successfully applied
- [ ] Original functionality preserved
- [ ] New package structure established
- [ ] Dependencies properly isolated
- [ ] Documentation updated
- [ ] CI/CD pipeline updated

## Notes

### Key Architectural Decisions
1. **Package Separation**: Core Context functionality isolated from Flow dependencies
2. **Dependency Direction**: Context-Flow integration depends on both packages
3. **Test Structure**: Tests mirror source structure exactly
4. **Migration Order**: Dependencies-first approach to avoid circular imports

### Important Reminders
- **One function/method per commit** - No exceptions
- **100% test coverage** - Every function must be tested
- **Type checking** - Must pass mypy validation
- **Pre-commit hooks** - Must pass all quality gates
- **Documentation** - Update relevant docs with each major component

### Key Migration Learnings (From Commit #1 Experience)

#### Test Import Strategy - CRITICAL
- **ALWAYS use relative imports in tests**: `from context.symbol import Symbol`
- **NEVER use absolute src imports**: `from src.context.symbol import Symbol`
- Poetry package structure expects relative imports for proper test collection
- Absolute `src.` imports cause test collection failures during pre-commit hooks

#### Package Configuration Requirements
- **Immediately add new packages to pyproject.toml** when creating them
- Add entry: `{ include = "context", from = "src" }` to `[tool.poetry] packages`
- Run `poetry install` after adding packages to update development environment
- Package imports work through poetry's package management, not direct file imports

#### Pre-commit Hook and Staging Best Practices
- **Always stage test files with correct imports before committing**
- Pre-commit hooks can stash/restore changes, potentially reverting import fixes
- Use `git add tests/context/test_file.py` to stage corrected imports explicitly
- Import path consistency is critical for successful test collection

#### Coverage During Migration
- Focus on 100% coverage for individual functions being migrated
- Global project coverage (90%) may conflict during early migration phases
- This is acceptable during migration - prioritize function-level coverage quality
- Individual function tests should be comprehensive and test all edge cases

#### Commit Message and File Management
- Use temporary directories for commit messages: `mktemp -d` then write to file
- Create retrospective files in `.claude/retros/` for each major initiative
- Update retrospective with each commit to track progress and learnings

This migration represents approximately **162 commits** over **3-4 weeks** of focused development work.
