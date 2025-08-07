use crate::core::Persona;
use crate::error::{AgentError, PersonaId};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

pub struct StageManager {
    personas: Arc<RwLock<HashMap<PersonaId, Box<dyn Persona>>>>,
}

impl StageManager {
    pub fn new() -> Self {
        Self {
            personas: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    // SYNC - Simple in-memory queries
    pub fn persona_count(&self) -> usize {
        self.personas.read().unwrap().len()
    }
    
    // ASYNC - Calls persona.start() which may do I/O or setup work
    pub async fn spawn_persona(&self, mut persona: Box<dyn Persona>) -> Result<(), AgentError> {
        let persona_id = persona.id();
        let mut personas = self.personas.write().unwrap();
        
        if personas.contains_key(&persona_id) {
            return Err(AgentError::PersonaAlreadyExists(persona_id));
        }
        
        // Start the persona
        persona.start().await?;
        
        personas.insert(persona_id, persona);
        Ok(())
    }
    
    pub fn has_persona(&self, persona_id: PersonaId) -> bool {
        self.personas.read().unwrap().contains_key(&persona_id)
    }
    
    // ASYNC - Calls persona.stop() which may do I/O or cleanup work  
    pub async fn terminate_persona(&self, persona_id: PersonaId) -> Result<(), AgentError> {
        let mut personas = self.personas.write().unwrap();
        
        match personas.remove(&persona_id) {
            Some(mut persona) => {
                persona.stop().await?;
                Ok(())
            },
            None => Err(AgentError::PersonaNotFound(persona_id)),
        }
    }
    
    pub fn get_persona(&self, persona_id: PersonaId) -> Option<PersonaRef> {
        let personas = self.personas.read().unwrap();
        personas.get(&persona_id).map(|persona| PersonaRef {
            persona_id,
            name: persona.name().to_string(),
            is_running: persona.is_running(),
        })
    }
    
    pub fn list_personas(&self) -> Vec<PersonaRef> {
        let personas = self.personas.read().unwrap();
        personas.iter().map(|(&id, persona)| PersonaRef {
            persona_id: id,
            name: persona.name().to_string(),
            is_running: persona.is_running(),
        }).collect()
    }
}

impl Default for StageManager {
    fn default() -> Self {
        Self::new()
    }
}

// Helper struct to provide safe access to persona information
pub struct PersonaRef {
    persona_id: PersonaId,
    name: String,
    is_running: bool,
}

impl PersonaRef {
    pub fn name(&self) -> &str {
        &self.name
    }
    
    pub fn is_running(&self) -> bool {
        self.is_running
    }
}