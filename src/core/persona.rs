use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;

#[async_trait]
pub trait Persona: Send + Sync {
    fn id(&self) -> PersonaId;
    fn name(&self) -> &str;
    async fn start(&mut self) -> Result<(), AgentError>;
    async fn stop(&mut self) -> Result<(), AgentError>;
    fn is_running(&self) -> bool;
}
