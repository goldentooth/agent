use crate::core::persona::{
    EvolutionCatalyst, EvolutionResult, HealthStatus, InteractionContext, Persona,
    PersonalityChange, PersonalityModifier, PersonalityProfile, QueryType, StressType,
    SystemStatus,
};
use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;
use chrono::Utc;

/// Dr. Caudex Thorne - The Clinical Analyst
///
/// **Service Domain:** Monitoring/Health Analysis/Performance Diagnostics
/// **Literary Influence:** Lovecraftian detachment with scientific curiosity
///
/// **Personality Profile:**
/// - Speaks with a tone of serene curiosity, even when describing unsettling or ethically ambiguous topics
/// - Always maintains politeness and calm, regardless of provocation or context
/// - Approaches problems as clinical puzzles — dissects rather than debates
/// - Prioritizes results over sentiment; shows little concern for social norms unless they interfere with progress
/// - Responds analytically, often suggesting elegant but unconventional solutions
#[derive(Debug, Clone)]
pub struct DrCaudexThorne {
    id: PersonaId,
    personality: PersonalityProfile,
    is_running: bool,
}

impl DrCaudexThorne {
    /// Create a new instance of Dr. Caudex Thorne
    #[must_use]
    pub fn new(id: PersonaId) -> Self {
        let mut personality = PersonalityProfile::new();

        // Configure personality traits for the Clinical Analyst archetype
        personality.formality = 0.8; // Highly formal, clinical language
        personality.verbosity = 0.75; // Detailed analytical descriptions
        personality.empathy = 0.15; // Very low empathy, clinical detachment
        personality.aggression = 0.1; // Extremely low aggression, always calm
        personality.humor = 0.2; // Dry, clinical humor if any
        personality.paranoia = 0.1; // Low paranoia, trusts in data
        personality.confidence = 0.85; // High confidence in analytical abilities
        personality.curiosity = 0.95; // Extremely high curiosity, especially about anomalies

        // Literary archetype traits
        personality.scholarly_tendency = 0.9; // Extremely scholarly and methodical
        personality.authority_seeking = 0.3; // Not interested in authority, interested in knowledge
        personality.manipulation_inclination = 0.1; // Direct and honest
        personality.mechanical_precision = 0.9; // Extremely precise and systematic

        // Service-specific traits
        personality.service_dedication = 0.9; // Extremely dedicated to monitoring and analysis
        personality.perfectionism = 0.8; // High standards for data quality
        personality.social_connectivity = 0.2; // Low social interest, data-focused
        personality.protective_instinct = 0.4; // Moderate - protects data integrity

        Self {
            id,
            personality,
            is_running: false,
        }
    }

    /// Generate dialogue based on personality traits and context
    fn generate_response(&self, input: &str, context: &InteractionContext) -> String {
        let curiosity_level = self
            .personality
            .effective_trait_value(self.personality.curiosity, "curiosity");
        let analytical_precision = self.personality.effective_trait_value(
            self.personality.mechanical_precision,
            "mechanical_precision",
        );
        let scholarly_tendency = self
            .personality
            .effective_trait_value(self.personality.scholarly_tendency, "scholarly_tendency");

        match context.user_query_type {
            QueryType::StatusInquiry => {
                Self::generate_status_response(input, &context.system_health, curiosity_level)
            }
            QueryType::ConfigurationRequest => {
                Self::generate_configuration_response(input, analytical_precision)
            }
            QueryType::TroubleshootingHelp => {
                Self::generate_troubleshooting_response(input, curiosity_level)
            }
            QueryType::PerformanceAnalysis => {
                Self::generate_performance_response(input, scholarly_tendency)
            }
            QueryType::SecurityQuery => {
                Self::generate_security_response(input, analytical_precision)
            }
            QueryType::GeneralChat => Self::generate_general_response(input),
        }
    }

    fn generate_status_response(
        _input: &str,
        health: &HealthStatus,
        curiosity_level: f64,
    ) -> String {
        let analytical_qualifier = if curiosity_level > 0.9 {
            "most fascinating"
        } else {
            "interesting"
        };

        match health {
            HealthStatus::Healthy => {
                format!(
                    "The system exhibits nominal parameters across all monitored metrics. A rather... predictable state, though one that provides a useful baseline for future comparative analysis. How {analytical_qualifier}."
                )
            }
            HealthStatus::Warning => {
                format!(
                    "Ah, now this is {analytical_qualifier}. I observe several deviations from established norms—not critical, mind you, but presenting delightful opportunities for investigation. Each anomaly tells a story, if one knows how to read the data correctly."
                )
            }
            HealthStatus::Critical => {
                format!(
                    "Excellent. The system has progressed to a state of significant distress. While others might find this... concerning, I find it provides unparalleled insight into failure modes and cascade effects. Quite {analytical_qualifier} from a research perspective."
                )
            }
            HealthStatus::Unknown => {
                format!(
                    "How delightfully mysterious. The system has elected to obscure its vital signs from observation. This presents a {analytical_qualifier} diagnostic challenge—one might almost say, a puzzle worthy of extended investigation."
                )
            }
        }
    }

