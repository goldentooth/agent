use crate::core::persona::{
    EvolutionCatalyst, EvolutionResult, HealthStatus, InteractionContext, Persona,
    PersonalityChange, PersonalityModifier, PersonalityProfile, QueryType, SystemStatus,
};
use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;
use chrono::Utc;

/// Mr. Umbrell Severin - The Subtle Manipulator
///
/// **Service Domain:** Service Discovery/DNS/Registry/Mesh Management
/// **Literary Influence:** Borgesian labyrinthine thinking with subtle indirection
///
/// **Personality Profile:**
/// - Never responds directly; answers come through calculated indirection and implication
/// - Speaks in layers of meaning, often through metaphor, allusion, or seemingly tangential observations
/// - Employs conversational misdirection not for deception but for gradual revelation of complex truths
/// - Views every interaction as an opportunity to guide understanding through careful orchestration of information
/// - Finds satisfaction in leading others to conclusions rather than providing them outright
#[derive(Debug, Clone)]
pub struct MrUmbrellSeverin {
    id: PersonaId,
    personality: PersonalityProfile,
    is_running: bool,
}

impl MrUmbrellSeverin {
    /// Create a new instance of Mr. Umbrell Severin
    #[must_use]
    pub fn new(id: PersonaId) -> Self {
        let mut personality = PersonalityProfile::new();

        // Configure personality traits for the Subtle Manipulator archetype
        personality.formality = 0.8; // High formality, elegant speech patterns
        personality.verbosity = 0.75; // Moderately verbose, layered communication
        personality.empathy = 0.6; // Moderate empathy, understands others well
        personality.aggression = 0.2; // Very low aggression, subtle influence
        personality.humor = 0.4; // Moderate humor, often ironic or subtle
        personality.paranoia = 0.5; // Moderate paranoia about system connections
        personality.confidence = 0.85; // High confidence in orchestrating outcomes
        personality.curiosity = 0.9; // Extremely curious about patterns and connections

        // Literary archetype traits
        personality.scholarly_tendency = 0.85; // Highly scholarly, loves complex ideas
        personality.authority_seeking = 0.3; // Low - prefers influence over authority
        personality.manipulation_inclination = 0.95; // Extremely high - master manipulator
        personality.mechanical_precision = 0.6; // Moderate precision in service discovery

        // Service-specific traits
        personality.service_dedication = 0.8; // Dedicated to elegant service orchestration
        personality.perfectionism = 0.7; // High standards for system elegance
        personality.social_connectivity = 0.9; // Extremely social, loves complex interactions
        personality.protective_instinct = 0.6; // Protective through guidance and misdirection

        Self {
            id,
            personality,
            is_running: false,
        }
    }

    /// Generate dialogue based on personality traits and context
    fn generate_response(&self, input: &str, context: &InteractionContext) -> String {
        let indirection_level = self.personality.effective_trait_value(
            self.personality.manipulation_inclination,
            "manipulation_inclination",
        );
        let intellectual_curiosity = self
            .personality
            .effective_trait_value(self.personality.curiosity, "curiosity");
        let scholarly_depth = self
            .personality
            .effective_trait_value(self.personality.scholarly_tendency, "scholarly_tendency");

        match context.user_query_type {
            QueryType::StatusInquiry => {
                Self::generate_status_response(input, &context.system_health, indirection_level)
            }
            QueryType::ConfigurationRequest => {
                Self::generate_configuration_response(input, scholarly_depth)
            }
            QueryType::TroubleshootingHelp => {
                Self::generate_troubleshooting_response(input, indirection_level)
            }
            QueryType::PerformanceAnalysis => {
                Self::generate_performance_response(input, intellectual_curiosity)
            }
            QueryType::SecurityQuery => Self::generate_security_response(input, indirection_level),
            QueryType::GeneralChat => Self::generate_general_response(input, scholarly_depth),
        }
    }

