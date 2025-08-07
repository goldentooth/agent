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
    pub fn new() -> Self {
        Self {
            registry: RwLock::new(HashMap::new()),
        }
    }
    
    pub fn count(&self) -> usize {
        self.registry.read().unwrap().len()
    }
    
    pub fn is_empty(&self) -> bool {
        self.registry.read().unwrap().is_empty()
    }
    
    // SYNC - Pure in-memory operations
    pub fn register(&self, persona_id: PersonaId, metadata: PersonaMetadata) -> Result<(), AgentError> {
        let mut registry = self.registry.write().unwrap();
        
        if registry.contains_key(&persona_id) {
            return Err(AgentError::PersonaAlreadyExists(persona_id));
        }
        
        registry.insert(persona_id, metadata);
        Ok(())
    }
    
    pub fn contains(&self, persona_id: PersonaId) -> bool {
        self.registry.read().unwrap().contains_key(&persona_id)
    }
    
    pub fn get(&self, persona_id: PersonaId) -> Option<PersonaMetadata> {
        self.registry.read().unwrap().get(&persona_id).cloned()
    }
    
    pub fn unregister(&self, persona_id: PersonaId) -> Result<PersonaMetadata, AgentError> {
        let mut registry = self.registry.write().unwrap();
        
        match registry.remove(&persona_id) {
            Some(metadata) => Ok(metadata),
            None => Err(AgentError::PersonaNotFound(persona_id)),
        }
    }
    
    pub fn update_state(&self, persona_id: PersonaId, new_state: PersonaState) -> Result<(), AgentError> {
        let mut registry = self.registry.write().unwrap();
        
        match registry.get_mut(&persona_id) {
            Some(metadata) => {
                metadata.state = new_state;
                Ok(())
            },
            None => Err(AgentError::PersonaNotFound(persona_id)),
        }
    }
    
    pub fn update_last_active(&self, persona_id: PersonaId) -> Result<(), AgentError> {
        let mut registry = self.registry.write().unwrap();
        
        match registry.get_mut(&persona_id) {
            Some(metadata) => {
                metadata.last_active = Utc::now();
                Ok(())
            },
            None => Err(AgentError::PersonaNotFound(persona_id)),
        }
    }
    
    pub fn list_all(&self) -> Vec<(PersonaId, PersonaMetadata)> {
        let registry = self.registry.read().unwrap();
        registry.iter().map(|(&id, metadata)| (id, metadata.clone())).collect()
    }
    
    pub fn find_by_archetype(&self, archetype: &str) -> Vec<(PersonaId, PersonaMetadata)> {
        let registry = self.registry.read().unwrap();
        registry
            .iter()
            .filter(|(_, metadata)| metadata.archetype == archetype)
            .map(|(&id, metadata)| (id, metadata.clone()))
            .collect()
    }
    
    pub fn find_active(&self) -> Vec<(PersonaId, PersonaMetadata)> {
        let registry = self.registry.read().unwrap();
        registry
            .iter()
            .filter(|(_, metadata)| metadata.state == PersonaState::Active)
            .map(|(&id, metadata)| (id, metadata.clone()))
            .collect()
    }
    
    // ASYNC - Only for I/O operations (future file persistence)
    pub async fn save_to_file(&self, path: &std::path::Path) -> Result<(), AgentError> {
        let registry = self.registry.read().unwrap();
        let data = registry.clone();
        drop(registry); // Release lock before I/O
        
        let json = serde_json::to_string_pretty(&data)
            .map_err(|e| AgentError::RegistryError(format!("Serialization error: {}", e)))?;
            
        tokio::fs::write(path, json).await
            .map_err(|e| AgentError::RegistryError(format!("File write error: {}", e)))?;
            
        Ok(())
    }
    
    pub async fn load_from_file(&self, path: &std::path::Path) -> Result<(), AgentError> {
        let json = tokio::fs::read_to_string(path).await
            .map_err(|e| AgentError::RegistryError(format!("File read error: {}", e)))?;
            
        let data: HashMap<PersonaId, PersonaMetadata> = serde_json::from_str(&json)
            .map_err(|e| AgentError::RegistryError(format!("Deserialization error: {}", e)))?;
            
        let mut registry = self.registry.write().unwrap();
        *registry = data;
        
        Ok(())
    }
}

impl Default for PersonaRegistry {
    fn default() -> Self {
        Self::new()
    }
}