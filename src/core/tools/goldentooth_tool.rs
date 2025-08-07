use async_trait::async_trait;
use std::process::Stdio;
use std::time::{Duration, Instant};
use tokio::process::Command;
use tokio::time::timeout;

use super::cluster_tool::{
    ClusterTool, CommandType, ToolCommand, ToolError, ToolExecutionContext, ToolResult,
};

/// Goldentooth CLI tool for cluster management operations
#[derive(Debug, Clone)]
pub struct GoldentoothTool {
    /// goldentooth binary path
    goldentooth_path: String,
    /// Default goldentooth options
    goldentooth_options: Vec<String>,
}

impl GoldentoothTool {
    /// Create a new goldentooth tool with default configuration
    #[must_use]
    pub fn new() -> Self {
        Self {
            goldentooth_path: "goldentooth".to_string(),
            goldentooth_options: Vec::new(),
        }
    }

    /// Create goldentooth tool with custom binary path
    #[must_use]
    pub fn with_path(goldentooth_path: impl Into<String>) -> Self {
        Self {
            goldentooth_path: goldentooth_path.into(),
            goldentooth_options: Vec::new(),
        }
    }

    /// Execute a goldentooth command
    async fn execute_goldentooth_command(
        &self,
        args: Vec<String>,
        context: &ToolExecutionContext,
        timeout_duration: Duration,
    ) -> Result<ToolResult, ToolError> {
        let start_time = Instant::now();

        // Handle dry run mode
        if context.dry_run {
            let full_command = format!("{} {}", self.goldentooth_path, args.join(" "));
            return Ok(
                ToolResult::success(format!("[DRY RUN] Would execute: {full_command}"))
                    .with_duration(Duration::from_millis(1)),
            );
        }

        // Build goldentooth command arguments
        let mut gt_args = self.goldentooth_options.clone();
        gt_args.extend(args);

        // Execute goldentooth command
        let mut cmd = Command::new(&self.goldentooth_path);
        cmd.args(&gt_args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        // Set environment variables from context
        for (key, value) in &context.environment {
            cmd.env(key, value);
        }

        // Set GOLDENTOOTH_ANSIBLE_PATH if specified in config
        if let Some(ansible_path) = context.cluster_config.get("ansible_path") {
            cmd.env("GOLDENTOOTH_ANSIBLE_PATH", ansible_path);
        }

        let child = cmd.spawn().map_err(|e| {
            ToolError::ExecutionFailed(format!("Failed to spawn goldentooth command: {e}"))
        })?;

        let output = timeout(timeout_duration, child.wait_with_output())
            .await
            .map_err(|_| ToolError::Timeout(timeout_duration))?
            .map_err(|e| {
                ToolError::ExecutionFailed(format!("goldentooth command execution failed: {e}"))
            })?;

        let duration = start_time.elapsed();
        let exit_code = output.status.code();
        let success = output.status.success();
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        let result = if success {
            ToolResult::success(stdout)
        } else {
            ToolResult::failure(stderr, exit_code)
        };

        Ok(result.with_duration(duration))
    }

    /// Ping all nodes
    async fn ping_all_nodes(
        &self,
        context: &ToolExecutionContext,
        timeout_duration: Duration,
    ) -> Result<ToolResult, ToolError> {
        let args = vec!["ping".to_string(), "all".to_string()];
        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Get node uptime
    async fn get_node_uptime(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let default_node = "all".to_string();
        let node = command.target_node.as_ref().unwrap_or(&default_node);

        let args = vec!["uptime".to_string(), node.clone()];
        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Execute shell command on nodes
    async fn execute_shell_command(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let default_node = "all".to_string();
        let node = command.target_node.as_ref().unwrap_or(&default_node);

        let shell_command = command.parameters.get("command").ok_or_else(|| {
            ToolError::InvalidCommand("command parameter is required".to_string())
        })?;

        let mut args = vec!["exec".to_string(), node.clone()];

        // Add root flag if needed
        if command.as_root {
            args.push("--root".to_string());
        }

        args.push(shell_command.clone());

        let timeout_duration = command.timeout.unwrap_or(Duration::from_secs(120));

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Get service status
    async fn get_service_status(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let service = command.parameters.get("service").ok_or_else(|| {
            ToolError::InvalidCommand("service parameter is required".to_string())
        })?;

        let default_node = "all".to_string();
        let node = command.target_node.as_ref().unwrap_or(&default_node);

        let shell_cmd = format!("systemctl status {service}");
        let args = vec!["exec".to_string(), node.clone(), shell_cmd];

        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Start service
    async fn start_service(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let service = command.parameters.get("service").ok_or_else(|| {
            ToolError::InvalidCommand("service parameter is required".to_string())
        })?;

        let node = command.target_node.as_ref().ok_or_else(|| {
            ToolError::InvalidCommand("Node must be specified for service operations".to_string())
        })?;

        let shell_cmd = format!("systemctl start {service}");
        let args = vec![
            "exec".to_string(),
            node.clone(),
            "--root".to_string(),
            shell_cmd,
        ];

        let timeout_duration = command.timeout.unwrap_or(Duration::from_secs(60));

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Stop service
    async fn stop_service(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let service = command.parameters.get("service").ok_or_else(|| {
            ToolError::InvalidCommand("service parameter is required".to_string())
        })?;

        let node = command.target_node.as_ref().ok_or_else(|| {
            ToolError::InvalidCommand("Node must be specified for service operations".to_string())
        })?;

        let shell_cmd = format!("systemctl stop {service}");
        let args = vec![
            "exec".to_string(),
            node.clone(),
            "--root".to_string(),
            shell_cmd,
        ];

        let timeout_duration = command.timeout.unwrap_or(Duration::from_secs(60));

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Restart service
    async fn restart_service(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let service = command.parameters.get("service").ok_or_else(|| {
            ToolError::InvalidCommand("service parameter is required".to_string())
        })?;

        let node = command.target_node.as_ref().ok_or_else(|| {
            ToolError::InvalidCommand("Node must be specified for service operations".to_string())
        })?;

        let shell_cmd = format!("systemctl restart {service}");
        let args = vec![
            "exec".to_string(),
            node.clone(),
            "--root".to_string(),
            shell_cmd,
        ];

        let timeout_duration = command.timeout.unwrap_or(Duration::from_secs(120));

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Get cluster configuration
    async fn get_cluster_config(
        &self,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let args = vec!["configure_cluster".to_string(), "--dry-run".to_string()];

        self.execute_goldentooth_command(args, context, Duration::from_secs(30))
            .await
    }

    /// Execute setup operation
    async fn execute_setup_operation(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let operation = command.parameters.get("operation").ok_or_else(|| {
            ToolError::InvalidCommand("operation parameter is required".to_string())
        })?;

        // Map common operations to goldentooth commands
        let gt_command = match operation.as_str() {
            "consul" => "setup_consul",
            "nomad" => "setup_nomad",
            "vault" => "setup_vault",
            "k8s" | "kubernetes" => "bootstrap_k8s",
            "ca" => "setup_cluster_ca",
            "mcp_server" => "setup_mcp_server",
            _ => {
                return Err(ToolError::InvalidCommand(format!(
                    "Unknown operation: {operation}"
                )));
            }
        };

        let args = vec![gt_command.to_string()];
        let timeout_duration = command.timeout.unwrap_or(Duration::from_secs(300)); // 5 minutes for setup operations

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }

    /// Execute custom goldentooth command
    async fn execute_custom_command(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let gt_args = command
            .parameters
            .get("args")
            .ok_or_else(|| ToolError::InvalidCommand("args parameter is required".to_string()))?;

        // Split args by whitespace (simple parsing - could be improved)
        let args: Vec<String> = gt_args.split_whitespace().map(String::from).collect();

        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_goldentooth_command(args, context, timeout_duration)
            .await
    }
}

impl Default for GoldentoothTool {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl ClusterTool for GoldentoothTool {
    fn name(&self) -> &'static str {
        "goldentooth"
    }

    fn description(&self) -> &'static str {
        "Goldentooth CLI tool for comprehensive cluster management and orchestration"
    }

    fn supported_commands(&self) -> Vec<CommandType> {
        vec![
            CommandType::NodePing,
            CommandType::NodeStatus,
            CommandType::NodeUptime,
            CommandType::ServiceStatus,
            CommandType::ServiceStart,
            CommandType::ServiceStop,
            CommandType::ServiceRestart,
            CommandType::ServiceLogs,
            CommandType::ResourceUsage,
            CommandType::ProcessList,
            CommandType::CertificateStatus,
            CommandType::VaultStatus,
            CommandType::NetworkStats,
            CommandType::ExecuteCommand,
            CommandType::ConfigurationRead,
            CommandType::Custom("setup".to_string()),
            CommandType::Custom("configure_cluster".to_string()),
        ]
    }

    async fn execute(
        &self,
        command: ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        self.validate_command(&command)?;

        match &command.command_type {
            CommandType::NodePing => {
                self.ping_all_nodes(context, command.timeout.unwrap_or(context.default_timeout))
                    .await
            }

            CommandType::NodeUptime => self.get_node_uptime(&command, context).await,

            CommandType::ServiceStatus => self.get_service_status(&command, context).await,

            CommandType::ServiceStart => self.start_service(&command, context).await,

            CommandType::ServiceStop => self.stop_service(&command, context).await,

            CommandType::ServiceRestart => self.restart_service(&command, context).await,

            CommandType::ExecuteCommand => self.execute_shell_command(&command, context).await,

            CommandType::Custom(op) if op == "setup" => {
                self.execute_setup_operation(&command, context).await
            }

            CommandType::Custom(op) if op == "configure_cluster" => {
                self.get_cluster_config(context).await
            }

            CommandType::Custom(_) => self.execute_custom_command(&command, context).await,

            _ => Err(ToolError::InvalidCommand(format!(
                "Command {:?} not implemented for goldentooth tool",
                command.command_type
            ))),
        }
    }

    async fn health_check(&self, context: &ToolExecutionContext) -> Result<bool, ToolError> {
        // Test goldentooth CLI availability by running ping command
        let args = vec!["ping".to_string(), "all".to_string()];
        let result = self
            .execute_goldentooth_command(args, context, Duration::from_secs(30))
            .await?;
        Ok(result.success)
    }

    fn required_config(&self) -> Vec<String> {
        vec![
            "ansible_path".to_string(), // GOLDENTOOTH_ANSIBLE_PATH
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_context() -> ToolExecutionContext {
        ToolExecutionContext::new()
            .with_config("ansible_path", "/path/to/goldentooth/ansible")
            .dry_run(true) // Use dry run for tests
    }

    #[test]
    fn test_goldentooth_tool_creation() {
        let tool = GoldentoothTool::new();
        assert_eq!(tool.name(), "goldentooth");
        assert_eq!(tool.goldentooth_path, "goldentooth");
        assert!(!tool.supported_commands().is_empty());
    }

    #[test]
    fn test_custom_goldentooth_path() {
        let tool = GoldentoothTool::with_path("/usr/local/bin/goldentooth");
        assert_eq!(tool.goldentooth_path, "/usr/local/bin/goldentooth");
    }

    #[test]
    fn test_supported_commands() {
        let tool = GoldentoothTool::new();
        let commands = tool.supported_commands();

        assert!(commands.contains(&CommandType::NodePing));
        assert!(commands.contains(&CommandType::ServiceStatus));
        assert!(commands.contains(&CommandType::ExecuteCommand));
        assert!(commands.contains(&CommandType::Custom("setup".to_string())));
        assert!(!commands.contains(&CommandType::PodsList)); // Kubernetes command
    }

    #[tokio::test]
    async fn test_node_ping_dry_run() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::NodePing);

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("[DRY RUN]"));
        assert!(result.stdout.contains("goldentooth ping all"));
    }

    #[tokio::test]
    async fn test_node_uptime_dry_run() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::NodeUptime).with_node("allyrion");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("goldentooth uptime allyrion"));
    }

    #[tokio::test]
    async fn test_service_status_dry_run() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ServiceStatus)
            .with_node("allyrion")
            .with_parameter("service", "consul");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("goldentooth exec allyrion"));
        assert!(result.stdout.contains("systemctl status consul"));
    }

