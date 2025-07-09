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
    ├── context/
    └── context_flow/
```

## Migration Order (By Dependency)

### Phase 1: Core Context Package (No Dependencies)

#### 1. Symbol System (`src/context/symbol.py`)
- **Commit 1**: `Symbol.__new__` method
- **Commit 2**: `Symbol.parts` property
- **Commit 3**: Symbol class documentation and type hints

#### 2. Context Key System (`src/context/key.py`)
- **Commit 4**: `ContextKey` class structure and `__init__`
- **Commit 5**: `ContextKey.create` classmethod
- **Commit 6**: `ContextKey.symbol` cached property
- **Commit 7**: `ContextKey.__str__` method
- **Commit 8**: `ContextKey.__repr__` method
- **Commit 9**: `ContextKey.__eq__` method
- **Commit 10**: `ContextKey.__hash__` method
- **Commit 11**: `context_key` utility function

#### 3. Context Frame System (`src/context/frame.py`)
- **Commit 12**: `ContextFrame.__init__` method
- **Commit 13**: `ContextFrame.__getitem__` method
- **Commit 14**: `ContextFrame.__setitem__` method
- **Commit 15**: `ContextFrame.__delitem__` method
- **Commit 16**: `ContextFrame.__contains__` method
- **Commit 17**: `ContextFrame.copy` method

#### 4. Dependency Graph System (`src/context/dependency_graph.py`)
- **Commit 18**: `DependencyGraph.__init__` method
- **Commit 19**: `DependencyGraph.add_dependency` method
- **Commit 20**: `DependencyGraph.remove_dependency` method
- **Commit 21**: `DependencyGraph.remove_all_dependencies` method
- **Commit 22**: `DependencyGraph.get_dependents` method
- **Commit 23**: `DependencyGraph.has_dependents` method
- **Commit 24**: `DependencyGraph.get_all_source_keys` method
- **Commit 25**: `DependencyGraph.clear` method
- **Commit 26**: `DependencyGraph.get_graph_copy` method
- **Commit 27**: `DependencyGraph.__len__` method
- **Commit 28**: `DependencyGraph.__contains__` method
- **Commit 29**: `DependencyGraph.__repr__` method

#### 5. History Tracking System (`src/context/history_tracker.py`)
- **Commit 30**: `ContextChangeEvent.__init__` method
- **Commit 31**: `ContextChangeEvent.__repr__` method
- **Commit 32**: `HistoryTracker.__init__` method
- **Commit 33**: `HistoryTracker.record_change` method
- **Commit 34**: `HistoryTracker.get_history` method
- **Commit 35**: `HistoryTracker.clear_history` method
- **Commit 36**: `HistoryTracker.get_history_size` method
- **Commit 37**: `HistoryTracker.set_max_history_size` method
- **Commit 38**: `HistoryTracker.replay_changes_since` method
- **Commit 39**: `HistoryTracker.get_changes_to_reverse` method
- **Commit 40**: `HistoryTracker.get_all_history` method

#### 6. Snapshot Management System (`src/context/snapshot_manager.py`)
- **Commit 41**: `SnapshotManager.__init__` method
- **Commit 42**: `SnapshotManager.create_snapshot` method
- **Commit 43**: `SnapshotManager.restore_snapshot` method
- **Commit 44**: `SnapshotManager.list_snapshots` method
- **Commit 45**: `SnapshotManager.delete_snapshot` method
- **Commit 46**: `SnapshotManager.get_snapshot` method
- **Commit 47**: `SnapshotManager.clear_snapshots` method

#### 7. Main Context System (`src/context/main.py`) - **LARGEST SECTION**

##### 7.1 ContextSnapshot Class
- **Commit 48**: `ContextSnapshot.__init__` method
- **Commit 49**: `ContextSnapshot.restore_to` method

##### 7.2 ComputedProperty Class
- **Commit 50**: `ComputedProperty.__init__` method
- **Commit 51**: `ComputedProperty.compute` method
- **Commit 52**: `ComputedProperty.invalidate` method
- **Commit 53**: `ComputedProperty.subscribe` method
- **Commit 54**: `ComputedProperty.notify_change` method

##### 7.3 Transformation Class
- **Commit 55**: `Transformation.__init__` method
- **Commit 56**: `Transformation.apply` method

##### 7.4 Context Class - Core Methods
- **Commit 57**: `Context.__init__` method
- **Commit 58**: `Context.get` method
- **Commit 59**: `Context.__getitem__` method
- **Commit 60**: `Context.set` method
- **Commit 61**: `Context.__setitem__` method
- **Commit 62**: `Context.__contains__` method

##### 7.5 Context Class - Layer Management
- **Commit 63**: `Context.push_layer` method
- **Commit 64**: `Context.pop_layer` method
- **Commit 65**: `Context.fork` method
- **Commit 66**: `Context.fork_with_history` method
- **Commit 67**: `Context.merge` method

##### 7.6 Context Class - Diff and Comparison
- **Commit 68**: `Context.diff` method
- **Commit 69**: `Context.deep_diff` method

##### 7.7 Context Class - Snapshot Management
- **Commit 70**: `Context.create_snapshot` method
- **Commit 71**: `Context.restore_snapshot` method
- **Commit 72**: `Context.list_snapshots` method
- **Commit 73**: `Context.delete_snapshot` method
- **Commit 74**: `Context.get_snapshots` method

##### 7.8 Context Class - History Management
- **Commit 75**: `Context.get_change_history` method
- **Commit 76**: `Context.clear_history` method
- **Commit 77**: `Context.get_history_size` method
- **Commit 78**: `Context.set_max_history_size` method
- **Commit 79**: `Context.rollback_to_timestamp` method
- **Commit 80**: `Context.replay_changes_since` method

##### 7.9 Context Class - Event System (Flow-Independent)
- **Commit 81**: `Context.keys` method
- **Commit 82**: `Context.subscribe_sync` method [NOT DONE]
- **Commit 83**: `Context.subscribe_async` method [NOT DONE]
- **Commit 84**: `Context.global_changes_sync` method [NOT DONE]
- **Commit 85**: `Context.global_changes_async` method [NOT DONE]

##### 7.10 Context Class - Computed Properties
- **Commit 86**: `Context.add_computed_property` method
- **Commit 87**: `Context.remove_computed_property` method
- **Commit 88**: `Context.get_computed_value` method
- **Commit 89**: `Context.is_computed_property` method
- **Commit 90**: `Context.computed_properties` property

##### 7.11 Context Class - Transformations
- **Commit 91**: `Context.add_transformation` method
- **Commit 92**: `Context.remove_transformations` method
- **Commit 93**: `Context.transformations` property

##### 7.12 Context Class - Query and Search
- **Commit 94**: `Context.query` method
- **Commit 95**: `Context.find_keys` method
- **Commit 96**: `Context.find_values` method
- **Commit 97**: `Context.filter_by_type` method
- **Commit 98**: `Context.search` method

##### 7.13 Context Class - Nested Operations
- **Commit 99**: `Context.get_nested` method
- **Commit 100**: `Context.set_nested` method
- **Commit 101**: `Context.has_nested` method
- **Commit 102**: `Context.flatten` method

##### 7.14 Context Class - Utility Methods
- **Commit 103**: `Context.dump` method
- **Commit 104**: `Context.__repr__` method

##### 7.15 Context Class - Private Methods
- **Commit 105**: `Context._record_change` method
- **Commit 106**: `Context._emit_change_event` method
- **Commit 107**: `Context._apply_transformations` method
- **Commit 108**: `Context._invalidate_dependent_computed_properties` method
- **Commit 109**: `Context._handle_computed_property_change` method

#### 8. Core Context Package Integration
- **Commit 110**: `src/context/__init__.py` - Core exports (no Flow dependencies)

### Phase 2: Context-Flow Integration Package

#### 9. Flow Integration Core (`src/context_flow/integration.py`)

##### 9.1 Exception Classes
- **Commit 111**: `ContextFlowError` exception class
- **Commit 112**: `MissingRequiredKeyError` exception class
- **Commit 113**: `ContextTypeMismatchError` exception class

##### 9.2 Utility Functions
- **Commit 114**: `_single_item_stream` function
- **Commit 115**: `run_flow_with_input` function
- **Commit 116**: `extend_flow_with_context` function
- **Commit 117**: `context_flow` decorator function

##### 9.3 Context-Flow Bridge Methods
- **Commit 118**: `Context.as_flow` method (Flow-dependent)
- **Commit 119**: `Context.global_changes_as_flow` method (Flow-dependent)

##### 9.4 ContextFlowCombinators Class
- **Commit 120**: `ContextFlowCombinators.get_key` method
- **Commit 121**: `ContextFlowCombinators.set_key` method
- **Commit 122**: `ContextFlowCombinators.require_key` method
- **Commit 123**: `ContextFlowCombinators.optional_key` method
- **Commit 124**: `ContextFlowCombinators.move_key` method
- **Commit 125**: `ContextFlowCombinators.copy_key` method
- **Commit 126**: `ContextFlowCombinators.forget_key` method
- **Commit 127**: `ContextFlowCombinators.require_keys` method
- **Commit 128**: `ContextFlowCombinators.transform_key` method

#### 10. Trampoline System (`src/context_flow/trampoline.py`)

##### 10.1 Utility Functions
- **Commit 129**: `_async_iter_from_item` function
- **Commit 130**: `extend_flow_with_trampoline` function

##### 10.2 Context Keys
- **Commit 131**: `SHOULD_EXIT_KEY` constant
- **Commit 132**: `SHOULD_BREAK_KEY` constant
- **Commit 133**: `SHOULD_SKIP_KEY` constant

##### 10.3 TrampolineFlowCombinators Class
- **Commit 134**: `TrampolineFlowCombinators.set_should_exit` method
- **Commit 135**: `TrampolineFlowCombinators.set_should_break` method
- **Commit 136**: `TrampolineFlowCombinators.set_should_skip` method
- **Commit 137**: `TrampolineFlowCombinators.check_should_exit` method
- **Commit 138**: `TrampolineFlowCombinators.check_should_break` method
- **Commit 139**: `TrampolineFlowCombinators.check_should_skip` method
- **Commit 140**: `TrampolineFlowCombinators.clear_break_flag` method
- **Commit 141**: `TrampolineFlowCombinators.clear_skip_flag` method
- **Commit 142**: `TrampolineFlowCombinators.exitable_chain` method
- **Commit 143**: `TrampolineFlowCombinators.trampoline` method
- **Commit 144**: `TrampolineFlowCombinators.trampoline_chain` method
- **Commit 145**: `TrampolineFlowCombinators.conditional_flow` method
- **Commit 146**: `TrampolineFlowCombinators.skip_if` method

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
