//! Integration tests for stdio transport with real MCP server

use goldentooth_agent::mcp::protocol::*;
use goldentooth_agent::mcp::transport::{StdioTransport, Transport};
use serde_json::json;
use std::path::PathBuf;

/// Build the MCP server binary for testing
async fn build_mcp_server() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mcp_server_dir = project_root
        .parent()
        .ok_or("Cannot find project parent directory")?
        .join("mcp-server");

    if !mcp_server_dir.exists() {
        return Err(format!("MCP server directory not found: {:?}", mcp_server_dir).into());
    }

    let server_binary = mcp_server_dir.join("target/release/goldentooth-mcp");
    if !server_binary.exists() {
        return Err(format!("MCP server binary not found: {:?}", server_binary).into());
    }

    Ok(server_binary)
}

#[tokio::test]
async fn test_stdio_connection_lifecycle() {
    // Initialize logging for test visibility
    let _ = goldentooth_agent::logging::init_with_level(log::LevelFilter::Debug);

    let server_path = build_mcp_server()
        .await
        .expect("Failed to find MCP server binary");
    let mut transport = StdioTransport::goldentooth_server(&server_path);

    // Initially not connected
    assert!(!transport.is_connected());

    // Start transport
    transport.start().await.expect("Failed to start transport");
    assert!(transport.is_connected());

    // Close transport
    transport.close().await.expect("Failed to close transport");
    assert!(!transport.is_connected());
}

#[tokio::test]
async fn test_stdio_mcp_handshake() {
    let _ = goldentooth_agent::logging::init_with_level(log::LevelFilter::Debug);

    let server_path = build_mcp_server()
        .await
        .expect("Failed to find MCP server binary");
    let mut transport = StdioTransport::goldentooth_server(&server_path);

    // Start the transport
    transport.start().await.expect("Failed to start transport");

    // Send initialize request
    let init_request = JsonRpcRequest::new(
        "init-test".into(),
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
        .send_request(init_request.clone())
        .await
        .expect("Initialize request failed");

    // Verify response structure
    assert_eq!(response.jsonrpc, "2.0");
    assert_eq!(response.id, RequestId::String("init-test".to_string()));

    match response.result {
        ResponseResult::Success { result } => {
            // Should have required MCP initialize response fields
            assert!(result.get("protocolVersion").is_some());
            assert!(result.get("capabilities").is_some());
            assert!(result.get("serverInfo").is_some());

            // Protocol version should match
            assert_eq!(result["protocolVersion"], "2025-06-18");

            println!(
                "✓ Initialize response: {}",
                serde_json::to_string_pretty(&result).unwrap()
            );
        }
        ResponseResult::Error { error } => {
            eprintln!("Initialize request sent:");
            eprintln!("{}", serde_json::to_string_pretty(&init_request).unwrap());
            eprintln!("Error received: {} - {}", error.code, error.message);
            if let Some(data) = &error.data {
                eprintln!(
                    "Error data: {}",
                    serde_json::to_string_pretty(data).unwrap()
                );
            }
            panic!(
                "Initialize failed with error: {} - {}",
                error.code, error.message
            );
        }
    }

    // Send initialized notification to complete handshake
    let initialized_notification = JsonRpcNotification::new("initialized", Some(json!({})));
    transport
        .send_notification(initialized_notification)
        .await
        .expect("Failed to send initialized notification");

    println!("✓ MCP handshake completed successfully");

    transport.close().await.expect("Failed to close transport");
}

#[tokio::test]
async fn test_stdio_tools_discovery() {
    let _ = goldentooth_agent::logging::init_with_level(log::LevelFilter::Debug);

    let server_path = build_mcp_server()
        .await
        .expect("Failed to find MCP server binary");
    let mut transport = StdioTransport::goldentooth_server(&server_path);

    // Start and complete MCP handshake
    transport.start().await.expect("Failed to start transport");

    // Initialize
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
    let tools_request = JsonRpcRequest::new("tools-discover".into(), "tools/list", Some(json!({})));

    let response = transport
        .send_request(tools_request)
        .await
        .expect("Tools list request failed");

    match response.result {
        ResponseResult::Success { result } => {
            println!(
                "✓ Tools response: {}",
                serde_json::to_string_pretty(&result).unwrap()
            );

            // Should have tools array
            let tools = result.get("tools").expect("Missing tools in response");
            let tools_array = tools.as_array().expect("Tools should be an array");

            // Get tool names
            let tool_names: Vec<String> = tools_array
                .iter()
                .map(|tool| tool["name"].as_str().unwrap().to_string())
                .collect();

            println!("✓ Available tools: {:?}", tool_names);

            // Check for key Goldentooth cluster management tools that should be available
            let required_tools = vec!["cluster_ping", "cluster_status", "service_status"];

            for required_tool in required_tools {
                assert!(
                    tool_names.contains(&required_tool.to_string()),
                    "Missing required tool: {}",
                    required_tool
                );
            }

            // Verify we have at least a reasonable number of tools
            assert!(
                tool_names.len() >= 3,
                "Expected at least 3 tools, got {}",
                tool_names.len()
            );

            println!("✓ All expected tools found!");
        }
        ResponseResult::Error { error } => {
            panic!(
                "Tools list failed with error: {} - {}",
                error.code, error.message
            );
        }
    }

    transport.close().await.expect("Failed to close transport");
}
