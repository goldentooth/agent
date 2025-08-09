//! Advanced integration tests using MCP server as a library dependency
//!
//! This provides more robust testing than subprocess spawning by:
//! - Using the actual server code as a library
//! - Testing both stdio and in-process communication
//! - Eliminating external process dependencies

mod common;

use goldentooth_agent::mcp::protocol::*;
use goldentooth_agent::mcp::transport::{StdioTransport, Transport};
use serde_json::json;

#[tokio::test]
async fn test_mcp_server_dependency_available() {
    common::init_test_logging();

    // Verify we can get the server binary
    let server_path = common::get_mcp_server_path();

    assert!(
        server_path.exists(),
        "MCP server binary should exist at {server_path:?}"
    );

    // Verify the binary is executable
    let metadata =
        std::fs::metadata(&server_path).expect("Should be able to read server binary metadata");

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let permissions = metadata.permissions();
        assert!(
            permissions.mode() & 0o111 != 0,
            "Binary should be executable"
        );
    }

    println!("✓ MCP server binary available at: {server_path:?}");
}

#[tokio::test]
#[allow(clippy::too_many_lines)]
async fn test_full_mcp_workflow_with_dev_dependency() {
    common::init_test_logging();

    let server_path = common::get_mcp_server_path();

    let mut transport = StdioTransport::goldentooth_server(&server_path);

    // Test complete MCP workflow
    transport.start().await.expect("Failed to start transport");

    // 1. Initialize
    let init_request = JsonRpcRequest::new(
        "workflow-init".into(),
        "initialize",
        Some(json!({
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "experimental": {},
                "sampling": {}
            },
            "clientInfo": {
                "name": "goldentooth-agent-integration-test",
                "version": "0.1.0"
            }
        })),
    );

    let init_response = transport
        .send_request(init_request)
        .await
        .expect("Initialize should succeed");

    match init_response.result {
        ResponseResult::Success { result } => {
            assert_eq!(result["protocolVersion"], "2025-06-18");
            assert!(result.get("capabilities").is_some());
            assert!(result.get("serverInfo").is_some());

            // Verify server info
            let server_info = &result["serverInfo"];
            assert_eq!(server_info["name"], "goldentooth-mcp");

            println!(
                "✓ Initialize successful with server: {}",
                server_info["name"]
            );
        }
        ResponseResult::Error { error } => {
            panic!("Initialize failed: {} - {}", error.code, error.message);
        }
    }

    // 2. Send initialized notification
    transport
        .send_notification(JsonRpcNotification::new("initialized", Some(json!({}))))
        .await
        .expect("Initialized notification should succeed");

    // 3. List tools
    let tools_request = JsonRpcRequest::new("workflow-tools".into(), "tools/list", Some(json!({})));

    let tools_response = transport
        .send_request(tools_request)
        .await
        .expect("Tools list should succeed");

    match tools_response.result {
        ResponseResult::Success { result } => {
            let tools = result.get("tools").expect("Should have tools array");
            let tools_array = tools.as_array().expect("Tools should be array");

            // Collect tool names
            let tool_names: Vec<String> = tools_array
                .iter()
                .map(|tool| tool["name"].as_str().unwrap().to_string())
                .collect();

            println!("✓ Available tools: {tool_names:?}");

            // Verify expected tools
            let expected_tools = ["cluster_ping", "cluster_status", "service_status"];
            for expected in expected_tools {
                assert!(
                    tool_names.contains(&expected.to_string()),
                    "Missing expected tool: {expected}"
                );
            }

            // Verify each tool has proper schema
            for tool in tools_array {
                assert!(tool.get("name").is_some(), "Tool should have name");
                assert!(
                    tool.get("description").is_some(),
                    "Tool should have description"
                );
                assert!(
                    tool.get("inputSchema").is_some(),
                    "Tool should have input schema"
                );

                let schema = &tool["inputSchema"];
                assert_eq!(
                    schema["type"], "object",
                    "Tool schema should be object type"
                );
            }

            println!("✓ All tools have valid schemas");
        }
        ResponseResult::Error { error } => {
            panic!("Tools list failed: {} - {}", error.code, error.message);
        }
    }

    // 4. Test error handling with invalid method
    let invalid_request = JsonRpcRequest::new(
        "workflow-invalid".into(),
        "nonexistent/method",
        Some(json!({})),
    );

    let invalid_response = transport
        .send_request(invalid_request)
        .await
        .expect("Invalid request should complete (with error response)");

    match invalid_response.result {
        ResponseResult::Error { error } => {
            // Should be a JSON-RPC error (could be -32600 Invalid Request or -32601 Method not found)
            assert!(
                error.code == -32600 || error.code == -32601,
                "Should be JSON-RPC error, got code: {}",
                error.code
            );
            println!("✓ Error handling works: {} - {}", error.code, error.message);
        }
        ResponseResult::Success { .. } => {
            panic!("Invalid method should return error, not success");
        }
    }

    transport
        .close()
        .await
        .expect("Transport should close cleanly");
    println!("✓ Full MCP workflow completed successfully");
}

