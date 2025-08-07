use crate::config::AgentConfig;
use crate::error::AgentError;
use std::path::Path;
use std::sync::RwLock;

#[derive(Debug)]
pub struct ConfigurationManager {
    config: RwLock<AgentConfig>,
}

impl ConfigurationManager {
    #[must_use]
    pub fn new() -> Self {
        Self {
            config: RwLock::new(AgentConfig::default()),
        }
    }

    #[must_use]
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

    /// Load configuration from a TOML file
    ///
    /// # Errors
    ///
    /// Returns `AgentError::ConfigLoadError` if file cannot be read
    /// Returns `AgentError::ConfigParseError` if TOML cannot be parsed
    pub async fn from_file(path: &Path) -> Result<Self, AgentError> {
        let content = tokio::fs::read_to_string(path)
            .await
            .map_err(|e| AgentError::ConfigLoadError(e.to_string()))?;

        let config: AgentConfig =
            toml::from_str(&content).map_err(|e| AgentError::ConfigParseError(e.to_string()))?;

        Ok(Self {
            config: RwLock::new(config),
        })
    }

    // SYNC - In-memory config access
    /// Get a copy of the current configuration
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn get_config(&self) -> Result<AgentConfig, AgentError> {
        let config = self.config.read().map_err(|e| {
            AgentError::LockPoisonError(format!("ConfigurationManager read lock poisoned: {e}"))
        })?;
        Ok(config.clone())
    }

    /// Set the cluster endpoint
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn set_cluster_endpoint(&self, endpoint: &str) -> Result<(), AgentError> {
        let mut config = self.config.write().map_err(|e| {
            AgentError::LockPoisonError(format!("ConfigurationManager write lock poisoned: {e}"))
        })?;
        config.cluster.endpoint = endpoint.to_string();
        Ok(())
    }

    /// Set the pulse interval in minutes
    ///
    /// # Errors
    ///
    /// Returns `AgentError::ConfigValidationError` if interval is out of range
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn set_pulse_interval(&self, interval: u32) -> Result<(), AgentError> {
        if interval < 5 {
            return Err(AgentError::ConfigValidationError(
                "Pulse interval must be at least 5 minutes".to_string(),
            ));
        }

        if interval > 120 {
            return Err(AgentError::ConfigValidationError(
                "Pulse interval must be no more than 120 minutes".to_string(),
            ));
        }

        let mut config = self.config.write().map_err(|e| {
            AgentError::LockPoisonError(format!("ConfigurationManager write lock poisoned: {e}"))
        })?;
        config.pulse.interval_minutes = interval;
        Ok(())
    }

    // ASYNC - File I/O operations
    /// Save configuration to a TOML file
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    /// Returns `AgentError::ConfigParseError` if TOML cannot be serialized
    /// Returns `AgentError::ConfigLoadError` if file cannot be written
    pub async fn save_to_file(&self, path: &Path) -> Result<(), AgentError> {
        let content = {
            let config = self.config.read().map_err(|e| {
                AgentError::LockPoisonError(format!("ConfigurationManager read lock poisoned: {e}"))
            })?;
            toml::to_string(&*config).map_err(|e| AgentError::ConfigParseError(e.to_string()))?
        }; // Drop lock before async call

        tokio::fs::write(path, content)
            .await
            .map_err(|e| AgentError::ConfigLoadError(e.to_string()))?;

        Ok(())
    }

    /// Get a configuration value by key
    ///
    /// # Errors
    ///
    /// Returns `AgentError::ConfigKeyNotFound` if key is not valid
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn get_config_value(&self, key: &str) -> Result<String, AgentError> {
        let config = self.config.read().map_err(|e| {
            AgentError::LockPoisonError(format!("ConfigurationManager read lock poisoned: {e}"))
        })?;

        match key {
            "cluster.endpoint" => Ok(config.cluster.endpoint.clone()),
            "cluster.verify_ssl" => Ok(config.cluster.verify_ssl.to_string()),
            "pulse.interval_minutes" => Ok(config.pulse.interval_minutes.to_string()),
            "pulse.enable_boredom_detection" => {
                Ok(config.pulse.enable_boredom_detection.to_string())
            }
            "persona.default_archetype" => Ok(config.persona.default_archetype.clone()),
            "persona.enable_evolution" => Ok(config.persona.enable_evolution.to_string()),
            "persona.max_concurrent_personas" => {
                Ok(config.persona.max_concurrent_personas.to_string())
            }
            "pulse.boredom_threshold" => Ok(config.pulse.boredom_threshold.to_string()),
            _ => Err(AgentError::ConfigKeyNotFound(key.to_string())),
        }
    }

