use crate::error::{AgentError, PersonaId};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use std::sync::RwLock;

#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub enum PersonaState {
    Active,
    Inactive,
    Suspended,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct PersonaMetadata {
    pub name: String,
    pub archetype: String,
    pub service_domain: Option<String>,
    pub created_at: DateTime<Utc>,
    pub last_active: DateTime<Utc>,
    pub state: PersonaState,
}

pub struct PersonaRegistry {
    registry: RwLock<HashMap<PersonaId, PersonaMetadata>>,
}

impl PersonaRegistry {
    #[must_use]
    pub fn new() -> Self {
        Self {
            registry: RwLock::new(HashMap::new()),
        }
    }

    /// Get the number of registered personas
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn count(&self) -> Result<usize, AgentError> {
        let registry = self.registry.read().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
        })?;
        Ok(registry.len())
    }

    /// Check if the registry is empty
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn is_empty(&self) -> Result<bool, AgentError> {
        let registry = self.registry.read().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
        })?;
        Ok(registry.is_empty())
    }

    // SYNC - Pure in-memory operations
    /// Register a new persona
    ///
    /// # Errors
    ///
    /// Returns `AgentError::PersonaAlreadyExists` if a persona with the same ID exists
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn register(
        &self,
        persona_id: PersonaId,
        metadata: PersonaMetadata,
    ) -> Result<(), AgentError> {
        let mut registry = self.registry.write().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry write lock poisoned: {e}"))
        })?;

        if registry.contains_key(&persona_id) {
            return Err(AgentError::PersonaAlreadyExists(persona_id));
        }

        registry.insert(persona_id, metadata);
        Ok(())
    }

    /// Check if a persona exists
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn contains(&self, persona_id: PersonaId) -> Result<bool, AgentError> {
        let registry = self.registry.read().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
        })?;
        Ok(registry.contains_key(&persona_id))
    }

    /// Get persona metadata by ID
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn get(&self, persona_id: PersonaId) -> Result<Option<PersonaMetadata>, AgentError> {
        let registry = self.registry.read().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
        })?;
        Ok(registry.get(&persona_id).cloned())
    }

    /// Remove and return persona metadata
    ///
    /// # Errors
    ///
    /// Returns `AgentError::PersonaNotFound` if the persona doesn't exist
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn unregister(&self, persona_id: PersonaId) -> Result<PersonaMetadata, AgentError> {
        let mut registry = self.registry.write().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry write lock poisoned: {e}"))
        })?;

        match registry.remove(&persona_id) {
            Some(metadata) => Ok(metadata),
            None => Err(AgentError::PersonaNotFound(persona_id)),
        }
    }

    /// Update the state of a persona
    ///
    /// # Errors
    ///
    /// Returns `AgentError::PersonaNotFound` if the persona doesn't exist
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn update_state(
        &self,
        persona_id: PersonaId,
        new_state: PersonaState,
    ) -> Result<(), AgentError> {
        let mut registry = self.registry.write().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry write lock poisoned: {e}"))
        })?;

        match registry.get_mut(&persona_id) {
            Some(metadata) => {
                metadata.state = new_state;
                Ok(())
            }
            None => Err(AgentError::PersonaNotFound(persona_id)),
        }
    }

    /// Update the last active timestamp of a persona
    ///
    /// # Errors
    ///
    /// Returns `AgentError::PersonaNotFound` if the persona doesn't exist
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn update_last_active(&self, persona_id: PersonaId) -> Result<(), AgentError> {
        let mut registry = self.registry.write().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry write lock poisoned: {e}"))
        })?;

        match registry.get_mut(&persona_id) {
            Some(metadata) => {
                metadata.last_active = Utc::now();
                Ok(())
            }
            None => Err(AgentError::PersonaNotFound(persona_id)),
        }
    }

    /// List all registered personas
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn list_all(&self) -> Result<Vec<(PersonaId, PersonaMetadata)>, AgentError> {
        let registry = self.registry.read().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
        })?;
        Ok(registry
            .iter()
            .map(|(&id, metadata)| (id, metadata.clone()))
            .collect())
    }

    /// Find personas by archetype
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn find_by_archetype(
        &self,
        archetype: &str,
    ) -> Result<Vec<(PersonaId, PersonaMetadata)>, AgentError> {
        let registry = self.registry.read().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
        })?;
        Ok(registry
            .iter()
            .filter(|(_, metadata)| metadata.archetype == archetype)
            .map(|(&id, metadata)| (id, metadata.clone()))
            .collect())
    }

    /// Find all active personas
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn find_active(&self) -> Result<Vec<(PersonaId, PersonaMetadata)>, AgentError> {
        let registry = self.registry.read().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
        })?;
        Ok(registry
            .iter()
            .filter(|(_, metadata)| metadata.state == PersonaState::Active)
            .map(|(&id, metadata)| (id, metadata.clone()))
            .collect())
    }

    // ASYNC - Only for I/O operations (future file persistence)
    /// Save the registry to a JSON file
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    /// Returns `AgentError::RegistrySerializationError` or `AgentError::RegistryFileError` if operations fail
    pub async fn save_to_file(&self, path: &std::path::Path) -> Result<(), AgentError> {
        let data = {
            let registry = self.registry.read().map_err(|e| {
                AgentError::LockPoisonError(format!("PersonaRegistry read lock poisoned: {e}"))
            })?;
            registry.clone()
        }; // Release lock before I/O

        let json = serde_json::to_string_pretty(&data).map_err(|e| {
            AgentError::RegistrySerializationError(format!("JSON serialization failed: {e}"))
        })?;

        tokio::fs::write(path, json).await.map_err(|e| {
            AgentError::RegistryFileError(format!("Failed to write registry file: {e}"))
        })?;

        Ok(())
    }

    /// Load the registry from a JSON file
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    /// Returns `AgentError::RegistryFileError` or `AgentError::RegistrySerializationError` if operations fail
    pub async fn load_from_file(&self, path: &std::path::Path) -> Result<(), AgentError> {
        let json = tokio::fs::read_to_string(path).await.map_err(|e| {
            AgentError::RegistryFileError(format!("Failed to read registry file: {e}"))
        })?;

        let data: HashMap<PersonaId, PersonaMetadata> =
            serde_json::from_str(&json).map_err(|e| {
                AgentError::RegistrySerializationError(format!("Deserialization error: {e}"))
            })?;

        let mut registry = self.registry.write().map_err(|e| {
            AgentError::LockPoisonError(format!("PersonaRegistry write lock poisoned: {e}"))
        })?;
        *registry = data;

        Ok(())
    }
}

impl Default for PersonaRegistry {
    fn default() -> Self {
        Self::new()
    }
}
