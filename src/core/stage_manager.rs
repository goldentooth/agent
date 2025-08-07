use crate::core::Persona;
use crate::error::{AgentError, PersonaId};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

pub struct StageManager {
    personas: Arc<RwLock<HashMap<PersonaId, Box<dyn Persona>>>>,
}

impl StageManager {
    #[must_use]
    pub fn new() -> Self {
        Self {
            personas: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    // SYNC - Simple in-memory queries
    /// Get the number of personas currently managed
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn persona_count(&self) -> Result<usize, AgentError> {
        let personas = self.personas.read().map_err(|e| {
            AgentError::LockPoisonError(format!("StageManager read lock poisoned: {e}"))
        })?;
        Ok(personas.len())
    }

    // ASYNC - Calls persona.start() which may do I/O or setup work
    /// Spawn a new persona and start it
    ///
    /// # Errors
    ///
    /// Returns `AgentError::PersonaAlreadyExists` if a persona with the same ID exists
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    /// Returns any error from the persona's start method
    ///
    /// # Panics
    ///
    /// Panics if the persona Option is None when expected to be Some (internal logic error)
    pub async fn spawn_persona(&self, mut persona: Box<dyn Persona>) -> Result<(), AgentError> {
        let persona_id = persona.id();

        // Start the persona first, before any lock operations
        // This ensures that if starting fails, we haven't modified any shared state
        persona.start().await?;

        // Try to insert atomically - return the persona if insertion failed
        let mut persona_option = Some(persona);
        let insertion_result = {
            let mut personas = self.personas.write().map_err(|e| {
                AgentError::LockPoisonError(format!("StageManager write lock poisoned: {e}"))
            })?;

            if let std::collections::hash_map::Entry::Vacant(e) = personas.entry(persona_id) {
                // Take ownership of persona and insert it
                let persona = persona_option.take().expect("Persona should be Some");
                e.insert(persona);
                Ok(())
            } else {
                Err(AgentError::PersonaAlreadyExists(persona_id))
            }
        }; // Lock is dropped here

        match insertion_result {
            Ok(()) => Ok(()),
            Err(error) => {
                // Persona wasn't inserted, clean it up if we still have it
                if let Some(mut persona) = persona_option {
                    let _ = persona.stop().await; // Best effort cleanup
                }
                Err(error)
            }
        }
    }

    /// Check if a persona with the given ID exists
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn has_persona(&self, persona_id: PersonaId) -> Result<bool, AgentError> {
        let personas = self.personas.read().map_err(|e| {
            AgentError::LockPoisonError(format!("StageManager read lock poisoned: {e}"))
        })?;
        Ok(personas.contains_key(&persona_id))
    }

    // ASYNC - Calls persona.stop() which may do I/O or cleanup work
    /// Terminate and remove a persona
    ///
    /// # Errors
    ///
    /// Returns `AgentError::PersonaNotFound` if the persona doesn't exist
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    /// Returns any error from the persona's stop method
    pub async fn terminate_persona(&self, persona_id: PersonaId) -> Result<(), AgentError> {
        // Remove persona from map first
        let mut persona = {
            let mut personas = self.personas.write().map_err(|e| {
                AgentError::LockPoisonError(format!("StageManager write lock poisoned: {e}"))
            })?;

            personas
                .remove(&persona_id)
                .ok_or(AgentError::PersonaNotFound(persona_id))?
        }; // Drop write lock before async call

        // Now stop the persona without holding any locks
        persona.stop().await?;
        Ok(())
    }

    /// Get a persona reference by ID
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn get_persona(&self, persona_id: PersonaId) -> Result<Option<PersonaRef>, AgentError> {
        let personas = self.personas.read().map_err(|e| {
            AgentError::LockPoisonError(format!("StageManager read lock poisoned: {e}"))
        })?;
        Ok(personas.get(&persona_id).map(|persona| PersonaRef {
            persona_id,
            name: persona.name().to_string(),
            is_running: persona.is_running(),
        }))
    }

    /// List all managed personas
    ///
    /// # Errors
    ///
    /// Returns `AgentError::LockPoisonError` if the lock is poisoned
    pub fn list_personas(&self) -> Result<Vec<PersonaRef>, AgentError> {
        let personas = self.personas.read().map_err(|e| {
            AgentError::LockPoisonError(format!("StageManager read lock poisoned: {e}"))
        })?;
        Ok(personas
            .iter()
            .map(|(&id, persona)| PersonaRef {
                persona_id: id,
                name: persona.name().to_string(),
                is_running: persona.is_running(),
            })
            .collect())
    }
}

impl Default for StageManager {
    fn default() -> Self {
        Self::new()
    }
}

// Helper struct to provide safe access to persona information
pub struct PersonaRef {
    #[allow(dead_code)] // Will be used in future persona implementation
    persona_id: PersonaId,
    name: String,
    is_running: bool,
}

impl PersonaRef {
    #[must_use]
    pub fn name(&self) -> &str {
        &self.name
    }

    #[must_use]
    pub fn is_running(&self) -> bool {
        self.is_running
    }
}