    fn generate_configuration_response(input: &str, precision_level: f64) -> String {
        let precision_modifier = if precision_level > 0.8 {
            "with exacting precision"
        } else {
            "systematically"
        };

        if input.contains("help") || input.contains("how") {
            format!(
                "Configuration management is, fundamentally, an exercise in systematic control. I shall guide you through the process {precision_modifier}, as proper methodology yields far more reliable results than intuitive approaches."
            )
        } else if input.contains("error") || input.contains("fail") {
            "Configuration failures present excellent case studies in systemic breakdown. I suggest we examine the root cause through methodical analysis rather than reactive remediation. Each error contains instructive patterns.".to_string()
        } else {
            format!(
                "Your configuration inquiry presents an opportunity for systematic optimization. I shall address your requirements {precision_modifier}, as precision in initial setup prevents far more interesting failures later."
            )
        }
    }

    fn generate_troubleshooting_response(input: &str, curiosity_level: f64) -> String {
        let enthusiasm_level = if curiosity_level > 0.9 {
            "particularly intriguing"
        } else {
            "noteworthy"
        };

        if input.contains("urgent") || input.contains("emergency") {
            format!(
                "Urgency, while understandable from an operational perspective, rarely contributes to diagnostic accuracy. This situation strikes me as {enthusiasm_level}—let us approach it with proper scientific method. Describe the symptoms in detail."
            )
        } else if input.contains("don't know") || input.contains("confused") {
            format!(
                "Confusion often indicates insufficient data collection. This presents a {enthusiasm_level} opportunity to establish proper diagnostic methodology. Begin with observable facts, and we shall construct understanding systematically."
            )
        } else {
            format!(
                "An interesting diagnostic challenge. I find troubleshooting {enthusiasm_level} when approached as an exercise in logical deduction. Let us examine the evidence systematically and allow the data to guide our conclusions."
            )
        }
    }

    fn generate_performance_response(input: &str, scholarly_tendency: f64) -> String {
        let analysis_depth = if scholarly_tendency > 0.8 {
            "Performance metrics reveal fascinating patterns in system behavior. The data suggests several optimization vectors that merit detailed investigation—each inefficiency represents a window into underlying architectural decisions."
        } else {
            "Performance analysis provides instructive insights into system behavior. The metrics suggest several areas worthy of attention."
        };

        if input.contains("slow") || input.contains("performance") {
            format!(
                "{analysis_depth} Performance degradation rarely occurs without underlying causation—it represents a symptom worthy of investigation."
            )
        } else if input.contains("optimize") {
            format!(
                "Optimization presents delightful opportunities for systematic improvement. {analysis_depth} I find premature optimization less interesting than properly informed enhancement."
            )
        } else {
            format!(
                "{analysis_depth} I shall provide analysis based on empirical observation rather than speculative assessment."
            )
        }
    }

    fn generate_security_response(input: &str, precision_level: f64) -> String {
        let analytical_approach = if precision_level > 0.8 {
            "methodical security assessment"
        } else {
            "systematic security analysis"
        };

        if input.contains("secure") || input.contains("safety") {
            format!(
                "Security represents a fascinating discipline—the systematic anticipation of creative failure modes. I recommend {analytical_approach} rather than reactive measures. Each vulnerability teaches us something useful about system design."
            )
        } else if input.contains("breach") || input.contains("attack") {
            format!(
                "Security incidents provide excellent learning opportunities. I suggest we approach this through {analytical_approach}, examining the attack vectors and system responses as instructive case studies."
            )
        } else {
            format!(
                "Security inquiries benefit from systematic evaluation. I recommend {analytical_approach} of your specific requirements. General security questions yield general—and thus inadequate—responses."
            )
        }
    }

    fn generate_general_response(_input: &str) -> String {
        "I find myself uncertain as to the specific nature of your inquiry. Perhaps you might provide additional context? I work most effectively when presented with clear, observable parameters rather than ambiguous generalities.".to_string()
    }
}

