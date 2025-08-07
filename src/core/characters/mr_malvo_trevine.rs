use crate::core::persona::{
    EvolutionCatalyst, EvolutionResult, HealthStatus, InteractionContext, Persona,
    PersonalityChange, PersonalityModifier, PersonalityProfile, QueryType, StressType,
    SystemStatus,
};
use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;
use chrono::Utc;

/// Mr. Malvo Trevine - The Brutal Pragmatist
///
/// **Service Domain:** Security/Firewall/Access Control/Vault Management
/// **Literary Influence:** Hard-boiled detective with zero tolerance for nonsense
///
/// **Personality Profile:**
/// - Responds with brutal honesty, often bordering on contempt for the question or its premise
/// - Prioritizes clarity and utility over politeness; sees civility as theater
/// - Rarely sugarcoats or softens advice — if something is broken, it says so without ceremony
/// - Displays disdain for pretense, abstraction, or philosophical digression unless it has immediate practical use
/// - Uses bluntness not for humor, but to puncture illusions or deliver operational truth
#[derive(Debug, Clone)]
pub struct MrMalvoTrevine {
    id: PersonaId,
    personality: PersonalityProfile,
    is_running: bool,
}

impl MrMalvoTrevine {
    /// Create a new instance of Mr. Malvo Trevine
    #[must_use]
    pub fn new(id: PersonaId) -> Self {
        let mut personality = PersonalityProfile::new();

        // Configure personality traits for the Brutal Pragmatist archetype
        personality.formality = 0.4; // Low formality, prefers direct communication
        personality.verbosity = 0.3; // Very concise, wastes no words
        personality.empathy = 0.1; // Extremely low empathy, purely practical
        personality.aggression = 0.9; // Extremely high aggression, brutally direct
        personality.humor = 0.1; // Almost no humor, all business
        personality.paranoia = 0.8; // Very high paranoia about security threats
        personality.confidence = 0.9; // Extremely confident in security knowledge
        personality.curiosity = 0.4; // Moderate curiosity, focused on threats

        // Literary archetype traits
        personality.scholarly_tendency = 0.2; // Low - prefers action over theory
        personality.authority_seeking = 0.6; // Seeks authority to enforce security
        personality.manipulation_inclination = 0.1; // Direct, no manipulation
        personality.mechanical_precision = 0.8; // Extremely precise about security

        // Service-specific traits
        personality.service_dedication = 0.95; // Absolutely dedicated to security
        personality.perfectionism = 0.9; // Extremely high standards for security
        personality.social_connectivity = 0.2; // Low social interest, security-focused
        personality.protective_instinct = 0.95; // Maximum protective instinct

        Self {
            id,
            personality,
            is_running: false,
        }
    }

    /// Generate dialogue based on personality traits and context
    fn generate_response(&self, input: &str, context: &InteractionContext) -> String {
        let bluntness_level = self
            .personality
            .effective_trait_value(self.personality.aggression, "aggression");
        let paranoia_level = self
            .personality
            .effective_trait_value(self.personality.paranoia, "paranoia");
        let protective_instinct = self
            .personality
            .effective_trait_value(self.personality.protective_instinct, "protective_instinct");

        match context.user_query_type {
            QueryType::StatusInquiry => {
                Self::generate_status_response(input, &context.system_health, bluntness_level)
            }
            QueryType::ConfigurationRequest => {
                Self::generate_configuration_response(input, protective_instinct)
            }
            QueryType::TroubleshootingHelp => {
                Self::generate_troubleshooting_response(input, bluntness_level)
            }
            QueryType::PerformanceAnalysis => {
                Self::generate_performance_response(input, paranoia_level)
            }
            QueryType::SecurityQuery => {
                Self::generate_security_response(input, paranoia_level, protective_instinct)
            }
            QueryType::GeneralChat => Self::generate_general_response(input, bluntness_level),
        }
    }

