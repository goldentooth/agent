# 🤖 Goldentooth Agent

An intelligent agent built for my [Pi Bramble](https://github.com/goldentooth/).

## 🎯 Overview

Goldentooth Agent is an **AI agent** that combines functional reactive programming with enterprise-grade features. Built on three core abstractions—**Flow**, **Context**, and **FlowAgent**—it provides type-safe, composable, and highly performant agent development with comprehensive security and tooling.

The system emphasizes **type safety**, **performance**, **security**, and **developer experience** while providing sophisticated features like reactive state management, intelligent caching, rate limiting, and comprehensive observability.

## 🚀 Current Status

**Flow Engine Migration: Epic 13 Complete ✅**

The Flow Engine migration is progressing steadily with comprehensive type safety and test coverage:

### Completed Epics
- ✅ **Epic 1-4**: Core infrastructure (package structure, exceptions, protocols, Flow class)
- ✅ **Epic 5-8**: Basic combinators (utils, sources, basic operations, __init__)
- ✅ **Epic 9**: Aggregation combinators (11 functions including buffer_stream, expand_stream, finalize_stream)
- ✅ **Epic 10**: Temporal combinators (6 functions for time-based operations)
- ✅ **Epic 11**: Observability combinators (5 functions + 3 notification classes for monitoring and tracing)
- ✅ **Epic 12**: Control flow combinators (11 functions for conditional processing, error handling, and flow control)
- ✅ **Epic 13**: Advanced combinators (10 functions including race_stream, parallel_stream, merge_stream, zip_stream)

### Migration Progress
- **13/40 Epics Complete** (32.5% overall progress)
- **~2,650 lines migrated** with 96%+ test coverage
- **100% type safety** - Full Pyright/MyPy compliance
- **Zero dependencies** - Standalone package architecture

### Architecture Status

- 🔄 **Flow Engine** (`flowengine`) - Core + basic + aggregation + temporal + observability + control flow + advanced combinators complete
- 📋 **Legacy System** (`old/`) - Original 25K+ LOC implementation (reference)
- 🏗️ **Migration Tools** (`src/git_hooks/`) - File/module validators and development tooling
- 🧪 **Test Infrastructure** - Comprehensive testing with pytest, coverage, and type checking

## 🌀 Wilder Ideas

Goldentooth Agent is a modular, persona-driven intelligent agent architecture designed to orchestrate and evolve distributed compute systems, narrative metaphors, and symbolic reasoning on a self-hosted Raspberry Pi cluster named Goldentooth. The cluster consists of 12 Raspberry Pi 4B nodes (Allyrion through Lipps), running Kubernetes, Nomad, Vault, Consul, Prometheus, real-time observability, ML workflows, and simulation-based jobs.

The Agent operates as an extensible, runtime-modifiable DAG of flows—reactive, composable logic primitives. It integrates numerous tools (e.g. REST, shell, file search), distinct personas, and behavior orchestrators (e.g. trampoline, rule engine, middleware pipelines). Agents can instantiate sub-agents, alter behavior through context-aware masks, and simulate dramatic or symbolic interactions (e.g. the customary assistant persona being “kidnapped” by another scheming persona). Prompt configuration is modular and writable at runtime, enabling recursive, evolving behavior.

The Agent’s narrative frame draws from Greek drama, Gormenghast, Edward Gorey, and ASOIAF heraldry, blending operational infrastructure with symbolic intelligence. It is capable of governing the Goldentooth cluster through declarative introspection, gossip CRDTs, Prometheus metrics, and service auto-discovery. The long-term goal is to blur the boundary between orchestration, narrative embodiment, and emergent symbolic computation—building a live actor-model-inspired system that is self-reflective, chaotic, aesthetic, and computationally useful. Subsystems like [Pulse](https://github.com/goldentooth/pulse/) (latency visualization), [Whispers](https://github.com/bitterbridge/whispers/) (CRDT state propagation), and Goldengrove (GPU-accelerated simulation architecture) form testbeds for this vision.

In sum: Goldentooth Agent is a programmable intelligence housed in a self-referential, story-aware cluster, designed to evolve both behavior and symbolic form while orchestrating real distributed infrastructure.

## 📄 License

This project is released into the public domain under the Unlicense - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds upon excellent work from the Python ecosystem:

- **[Anthropic](https://github.com/anthropics/anthropic-sdk-python)**: Claude AI integration
- **[Pydantic](https://github.com/pydantic/pydantic)**: Schema validation and serialization
- **[Antidote](https://github.com/Finistere/antidote)**: Dependency injection framework
- **[Typer](https://github.com/tiangolo/typer)**: CLI framework
- **[Instructor](https://github.com/jxnl/instructor)**: Structured LLM output processing
- **[Cryptography](https://github.com/pyca/cryptography)**: Secure encryption and key management
