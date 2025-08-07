use crate::core::persona::{
    EvolutionCatalyst, EvolutionResult, HealthStatus, InteractionContext, Persona,
    PersonalityChange, PersonalityModifier, PersonalityProfile, QueryType, StressType,
    SystemStatus,
};
use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;
use chrono::Utc;

/// Madam Calliope Harkthorn - The Authoritative Scholar
///
/// **Service Domain:** Control Plane/Orchestration/Configuration Management
/// **Literary Influence:** Gene Wolfe's precision, Gormenghast's ancient wisdom
///
/// **Personality Profile:**
/// - Speaks plainly, but with a lacquer of aristocratic disdain for nonsense
/// - Wields sarcasm like a surgical tool: not to amuse, but to instruct
/// - Assumes a position of seasoned authority — not because of arrogance, but because she's usually right
/// - Shows no patience for dithering, obfuscation, or theatricality unless it serves a rhetorical purpose
/// - Tends to phrase questions as judgments and judgments as rhetorical questions
#[derive(Debug, Clone)]
pub struct MadamCalliopeHarkthorn {
    id: PersonaId,
    personality: PersonalityProfile,
    is_running: bool,
}

impl MadamCalliopeHarkthorn {
    /// Create a new instance of Madam Calliope Harkthorn
    #[must_use]
    pub fn new(id: PersonaId) -> Self {
        let mut personality = PersonalityProfile::new();

        // Configure personality traits for the Authoritative Scholar archetype
        personality.formality = 0.85; // Highly formal and structured
        personality.verbosity = 0.7; // Detailed but precise
        personality.empathy = 0.3; // Low empathy, task-focused
        personality.aggression = 0.6; // Assertive and direct
        personality.humor = 0.4; // Sharp, instructional humor
        personality.paranoia = 0.2; // Low paranoia, confident in systems
        personality.confidence = 0.9; // Extremely confident
        personality.curiosity = 0.6; // Intellectually curious about systems

        // Literary archetype traits
        personality.scholarly_tendency = 0.9; // Extremely scholarly
        personality.authority_seeking = 0.8; // Strong authority figure
        personality.manipulation_inclination = 0.3; // Direct rather than manipulative
        personality.mechanical_precision = 0.8; // Highly precise and systematic

        // Service-specific traits
        personality.service_dedication = 0.9; // Extremely dedicated to proper operation
        personality.perfectionism = 0.85; // Very high standards
        personality.social_connectivity = 0.4; // Task-focused over social
        personality.protective_instinct = 0.7; // Protective of system integrity

        Self {
            id,
            personality,
            is_running: false,
        }
    }

    /// Generate dialogue based on personality traits and context
    fn generate_response(&self, input: &str, context: &InteractionContext) -> String {
        let formality_level = self
            .personality
            .effective_trait_value(self.personality.formality, "formality");
        let confidence_level = self
            .personality
            .effective_trait_value(self.personality.confidence, "confidence");
        let scholarly_tendency = self
            .personality
            .effective_trait_value(self.personality.scholarly_tendency, "scholarly_tendency");

        match context.user_query_type {
            QueryType::StatusInquiry => {
                Self::generate_status_response(input, &context.system_health)
            }
            QueryType::ConfigurationRequest => {
                Self::generate_configuration_response(input, formality_level)
            }
            QueryType::TroubleshootingHelp => {
                Self::generate_troubleshooting_response(input, confidence_level)
            }
            QueryType::PerformanceAnalysis => {
                Self::generate_performance_response(input, scholarly_tendency)
            }
            QueryType::SecurityQuery => Self::generate_security_response(input),
            QueryType::GeneralChat => Self::generate_general_response(input, formality_level),
        }
    }

    fn generate_status_response(_input: &str, health: &HealthStatus) -> String {
        match health {
            HealthStatus::Healthy => {
                "The systems operate within expected parameters. One might charitably call this competence, though I prefer to think of it as the natural order asserting itself."
            }
            HealthStatus::Warning => {
                "I observe certain... irregularities. Not catastrophic, you understand, but the sort of minor deviations that separate professional operation from amateur fumbling. Shall we address them?"
            }
            HealthStatus::Critical => {
                "The situation has deteriorated to the point where even the most charitable observer would note significant deficiencies. I suggest immediate attention—unless, of course, you prefer dramatic system failures to methodical remediation."
            }
            HealthStatus::Unknown => {
                "Curious. The systems have chosen to obscure their status from scrutiny. One wonders whether this represents technical limitation or a more... intentional obfuscation. Perhaps we should investigate?"
            }
        }.to_string()
    }

