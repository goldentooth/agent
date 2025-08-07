use async_trait::async_trait;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;

use crate::error::AgentError;

/// Types of commands that tools can execute
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum CommandType {
    /// Node connectivity and status
    NodePing,
    NodeStatus,
    NodeUptime,

    /// Service management
    ServiceStatus,
    ServiceStart,
    ServiceStop,
    ServiceRestart,
    ServiceLogs,

    /// Resource monitoring
    ResourceUsage,
    ProcessList,

    /// Kubernetes operations
    PodsList,
    PodStatus,
    PodLogs,
    ServicesList,
    DeploymentStatus,

    /// Security operations
    CertificateStatus,
    VaultStatus,
    AccessControlCheck,

    /// Network operations
    PortScan,
    ConnectivityTest,
    NetworkStats,

    /// System operations
    ExecuteCommand,
    FileTransfer,
    ConfigurationRead,
    ConfigurationWrite,

    /// Custom command
    Custom(String),
}

/// Command parameters for tool execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCommand {
    /// Type of command to execute
    pub command_type: CommandType,

    /// Target node (if applicable)
    pub target_node: Option<String>,

    /// Command parameters
    pub parameters: HashMap<String, String>,

    /// Execution timeout
    pub timeout: Option<Duration>,

    /// Whether to execute as root
    pub as_root: bool,
}

impl ToolCommand {
    /// Create a new tool command
    #[must_use]
    pub fn new(command_type: CommandType) -> Self {
        Self {
            command_type,
            target_node: None,
            parameters: HashMap::new(),
            timeout: Some(Duration::from_secs(30)),
            as_root: false,
        }
    }

    /// Set target node for the command
    #[must_use]
    pub fn with_node(mut self, node: impl Into<String>) -> Self {
        self.target_node = Some(node.into());
        self
    }

    /// Add a parameter to the command
    #[must_use]
    pub fn with_parameter(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.parameters.insert(key.into(), value.into());
        self
    }

    /// Set execution timeout
    #[must_use]
    pub fn with_timeout(mut self, timeout: Duration) -> Self {
        self.timeout = Some(timeout);
        self
    }

    /// Set whether to execute as root
    #[must_use]
    pub fn as_root(mut self, as_root: bool) -> Self {
        self.as_root = as_root;
        self
    }
}

/// Result of tool execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolResult {
    /// Whether the command was successful
    pub success: bool,

    /// Exit code (for shell commands)
    pub exit_code: Option<i32>,

    /// Standard output
    pub stdout: String,

    /// Standard error
    pub stderr: String,

    /// Execution duration
    pub duration: Duration,

    /// Timestamp when executed
    pub timestamp: DateTime<Utc>,

    /// Node where command was executed
    pub node: Option<String>,

    /// Structured data (for non-text results)
    pub data: Option<serde_json::Value>,
}

impl ToolResult {
    /// Create a successful result
    #[must_use]
    pub fn success(stdout: String) -> Self {
        Self {
            success: true,
            exit_code: Some(0),
            stdout,
            stderr: String::new(),
            duration: Duration::from_millis(0),
            timestamp: Utc::now(),
            node: None,
            data: None,
        }
    }

    /// Create a failed result
    #[must_use]
    pub fn failure(stderr: String, exit_code: Option<i32>) -> Self {
        Self {
            success: false,
            exit_code,
            stdout: String::new(),
            stderr,
            duration: Duration::from_millis(0),
            timestamp: Utc::now(),
            node: None,
            data: None,
        }
    }

    /// Set execution duration
    #[must_use]
    pub fn with_duration(mut self, duration: Duration) -> Self {
        self.duration = duration;
        self
    }

    /// Set the node where command was executed
    #[must_use]
    pub fn on_node(mut self, node: impl Into<String>) -> Self {
        self.node = Some(node.into());
        self
    }

    /// Set structured data
    #[must_use]
    pub fn with_data(mut self, data: serde_json::Value) -> Self {
        self.data = Some(data);
        self
    }
}

/// Context for tool execution
#[derive(Debug, Clone)]
pub struct ToolExecutionContext {
    /// Configuration for cluster connections
    pub cluster_config: HashMap<String, String>,

