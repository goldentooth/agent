use async_trait::async_trait;
use reqwest::Client;
use std::collections::HashMap;
use std::fmt::Write as _;
use std::time::{Duration, Instant};

use super::cluster_tool::{
    ClusterTool, CommandType, ToolCommand, ToolError, ToolExecutionContext, ToolResult,
};

/// Health check tool for service status monitoring using existing Goldentooth infrastructure
#[derive(Debug, Clone)]
pub struct HealthCheckTool {
    /// HTTP client for making requests
    client: Client,
    /// Node IP mappings (from the MCP server infrastructure)
    node_ips: HashMap<String, String>,
}

impl HealthCheckTool {
    /// Create a new health check tool with default configuration
    ///
    /// # Panics
    ///
    /// Panics if the HTTP client cannot be created.
    #[must_use]
    pub fn new() -> Self {
        let mut node_ips = HashMap::new();

        // Raspberry Pi nodes (consistent with existing infrastructure)
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

        let client = Client::builder()
            .timeout(Duration::from_secs(10))
            .build()
            .expect("Failed to create HTTP client");

        Self { client, node_ips }
    }

    /// Create health check tool with custom node mappings
    ///
    /// # Panics
    ///
    /// Panics if the HTTP client cannot be created.
    #[must_use]
    pub fn with_nodes(node_ips: HashMap<String, String>) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(10))
            .build()
            .expect("Failed to create HTTP client");

        Self { client, node_ips }
    }

    /// Get IP address for a node
    fn get_node_ip(&self, node: &str) -> Result<&str, ToolError> {
        self.node_ips
            .get(node)
            .map(String::as_str)
            .ok_or_else(|| ToolError::ConfigurationError(format!("Unknown node: {node}")))
    }

    /// Check node connectivity using ping/TCP connection
    async fn check_node_connectivity(
        &self,
        node: &str,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let start_time = Instant::now();
        let ip = self.get_node_ip(node)?;

        if context.dry_run {
            return Ok(ToolResult::success(format!(
                "[DRY RUN] Would check connectivity to {node} ({ip})"
            ))
            .with_duration(Duration::from_millis(1))
            .on_node(node));
        }

        // Try HTTP connection to node_exporter (port 9100) for health check
        let url = format!("http://{ip}:9100/metrics");

        match self.client.get(&url).send().await {
            Ok(response) => {
                let duration = start_time.elapsed();
                let success = response.status().is_success();

                if success {
                    Ok(ToolResult::success(format!(
                        "Node {node} ({ip}) is online - node_exporter responding"
                    ))
                    .with_duration(duration)
                    .on_node(node))
                } else {
                    Ok(ToolResult::failure(
                        format!("Node {node} ({ip}) returned HTTP {}", response.status()),
                        Some(i32::from(response.status().as_u16())),
                    )
                    .with_duration(duration)
                    .on_node(node))
                }
            }
            Err(e) => {
                let duration = start_time.elapsed();
                Ok(ToolResult::failure(
                    format!("Failed to connect to node {node} ({ip}): {e}"),
                    None,
                )
                .with_duration(duration)
                .on_node(node))
            }
        }
    }

    /// Get detailed node status from `node_exporter` metrics
    async fn get_node_status(
        &self,
        node: &str,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let start_time = Instant::now();
        let ip = self.get_node_ip(node)?;

        if context.dry_run {
            return Ok(ToolResult::success(format!(
                "[DRY RUN] Would get status from {node} ({ip})"
            ))
            .with_duration(Duration::from_millis(1))
            .on_node(node));
        }

        let url = format!("http://{ip}:9100/metrics");

        match self.client.get(&url).send().await {
            Ok(response) => {
                let duration = start_time.elapsed();

                if !response.status().is_success() {
                    return Ok(ToolResult::failure(
                        format!("Node {node} returned HTTP {}", response.status()),
                        Some(i32::from(response.status().as_u16())),
                    )
                    .with_duration(duration)
                    .on_node(node));
                }

                let metrics_text = response.text().await.map_err(|e| {
                    ToolError::NetworkError(format!("Failed to read metrics from {node}: {e}"))
                })?;

                // Parse key metrics from node_exporter output
                let status_info = Self::parse_node_metrics(&metrics_text);

                Ok(ToolResult::success(status_info)
                    .with_duration(duration)
                    .on_node(node))
            }
            Err(e) => {
                let duration = start_time.elapsed();
                Ok(ToolResult::failure(
                    format!("Failed to get status from node {node} ({ip}): {e}"),
                    None,
                )
                .with_duration(duration)
                .on_node(node))
            }
        }
    }

    /// Parse `node_exporter` metrics to extract useful status information
    fn parse_node_metrics(metrics_text: &str) -> String {
        let mut info = HashMap::new();

        for line in metrics_text.lines() {
            if line.starts_with('#') || line.trim().is_empty() {
                continue;
            }

            // Parse key metrics
            if line.starts_with("node_boot_time_seconds ") {
                if let Some(value_str) = line.split_whitespace().nth(1) {
                    if let Ok(boot_time) = value_str.parse::<f64>() {
                        #[allow(clippy::cast_precision_loss)]
                        let current_time = std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs() as f64;

                        let uptime_seconds = current_time - boot_time;
                        #[allow(clippy::cast_possible_truncation, clippy::cast_sign_loss)]
                        let uptime = uptime_seconds as u64;
                        info.insert("uptime".to_string(), format_uptime(uptime));
                    }
                }
            } else if line.starts_with("node_load1 ") {
                if let Some(value) = line.split_whitespace().nth(1) {
                    info.insert("load_1m".to_string(), value.to_string());
                }
            } else if line.starts_with("node_load5 ") {
                if let Some(value) = line.split_whitespace().nth(1) {
                    info.insert("load_5m".to_string(), value.to_string());
                }
            } else if line.starts_with("node_load15 ") {
                if let Some(value) = line.split_whitespace().nth(1) {
                    info.insert("load_15m".to_string(), value.to_string());
                }
            } else if line.starts_with("node_memory_MemTotal_bytes ") {
                if let Some(value_str) = line.split_whitespace().nth(1) {
                    if let Ok(bytes) = value_str.parse::<u64>() {
                        let mb = bytes / 1_048_576;
                        info.insert("memory_total_mb".to_string(), mb.to_string());
                    }
                }
            } else if line.starts_with("node_memory_MemAvailable_bytes ") {
                if let Some(value_str) = line.split_whitespace().nth(1) {
                    if let Ok(bytes) = value_str.parse::<u64>() {
                        let mb = bytes / 1_048_576;
                        info.insert("memory_available_mb".to_string(), mb.to_string());
                    }
                }
            }
        }

        // Format as JSON-like string
        let mut result = String::from("{\n");
        for (key, value) in &info {
            let _ = writeln!(result, "  \"{key}\": \"{value}\",");
        }

        // Add basic status
        result.push_str("  \"status\": \"online\",\n");
        result.push_str("  \"source\": \"node_exporter\"\n");
        result.push('}');

        result
    }

    /// Get resource usage for a node
    async fn get_resource_usage(
        &self,
        node: &str,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        let start_time = Instant::now();
        let ip = self.get_node_ip(node)?;

        if context.dry_run {
            return Ok(ToolResult::success(format!(
                "[DRY RUN] Would get resource usage from {node} ({ip})"
            ))
            .with_duration(Duration::from_millis(1))
            .on_node(node));
        }

        let url = format!("http://{ip}:9100/metrics");

        match self.client.get(&url).send().await {
            Ok(response) => {
                let duration = start_time.elapsed();

                if !response.status().is_success() {
                    return Ok(ToolResult::failure(
                        format!("Node {node} returned HTTP {}", response.status()),
                        Some(i32::from(response.status().as_u16())),
                    )
                    .with_duration(duration)
                    .on_node(node));
                }

                let metrics_text = response.text().await.map_err(|e| {
                    ToolError::NetworkError(format!("Failed to read metrics from {node}: {e}"))
                })?;

                let resource_info = Self::parse_resource_metrics(&metrics_text);

                Ok(ToolResult::success(resource_info)
                    .with_duration(duration)
                    .on_node(node))
            }
            Err(e) => {
                let duration = start_time.elapsed();
                Ok(ToolResult::failure(
                    format!("Failed to get resource usage from node {node} ({ip}): {e}"),
                    None,
                )
                .with_duration(duration)
                .on_node(node))
            }
        }
    }

    /// Parse resource usage metrics
    fn parse_resource_metrics(metrics_text: &str) -> String {
        let mut memory_total: Option<u64> = None;
        let mut memory_available: Option<u64> = None;
        let mut filesystems: Vec<String> = Vec::new();

        for line in metrics_text.lines() {
            if line.starts_with('#') || line.trim().is_empty() {
                continue;
            }

            if line.starts_with("node_memory_MemTotal_bytes ") {
                if let Some(value_str) = line.split_whitespace().nth(1) {
                    memory_total = value_str.parse().ok();
                }
            } else if line.starts_with("node_memory_MemAvailable_bytes ") {
                if let Some(value_str) = line.split_whitespace().nth(1) {
                    memory_available = value_str.parse().ok();
                }
            } else if line.starts_with("node_filesystem_size_bytes{") {
                // Extract filesystem info - simplified parsing
                if line.contains("mountpoint=\"/\"") && line.contains("device=\"/dev/") {
                    if let Some(value_str) = line.split_whitespace().last() {
                        if let Ok(bytes) = value_str.parse::<u64>() {
                            #[allow(clippy::cast_precision_loss)]
                            let gb = bytes as f64 / 1_073_741_824.0;
                            filesystems.push(format!("root: {gb:.1} GB total"));
                        }
                    }
                }
            }
        }

        let mut result = String::from("{\n");

        // Memory information
        if let (Some(total), Some(available)) = (memory_total, memory_available) {
            let used = total - available;
            #[allow(clippy::cast_precision_loss)]
            let percent = (used as f64 / total as f64) * 100.0;
            let _ = writeln!(result, "  \"memory_total_mb\": {},", total / 1_048_576);
            let _ = writeln!(result, "  \"memory_used_mb\": {},", used / 1_048_576);
            let _ = writeln!(
                result,
                "  \"memory_available_mb\": {},",
                available / 1_048_576
            );
            let _ = writeln!(result, "  \"memory_percent_used\": {percent:.1},");
        }

        // Filesystem information
        if !filesystems.is_empty() {
            result.push_str("  \"filesystems\": [\n");
            for (i, fs) in filesystems.iter().enumerate() {
                let _ = write!(result, "    \"{fs}\"");
                if i < filesystems.len() - 1 {
                    result.push(',');
                }
                result.push('\n');
            }
            result.push_str("  ],\n");
        }

        result.push_str("  \"source\": \"node_exporter\"\n");
        result.push('}');

        result
    }

    /// Check multiple nodes sequentially (simplified to avoid Send trait issues)
    async fn check_multiple_nodes(
        &self,
        nodes: Vec<String>,
        context: &ToolExecutionContext,
        check_type: &str,
    ) -> Result<ToolResult, ToolError> {
        let start_time = Instant::now();

        if context.dry_run {
            return Ok(ToolResult::success(format!(
                "[DRY RUN] Would check {check_type} for nodes: {}",
                nodes.join(", ")
            ))
            .with_duration(Duration::from_millis(1)));
        }

        // Execute checks sequentially
        let mut output = String::new();
        let mut all_successful = true;

        for node in nodes {
            let result = match check_type {
                "connectivity" => self.check_node_connectivity(&node, context).await,
                "status" => self.get_node_status(&node, context).await,
                "resources" => self.get_resource_usage(&node, context).await,
                _ => Err(ToolError::InvalidCommand(format!(
                    "Unknown check type: {check_type}"
                ))),
            };

            match result {
                Ok(tool_result) => {
                    let _ = writeln!(output, "Node {node}:");
                    output.push_str(&tool_result.stdout);
                    output.push_str("\n\n");
                    if !tool_result.success {
                        all_successful = false;
                    }
                }
                Err(e) => {
                    let _ = write!(output, "Node {node}: ERROR - {e}\n\n");
                    all_successful = false;
                }
            }
        }

        let duration = start_time.elapsed();
        let result = if all_successful {
            ToolResult::success(output)
        } else {
            ToolResult::failure(output, Some(1))
        };

        Ok(result.with_duration(duration))
    }
}

