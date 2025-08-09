# Goldentooth Agent MCP Client Requirements

## Project Overview

The Goldentooth Agent is an intelligent agent designed to communicate with MCP (Model Context Protocol) servers, with a primary focus on integration with the Goldentooth cluster MCP server. The agent must support both stdio and HTTP transports seamlessly for maximum flexibility and testability.

## Core Requirements

### 1. MCP Client Implementation

The agent MUST implement a complete MCP client that:
- Supports both stdio and HTTP with Server-Sent Events (SSE) transports
- Provides identical functionality across both transport modes
- Implements the full MCP protocol specification (version 2025-06-18)
- Handles JSON-RPC 2.0 message format correctly
- Supports dynamic capability discovery and negotiation

### 2. Transport Requirements

#### Dual Transport Support
Both transports MUST be:
- **Fully functional**: No transport-specific limitations
- **Equally testable**: Testing frameworks for both modes
- **Production-ready**: Robust error handling and connection management
- **Authentication-capable**: OAuth 2.1 support where required

#### stdio Transport Specifications
- Launch MCP server as subprocess
- Communicate via stdin/stdout with newline-delimited JSON
- Handle server stderr output (logging, diagnostics)
- Process lifecycle management (start, monitor, cleanup)
- Error handling for process failures

#### HTTP Transport Specifications
- HTTP POST for message transmission to `/mcp` endpoint
- GET with SSE for receiving server messages
- Required headers: `Accept: application/json, text/event-stream`
- Session management via `Mcp-Session-Id` header
- Origin validation and DNS rebinding protection
- Connection resumability using event IDs

### 3. Authentication and Security

#### OAuth 2.1 Integration
- Full OAuth 2.1 client implementation
- PKCE (Proof Key for Code Exchange) support for public clients
- Authorization server discovery and metadata handling
- Secure token storage and automatic renewal
- Resource Indicators (RFC 8707) support

#### Security Requirements
- HTTPS enforcement for all authorization endpoints
- Bearer token handling in Authorization headers
- Origin header validation for HTTP transport
- Cryptographically secure session ID generation
- No tokens in URI query strings

### 4. Connection Lifecycle Management

#### State Management
- Connection state tracking (Disconnected, Connecting, Initialized, Ready, Closing, Closed, Error)
- Graceful connection establishment and teardown
- Automatic reconnection with exponential backoff
- Pending request management across reconnections

#### Message Processing
- Asynchronous request/response correlation
- Notification handling (one-way messages)
- Message queuing during connection interruptions
- Proper JSON-RPC 2.0 error responses

### 5. Error Handling and Resilience

#### Comprehensive Error Handling
- JSON-RPC standard error codes (-32700 to -32603)
- MCP-specific error codes (-32000 and above)
- Transport-specific error handling
- Authentication error recovery

#### Fault Tolerance
- Connection retry logic with backoff
- Timeout management for all operations
- Resource cleanup on failures
- Graceful degradation when servers unavailable

### 6. Development and Testing Requirements

#### Testing Framework
- Unit tests for all transport modes
- Integration tests with mock MCP servers
- Authentication flow testing
- Error condition and recovery testing
- Performance testing under load

#### Development Tools
- Hot-reload development mode
- Comprehensive logging to stderr
- Configuration management
- Debug modes for protocol inspection

## Goldentooth-Specific Integration

### Cluster MCP Server Communication
The agent MUST efficiently communicate with the Goldentooth MCP server tools:
- `cluster_ping`: Node connectivity testing
- `cluster_status`: Health monitoring via node_exporter
- `service_status`: systemd service monitoring
- `resource_usage`: CPU, memory, disk utilization
- `cluster_info`: Comprehensive cluster state
- `shell_command`: Remote command execution
- `journald_logs`: systemd journal aggregation
- `loki_logs`: LogQL querying
- `screenshot_url`: Webpage capture
- `screenshot_dashboard`: Dashboard capture

### Authentication Context
- Integration with Goldentooth cluster PKI
- SSH certificate handling
- Consul/Vault integration for secrets
- Step-CA certificate management

### Operational Context
- Support for 12 Raspberry Pi nodes + 1 GPU node
- Kubernetes and HashiCorp stack integration
- Prometheus metrics and Grafana dashboard access
- Distributed storage and service mesh awareness

## Technical Architecture

### Language and Framework
- **Rust 2024 edition**: Type safety, performance, async support
- **Tokio runtime**: Full async/await with all features enabled
- **Hyper/Reqwest**: HTTP client with rustls-tls
- **Serde**: JSON serialization/deserialization
- **OAuth2 crate**: Authentication implementation
- **Thiserror**: Structured error handling

### Module Structure
```
src/
├── mcp/           # Core MCP client implementation
│   ├── client.rs  # Main MCP client
│   ├── transport/ # Transport layer implementations
│   ├── auth/      # OAuth 2.1 authentication
│   └── protocol/  # JSON-RPC and MCP protocol handling
├── goldentooth/   # Goldentooth-specific integrations
│   ├── cluster.rs # Cluster management operations
│   └── tools.rs   # Tool invocation helpers
├── config/        # Configuration management
├── logging/       # Structured logging (stderr only)
└── error/         # Error types and handling
```

## Non-Functional Requirements

### Performance
- **Latency**: <100ms for typical cluster operations
- **Throughput**: Handle multiple concurrent requests
- **Resource Usage**: Efficient on Raspberry Pi hardware
- **Scalability**: Support for cluster growth

### Reliability
- **Uptime**: Graceful handling of network partitions
- **Data Integrity**: Consistent state across reconnections
- **Fault Recovery**: Automatic recovery from transient failures
- **Monitoring**: Health check endpoints and metrics

### Maintainability
- **Modularity**: Clear separation of concerns
- **Documentation**: Comprehensive API documentation
- **Testability**: High test coverage across all modules
- **Debugging**: Rich logging and error context

### Security
- **Authentication**: Secure token handling and renewal
- **Authorization**: Proper scope validation
- **Transport Security**: TLS for all external communications
- **Input Validation**: Sanitization of all external inputs

## Future Extensibility

### Plugin Architecture
- Modular tool implementations
- Configuration-driven server registration
- Dynamic capability registration
- Runtime plugin loading

### Monitoring Integration
- Prometheus metrics export
- Distributed tracing support
- Performance monitoring
- Audit logging capabilities

### Multi-Server Support
- Connection pooling for multiple MCP servers
- Load balancing and failover
- Server capability aggregation
- Unified authentication across servers

## Success Criteria

### Core Functionality
- [ ] stdio transport works with Goldentooth MCP server
- [ ] HTTP transport works with Goldentooth MCP server
- [ ] All cluster management tools accessible via both transports
- [ ] Authentication flows work end-to-end
- [ ] Error handling provides meaningful diagnostics

### Testing Validation
- [ ] 100% transport parity in test suite
- [ ] Integration tests pass with real MCP server
- [ ] Authentication flows validated
- [ ] Performance benchmarks meet requirements
- [ ] Error conditions properly handled

### Production Readiness
- [ ] Configuration management working
- [ ] Logging provides operational visibility
- [ ] Monitoring and health checks functional
- [ ] Documentation complete and accurate
- [ ] Security review passed

This comprehensive requirements document ensures the Goldentooth Agent will be a robust, secure, and fully-featured MCP client capable of efficient cluster management operations.