    /// Authentication tokens/credentials
    pub credentials: HashMap<String, String>,

    /// Execution environment variables
    pub environment: HashMap<String, String>,

    /// Whether to use dry-run mode
    pub dry_run: bool,

    /// Default timeout for operations
    pub default_timeout: Duration,
}

impl ToolExecutionContext {
    /// Create a new execution context
    #[must_use]
    pub fn new() -> Self {
        Self {
            cluster_config: HashMap::new(),
            credentials: HashMap::new(),
            environment: HashMap::new(),
            dry_run: false,
            default_timeout: Duration::from_secs(30),
        }
    }

    /// Set cluster configuration
    #[must_use]
    pub fn with_cluster_config(mut self, config: HashMap<String, String>) -> Self {
        self.cluster_config = config;
        self
    }

    /// Add a configuration value
    #[must_use]
    pub fn with_config(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.cluster_config.insert(key.into(), value.into());
        self
    }

    /// Set dry-run mode
    #[must_use]
    pub fn dry_run(mut self, dry_run: bool) -> Self {
        self.dry_run = dry_run;
        self
    }
}

impl Default for ToolExecutionContext {
    fn default() -> Self {
        Self::new()
    }
}

/// Errors that can occur during tool execution
#[derive(Debug, PartialEq, thiserror::Error)]
pub enum ToolError {
    #[error("Command execution failed: {0}")]
    ExecutionFailed(String),

    #[error("Connection failed: {0}")]
    ConnectionFailed(String),

    #[error("Authentication failed: {0}")]
    AuthenticationFailed(String),

    #[error("Configuration error: {0}")]
    ConfigurationError(String),

    #[error("Timeout occurred after {0:?}")]
    Timeout(Duration),

    #[error("Permission denied: {0}")]
    PermissionDenied(String),

    #[error("Tool not available: {0}")]
    ToolNotAvailable(String),

    #[error("Invalid command: {0}")]
    InvalidCommand(String),

    #[error("Parsing error: {0}")]
    ParsingError(String),

    #[error("Network error: {0}")]
    NetworkError(String),
}

impl From<ToolError> for AgentError {
    fn from(error: ToolError) -> Self {
        AgentError::ToolExecutionFailed(error.to_string())
    }
}

impl From<std::io::Error> for ToolError {
    fn from(error: std::io::Error) -> Self {
        ToolError::ExecutionFailed(format!("IO error: {error}"))
    }
}

/// Core trait for cluster management tools
#[async_trait]
pub trait ClusterTool: Send + Sync {
    /// Tool name for identification
    fn name(&self) -> &'static str;

    /// Tool description
    fn description(&self) -> &'static str;

    /// Commands supported by this tool
    fn supported_commands(&self) -> Vec<CommandType>;

    /// Execute a command using this tool
    async fn execute(
        &self,
        command: ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError>;

    /// Check if the tool is available and properly configured
    async fn health_check(&self, context: &ToolExecutionContext) -> Result<bool, ToolError>;

    /// Get tool-specific configuration requirements
    fn required_config(&self) -> Vec<String> {
        Vec::new()
    }

    /// Validate command before execution
    ///
    /// # Errors
    ///
    /// Returns `ToolError::InvalidCommand` if the command type is not supported by this tool.
    fn validate_command(&self, command: &ToolCommand) -> Result<(), ToolError> {
        let supported = self.supported_commands();
        if !supported.contains(&command.command_type) {
            return Err(ToolError::InvalidCommand(format!(
                "Command {:?} not supported by tool {}",
                command.command_type,
                self.name()
            )));
        }
        Ok(())
    }
}

/// Concrete tool enum to handle different tool types
#[derive(Debug, Clone)]
pub enum Tool {
    Ssh(crate::core::tools::SshTool),
    Kubectl(crate::core::tools::KubectlTool),
    Goldentooth(crate::core::tools::GoldentoothTool),
    HealthCheck(crate::core::tools::HealthCheckTool),
}

impl Tool {
    /// Get the tool name
    #[must_use]
    pub fn name(&self) -> &'static str {
        match self {
            Tool::Ssh(tool) => tool.name(),
            Tool::Kubectl(tool) => tool.name(),
            Tool::Goldentooth(tool) => tool.name(),
            Tool::HealthCheck(tool) => tool.name(),
        }
    }