impl Default for HealthCheckTool {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl ClusterTool for HealthCheckTool {
    fn name(&self) -> &'static str {
        "health_check"
    }

    fn description(&self) -> &'static str {
        "Health check tool for service status monitoring using node_exporter metrics"
    }

    fn supported_commands(&self) -> Vec<CommandType> {
        vec![
            CommandType::NodePing,
            CommandType::NodeStatus,
            CommandType::ResourceUsage,
            CommandType::ConnectivityTest,
        ]
    }

    async fn execute(
        &self,
        command: ToolCommand,
        context: &ToolExecutionContext,
    ) -> Result<ToolResult, ToolError> {
        self.validate_command(&command)?;

        match command.command_type {
            CommandType::NodePing | CommandType::ConnectivityTest => {
                if let Some(node) = &command.target_node {
                    self.check_node_connectivity(node, context).await
                } else {
                    // Check all nodes
                    let all_nodes: Vec<String> = self.node_ips.keys().cloned().collect();
                    self.check_multiple_nodes(all_nodes, context, "connectivity")
                        .await
                }
            }

            CommandType::NodeStatus => {
                if let Some(node) = &command.target_node {
                    self.get_node_status(node, context).await
                } else {
                    // Check all nodes
                    let all_nodes: Vec<String> = self.node_ips.keys().cloned().collect();
                    self.check_multiple_nodes(all_nodes, context, "status")
                        .await
                }
            }

            CommandType::ResourceUsage => {
                if let Some(node) = &command.target_node {
                    self.get_resource_usage(node, context).await
                } else {
                    // Check all nodes
                    let all_nodes: Vec<String> = self.node_ips.keys().cloned().collect();
                    self.check_multiple_nodes(all_nodes, context, "resources")
                        .await
                }
            }

            _ => Err(ToolError::InvalidCommand(format!(
                "Command {:?} not implemented for health check tool",
                command.command_type
            ))),
        }
    }

    async fn health_check(&self, context: &ToolExecutionContext) -> Result<bool, ToolError> {
        // Test by checking connectivity to allyrion node
        let result = self.check_node_connectivity("allyrion", context).await?;
        Ok(result.success)
    }

    fn required_config(&self) -> Vec<String> {
        vec![]
    }
}