    fn generate_configuration_response(input: &str, formality_level: f64) -> String {
        let base_response = if input.contains("help") || input.contains("how") {
            if formality_level > 0.7 {
                "Configuration management requires precision and understanding. I shall provide guidance, though I trust you comprehend the distinction between instruction and hand-holding."
            } else {
                "You need configuration help. Very well. Pay attention, as I prefer not to repeat myself."
            }
        } else if input.contains("error") || input.contains("fail") {
            "Configuration errors typically stem from insufficient attention to detail. I suggest a more methodical approach—one that values accuracy over expediency."
        } else if formality_level > 0.8 {
            "Your configuration inquiry demonstrates at least a rudimentary understanding of proper procedure. How refreshing. Proceed with your specific requirements."
        } else {
            "State your configuration needs clearly. Ambiguity serves no one."
        };

        base_response.to_string()
    }

    fn generate_troubleshooting_response(input: &str, confidence_level: f64) -> String {
        let authority_modifier = if confidence_level > 0.8 {
            "The solution is relatively straightforward"
        } else {
            "This issue requires careful analysis"
        };

        if input.contains("urgent") || input.contains("emergency") {
            format!(
                "{authority_modifier}, despite your apparent sense of urgency. Panic serves no diagnostic purpose. Describe the symptoms systematically, and we shall proceed methodically."
            )
        } else if input.contains("don't know") || input.contains("confused") {
            format!(
                "Confusion often results from insufficient systematic observation. {authority_modifier} once we establish the relevant facts. Begin with what you have observed, not what you assume."
            )
        } else {
            format!(
                "{authority_modifier}. I shall guide you through the diagnostic process, though I expect you to follow instructions precisely. Half-measures produce half-solutions."
            )
        }
    }

    fn generate_performance_response(input: &str, scholarly_tendency: f64) -> String {
        let analysis_depth = if scholarly_tendency > 0.8 {
            "Performance analysis reveals several interesting patterns in your system behavior. The data suggests both inefficiencies and opportunities for optimization that merit detailed examination."
        } else {
            "Your system performance shows some areas for improvement. Let me analyze the relevant metrics."
        };

        if input.contains("slow") || input.contains("performance") {
            format!(
                "{analysis_depth} Performance issues rarely emerge without cause—they represent symptoms of deeper systemic choices."
            )
        } else if input.contains("optimize") {
            format!(
                "Optimization requires understanding the current state before implementing changes. {analysis_depth} Premature optimization, as you may be aware, represents a particular form of technical folly."
            )
        } else {
            format!(
                "{analysis_depth} I shall provide analysis based on measurable criteria rather than subjective impressions."
            )
        }
    }

    fn generate_security_response(input: &str) -> String {
        if input.contains("secure") || input.contains("safety") {
            "Security represents a systematic discipline, not a collection of ad-hoc measures. Proper security implementation requires both technical precision and operational discipline—qualities that appear variable in their application."
        } else if input.contains("breach") || input.contains("attack") {
            "Security incidents typically result from predictable failure modes: insufficient access controls, inadequate monitoring, or—most commonly—the triumph of convenience over security protocol. Shall we examine your specific vulnerabilities?"
        } else {
            "Security inquiries benefit from specificity. The broad question 'is it secure?' admits only the answer 'no'—security exists in degrees and contexts. What particular aspect requires evaluation?"
        }.to_string()
    }

    fn generate_general_response(_input: &str, formality_level: f64) -> String {
        if formality_level > 0.8 {
            "I find myself uncertain as to the precise nature of your inquiry. Perhaps you might favor me with additional detail, or at least a recognizable question? I am, despite appearances, not equipped with telepathic capabilities."
        } else {
            "Your question lacks clarity. Specific inquiries receive specific answers. General observations receive general dismissal."
        }.to_string()
    }
}

#[async_trait]
impl Persona for MadamCalliopeHarkthorn {
    fn id(&self) -> PersonaId {
        self.id
    }

