use goldentooth_agent::config::{ConfigurationManager, AgentConfig, ClusterConfig, PulseConfig};
use goldentooth_agent::error::AgentError;
use tokio_test;
use std::path::PathBuf;
use tempfile::TempDir;

#[tokio::test]
async fn configuration_manager_can_be_created_with_defaults() {
    let config_manager = ConfigurationManager::new();
    
    let config = config_manager.get_config();
    assert!(config.cluster.endpoint.is_empty()); // Should start empty
    assert_eq!(config.pulse.interval_minutes, 30); // Default pulse interval
    assert!(!config.cluster.verify_ssl); // Default should be false for dev
}

#[tokio::test] 
async fn configuration_manager_can_load_from_file() {
    let temp_dir = TempDir::new().unwrap();
    let config_path = temp_dir.path().join("agent-config.toml");
    
    let config_content = r#"
[cluster]
endpoint = "https://k8s.goldentooth.net"
verify_ssl = true
ssh_key_path = "/home/user/.ssh/goldentooth"

[pulse]
interval_minutes = 15
uptime_kuma_url = "https://uptime.goldentooth.net"
enable_boredom_detection = true
boredom_threshold = 0.5

[persona]
default_archetype = "AuthoritativeScholar"
enable_evolution = true
max_concurrent_personas = 10
"#;
    
    std::fs::write(&config_path, config_content).unwrap();
    
    let config_manager = ConfigurationManager::from_file(&config_path).await;
    assert!(config_manager.is_ok());
    
    let config = config_manager.unwrap().get_config();
    assert_eq!(config.cluster.endpoint, "https://k8s.goldentooth.net");
    assert!(config.cluster.verify_ssl);
    assert_eq!(config.pulse.interval_minutes, 15);
    assert!(config.pulse.enable_boredom_detection);
}

#[tokio::test]
async fn configuration_manager_handles_missing_config_file() {
    let nonexistent_path = PathBuf::from("/tmp/nonexistent-config.toml");
    
    let result = ConfigurationManager::from_file(&nonexistent_path).await;
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::ConfigLoadError(_) => {}, // Expected
        _ => panic!("Expected ConfigLoadError"),
    }
}

#[tokio::test]
async fn configuration_manager_handles_invalid_toml() {
    let temp_dir = TempDir::new().unwrap();
    let config_path = temp_dir.path().join("invalid-config.toml");
    
    let invalid_content = r#"
[cluster
endpoint = "missing closing bracket"
invalid toml syntax
"#;
    
    std::fs::write(&config_path, invalid_content).unwrap();
    
    let result = ConfigurationManager::from_file(&config_path).await;
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::ConfigParseError(_) => {}, // Expected
        _ => panic!("Expected ConfigParseError"),
    }
}

#[tokio::test]
async fn configuration_manager_can_update_cluster_endpoint() {
    let mut config_manager = ConfigurationManager::new();
    
    let new_endpoint = "https://new-cluster.goldentooth.net";
    let result = config_manager.set_cluster_endpoint(new_endpoint);
    assert!(result.is_ok());
    
    let config = config_manager.get_config();
    assert_eq!(config.cluster.endpoint, new_endpoint);
}

#[tokio::test]
async fn configuration_manager_can_update_pulse_interval() {
    let mut config_manager = ConfigurationManager::new();
    
    let new_interval = 45;
    let result = config_manager.set_pulse_interval(new_interval);
    assert!(result.is_ok());
    
    let config = config_manager.get_config();
    assert_eq!(config.pulse.interval_minutes, new_interval);
}

#[tokio::test]
async fn configuration_manager_validates_pulse_interval_range() {
    let mut config_manager = ConfigurationManager::new();
    
    // Too low (less than 5 minutes)
    let result = config_manager.set_pulse_interval(2);
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::ConfigValidationError(msg) => {
            assert!(msg.contains("interval"));
            assert!(msg.contains("5"));
        },
        _ => panic!("Expected ConfigValidationError for low interval"),
    }
    
    // Too high (more than 120 minutes)
    let result = config_manager.set_pulse_interval(150);
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::ConfigValidationError(msg) => {
            assert!(msg.contains("interval"));
            assert!(msg.contains("120"));
        },
        _ => panic!("Expected ConfigValidationError for high interval"),
    }
}

