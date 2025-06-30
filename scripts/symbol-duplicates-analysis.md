# Symbol Uniqueness Analysis for Goldentooth Agent

## Summary

- Total duplicate symbols: 1,167
- Type variables: 8 (OK to duplicate)
- Common methods: 27 (OK in different contexts)
- Example symbols: 81 (OK - isolated to examples/)
- Test symbols: 179 (OK - isolated to tests/)
- Helper functions: 45 (Mostly OK)
- **Actual duplicates needing investigation: 827**

## Categories

### 1. Type Variables (8 symbols) - **Probably OK**
Generic type parameters like `T`, `K`, `V`, `Input`, `Output`, etc. These are commonly reused across different modules and are expected to be duplicated.

### 2. Common Methods (27 symbols) - **Probably OK**
Standard method names like `__init__`, `run`, `process`, `get`, `set`, etc. These are interface methods that naturally appear in multiple classes.

### 3. Example Code (81 symbols) - **Probably OK**
Symbols that only appear in the `examples/` directory. These are isolated demonstration code and don't affect the main codebase.

### 4. Test Code (179 symbols) - **Probably OK**
Symbols that only appear in `tests/` directories. Test fixtures, mocks, and test functions are expected to have some duplication.

### 5. Helper Functions (45 symbols) - **Mostly OK**
Private functions (starting with `_`) and common helper patterns. Many of these are implementation details that can reasonably be duplicated.

### 6. Actual Duplicates (827 symbols) - **Need Investigation**

Key problematic duplicates that should be addressed:

#### High-Priority Duplicates (appear in main codebase):
- **APP_NAME**, **APP_AUTHOR**: Duplicated between `src/.../paths/main.py` and `old/.../path/main.py`
- **AgentRegistry**: In both CLI commands and old registry module
- **AnyFlow**, **AnyInput**, **AnyValue**: Type aliases duplicated across multiple modules
- **Context**: Core class duplicated between current and old code
- **Flow**: Core abstraction duplicated in multiple places
- **BaseAgent**, **FlowAgent**: Agent classes duplicated
- **SearchResult**, **DocumentChunk**: Data models duplicated
- Many service classes: **EmbeddingsService**, **VectorStore**, **DocumentStore**, etc.

#### Patterns of Duplication:
1. **Old vs New Code**: Many duplicates exist between `src/` and `old/` directories
2. **Test Fixtures**: Extensive duplication in test helper code
3. **Flow Engine Types**: Many type aliases (`FlowFunc`, `StreamFunc`, etc.) duplicated
4. **Atomic Agents**: Significant duplication in the old atomic-agents subdirectory

## Recommendations

### Immediate Actions:
1. **Remove or clearly mark the `old/` directory** - This contains many duplicates of current code
2. **Consolidate type aliases** - Create a central `types.py` module for shared type definitions
3. **Extract common test fixtures** - Create shared test utilities module

### Medium-term Actions:
1. **Review flow engine types** - Many similar type definitions could be consolidated
2. **Standardize service interfaces** - Similar patterns in embeddings, vector store, etc.
3. **Clean up examples** - Some example code could be refactored to reduce duplication

### Low Priority:
1. Generic type variables (T, K, V) - These are fine to duplicate
2. Common method names - Expected in OOP design
3. Test-specific helpers - Acceptable duplication in test code

## Most Concerning Duplicates

These require immediate attention as they may cause confusion or bugs:

1. **Core Classes**: `Context`, `Flow`, `BaseAgent` duplicated between old and new
2. **Configuration**: `APP_NAME`, `APP_AUTHOR` in different paths modules
3. **Type Definitions**: `AnyFlow`, `FlowFunc`, etc. scattered across modules
4. **Service Classes**: Multiple versions of embeddings, vector stores, etc.
5. **Registry Classes**: `AgentRegistry`, `FlowRegistry` in multiple locations
