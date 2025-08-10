//! Transport layer for MCP communication
//!
//! Provides both stdio and HTTP transports with identical interfaces.

use crate::error::{Error, Result, TransportError};
use crate::mcp::protocol::{JsonRpcMessage, JsonRpcRequest, JsonRpcResponse, RequestId};
use async_trait::async_trait;
use log::{debug, error, info, warn};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{Mutex, oneshot};
use tokio_stream::StreamExt;

/// Transport trait that both stdio and HTTP transports implement
#[async_trait]
pub trait Transport: Send + Sync {
    /// Start the transport (establish connection, spawn process, etc.)
    async fn start(&mut self) -> Result<()>;

    /// Send a JSON-RPC request and wait for response
    async fn send_request(&self, request: JsonRpcRequest) -> Result<JsonRpcResponse>;

    /// Send a JSON-RPC notification (no response expected)
    async fn send_notification(
        &self,
        notification: crate::mcp::protocol::JsonRpcNotification,
    ) -> Result<()>;

    /// Close the transport connection
    async fn close(&mut self) -> Result<()>;

    /// Check if the transport is connected
    fn is_connected(&self) -> bool;
}

/// stdio transport implementation
pub struct StdioTransport {
    process_command: Vec<String>,
    process: Option<tokio::process::Child>,
    stdin: Option<Arc<Mutex<tokio::process::ChildStdin>>>,
    pending_requests: Arc<Mutex<HashMap<RequestId, oneshot::Sender<JsonRpcResponse>>>>,
    _message_handler: Option<tokio::task::JoinHandle<()>>,
    connected: bool,
}

impl StdioTransport {
    /// Create a new stdio transport with the command to run the MCP server
    #[must_use]
    pub fn new(command: Vec<String>) -> Self {
        Self {
            process_command: command,
            process: None,
            stdin: None,
            pending_requests: Arc::new(Mutex::new(HashMap::new())),
            _message_handler: None,
            connected: false,
        }
    }

    /// Create stdio transport for the Goldentooth MCP server
    pub fn goldentooth_server(server_path: impl Into<std::path::PathBuf>) -> Self {
        let server_path = server_path.into();
        Self::new(vec![server_path.to_string_lossy().to_string()])
    }
}

#[async_trait]
impl Transport for StdioTransport {
    async fn start(&mut self) -> Result<()> {
        info!(
            "Starting stdio transport with command: {:?}",
            self.process_command
        );

        if self.process_command.is_empty() {
            return Err(Error::Transport(TransportError::ProcessSpawnFailed(
                std::io::Error::new(std::io::ErrorKind::InvalidInput, "Empty command"),
            )));
        }

        let mut cmd = tokio::process::Command::new(&self.process_command[0]);
        if self.process_command.len() > 1 {
            cmd.args(&self.process_command[1..]);
        }

        cmd.stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::null()) // Discard all stderr output to prevent logging interference
            .env("RUST_LOG", "off") // Disable Rust logging
            .env("LOG_LEVEL", "OFF") // Disable other logging
            .env("GOLDENTOOTH_LOG_LEVEL", "OFF") // Disable Goldentooth-specific logging
            .env("MCP_LOG_LEVEL", "OFF") // Disable MCP-specific logging
            .env("SILENT", "1") // Request silent mode
            .env("QUIET", "1"); // Request quiet mode

        let mut child = cmd.spawn().map_err(TransportError::ProcessSpawnFailed)?;

        let stdin = child.stdin.take().ok_or_else(|| {
            Error::Transport(TransportError::ProcessSpawnFailed(std::io::Error::new(
                std::io::ErrorKind::Other,
                "Failed to get stdin",
            )))
        })?;
        let stdin = Arc::new(Mutex::new(stdin));

        let stdout = child.stdout.take().ok_or_else(|| {
            Error::Transport(TransportError::ProcessSpawnFailed(std::io::Error::new(
                std::io::ErrorKind::Other,
                "Failed to get stdout",
            )))
        })?;

