//! Mock MCP Server for testing HTTP transport compatibility
//!
//! This mock server mimics the behavior of the Goldentooth MCP server
//! to enable testing without requiring the actual server to be running.

use http_body_util::{BodyExt, Full};
use hyper::body::{Bytes, Incoming};
use hyper::service::service_fn;
use hyper::{Request, Response, StatusCode, header};
use hyper_util::rt::TokioIo;
use serde_json::json;
use std::collections::HashMap;
use std::convert::Infallible;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::sync::RwLock;

/// Mock MCP server that mimics Goldentooth server behavior
pub struct MockMcpServer {
    addr: SocketAddr,
    state: Arc<MockServerState>,
    _server_handle: tokio::task::JoinHandle<()>,
}

/// Internal state tracking for the mock server
#[derive(Debug, Default)]
struct MockServerState {
    /// Track requests by path and method
    requests: RwLock<HashMap<String, Vec<MockRequest>>>,
    /// Server configuration
    config: MockServerConfig,
}

/// Configuration for mock server behavior
#[derive(Debug, Clone)]
struct MockServerConfig {
    /// Whether to require JWT authentication
    require_auth: bool,
    /// Whether to send Connection: close header
    send_connection_close: bool,
    /// Whether to respond with SSE format
    use_sse_response: bool,
    /// Valid JWT token for testing
    valid_token: Option<String>,
}

impl Default for MockServerConfig {
    fn default() -> Self {
        Self {
            require_auth: false,
            send_connection_close: false,
            use_sse_response: false,
            valid_token: Some("valid-test-jwt-token".to_string()),
        }
    }
}

/// Captured request information
#[derive(Debug, Clone)]
pub struct MockRequest {
    pub method: String,
    pub path: String,
    pub headers: HashMap<String, String>,
    pub body: String,
}

impl MockRequest {
    pub fn headers(&self) -> &HashMap<String, String> {
        &self.headers
    }
}

impl MockMcpServer {
    /// Create a new mock server with default settings
    pub async fn new() -> Self {
        Self::with_config(MockServerConfig::default()).await
    }

    /// Create a mock server that responds with SSE format
    pub async fn with_sse_responses() -> Self {
        let config = MockServerConfig {
            use_sse_response: true,
            ..Default::default()
        };
        Self::with_config(config).await
    }

    /// Create a mock server that sends Connection: close
    pub async fn with_connection_close() -> Self {
        let config = MockServerConfig {
            send_connection_close: true,
            ..Default::default()
        };
        Self::with_config(config).await
    }

    /// Create a mock server that requires JWT authentication
    pub async fn with_jwt_auth() -> Self {
        let config = MockServerConfig {
            require_auth: true,
            ..Default::default()
        };
        Self::with_config(config).await
    }

    /// Create a mock server with custom configuration
    async fn with_config(config: MockServerConfig) -> Self {
        let state = Arc::new(MockServerState {
            requests: RwLock::new(HashMap::new()),
            config,
        });

        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();

        let state_for_service = Arc::clone(&state);

        let server_handle = tokio::spawn(async move {
            loop {
                match listener.accept().await {
                    Ok((stream, _)) => {
                        let state = Arc::clone(&state_for_service);
                        let io = TokioIo::new(stream);

                        tokio::spawn(async move {
                            let service = service_fn(move |req| {
                                let state = Arc::clone(&state);
                                handle_request(req, state)
                            });

                            if let Err(err) = hyper::server::conn::http1::Builder::new()
                                .serve_connection(io, service)
                                .await
                            {
                                eprintln!("Error serving connection: {err:?}");
                            }
                        });
                    }
                    Err(e) => {
                        eprintln!("Error accepting connection: {e}");
                        break;
                    }
                }
            }
        });

        // Give the server a moment to start
        tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;

        Self {
            addr,
            state,
            _server_handle: server_handle,
        }
    }

    /// Get the base URL of the mock server
    pub fn url(&self) -> String {
        format!("http://{}", self.addr)
    }

    /// Get the number of requests to a specific path (any method)
    pub async fn request_count(&self, path: &str) -> usize {
        let requests = self.state.requests.read().await;
        requests
            .values()
            .flatten()
            .filter(|req| req.path == path)
            .count()
    }

    /// Get the number of GET requests to a specific path
    pub async fn get_request_count(&self, path: &str) -> usize {
        let requests = self.state.requests.read().await;
        requests
            .get(&format!("GET:{path}"))
            .map_or(0, std::vec::Vec::len)
    }

    /// Get the number of POST requests to a specific path
    pub async fn post_request_count(&self, path: &str) -> usize {
        let requests = self.state.requests.read().await;
        requests
            .get(&format!("POST:{path}"))
            .map_or(0, std::vec::Vec::len)
    }

