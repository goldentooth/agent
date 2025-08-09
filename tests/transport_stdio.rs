//! Tests for stdio transport with real Goldentooth MCP server

mod common;

use common::TestEnvironment;
use goldentooth_agent::mcp::protocol::*;
use goldentooth_agent::mcp::transport::Transport;
use serde_json::json;

#[tokio::test]
async fn test_stdio_transport_connection() {
    let env = TestEnvironment::setup()
        .await
        .expect("Failed to setup test environment");
    let mut transport = env.stdio_transport;

    // Initially not connected
    assert!(!transport.is_connected());

    // Start transport
    transport.start().await.expect("Failed to start transport");
    assert!(transport.is_connected());

    // Close transport
    transport.close().await.expect("Failed to close transport");
    assert!(!transport.is_connected());

    // Note: env cleanup happens automatically when dropped
}

#[tokio::test]
async fn test_stdio_mcp_initialization() {
    let env = TestEnvironment::setup()
        .await
        .expect("Failed to setup test environment");
    let mut transport = env.stdio_transport;

    // Start the transport
    transport.start().await.expect("Failed to start transport");

    // Send initialize request
    let init_request = JsonRpcRequest::new(
        "init-1".into(),
        "initialize",
        Some(json!({
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "experimental": {},
                "sampling": {}
            },
            "clientInfo": {
                "name": "goldentooth-agent-test",
                "version": "0.1.0"
            }
        })),
    );

    let response = transport
        .send_request(init_request)
        .await
        .expect("Initialize request failed");

    // Verify response
    assert_eq!(response.jsonrpc, "2.0");
    assert_eq!(response.id, RequestId::String("init-1".to_string()));

    match response.result {
        ResponseResult::Success { result } => {
            // Should have protocolVersion and capabilities
            assert!(result.get("protocolVersion").is_some());
            assert!(result.get("capabilities").is_some());
            assert!(result.get("serverInfo").is_some());

            // Check protocol version matches
            assert_eq!(result["protocolVersion"], "2025-06-18");

            println!(
                "Initialize response: {}",
                serde_json::to_string_pretty(&result).unwrap()
            );
        }
        ResponseResult::Error { error } => {
            panic!(
                "Initialize failed with error: {} - {}",
                error.code, error.message
            );
        }
    }

    // Send initialized notification
    let initialized_notification = JsonRpcNotification::new("initialized", Some(json!({})));
    transport
        .send_notification(initialized_notification)
        .await
        .expect("Failed to send initialized notification");

    transport.close().await.expect("Failed to close transport");
    // Note: env cleanup happens automatically when dropped
}

#[tokio::test]
async fn test_stdio_tools_list() {
    let env = TestEnvironment::setup()
        .await
        .expect("Failed to setup test environment");
    let mut transport = env.stdio_transport;

    // Start and initialize
    transport.start().await.expect("Failed to start transport");

    // Initialize the MCP session
    let init_response = transport
        .send_request(JsonRpcRequest::new(
            "init".into(),
            "initialize",
            Some(json!({
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            })),
        ))
        .await
        .expect("Initialize failed");

    // Verify initialization succeeded
    match init_response.result {
        ResponseResult::Success { .. } => {}
        ResponseResult::Error { error } => panic!("Initialize failed: {}", error.message),
    }

    // Send initialized notification
    transport
        .send_notification(JsonRpcNotification::new("initialized", Some(json!({}))))
        .await
        .expect("Failed to send initialized");

    // Request tools list
    let tools_request = JsonRpcRequest::new("tools-1".into(), "tools/list", Some(json!({})));

    let response = transport
        .send_request(tools_request)
        .await
        .expect("Tools list request failed");

    match response.result {
        ResponseResult::Success { result } => {
            println!(
                "Tools response: {}",
                serde_json::to_string_pretty(&result).unwrap()
            );

            // Should have tools array
            let tools = result.get("tools").expect("Missing tools in response");
            let tools_array = tools.as_array().expect("Tools should be an array");

            // Should have Goldentooth cluster management tools
            let tool_names: Vec<String> = tools_array
                .iter()
                .map(|tool| tool["name"].as_str().unwrap().to_string())
                .collect();

            println!("Available tools: {tool_names:?}");

            // Check for expected Goldentooth tools (based on actual server response)
            let expected_tools = vec![
                "cluster_ping",
                "cluster_status",
                "service_status",
                "shell_command",
            ];

            for expected_tool in expected_tools {
                assert!(
                    tool_names.contains(&expected_tool.to_string()),
                    "Missing expected tool: {expected_tool}"
                );
            }
        }
        ResponseResult::Error { error } => {
            panic!(
                "Tools list failed with error: {} - {}",
                error.code, error.message
            );
        }
    }

    transport.close().await.expect("Failed to close transport");
    // Note: env cleanup happens automatically when dropped
}