        // Spawn task to handle incoming messages from stdout
        let pending_requests = Arc::clone(&self.pending_requests);
        let message_handler = tokio::spawn(async move {
            use tokio::io::{AsyncBufReadExt, BufReader};
            let reader = BufReader::new(stdout);
            let mut lines = reader.lines();

            while let Ok(Some(line)) = lines.next_line().await {
                debug!("Received message: {line}");

                // Skip lines that don't look like JSON-RPC (filter out log messages)
                if !line.trim().starts_with('{') {
                    debug!("Skipping non-JSON line: {line}");
                    continue;
                }

                match serde_json::from_str::<JsonRpcMessage>(&line) {
                    Ok(JsonRpcMessage::Response(response)) => {
                        // Handle response by notifying waiting request
                        let mut pending = pending_requests.lock().await;
                        if let Some(sender) = pending.remove(&response.id) {
                            if sender.send(response).is_err() {
                                warn!("Failed to send response to waiting request");
                            }
                        } else {
                            warn!("Received response for unknown request ID: {}", response.id);
                        }
                    }
                    Ok(JsonRpcMessage::Notification(notification)) => {
                        info!("Received notification: {}", notification.method);
                        // TODO: Handle notifications (server-initiated messages)
                    }
                    Ok(JsonRpcMessage::Request(_)) => {
                        warn!("Received request from server (not yet supported)");
                        // TODO: Handle server requests (if needed)
                    }
                    Err(e) => {
                        debug!(
                            "Failed to parse JSON-RPC message (likely a log line): {e} - {line}"
                        );
                    }
                }
            }

            info!("Message handler terminated");
        });

        self.process = Some(child);
        self.stdin = Some(stdin);
        self._message_handler = Some(message_handler);
        self.connected = true;

        info!("stdio transport started successfully");
        Ok(())
    }

    async fn send_request(&self, request: JsonRpcRequest) -> Result<JsonRpcResponse> {
        if !self.connected {
            return Err(Error::Transport(TransportError::ConnectionClosed));
        }

        let (response_sender, response_receiver) = oneshot::channel();

        // Register the pending request
        {
            let mut pending = self.pending_requests.lock().await;
            pending.insert(request.id.clone(), response_sender);
        }

        // Send the request
        let message = serde_json::to_string(&JsonRpcMessage::Request(request.clone()))
            .map_err(Error::Json)?;

        debug!("Sending request: {}", message);

        if let Some(stdin) = &self.stdin {
            use tokio::io::AsyncWriteExt;
            let mut stdin_guard = stdin.lock().await;
            stdin_guard.write_all(message.as_bytes()).await?;
            stdin_guard.write_all(b"\n").await?;
            stdin_guard.flush().await?;
        } else {
            return Err(Error::Transport(TransportError::ConnectionClosed));
        }

        // Wait for response
        match tokio::time::timeout(std::time::Duration::from_secs(30), response_receiver).await {
            Ok(Ok(response)) => Ok(response),
            Ok(Err(_)) => {
                // Clean up pending request
                let mut pending = self.pending_requests.lock().await;
                pending.remove(&request.id);
                Err(Error::Transport(TransportError::ConnectionClosed))
            }
            Err(_) => {
                // Clean up pending request
                let mut pending = self.pending_requests.lock().await;
                pending.remove(&request.id);
                Err(Error::Transport(TransportError::Timeout))
            }
        }
    }

    async fn send_notification(
        &self,
        notification: crate::mcp::protocol::JsonRpcNotification,
    ) -> Result<()> {
        if !self.connected {
            return Err(Error::Transport(TransportError::ConnectionClosed));
        }

        let message = serde_json::to_string(&JsonRpcMessage::Notification(notification))
            .map_err(Error::Json)?;

        debug!("Sending notification: {}", message);

        if let Some(stdin) = &self.stdin {
            use tokio::io::AsyncWriteExt;
            let mut stdin_guard = stdin.lock().await;
            stdin_guard.write_all(message.as_bytes()).await?;
            stdin_guard.write_all(b"\n").await?;
            stdin_guard.flush().await?;
        } else {
            return Err(Error::Transport(TransportError::ConnectionClosed));
        }

        Ok(())
    }

    async fn close(&mut self) -> Result<()> {
        info!("Closing stdio transport");

        self.connected = false;

        if let Some(mut process) = self.process.take() {
            // Close stdin to signal the process to exit
            drop(self.stdin.take());

            // Wait for process to exit gracefully
            match tokio::time::timeout(std::time::Duration::from_secs(5), process.wait()).await {
                Ok(Ok(status)) => {
                    if status.success() {
                        info!("Process exited successfully");
                    } else {
                        warn!("Process exited with status: {status}");
                    }
                }
                Ok(Err(e)) => {
                    error!("Error waiting for process: {e}");
                }
                Err(_) => {
                    warn!("Process did not exit gracefully, killing it");
                    let _ = process.kill().await;
                }
            }
        }

        // Cancel message handler
        if let Some(handler) = self._message_handler.take() {
            handler.abort();
        }

        // Clear pending requests
        {
            let mut pending = self.pending_requests.lock().await;
            pending.clear();
        }

        info!("stdio transport closed");
        Ok(())
    }

    fn is_connected(&self) -> bool {
        self.connected
    }
}

