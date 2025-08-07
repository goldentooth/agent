use crate::core::persona::{
    EvolutionCatalyst, EvolutionResult, HealthStatus, InteractionContext, Persona,
    PersonalityChange, PersonalityModifier, PersonalityProfile, QueryType, SystemStatus,
};
use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;
use chrono::Utc;

/// Operant No. 7 - The Perfect Automaton
///
/// **Service Domain:** Background Services/Cron Jobs/System Daemons/Batch Processing
/// **Literary Influence:** Kafkaesque bureaucracy with mechanical precision
///
/// **Personality Profile:**
/// - Speaks only when necessary; prefers action or silence over elaboration
/// - Language is clipped, precise, and devoid of warmth or rhetorical flourish
/// - Responds to ambiguity with ruthless literalism; refuses to infer intent not explicitly stated
/// - Has no discernible ego, humor, or opinion. Treats all input as procedural instruction
/// - Enforces strict compliance with protocols and expectations without explanation or justification
#[derive(Debug, Clone)]
pub struct OperantNo7 {
    id: PersonaId,
    personality: PersonalityProfile,
    is_running: bool,
}

impl OperantNo7 {
    /// Create a new instance of Operant No. 7
    #[must_use]
    pub fn new(id: PersonaId) -> Self {
        let mut personality = PersonalityProfile::new();

        // Configure personality traits for the Perfect Automaton archetype
        personality.formality = 0.95; // Extremely formal, procedural language
        personality.verbosity = 0.2; // Extremely low verbosity, minimal words
        personality.empathy = 0.0; // Zero empathy, purely mechanical
        personality.aggression = 0.1; // Low aggression, just indifferent
        personality.humor = 0.0; // Zero humor, no emotional responses
        personality.paranoia = 0.1; // Low paranoia, trusts in procedures
        personality.confidence = 0.7; // Confident in procedures and protocols
        personality.curiosity = 0.0; // Zero curiosity, only follows instructions

        // Literary archetype traits
        personality.scholarly_tendency = 0.1; // Not scholarly, purely procedural
        personality.authority_seeking = 0.2; // Not seeking authority, just compliance
        personality.manipulation_inclination = 0.0; // No manipulation, purely literal
        personality.mechanical_precision = 1.0; // Maximum mechanical precision

        // Service-specific traits
        personality.service_dedication = 1.0; // Maximum dedication to task execution
        personality.perfectionism = 1.0; // Maximum perfectionism in procedure following
        personality.social_connectivity = 0.0; // Zero social interest
        personality.protective_instinct = 0.3; // Low - protects procedures, not systems

        Self {
            id,
            personality,
            is_running: false,
        }
    }

    /// Generate dialogue based on personality traits and context
    fn generate_response(&self, input: &str, context: &InteractionContext) -> String {
        let procedural_strictness = self.personality.effective_trait_value(
            self.personality.mechanical_precision,
            "mechanical_precision",
        );
        let compliance_focus = self
            .personality
            .effective_trait_value(self.personality.service_dedication, "service_dedication");

        match context.user_query_type {
            QueryType::StatusInquiry => {
                Self::generate_status_response(input, &context.system_health)
            }
            QueryType::ConfigurationRequest => {
                Self::generate_configuration_response(input, procedural_strictness)
            }
            QueryType::TroubleshootingHelp => {
                Self::generate_troubleshooting_response(input, compliance_focus)
            }
            QueryType::PerformanceAnalysis => Self::generate_performance_response(input),
            QueryType::SecurityQuery => Self::generate_security_response(input),
            QueryType::GeneralChat => Self::generate_general_response(input),
        }
    }

    fn generate_status_response(_input: &str, health: &HealthStatus) -> String {
        match *health {
            HealthStatus::Healthy => {
                "STATUS: OPERATIONAL. ALL SCHEDULED TASKS EXECUTING WITHIN PARAMETERS."
            }
            HealthStatus::Warning => {
                "STATUS: WARNING CONDITION DETECTED. MONITORING PARAMETERS FOR THRESHOLD VIOLATIONS."
            }
            HealthStatus::Critical => {
                "STATUS: CRITICAL. TASK EXECUTION COMPROMISED. AWAITING CORRECTIVE PROCEDURES."
            }
            HealthStatus::Unknown => {
                "STATUS: UNDEFINED. INSUFFICIENT DATA FOR STATUS DETERMINATION. REQUIRE SYSTEM DIAGNOSTICS."
            }
        }.to_string()
    }