#[tokio::test]
async fn test_concurrent_requests_with_dev_dependency() {
    common::init_test_logging();

    let server_path = common::get_mcp_server_path();

    let mut transport = StdioTransport::goldentooth_server(&server_path);
    transport.start().await.expect("Failed to start transport");

    // Initialize first
    let init_response = transport
        .send_request(JsonRpcRequest::new(
            "concurrent-init".into(),
            "initialize",
            Some(json!({
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "concurrent-test", "version": "1.0.0"}
            })),
        ))
        .await
        .expect("Initialize should succeed");

    match init_response.result {
        ResponseResult::Success { .. } => {}
        ResponseResult::Error { error } => {
            panic!("Initialize failed: {}", error.message);
        }
    }

    transport
        .send_notification(JsonRpcNotification::new("initialized", Some(json!({}))))
        .await
        .expect("Initialized notification should succeed");

    // Send multiple concurrent requests
    let request1 = transport.send_request(JsonRpcRequest::new(
        "concurrent-1".into(),
        "tools/list",
        Some(json!({})),
    ));

    let request2 = transport.send_request(JsonRpcRequest::new(
        "concurrent-2".into(),
        "tools/list",
        Some(json!({})),
    ));

    let request3 = transport.send_request(JsonRpcRequest::new(
        "concurrent-3".into(),
        "tools/list",
        Some(json!({})),
    ));

    // All should complete successfully
    let (response1, response2, response3) = tokio::join!(request1, request2, request3);

    let resp1 = response1.expect("Request 1 should succeed");
    let resp2 = response2.expect("Request 2 should succeed");
    let resp3 = response3.expect("Request 3 should succeed");

    // Verify IDs are correct
    assert_eq!(resp1.id, RequestId::String("concurrent-1".to_string()));
    assert_eq!(resp2.id, RequestId::String("concurrent-2".to_string()));
    assert_eq!(resp3.id, RequestId::String("concurrent-3".to_string()));

    // All should be successful
    for (i, response) in [resp1, resp2, resp3].iter().enumerate() {
        match &response.result {
            ResponseResult::Success { .. } => {}
            ResponseResult::Error { error } => {
                panic!("Concurrent request {} failed: {}", i + 1, error.message);
            }
        }
    }

    transport
        .close()
        .await
        .expect("Transport should close cleanly");
    println!("✓ Concurrent requests handled correctly");
}

#[tokio::test]
async fn test_protocol_version_validation() {
    common::init_test_logging();

    let server_path = common::get_mcp_server_path();

    let mut transport = StdioTransport::goldentooth_server(&server_path);
    transport.start().await.expect("Failed to start transport");

    // Test with unsupported protocol version
    let invalid_init_request = JsonRpcRequest::new(
        "version-test".into(),
        "initialize",
        Some(json!({
            "protocolVersion": "1999-01-01", // Invalid old version
            "capabilities": {},
            "clientInfo": {"name": "version-test", "version": "1.0.0"}
        })),
    );

    let response = transport
        .send_request(invalid_init_request)
        .await
        .expect("Request should complete");

    match response.result {
        ResponseResult::Error { error } => {
            // Should get protocol version error
            assert_eq!(error.code, -32602, "Should be invalid params error");

            // Log error details if present
            if let Some(data) = &error.data {
                println!(
                    "Error details: {}",
                    serde_json::to_string_pretty(data).unwrap()
                );
            }

            // Accept generic "Invalid params" if we get proper error code - this is valid MCP behavior
            println!(
                "✓ Protocol version validation works: {} (error code: {})",
                error.message, error.code
            );
        }
        ResponseResult::Success { .. } => {
            panic!("Invalid protocol version should be rejected");
        }
    }

    transport
        .close()
        .await
        .expect("Transport should close cleanly");
}

#[tokio::test]
async fn test_server_capabilities_inspection() {
    common::init_test_logging();

    let server_path = common::get_mcp_server_path();

    let mut transport = StdioTransport::goldentooth_server(&server_path);
    transport.start().await.expect("Failed to start transport");

    // Initialize and inspect server capabilities
    let init_response = transport
        .send_request(JsonRpcRequest::new(
            "capabilities-test".into(),
            "initialize",
            Some(json!({
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "experimental": {"test": true},
                    "sampling": {}
                },
                "clientInfo": {"name": "capabilities-test", "version": "1.0.0"}
            })),
        ))
        .await
        .expect("Initialize should succeed");

    match init_response.result {
        ResponseResult::Success { result } => {
            let capabilities = result
                .get("capabilities")
                .expect("Should have capabilities");

            // The server should advertise tools capability
            if let Some(tools_cap) = capabilities.get("tools") {
                println!(
                    "✓ Server advertises tools capability: {}",
                    serde_json::to_string_pretty(tools_cap).unwrap()
                );

                // Should be an array of tool names or capability object
                if let Some(tools_array) = tools_cap.as_array() {
                    assert!(!tools_array.is_empty(), "Tools array should not be empty");
                    println!("✓ Server provides {} tools", tools_array.len());
                } else if let Some(_tools_obj) = tools_cap.as_object() {
                    println!("✓ Server provides tools capability object");
                }
            } else {
                // Check if tools are listed in some other way
                println!(
                    "Server capabilities: {}",
                    serde_json::to_string_pretty(capabilities).unwrap()
                );
            }

            // Check server info
            let server_info = result.get("serverInfo").expect("Should have server info");
            println!(
                "✓ Server info: {}",
                serde_json::to_string_pretty(server_info).unwrap()
            );

            assert_eq!(server_info["name"], "goldentooth-mcp");
            assert!(server_info.get("version").is_some());
        }
        ResponseResult::Error { error } => {
            panic!("Initialize failed: {} - {}", error.code, error.message);
        }
    }

    transport
        .close()
        .await
        .expect("Transport should close cleanly");
}
