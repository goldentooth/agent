# Authentication Flow

Simple authentication patterns for Goldentooth cluster access.

## Overview

The Goldentooth agent uses SSH key-based authentication to connect to cluster nodes. This document outlines the authentication flow and security considerations for the rebuilt agent.

## Authentication Methods

### 1. SSH Key Authentication (Primary)

**Recommended for production and development.**

```rust
// Simple SSH client configuration
struct ClusterConfig {
    nodes: Vec<NodeConfig>,
    ssh_key_path: PathBuf,
    ssh_user: String,
}

struct NodeConfig {
    hostname: String,
    port: u16,
}
```

**Setup:**
```bash
# Copy your SSH key to all cluster nodes
ssh-copy-id pi@allyrion.goldentooth.net
ssh-copy-id pi@jast.goldentooth.net
# ... for all 13 nodes
```

**Usage:**
```rust
// Agent automatically uses SSH key from ~/.ssh/id_rsa
let client = ClusterClient::new(ClusterConfig::from_env())?;
let result = client.execute_command("allyrion", "uptime").await?;
```

### 2. SSH Agent Integration

**For development environments with SSH agent.**

```bash
# Start SSH agent and add key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/goldentooth_key

# Agent will use SSH agent automatically
cargo run -- ping allyrion
```

### 3. Configuration File Authentication

**For multiple key scenarios or custom configurations.**

```toml
# ~/.config/goldentooth/agent.toml
[cluster]
ssh_user = "pi"
ssh_key_path = "~/.ssh/goldentooth_rsa"

[[cluster.nodes]]
name = "allyrion"
hostname = "allyrion.goldentooth.net"
port = 22

[[cluster.nodes]]
name = "jast"
hostname = "jast.goldentooth.net"
port = 22
```

## Security Considerations

### SSH Key Management

1. **Use dedicated SSH keys** for cluster access
2. **Set appropriate permissions**: `chmod 600 ~/.ssh/goldentooth_key`
3. **Use SSH agent** for key loading in development
4. **Rotate keys regularly** (every 90 days recommended)

### Network Security

1. **Use SSH host key verification** to prevent MITM attacks
2. **Configure SSH timeouts** to prevent hanging connections
3. **Use SSH connection multiplexing** for performance
4. **Implement connection pooling** for frequent operations

### Error Handling

```rust
#[derive(thiserror::Error, Debug)]
pub enum AuthError {
    #[error("SSH key not found at path: {path}")]
    KeyNotFound { path: String },

    #[error("SSH authentication failed for {user}@{host}")]
    AuthenticationFailed { user: String, host: String },

    #[error("SSH connection timeout to {host}")]
    ConnectionTimeout { host: String },

    #[error("SSH permission denied for {user}@{host}")]
    PermissionDenied { user: String, host: String },
}
```

## Implementation Guidelines

### Phase 1: Basic SSH Authentication

**Week 1 Priority:** Get basic SSH working to one node.

```rust
// Minimal working SSH client
pub struct SimpleSSHClient {
    config: ClusterConfig,
}

impl SimpleSSHClient {
    pub async fn execute(&self, node: &str, command: &str) -> Result<String, AuthError> {
        // Use openssh or similar for simple SSH execution
        // No complex abstractions initially
    }
}
```

### Phase 2: Multi-Node Support

**Week 2-3:** Extend to all 13 nodes with proper error handling.

```rust
pub async fn execute_on_nodes(&self, nodes: &[&str], command: &str) -> Vec<NodeResult> {
    // Parallel execution across multiple nodes
    // Proper error collection and reporting
}
```

### Phase 3: Advanced Features

**Week 4+:** Only after basic functionality proven useful.

- SSH connection pooling
- Automatic retry with backoff
- SSH tunnel support for services
- Certificate-based authentication via step-ca

## Testing Strategy

### Unit Tests
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_ssh_connection_to_allyrion() {
        let client = SimpleSSHClient::new(test_config());
        let result = client.execute("allyrion", "echo 'test'").await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap().trim(), "test");
    }
}
```

### Integration Tests
```rust
#[tokio::test]
async fn test_goldentooth_cli_integration() {
    // Test actual goldentooth CLI command execution
    let result = execute_goldentooth_command(&["ping", "allyrion"]).await;
    assert!(result.contains("reachable"));
}
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Check SSH key permissions and authorized_keys
2. **Connection timeout**: Verify network connectivity and SSH daemon status
3. **Host key verification failed**: Update known_hosts or disable strict checking for development
4. **Agent not found**: Ensure SSH agent is running and key is added

### Debug Commands

```bash
# Test SSH connectivity manually
ssh -v pi@allyrion.goldentooth.net "echo 'connected'"

# Check SSH agent
ssh-add -l

# Test goldentooth CLI
goldentooth ping allyrion

# Agent debug mode
RUST_LOG=debug cargo run -- ping allyrion
```

## Migration from Current Implementation

When rebuilding from scratch, **do not** port over the complex tool abstraction layer. Instead:

1. Start with direct SSH execution using `std::process::Command`
2. Add proper error handling from day 1
3. Use existing `goldentooth` CLI where possible
4. Build abstractions only after proving basic functionality works

The current implementation's tool registry and complex command abstractions should be **deleted entirely** in favor of simple, direct SSH execution that can be incrementally improved.