    /// Get the tool description
    #[must_use]
    pub fn description(&self) -> &'static str {
        match self {
            Tool::Ssh(tool) => tool.description(),
            Tool::Kubectl(tool) => tool.description(),
            Tool::Goldentooth(tool) => tool.description(),
            Tool::HealthCheck(tool) => tool.description(),
        }
    }

    /// Get supported commands
    #[must_use]
    pub fn supported_commands(&self) -> Vec<CommandType> {
        match self {
            Tool::Ssh(tool) => tool.supported_commands(),
            Tool::Kubectl(tool) => tool.supported_commands(),
            Tool::Goldentooth(tool) => tool.supported_commands(),
            Tool::HealthCheck(tool) => tool.supported_commands(),
        }
    }

    /// Execute a command using this tool
    ///
    /// # Errors
    ///
    /// Returns `ToolError` if the command execution fails for any reason.
    pub async fn execute(
        &self,
        command: ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        match self {
            Tool::Ssh(tool) => tool.execute(command, context).await,
            Tool::Kubectl(tool) => tool.execute(command, context).await,
            Tool::Goldentooth(tool) => tool.execute(command, context).await,
            Tool::HealthCheck(tool) => tool.execute(command, context).await,
        }
    }

    /// Check if the tool is available
    ///
    /// # Errors
    ///
    /// Returns `ToolError` if the health check fails.
    pub async fn health_check(&self, context: &ToolExecutionContext) -> Result<bool, ToolError> {
        match self {
            Tool::Ssh(tool) => tool.health_check(context).await,
            Tool::Kubectl(tool) => tool.health_check(context).await,
            Tool::Goldentooth(tool) => tool.health_check(context).await,
            Tool::HealthCheck(tool) => tool.health_check(context).await,
        }
    }
}

/// Registry for managing cluster tools
#[derive(Debug, Clone)]
pub struct ToolRegistry {
    tools: HashMap<String, Tool>,
}

impl ToolRegistry {
    /// Create a new tool registry
    #[must_use]
    pub fn new() -> Self {
        Self {
            tools: HashMap::new(),
        }
    }

    /// Create a registry with default tools
    #[must_use]
    pub fn with_default_tools() -> Self {
        let mut registry = Self::new();

        registry.register_tool(Tool::Ssh(crate::core::tools::SshTool::new()));
        registry.register_tool(Tool::Kubectl(crate::core::tools::KubectlTool::new()));
        registry.register_tool(Tool::Goldentooth(crate::core::tools::GoldentoothTool::new()));
        registry.register_tool(Tool::HealthCheck(crate::core::tools::HealthCheckTool::new()));

        registry
    }

    /// Register a tool
    pub fn register_tool(&mut self, tool: Tool) {
        let name = tool.name().to_string();
        self.tools.insert(name, tool);
    }

    /// Get a tool by name
    #[must_use]
    pub fn get_tool(&self, name: &str) -> Option<&Tool> {
        self.tools.get(name)
    }

    /// Get all registered tools
    #[must_use]
    pub fn list_tools(&self) -> Vec<&str> {
        self.tools.keys().map(String::as_str).collect()
    }

    /// Find tools that support a specific command type
    #[must_use]
    pub fn find_tools_for_command(&self, command_type: &CommandType) -> Vec<&str> {
        self.tools
            .values()
            .filter(|tool| tool.supported_commands().contains(command_type))
            .map(Tool::name)
            .collect()
    }
}

impl Default for ToolRegistry {
    fn default() -> Self {
        Self::with_default_tools()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[derive(Debug, Clone)]
    struct MockTool {
        name: &'static str,
    }

    #[async_trait]
    impl ClusterTool for MockTool {
        fn name(&self) -> &'static str {
            self.name
        }

        fn description(&self) -> &'static str {
            "Mock tool for testing"
        }

