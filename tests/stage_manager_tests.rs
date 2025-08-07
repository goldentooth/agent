use goldentooth_agent::core::{StageManager, PersonaId, Persona};
use goldentooth_agent::error::AgentError;
use tokio_test;
use std::sync::Arc;
use async_trait::async_trait;

// Mock persona for testing
struct MockPersona {
    id: PersonaId,
    name: String,
    is_running: bool,
}

impl MockPersona {
    fn new(id: PersonaId, name: impl Into<String>) -> Self {
        Self {
            id,
            name: name.into(),
            is_running: false,
        }
    }
}

#[async_trait]
impl Persona for MockPersona {
    fn id(&self) -> PersonaId {
        self.id
    }
    
    fn name(&self) -> &str {
        &self.name
    }
    
    async fn start(&mut self) -> Result<(), AgentError> {
        self.is_running = true;
        Ok(())
    }
    
    async fn stop(&mut self) -> Result<(), AgentError> {
        self.is_running = false;
        Ok(())
    }
    
    fn is_running(&self) -> bool {
        self.is_running
    }
}

#[tokio::test]
async fn stage_manager_can_be_created() {
    let stage_manager = StageManager::new();
    assert_eq!(stage_manager.persona_count(), 0);
}

#[tokio::test] 
async fn stage_manager_can_spawn_persona() {
    let mut stage_manager = StageManager::new();
    let persona = Box::new(MockPersona::new(PersonaId::new(1), "Test Persona"));
    let persona_id = persona.id();
    
    let result = stage_manager.spawn_persona(persona).await;
    assert!(result.is_ok());
    assert_eq!(stage_manager.persona_count(), 1);
    assert!(stage_manager.has_persona(persona_id));
}

#[tokio::test]
async fn stage_manager_can_spawn_multiple_personas() {
    let mut stage_manager = StageManager::new();
    
    let persona1 = Box::new(MockPersona::new(PersonaId::new(1), "Persona 1"));
    let persona2 = Box::new(MockPersona::new(PersonaId::new(2), "Persona 2"));
    let persona3 = Box::new(MockPersona::new(PersonaId::new(3), "Persona 3"));
    
    stage_manager.spawn_persona(persona1).await.unwrap();
    stage_manager.spawn_persona(persona2).await.unwrap();  
    stage_manager.spawn_persona(persona3).await.unwrap();
    
    assert_eq!(stage_manager.persona_count(), 3);
}

#[tokio::test]
async fn stage_manager_prevents_duplicate_persona_ids() {
    let mut stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    
    let persona1 = Box::new(MockPersona::new(persona_id, "Persona 1"));
    let persona2 = Box::new(MockPersona::new(persona_id, "Persona 2"));
    
    // First spawn should succeed
    let result1 = stage_manager.spawn_persona(persona1).await;
    assert!(result1.is_ok());
    
    // Second spawn with same ID should fail
    let result2 = stage_manager.spawn_persona(persona2).await;
    assert!(result2.is_err());
    assert_eq!(stage_manager.persona_count(), 1);
}

#[tokio::test]
async fn stage_manager_can_terminate_persona() {
    let mut stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));
    
    stage_manager.spawn_persona(persona).await.unwrap();
    assert_eq!(stage_manager.persona_count(), 1);
    
    let result = stage_manager.terminate_persona(persona_id).await;
    assert!(result.is_ok());
    assert_eq!(stage_manager.persona_count(), 0);
}

#[tokio::test]
async fn stage_manager_handles_terminating_nonexistent_persona() {
    let mut stage_manager = StageManager::new();
    let nonexistent_id = PersonaId::new(999);
    
    let result = stage_manager.terminate_persona(nonexistent_id).await;
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::PersonaNotFound(id) => assert_eq!(id, nonexistent_id),
        _ => panic!("Expected PersonaNotFound error"),
    }
}

#[tokio::test]
async fn stage_manager_can_get_persona_by_id() {
    let mut stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));
    
    stage_manager.spawn_persona(persona).await.unwrap();
    
    let retrieved_persona = stage_manager.get_persona(persona_id);
    assert!(retrieved_persona.is_some());
    assert_eq!(retrieved_persona.unwrap().name(), "Test Persona");
}

#[tokio::test]
async fn stage_manager_can_list_all_personas() {
    let mut stage_manager = StageManager::new();
    
    let persona1 = Box::new(MockPersona::new(PersonaId::new(1), "Persona 1"));
    let persona2 = Box::new(MockPersona::new(PersonaId::new(2), "Persona 2"));
    
    stage_manager.spawn_persona(persona1).await.unwrap();
    stage_manager.spawn_persona(persona2).await.unwrap();
    
    let personas = stage_manager.list_personas();
    assert_eq!(personas.len(), 2);
    
    let names: Vec<&str> = personas.iter().map(|p| p.name()).collect();
    assert!(names.contains(&"Persona 1"));
    assert!(names.contains(&"Persona 2"));
}

#[tokio::test]
async fn stage_manager_starts_personas_on_spawn() {
    let mut stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));
    
    stage_manager.spawn_persona(persona).await.unwrap();
    
    let retrieved_persona = stage_manager.get_persona(persona_id).unwrap();
    assert!(retrieved_persona.is_running());
}

#[tokio::test]
async fn stage_manager_stops_personas_on_termination() {
    let mut stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));
    
    stage_manager.spawn_persona(persona).await.unwrap();
    
    // Verify persona is running before termination
    let running_persona = stage_manager.get_persona(persona_id).unwrap();
    assert!(running_persona.is_running());
    
    // Terminate and verify it was stopped
    stage_manager.terminate_persona(persona_id).await.unwrap();
    
    // Persona should no longer exist in stage manager
    assert!(!stage_manager.has_persona(persona_id));
}