    #[tokio::test]
    async fn test_service_start_dry_run() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ServiceStart)
            .with_node("allyrion")
            .with_parameter("service", "consul");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("exec allyrion --root"));
        assert!(result.stdout.contains("systemctl start consul"));
    }

    #[tokio::test]
    async fn test_setup_operation_dry_run() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::Custom("setup".to_string()))
            .with_parameter("operation", "consul");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("goldentooth setup_consul"));
    }

    #[tokio::test]
    async fn test_execute_command_dry_run() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ExecuteCommand)
            .with_node("allyrion")
            .with_parameter("command", "free -h")
            .as_root(true);

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("exec allyrion --root"));
        assert!(result.stdout.contains("free -h"));
    }

    #[tokio::test]
    async fn test_missing_service_parameter() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ServiceStatus).with_node("allyrion"); // No service parameter

        let result = tool.execute(command, &context).await;
        assert!(result.is_err());

        match result.unwrap_err() {
            ToolError::InvalidCommand(msg) => {
                assert!(msg.contains("service parameter is required"))
            }
            _ => panic!("Expected InvalidCommand error"),
        }
    }

    #[tokio::test]
    async fn test_missing_node_for_service_start() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command =
            ToolCommand::new(CommandType::ServiceStart).with_parameter("service", "consul"); // No node specified

        let result = tool.execute(command, &context).await;
        assert!(result.is_err());

        match result.unwrap_err() {
            ToolError::InvalidCommand(msg) => assert!(msg.contains("Node must be specified")),
            _ => panic!("Expected InvalidCommand error"),
        }
    }

    #[tokio::test]
    async fn test_unknown_setup_operation() {
        let tool = GoldentoothTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::Custom("setup".to_string()))
            .with_parameter("operation", "unknown_service");

        let result = tool.execute(command, &context).await;
        assert!(result.is_err());

        match result.unwrap_err() {
            ToolError::InvalidCommand(msg) => assert!(msg.contains("Unknown operation")),
            _ => panic!("Expected InvalidCommand error"),
        }
    }

    #[test]
    fn test_required_config() {
        let tool = GoldentoothTool::new();
        let required = tool.required_config();
        assert!(required.contains(&"ansible_path".to_string()));
    }

    #[test]
    fn test_tool_validation() {
        let tool = GoldentoothTool::new();
        let valid_command = ToolCommand::new(CommandType::NodePing);
        let invalid_command = ToolCommand::new(CommandType::PodsList);

        assert!(tool.validate_command(&valid_command).is_ok());
        assert!(tool.validate_command(&invalid_command).is_err());
    }
}