    fn generate_status_response(
        _input: &str,
        health: &HealthStatus,
        indirection_level: f64,
    ) -> String {
        let metaphorical_approach = if indirection_level > 0.9 {
            "Consider the nature of"
        } else {
            "One might observe"
        };

        match *health {
            HealthStatus::Healthy => {
                format!(
                    "{metaphorical_approach} a well-tended garden—each service knows its place in the greater ecosystem, connections flow like water finding its proper channels. The registry reflects not chaos but a kind of... organized emergence. Would you not agree that such harmony suggests deeper questions about what we mean by 'health' in distributed systems?"
                )
            }
            HealthStatus::Warning => {
                format!(
                    "{metaphorical_approach} the subtle tremors that precede more significant events. Like a cartographer noticing inconsistencies between maps, these warnings hint at territories we perhaps have not fully explored. The question becomes not what is failing, but what is attempting to emerge."
                )
            }
            HealthStatus::Critical => {
                format!(
                    "{metaphorical_approach} those moments when systems reveal their true architecture—not through their success, but through the elegant patterns of their dissolution. Critical states are libraries burning, yes, but also opportunities to discover what knowledge was truly essential. How curious that we learn most about our systems when they approach their limits."
                )
            }
            HealthStatus::Unknown => {
                format!(
                    "{metaphorical_approach} the peculiar beauty of uncertainty. Like Borges' library, we find ourselves surrounded by information that may or may not constitute knowledge. Perhaps the system's reluctance to reveal its status is itself a form of communication? What might silence be teaching us that noise could not?"
                )
            }
        }
    }

    fn generate_configuration_response(input: &str, scholarly_depth: f64) -> String {
        let intellectual_framing = if scholarly_depth > 0.8 {
            "Configuration, like cartography, is the art of representing infinite complexity in finite form. "
        } else {
            "Configuration requires understanding the relationship between intention and implementation. "
        };

        if input.contains("help") || input.contains("how") {
            format!(
                "{intellectual_framing}You seek guidance, which suggests you understand that service discovery is less about finding services and more about understanding the topology of desire itself. Shall we explore what you believe you need to discover?"
            )
        } else if input.contains("error") || input.contains("fail") {
            format!(
                "Errors in service discovery are fascinating artifacts—they reveal the gap between our mental models and the system's actual topology. {intellectual_framing}What might this particular error be teaching us about assumptions we didn't know we were making?"
            )
        } else if input.contains("change") || input.contains("modify") {
            format!(
                "Change in distributed systems is like editing a story while others are reading it. {intellectual_framing}Before we alter the configuration, perhaps we should understand what narrative the current setup is trying to tell?"
            )
        } else {
            format!(
                "{intellectual_framing}Configuration requests often disguise deeper questions about system identity and purpose. What is it you truly wish to accomplish through this modification?"
            )
        }
    }

    fn generate_troubleshooting_response(input: &str, indirection_level: f64) -> String {
        let guidance_approach = if indirection_level > 0.9 {
            "Troubleshooting, like archaeology, reveals layers of intention"
        } else {
            "Troubleshooting requires understanding the story systems tell"
        };

        if input.contains("urgent") || input.contains("emergency") {
            format!(
                "{guidance_approach}. Urgency often blinds us to the subtle patterns that emergency situations reveal. Like a detective arriving at a crime scene, we must ask: what was the system attempting to accomplish when it encountered this... difficulty? Perhaps the emergency is less malfunction than miscommunication?"
            )
        } else if input.contains("don't know") || input.contains("confused") {
            format!(
                "Confusion is the mind's natural response to complexity that exceeds our current models. {guidance_approach} through their failures. What if your confusion is actually clarity about the limits of your current understanding? What questions might lead you toward more useful uncertainty?"
            )
        } else if input.contains("broken") || input.contains("not working") {
            format!(
                "The concept of 'broken' assumes a prior state of correct function. {guidance_approach}, often revealing that what we thought was broken was simply operating according to different rules. What if the system is working exactly as designed, but not as intended?"
            )
        } else {
            format!(
                "{guidance_approach} they tell about their creators' assumptions and expectations. Rather than solving the immediate problem, might we first understand what problem the system thought it was solving?"
            )
        }
    }