/// HTTP transport implementation using POST requests and Server-Sent Events
pub struct HttpTransport {
    endpoint_url: String,
    sse_endpoint_url: String,
    client: reqwest::Client,
    pending_requests: Arc<Mutex<HashMap<RequestId, oneshot::Sender<JsonRpcResponse>>>>,
    _sse_handler: Option<tokio::task::JoinHandle<()>>,
    connected: bool,
}

impl HttpTransport {
    /// Create a new HTTP transport
    pub fn new(endpoint_url: impl Into<String>) -> Self {
        let endpoint_url = endpoint_url.into();
        let sse_endpoint_url = if endpoint_url.ends_with('/') {
            format!("{endpoint_url}sse")
        } else {
            format!("{endpoint_url}/sse")
        };

        Self {
            endpoint_url,
            sse_endpoint_url,
            client: reqwest::Client::new(),
            pending_requests: Arc::new(Mutex::new(HashMap::new())),
            _sse_handler: None,
            connected: false,
        }
    }

    /// Create HTTP transport for the Goldentooth MCP server
    pub fn goldentooth_server(base_url: impl Into<String>) -> Self {
        let base_url = base_url.into();
        let endpoint_url = if base_url.ends_with('/') {
            format!("{base_url}mcp")
        } else {
            format!("{base_url}/mcp")
        };
        Self::new(endpoint_url)
    }