#[tokio::test]
async fn configuration_manager_can_save_to_file() {
    let temp_dir = TempDir::new().unwrap();
    let config_path = temp_dir.path().join("test-config.toml");
    
    let mut config_manager = ConfigurationManager::new();
    config_manager.set_cluster_endpoint("https://test.goldentooth.net").unwrap();
    config_manager.set_pulse_interval(25).unwrap();
    
    let result = config_manager.save_to_file(&config_path).await;
    assert!(result.is_ok());
    
    // Verify file was created and contains expected content
    assert!(config_path.exists());
    let content = std::fs::read_to_string(&config_path).unwrap();
    assert!(content.contains("test.goldentooth.net"));
    assert!(content.contains("interval_minutes = 25"));
}

#[tokio::test]
async fn configuration_manager_can_get_config_value_by_key() {
    let mut config_manager = ConfigurationManager::new();
    config_manager.set_cluster_endpoint("https://test.example.com").unwrap();
    
    let result = config_manager.get_config_value("cluster.endpoint");
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "https://test.example.com");
    
    let result = config_manager.get_config_value("pulse.interval_minutes");
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), "30"); // Default value
}

#[tokio::test]
async fn configuration_manager_handles_invalid_config_keys() {
    let config_manager = ConfigurationManager::new();
    
    let result = config_manager.get_config_value("invalid.key");
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::ConfigKeyNotFound(key) => assert_eq!(key, "invalid.key"),
        _ => panic!("Expected ConfigKeyNotFound error"),
    }
}

#[tokio::test]
async fn configuration_manager_can_set_config_value_by_key() {
    let mut config_manager = ConfigurationManager::new();
    
    let result = config_manager.set_config_value("cluster.endpoint", "https://new.endpoint.com");
    assert!(result.is_ok());
    
    let config = config_manager.get_config();
    assert_eq!(config.cluster.endpoint, "https://new.endpoint.com");
    
    let result = config_manager.set_config_value("pulse.interval_minutes", "20");
    assert!(result.is_ok());
    
    let config = config_manager.get_config();
    assert_eq!(config.pulse.interval_minutes, 20);
}

#[tokio::test]
async fn configuration_manager_validates_config_values() {
    let mut config_manager = ConfigurationManager::new();
    
    // Invalid pulse interval
    let result = config_manager.set_config_value("pulse.interval_minutes", "invalid");
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::ConfigValidationError(_) => {}, // Expected
        _ => panic!("Expected ConfigValidationError for invalid interval"),
    }
    
    // Invalid boolean value
    let result = config_manager.set_config_value("cluster.verify_ssl", "maybe");
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::ConfigValidationError(_) => {}, // Expected
        _ => panic!("Expected ConfigValidationError for invalid boolean"),
    }
}

#[tokio::test]
async fn configuration_manager_supports_config_sections() {
    let config_manager = ConfigurationManager::new();
    
    let cluster_keys = config_manager.list_config_keys("cluster");
    assert!(cluster_keys.is_ok());
    
    let keys = cluster_keys.unwrap();
    assert!(keys.contains(&"endpoint".to_string()));
    assert!(keys.contains(&"verify_ssl".to_string()));
    assert!(keys.contains(&"ssh_key_path".to_string()));
    
    let pulse_keys = config_manager.list_config_keys("pulse");
    assert!(pulse_keys.is_ok());
    
    let keys = pulse_keys.unwrap();
    assert!(keys.contains(&"interval_minutes".to_string()));
    assert!(keys.contains(&"uptime_kuma_url".to_string()));
    assert!(keys.contains(&"enable_boredom_detection".to_string()));
}

#[tokio::test]
async fn configuration_manager_handles_environment_variable_overrides() {
    // Set environment variable
    unsafe {
        std::env::set_var("GOLDENTOOTH_CLUSTER_ENDPOINT", "https://env-override.com");
        std::env::set_var("GOLDENTOOTH_PULSE_INTERVAL", "60");
    }
    
    let config_manager = ConfigurationManager::with_env_overrides();
    let config = config_manager.get_config();
    
    assert_eq!(config.cluster.endpoint, "https://env-override.com");
    assert_eq!(config.pulse.interval_minutes, 60);
    
    // Clean up
    unsafe {
        std::env::remove_var("GOLDENTOOTH_CLUSTER_ENDPOINT");
        std::env::remove_var("GOLDENTOOTH_PULSE_INTERVAL");
    }
}

// Configuration types are already defined in the library