# Background Documentation Guidelines

## Overview

Background documentation (`README.bg.md`) provides in-depth context about a module's motivation, theoretical foundations, and design decisions. This information is automatically integrated into the generated `README.md` files.

## When to Create Background Files

Background files should be created for **significant modules** that meet any of these criteria:

- **High/Critical complexity** modules
- Modules with **5+ Python files**
- Modules with **3+ classes**
- Modules with **20+ functions**

### Examples of Modules Requiring Background Files

✅ **Complex algorithmic modules**: Embeddings, search engines, flow composition
✅ **Core architectural components**: Context management, dependency injection
✅ **Domain-specific logic**: RAG systems, document processing, LLM integration
✅ **Performance-critical modules**: Vector storage, caching systems

### Examples of Modules Not Requiring Background Files

❌ **Simple utility modules**: Path helpers, basic string operations
❌ **Configuration modules**: Settings, constants
❌ **Thin wrapper modules**: Simple API clients, basic data models

## When to Update Background Files

Update `README.bg.md` files when:

### 🔄 **Major Changes Required**
- **Architectural changes**: New design patterns, restructured classes
- **Algorithm changes**: Different approaches, new theoretical foundations
- **Purpose evolution**: Module scope expands or contracts significantly
- **New dependencies**: Integration with different systems or libraries

### 🔄 **Content Updates Recommended**
- **Performance optimizations**: New strategies for efficiency
- **Security enhancements**: New threat models or mitigation strategies
- **Integration patterns**: How the module connects with other components
- **Lessons learned**: Post-implementation insights about design decisions

### ✅ **Minor Changes (No Update Needed)**
- Bug fixes that don't change approach
- Code style improvements
- Minor refactoring without architectural impact
- Adding simple helper methods

## Content Structure

### Required Sections

#### 1. **Background & Motivation**
```markdown
## Background & Motivation

### Problem Statement
What specific problem does this module solve? Why does it exist?

### Theoretical Foundation
What concepts, algorithms, or design patterns are used?
```

#### 2. **Design Philosophy**
```markdown
### Design Philosophy

#### Core Concepts
Key abstractions and their relationships

#### Architecture Decisions
Major design choices and their rationale
```

#### 3. **Technical Challenges**
```markdown
### Technical Challenges Addressed

1. **Challenge Name**: Description and solution approach
2. **Performance**: How efficiency concerns are handled
3. **Scalability**: How the module handles growth
```

### Optional Sections

#### **Integration Patterns**
How the module fits into the larger system

#### **Future Considerations**
Known limitations, planned improvements, technical debt

#### **References**
Academic papers, design documents, or external resources

## Quality Standards

### ✅ **Good Background Documentation**
- **Explains the "why"**, not just the "what"
- **Provides context** for design decisions
- **Describes tradeoffs** and alternatives considered
- **Uses clear examples** and analogies
- **Focuses on concepts** over implementation details

### ❌ **Poor Background Documentation**
- Repeats information already in docstrings
- Lists features without explaining motivation
- Too technical without conceptual framework
- Outdated information that doesn't match current implementation

## Maintenance Workflow

### 1. **Pre-commit Check**
The pre-commit hook will warn if significant modules lack background files:
```bash
poetry run goldentooth-agent dev module check-background-for-commit
```

### 2. **Creating Background Files**
```bash
# Generate a template
poetry run goldentooth-agent dev module generate-background src/my_module

# Check which modules need background files
poetry run goldentooth-agent dev module check-background
```

### 3. **Integration**
Background content is automatically integrated when generating README files:
```bash
poetry run goldentooth-agent dev module generate-readme src/my_module
```

## Examples

### Excellent Background Documentation
See `src/goldentooth_agent/core/embeddings/README.bg.md` for an example that:
- Explains the information retrieval problem
- Describes vector embedding theory
- Details hybrid search strategy
- Addresses technical challenges
- Shows integration with RAG pipeline

### Template Structure
```markdown
## Background & Motivation

### Problem Statement
[Clear description of the problem being solved]

### Theoretical Foundation
#### Core Concepts
[Key algorithms, patterns, or theories]

### Design Philosophy
#### Architecture Decisions
[Major design choices and rationale]

### Technical Challenges Addressed
1. **Challenge**: [Solution approach]

### Integration & Usage
[How it fits into the larger system]
```

## Best Practices

1. **Write for your future self** - explain decisions you might forget
2. **Include alternatives considered** - why this approach over others
3. **Reference external sources** - papers, RFCs, design documents
4. **Update when assumptions change** - keep information current
5. **Use diagrams sparingly** - focus on conceptual understanding
6. **Test your explanations** - would a new team member understand?

## Automation

The system provides several automation features:

- **Pre-commit warnings** for missing background files
- **Template generation** for consistent structure
- **Automatic integration** into README.md files
- **Freshness checking** to identify outdated documentation

This ensures background documentation stays current and valuable for the development team.
