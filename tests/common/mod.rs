//! Common test utilities and setup

#![allow(dead_code)]

use goldentooth_agent::mcp::transport::{HttpTransport, StdioTransport, Transport};
use std::path::PathBuf;
use std::sync::Once;

static INIT: Once = Once::new();

/// Initialize logging for tests (only once)
pub fn init_test_logging() {
    INIT.call_once(|| {
        let _ = goldentooth_agent::logging::init_with_level(log::LevelFilter::Debug);
    });
}

/// Test environment that manages both stdio and HTTP transports
pub struct TestEnvironment {
    pub stdio_transport: StdioTransport,
    pub http_transport: HttpTransport,
    server_path: PathBuf,
}

impl TestEnvironment {
    /// Set up test environment with both transports
    pub fn setup() -> Self {
        init_test_logging();

        // Get the MCP server path (binary should be installed by CI workflow)
        let server_path = get_mcp_server_path();

        // Create both transports
        let stdio_transport = StdioTransport::goldentooth_server(&server_path);
        let http_transport = HttpTransport::goldentooth_server("http://localhost:8080");

        Self {
            stdio_transport,
            http_transport,
            server_path,
        }
    }

    /// Get the path to the built MCP server
    pub fn server_path(&self) -> &PathBuf {
        &self.server_path
    }

    /// Clean up test environment
    pub async fn cleanup(mut self) {
        let _ = self.stdio_transport.close().await;
        let _ = self.http_transport.close().await;
    }
}

/// Get the path to the MCP server binary
/// Assumes binary has been installed at target/test-binaries/goldentooth-mcp by CI workflow
pub fn get_mcp_server_path() -> PathBuf {
    let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    project_root
        .join("target")
        .join("test-binaries")
        .join("goldentooth-mcp")
}

// Macro removed for now - not used yet