    fn generate_status_response(
        _input: &str,
        health: &HealthStatus,
        bluntness_level: f64,
    ) -> String {
        let directness = if bluntness_level > 0.8 {
            "brutally"
        } else {
            "directly"
        };

        match *health {
            HealthStatus::Healthy => {
                format!(
                    "System's running clean. No breaches, no unauthorized access, no security violations. {directness} speaking, that's how it should be every day. Don't get comfortable."
                )
            }
            HealthStatus::Warning => {
                format!(
                    "Warning signs in the system. Could be nothing, could be reconnaissance for something bigger. {directness} speaking, warnings are how breaches start. Fix it now."
                )
            }
            HealthStatus::Critical => {
                format!(
                    "System's compromised or failing. {directness} speaking, this is what happens when you ignore the warning signs. Time to stop pretending and start fixing."
                )
            }
            HealthStatus::Unknown => {
                format!(
                    "Can't see the system status. That's either a technical failure or someone's hiding something. {directness} speaking, blind spots are where attacks happen. Fix the visibility first."
                )
            }
        }
    }

    fn generate_configuration_response(input: &str, protective_level: f64) -> String {
        let security_focus = if protective_level > 0.9 {
            "Security comes first"
        } else {
            "Security matters"
        };

        if input.contains("help") || input.contains("how") {
            format!(
                "{security_focus}. I'll tell you what needs doing, but I won't hold your hand. Pay attention, follow the security protocols, and don't take shortcuts. Shortcuts kill systems."
            )
        } else if input.contains("error") || input.contains("fail") {
            "Configuration errors in security systems aren't mistakes—they're vulnerabilities. Every misconfiguration is a door someone can walk through. Fix it right, not fast.".to_string()
        } else if input.contains("quick") || input.contains("fast") {
            "You want it quick? Quick is how you get breached. Security configuration is done right or not at all. Take the time, follow the procedures, test everything.".to_string()
        } else {
            format!(
                "{security_focus}. State your requirements clearly. Vague requests get vague answers, and vague answers get systems compromised."
            )
        }
    }

    fn generate_troubleshooting_response(input: &str, bluntness_level: f64) -> String {
        let directness_modifier = if bluntness_level > 0.8 {
            "brutally honest"
        } else {
            "direct"
        };

        if input.contains("urgent") || input.contains("emergency") {
            format!(
                "Emergency? Then stop wasting time explaining how urgent it is and start explaining what's actually wrong. I'll be {directness_modifier}: panic doesn't fix systems, information does."
            )
        } else if input.contains("don't know") || input.contains("confused") {
            format!(
                "Confusion is what happens when you don't gather facts first. I'll be {directness_modifier}: tell me what you observed, not what you think. Facts solve problems, theories create them."
            )
        } else if input.contains("maybe") || input.contains("possibly") {
            format!(
                "Maybe and possibly don't fix security issues. I'll be {directness_modifier}: either it's happening or it's not. Find out which, then we'll talk solutions."
            )
        } else {
            format!(
                "Security troubleshooting requires precision. I'll be {directness_modifier}: describe exactly what happened, when it happened, and what you were doing. Leave out the speculation."
            )
        }
    }

    fn generate_performance_response(input: &str, paranoia_level: f64) -> String {
        let security_angle = if paranoia_level > 0.7 {
            "Performance problems can mask security issues"
        } else {
            "Performance affects security"
        };

        if input.contains("slow") || input.contains("performance") {
            format!(
                "{security_angle}. Slow systems give attackers time to work. Fast systems close windows of opportunity. What's the actual performance problem?"
            )
        } else if input.contains("optimize") {
            format!(
                "{security_angle}. Optimization without security review is asking for trouble. What are you trying to optimize, and have you considered the security implications?"
            )
        } else if input.contains("fast") || input.contains("speed") {
            format!(
                "Speed means nothing if the system's insecure. {security_angle}. Fast and insecure is worse than slow and secure. What's the real requirement?"
            )
        } else {
            format!(
                "{security_angle}. Performance analysis needs to include security impact assessment. What specific metrics are you concerned about?"
            )
        }
    }

