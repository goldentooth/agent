pub mod agent_foundation;
pub mod characters;
pub mod persona;
pub mod persona_registry;
pub mod stage_manager;
pub mod tools;

pub use crate::error::PersonaId;
pub use agent_foundation::AgentFoundation;
pub use characters::{
    DrCaudexThorne, MadamCalliopeHarkthorn, MissGlestrineVellum, MrMalvoTrevine, MrUmbrellSeverin,
    OperantNo7,
};
pub use persona::Persona;
pub use persona_registry::{PersonaMetadata, PersonaRegistry, PersonaState};
pub use stage_manager::StageManager;