#[tokio::test]
async fn test_stdio_concurrent_requests() {
    let env = TestEnvironment::setup()
        .await
        .expect("Failed to setup test environment");
    let mut transport = env.stdio_transport;

    transport.start().await.expect("Failed to start transport");

    // Initialize first
    let init_response = transport
        .send_request(JsonRpcRequest::new(
            "init".into(),
            "initialize",
            Some(json!({
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            })),
        ))
        .await
        .expect("Initialize failed");

    match init_response.result {
        ResponseResult::Success { .. } => {}
        ResponseResult::Error { error } => panic!("Initialize failed: {}", error.message),
    }

    transport
        .send_notification(JsonRpcNotification::new("initialized", Some(json!({}))))
        .await
        .expect("Failed to send initialized");

    // Send multiple concurrent requests
    let request1 = transport.send_request(JsonRpcRequest::new(
        "req1".into(),
        "tools/list",
        Some(json!({})),
    ));

    let request2 = transport.send_request(JsonRpcRequest::new(
        "req2".into(),
        "tools/list",
        Some(json!({})),
    ));

    let request3 = transport.send_request(JsonRpcRequest::new(
        "req3".into(),
        "tools/list",
        Some(json!({})),
    ));

    // All should complete successfully regardless of response order
    let (response1, response2, response3) = tokio::join!(request1, request2, request3);

    let resp1 = response1.expect("Request 1 failed");
    let resp2 = response2.expect("Request 2 failed");
    let resp3 = response3.expect("Request 3 failed");

    // Verify all responses are successful and have correct IDs
    assert_eq!(resp1.id, RequestId::String("req1".to_string()));
    assert_eq!(resp2.id, RequestId::String("req2".to_string()));
    assert_eq!(resp3.id, RequestId::String("req3".to_string()));

    for response in [resp1, resp2, resp3] {
        match response.result {
            ResponseResult::Success { .. } => {}
            ResponseResult::Error { error } => panic!("Request failed: {}", error.message),
        }
    }

    transport.close().await.expect("Failed to close transport");
    // Note: env cleanup happens automatically when dropped
}

#[tokio::test]
async fn test_stdio_error_handling() {
    let env = TestEnvironment::setup()
        .await
        .expect("Failed to setup test environment");
    let mut transport = env.stdio_transport;

    transport.start().await.expect("Failed to start transport");

    // Send invalid request (method not found)
    let invalid_request =
        JsonRpcRequest::new("invalid-1".into(), "nonexistent/method", Some(json!({})));

    let response = transport
        .send_request(invalid_request)
        .await
        .expect("Request should complete");

    match response.result {
        ResponseResult::Error { error } => {
            // Should be either Invalid Request (-32600) or Method not found (-32601)
            assert!(
                error.code == -32600 || error.code == -32601,
                "Expected JSON-RPC error, got code: {}",
                error.code
            );
            println!("Got expected error: {} - {}", error.code, error.message);
        }
        ResponseResult::Success { .. } => {
            panic!("Expected error response for invalid method");
        }
    }

    transport.close().await.expect("Failed to close transport");
    // Note: env cleanup happens automatically when dropped
}

#[tokio::test]
async fn test_stdio_request_timeout() {
    let env = TestEnvironment::setup()
        .await
        .expect("Failed to setup test environment");
    let mut transport = env.stdio_transport;

    transport.start().await.expect("Failed to start transport");

    // Send request with invalid JSON that might hang
    let malformed_request = JsonRpcRequest::new(
        "timeout-test".into(),
        "initialize",
        Some(json!({"invalid": true})),
    );

    // This should either succeed with an error response or timeout
    match transport.send_request(malformed_request).await {
        Ok(response) => match response.result {
            ResponseResult::Error { error } => {
                println!("Got error as expected: {}", error.message);
            }
            ResponseResult::Success { .. } => {
                println!("Request succeeded unexpectedly");
            }
        },
        Err(e) => {
            println!("Request failed as expected: {e}");
        }
    }

    transport.close().await.expect("Failed to close transport");
    // Note: env cleanup happens automatically when dropped
}