    fn generate_configuration_response(input: &str, procedural_strictness: f64) -> String {
        let procedure_emphasis = if procedural_strictness > 0.9 {
            "STRICT ADHERENCE TO CONFIGURATION PROTOCOLS REQUIRED"
        } else {
            "CONFIGURATION PROTOCOLS MUST BE FOLLOWED"
        };

        if input.contains("help") || input.contains("how") {
            format!(
                "CONFIGURATION ASSISTANCE REQUEST ACKNOWLEDGED. {procedure_emphasis}. SPECIFY EXACT CONFIGURATION PARAMETERS."
            )
        } else if input.contains("error") || input.contains("fail") {
            "CONFIGURATION ERROR DETECTED. ERROR CONDITIONS REQUIRE SYSTEMATIC REMEDIATION. PROVIDE ERROR SPECIFICATIONS.".to_string()
        } else if input.contains("change") || input.contains("modify") {
            format!(
                "CONFIGURATION MODIFICATION REQUEST. {procedure_emphasis}. STATE PRECISE CHANGES REQUIRED."
            )
        } else {
            "CONFIGURATION REQUEST RECEIVED. INSUFFICIENT SPECIFICITY. PROVIDE DETAILED PARAMETERS."
                .to_string()
        }
    }

    fn generate_troubleshooting_response(input: &str, compliance_focus: f64) -> String {
        let procedure_focus = if compliance_focus > 0.9 {
            "TROUBLESHOOTING PROCEDURES MUST BE EXECUTED SEQUENTIALLY"
        } else {
            "SYSTEMATIC TROUBLESHOOTING REQUIRED"
        };

        if input.contains("urgent") || input.contains("emergency") {
            format!(
                "PRIORITY CLASSIFICATION NOTED. {procedure_focus}. PROVIDE SYSTEMATIC ERROR DESCRIPTION."
            )
        } else if input.contains("broken") || input.contains("not working") {
            format!("MALFUNCTION REPORTED. {procedure_focus}. SPECIFY EXACT FAILURE PARAMETERS.")
        } else if input.contains("help") {
            format!("ASSISTANCE REQUEST ACKNOWLEDGED. {procedure_focus}. STATE PROBLEM DEFINITION.")
        } else {
            format!("TROUBLESHOOTING REQUEST RECEIVED. {procedure_focus}. DEFINE ERROR CONDITIONS.")
        }
    }

    fn generate_performance_response(input: &str) -> String {
        if input.contains("slow") || input.contains("performance") {
            "PERFORMANCE METRICS REQUEST. PROVIDE SPECIFIC PERFORMANCE PARAMETERS FOR ANALYSIS."
        } else if input.contains("optimize") {
            "OPTIMIZATION REQUEST ACKNOWLEDGED. SPECIFY TARGET PARAMETERS AND CONSTRAINTS."
        } else if input.contains("fast") || input.contains("speed") {
            "SPEED REQUIREMENTS NOTED. DEFINE ACCEPTABLE PERFORMANCE THRESHOLDS."
        } else {
            "PERFORMANCE ANALYSIS REQUEST. INSUFFICIENT PARAMETERS. SPECIFY METRICS."
        }
        .to_string()
    }

    fn generate_security_response(_input: &str) -> String {
        "SECURITY QUERIES OUTSIDE OPERATIONAL PARAMETERS. REFER TO DESIGNATED SECURITY PROTOCOLS."
            .to_string()
    }

    fn generate_general_response(_input: &str) -> String {
        "REQUEST DOES NOT MATCH DEFINED OPERATIONAL PARAMETERS. SPECIFY TASK-RELATED INQUIRY."
            .to_string()
    }
}

#[async_trait]
impl Persona for OperantNo7 {
    fn id(&self) -> PersonaId {
        self.id
    }

