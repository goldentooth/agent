use async_trait::async_trait;
use goldentooth_agent::core::persona::{
    EvolutionCatalyst, EvolutionResult, InteractionContext, PersonalityProfile, SystemStatus,
};
use goldentooth_agent::core::stage_manager::PersonaRef;
use goldentooth_agent::core::{Persona, StageManager};
use goldentooth_agent::error::{AgentError, PersonaId};

// Mock persona for testing
struct MockPersona {
    id: PersonaId,
    name: String,
    is_running: bool,
    personality: PersonalityProfile,
}

impl MockPersona {
    fn new(id: PersonaId, name: impl Into<String>) -> Self {
        Self {
            id,
            name: name.into(),
            is_running: false,
            personality: PersonalityProfile::new(),
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

    fn archetype(&self) -> &'static str {
        "Mock Persona"
    }

    fn service_domain(&self) -> Option<&str> {
        Some("Testing")
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

    fn personality(&self) -> &PersonalityProfile {
        &self.personality
    }

    fn personality_mut(&mut self) -> &mut PersonalityProfile {
        &mut self.personality
    }

    async fn respond(
        &self,
        _input: &str,
        _context: &InteractionContext,
    ) -> Result<String, AgentError> {
        Ok("Mock response".to_string())
    }

    async fn status_report(&self, _system_status: &SystemStatus) -> Result<String, AgentError> {
        Ok("Mock status report".to_string())
    }

    async fn evolve(
        &mut self,
        _catalyst: EvolutionCatalyst,
    ) -> Result<EvolutionResult, AgentError> {
        Ok(EvolutionResult::NoChange)
    }
}

#[tokio::test]
async fn stage_manager_can_be_created() {
    let stage_manager = StageManager::new();
    assert_eq!(stage_manager.persona_count().unwrap(), 0);
}

#[tokio::test]
async fn stage_manager_can_spawn_persona() {
    let stage_manager = StageManager::new();
    let persona = Box::new(MockPersona::new(PersonaId::new(1), "Test Persona"));
    let persona_id = persona.id();

    let result = stage_manager.spawn_persona(persona).await;
    assert!(result.is_ok());
    assert_eq!(stage_manager.persona_count().unwrap(), 1);
    assert!(stage_manager.has_persona(persona_id).unwrap());
}

#[tokio::test]
async fn stage_manager_can_spawn_multiple_personas() {
    let stage_manager = StageManager::new();

    let persona1 = Box::new(MockPersona::new(PersonaId::new(1), "Persona 1"));
    let persona2 = Box::new(MockPersona::new(PersonaId::new(2), "Persona 2"));
    let persona3 = Box::new(MockPersona::new(PersonaId::new(3), "Persona 3"));

    stage_manager.spawn_persona(persona1).await.unwrap();
    stage_manager.spawn_persona(persona2).await.unwrap();
    stage_manager.spawn_persona(persona3).await.unwrap();

    assert_eq!(stage_manager.persona_count().unwrap(), 3);
}

#[tokio::test]
async fn stage_manager_prevents_duplicate_persona_ids() {
    let stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);

    let persona1 = Box::new(MockPersona::new(persona_id, "Persona 1"));
    let persona2 = Box::new(MockPersona::new(persona_id, "Persona 2"));

    // First spawn should succeed
    let result1 = stage_manager.spawn_persona(persona1).await;
    assert!(result1.is_ok());

    // Second spawn with same ID should fail
    let result2 = stage_manager.spawn_persona(persona2).await;
    assert!(result2.is_err());
    assert_eq!(stage_manager.persona_count().unwrap(), 1);
}

#[tokio::test]
async fn stage_manager_can_terminate_persona() {
    let stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));

    stage_manager.spawn_persona(persona).await.unwrap();
    assert_eq!(stage_manager.persona_count().unwrap(), 1);

    let result = stage_manager.terminate_persona(persona_id).await;
    assert!(result.is_ok());
    assert_eq!(stage_manager.persona_count().unwrap(), 0);
}

#[tokio::test]
async fn stage_manager_handles_terminating_nonexistent_persona() {
    let stage_manager = StageManager::new();
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
    let stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));

    stage_manager.spawn_persona(persona).await.unwrap();

    let retrieved_persona = stage_manager.get_persona(persona_id).unwrap();
    assert!(retrieved_persona.is_some());
    assert_eq!(retrieved_persona.unwrap().name(), "Test Persona");
}

#[tokio::test]
async fn stage_manager_can_list_all_personas() {
    let stage_manager = StageManager::new();

    let persona1 = Box::new(MockPersona::new(PersonaId::new(1), "Persona 1"));
    let persona2 = Box::new(MockPersona::new(PersonaId::new(2), "Persona 2"));

    stage_manager.spawn_persona(persona1).await.unwrap();
    stage_manager.spawn_persona(persona2).await.unwrap();

    let persona_list = stage_manager.list_personas().unwrap();
    assert_eq!(persona_list.len(), 2);

    let names: Vec<&str> = persona_list.iter().map(PersonaRef::name).collect();
    assert!(names.contains(&"Persona 1"));
    assert!(names.contains(&"Persona 2"));
}

#[tokio::test]
async fn stage_manager_starts_personas_on_spawn() {
    let stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));

    stage_manager.spawn_persona(persona).await.unwrap();

    let retrieved_persona = stage_manager.get_persona(persona_id).unwrap().unwrap();
    assert!(retrieved_persona.is_running());
}

#[tokio::test]
async fn stage_manager_stops_personas_on_termination() {
    let stage_manager = StageManager::new();
    let persona_id = PersonaId::new(1);
    let persona = Box::new(MockPersona::new(persona_id, "Test Persona"));

    stage_manager.spawn_persona(persona).await.unwrap();

    // Verify persona is running before termination
    let running_persona = stage_manager.get_persona(persona_id).unwrap().unwrap();
    assert!(running_persona.is_running());

    // Terminate and verify it was stopped
    stage_manager.terminate_persona(persona_id).await.unwrap();

    // Persona should no longer exist in stage manager
    assert!(!stage_manager.has_persona(persona_id).unwrap());
}