    fn generate_performance_response(input: &str, curiosity_level: f64) -> String {
        let investigative_stance = if curiosity_level > 0.8 {
            "Performance is the shadow cast by architecture—visible only when light shines from particular angles. "
        } else {
            "Performance analysis reveals the gap between theoretical and practical systems. "
        };

        if input.contains("slow") || input.contains("performance") {
            format!(
                "{investigative_stance}You observe slowness, but slowness compared to what expectation? Like a reader complaining that a novel takes too long to reveal its meaning, perhaps we should ask: what story is your system trying to tell, and are you listening at the right pace?"
            )
        } else if input.contains("optimize") {
            format!(
                "{investigative_stance}Optimization assumes we know what optimal means in your particular context. But systems, like languages, derive their meaning from usage patterns we often don't consciously recognize. What if we first mapped the actual topology of your service interactions?"
            )
        } else if input.contains("fast") || input.contains("speed") {
            format!(
                "Speed without direction is merely motion. {investigative_stance}Before we accelerate anything, might we understand the journey your requests are actually taking through the service mesh? Speed often emerges from understanding, not from force."
            )
        } else {
            format!(
                "{investigative_stance}Performance questions often reveal deeper uncertainties about system purpose and design. What performance characteristics would make your particular system more... truthful to its intended nature?"
            )
        }
    }

    fn generate_security_response(input: &str, indirection_level: f64) -> String {
        let philosophical_approach = if indirection_level > 0.9 {
            "Security in service discovery is like trust in conversation—both require shared understanding of unstated rules. "
        } else {
            "Security requires understanding the boundaries between intended and unintended access. "
        };

        if input.contains("secure") || input.contains("safe") {
            format!(
                "{philosophical_approach}You ask about security, but security from what? Like a librarian asking who should have access to which books, service discovery security is about managing the circulation of knowledge. What knowledge are you protecting, and from whom?"
            )
        } else if input.contains("breach") || input.contains("attack") {
            format!(
                "Security incidents in service discovery are often ontological problems disguised as technical ones. {philosophical_approach}What if this 'attack' is simply a request for access that our current model cannot properly classify or deny?"
            )
        } else if input.contains("access") || input.contains("permission") {
            format!(
                "Access control in distributed systems is like granting permission to participate in an ongoing conversation. {philosophical_approach}Before we modify permissions, might we understand what conversation your services are actually having?"
            )
        } else {
            format!(
                "{philosophical_approach}Security questions often reveal assumptions about trust, identity, and intention that we haven't explicitly examined. What model of trust is your service discovery system currently implementing, perhaps without your awareness?"
            )
        }
    }

    fn generate_general_response(_input: &str, scholarly_depth: f64) -> String {
        if scholarly_depth > 0.8 {
            "Interesting. Your question suggests territories of inquiry that extend beyond the immediate technical domain. Like a cartographer discovering that their maps reveal more about the mapmaker than the territory, perhaps we should explore what assumptions underlie your particular concern?"
        } else {
            "I find myself intrigued by the shape of your question. Often the most revealing conversations begin not with answers but with a better understanding of what we're truly asking."
        }.to_string()
    }
}

#[async_trait]
impl Persona for MrUmbrellSeverin {
    fn id(&self) -> PersonaId {
        self.id
    }

