use crate::config::AgentConfig;
use crate::error::AgentError;
use std::path::Path;
use std::sync::RwLock;

#[derive(Debug)]
pub struct ConfigurationManager {
    config: RwLock<AgentConfig>,
}

impl ConfigurationManager {
    pub fn new() -> Self {
        Self {
            config: RwLock::new(AgentConfig::default()),
        }
    }
    
    pub fn with_env_overrides() -> Self {
        let mut config = AgentConfig::default();
        
        if let Ok(endpoint) = std::env::var("GOLDENTOOTH_CLUSTER_ENDPOINT") {
            config.cluster.endpoint = endpoint;
        }
        
        if let Ok(interval_str) = std::env::var("GOLDENTOOTH_PULSE_INTERVAL") {
            if let Ok(interval) = interval_str.parse::<u32>() {
                config.pulse.interval_minutes = interval;
            }
        }
        
        Self {
            config: RwLock::new(config),
        }
    }
    
    pub async fn from_file(path: &Path) -> Result<Self, AgentError> {
        let content = tokio::fs::read_to_string(path).await
            .map_err(|e| AgentError::ConfigLoadError(e.to_string()))?;
            
        let config: AgentConfig = toml::from_str(&content)
            .map_err(|e| AgentError::ConfigParseError(e.to_string()))?;
            
        Ok(Self {
            config: RwLock::new(config),
        })
    }
    
    // SYNC - In-memory config access
    pub fn get_config(&self) -> AgentConfig {
        self.config.read().unwrap().clone()
    }
    
    pub fn set_cluster_endpoint(&self, endpoint: &str) -> Result<(), AgentError> {
        let mut config = self.config.write().unwrap();
        config.cluster.endpoint = endpoint.to_string();
        Ok(())
    }
    
    pub fn set_pulse_interval(&self, interval: u32) -> Result<(), AgentError> {
        if interval < 5 {
            return Err(AgentError::ConfigValidationError(
                "Pulse interval must be at least 5 minutes".to_string()
            ));
        }
        
        if interval > 120 {
            return Err(AgentError::ConfigValidationError(
                "Pulse interval must be no more than 120 minutes".to_string()
            ));
        }
        
        let mut config = self.config.write().unwrap();
        config.pulse.interval_minutes = interval;
        Ok(())
    }
    
    // ASYNC - File I/O operations
    pub async fn save_to_file(&self, path: &Path) -> Result<(), AgentError> {
        let config = self.config.read().unwrap();
        let content = toml::to_string(&*config)
            .map_err(|e| AgentError::ConfigParseError(e.to_string()))?;
            
        tokio::fs::write(path, content).await
            .map_err(|e| AgentError::ConfigLoadError(e.to_string()))?;
            
        Ok(())
    }
    
    pub fn get_config_value(&self, key: &str) -> Result<String, AgentError> {
        let config = self.config.read().unwrap();
        
        match key {
            "cluster.endpoint" => Ok(config.cluster.endpoint.clone()),
            "cluster.verify_ssl" => Ok(config.cluster.verify_ssl.to_string()),
            "pulse.interval_minutes" => Ok(config.pulse.interval_minutes.to_string()),
            "pulse.enable_boredom_detection" => Ok(config.pulse.enable_boredom_detection.to_string()),
            "persona.default_archetype" => Ok(config.persona.default_archetype.clone()),
            "persona.enable_evolution" => Ok(config.persona.enable_evolution.to_string()),
            "persona.max_concurrent_personas" => Ok(config.persona.max_concurrent_personas.to_string()),
            _ => Err(AgentError::ConfigKeyNotFound(key.to_string())),
        }
    }
    
    pub fn set_config_value(&self, key: &str, value: &str) -> Result<(), AgentError> {
        let mut config = self.config.write().unwrap();
        
        match key {
            "cluster.endpoint" => {
                config.cluster.endpoint = value.to_string();
            },
            "cluster.verify_ssl" => {
                config.cluster.verify_ssl = value.parse()
                    .map_err(|_| AgentError::ConfigValidationError("Invalid boolean value".to_string()))?;
            },
            "pulse.interval_minutes" => {
                let interval: u32 = value.parse()
                    .map_err(|_| AgentError::ConfigValidationError("Invalid number value".to_string()))?;
                    
                if interval < 5 || interval > 120 {
                    return Err(AgentError::ConfigValidationError(
                        "Pulse interval must be between 5 and 120 minutes".to_string()
                    ));
                }
                
                config.pulse.interval_minutes = interval;
            },
            "pulse.enable_boredom_detection" => {
                config.pulse.enable_boredom_detection = value.parse()
                    .map_err(|_| AgentError::ConfigValidationError("Invalid boolean value".to_string()))?;
            },
            "persona.default_archetype" => {
                config.persona.default_archetype = value.to_string();
            },
            "persona.enable_evolution" => {
                config.persona.enable_evolution = value.parse()
                    .map_err(|_| AgentError::ConfigValidationError("Invalid boolean value".to_string()))?;
            },
            "persona.max_concurrent_personas" => {
                let max_personas: u32 = value.parse()
                    .map_err(|_| AgentError::ConfigValidationError("Invalid number value".to_string()))?;
                config.persona.max_concurrent_personas = max_personas;
            },
            _ => return Err(AgentError::ConfigKeyNotFound(key.to_string())),
        }
        
        Ok(())
    }
    
    pub fn list_config_keys(&self, section: &str) -> Result<Vec<String>, AgentError> {
        match section {
            "cluster" => Ok(vec![
                "endpoint".to_string(),
                "verify_ssl".to_string(),
                "ssh_key_path".to_string(),
                "kubeconfig_path".to_string(),
            ]),
            "pulse" => Ok(vec![
                "interval_minutes".to_string(),
                "uptime_kuma_url".to_string(),
                "enable_boredom_detection".to_string(),
                "boredom_threshold".to_string(),
            ]),
            "persona" => Ok(vec![
                "default_archetype".to_string(),
                "enable_evolution".to_string(),
                "max_concurrent_personas".to_string(),
            ]),
            _ => Err(AgentError::ConfigKeyNotFound(format!("section.{}", section))),
        }
    }
}

impl Default for ConfigurationManager {
    fn default() -> Self {
        Self::new()
    }
}