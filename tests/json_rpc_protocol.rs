//! Tests for JSON-RPC protocol message handling

#[allow(dead_code)]
mod common;

use goldentooth_agent::mcp::protocol::*;
use serde_json::json;

#[test]
fn test_json_rpc_request_creation_and_serialization() {
    let request = JsonRpcRequest::new(
        "test-123".into(),
        "initialize",
        Some(json!({
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })),
    );

    // Verify structure
    assert_eq!(request.jsonrpc, "2.0");
    assert_eq!(request.method, "initialize");
    assert_eq!(request.id, RequestId::String("test-123".to_string()));
    assert!(request.params.is_some());

    // Verify serialization
    let serialized = serde_json::to_string(&request).unwrap();
    assert!(serialized.contains(r#""jsonrpc":"2.0""#));
    assert!(serialized.contains(r#""method":"initialize""#));
    assert!(serialized.contains(r#""id":"test-123""#));
    assert!(serialized.contains(r#""protocolVersion":"2025-06-18""#));
}

#[test]
fn test_json_rpc_response_success_and_error() {
    // Test successful response
    let success_response = JsonRpcResponse::success(
        "req-1".into(),
        json!({
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "tools": {
                    "listChanged": false
                }
            }
        }),
    );

    assert_eq!(success_response.jsonrpc, "2.0");
    assert_eq!(success_response.id, RequestId::String("req-1".to_string()));
    match success_response.result {
        ResponseResult::Success { .. } => {}
        ResponseResult::Error { .. } => panic!("Expected success result"),
    }

    // Test error response
    let error_response =
        JsonRpcResponse::error("req-2".into(), JsonRpcError::new(-32602, "Invalid params"));

    match error_response.result {
        ResponseResult::Error { error } => {
            assert_eq!(error.code, -32602);
            assert_eq!(error.message, "Invalid params");
            assert!(error.data.is_none());
        }
        ResponseResult::Success { .. } => panic!("Expected error result"),
    }
}

#[test]
fn test_json_rpc_notification() {
    let notification = JsonRpcNotification::new("initialized", Some(json!({})));

    assert_eq!(notification.jsonrpc, "2.0");
    assert_eq!(notification.method, "initialized");
    assert!(notification.params.is_some());

    let serialized = serde_json::to_string(&notification).unwrap();
    assert!(serialized.contains(r#""method":"initialized""#));
    assert!(!serialized.contains("id")); // Notifications don't have IDs
}

#[test]
fn test_json_rpc_message_variants() {
    // Test request variant
    let request_json = r#"{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}"#;
    let message: JsonRpcMessage = serde_json::from_str(request_json).unwrap();
    match message {
        JsonRpcMessage::Request(req) => {
            assert_eq!(req.method, "tools/list");
            assert_eq!(req.id, RequestId::String("1".to_string()));
        }
        _ => panic!("Expected request message"),
    }

    // Test response variant
    let response_json = r#"{"jsonrpc":"2.0","id":"1","result":{"tools":[]}}"#;
    let message: JsonRpcMessage = serde_json::from_str(response_json).unwrap();
    match message {
        JsonRpcMessage::Response(resp) => {
            assert_eq!(resp.id, RequestId::String("1".to_string()));
            match resp.result {
                ResponseResult::Success { .. } => {}
                ResponseResult::Error { .. } => panic!("Expected success result"),
            }
        }
        _ => panic!("Expected response message"),
    }

    // Test notification variant
    let notification_json = r#"{"jsonrpc":"2.0","method":"logging/message","params":{"level":"info","message":"test"}}"#;
    let message: JsonRpcMessage = serde_json::from_str(notification_json).unwrap();
    match message {
        JsonRpcMessage::Notification(notif) => {
            assert_eq!(notif.method, "logging/message");
        }
        _ => panic!("Expected notification message"),
    }
}

#[test]
fn test_request_id_variants() {
    // String IDs
    let string_id: RequestId = "uuid-12345".into();
    assert_eq!(string_id.to_string(), "uuid-12345");

    // Numeric IDs
    let numeric_id: RequestId = 42i64.into();
    assert_eq!(numeric_id.to_string(), "42");

    // Serialization round-trip
    let original_string = RequestId::String("test".to_string());
    let json = serde_json::to_string(&original_string).unwrap();
    let parsed: RequestId = serde_json::from_str(&json).unwrap();
    assert_eq!(original_string, parsed);

    let original_number = RequestId::Number(123);
    let json = serde_json::to_string(&original_number).unwrap();
    let parsed: RequestId = serde_json::from_str(&json).unwrap();
    assert_eq!(original_number, parsed);
}

#[test]
fn test_mcp_initialize_structures() {
    let init_params = InitializeParams {
        protocol_version: "2025-06-18".to_string(),
        capabilities: ClientCapabilities {
            experimental: Some([("test".to_string(), json!("value"))].into_iter().collect()),
            sampling: None,
        },
        client_info: ClientInfo {
            name: "goldentooth-agent".to_string(),
            version: "0.1.0".to_string(),
        },
    };

    // Should serialize correctly
    let json = serde_json::to_string(&init_params).unwrap();
    assert!(json.contains(r#""protocolVersion":"2025-06-18""#));
    assert!(json.contains(r#""clientInfo""#));
    assert!(json.contains(r#""name":"goldentooth-agent""#));

    // Should deserialize correctly
    let parsed: InitializeParams = serde_json::from_str(&json).unwrap();
    assert_eq!(parsed.protocol_version, "2025-06-18");
    assert_eq!(parsed.client_info.name, "goldentooth-agent");
    assert!(parsed.capabilities.experimental.is_some());
}

#[test]
fn test_tool_structures() {
    let tool = Tool {
        name: "cluster_ping".to_string(),
        description: "Ping cluster nodes to check connectivity".to_string(),
        input_schema: json!({
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }),
    };

    let json = serde_json::to_string(&tool).unwrap();
    assert!(json.contains(r#""name":"cluster_ping""#));
    assert!(json.contains(r#""inputSchema""#));

    // Round-trip test
    let parsed: Tool = serde_json::from_str(&json).unwrap();
    assert_eq!(parsed.name, "cluster_ping");
    assert_eq!(
        parsed.description,
        "Ping cluster nodes to check connectivity"
    );
}

#[test]
fn test_json_rpc_error_codes() {
    // Standard JSON-RPC error codes
    let parse_error = JsonRpcError::new(-32700, "Parse error");
    assert_eq!(parse_error.code, -32700);

    let invalid_request = JsonRpcError::new(-32600, "Invalid Request");
    assert_eq!(invalid_request.code, -32600);

    let method_not_found = JsonRpcError::new(-32601, "Method not found");
    assert_eq!(method_not_found.code, -32601);

    let invalid_params = JsonRpcError::new(-32602, "Invalid params");
    assert_eq!(invalid_params.code, -32602);

    let internal_error = JsonRpcError::new(-32603, "Internal error");
    assert_eq!(internal_error.code, -32603);

    // Custom error with data
    let custom_error = JsonRpcError::with_data(
        -32000,
        "Authentication failed",
        json!({"details": "Invalid token"}),
    );
    assert_eq!(custom_error.code, -32000);
    assert!(custom_error.data.is_some());
}

#[test]
fn test_message_serialization_roundtrip() {
    // Test that we can serialize and deserialize all message types correctly
    let messages = vec![
        JsonRpcMessage::Request(JsonRpcRequest::new(
            "1".into(),
            "initialize",
            Some(json!({"protocolVersion": "2025-06-18"})),
        )),
        JsonRpcMessage::Response(JsonRpcResponse::success(
            "1".into(),
            json!({"protocolVersion": "2025-06-18", "capabilities": {}}),
        )),
        JsonRpcMessage::Response(JsonRpcResponse::error(
            "2".into(),
            JsonRpcError::new(-32602, "Invalid params"),
        )),
        JsonRpcMessage::Notification(JsonRpcNotification::new("initialized", Some(json!({})))),
    ];

    for message in messages {
        let json = serde_json::to_string(&message).unwrap();
        let parsed: JsonRpcMessage = serde_json::from_str(&json).unwrap();

        // Verify types match
        match (&message, &parsed) {
            (JsonRpcMessage::Request(_), JsonRpcMessage::Request(_)) => {}
            (JsonRpcMessage::Response(_), JsonRpcMessage::Response(_)) => {}
            (JsonRpcMessage::Notification(_), JsonRpcMessage::Notification(_)) => {}
            _ => panic!("Message type mismatch after roundtrip"),
        }
    }
}
