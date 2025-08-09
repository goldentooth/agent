//! Error types for the Goldentooth Agent

use thiserror::Error;

/// Main error type for the Goldentooth Agent
#[derive(Error, Debug)]
pub enum Error {
    /// JSON-RPC protocol errors
    #[error("JSON-RPC error: {code} - {message}")]
    JsonRpc {
        code: i32,
        message: String,
        data: Option<serde_json::Value>,
    },

    /// Transport layer errors
    #[error("Transport error: {0}")]
    Transport(#[from] TransportError),

    /// MCP protocol errors
    #[error("MCP protocol error: {0}")]
    Protocol(String),

    /// Authentication errors
    #[error("Authentication error: {0}")]
    Auth(String),

    /// Configuration errors
    #[error("Configuration error: {0}")]
    Config(String),

    /// I/O errors
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    /// JSON serialization/deserialization errors
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    /// HTTP client errors
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),

    /// Generic error with context
    #[error("{context}: {source}")]
    Context {
        context: String,
        source: Box<dyn std::error::Error + Send + Sync>,
    },
}

/// Transport-specific error types
#[derive(Error, Debug)]
pub enum TransportError {
    /// Connection failed
    #[error("Connection failed: {0}")]
    ConnectionFailed(String),

    /// Connection closed unexpectedly
    #[error("Connection closed")]
    ConnectionClosed,

    /// Process spawn failed (stdio transport)
    #[error("Process spawn failed: {0}")]
    ProcessSpawnFailed(std::io::Error),

    /// Process exited with error (stdio transport)
    #[error("Process exited with code {code}")]
    ProcessExited { code: i32 },

    /// HTTP transport specific errors
    #[error("HTTP error: {0}")]
    Http(reqwest::Error),

    /// Timeout error
    #[error("Operation timed out")]
    Timeout,
}

/// Convenient result type
pub type Result<T> = std::result::Result<T, Error>;

impl Error {
    /// Create a new error with additional context
    #[must_use]
    pub fn with_context<C: Into<String>>(self, context: C) -> Self {
        Error::Context {
            context: context.into(),
            source: Box::new(self),
        }
    }

    /// Create a JSON-RPC error
    pub fn json_rpc(code: i32, message: impl Into<String>) -> Self {
        Error::JsonRpc {
            code,
            message: message.into(),
            data: None,
        }
    }

    /// Create a JSON-RPC error with additional data
    pub fn json_rpc_with_data(
        code: i32,
        message: impl Into<String>,
        data: serde_json::Value,
    ) -> Self {
        Error::JsonRpc {
            code,
            message: message.into(),
            data: Some(data),
        }
    }
}
