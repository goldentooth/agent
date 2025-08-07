use async_trait::async_trait;
use std::collections::HashMap;
use std::process::Stdio;
use std::time::{Duration, Instant};
use tokio::process::Command;
use tokio::time::timeout;

use super::cluster_tool::{
    ClusterTool, CommandType, ToolCommand, ToolError, ToolExecutionContext, ToolResult,
};

/// SSH tool for direct node communication
#[derive(Debug, Clone)]
pub struct SshTool {
    /// Default SSH options
    ssh_options: Vec<String>,
    /// Node IP mappings
    node_ips: HashMap<String, String>,
}

impl SshTool {
    /// Create a new SSH tool with default configuration
    #[must_use]
    pub fn new() -> Self {
        let mut node_ips = HashMap::new();

        // Raspberry Pi nodes (based on Goldentooth cluster configuration)
        node_ips.insert("allyrion".to_string(), "10.4.0.10".to_string());
        node_ips.insert("bettley".to_string(), "10.4.0.11".to_string());
        node_ips.insert("cargyll".to_string(), "10.4.0.12".to_string());
        node_ips.insert("dalt".to_string(), "10.4.0.13".to_string());
        node_ips.insert("erenford".to_string(), "10.4.0.14".to_string());
        node_ips.insert("fenn".to_string(), "10.4.0.15".to_string());
        node_ips.insert("gardener".to_string(), "10.4.0.16".to_string());
        node_ips.insert("harlton".to_string(), "10.4.0.17".to_string());
        node_ips.insert("inchfield".to_string(), "10.4.0.18".to_string());
        node_ips.insert("jast".to_string(), "10.4.0.19".to_string());
        node_ips.insert("karstark".to_string(), "10.4.0.20".to_string());
        node_ips.insert("lipps".to_string(), "10.4.0.21".to_string());
        // x86 GPU node
        node_ips.insert("velaryon".to_string(), "10.4.0.30".to_string());

        Self {
            ssh_options: vec![
                "-o".to_string(),
                "ConnectTimeout=10".to_string(),
                "-o".to_string(),
                "BatchMode=yes".to_string(),
                "-o".to_string(),
                "StrictHostKeyChecking=no".to_string(),
                "-o".to_string(),
                "UserKnownHostsFile=/dev/null".to_string(),
                "-o".to_string(),
                "LogLevel=QUIET".to_string(),
            ],
            node_ips,
        }
    }

    /// Create SSH tool with custom node mappings
    #[must_use]
    pub fn with_nodes(node_ips: HashMap<String, String>) -> Self {
        Self {
            ssh_options: vec![
                "-o".to_string(),
                "ConnectTimeout=10".to_string(),
                "-o".to_string(),
                "BatchMode=yes".to_string(),
                "-o".to_string(),
                "StrictHostKeyChecking=no".to_string(),
                "-o".to_string(),
                "UserKnownHostsFile=/dev/null".to_string(),
                "-o".to_string(),
                "LogLevel=QUIET".to_string(),
            ],
            node_ips,
        }
    }

    /// Get IP address for a node
    fn get_node_ip(&self, node: &str) -> Result<&str, ToolError> {
        self.node_ips
            .get(node)
            .map(String::as_str)
            .ok_or_else(|| ToolError::ConfigurationError(format!("Unknown node: {node}")))
    }

