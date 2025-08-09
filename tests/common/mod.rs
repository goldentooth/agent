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
    /// Returns None if MCP server binary is not available (e.g., in CI)
    pub async fn setup() -> Result<Option<Self>, Box<dyn std::error::Error>> {
        init_test_logging();

        // Build the MCP server first
        let Some(server_path) = get_or_build_mcp_server().await? else {
            return Ok(None);
        };

        // Create both transports
        let stdio_transport = StdioTransport::goldentooth_server(&server_path);
        let http_transport = HttpTransport::goldentooth_server("http://localhost:8080");

        Ok(Some(Self {
            stdio_transport,
            http_transport,
            server_path,
        }))
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

/// Get the path to the MCP server binary from GitHub releases or build locally
/// Returns None if running in CI environment without binary access
pub async fn get_or_build_mcp_server() -> Result<Option<PathBuf>, Box<dyn std::error::Error>> {
    let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let cache_dir = project_root.join("target").join("test-binaries");

    // Create cache directory if it doesn't exist
    tokio::fs::create_dir_all(&cache_dir).await?;

    let binary_path = cache_dir.join("goldentooth-mcp");

    // Check if we already have the binary cached
    if binary_path.exists() {
        return Ok(Some(binary_path));
    }

    // Detect the current platform
    let os = std::env::consts::OS;
    let arch = std::env::consts::ARCH;

    let binary_name = match (os, arch) {
        ("linux", "x86_64") => "goldentooth-mcp-x86_64-linux",
        ("linux", "aarch64") => "goldentooth-mcp-aarch64-linux",
        ("macos", _) => {
            // macOS binaries aren't available in releases, build locally instead
            let built_binary = build_local_mcp_server().await?;
            return Ok(Some(built_binary));
        }
        _ => {
            // In unsupported environments (like CI), gracefully skip tests
            log::warn!(
                "Unsupported platform for MCP server download: {os}-{arch}, skipping binary-dependent tests"
            );
            return Ok(None);
        }
    };

    // Download the latest release
    let release_url =
        format!("https://github.com/goldentooth/mcp-server/releases/latest/download/{binary_name}");

    // Create client with explicit security settings
    let client = reqwest::Client::builder()
        .https_only(true)
        .timeout(std::time::Duration::from_secs(30))
        .build()?;
    let response = client.get(&release_url).send().await?;

    if !response.status().is_success() {
        log::warn!(
            "Failed to download MCP server binary: HTTP {} - {}, skipping binary-dependent tests",
            response.status(),
            response
                .status()
                .canonical_reason()
                .unwrap_or("Unknown error")
        );
        return Ok(None);
    }

    let binary_content = response.bytes().await?;

    // Write the binary to disk
    tokio::fs::write(&binary_path, &binary_content).await?;

    // Make it executable on Unix systems
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut permissions = tokio::fs::metadata(&binary_path).await?.permissions();
        permissions.set_mode(0o755);
        tokio::fs::set_permissions(&binary_path, permissions).await?;
    }

    Ok(Some(binary_path))
}

/// Build MCP server locally from git (fallback for platforms without pre-built binaries)
pub async fn build_local_mcp_server() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let cache_dir = project_root.join("target").join("test-binaries");

    tokio::fs::create_dir_all(&cache_dir).await?;

    let binary_path = cache_dir.join("goldentooth-mcp-local");

    // Check if we already built it
    if binary_path.exists() {
        return Ok(binary_path);
    }

    let temp_dir = cache_dir.join("mcp-server-build");

    // Clean up any existing temp directory
    if temp_dir.exists() {
        tokio::fs::remove_dir_all(&temp_dir).await?;
    }

    // Clone the repository
    let clone_output = tokio::process::Command::new("git")
        .args(["clone", "https://github.com/goldentooth/mcp-server.git"])
        .arg(&temp_dir)
        .output()
        .await?;

    if !clone_output.status.success() {
        let stderr = String::from_utf8_lossy(&clone_output.stderr);
        return Err(format!("Failed to clone MCP server repository: {stderr}").into());
    }

    // Build the binary
    let build_output = tokio::process::Command::new("cargo")
        .args(["build", "--release"])
        .current_dir(&temp_dir)
        .output()
        .await?;

    if !build_output.status.success() {
        let stderr = String::from_utf8_lossy(&build_output.stderr);
        return Err(format!("Failed to build MCP server: {stderr}").into());
    }

    // Copy the built binary to our cache
    let built_binary = temp_dir
        .join("target")
        .join("release")
        .join("goldentooth-mcp");
    if !built_binary.exists() {
        return Err("Built binary not found".into());
    }

    tokio::fs::copy(&built_binary, &binary_path).await?;

    // Clean up temp directory
    tokio::fs::remove_dir_all(&temp_dir).await?;

    Ok(binary_path)
}

// Macro removed for now - not used yet