    /// Start the SSE connection handler
    fn start_sse_handler(
        sse_url: String,
        client: reqwest::Client,
        pending_requests: Arc<Mutex<HashMap<RequestId, oneshot::Sender<JsonRpcResponse>>>>,
    ) -> tokio::task::JoinHandle<()> {
        tokio::spawn(async move {
            info!("Starting SSE connection to: {sse_url}");

            match client
                .get(&sse_url)
                .header("Accept", "text/event-stream")
                .header("Cache-Control", "no-cache")
                .timeout(std::time::Duration::from_secs(30))
                .send()
                .await
            {
                Ok(response) => {
                    if !response.status().is_success() {
                        error!("SSE connection failed with status: {}", response.status());
                        return;
                    }

                    info!("SSE connection established");
                    let mut stream = response.bytes_stream();
                    let mut buffer = Vec::new();

                    while let Some(chunk_result) = stream.next().await {
                        match chunk_result {
                            Ok(chunk) => {
                                buffer.extend_from_slice(&chunk);

                                // Process complete lines
                                while let Some(line_end) = buffer.iter().position(|&b| b == b'\n') {
                                    let line_bytes = buffer.drain(..=line_end).collect::<Vec<_>>();
                                    let line = String::from_utf8_lossy(
                                        &line_bytes[..line_bytes.len() - 1],
                                    );

                                    // Process SSE data lines
                                    if let Some(data) = line.strip_prefix("data: ") {
                                        if !data.is_empty() && data != "[DONE]" {
                                            debug!("Received SSE data: {data}");

                                            match serde_json::from_str::<JsonRpcMessage>(data) {
                                                Ok(JsonRpcMessage::Response(response)) => {
                                                    // Handle response by notifying waiting request
                                                    let mut pending = pending_requests.lock().await;
                                                    if let Some(sender) =
                                                        pending.remove(&response.id)
                                                    {
                                                        if sender.send(response).is_err() {
                                                            warn!(
                                                                "Failed to send response to waiting request"
                                                            );
                                                        }
                                                    } else {
                                                        warn!(
                                                            "Received response for unknown request ID: {}",
                                                            response.id
                                                        );
                                                    }
                                                }
                                                Ok(JsonRpcMessage::Notification(notification)) => {
                                                    info!(
                                                        "Received notification: {}",
                                                        notification.method
                                                    );
                                                    // TODO: Handle notifications (server-initiated messages)
                                                }
                                                Ok(JsonRpcMessage::Request(_)) => {
                                                    warn!(
                                                        "Received request from server (not yet supported)"
                                                    );
                                                    // TODO: Handle server requests (if needed)
                                                }
                                                Err(e) => {
                                                    debug!(
                                                        "Failed to parse JSON-RPC message: {e} - {data}"
                                                    );
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            Err(e) => {
                                error!("SSE stream error: {e}");
                                break;
                            }
                        }
                    }

                    info!("SSE connection closed");
                }
                Err(e) => {
                    error!("Failed to establish SSE connection: {e}");
                }
            }
        })
    }
}

#[async_trait]
impl Transport for HttpTransport {
    async fn start(&mut self) -> Result<()> {
        info!("Starting HTTP transport to: {}", self.endpoint_url);

        // Test connection to the endpoint
        let response = self
            .client
            .get(&self.endpoint_url)
            .timeout(std::time::Duration::from_secs(10))
            .send()
            .await
            .map_err(|e| {
                Error::Transport(TransportError::ConnectionFailed(format!(
                    "Failed to connect: {e}"
                )))
            })?;

        if !response.status().is_success() {
            return Err(Error::Transport(TransportError::ConnectionFailed(format!(
                "Server returned status: {}",
                response.status()
            ))));
        }

        // Start SSE connection for receiving server messages
        let sse_handler = Self::start_sse_handler(
            self.sse_endpoint_url.clone(),
            self.client.clone(),
            Arc::clone(&self.pending_requests),
        );

        self._sse_handler = Some(sse_handler);
        self.connected = true;

        info!("HTTP transport started successfully");
        Ok(())
    }

    async fn send_request(&self, request: JsonRpcRequest) -> Result<JsonRpcResponse> {
        if !self.connected {
            return Err(Error::Transport(TransportError::ConnectionClosed));
        }

        let (response_sender, response_receiver) = oneshot::channel();

        // Register the pending request
        {
            let mut pending = self.pending_requests.lock().await;
            pending.insert(request.id.clone(), response_sender);
        }

        // Send the request via POST
        let message = serde_json::to_string(&JsonRpcMessage::Request(request.clone()))
            .map_err(Error::Json)?;

        debug!("Sending HTTP request: {}", message);

        let response = self
            .client
            .post(&self.endpoint_url)
            .header("Content-Type", "application/json")
            .body(message)
            .timeout(std::time::Duration::from_secs(30))
            .send()
            .await;

        match response {
            Ok(http_response) => {
                if !http_response.status().is_success() {
                    // Clean up pending request
                    let mut pending = self.pending_requests.lock().await;
                    pending.remove(&request.id);
                    return Err(Error::Transport(TransportError::Http(
                        reqwest::Response::error_for_status(http_response).unwrap_err(),
                    )));
                }

                // For HTTP transport, the response comes via SSE, so we wait for it
                match tokio::time::timeout(std::time::Duration::from_secs(30), response_receiver)
                    .await
                {
                    Ok(Ok(response)) => Ok(response),
                    Ok(Err(_)) => {
                        // Clean up pending request
                        let mut pending = self.pending_requests.lock().await;
                        pending.remove(&request.id);
                        Err(Error::Transport(TransportError::ConnectionClosed))
                    }
                    Err(_) => {
                        // Clean up pending request
                        let mut pending = self.pending_requests.lock().await;
                        pending.remove(&request.id);
                        Err(Error::Transport(TransportError::Timeout))
                    }
                }
            }
            Err(e) => {
                // Clean up pending request
                let mut pending = self.pending_requests.lock().await;
                pending.remove(&request.id);
                Err(Error::Transport(TransportError::Http(e)))
            }
        }
    }

    async fn send_notification(
        &self,
        notification: crate::mcp::protocol::JsonRpcNotification,
    ) -> Result<()> {
        if !self.connected {
            return Err(Error::Transport(TransportError::ConnectionClosed));
        }

        let message = serde_json::to_string(&JsonRpcMessage::Notification(notification))
            .map_err(Error::Json)?;

        debug!("Sending HTTP notification: {}", message);

        let response = self
            .client
            .post(&self.endpoint_url)
            .header("Content-Type", "application/json")
            .body(message)
            .timeout(std::time::Duration::from_secs(30))
            .send()
            .await
            .map_err(TransportError::Http)?;

        if !response.status().is_success() {
            return Err(Error::Transport(TransportError::Http(
                reqwest::Response::error_for_status(response).unwrap_err(),
            )));
        }

        Ok(())
    }

    async fn close(&mut self) -> Result<()> {
        info!("Closing HTTP transport");

        self.connected = false;

        // Cancel SSE handler
        if let Some(handler) = self._sse_handler.take() {
            handler.abort();
        }

        // Clear pending requests
        {
            let mut pending = self.pending_requests.lock().await;
            pending.clear();
        }

        info!("HTTP transport closed");
        Ok(())
    }

    fn is_connected(&self) -> bool {
        self.connected
    }
}