    /// Execute a command via SSH on a specific node
    async fn execute_ssh_command(
        &self,
        node: &str,
        command: &str,
        context: &ToolExecutionContext,
        timeout_duration: Duration,
        as_root: bool,
    ) -> Result<ToolResult, ToolError> {
        let ip = self.get_node_ip(node)?;
        let start_time = Instant::now();

        // Get SSH user from context or use default
        let ssh_user = context
            .cluster_config
            .get("ssh_user")
            .map_or("pi", String::as_str);

        // Construct SSH command
        let final_command = if as_root {
            format!("sudo {command}")
        } else {
            command.to_string()
        };

        // Handle dry run mode
        if context.dry_run {
            return Ok(ToolResult::success(format!(
                "[DRY RUN] Would execute on {node} ({ip}): {final_command}"
            ))
            .with_duration(Duration::from_millis(1))
            .on_node(node));
        }

        // Build SSH command arguments
        let mut ssh_args = self.ssh_options.clone();
        ssh_args.push(format!("{ssh_user}@{ip}"));
        ssh_args.push(final_command);

        // Execute SSH command
        let mut cmd = Command::new("ssh");
        cmd.args(&ssh_args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        let child = cmd
            .spawn()
            .map_err(|e| ToolError::ExecutionFailed(format!("Failed to spawn ssh command: {e}")))?;

        let output = timeout(timeout_duration, child.wait_with_output())
            .await
            .map_err(|_| ToolError::Timeout(timeout_duration))?
            .map_err(|e| {
                ToolError::ExecutionFailed(format!("SSH command execution failed: {e}"))
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

        Ok(result.with_duration(duration).on_node(node))
    }

    /// Ping a node using SSH connectivity test
    async fn ping_node(
        &self,
        node: &str,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        self.execute_ssh_command(
            node,
            "echo 'SSH connection successful'",
            context,
            Duration::from_secs(10),
            false,
        )
        .await
    }

    /// Get node status information
    async fn get_node_status(
        &self,
        node: &str,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let command = "echo '{' && \
            echo '\"hostname\":\"'$(hostname)'\",' && \
            echo '\"uptime\":\"'$(uptime -p)'\",' && \
            echo '\"load_avg\":\"'$(cat /proc/loadavg | cut -d' ' -f1-3)'\",' && \
            echo '\"memory\":\"'$(free -h | grep '^Mem' | awk '{print $3\"/\"$2}')'\",' && \
            echo '\"disk\":\"'$(df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\" used)\"}')'\"' && \
            echo '}'";

        self.execute_ssh_command(node, command, context, Duration::from_secs(15), false)
            .await
    }

    /// Get service status
    async fn get_service_status(
        &self,
        node: &str,
        service: &str,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let command = format!("systemctl is-active {service} && systemctl is-enabled {service}");

        self.execute_ssh_command(node, &command, context, Duration::from_secs(10), false)
            .await
    }

    /// Get resource usage information
    async fn get_resource_usage(
        &self,
        node: &str,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let command = "echo '{' && \
            echo '\"cpu_percent\":\"'$(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)'\",' && \
            echo '\"memory_percent\":\"'$(free | grep '^Mem' | awk '{printf \"%.1f\", $3/$2 * 100.0}')'\",' && \
            echo '\"disk_percent\":\"'$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)'\",' && \
            echo '\"network_bytes\":\"'$(cat /proc/net/dev | grep -E '(eth0|wlan0|enp|wlp)' | head -1 | awk '{print $2+$10}')'\"' && \
            echo '}'";

        self.execute_ssh_command(node, command, context, Duration::from_secs(15), false)
            .await
    }

    /// Execute a custom command
    async fn execute_custom_command(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let node = command.target_node.as_ref().ok_or_else(|| {
            ToolError::InvalidCommand("Node must be specified for SSH commands".to_string())
        })?;

        let custom_command = command.parameters.get("command").ok_or_else(|| {
            ToolError::InvalidCommand("Command parameter is required".to_string())
        })?;

        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_ssh_command(
            node,
            custom_command,
            context,
            timeout_duration,
            command.as_root,
        )
        .await
    }
}

impl Default for SshTool {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl ClusterTool for SshTool {
    fn name(&self) -> &'static str {
        "ssh"
    }

    fn description(&self) -> &'static str {
        "SSH tool for direct node communication and command execution"
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
            CommandType::ResourceUsage,
            CommandType::ProcessList,
            CommandType::ExecuteCommand,
            CommandType::ConfigurationRead,
            CommandType::NetworkStats,
        ]
    }

    async fn execute(
        &self,
        command: ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        self.validate_command(&command)?;

        match command.command_type {
            CommandType::NodePing => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified for ping".to_string())
                })?;
                self.ping_node(node, context).await
            }

