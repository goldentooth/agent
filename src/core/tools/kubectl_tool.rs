use async_trait::async_trait;
use std::process::Stdio;
use std::time::{Duration, Instant};
use tokio::process::Command;
use tokio::time::timeout;

use super::cluster_tool::{
    ClusterTool, CommandType, ToolCommand, ToolError, ToolExecutionContext, ToolResult,
};

/// Kubectl tool for Kubernetes operations
#[derive(Debug, Clone)]
pub struct KubectlTool {
    /// kubectl binary path
    kubectl_path: String,
    /// Default kubectl options
    kubectl_options: Vec<String>,
}

impl KubectlTool {
    /// Create a new kubectl tool with default configuration
    #[must_use]
    pub fn new() -> Self {
        Self {
            kubectl_path: "kubectl".to_string(),
            kubectl_options: vec!["--request-timeout=30s".to_string()],
        }
    }

    /// Create kubectl tool with custom binary path
    pub fn with_path(kubectl_path: impl Into<String>) -> Self {
        Self {
            kubectl_path: kubectl_path.into(),
            kubectl_options: vec!["--request-timeout=30s".to_string()],
        }
    }

    /// Execute a kubectl command
    async fn execute_kubectl_command(
        &self,
        args: Vec<String>,
        context: &ToolExecutionContext,
        timeout_duration: Duration,
    ) -> Result<ToolResult, ToolError> {
        let start_time = Instant::now();

        // Handle dry run mode
        if context.dry_run {
            let full_command = format!("{} {}", self.kubectl_path, args.join(" "));
            return Ok(
                ToolResult::success(format!("[DRY RUN] Would execute: {full_command}"))
                    .with_duration(Duration::from_millis(1)),
            );
        }

        // Build kubectl command arguments
        let mut kubectl_args = self.kubectl_options.clone();

        // Add kubeconfig if specified in context
        if let Some(kubeconfig) = context.cluster_config.get("kubeconfig") {
            kubectl_args.push("--kubeconfig".to_string());
            kubectl_args.push(kubeconfig.clone());
        }

        // Add namespace if specified in context
        if let Some(namespace) = context.cluster_config.get("namespace") {
            kubectl_args.push("--namespace".to_string());
            kubectl_args.push(namespace.clone());
        }

        kubectl_args.extend(args);

        // Execute kubectl command
        let mut cmd = Command::new(&self.kubectl_path);
        cmd.args(&kubectl_args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        let child = cmd.spawn().map_err(|e| {
            ToolError::ExecutionFailed(format!("Failed to spawn kubectl command: {e}"))
        })?;

        let output = timeout(timeout_duration, child.wait_with_output())
            .await
            .map_err(|_| ToolError::Timeout(timeout_duration))?
            .map_err(|e| {
                ToolError::ExecutionFailed(format!("kubectl command execution failed: {e}"))
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

    /// List pods
    async fn list_pods(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let mut args = vec!["get", "pods"];

        // Add output format
        let format = command
            .parameters
            .get("format")
            .map_or("wide", String::as_str);
        args.push("-o");
        args.push(format);

        // Add selector if specified
        if let Some(selector) = command.parameters.get("selector") {
            args.push("-l");
            args.push(selector);
        }

        // Add all namespaces flag if requested
        if command.parameters.get("all_namespaces") == Some(&"true".to_string()) {
            args.push("--all-namespaces");
        }

        let args: Vec<String> = args.into_iter().map(String::from).collect();
        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_kubectl_command(args, context, timeout_duration)
            .await
    }

    /// Get pod status
    async fn get_pod_status(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let pod_name = command
            .parameters
            .get("pod")
            .ok_or_else(|| ToolError::InvalidCommand("Pod name is required".to_string()))?;

        let args = vec![
            "get".to_string(),
            "pod".to_string(),
            pod_name.clone(),
            "-o".to_string(),
            "json".to_string(),
        ];

        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_kubectl_command(args, context, timeout_duration)
            .await
    }

    /// Get pod logs
    async fn get_pod_logs(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let pod_name = command
            .parameters
            .get("pod")
            .ok_or_else(|| ToolError::InvalidCommand("Pod name is required".to_string()))?;

        let mut args = vec!["logs".to_string(), pod_name.clone()];

        // Add container if specified
        if let Some(container) = command.parameters.get("container") {
            args.push("-c".to_string());
            args.push(container.clone());
        }

        // Add tail lines if specified
        if let Some(lines) = command.parameters.get("lines") {
            args.push("--tail".to_string());
            args.push(lines.clone());
        }

        // Add follow flag if specified
        if command.parameters.get("follow") == Some(&"true".to_string()) {
            args.push("-f".to_string());
        }

        // Add previous flag if specified
        if command.parameters.get("previous") == Some(&"true".to_string()) {
            args.push("-p".to_string());
        }

        let timeout_duration = command.timeout.unwrap_or(Duration::from_secs(60));

        self.execute_kubectl_command(args, context, timeout_duration)
            .await
    }

    /// List services
    async fn list_services(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let mut args = vec!["get", "services"];

        // Add output format
        let format = command
            .parameters
            .get("format")
            .map_or("wide", String::as_str);
        args.push("-o");
        args.push(format);

        // Add all namespaces flag if requested
        if command.parameters.get("all_namespaces") == Some(&"true".to_string()) {
            args.push("--all-namespaces");
        }

        let args: Vec<String> = args.into_iter().map(String::from).collect();
        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_kubectl_command(args, context, timeout_duration)
            .await
    }

    /// Get deployment status
    async fn get_deployment_status(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let deployment = command.parameters.get("deployment");

        let mut args = vec!["get".to_string(), "deployments".to_string()];

        if let Some(dep) = deployment {
            args.push(dep.clone());
        }

        args.push("-o".to_string());
        args.push("wide".to_string());

        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_kubectl_command(args, context, timeout_duration)
            .await
    }

    /// Execute custom kubectl command
    async fn execute_custom_command(
        &self,
        command: &ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let kubectl_args = command
            .parameters
            .get("args")
            .ok_or_else(|| ToolError::InvalidCommand("args parameter is required".to_string()))?;

        // Split args by whitespace (simple parsing - could be improved)
        let args: Vec<String> = kubectl_args.split_whitespace().map(String::from).collect();

        let timeout_duration = command.timeout.unwrap_or(context.default_timeout);

        self.execute_kubectl_command(args, context, timeout_duration)
            .await
    }
}

impl Default for KubectlTool {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl ClusterTool for KubectlTool {
    fn name(&self) -> &'static str {
        "kubectl"
    }

    fn description(&self) -> &'static str {
        "Kubectl tool for Kubernetes cluster operations and management"
    }

    fn supported_commands(&self) -> Vec<CommandType> {
        vec![
            CommandType::PodsList,
            CommandType::PodStatus,
            CommandType::PodLogs,
            CommandType::ServicesList,
            CommandType::DeploymentStatus,
            CommandType::ExecuteCommand,
        ]
    }

    async fn execute(
        &self,
        command: ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        self.validate_command(&command)?;

        match command.command_type {
            CommandType::PodsList => self.list_pods(&command, context).await,

            CommandType::PodStatus => self.get_pod_status(&command, context).await,

            CommandType::PodLogs => self.get_pod_logs(&command, context).await,

            CommandType::ServicesList => self.list_services(&command, context).await,

            CommandType::DeploymentStatus => self.get_deployment_status(&command, context).await,

            CommandType::ExecuteCommand => self.execute_custom_command(&command, context).await,

            _ => Err(ToolError::InvalidCommand(format!(
                "Command {:?} not implemented for kubectl tool",
                command.command_type
            ))),
        }
    }

    async fn health_check(&self, context: &ToolExecutionContext) -> Result<bool, ToolError> {
        // Test kubectl connectivity by getting cluster info
        let args = vec!["cluster-info".to_string()];
        let result = self
            .execute_kubectl_command(args, context, Duration::from_secs(10))
            .await?;
        Ok(result.success)
    }

    fn required_config(&self) -> Vec<String> {
        vec![
            // kubeconfig is optional - kubectl can use default locations
            // namespace is optional - kubectl can use default namespace
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_context() -> ToolExecutionContext {
        ToolExecutionContext::new()
            .with_config("kubeconfig", "/path/to/kubeconfig")
            .with_config("namespace", "default")
            .dry_run(true) // Use dry run for tests
    }

    #[test]
    fn test_kubectl_tool_creation() {
        let tool = KubectlTool::new();
        assert_eq!(tool.name(), "kubectl");
        assert_eq!(tool.kubectl_path, "kubectl");
        assert!(!tool.supported_commands().is_empty());
    }

    #[test]
    fn test_custom_kubectl_path() {
        let tool = KubectlTool::with_path("/usr/local/bin/kubectl");
        assert_eq!(tool.kubectl_path, "/usr/local/bin/kubectl");
    }

    #[test]
    fn test_supported_commands() {
        let tool = KubectlTool::new();
        let commands = tool.supported_commands();

        assert!(commands.contains(&CommandType::PodsList));
        assert!(commands.contains(&CommandType::PodStatus));
        assert!(commands.contains(&CommandType::PodLogs));
        assert!(commands.contains(&CommandType::ServicesList));
        assert!(commands.contains(&CommandType::DeploymentStatus));
        assert!(!commands.contains(&CommandType::NodePing)); // SSH command
    }

    #[tokio::test]
    async fn test_list_pods_dry_run() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::PodsList)
            .with_parameter("format", "json")
            .with_parameter("all_namespaces", "true");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("[DRY RUN]"));
        assert!(result.stdout.contains("kubectl"));
    }

    #[tokio::test]
    async fn test_pod_status_dry_run() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::PodStatus).with_parameter("pod", "test-pod");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("get pod test-pod"));
    }

    #[tokio::test]
    async fn test_pod_logs_dry_run() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::PodLogs)
            .with_parameter("pod", "test-pod")
            .with_parameter("container", "test-container")
            .with_parameter("lines", "100")
            .with_parameter("follow", "true");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("logs test-pod"));
        assert!(result.stdout.contains("-c test-container"));
        assert!(result.stdout.contains("--tail 100"));
        assert!(result.stdout.contains("-f"));
    }

    #[tokio::test]
    async fn test_services_list_dry_run() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ServicesList).with_parameter("format", "yaml");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("get services"));
        assert!(result.stdout.contains("-o yaml"));
    }

    #[tokio::test]
    async fn test_deployment_status_dry_run() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command =
            ToolCommand::new(CommandType::DeploymentStatus).with_parameter("deployment", "nginx");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("get deployments nginx"));
    }

    #[tokio::test]
    async fn test_custom_command_dry_run() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ExecuteCommand)
            .with_parameter("args", "get nodes -o wide");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("get nodes -o wide"));
    }

    #[tokio::test]
    async fn test_missing_pod_parameter() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::PodStatus); // No pod parameter

        let result = tool.execute(command, &context).await;
        assert!(result.is_err());

        match result.unwrap_err() {
            ToolError::InvalidCommand(msg) => assert!(msg.contains("Pod name is required")),
            _ => panic!("Expected InvalidCommand error"),
        }
    }

    #[tokio::test]
    async fn test_missing_args_parameter() {
        let tool = KubectlTool::new();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ExecuteCommand); // No args parameter

        let result = tool.execute(command, &context).await;
        assert!(result.is_err());

        match result.unwrap_err() {
            ToolError::InvalidCommand(msg) => assert!(msg.contains("args parameter is required")),
            _ => panic!("Expected InvalidCommand error"),
        }
    }

    #[test]
    fn test_tool_validation() {
        let tool = KubectlTool::new();
        let valid_command = ToolCommand::new(CommandType::PodsList);
        let invalid_command = ToolCommand::new(CommandType::NodePing);

        assert!(tool.validate_command(&valid_command).is_ok());
        assert!(tool.validate_command(&invalid_command).is_err());
    }
}