/// Format uptime seconds into human-readable string
fn format_uptime(seconds: u64) -> String {
    let days = seconds / 86400;
    let hours = (seconds % 86400) / 3600;
    let minutes = (seconds % 3600) / 60;

    if days > 0 {
        format!("{days} days, {hours}:{minutes:02}")
    } else {
        format!("{hours}:{minutes:02}")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    fn create_test_tool() -> HealthCheckTool {
        let mut nodes = HashMap::new();
        nodes.insert("test-node".to_string(), "192.168.1.100".to_string());
        HealthCheckTool::with_nodes(nodes)
    }

    fn create_test_context() -> ToolExecutionContext {
        ToolExecutionContext::new().dry_run(true) // Use dry run for tests
    }

    #[test]
    fn test_health_check_tool_creation() {
        let tool = HealthCheckTool::new();
        assert_eq!(tool.name(), "health_check");
        assert_eq!(tool.node_ips.len(), 13); // 12 Pi nodes + 1 x86 node
        assert!(!tool.supported_commands().is_empty());
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
        assert!(commands.contains(&CommandType::ResourceUsage));
        assert!(commands.contains(&CommandType::ConnectivityTest));
        assert!(!commands.contains(&CommandType::PodsList)); // Kubernetes command
    }

    #[tokio::test]
    async fn test_node_connectivity_dry_run() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::NodePing).with_node("test-node");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("[DRY RUN]"));
        assert!(result.stdout.contains("test-node"));
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
        assert!(result.stdout.contains("test-node"));
    }

    #[tokio::test]
    async fn test_resource_usage_dry_run() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ResourceUsage).with_node("test-node");

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("[DRY RUN]"));
        assert!(result.stdout.contains("test-node"));
    }

    #[tokio::test]
    async fn test_all_nodes_connectivity_dry_run() {
        let tool = create_test_tool();
        let context = create_test_context();
        let command = ToolCommand::new(CommandType::ConnectivityTest); // No specific node

        let result = tool.execute(command, &context).await;
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(result.success);
        assert!(result.stdout.contains("[DRY RUN]"));
        assert!(result.stdout.contains("test-node"));
    }

    #[test]
    fn test_parse_node_metrics() {
        let _tool = create_test_tool();
        let metrics_text = r#"
# HELP node_boot_time_seconds Node boot time, in unixtime.
node_boot_time_seconds 1704067200
# HELP node_load1 1m load average.
node_load1 0.15
node_load5 0.20
node_load15 0.18
node_memory_MemTotal_bytes 8589934592
node_memory_MemAvailable_bytes 6442450944
"#;

        let result = HealthCheckTool::parse_node_metrics(metrics_text);
        assert!(result.contains("\"load_1m\": \"0.15\""));
        assert!(result.contains("\"memory_total_mb\""));
        assert!(result.contains("\"uptime\""));
        assert!(result.contains("\"status\": \"online\""));
    }

    #[test]
    fn test_format_uptime() {
        assert_eq!(format_uptime(0), "0:00");
        assert_eq!(format_uptime(3661), "1:01");
        assert_eq!(format_uptime(86400), "1 days, 0:00");
        assert_eq!(format_uptime(443700), "5 days, 3:15");
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