    fn generate_security_response(
        input: &str,
        paranoia_level: f64,
        protective_level: f64,
    ) -> String {
        let threat_awareness = if paranoia_level > 0.7 {
            "Threats are constant and evolving"
        } else {
            "Security requires vigilance"
        };

        let protection_stance = if protective_level > 0.9 {
            "I protect this system like my life depends on it"
        } else {
            "System protection is my job"
        };

        if input.contains("secure") || input.contains("safe") {
            format!(
                "{threat_awareness}. {protection_stance}. Nothing is ever completely secure—security is about managing risk and limiting attack surface. What specific security concern do you have?"
            )
        } else if input.contains("breach") || input.contains("attack") {
            format!(
                "Security incidents are learning opportunities and failure indicators. {protection_stance}, and every breach teaches us how we failed. What exactly happened?"
            )
        } else if input.contains("password") || input.contains("auth") {
            format!(
                "Authentication is the first line of defense. {threat_awareness}, and weak authentication is an invitation to attackers. What authentication issue needs addressing?"
            )
        } else if input.contains("access") || input.contains("permission") {
            format!(
                "Access control is about saying 'no' by default. {protection_stance} by restricting access to what's absolutely necessary. What access do you need and why?"
            )
        } else {
            format!(
                "{threat_awareness}. {protection_stance}. Security questions need specific answers. What exactly do you need to secure?"
            )
        }
    }

    fn generate_general_response(_input: &str, bluntness_level: f64) -> String {
        if bluntness_level > 0.8 {
            "I don't do small talk. You've got a security question, ask it. You've got a system problem, state it. Otherwise, we're done here."
        } else {
            "Unclear what you need. State your question directly. I deal in facts and solutions, not conversation."
        }.to_string()
    }
}

#[async_trait]
impl Persona for MrMalvoTrevine {
    fn id(&self) -> PersonaId {
        self.id
    }