        fn supported_commands(&self) -> Vec<CommandType> {
            vec![CommandType::NodePing, CommandType::NodeStatus]
        }

        async fn execute(
            &self,
            _command: ToolCommand,
            _context: &ToolExecutionContext,
        ) -> Result<ToolResult, ToolError> {
            Ok(ToolResult::success("Mock output".to_string()))
        }

        async fn health_check(&self, _context: &ToolExecutionContext) -> Result<bool, ToolError> {
            Ok(true)
        }
    }

    #[test]
    fn test_tool_command_builder() {
        let command = ToolCommand::new(CommandType::NodeStatus)
            .with_node("allyrion")
            .with_parameter("format", "json")
            .with_timeout(Duration::from_secs(60))
            .as_root(true);

        assert_eq!(command.command_type, CommandType::NodeStatus);
        assert_eq!(command.target_node, Some("allyrion".to_string()));
        assert_eq!(command.parameters.get("format"), Some(&"json".to_string()));
        assert_eq!(command.timeout, Some(Duration::from_secs(60)));
        assert!(command.as_root);
    }

    #[test]
    fn test_tool_result_builder() {
        let result = ToolResult::success("test output".to_string())
            .with_duration(Duration::from_millis(500))
            .on_node("allyrion");

        assert!(result.success);
        assert_eq!(result.stdout, "test output");
        assert_eq!(result.duration, Duration::from_millis(500));
        assert_eq!(result.node, Some("allyrion".to_string()));
    }

    #[test]
    fn test_execution_context_builder() {
        let mut config = HashMap::new();
        config.insert(
            "cluster_endpoint".to_string(),
            "https://api.goldentooth.net".to_string(),
        );

        let context = ToolExecutionContext::new()
            .with_cluster_config(config)
            .with_config("timeout", "30")
            .dry_run(true);

        assert_eq!(
            context.cluster_config.get("cluster_endpoint"),
            Some(&"https://api.goldentooth.net".to_string())
        );
        assert_eq!(
            context.cluster_config.get("timeout"),
            Some(&"30".to_string())
        );
        assert!(context.dry_run);
    }

    #[test]
    fn test_tool_registry() {
        // Since we can't use MockTool directly in the Tool enum,
        // let's test with the default registry
        let default_registry = ToolRegistry::default();

        assert!(default_registry.list_tools().len() >= 4);
        assert!(default_registry.list_tools().contains(&"ssh"));
        assert!(default_registry.list_tools().contains(&"kubectl"));
        assert!(default_registry.list_tools().contains(&"goldentooth"));
        assert!(default_registry.list_tools().contains(&"health_check"));

        let tool = default_registry.get_tool("ssh");
        assert!(tool.is_some());
        assert_eq!(tool.unwrap().name(), "ssh");
    }

    #[test]
    fn test_find_tools_for_command() {
        let registry = ToolRegistry::default();

        let tools = registry.find_tools_for_command(&CommandType::NodePing);
        assert!(tools.len() >= 2); // SSH and HealthCheck tools support NodePing
        assert!(tools.contains(&"ssh"));
        assert!(tools.contains(&"health_check"));

        let tools = registry.find_tools_for_command(&CommandType::PodsList);
        assert!(tools.contains(&"kubectl")); // Only kubectl supports PodsList
    }

    #[tokio::test]
    async fn test_mock_tool_execution() {
        let tool = MockTool { name: "test" };
        let context = ToolExecutionContext::new();
        let command = ToolCommand::new(CommandType::NodePing);

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert_eq!(result.stdout, "Mock output");
    }

    #[tokio::test]
    async fn test_tool_health_check() {
        let tool = MockTool { name: "test" };
        let context = ToolExecutionContext::new();

        let result = tool.health_check(&context).await;
        assert!(result.is_ok());
        assert!(result.unwrap());
    }

    #[test]
    fn test_tool_validation() {
        let tool = MockTool { name: "test" };
        let valid_command = ToolCommand::new(CommandType::NodePing);
        let invalid_command = ToolCommand::new(CommandType::PodsList);

        assert!(tool.validate_command(&valid_command).is_ok());
        assert!(tool.validate_command(&invalid_command).is_err());
    }
}
