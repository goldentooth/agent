//! Tests for HTTP transport compatibility with Goldentooth MCP server
//! These tests validate the new POST-with-SSE-response pattern

mod common;

use common::{MockMcpServer, init_test_logging};
use goldentooth_agent::error::{Error, TransportError};
use goldentooth_agent::mcp::protocol::*;
use goldentooth_agent::mcp::transport::{HttpTransport, Transport};
use serde_json::json;

#[tokio::test]
async fn test_http_transport_uses_single_mcp_endpoint() {
    // RED: This test will fail until we fix the transport
    init_test_logging();

    let mock_server = MockMcpServer::new().await;
    let mut transport = HttpTransport::goldentooth_server(mock_server.url());

    transport.start().await.expect("Transport should start");

    let request = JsonRpcRequest::new(
        "test-1".into(),
        "initialize",
        Some(json!({
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "goldentooth-agent-test",
                "version": "0.1.0"
            }
        })),
    );

    // This should send POST to /mcp endpoint, not try to establish separate SSE connection
    let response = transport
        .send_request(request)
        .await
        .expect("Request should succeed");

    // Verify we got a proper response
    match response.result {
        ResponseResult::Success { .. } => {
            // Success - verify the server only received requests to /mcp endpoint
            assert_eq!(mock_server.request_count("/mcp").await, 1);
            assert_eq!(mock_server.request_count("/sse").await, 0); // Should be zero
        }
        ResponseResult::Error { error } => {
            panic!("Initialize failed: {error:?}");
        }
    }

    transport.close().await.expect("Transport should close");
}

#[tokio::test]
async fn test_http_transport_sends_correct_headers() {
    // RED: This test will fail until we send proper headers
    init_test_logging();

    let mock_server = MockMcpServer::new().await;
    let mut transport = HttpTransport::goldentooth_server(mock_server.url());

    transport.start().await.expect("Transport should start");

    let request = JsonRpcRequest::new("test-2".into(), "ping", None);

    transport
        .send_request(request)
        .await
        .expect("Request should succeed");

    // Verify the correct headers were sent
    let last_request = mock_server
        .last_request()
        .await
        .expect("Should have received a request");
    assert_eq!(
        last_request.headers().get("content-type").unwrap(),
        "application/json"
    );
    assert_eq!(
        last_request.headers().get("accept").unwrap(),
        "text/event-stream"
    );

    transport.close().await.expect("Transport should close");
}

#[tokio::test]
async fn test_http_transport_handles_sse_response_format() {
    // RED: This test will fail until we parse SSE format correctly
    init_test_logging();

    let mock_server = MockMcpServer::with_sse_responses().await;
    let mut transport = HttpTransport::goldentooth_server(mock_server.url());

    transport.start().await.expect("Transport should start");

    let request = JsonRpcRequest::new(
        "test-3".into(),
        "cluster_ping",
        Some(json!({
            "nodes": ["allyrion"]
        })),
    );

    let response = transport
        .send_request(request)
        .await
        .expect("Request should succeed");

    // Verify we parsed the SSE response correctly
    assert_eq!(response.id, "test-3".into());
    match response.result {
        ResponseResult::Success { result } => {
            assert!(result.get("nodes").is_some());
        }
        ResponseResult::Error { error } => {
            panic!("Request failed: {error:?}");
        }
    }

    transport.close().await.expect("Transport should close");
}

#[tokio::test]
async fn test_http_transport_handles_connection_close() {
    // RED: This test will fail until we handle Connection: close properly
    init_test_logging();

    let mock_server = MockMcpServer::with_connection_close().await;
    let mut transport = HttpTransport::goldentooth_server(mock_server.url());

    transport.start().await.expect("Transport should start");

    // Send multiple requests - each should work despite Connection: close
    for i in 1..=3 {
        let request = JsonRpcRequest::new(format!("test-{i}").into(), "ping", None);

        let response = transport
            .send_request(request)
            .await
            .unwrap_or_else(|_| panic!("Request {i} should succeed"));
        assert_eq!(response.id, format!("test-{i}").into());
    }

    transport.close().await.expect("Transport should close");
}

#[tokio::test]
async fn test_http_transport_authentication_flow() {
    // RED: This test will fail until we implement JWT auth
    init_test_logging();

    let mock_server = MockMcpServer::with_jwt_auth().await;
    let mut transport = HttpTransport::goldentooth_server(mock_server.url());

    // Should fail without authentication
    transport.start().await.expect("Transport should start");

    let request = JsonRpcRequest::new("auth-test-1".into(), "cluster_ping", None);

    let result = transport.send_request(request.clone()).await;

    // Should get authentication error
    match result {
        Err(Error::Transport(TransportError::Http(err)))
            if err.status().map(|s| s.as_u16()) == Some(401) =>
        {
            // Expected - no auth provided
        }
        other => panic!("Expected 401 Unauthorized, got: {other:?}"),
    }

    // Now add JWT token and retry
    transport.set_auth_token("Bearer valid-test-jwt-token");

    let response = transport
        .send_request(request)
        .await
        .expect("Authenticated request should succeed");

    match response.result {
        ResponseResult::Success { .. } => {
            // Success with authentication
        }
        ResponseResult::Error { error } => {
            panic!("Authenticated request failed: {error:?}");
        }
    }

    transport.close().await.expect("Transport should close");
}

#[tokio::test]
async fn test_http_transport_no_persistent_sse_connection() {
    // RED: This test will fail until we remove persistent SSE connection attempt
    init_test_logging();

    let mock_server = MockMcpServer::new().await;
    let mut transport = HttpTransport::goldentooth_server(mock_server.url());

    // Start should NOT try to establish persistent SSE connection
    transport
        .start()
        .await
        .expect("Transport should start without SSE connection");

    // Verify no GET request to SSE endpoint was made during start()
    assert_eq!(mock_server.get_request_count("/mcp").await, 0);
    assert_eq!(mock_server.get_request_count("/sse").await, 0);

    // Only POST requests should be made when sending messages
    let request = JsonRpcRequest::new("test-1".into(), "ping", None);
    transport
        .send_request(request)
        .await
        .expect("Request should succeed");

    // Should have exactly one POST request to /mcp
    assert_eq!(mock_server.post_request_count("/mcp").await, 1);
    assert_eq!(mock_server.get_request_count("/mcp").await, 0);

    transport.close().await.expect("Transport should close");
}
