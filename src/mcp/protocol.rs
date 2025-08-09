//! MCP protocol types and JSON-RPC message handling

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

/// JSON-RPC 2.0 request message
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct JsonRpcRequest {
    pub jsonrpc: String,
    pub id: RequestId,
    pub method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub params: Option<Value>,
}

/// JSON-RPC 2.0 response message
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct JsonRpcResponse {
    pub jsonrpc: String,
    pub id: RequestId,
    #[serde(flatten)]
    pub result: ResponseResult,
}

/// JSON-RPC 2.0 notification message (no response expected)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct JsonRpcNotification {
    pub jsonrpc: String,
    pub method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub params: Option<Value>,
}

/// JSON-RPC message (request, response, or notification)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum JsonRpcMessage {
    Request(JsonRpcRequest),
    Response(JsonRpcResponse),
    Notification(JsonRpcNotification),
}

/// JSON-RPC request ID
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(untagged)]
pub enum RequestId {
    String(String),
    Number(i64),
}

/// JSON-RPC response result or error
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum ResponseResult {
    Success { result: Value },
    Error { error: JsonRpcError },
}

/// JSON-RPC error object
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct JsonRpcError {
    pub code: i32,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<Value>,
}

// MCP Protocol Types

/// MCP Initialize request parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InitializeParams {
    #[serde(rename = "protocolVersion")]
    pub protocol_version: String,
    pub capabilities: ClientCapabilities,
    #[serde(rename = "clientInfo")]
    pub client_info: ClientInfo,
}

/// MCP Initialize response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InitializeResult {
    #[serde(rename = "protocolVersion")]
    pub protocol_version: String,
    pub capabilities: ServerCapabilities,
    #[serde(rename = "serverInfo")]
    pub server_info: ServerInfo,
}

/// Client capabilities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClientCapabilities {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub experimental: Option<HashMap<String, Value>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sampling: Option<HashMap<String, Value>>,
}

/// Server capabilities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerCapabilities {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub experimental: Option<HashMap<String, Value>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub logging: Option<HashMap<String, Value>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub prompts: Option<PromptCapabilities>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub resources: Option<ResourceCapabilities>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tools: Option<ToolCapabilities>,
}

/// Prompt-related capabilities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PromptCapabilities {
    #[serde(default, rename = "listChanged")]
    pub list_changed: Option<bool>,
}

/// Resource-related capabilities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceCapabilities {
    #[serde(default)]
    pub subscribe: Option<bool>,
    #[serde(default, rename = "listChanged")]
    pub list_changed: Option<bool>,
}

/// Tool-related capabilities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCapabilities {
    #[serde(default, rename = "listChanged")]
    pub list_changed: Option<bool>,
}

/// Client information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClientInfo {
    pub name: String,
    pub version: String,
}

/// Server information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerInfo {
    pub name: String,
    pub version: String,
}

/// Tool definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tool {
    pub name: String,
    pub description: String,
    #[serde(rename = "inputSchema")]
    pub input_schema: Value,
}

/// Tool call parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCallParams {
    pub name: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub arguments: Option<Value>,
}

/// Tool call result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCallResult {
    pub content: Vec<ToolContent>,
    #[serde(default, rename = "isError")]
    pub is_error: Option<bool>,
}

/// Tool content (text or other formats)
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum ToolContent {
    #[serde(rename = "text")]
    Text { text: String },
}

impl JsonRpcRequest {
    /// Create a new JSON-RPC request
    pub fn new(id: RequestId, method: impl Into<String>, params: Option<Value>) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            method: method.into(),
            params,
        }
    }
}

impl JsonRpcResponse {
    /// Create a successful JSON-RPC response
    #[must_use]
    pub fn success(id: RequestId, result: Value) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: ResponseResult::Success { result },
        }
    }

    /// Create an error JSON-RPC response
    #[must_use]
    pub fn error(id: RequestId, error: JsonRpcError) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: ResponseResult::Error { error },
        }
    }
}

impl JsonRpcNotification {
    /// Create a new JSON-RPC notification
    pub fn new(method: impl Into<String>, params: Option<Value>) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            method: method.into(),
            params,
        }
    }
}