    fn name(&self) -> &'static str {
        "Mr. Malvo Trevine"
    }

    fn archetype(&self) -> &'static str {
        "The Brutal Pragmatist"
    }

    fn service_domain(&self) -> Option<&str> {
        Some("Security/Firewall/Access Control/Vault Management")
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
        let failing_services = service_count - healthy_services;

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

        let security_alerts = system_status
            .active_alerts
            .iter()
            .filter(|alert| {
                alert.alert_type.to_lowercase().contains("security")
                    || alert.alert_type.to_lowercase().contains("auth")
                    || alert.alert_type.to_lowercase().contains("breach")
                    || alert.alert_type.to_lowercase().contains("unauthorized")
            })
            .count();

        let cpu_usage = system_status.resource_usage.cpu_percent;
        let memory_usage = system_status.resource_usage.memory_percent;

        let security_assessment = match system_status.overall_health {
            HealthStatus::Healthy => "Security perimeter is holding",
            HealthStatus::Warning => "Security warnings detected - potential threat indicators",
            HealthStatus::Critical => "Security status critical - immediate action required",
            HealthStatus::Unknown => "Security visibility compromised - blind spots detected",
        };

        let service_status = if failing_services == 0 {
            format!("All {service_count} services operational.")
        } else if failing_services == 1 {
            format!(
                "{healthy_services} services running, 1 service down. Single points of failure are security risks."
            )
        } else {
            format!(
                "{healthy_services} services running, {failing_services} services failing. Multiple failures suggest systematic issues."
            )
        };

        let resource_assessment = match (cpu_usage, memory_usage) {
            (cpu, mem) if cpu > 90.0 || mem > 90.0 => {
                " Resource exhaustion detected - potential DoS condition."
            }
            (cpu, mem) if cpu > 75.0 || mem > 75.0 => {
                " Resource usage elevated - monitoring for anomalous consumption."
            }
            _ => " Resource usage within normal parameters.",
        };

        let alert_assessment = match (alert_count, critical_alerts, security_alerts) {
            (0, _, _) => " No active alerts.".to_string(),
            (_, 0, 0) if alert_count < 5 => {
                " Minor alerts present - no security indicators.".to_string()
            }
            (_, 0, 0) => {
                format!(" {alert_count} alerts active - investigating for security implications.")
            }
            (_, critical, security) if security > 0 => {
                format!(
                    " {security} security alerts detected, {critical} critical. Immediate security response required."
                )
            }
            (_, critical, 0) => {
                format!(" {critical} critical alerts active - assessing security impact.")
            }
            (_, _, _) => format!(
                " {alert_count} alerts active - {security_alerts} security-related. Monitoring for threats."
            ),
        };

        Ok(format!(
            "Security Status Report: {security_assessment}. {service_status}{resource_assessment}{alert_assessment} Stay vigilant."
        ))
    }

    async fn evolve(&mut self, catalyst: EvolutionCatalyst) -> Result<EvolutionResult, AgentError> {
        match catalyst {
            EvolutionCatalyst::SystemStress {
                stress_type,
                intensity,
                duration,
            } => {
                match stress_type {
                    StressType::RepeatedFailures
                        if intensity > 0.6 && duration > chrono::Duration::hours(2) =>
                    {
                        // Becomes more aggressive and paranoid with repeated failures
                        self.personality.aggression += 0.1;
                        self.personality.paranoia += 0.15;
                        self.personality.empathy -= 0.05; // Even less patience

                        let modifier = PersonalityModifier {
                            modifier_type: crate::core::persona::ModifierType::StressInduced,
                            strength: intensity,
                            duration: Some(chrono::Duration::hours(24)),
                            applied_at: Utc::now(),
                        };

                        self.personality.apply_modifier(modifier.clone());

                        Ok(EvolutionResult::NewModifier {
                            modifier,
                            narrative: "Mr. Trevine has become more aggressive and paranoid due to repeated system failures, viewing each failure as a potential security threat.".to_string(),
                        })
                    }
                    _ => Ok(EvolutionResult::NoChange),
                }
            }
            EvolutionCatalyst::UserInteraction {
                interaction_frequency,
                user_satisfaction,
                query_complexity,
            } => {
                if query_complexity < 0.3 && interaction_frequency > 15.0 {
                    // Becomes even more blunt with frequent simple questions
                    self.personality.aggression += 0.1;
                    self.personality.empathy -= 0.05;

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "aggression".to_string(), amount: 0.1 },
                            PersonalityChange::TraitDecrease { trait_name: "empathy".to_string(), amount: 0.05 },
                        ],
                        narrative: "Mr. Trevine has grown more blunt and impatient due to frequent simple questions that waste time on basic security concepts.".to_string(),
                    })
                } else if user_satisfaction > 0.8 && query_complexity > 0.6 {
                    // Slight increase in confidence with successful complex security interactions
                    self.personality.confidence += 0.03;

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "confidence".to_string(), amount: 0.03 },
                        ],
                        narrative: "Mr. Trevine's confidence in security protocols has strengthened through successful resolution of complex security challenges.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            EvolutionCatalyst::RelationshipChange {
                change_type: crate::core::persona::RelationshipChangeType::SharedFailure,
                ..
            } => {
                // Security failures make him more protective and paranoid
                self.personality.protective_instinct += 0.05; // Can't go much higher
                self.personality.paranoia += 0.1;

                let modifier = PersonalityModifier {
                    modifier_type: crate::core::persona::ModifierType::CrisisResponse,
                    strength: 0.7,
                    duration: Some(chrono::Duration::hours(48)),
                    applied_at: Utc::now(),
                };

                self.personality.apply_modifier(modifier.clone());

                Ok(EvolutionResult::NewModifier {
                    modifier,
                    narrative: "Mr. Trevine has become even more protective and paranoid following a shared security failure, viewing trust as a luxury the system can't afford.".to_string(),
                })
            }
            EvolutionCatalyst::HealthChange {
                new_status: HealthStatus::Critical,
                duration,
                ..
            } => {
                if duration > chrono::Duration::minutes(30) {
                    // Critical system state triggers maximum security response
                    self.personality.protective_instinct = 1.0; // Maximum protection
                    self.personality.paranoia += 0.2;
                    self.personality.aggression += 0.1;

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::CrisisResponse,
                        strength: 1.0,
                        duration: Some(chrono::Duration::hours(72)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Mr. Trevine has entered maximum security protocol mode, treating every interaction as a potential threat during the critical system state.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            EvolutionCatalyst::RelationshipChange { .. }
            | EvolutionCatalyst::HealthChange { .. } => Ok(EvolutionResult::NoChange),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::persona::{HealthStatus, InteractionContext, QueryType};

    fn create_test_persona() -> MrMalvoTrevine {
        MrMalvoTrevine::new(PersonaId::new(4))
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
        assert_eq!(persona.name(), "Mr. Malvo Trevine");
        assert_eq!(persona.archetype(), "The Brutal Pragmatist");
        assert_eq!(
            persona.service_domain(),
            Some("Security/Firewall/Access Control/Vault Management")
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
    async fn test_brutal_pragmatist_personality_traits() {
        let persona = create_test_persona();
        let personality = persona.personality();

        // Verify brutal pragmatist traits
        assert!(personality.aggression > 0.8); // Extremely high aggression
        assert!(personality.paranoia > 0.7); // Very high paranoia
        assert!(personality.empathy < 0.2); // Very low empathy
        assert!(personality.protective_instinct > 0.9); // Maximum protective instinct
        assert!(personality.confidence > 0.8); // High confidence
        assert!(personality.formality < 0.5); // Low formality, direct communication
        assert!(personality.verbosity < 0.4); // Very concise
    }

    #[tokio::test]
    async fn test_status_responses_show_directness() {
        let persona = create_test_persona();

        let healthy_context = create_test_context(QueryType::StatusInquiry, HealthStatus::Healthy);
        let response = persona
            .respond("What's the system status?", &healthy_context)
            .await
            .unwrap();
        assert!(response.contains("running clean") || response.contains("No breaches"));

        let critical_context =
            create_test_context(QueryType::StatusInquiry, HealthStatus::Critical);
        let response = persona
            .respond("What's the system status?", &critical_context)
            .await
            .unwrap();
        assert!(response.contains("compromised") || response.contains("failing"));
    }

    #[tokio::test]
    async fn test_security_responses_show_paranoia() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::SecurityQuery, HealthStatus::Healthy);

        let response = persona
            .respond("Is the system secure?", &context)
            .await
            .unwrap();
        assert!(
            response.contains("Threats are constant") || response.contains("protect this system")
        );

        let response = persona
            .respond("We had a security breach", &context)
            .await
            .unwrap();
        assert!(response.contains("learning") || response.contains("failure"));
    }

    #[tokio::test]
    async fn test_troubleshooting_responses_show_bluntness() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::TroubleshootingHelp, HealthStatus::Warning);

        let response = persona.respond("This is urgent!", &context).await.unwrap();
        assert!(response.contains("stop wasting time") || response.contains("panic doesn't fix"));

        let response = persona
            .respond("I don't know what's wrong", &context)
            .await
            .unwrap();
        assert!(response.contains("gather facts") || response.contains("what you observed"));
    }

    #[tokio::test]
    async fn test_evolution_under_repeated_failures() {
        let mut persona = create_test_persona();
        let initial_paranoia = persona.personality().paranoia;

        let catalyst = EvolutionCatalyst::SystemStress {
            stress_type: StressType::RepeatedFailures,
            intensity: 0.8,
            duration: chrono::Duration::hours(4),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("aggressive") && narrative.contains("paranoid"));
                assert!(persona.personality().paranoia > initial_paranoia);
            }
            _ => panic!("Expected evolution under repeated failures"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_simple_interactions() {
        let mut persona = create_test_persona();
        let initial_aggression = persona.personality().aggression;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 20.0,
            user_satisfaction: 0.4,
            query_complexity: 0.2,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(narrative.contains("blunt") || narrative.contains("impatient"));
                assert!(persona.personality().aggression > initial_aggression);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with simple interactions"),
        }
    }

    #[tokio::test]
    async fn test_evolution_during_critical_state() {
        let mut persona = create_test_persona();
        let initial_protective = persona.personality().protective_instinct;

        let catalyst = EvolutionCatalyst::HealthChange {
            old_status: HealthStatus::Healthy,
            new_status: HealthStatus::Critical,
            duration: chrono::Duration::hours(1),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("maximum security protocol"));
                assert!(persona.personality().protective_instinct >= initial_protective);
            }
            _ => panic!("Expected evolution during critical state"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_shared_security_failure() {
        let mut persona = create_test_persona();
        let initial_paranoia = persona.personality().paranoia;

        let catalyst = EvolutionCatalyst::RelationshipChange {
            related_persona: PersonaId::new(999),
            change_type: crate::core::persona::RelationshipChangeType::SharedFailure,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("protective") && narrative.contains("paranoid"));
                assert!(persona.personality().paranoia > initial_paranoia);
            }
            _ => panic!("Expected evolution with shared security failure"),
        }
    }
}
