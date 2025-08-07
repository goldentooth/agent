use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Core trait defining the behavior and personality of a persona
#[async_trait]
pub trait Persona: Send + Sync {
    // Lifecycle management
    fn id(&self) -> PersonaId;
    fn name(&self) -> &str;
    fn archetype(&self) -> &str;
    fn service_domain(&self) -> Option<&str>;
    async fn start(&mut self) -> Result<(), AgentError>;
    async fn stop(&mut self) -> Result<(), AgentError>;
    fn is_running(&self) -> bool;

    // Personality and dialogue
    fn personality(&self) -> &PersonalityProfile;
    fn personality_mut(&mut self) -> &mut PersonalityProfile;

    /// Generate a response to user input based on personality
    async fn respond(
        &self,
        input: &str,
        context: &InteractionContext,
    ) -> Result<String, AgentError>;

    /// Generate a status report in character
    async fn status_report(&self, system_status: &SystemStatus) -> Result<String, AgentError>;

    /// Process an evolution catalyst and potentially change personality
    async fn evolve(&mut self, catalyst: EvolutionCatalyst) -> Result<EvolutionResult, AgentError>;
}

/// Comprehensive personality profile system
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersonalityProfile {
    // Core traits (0.0 to 1.0)
    pub formality: f64,
    pub verbosity: f64,
    pub empathy: f64,
    pub aggression: f64,
    pub humor: f64,
    pub paranoia: f64,
    pub confidence: f64,
    pub curiosity: f64,

    // Literary archetype traits
    pub scholarly_tendency: f64,
    pub authority_seeking: f64,
    pub manipulation_inclination: f64,
    pub mechanical_precision: f64,

    // Service-specific traits
    pub service_dedication: f64,
    pub perfectionism: f64,
    pub social_connectivity: f64,
    pub protective_instinct: f64,

    // Evolution modifiers
    pub current_modifiers: Vec<PersonalityModifier>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersonalityModifier {
    pub modifier_type: ModifierType,
    pub strength: f64,
    pub duration: Option<chrono::Duration>,
    pub applied_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ModifierType {
    StressInduced,
    SuccessEuphoria,
    CrisisResponse,
    LongTermNeglect,
    SecurityThreat,
    PerformancePride,
}

/// Context for character interactions
#[derive(Debug, Clone)]
pub struct InteractionContext {
    pub user_query_type: QueryType,
    pub system_health: HealthStatus,
    pub recent_events: Vec<SystemEvent>,
    pub interaction_history: Vec<String>,
}

#[derive(Debug, Clone)]
pub enum QueryType {
    StatusInquiry,
    ConfigurationRequest,
    TroubleshootingHelp,
    PerformanceAnalysis,
    SecurityQuery,
    GeneralChat,
}

#[derive(Debug, Clone)]
pub enum HealthStatus {
    Healthy,
    Warning,
    Critical,
    Unknown,
}

#[derive(Debug, Clone)]
pub struct SystemEvent {
    pub event_type: EventType,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub description: String,
    pub severity: EventSeverity,
}

#[derive(Debug, Clone)]
pub enum EventType {
    ServiceStart,
    ServiceStop,
    ServiceFailure,
    PerformanceAlert,
    SecurityIncident,
    ConfigurationChange,
}

#[derive(Debug, Clone)]
pub enum EventSeverity {
    Info,
    Warning,
    Error,
    Critical,
}

#[derive(Debug, Clone)]
pub struct SystemStatus {
    pub overall_health: HealthStatus,
    pub services_status: HashMap<String, HealthStatus>,
    pub resource_usage: ResourceUsage,
    pub active_alerts: Vec<Alert>,
}

#[derive(Debug, Clone)]
pub struct ResourceUsage {
    pub cpu_percent: f64,
    pub memory_percent: f64,
    pub disk_percent: f64,
    pub network_bytes_per_sec: u64,
}

#[derive(Debug, Clone)]
pub struct Alert {
    pub alert_type: String,
    pub message: String,
    pub severity: EventSeverity,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Evolution catalysts that can change personality
#[derive(Debug, Clone)]
pub enum EvolutionCatalyst {
    HealthChange {
        old_status: HealthStatus,
        new_status: HealthStatus,
        duration: chrono::Duration,
    },
    UserInteraction {
        interaction_frequency: f64,
        user_satisfaction: f64,
        query_complexity: f64,
    },
    SystemStress {
        stress_type: StressType,
        intensity: f64,
        duration: chrono::Duration,
    },
    RelationshipChange {
        related_persona: PersonaId,
        change_type: RelationshipChangeType,
    },
}

#[derive(Debug, Clone)]
pub enum StressType {
    HighLoad,
    ResourceStarvation,
    RepeatedFailures,
    ConfigurationDrift,
}

#[derive(Debug, Clone)]
pub enum RelationshipChangeType {
    NewDependency,
    DependencyRemoved,
    SharedFailure,
    SuccessfulCollaboration,
}

/// Result of an evolution event
#[derive(Debug, Clone)]
pub enum EvolutionResult {
    NoChange,
    PersonalityShift {
        changes: Vec<PersonalityChange>,
        narrative: String,
    },
    NewModifier {
        modifier: PersonalityModifier,
        narrative: String,
    },
}

#[derive(Debug, Clone)]
pub enum PersonalityChange {
    TraitIncrease { trait_name: String, amount: f64 },
    TraitDecrease { trait_name: String, amount: f64 },
    NewBehaviorPattern { pattern: String },
    DialogueStyleChange { style: String },
}

impl PersonalityProfile {
    /// Create a new personality profile with default values
    #[must_use]
    pub fn new() -> Self {
        Self {
            formality: 0.5,
            verbosity: 0.5,
            empathy: 0.5,
            aggression: 0.3,
            humor: 0.3,
            paranoia: 0.2,
            confidence: 0.6,
            curiosity: 0.5,
            scholarly_tendency: 0.3,
            authority_seeking: 0.4,
            manipulation_inclination: 0.2,
            mechanical_precision: 0.5,
            service_dedication: 0.7,
            perfectionism: 0.5,
            social_connectivity: 0.4,
            protective_instinct: 0.5,
            current_modifiers: Vec::new(),
        }
    }

    /// Apply a personality modifier
    pub fn apply_modifier(&mut self, modifier: PersonalityModifier) {
        self.current_modifiers.push(modifier);
    }

    /// Remove expired modifiers
    pub fn cleanup_modifiers(&mut self) {
        let now = chrono::Utc::now();
        self.current_modifiers.retain(|modifier| {
            if let Some(duration) = modifier.duration {
                now.signed_duration_since(modifier.applied_at) < duration
            } else {
                true // Permanent modifiers
            }
        });
    }

    /// Get effective trait value including modifiers
    #[must_use]
    pub fn effective_trait_value(&self, base_value: f64, trait_name: &str) -> f64 {
        let mut effective_value = base_value;

        for modifier in &self.current_modifiers {
            match modifier.modifier_type {
                ModifierType::StressInduced if trait_name == "aggression" => {
                    effective_value += modifier.strength * 0.3;
                }
                ModifierType::SuccessEuphoria if trait_name == "confidence" => {
                    effective_value += modifier.strength * 0.2;
                }
                ModifierType::SecurityThreat if trait_name == "paranoia" => {
                    effective_value += modifier.strength * 0.4;
                }
                _ => {}
            }
        }

        // Clamp to valid range
        effective_value.clamp(0.0, 1.0)
    }
}

impl Default for PersonalityProfile {
    fn default() -> Self {
        Self::new()
    }
}
