use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum AgentError {
    PersonaNotFound(PersonaId),
    PersonaAlreadyExists(PersonaId),
    CLIParseError(String),
    ConfigLoadError(String),
    ConfigParseError(String),
    ConfigValidationError(String),
    ConfigKeyNotFound(String),
    RegistrySerializationError(String),
    RegistryFileError(String),
    LockPoisonError(String),
}

impl fmt::Display for AgentError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AgentError::PersonaNotFound(id) => write!(f, "Persona not found: {id:?}"),
            AgentError::PersonaAlreadyExists(id) => write!(f, "Persona already exists: {id:?}"),
            AgentError::CLIParseError(msg) => write!(f, "CLI parse error: {msg}"),
            AgentError::ConfigLoadError(msg) => write!(f, "Configuration load error: {msg}"),
            AgentError::ConfigParseError(msg) => write!(f, "Configuration parse error: {msg}"),
            AgentError::ConfigValidationError(msg) => {
                write!(f, "Configuration validation error: {msg}")
            }
            AgentError::ConfigKeyNotFound(key) => write!(f, "Configuration key not found: {key}"),
            AgentError::RegistrySerializationError(msg) => {
                write!(f, "Registry serialization error: {msg}")
            }
            AgentError::RegistryFileError(msg) => write!(f, "Registry file error: {msg}"),
            AgentError::LockPoisonError(msg) => write!(f, "Lock poison error: {msg}"),
        }
    }
}

impl std::error::Error for AgentError {}

// Define PersonaId here since it's used in error types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize)]
pub struct PersonaId(u64);

impl PersonaId {
    #[must_use]
    pub fn new(id: u64) -> Self {
        Self(id)
    }

    #[must_use]
    pub fn as_u64(&self) -> u64 {
        self.0
    }
}
