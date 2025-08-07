#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct AgentConfig {
    pub cluster: ClusterConfig,
    pub pulse: PulseConfig,
    pub persona: PersonaConfig,
}

#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct ClusterConfig {
    pub endpoint: String,
    pub verify_ssl: bool,
    pub ssh_key_path: Option<String>,
    pub kubeconfig_path: Option<String>,
}

#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct PulseConfig {
    pub interval_minutes: u32,
    pub uptime_kuma_url: Option<String>,
    pub enable_boredom_detection: bool,
    pub boredom_threshold: f64,
}

#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct PersonaConfig {
    pub default_archetype: String,
    pub enable_evolution: bool,
    pub max_concurrent_personas: u32,
}

impl Default for AgentConfig {
    fn default() -> Self {
        Self {
            cluster: ClusterConfig {
                endpoint: String::new(),
                verify_ssl: false,
                ssh_key_path: None,
                kubeconfig_path: None,
            },
            pulse: PulseConfig {
                interval_minutes: 30,
                uptime_kuma_url: None,
                enable_boredom_detection: false,
                boredom_threshold: 0.3,
            },
            persona: PersonaConfig {
                default_archetype: "AuthoritativeScholar".to_string(),
                enable_evolution: false,
                max_concurrent_personas: 6,
            },
        }
    }
}