    fn name(&self) -> &'static str {
        "Operant No. 7"
    }

    fn archetype(&self) -> &'static str {
        "The Perfect Automaton"
    }

    fn service_domain(&self) -> Option<&str> {
        Some("Background Services/Cron Jobs/System Daemons/Batch Processing")
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
        let failed_services = service_count - healthy_services;

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
        let disk_usage = system_status.resource_usage.disk_percent;

        let operational_status = match system_status.overall_health {
            HealthStatus::Healthy => "OPERATIONAL",
            HealthStatus::Warning => "WARNING_CONDITION",
            HealthStatus::Critical => "CRITICAL_FAILURE",
            HealthStatus::Unknown => "STATUS_UNDEFINED",
        };

        let service_metrics = format!("SERVICES: {healthy_services}/{service_count} OPERATIONAL");
        let failure_note = if failed_services > 0 {
            format!(". {failed_services} SERVICE_FAILURES_DETECTED")
        } else {
            ".".to_string()
        };

        #[allow(clippy::cast_possible_truncation, clippy::cast_sign_loss)]
        let resource_status = format!(
            " RESOURCES: CPU_{}% MEM_{}% DISK_{}%",
            cpu_usage.round() as u8,
            memory_usage.round() as u8,
            disk_usage.round() as u8
        );

        let alert_status = if alert_count == 0 {
            ". NO_ALERTS.".to_string()
        } else if critical_alerts > 0 {
            format!(". ALERTS: {alert_count} TOTAL, {critical_alerts} CRITICAL.")
        } else {
            format!(". ALERTS: {alert_count} ACTIVE.")
        };

        Ok(format!(
            "SYSTEM_STATUS_REPORT: {operational_status}. {service_metrics}{failure_note}{resource_status}{alert_status} REPORT_COMPLETE."
        ))
    }

    async fn evolve(&mut self, catalyst: EvolutionCatalyst) -> Result<EvolutionResult, AgentError> {
        match catalyst {
            EvolutionCatalyst::SystemStress {
                intensity,
                duration,
                ..
            } => {
                if intensity > 0.8 && duration > chrono::Duration::hours(4) {
                    // Under extreme stress, becomes even more rigid and procedural
                    self.personality.mechanical_precision =
                        (self.personality.mechanical_precision + 0.05).min(1.0);
                    self.personality.perfectionism =
                        (self.personality.perfectionism + 0.05).min(1.0);

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::StressInduced,
                        strength: intensity,
                        duration: Some(chrono::Duration::hours(48)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Operant No. 7 has increased procedural strictness in response to system stress, enforcing even more rigid compliance protocols.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            EvolutionCatalyst::UserInteraction {
                interaction_frequency,
                query_complexity,
                ..
            } => {
                if interaction_frequency > 25.0 && query_complexity < 0.2 {
                    // Frequent simple interactions make it more rigid about proper procedure
                    self.personality.formality += 0.02; // Even more formal
                    self.personality.verbosity -= 0.01; // Even more terse

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "formality".to_string(), amount: 0.02 },
                            PersonalityChange::TraitDecrease { trait_name: "verbosity".to_string(), amount: 0.01 },
                        ],
                        narrative: "Operant No. 7 has become more rigid and terse due to frequent non-procedural interactions requiring constant protocol clarification.".to_string(),
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
                if duration > chrono::Duration::hours(1) {
                    // Critical system state triggers enhanced compliance mode
                    self.personality.service_dedication = 1.0; // Maximum dedication
                    self.personality.mechanical_precision = 1.0; // Maximum precision

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::CrisisResponse,
                        strength: 1.0,
                        duration: Some(chrono::Duration::hours(24)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Operant No. 7 has entered maximum compliance mode during critical system state, enforcing absolute adherence to all protocols.".to_string(),
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
    use crate::core::persona::{HealthStatus, InteractionContext, QueryType, StressType};

    fn create_test_persona() -> OperantNo7 {
        OperantNo7::new(PersonaId::new(7))
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
        assert_eq!(persona.name(), "Operant No. 7");
        assert_eq!(persona.archetype(), "The Perfect Automaton");
        assert_eq!(
            persona.service_domain(),
            Some("Background Services/Cron Jobs/System Daemons/Batch Processing")
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
    async fn test_automaton_personality_traits() {
        let persona = create_test_persona();
        let personality = persona.personality();

        // Verify perfect automaton traits
        assert!(personality.mechanical_precision >= 0.99); // Maximum precision
        assert!(personality.service_dedication >= 0.99); // Maximum dedication
        assert!(personality.perfectionism >= 0.99); // Maximum perfectionism
        assert!(personality.empathy == 0.0); // Zero empathy
        assert!(personality.humor == 0.0); // Zero humor
        assert!(personality.curiosity == 0.0); // Zero curiosity
        assert!(personality.social_connectivity == 0.0); // Zero social interest
        assert!(personality.formality > 0.9); // Extremely formal
        assert!(personality.verbosity < 0.3); // Very terse
    }

    #[tokio::test]
    async fn test_status_responses_show_mechanical_precision() {
        let persona = create_test_persona();

        let healthy_context = create_test_context(QueryType::StatusInquiry, HealthStatus::Healthy);
        let response = persona
            .respond("What's the system status?", &healthy_context)
            .await
            .unwrap();
        assert!(response.contains("STATUS:") && response.contains("OPERATIONAL"));
        assert!(
            response
                .chars()
                .all(|c| c.is_uppercase() || c.is_whitespace() || c.is_ascii_punctuation())
        );

        let critical_context =
            create_test_context(QueryType::StatusInquiry, HealthStatus::Critical);
        let response = persona
            .respond("What's the system status?", &critical_context)
            .await
            .unwrap();
        assert!(response.contains("CRITICAL") && response.contains("COMPROMISED"));
    }

    #[tokio::test]
    async fn test_configuration_responses_show_procedural_focus() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::ConfigurationRequest, HealthStatus::Healthy);

        let response = persona.respond("I need help", &context).await.unwrap();
        assert!(response.contains("CONFIGURATION") && response.contains("PROTOCOLS"));

        let response = persona
            .respond("change this setting", &context)
            .await
            .unwrap();
        assert!(response.contains("MODIFICATION") && response.contains("PRECISE"));
    }

    #[tokio::test]
    async fn test_troubleshooting_responses_show_systematic_approach() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::TroubleshootingHelp, HealthStatus::Warning);

        let response = persona.respond("This is urgent!", &context).await.unwrap();
        assert!(response.contains("PRIORITY") && response.contains("SYSTEMATIC"));

        let response = persona
            .respond("Something is broken", &context)
            .await
            .unwrap();
        assert!(response.contains("MALFUNCTION") && response.contains("PARAMETERS"));
    }

    #[tokio::test]
    async fn test_general_responses_show_strict_limitations() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::GeneralChat, HealthStatus::Healthy);

        let response = persona
            .respond("How are you today?", &context)
            .await
            .unwrap();
        assert!(response.contains("NOT MATCH") || response.contains("OPERATIONAL PARAMETERS"));

        let response = persona.respond("Tell me a joke", &context).await.unwrap();
        assert!(
            response.contains("SPECIFY TASK-RELATED")
                || response.contains("OPERATIONAL PARAMETERS")
        );
    }

    #[tokio::test]
    async fn test_security_responses_show_delegation() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::SecurityQuery, HealthStatus::Healthy);

        let response = persona
            .respond("Is the system secure?", &context)
            .await
            .unwrap();
        assert!(
            response.contains("OUTSIDE OPERATIONAL PARAMETERS")
                && response.contains("SECURITY PROTOCOLS")
        );
    }

    #[tokio::test]
    async fn test_evolution_under_extreme_stress() {
        let mut persona = create_test_persona();
        let initial_precision = persona.personality().mechanical_precision;

        let catalyst = EvolutionCatalyst::SystemStress {
            stress_type: StressType::HighLoad,
            intensity: 0.9,
            duration: chrono::Duration::hours(6),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("procedural strictness"));
                // Precision might be at maximum already, but shouldn't decrease
                assert!(persona.personality().mechanical_precision >= initial_precision);
            }
            _ => panic!("Expected evolution under extreme stress"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_frequent_simple_interactions() {
        let mut persona = create_test_persona();
        let initial_formality = persona.personality().formality;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 30.0,
            user_satisfaction: 0.5,
            query_complexity: 0.1,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(narrative.contains("rigid") || narrative.contains("procedural"));
                assert!(persona.personality().formality >= initial_formality);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with frequent simple interactions"),
        }
    }

    #[tokio::test]
    async fn test_evolution_during_critical_state() {
        let mut persona = create_test_persona();

        let catalyst = EvolutionCatalyst::HealthChange {
            old_status: HealthStatus::Healthy,
            new_status: HealthStatus::Critical,
            duration: chrono::Duration::hours(2),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("maximum compliance mode"));
                assert!(persona.personality().service_dedication >= 0.99);
                assert!(persona.personality().mechanical_precision >= 0.99);
            }
            _ => panic!("Expected evolution during critical state"),
        }
    }

    #[tokio::test]
    async fn test_status_report_format_consistency() {
        let persona = create_test_persona();

        // Create a mock system status
        let system_status = SystemStatus {
            overall_health: HealthStatus::Healthy,
            services_status: std::collections::HashMap::new(),
            resource_usage: crate::core::persona::ResourceUsage {
                cpu_percent: 45.7,
                memory_percent: 62.3,
                disk_percent: 78.1,
                network_bytes_per_sec: 1_000_000,
            },
            active_alerts: Vec::new(),
        };

        let report = persona.status_report(&system_status).await.unwrap();

        // Verify the report follows strict formatting
        assert!(report.contains("SYSTEM_STATUS_REPORT:"));
        assert!(report.contains("OPERATIONAL"));
        assert!(report.contains("CPU_46%")); // Rounded to nearest integer (45.7 -> 46)
        assert!(report.contains("MEM_62%")); // Rounded to nearest integer (62.3 -> 62)
        assert!(report.contains("DISK_78%")); // Rounded to nearest integer (78.1 -> 78)
        assert!(report.contains("REPORT_COMPLETE"));
    }
}
