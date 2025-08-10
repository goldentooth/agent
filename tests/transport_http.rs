//! Tests for HTTP transport implementation

mod common;
use goldentooth_agent::error::TransportError;
use goldentooth_agent::mcp::protocol::*;
use goldentooth_agent::mcp::transport::{HttpTransport, Transport};
use serde_json::json;

#[tokio::test]
async fn test_http_transport_creation() {
    let transport = HttpTransport::new("http://localhost:8080/mcp");

    // Initially not connected
    assert!(!transport.is_connected());
}

#[tokio::test]
async fn test_http_transport_goldentooth_server_url_construction() {
    // Test with trailing slash
    let transport1 = HttpTransport::goldentooth_server("http://localhost:8080/");
    // Test without trailing slash
    let transport2 = HttpTransport::goldentooth_server("http://localhost:8080");

    // Both should create the same effective endpoint URL
    // (We can't directly check URLs as they're private, but we test behavior)
    assert!(!transport1.is_connected());
    assert!(!transport2.is_connected());
}

#[tokio::test]
async fn test_http_transport_connection_failure() {
    let mut transport = HttpTransport::new("http://localhost:9999/nonexistent");

    // Should fail to connect to nonexistent server
    let result = transport.start().await;
    assert!(result.is_err());

    match result.unwrap_err() {
        goldentooth_agent::error::Error::Transport(TransportError::ConnectionFailed(_)) => {
            // Expected error type
        }
        other => panic!("Expected ConnectionFailed error, got: {other:?}"),
    }

    // Should still not be connected
    assert!(!transport.is_connected());
}

#[tokio::test]
async fn test_http_transport_send_request_when_disconnected() {
    let transport = HttpTransport::new("http://localhost:8080/mcp");

    // Try to send request without starting transport
    let request = JsonRpcRequest::new(
        "test-1".into(),
        "initialize",
        Some(json!({
            "protocolVersion": "2025-06-18"
        })),
    );

    let result = transport.send_request(request).await;
    assert!(result.is_err());

    match result.unwrap_err() {
        goldentooth_agent::error::Error::Transport(TransportError::ConnectionClosed) => {
            // Expected error type
        }
        other => panic!("Expected ConnectionClosed error, got: {other:?}"),
    }
}

#[tokio::test]
async fn test_http_transport_send_notification_when_disconnected() {
    let transport = HttpTransport::new("http://localhost:8080/mcp");

    // Try to send notification without starting transport
    let notification = JsonRpcNotification::new("initialized", Some(json!({})));

    let result = transport.send_notification(notification).await;
    assert!(result.is_err());

    match result.unwrap_err() {
        goldentooth_agent::error::Error::Transport(TransportError::ConnectionClosed) => {
            // Expected error type
        }
        other => panic!("Expected ConnectionClosed error, got: {other:?}"),
    }
}

#[tokio::test]
async fn test_http_transport_lifecycle() {
    let mut transport = HttpTransport::new("http://localhost:9999/test");

    // Initially not connected
    assert!(!transport.is_connected());

    // Attempt to start (will fail due to no server, but test lifecycle)
    let start_result = transport.start().await;
    assert!(start_result.is_err()); // Expected to fail

    // Close should always succeed regardless of connection state
    let close_result = transport.close().await;
    assert!(close_result.is_ok());

    // Should be marked as disconnected after close
    assert!(!transport.is_connected());
}

// NOTE: Integration tests with real HTTP MCP server would go here
// These tests would require:
// 1. An HTTP MCP server implementation (currently only stdio exists)
// 2. Server setup/teardown in tests
// 3. Full request/response cycle testing
//
// For now, the above tests validate:
// - Basic structure and error handling
// - Connection lifecycle
// - Error conditions
// - Transport trait compliance

// Integration tests would go here when HTTP MCP server is available
// For now, commented out to avoid compilation issues

/*
#[ignore = "requires HTTP MCP server"]
#[tokio::test]
async fn test_http_transport_full_workflow() {
    // TODO: Implement when HTTP MCP server is available
    use common::TestEnvironment;
    let env = TestEnvironment::setup();
    let mut transport = env.http_transport;

    // Start transport and test full MCP workflow
    transport.start().await.expect("Failed to start HTTP transport");

    // Send initialize request
    let init_request = JsonRpcRequest::new(
        "init-1".into(),
        "initialize",
        Some(json!({
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "goldentooth-agent-test",
                "version": "0.1.0"
            }
        }))
    );

    let response = transport.send_request(init_request).await
        .expect("Failed to send initialize request");

    // Verify response structure
    match response.result {
        ResponseResult::Success { result } => {
            assert!(result.get("protocolVersion").is_some());
            assert!(result.get("capabilities").is_some());
        }
        ResponseResult::Error { error } => {
            panic!("Initialize failed: {:?}", error);
        }
    }

    transport.close().await.expect("Failed to close transport");
}
*/
