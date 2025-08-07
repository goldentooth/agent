pub mod stage_manager;
pub mod persona_registry;
pub mod persona;
pub mod agent_foundation;

pub use stage_manager::StageManager;
pub use persona_registry::{PersonaRegistry, PersonaMetadata, PersonaState};
pub use persona::Persona;
pub use agent_foundation::AgentFoundation;
pub use crate::error::PersonaId;