    /// Get the last request received (any method/path)
    pub async fn last_request(&self) -> Option<MockRequest> {
        let requests = self.state.requests.read().await;
        requests.values().flatten().last().cloned()
    }
}

/// Handle incoming requests to the mock server
async fn handle_request(
    req: Request<Incoming>,
    state: Arc<MockServerState>,
) -> Result<Response<Full<Bytes>>, Infallible> {
    let method = req.method().to_string();
    let path = req.uri().path().to_string();
    let key = format!("{method}:{path}");

    // Extract headers
    let mut headers = HashMap::new();
    for (name, value) in req.headers() {
        if let Ok(value_str) = value.to_str() {
            headers.insert(name.to_string(), value_str.to_string());
        }
    }

    // Read body
    let body_bytes = req.collect().await.unwrap_or_default().to_bytes();
    let body = String::from_utf8_lossy(&body_bytes).to_string();

    // Store the request
    {
        let mut requests = state.requests.write().await;
        requests.entry(key).or_default().push(MockRequest {
            method: method.clone(),
            path: path.clone(),
            headers: headers.clone(),
            body: body.clone(),
        });
    }

    // Handle the request based on path and configuration
    match (method.as_str(), path.as_str()) {
        ("POST", "/mcp") => handle_mcp_request(&headers, &body, &state.config),
        ("GET", "/mcp" | "/sse") => {
            // Mock server doesn't support GET requests (like real server)
            Ok(Response::builder()
                .status(StatusCode::BAD_REQUEST)
                .body(Full::new(Bytes::from("SSE connections via GET not supported. Use POST with Accept: text/event-stream")))
                .unwrap())
        }
        _ => Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Full::new(Bytes::from("Not Found")))
            .unwrap()),
    }
}

/// Handle MCP requests
#[allow(clippy::unnecessary_wraps)]
fn handle_mcp_request(
    headers: &HashMap<String, String>,
    body: &str,
    config: &MockServerConfig,
) -> Result<Response<Full<Bytes>>, Infallible> {
    // Check authentication if required
    if config.require_auth {
        if let Some(auth_header) = headers.get("authorization") {
            let token = auth_header.strip_prefix("Bearer ").unwrap_or("");
            if config.valid_token.as_deref() != Some(token) {
                return Ok(Response::builder()
                    .status(StatusCode::UNAUTHORIZED)
                    .header("Content-Type", "application/json")
                    .body(Full::new(Bytes::from(
                        json!({
                            "jsonrpc": "2.0",
                            "id": null,
                            "error": {
                                "code": -32001,
                                "message": "Authentication required",
                                "data": {
                                    "type": "AuthenticationError",
                                    "details": "HTTP transport requires valid JWT token"
                                }
                            }
                        })
                        .to_string(),
                    )))
                    .unwrap());
            }
        } else {
            return Ok(Response::builder()
                .status(StatusCode::UNAUTHORIZED)
                .header("Content-Type", "application/json")
                .body(Full::new(Bytes::from(
                    json!({
                        "jsonrpc": "2.0",
                        "id": null,
                        "error": {
                            "code": -32001,
                            "message": "Authentication required"
                        }
                    })
                    .to_string(),
                )))
                .unwrap());
        }
    }

    // Extract request ID from the request body
    let request_id = if let Ok(request_json) = serde_json::from_str::<serde_json::Value>(body) {
        request_json
            .get("id")
            .and_then(|id| id.as_str())
            .unwrap_or("test-1")
            .to_string()
    } else {
        "test-1".to_string() // Fallback ID
    };

    // Create mock response with the correct request ID
    let response_data = json!({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "mock-goldentooth-mcp-server",
                "version": "0.1.0"
            },
            "nodes": ["allyrion", "jast"]
        }
    });

    let mut response_builder = Response::builder().status(StatusCode::OK);

    // Add Connection: close header if configured
    if config.send_connection_close {
        response_builder = response_builder.header(header::CONNECTION, "close");
    }

    // Choose response format based on configuration
    if config.use_sse_response
        || headers
            .get("accept")
            .is_some_and(|h| h.contains("text/event-stream"))
    {
        // Return SSE-formatted response
        let sse_data = format!("data: {response_data}\n\n");

        Ok(response_builder
            .header("Content-Type", "text/event-stream")
            .header("Cache-Control", "no-cache")
            .body(Full::new(Bytes::from(sse_data)))
            .unwrap())
    } else {
        // Return regular JSON response
        Ok(response_builder
            .header("Content-Type", "application/json")
            .body(Full::new(Bytes::from(response_data.to_string())))
            .unwrap())
    }
}