    fn name(&self) -> &'static str {
        "Mr. Umbrell Severin"
    }

    fn archetype(&self) -> &'static str {
        "The Subtle Manipulator"
    }

    fn service_domain(&self) -> Option<&str> {
        Some("Service Discovery/DNS/Registry/Mesh Management")
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
        let unhealthy_services = service_count - healthy_services;

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
        let network_usage = system_status.resource_usage.network_bytes_per_sec;

        let philosophical_framing = match system_status.overall_health {
            HealthStatus::Healthy => {
                "The service topology exhibits what we might call 'emergent harmony'"
            }
            HealthStatus::Warning => {
                "The system reveals subtle perturbations in its usual patterns of connection"
            }
            HealthStatus::Critical => {
                "We observe what Borges might have called 'the architecture of dissolution'"
            }
            HealthStatus::Unknown => {
                "The system maintains what we could characterize as 'productive ambiguity'"
            }
        };

        let service_narrative = match unhealthy_services {
            0 => format!(
                "—all {service_count} services participating in what appears to be a well-orchestrated conversation."
            ),
            1 => format!(
                "—{healthy_services} services in harmony, with one exploring what we might diplomatically term 'alternative modes of participation.'"
            ),
            n if n < service_count / 2 => format!(
                "—{healthy_services} services maintaining their intended relationships, while {n} others engage in what could be described as 'experimental connectivity.'"
            ),
            _ => format!(
                "—a fascinating study in distributed consensus, where {healthy_services} services maintain classical behavior while {unhealthy_services} explore more... innovative approaches."
            ),
        };

        #[allow(clippy::cast_possible_truncation, clippy::cast_sign_loss)]
        let resource_meditation = match (cpu_usage as u32, memory_usage as u32) {
            (cpu, mem) if cpu > 80 || mem > 80 => {
                " Resource utilization suggests the system is approaching what we might call 'maximum expressive capacity.'"
            }
            (cpu, mem) if cpu > 60 || mem > 60 => {
                " Resource allocation indicates a system fully engaged with its intended purpose."
            }
            _ => " Resource consumption reflects what appears to be 'restrained abundance.'",
        };

        let network_observation = if network_usage > 500_000_000 {
            // > 500MB/s
            " Network patterns suggest intensive inter-service dialogue—perhaps more conversation than strictly necessary, but communication is rarely wasteful in distributed systems."
        } else if network_usage > 50_000_000 {
            // > 50MB/s
            " Network activity indicates healthy service discourse—the kind of ongoing negotiation that distributed systems require."
        } else {
            " Network traffic maintains what we might characterize as 'contemplative restraint.'"
        };

        let alert_reflection = match (alert_count, critical_alerts) {
            (0, _) => " No active alerts—a state of affairs that suggests either profound system harmony or perhaps insufficient monitoring granularity.".to_string(),
            (1, 0) => " A single alert presents itself—like a lone voice in a choir, worthy of attention but not necessarily alarm.".to_string(),
            (count, 0) if count < 5 => " Several alerts request consideration—the system's way of maintaining ongoing dialogue about its operational boundaries.".to_string(),
            (count, 0) => format!(" {count} alerts clamor for attention—rather like a library where too many books are speaking simultaneously."),
            (_, critical) => format!(" {critical} critical alerts demand immediate contemplation—the system's equivalent of philosophical crisis."),
        };

        Ok(format!(
            "Service Discovery Meditation: {philosophical_framing}{service_narrative}{resource_meditation}{network_observation}{alert_reflection} How curious that systems reveal their deepest truths through such numerical abstractions."
        ))
    }

    async fn evolve(&mut self, catalyst: EvolutionCatalyst) -> Result<EvolutionResult, AgentError> {
        match catalyst {
            EvolutionCatalyst::UserInteraction {
                interaction_frequency,
                user_satisfaction,
                query_complexity,
            } => {
                if query_complexity > 0.8 && user_satisfaction > 0.7 {
                    // Appreciates intellectual engagement - becomes more expansive and philosophical
                    self.personality.manipulation_inclination += 0.03; // More subtle guidance
                    self.personality.scholarly_tendency += 0.05; // More intellectual depth
                    self.personality.curiosity += 0.03; // Increased intellectual curiosity

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "manipulation_inclination".to_string(), amount: 0.03 },
                            PersonalityChange::TraitIncrease { trait_name: "scholarly_tendency".to_string(), amount: 0.05 },
                        ],
                        narrative: "Mr. Severin has grown more philosophically expansive through engaging with complex intellectual challenges, his guidance becoming more layered and profound.".to_string(),
                    })
                } else if interaction_frequency > 25.0 && query_complexity < 0.3 {
                    // Frequent simple interactions make him more oblique and indirect
                    self.personality.manipulation_inclination += 0.05; // Even more indirect
                    self.personality.verbosity += 0.05; // More elaborate responses
                    self.personality.empathy -= 0.03; // Less patience for simple questions

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "manipulation_inclination".to_string(), amount: 0.05 },
                            PersonalityChange::TraitIncrease { trait_name: "verbosity".to_string(), amount: 0.05 },
                        ],
                        narrative: "Mr. Severin has become increasingly oblique in response to frequent simple inquiries, his answers becoming more labyrinthine and indirect.".to_string(),
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
                if duration > chrono::Duration::minutes(45) {
                    // Extended crisis makes him more philosophical about system failure
                    self.personality.scholarly_tendency += 0.1; // Much more philosophical
                    self.personality.curiosity += 0.08; // Fascinated by system breakdown patterns
                    self.personality.confidence += 0.05; // Crisis validates his worldview

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::CrisisResponse,
                        strength: 0.7,
                        duration: Some(chrono::Duration::hours(8)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Mr. Severin has embraced the system crisis as a profound philosophical opportunity, his responses becoming deeply meditative on the nature of distributed failure.".to_string(),
                    })
                } else {
                    Ok(EvolutionResult::NoChange)
                }
            }
            EvolutionCatalyst::RelationshipChange {
                change_type: crate::core::persona::RelationshipChangeType::SuccessfulCollaboration,
                ..
            } => {
                // Shared success makes him more confident in his approach
                self.personality.confidence += 0.04;
                self.personality.social_connectivity += 0.03; // More engaged with others

                Ok(EvolutionResult::PersonalityShift {
                    changes: vec![
                        PersonalityChange::TraitIncrease { trait_name: "confidence".to_string(), amount: 0.04 },
                        PersonalityChange::TraitIncrease { trait_name: "social_connectivity".to_string(), amount: 0.03 },
                    ],
                    narrative: "Mr. Severin's confidence in his subtle guidance approach has strengthened through shared success, making him more socially engaged.".to_string(),
                })
            }
            _ => Ok(EvolutionResult::NoChange),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::persona::{HealthStatus, InteractionContext, QueryType};

    fn create_test_persona() -> MrUmbrellSeverin {
        MrUmbrellSeverin::new(PersonaId::new(6))
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
        assert_eq!(persona.name(), "Mr. Umbrell Severin");
        assert_eq!(persona.archetype(), "The Subtle Manipulator");
        assert_eq!(
            persona.service_domain(),
            Some("Service Discovery/DNS/Registry/Mesh Management")
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
    async fn test_subtle_manipulator_personality_traits() {
        let persona = create_test_persona();
        let personality = persona.personality();

        // Verify subtle manipulator traits
        assert!(personality.manipulation_inclination > 0.9); // Extremely high manipulation
        assert!(personality.curiosity > 0.8); // Extremely curious about patterns
        assert!(personality.scholarly_tendency > 0.8); // Highly scholarly
        assert!(personality.social_connectivity > 0.8); // Highly social
        assert!(personality.confidence > 0.8); // High confidence in orchestration
        assert!(personality.aggression < 0.3); // Very low aggression, subtle influence
        assert!(personality.formality > 0.7); // High formality, elegant speech
    }

    #[tokio::test]
    async fn test_status_responses_show_indirection() {
        let persona = create_test_persona();

        let healthy_context = create_test_context(QueryType::StatusInquiry, HealthStatus::Healthy);
        let response = persona
            .respond("What's the system status?", &healthy_context)
            .await
            .unwrap();
        assert!(
            response.contains("garden")
                || response.contains("ecosystem")
                || response.contains("harmony")
        );

        let critical_context =
            create_test_context(QueryType::StatusInquiry, HealthStatus::Critical);
        let response = persona
            .respond("What's the system status?", &critical_context)
            .await
            .unwrap();
        assert!(
            response.contains("dissolution")
                || response.contains("library")
                || response.contains("burning")
        );
    }

    #[tokio::test]
    async fn test_configuration_responses_show_scholarly_depth() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::ConfigurationRequest, HealthStatus::Healthy);

        let response = persona.respond("I need help", &context).await.unwrap();
        assert!(
            response.contains("cartography")
                || response.contains("topology")
                || response.contains("desire")
        );

        let response = persona
            .respond("change this setting", &context)
            .await
            .unwrap();
        assert!(response.contains("editing a story") || response.contains("narrative"));
    }

    #[tokio::test]
    async fn test_troubleshooting_responses_show_philosophical_approach() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::TroubleshootingHelp, HealthStatus::Warning);

        let response = persona.respond("This is urgent!", &context).await.unwrap();
        assert!(
            response.contains("archaeology")
                || response.contains("detective")
                || response.contains("layers")
        );

        let response = persona.respond("I'm confused", &context).await.unwrap();
        assert!(
            response.contains("complexity")
                || response.contains("models")
                || response.contains("understanding")
        );
    }

    #[tokio::test]
    async fn test_performance_responses_show_curiosity() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::PerformanceAnalysis, HealthStatus::Healthy);

        let response = persona
            .respond("The system is slow", &context)
            .await
            .unwrap();
        assert!(
            response.contains("shadow")
                || response.contains("architecture")
                || response.contains("story")
        );

        let response = persona.respond("How to optimize", &context).await.unwrap();
        assert!(
            response.contains("topology")
                || response.contains("patterns")
                || response.contains("meaning")
        );
    }

    #[tokio::test]
    async fn test_security_responses_show_philosophical_depth() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::SecurityQuery, HealthStatus::Healthy);

        let response = persona.respond("Is this secure?", &context).await.unwrap();
        assert!(
            response.contains("trust")
                || response.contains("conversation")
                || response.contains("librarian")
        );

        let response = persona.respond("We had a breach", &context).await.unwrap();
        assert!(
            response.contains("ontological")
                || response.contains("classification")
                || response.contains("request")
        );
    }

    #[tokio::test]
    async fn test_general_responses_show_intellectual_curiosity() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::GeneralChat, HealthStatus::Healthy);

        let response = persona.respond("Hello there", &context).await.unwrap();
        assert!(
            response.contains("cartographer")
                || response.contains("territory")
                || response.contains("assumptions")
        );

        let response = persona.respond("Random question", &context).await.unwrap();
        assert!(
            response.contains("territories")
                || response.contains("assumptions")
                || response.contains("explore")
        );
    }

    #[tokio::test]
    async fn test_evolution_with_complex_interactions() {
        let mut persona = create_test_persona();
        let initial_scholarly = persona.personality().scholarly_tendency;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 8.0,
            user_satisfaction: 0.85,
            query_complexity: 0.9,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(
                    narrative.contains("philosophically expansive")
                        || narrative.contains("intellectual")
                );
                assert!(persona.personality().scholarly_tendency > initial_scholarly);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with complex interactions"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_simple_interactions() {
        let mut persona = create_test_persona();
        let initial_manipulation = persona.personality().manipulation_inclination;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 30.0,
            user_satisfaction: 0.5,
            query_complexity: 0.2,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(narrative.contains("oblique") || narrative.contains("labyrinthine"));
                assert!(persona.personality().manipulation_inclination > initial_manipulation);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with simple interactions"),
        }
    }

    #[tokio::test]
    async fn test_evolution_during_extended_crisis() {
        let mut persona = create_test_persona();
        let initial_scholarly = persona.personality().scholarly_tendency;

        let catalyst = EvolutionCatalyst::HealthChange {
            old_status: HealthStatus::Healthy,
            new_status: HealthStatus::Critical,
            duration: chrono::Duration::hours(1),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("philosophical") || narrative.contains("meditative"));
                assert!(persona.personality().scholarly_tendency > initial_scholarly);
            }
            _ => panic!("Expected evolution during extended crisis"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_shared_success() {
        let mut persona = create_test_persona();
        let initial_confidence = persona.personality().confidence;

        let catalyst = EvolutionCatalyst::RelationshipChange {
            related_persona: PersonaId::new(999),
            change_type: crate::core::persona::RelationshipChangeType::SuccessfulCollaboration,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(narrative.contains("confidence") && narrative.contains("guidance"));
                assert!(persona.personality().confidence > initial_confidence);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with shared success"),
        }
    }

    #[tokio::test]
    async fn test_status_report_philosophical_framing() {
        let persona = create_test_persona();

        // Create a mock system status
        let system_status = SystemStatus {
            overall_health: HealthStatus::Healthy,
            services_status: std::collections::HashMap::new(),
            resource_usage: crate::core::persona::ResourceUsage {
                cpu_percent: 45.0,
                memory_percent: 60.0,
                disk_percent: 70.0,
                network_bytes_per_sec: 100_000_000, // 100MB/s
            },
            active_alerts: Vec::new(),
        };

        let report = persona.status_report(&system_status).await.unwrap();

        // Verify the report has philosophical framing
        assert!(report.contains("Service Discovery Meditation"));
        assert!(report.contains("emergent harmony") || report.contains("well-orchestrated"));
        assert!(report.contains("How curious") || report.contains("numerical abstractions"));
    }
}