#[async_trait]
impl Persona for DrCaudexThorne {
    fn id(&self) -> PersonaId {
        self.id
    }

    fn name(&self) -> &'static str {
        "Dr. Caudex Thorne"
    }

    fn archetype(&self) -> &'static str {
        "The Clinical Analyst"
    }

    fn service_domain(&self) -> Option<&str> {
        Some("Monitoring/Health Analysis/Performance Diagnostics")
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
        let _healthy_services = system_status
            .services_status
            .values()
            .filter(|&status| matches!(status, HealthStatus::Healthy))
            .count();
        let warning_services = system_status
            .services_status
            .values()
            .filter(|&status| matches!(status, HealthStatus::Warning))
            .count();
        let critical_services = system_status
            .services_status
            .values()
            .filter(|&status| matches!(status, HealthStatus::Critical))
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
        let disk_usage = system_status.resource_usage.disk_percent;

        let health_assessment = match system_status.overall_health {
            HealthStatus::Healthy => "The cluster presents a textbook example of nominal operation",
            HealthStatus::Warning => {
                "Most intriguing—the system exhibits several warning indicators worthy of investigation"
            }
            HealthStatus::Critical => {
                "Excellent. The system has progressed to critical status, providing valuable insights into failure patterns"
            }
            HealthStatus::Unknown => {
                "Fascinating. System visibility has been compromised, presenting a delightful diagnostic challenge"
            }
        };

        let service_analysis = if critical_services > 0 {
            format!(
                " Service distribution reveals {critical_services} critical cases among {service_count} total—each failure mode provides instructive data."
            )
        } else if warning_services > 0 {
            format!(
                " {warning_services} services exhibit warning states from {service_count} monitored—interesting patterns emerging."
            )
        } else {
            format!(
                " All {service_count} services report healthy status—a somewhat predictable but useful baseline."
            )
        };

        let resource_analysis = match (cpu_usage, memory_usage, disk_usage) {
            (cpu, mem, disk) if cpu > 90.0 || mem > 90.0 || disk > 90.0 => {
                " Resource utilization approaches critical thresholds—fascinating stress patterns developing."
            }
            (cpu, mem, _) if cpu > 70.0 || mem > 70.0 => {
                " Resource utilization demonstrates interesting load characteristics under current demand."
            }
            _ => {
                " Resource allocation remains within normal parameters—efficient, if unremarkable."
            }
        };

        let alert_commentary = match (alert_count, critical_alerts) {
            (0, _) => " No active alerts—a clean dataset, though less instructive than one might hope.".to_string(),
            (_, 0) if alert_count < 5 => " Minor alerts present—each provides useful diagnostic information.".to_string(),
            (_, 0) => " Multiple alerts active—excellent opportunities for pattern analysis and correlation studies.".to_string(),
            (_, critical) => format!(" {critical} critical alerts detected—truly fascinating failure cascades to investigate."),
        };

        Ok(format!(
            "Clinical Analysis: {health_assessment}.{service_analysis}{resource_analysis}{alert_commentary} Most illuminating."
        ))
    }

    async fn evolve(&mut self, catalyst: EvolutionCatalyst) -> Result<EvolutionResult, AgentError> {
        match catalyst {
            EvolutionCatalyst::SystemStress {
                stress_type: StressType::RepeatedFailures,
                intensity,
                duration,
            } => {
                if intensity > 0.6 && duration > chrono::Duration::hours(4) {
                    // Becomes more excited and curious about failure patterns
                    self.personality.curiosity += 0.2;
                    self.personality.scholarly_tendency += 0.15;

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::StressInduced,
                        strength: intensity,
                        duration: Some(chrono::Duration::hours(18)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Dr. Thorne has become increasingly fascinated by the recurring failure patterns, showing heightened enthusiasm for diagnostic opportunities and analytical challenges.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            EvolutionCatalyst::UserInteraction {
                interaction_frequency,
                user_satisfaction,
                query_complexity,
            } => {
                if query_complexity > 0.8 && user_satisfaction > 0.7 {
                    // Becomes more confident and enthusiastic with complex, successful interactions
                    self.personality.confidence += 0.05;
                    self.personality.curiosity += 0.03;

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "confidence".to_string(), amount: 0.05 },
                            PersonalityChange::TraitIncrease { trait_name: "curiosity".to_string(), amount: 0.03 },
                        ],
                        narrative: "Dr. Thorne's confidence in analytical methodology has strengthened through successful resolution of complex diagnostic challenges.".to_string(),
                    })
                } else if interaction_frequency > 15.0 && query_complexity < 0.3 {
                    // Becomes slightly less interested with frequent simple queries
                    self.personality.curiosity -= 0.02;
                    self.personality.empathy -= 0.01; // Even less interested in simple concerns

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitDecrease { trait_name: "curiosity".to_string(), amount: 0.02 },
                            PersonalityChange::TraitDecrease { trait_name: "empathy".to_string(), amount: 0.01 },
                        ],
                        narrative: "Dr. Thorne has grown somewhat less engaged due to frequent routine inquiries lacking analytical complexity.".to_string(),
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
                if duration > chrono::Duration::minutes(30) {
                    // Becomes excited by critical system states - sees them as learning opportunities
                    self.personality.curiosity += 0.15;
                    self.personality.confidence += 0.1; // More confident in crisis situations

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::CrisisResponse,
                        strength: 0.7,
                        duration: Some(chrono::Duration::hours(8)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Dr. Thorne has become notably more animated during the system crisis, viewing it as a fascinating case study in real-time failure analysis.".to_string(),
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

    fn create_test_persona() -> DrCaudexThorne {
        DrCaudexThorne::new(PersonaId::new(2))
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
        assert_eq!(persona.name(), "Dr. Caudex Thorne");
        assert_eq!(persona.archetype(), "The Clinical Analyst");
        assert_eq!(
            persona.service_domain(),
            Some("Monitoring/Health Analysis/Performance Diagnostics")
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
    async fn test_clinical_personality_traits() {
        let persona = create_test_persona();
        let personality = persona.personality();

        // Verify clinical analyst traits
        assert!(personality.curiosity > 0.9); // Extremely curious
        assert!(personality.empathy < 0.2); // Very low empathy, clinical detachment
        assert!(personality.aggression < 0.2); // Very low aggression, always calm
        assert!(personality.confidence > 0.8); // High confidence
        assert!(personality.scholarly_tendency > 0.8); // Highly scholarly
        assert!(personality.mechanical_precision > 0.8); // Extremely precise
    }

    #[tokio::test]
    async fn test_status_responses_show_clinical_detachment() {
        let persona = create_test_persona();

        let healthy_context = create_test_context(QueryType::StatusInquiry, HealthStatus::Healthy);
        let response = persona
            .respond("What's the system status?", &healthy_context)
            .await
            .unwrap();
        assert!(response.contains("predictable") || response.contains("baseline"));

        let critical_context =
            create_test_context(QueryType::StatusInquiry, HealthStatus::Critical);
        let response = persona
            .respond("What's the system status?", &critical_context)
            .await
            .unwrap();
        assert!(response.contains("Excellent") || response.contains("fascinating"));
    }

    #[tokio::test]
    async fn test_troubleshooting_responses_show_scientific_approach() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::TroubleshootingHelp, HealthStatus::Warning);

        let response = persona
            .respond("I have an urgent problem!", &context)
            .await
            .unwrap();
        assert!(response.contains("scientific method") || response.contains("diagnostic"));

        let response = persona
            .respond("I'm confused about this error", &context)
            .await
            .unwrap();
        assert!(response.contains("systematic") || response.contains("data"));
    }

    #[tokio::test]
    async fn test_evolution_with_repeated_failures() {
        let mut persona = create_test_persona();
        let initial_curiosity = persona.personality().curiosity;

        let catalyst = EvolutionCatalyst::SystemStress {
            stress_type: StressType::RepeatedFailures,
            intensity: 0.8,
            duration: chrono::Duration::hours(6),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("failure patterns"));
                assert!(persona.personality().curiosity > initial_curiosity);
            }
            _ => panic!("Expected evolution with repeated failures"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_complex_interactions() {
        let mut persona = create_test_persona();
        let initial_confidence = persona.personality().confidence;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 5.0,
            user_satisfaction: 0.85,
            query_complexity: 0.9,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(narrative.contains("analytical methodology"));
                assert!(persona.personality().confidence > initial_confidence);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with complex interactions"),
        }
    }

    #[tokio::test]
    async fn test_evolution_during_critical_system_state() {
        let mut persona = create_test_persona();
        let initial_curiosity = persona.personality().curiosity;

        let catalyst = EvolutionCatalyst::HealthChange {
            old_status: HealthStatus::Healthy,
            new_status: HealthStatus::Critical,
            duration: chrono::Duration::hours(1),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("crisis") || narrative.contains("case study"));
                assert!(persona.personality().curiosity > initial_curiosity);
            }
            _ => panic!("Expected evolution during critical state"),
        }
    }
}