    /// Set a configuration value by key
    ///
    /// # Errors
    ///
    /// Returns `AgentError::ConfigKeyNotFound` if key is not valid
    /// Returns `AgentError::ConfigValidationError` if value is invalid
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn set_config_value(&self, key: &str, value: &str) -> Result<(), AgentError> {
        let mut config = self.config.write().map_err(|e| {
            AgentError::LockPoisonError(format!("ConfigurationManager write lock poisoned: {e}"))
        })?;

        match key {
            "cluster.endpoint" => {
                // Validate URL format if not empty
                if !value.is_empty() {
                    // Basic URL validation - must start with http:// or https://
                    if !value.starts_with("http://") && !value.starts_with("https://") {
                        return Err(AgentError::ConfigValidationError(
                            "Cluster endpoint must be a valid HTTP/HTTPS URL".to_string(),
                        ));
                    }
                }
                config.cluster.endpoint = value.to_string();
            }
            "cluster.verify_ssl" => {
                config.cluster.verify_ssl = value.parse().map_err(|_| {
                    AgentError::ConfigValidationError("Invalid boolean value".to_string())
                })?;
            }
            "pulse.interval_minutes" => {
                let interval: u32 = value.parse().map_err(|_| {
                    AgentError::ConfigValidationError("Invalid number value".to_string())
                })?;

                if !(5..=120).contains(&interval) {
                    return Err(AgentError::ConfigValidationError(
                        "Pulse interval must be between 5 and 120 minutes".to_string(),
                    ));
                }

                config.pulse.interval_minutes = interval;
            }
            "pulse.enable_boredom_detection" => {
                config.pulse.enable_boredom_detection = value.parse().map_err(|_| {
                    AgentError::ConfigValidationError("Invalid boolean value".to_string())
                })?;
            }
            "persona.default_archetype" => {
                config.persona.default_archetype = value.to_string();
            }
            "persona.enable_evolution" => {
                config.persona.enable_evolution = value.parse().map_err(|_| {
                    AgentError::ConfigValidationError("Invalid boolean value".to_string())
                })?;
            }
            "persona.max_concurrent_personas" => {
                let max_personas: u32 = value.parse().map_err(|_| {
                    AgentError::ConfigValidationError("Invalid number value".to_string())
                })?;

                if max_personas == 0 {
                    return Err(AgentError::ConfigValidationError(
                        "Max concurrent personas must be at least 1".to_string(),
                    ));
                }

                if max_personas > 50 {
                    return Err(AgentError::ConfigValidationError(
                        "Max concurrent personas cannot exceed 50 (resource constraints)"
                            .to_string(),
                    ));
                }

                config.persona.max_concurrent_personas = max_personas;
            }
            "pulse.boredom_threshold" => {
                let threshold: f64 = value.parse().map_err(|_| {
                    AgentError::ConfigValidationError("Invalid decimal value".to_string())
                })?;

                if !(0.0..=1.0).contains(&threshold) {
                    return Err(AgentError::ConfigValidationError(
                        "Boredom threshold must be between 0.0 and 1.0".to_string(),
                    ));
                }

                config.pulse.boredom_threshold = threshold;
            }
            _ => return Err(AgentError::ConfigKeyNotFound(key.to_string())),
        }

        Ok(())
    }

    /// List all configuration keys in a section
    ///
    /// # Errors
    ///
    /// Returns `AgentError::ConfigKeyNotFound` if section is not valid
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
            _ => Err(AgentError::ConfigKeyNotFound(format!("section.{section}"))),
        }
    }
}

impl Default for ConfigurationManager {
    fn default() -> Self {
        Self::new()
    }
}
