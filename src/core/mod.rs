pub mod agent_foundation;
pub mod persona;
pub mod persona_registry;
pub mod stage_manager;

pub use crate::error::PersonaId;
pub use agent_foundation::AgentFoundation;
pub use persona::Persona;
pub use persona_registry::{PersonaMetadata, PersonaRegistry, PersonaState};
pub use stage_manager::StageManager;