            CommandType::NodeStatus => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified for status".to_string())
                })?;
                self.get_node_status(node, context).await
            }

            CommandType::ServiceStatus => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand(
                        "Node must be specified for service status".to_string(),
                    )
                })?;
                let service = command.parameters.get("service").ok_or_else(|| {
                    ToolError::InvalidCommand("Service parameter is required".to_string())
                })?;
                self.get_service_status(node, service, context).await
            }

            CommandType::ServiceStart => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified".to_string())
                })?;
                let service = command.parameters.get("service").ok_or_else(|| {
                    ToolError::InvalidCommand("Service parameter is required".to_string())
                })?;
                let cmd = format!("systemctl start {service}");
                self.execute_ssh_command(node, &cmd, context, Duration::from_secs(30), true)
                    .await
            }

            CommandType::ServiceStop => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified".to_string())
                })?;
                let service = command.parameters.get("service").ok_or_else(|| {
                    ToolError::InvalidCommand("Service parameter is required".to_string())
                })?;
                let cmd = format!("systemctl stop {service}");
                self.execute_ssh_command(node, &cmd, context, Duration::from_secs(30), true)
                    .await
            }

            CommandType::ServiceRestart => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified".to_string())
                })?;
                let service = command.parameters.get("service").ok_or_else(|| {
                    ToolError::InvalidCommand("Service parameter is required".to_string())
                })?;
                let cmd = format!("systemctl restart {service}");
                self.execute_ssh_command(node, &cmd, context, Duration::from_secs(60), true)
                    .await
            }

            CommandType::ResourceUsage => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand(
                        "Node must be specified for resource usage".to_string(),
                    )
                })?;
                self.get_resource_usage(node, context).await
            }

            CommandType::ProcessList => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified".to_string())
                })?;
                let cmd = "ps aux --sort=-%cpu | head -20";
                self.execute_ssh_command(node, cmd, context, Duration::from_secs(15), false)
                    .await
            }

            CommandType::ExecuteCommand => self.execute_custom_command(&command, context).await,

            CommandType::ConfigurationRead => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified".to_string())
                })?;
                let file_path = command.parameters.get("file_path").ok_or_else(|| {
                    ToolError::InvalidCommand("file_path parameter is required".to_string())
                })?;
                let cmd = format!("cat {file_path}");
                self.execute_ssh_command(node, &cmd, context, Duration::from_secs(10), false)
                    .await
            }

            CommandType::NetworkStats => {
                let node = command.target_node.as_ref().ok_or_else(|| {
                    ToolError::InvalidCommand("Node must be specified".to_string())
                })?;
                let cmd = "ss -tuln | grep LISTEN";
                self.execute_ssh_command(node, cmd, context, Duration::from_secs(10), false)
                    .await
            }

            _ => Err(ToolError::InvalidCommand(format!(
                "Command {:?} not implemented for SSH tool",
                command.command_type
            ))),
        }
    }

    async fn health_check(&self, context: &ToolExecutionContext) -> Result<bool, ToolError> {
        // Test SSH connectivity to a known node (allyrion)
        if let Some(ip) = self.node_ips.get("allyrion") {
            let ssh_user = context
                .cluster_config
                .get("ssh_user")
                .map_or("pi", String::as_str);

            let mut ssh_args = self.ssh_options.clone();
            ssh_args.push(format!("{ssh_user}@{ip}"));
            ssh_args.push("echo 'health_check'".to_string());

            let mut cmd = Command::new("ssh");
            cmd.args(&ssh_args)
                .stdout(Stdio::piped())
                .stderr(Stdio::piped());

            match timeout(Duration::from_secs(10), cmd.spawn()?.wait_with_output()).await {
                Ok(Ok(output)) => Ok(output.status.success()),
                _ => Ok(false),
            }
        } else {
            Err(ToolError::ConfigurationError(
                "No nodes configured".to_string(),
            ))
        }
    }

    fn required_config(&self) -> Vec<String> {
        vec!["ssh_user".to_string()]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    fn create_test_tool() -> SshTool {
        let mut nodes = HashMap::new();
        nodes.insert("test-node".to_string(), "192.168.1.100".to_string());
        SshTool::with_nodes(nodes)
    }

    fn create_test_context() -> ToolExecutionContext {
        ToolExecutionContext::new()
            .with_config("ssh_user", "testuser")
            .dry_run(true) // Use dry run for tests to avoid actual SSH connections
    }

    #[test]
    fn test_ssh_tool_creation() {
        let tool = SshTool::new();
        assert_eq!(tool.name(), "ssh");
        assert!(!tool.supported_commands().is_empty());
        assert_eq!(tool.node_ips.len(), 13); // 12 Pi nodes + 1 x86 node
    }

    #[test]
    fn test_custom_nodes() {
        let tool = create_test_tool();
        assert_eq!(tool.get_node_ip("test-node"), Ok("192.168.1.100"));
        assert!(tool.get_node_ip("nonexistent").is_err());
    }

    #[test]
    fn test_supported_commands() {
        let tool = create_test_tool();
        let commands = tool.supported_commands();

        assert!(commands.contains(&CommandType::NodePing));
        assert!(commands.contains(&CommandType::NodeStatus));
        assert!(commands.contains(&CommandType::ExecuteCommand));
        assert!(!commands.contains(&CommandType::PodsList)); // Kubernetes command
    }

    #[tokio::test]
    async fn test_node_ping_dry_run() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::NodePing).with_node("test-node");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("[DRY RUN]"));
        assert_eq!(result.node, Some("test-node".to_string()));
    }

    #[tokio::test]
    async fn test_node_status_dry_run() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::NodeStatus).with_node("test-node");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("[DRY RUN]"));
    }

    #[tokio::test]
    async fn test_service_status_dry_run() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ServiceStatus)
            .with_node("test-node")
            .with_parameter("service", "nginx");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("systemctl is-active nginx"));
    }

    #[tokio::test]
    async fn test_custom_command_dry_run() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ExecuteCommand)
            .with_node("test-node")
            .with_parameter("command", "ls -la /tmp");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("ls -la /tmp"));
    }

    #[tokio::test]
    async fn test_missing_node_error() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::NodePing); // No node specified

        let result = tool.execute(command, &context).await;
        assert!(result.is_err());

        match result.unwrap_err() {
            ToolError::InvalidCommand(msg) => assert!(msg.contains("Node must be specified")),
            _ => panic!("Expected InvalidCommand error"),
        }
    }

    #[tokio::test]
    async fn test_missing_service_parameter() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ServiceStatus).with_node("test-node"); // No service parameter

        let result = tool.execute(command, &context).await;
        assert!(result.is_err());

        match result.unwrap_err() {
            ToolError::InvalidCommand(msg) => {
                assert!(msg.contains("Service parameter is required"))
            }
            _ => panic!("Expected InvalidCommand error"),
        }
    }

    #[test]
    fn test_required_config() {
        let tool = create_test_tool();
        let required = tool.required_config();
        assert!(required.contains(&"ssh_user".to_string()));
    }

    #[test]
    fn test_tool_validation() {
        let tool = create_test_tool();
        let valid_command = ToolCommand::new(CommandType::NodePing);
        let invalid_command = ToolCommand::new(CommandType::PodsList);

        assert!(tool.validate_command(&valid_command).is_ok());
        assert!(tool.validate_command(&invalid_command).is_err());
    }
}