impl JsonRpcError {
    /// Create a new JSON-RPC error
    pub fn new(code: i32, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            data: None,
        }
    }

    /// Create a JSON-RPC error with additional data
    pub fn with_data(code: i32, message: impl Into<String>, data: Value) -> Self {
        Self {
            code,
            message: message.into(),
            data: Some(data),
        }
    }
}

impl From<String> for RequestId {
    fn from(s: String) -> Self {
        RequestId::String(s)
    }
}

impl From<&str> for RequestId {
    fn from(s: &str) -> Self {
        RequestId::String(s.to_string())
    }
}

impl From<i64> for RequestId {
    fn from(n: i64) -> Self {
        RequestId::Number(n)
    }
}

impl std::fmt::Display for RequestId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RequestId::String(s) => write!(f, "{s}"),
            RequestId::Number(n) => write!(f, "{n}"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_json_rpc_request_serialization() {
        let request = JsonRpcRequest::new(
            "test-id".into(),
            "initialize",
            Some(json!({
                "protocolVersion": "2025-06-18"
            })),
        );

        let serialized = serde_json::to_string(&request).unwrap();
        let expected = r#"{"jsonrpc":"2.0","id":"test-id","method":"initialize","params":{"protocolVersion":"2025-06-18"}}"#;

        assert_eq!(serialized, expected);
    }

    #[test]
    fn test_json_rpc_response_serialization() {
        let response = JsonRpcResponse::success(
            "test-id".into(),
            json!({
                "protocolVersion": "2025-06-18",
                "capabilities": {}
            }),
        );

        let serialized = serde_json::to_string(&response).unwrap();
        assert!(serialized.contains(r#""jsonrpc":"2.0""#));
        assert!(serialized.contains(r#""id":"test-id""#));
        assert!(serialized.contains("result"));
    }

    #[test]
    fn test_json_rpc_error_serialization() {
        let error_response = JsonRpcResponse::error(
            "test-id".into(),
            JsonRpcError::new(-32602, "Invalid params"),
        );

        let serialized = serde_json::to_string(&error_response).unwrap();
        assert!(serialized.contains(r#""error""#));
        assert!(serialized.contains(r#""code":-32602"#));
        assert!(serialized.contains(r#""message":"Invalid params""#));
    }

    #[test]
    fn test_json_rpc_notification_serialization() {
        let notification = JsonRpcNotification::new("initialized", Some(json!({})));

        let serialized = serde_json::to_string(&notification).unwrap();
        let expected = r#"{"jsonrpc":"2.0","method":"initialized","params":{}}"#;

        assert_eq!(serialized, expected);
    }

    #[test]
    fn test_json_rpc_message_deserialization() {
        // Test request deserialization
        let request_json = r#"{"jsonrpc":"2.0","id":"1","method":"test","params":{}}"#;
        let message: JsonRpcMessage = serde_json::from_str(request_json).unwrap();
        match message {
            JsonRpcMessage::Request(req) => {
                assert_eq!(req.method, "test");
                assert_eq!(req.id, RequestId::String("1".to_string()));
            }
            _ => panic!("Expected request message"),
        }

        // Test notification deserialization
        let notification_json = r#"{"jsonrpc":"2.0","method":"initialized"}"#;
        let message: JsonRpcMessage = serde_json::from_str(notification_json).unwrap();
        match message {
            JsonRpcMessage::Notification(notif) => {
                assert_eq!(notif.method, "initialized");
            }
            _ => panic!("Expected notification message"),
        }
    }

    #[test]
    fn test_mcp_initialize_params_serialization() {
        let params = InitializeParams {
            protocol_version: "2025-06-18".to_string(),
            capabilities: ClientCapabilities {
                experimental: Some(HashMap::new()),
                sampling: None,
            },
            client_info: ClientInfo {
                name: "test-client".to_string(),
                version: "1.0.0".to_string(),
            },
        };

        let serialized = serde_json::to_string(&params).unwrap();
        assert!(serialized.contains(r#""protocolVersion":"2025-06-18""#));
        assert!(serialized.contains(r#""clientInfo""#));
    }

    #[test]
    fn test_request_id_variants() {
        // String ID
        let string_id: RequestId = "test-123".into();
        assert_eq!(string_id.to_string(), "test-123");

        // Numeric ID
        let numeric_id: RequestId = 42i64.into();
        assert_eq!(numeric_id.to_string(), "42");
    }
}
