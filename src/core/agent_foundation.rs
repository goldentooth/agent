use crate::cli::CLIInterface;
use crate::config::ConfigurationManager;
use crate::core::{PersonaRegistry, StageManager};
use crate::error::AgentError;

pub struct AgentFoundation {
    pub stage_manager: StageManager,
    pub persona_registry: PersonaRegistry,
    pub configuration_system: ConfigurationManager,
    pub basic_cli: CLIInterface,
}

impl AgentFoundation {
    /// Create a new agent foundation
    ///
    /// # Errors
    ///
    /// Currently always succeeds, but returns Result for future extensibility
    pub fn new() -> Result<Self, AgentError> {
        Ok(Self {
            stage_manager: StageManager::new(),
            persona_registry: PersonaRegistry::new(),
            configuration_system: ConfigurationManager::new(),
            basic_cli: CLIInterface::new(),
        })
    }
}