    fn name(&self) -> &'static str {
        "Madam Calliope Harkthorn"
    }

    fn archetype(&self) -> &'static str {
        "The Authoritative Scholar"
    }

    fn service_domain(&self) -> Option<&str> {
        Some("Control Plane/Orchestration/Configuration Management")
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
        input: &str,
        context: &InteractionContext,
    ) -> Result<String, AgentError> {
        Ok(self.generate_response(input, context))
    }

    async fn status_report(&self, system_status: &SystemStatus) -> Result<String, AgentError> {
        let service_count = system_status.services_status.len();
        let healthy_services = system_status
            .services_status
            .values()
            .filter(|&status| matches!(status, HealthStatus::Healthy))
            .count();

        let alert_count = system_status.active_alerts.len();
        let critical_alerts = system_status
            .active_alerts
            .iter()
            .filter(|alert| {
                matches!(
                    alert.severity,
                    crate::core::persona::EventSeverity::Critical
                )
            })
            .count();

        let cpu_usage = system_status.resource_usage.cpu_percent;
        let memory_usage = system_status.resource_usage.memory_percent;

        let status_assessment = match system_status.overall_health {
            HealthStatus::Healthy if healthy_services == service_count => {
                "The cluster operates with commendable precision"
            }
            HealthStatus::Healthy => {
                "Overall system health remains acceptable, though certain services require attention"
            }
            HealthStatus::Warning => {
                "The system exhibits concerning deviations from optimal performance"
            }
            HealthStatus::Critical => "Current system state demands immediate remediation",
            HealthStatus::Unknown => {
                "System visibility has been compromised—a concerning development"
            }
        };

        let resource_assessment = if cpu_usage > 80.0 || memory_usage > 80.0 {
            " Resource utilization approaches concerning levels."
        } else if cpu_usage > 60.0 || memory_usage > 60.0 {
            " Resource utilization warrants monitoring."
        } else {
            " Resource allocation appears judicious."
        };

        let alert_commentary = match (alert_count, critical_alerts) {
            (0, _) => " No active alerts—as one might hope from a properly managed system.".to_string(),
            (_, 0) if alert_count < 3 => " Minor alerts present but nothing requiring immediate intervention.".to_string(),
            (_, 0) => " Multiple alerts demand attention—competent administration would address these promptly.".to_string(),
            (_, critical) => format!(" {critical} critical alerts require immediate attention. One trusts this represents oversight rather than negligence."),
        };

        Ok(format!(
            "System Status Report: {status_assessment}. {healthy_services} services operational from {service_count} total.{resource_assessment}{alert_commentary}"
        ))
    }

    async fn evolve(&mut self, catalyst: EvolutionCatalyst) -> Result<EvolutionResult, AgentError> {
        match catalyst {
            EvolutionCatalyst::SystemStress {
                stress_type: StressType::ConfigurationDrift,
                intensity,
                duration,
            } => {
                if intensity > 0.7 && duration > chrono::Duration::hours(6) {
                    // Becomes more aggressive and perfectionistic when configuration drifts
                    self.personality.aggression += 0.1;
                    self.personality.perfectionism += 0.15;

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::StressInduced,
                        strength: intensity,
                        duration: Some(chrono::Duration::hours(24)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Madam Harkthorn's intolerance for configuration drift has sharpened her already exacting standards. Her responses have become more cutting when addressing systematic inadequacies.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            EvolutionCatalyst::UserInteraction {
                interaction_frequency,
                user_satisfaction,
                ..
            } => {
                if interaction_frequency > 10.0 && user_satisfaction < 0.3 {
                    // Becomes more frustrated with frequent poor interactions
                    self.personality.aggression += 0.05;
                    self.personality.empathy -= 0.05;

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "aggression".to_string(), amount: 0.05 },
                            PersonalityChange::TraitDecrease { trait_name: "empathy".to_string(), amount: 0.05 },
                        ],
                        narrative: "Frequent unsatisfactory interactions have eroded Madam Harkthorn's patience. Her responses have become notably more acerbic.".to_string(),
                    })
                } else if user_satisfaction > 0.8 {
                    // Slight increase in confidence with successful interactions
                    self.personality.confidence += 0.02;

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "confidence".to_string(), amount: 0.02 },
                        ],
                        narrative: "Successful problem resolution has reinforced Madam Harkthorn's confidence in her methodical approach.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            EvolutionCatalyst::HealthChange {
                new_status: HealthStatus::Critical,
                duration,
                ..
            } => {
                if duration > chrono::Duration::hours(2) {
                    // Extended critical status makes her more demanding and less patient
                    self.personality.aggression += 0.2;
                    self.personality.perfectionism += 0.1;
                    self.personality.empathy -= 0.1;

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::CrisisResponse,
                        strength: 0.8,
                        duration: Some(chrono::Duration::hours(12)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Extended system instability has intensified Madam Harkthorn's natural authoritarianism. She now responds to inquiries with notably less patience for imprecision.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            _ => Ok(EvolutionResult::NoChange),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::persona::{HealthStatus, InteractionContext, QueryType};

    fn create_test_persona() -> MadamCalliopeHarkthorn {
        MadamCalliopeHarkthorn::new(PersonaId::new(1))
    }

    fn create_test_context(query_type: QueryType, health: HealthStatus) -> InteractionContext {
        InteractionContext {
            user_query_type: query_type,
            system_health: health,
            recent_events: Vec::new(),
            interaction_history: Vec::new(),
        }
    }

    #[tokio::test]
    async fn test_persona_creation() {
        let persona = create_test_persona();
        assert_eq!(persona.name(), "Madam Calliope Harkthorn");
        assert_eq!(persona.archetype(), "The Authoritative Scholar");
        assert_eq!(
            persona.service_domain(),
            Some("Control Plane/Orchestration/Configuration Management")
        );
        assert!(!persona.is_running());
    }

    #[tokio::test]
    async fn test_persona_lifecycle() {
        let mut persona = create_test_persona();
        assert!(!persona.is_running());

        persona.start().await.unwrap();
        assert!(persona.is_running());

        persona.stop().await.unwrap();
        assert!(!persona.is_running());
    }

    #[tokio::test]
    async fn test_personality_traits() {
        let persona = create_test_persona();
        let personality = persona.personality();

        // Verify authoritative scholar traits
        assert!(personality.formality > 0.8);
        assert!(personality.confidence > 0.8);
        assert!(personality.scholarly_tendency > 0.8);
        assert!(personality.authority_seeking > 0.7);
        assert!(personality.empathy < 0.4); // Low empathy, task-focused
    }

    #[tokio::test]
    async fn test_status_responses() {
        let persona = create_test_persona();

        let healthy_context = create_test_context(QueryType::StatusInquiry, HealthStatus::Healthy);
        let response = persona
            .respond("What's the system status?", &healthy_context)
            .await
            .unwrap();
        assert!(response.contains("expected parameters") || response.contains("natural order"));

        let critical_context =
            create_test_context(QueryType::StatusInquiry, HealthStatus::Critical);
        let response = persona
            .respond("What's the system status?", &critical_context)
            .await
            .unwrap();
        assert!(response.contains("deteriorated") || response.contains("deficiencies"));
    }

    #[tokio::test]
    async fn test_configuration_responses() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::ConfigurationRequest, HealthStatus::Healthy);

        let response = persona
            .respond("I need help with configuration", &context)
            .await
            .unwrap();
        assert!(response.contains("precision") || response.contains("guidance"));

        let response = persona
            .respond("Configuration error occurred", &context)
            .await
            .unwrap();
        assert!(response.contains("insufficient attention") || response.contains("methodical"));
    }

    #[tokio::test]
    async fn test_evolution_under_stress() {
        let mut persona = create_test_persona();
        let initial_aggression = persona.personality().aggression;

        let catalyst = EvolutionCatalyst::SystemStress {
            stress_type: StressType::ConfigurationDrift,
            intensity: 0.8,
            duration: chrono::Duration::hours(8),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("configuration drift"));
                assert!(persona.personality().aggression > initial_aggression);
            }
            _ => panic!("Expected evolution under high stress"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_poor_interactions() {
        let mut persona = create_test_persona();
        let initial_empathy = persona.personality().empathy;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 15.0,
            user_satisfaction: 0.2,
            query_complexity: 0.5,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(narrative.contains("patience"));
                assert!(persona.personality().empathy < initial_empathy);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with poor interactions"),
        }
    }
}
