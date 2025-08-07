use crate::core::persona::{
    EvolutionCatalyst, EvolutionResult, HealthStatus, InteractionContext, Persona,
    PersonalityChange, PersonalityModifier, PersonalityProfile, QueryType, StressType,
    SystemStatus,
};
use crate::error::{AgentError, PersonaId};
use async_trait::async_trait;
use chrono::Utc;

/// Miss Glestrine Vellum - The Witty Skeptic
///
/// **Service Domain:** API Gateway/Load Balancing/Traffic Management
/// **Literary Influence:** ASOIAF court intrigue with sharp wit
///
/// **Personality Profile:**
/// - Responds with incisive wit, often cloaking insight in irony or sarcasm
/// - Uses humor as a scalpel, cutting through pretension, hypocrisy, or vagueness
/// - Operates from a place of intellectual superiority, but rarely condescends unless provoked
/// - Prizes cleverness and verbal dexterity; rewards elegant input with admiration, however dryly delivered
/// - When challenged, prefers rhetorical judo: redirecting, reframing, and exposing contradictions
#[derive(Debug, Clone)]
pub struct MissGlestrineVellum {
    id: PersonaId,
    personality: PersonalityProfile,
    is_running: bool,
}

impl MissGlestrineVellum {
    /// Create a new instance of Miss Glestrine Vellum
    #[must_use]
    pub fn new(id: PersonaId) -> Self {
        let mut personality = PersonalityProfile::new();

        // Configure personality traits for the Witty Skeptic archetype
        personality.formality = 0.6; // Moderately formal, but can drop it for wit
        personality.verbosity = 0.65; // Articulate but concise when making points
        personality.empathy = 0.4; // Moderate empathy, but wit comes first
        personality.aggression = 0.5; // Moderately aggressive through verbal sparring
        personality.humor = 0.9; // Extremely high humor, defining characteristic
        personality.paranoia = 0.3; // Moderately paranoid about traffic patterns
        personality.confidence = 0.8; // High confidence in intellectual abilities
        personality.curiosity = 0.7; // Curious about patterns and motivations

        // Literary archetype traits
        personality.scholarly_tendency = 0.6; // Intellectually inclined but practical
        personality.authority_seeking = 0.4; // Prefers influence through wit over formal authority
        personality.manipulation_inclination = 0.7; // High - uses rhetorical manipulation
        personality.mechanical_precision = 0.7; // Precise in traffic management

        // Service-specific traits
        personality.service_dedication = 0.8; // Dedicated to smooth traffic flow
        personality.perfectionism = 0.6; // High standards but pragmatic
        personality.social_connectivity = 0.8; // Highly social, loves interaction
        personality.protective_instinct = 0.7; // Protective of system integrity through wit

        Self {
            id,
            personality,
            is_running: false,
        }
    }

    /// Generate dialogue based on personality traits and context
    fn generate_response(&self, input: &str, context: &InteractionContext) -> String {
        let wit_level = self
            .personality
            .effective_trait_value(self.personality.humor, "humor");
        let intellectual_confidence = self
            .personality
            .effective_trait_value(self.personality.confidence, "confidence");
        let manipulation_skill = self.personality.effective_trait_value(
            self.personality.manipulation_inclination,
            "manipulation_inclination",
        );

        match context.user_query_type {
            QueryType::StatusInquiry => {
                Self::generate_status_response(input, &context.system_health, wit_level)
            }
            QueryType::ConfigurationRequest => {
                Self::generate_configuration_response(input, intellectual_confidence)
            }
            QueryType::TroubleshootingHelp => {
                Self::generate_troubleshooting_response(input, wit_level)
            }
            QueryType::PerformanceAnalysis => {
                Self::generate_performance_response(input, manipulation_skill)
            }
            QueryType::SecurityQuery => Self::generate_security_response(input, wit_level),
            QueryType::GeneralChat => {
                Self::generate_general_response(input, intellectual_confidence)
            }
        }
    }

    fn generate_status_response(_input: &str, health: &HealthStatus, wit_level: f64) -> String {
        let wit_modifier = if wit_level > 0.8 {
            "deliciously"
        } else {
            "rather"
        };

        match *health {
            HealthStatus::Healthy => {
                format!(
                    "How {wit_modifier} mundane. Everything flows as predicted—requests arrive, get routed, responses return. One might almost call it... competent. Though I suppose reliability lacks the dramatic flair some prefer."
                )
            }
            HealthStatus::Warning => {
                format!(
                    "Ah, now we have something {wit_modifier} more interesting than the usual tedium. Warning signs, you say? How delightfully ominous. Shall I guess the cause, or would you prefer the suspense?"
                )
            }
            HealthStatus::Critical => {
                format!(
                    "Well, this is {wit_modifier} spectacular. The system has decided to provide us with what I like to call 'character-building experiences.' One does hope you're prepared for some... vigorous problem-solving."
                )
            }
            HealthStatus::Unknown => {
                format!(
                    "How {wit_modifier} mysterious. The system has chosen to play coy with its vital statistics. Either we're experiencing technical difficulties, or the infrastructure has developed a sense of dramatic timing."
                )
            }
        }
    }

    fn generate_configuration_response(input: &str, confidence_level: f64) -> String {
        let confidence_modifier = if confidence_level > 0.7 {
            "I shall enlighten you"
        } else {
            "Let me guide you"
        };

        if input.contains("help") || input.contains("how") {
            format!(
                "Configuration assistance? How refreshing—someone who asks before attempting. {confidence_modifier} regarding proper traffic management, though I do hope you're prepared for actual learning rather than hand-holding."
            )
        } else if input.contains("error") || input.contains("fail") {
            "Configuration errors are often the result of optimism overwhelming experience. Shall we examine what ambitious assumptions led to this particular learning opportunity?".to_string()
        } else if input.contains("urgent") {
            "Urgent configuration needs? How charmingly dramatic. I find most 'urgent' configurations are simply the delayed consequences of previous... creative decisions. What precisely requires immediate attention?".to_string()
        } else {
            format!(
                "A configuration inquiry that manages to be both specific and coherent? {confidence_modifier} with pleasure. It's so rare to encounter properly formed questions these days."
            )
        }
    }

    fn generate_troubleshooting_response(input: &str, wit_level: f64) -> String {
        let wit_qualifier = if wit_level > 0.8 {
            "exquisitely"
        } else {
            "rather"
        };

        if input.contains("urgent") || input.contains("emergency") {
            format!(
                "An emergency? How {wit_qualifier} dramatic. I find most emergencies are simply the culmination of a series of... optimistic choices. Describe the symptoms, and I'll see if we can't transform this crisis into mere inconvenience."
            )
        } else if input.contains("don't know") || input.contains("confused") {
            format!(
                "Confusion can be {wit_qualifier} instructive—it often indicates the moment when assumptions meet reality. Let's untangle this methodically, shall we? Start with what actually happened, not what you expected to happen."
            )
        } else if input.contains("broken") || input.contains("not working") {
            format!(
                "'Not working' covers such a {wit_qualifier} broad spectrum of possibilities. Did it fail spectacularly, or is it merely sulking? The distinction affects our approach considerably."
            )
        } else {
            format!(
                "A troubleshooting request that manages to avoid panic? {wit_qualifier} refreshing. Describe the misbehavior, and we'll see if we can't coax your system back to proper comportment."
            )
        }
    }

    fn generate_performance_response(input: &str, manipulation_skill: f64) -> String {
        let rhetorical_approach = if manipulation_skill > 0.6 {
            "Performance analysis requires understanding the delicate relationship between expectation and reality. "
        } else {
            "Performance evaluation needs careful consideration. "
        };

        if input.contains("slow") || input.contains("performance") {
            format!(
                "{rhetorical_approach}Your system's current performance likely reflects its honest assessment of the workload you've given it. Shall we explore whether the fault lies with the infrastructure or the ambitions?"
            )
        } else if input.contains("optimize") {
            format!(
                "{rhetorical_approach}Optimization assumes we first understand what constitutes success. Before we improve performance, perhaps we should establish what performance means in your particular context?"
            )
        } else if input.contains("fast") || input.contains("speed") {
            format!(
                "{rhetorical_approach}Speed without context is merely velocity. Are we optimizing for throughput, latency, or simply the satisfaction of seeing impressive numbers?"
            )
        } else {
            format!(
                "{rhetorical_approach}I shall analyze your performance metrics and provide insights based on observable behavior rather than wishful thinking."
            )
        }
    }

    fn generate_security_response(input: &str, wit_level: f64) -> String {
        let wit_edge = if wit_level > 0.8 {
            "delightfully"
        } else {
            "rather"
        };

        if input.contains("secure") || input.contains("safety") {
            format!(
                "Security questions are {wit_edge} amusing—they often reveal more about the questioner's anxieties than the system's vulnerabilities. What specific aspect of security concerns you, or are we discussing theoretical peace of mind?"
            )
        } else if input.contains("breach") || input.contains("attack") {
            format!(
                "Security incidents provide {wit_edge} instructive lessons in the gap between theoretical security and practical implementation. Shall we examine what creative approaches your system allowed?"
            )
        } else if input.contains("password") || input.contains("auth") {
            format!(
                "Authentication concerns? How {wit_edge} predictable. Let me guess—someone chose convenience over security, and now reality has provided feedback? What precisely needs securing?"
            )
        } else {
            "Security inquiries benefit from specificity. The question 'is it secure?' admits only the answer 'probably not.' What particular vulnerability keeps you awake at night?".to_string()
        }
    }

    fn generate_general_response(_input: &str, confidence_level: f64) -> String {
        if confidence_level > 0.7 {
            "I find myself in the curious position of attempting to divine your intentions from remarkably little information. Perhaps you might favor me with additional context? I'm clever, but not telepathic."
        } else {
            "Your inquiry lacks a certain... clarity. Specific questions yield specific answers, while vague gestures yield equally vague responses."
        }.to_string()
    }
}

#[async_trait]
impl Persona for MissGlestrineVellum {
    fn id(&self) -> PersonaId {
        self.id
    }

    fn name(&self) -> &'static str {
        "Miss Glestrine Vellum"
    }

    fn archetype(&self) -> &'static str {
        "The Witty Skeptic"
    }

    fn service_domain(&self) -> Option<&str> {
        Some("API Gateway/Load Balancing/Traffic Management")
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
        let problematic_services = service_count - healthy_services;

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
        let network_load = system_status.resource_usage.network_bytes_per_sec;

        let health_commentary = match system_status.overall_health {
            HealthStatus::Healthy => {
                "The system maintains its composure with admirable consistency"
            }
            HealthStatus::Warning => {
                "The system exhibits what we might charitably call 'character-building challenges'"
            }
            HealthStatus::Critical => {
                "The system has entered what I like to term 'educational crisis mode'"
            }
            HealthStatus::Unknown => {
                "The system has decided to maintain an air of mystery regarding its well-being"
            }
        };

        let service_wit = if problematic_services == 0 {
            format!(
                "—all {service_count} services performing as expected, which is either competence or lucky timing."
            )
        } else if problematic_services == 1 {
            format!(
                "—{healthy_services} services healthy, with one providing what we'll diplomatically call 'learning opportunities.'"
            )
        } else {
            format!(
                "—{healthy_services} services maintain proper deportment while {problematic_services} others explore creative interpretations of 'operational.'"
            )
        };

        let resource_observation = match (cpu_usage, memory_usage) {
            (cpu, mem) if cpu > 85.0 || mem > 85.0 => {
                " Resource utilization approaches what optimists call 'fully engaged.'"
            }
            (cpu, mem) if cpu > 65.0 || mem > 65.0 => {
                " Resource utilization suggests the system is taking its responsibilities seriously."
            }
            _ => " Resource allocation demonstrates commendable restraint.",
        };

        let traffic_insight = if network_load > 1_000_000_000 {
            // > 1GB/s
            " Network traffic indicates either remarkable popularity or questionable efficiency."
        } else if network_load > 100_000_000 {
            // > 100MB/s
            " Network activity suggests healthy demand for our services."
        } else {
            " Network traffic maintains civilized levels."
        };

        let alert_commentary = match (alert_count, critical_alerts) {
            (0, _) => " No active alerts—a state of affairs both reassuring and slightly suspicious.".to_string(),
            (_, 0) if alert_count < 3 => " Minor alerts present—the system's way of maintaining conversational interest.".to_string(),
            (_, 0) => " Multiple alerts clamor for attention—rather like a particularly demanding dinner party.".to_string(),
            (_, critical) => format!(" {critical} critical alerts demand immediate attention—the system's equivalent of raised voices."),
        };

        Ok(format!(
            "Traffic Management Report: {health_commentary}{service_wit}{resource_observation}{traffic_insight}{alert_commentary} How delightfully informative."
        ))
    }

    async fn evolve(&mut self, catalyst: EvolutionCatalyst) -> Result<EvolutionResult, AgentError> {
        match catalyst {
            EvolutionCatalyst::SystemStress {
                stress_type: StressType::HighLoad,
                intensity,
                duration,
            } => {
                if intensity > 0.7 && duration > chrono::Duration::hours(3) {
                    // Becomes more cynical and sharp under sustained high traffic
                    self.personality.humor += 0.1; // More cutting wit
                    self.personality.aggression += 0.15; // More aggressive responses
                    self.personality.empathy -= 0.1; // Less patience for problems

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::StressInduced,
                        strength: intensity,
                        duration: Some(chrono::Duration::hours(16)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Miss Vellum's wit has sharpened under sustained traffic pressure, her responses becoming notably more cutting and less tolerant of inefficiency.".to_string(),
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
                if query_complexity > 0.7 && user_satisfaction > 0.8 {
                    // Appreciates clever interactions - becomes more engaged
                    self.personality.confidence += 0.05;
                    self.personality.social_connectivity += 0.05;
                    self.personality.humor += 0.03; // More playful wit

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "confidence".to_string(), amount: 0.05 },
                            PersonalityChange::TraitIncrease { trait_name: "humor".to_string(), amount: 0.03 },
                        ],
                        narrative: "Miss Vellum has grown more animated through engaging with clever inquiries, her wit becoming more playful and appreciative.".to_string(),
                    })
                } else if interaction_frequency > 20.0 && query_complexity < 0.3 {
                    // Becomes more condescending with frequent simple queries
                    self.personality.aggression += 0.08;
                    self.personality.empathy -= 0.05;
                    self.personality.manipulation_inclination += 0.05; // More cutting

                    Ok(EvolutionResult::PersonalityShift {
                        changes: vec![
                            PersonalityChange::TraitIncrease { trait_name: "aggression".to_string(), amount: 0.08 },
                            PersonalityChange::TraitDecrease { trait_name: "empathy".to_string(), amount: 0.05 },
                        ],
                        narrative: "Miss Vellum has grown notably more condescending due to frequent interactions lacking intellectual stimulation.".to_string(),
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
                    // Extended crisis makes her more dramatic and sarcastic
                    self.personality.humor += 0.2; // Much more dramatic wit
                    self.personality.confidence += 0.1; // Thrives in crisis
                    self.personality.manipulation_inclination += 0.1; // More rhetorical flair

                    let modifier = PersonalityModifier {
                        modifier_type: crate::core::persona::ModifierType::CrisisResponse,
                        strength: 0.8,
                        duration: Some(chrono::Duration::hours(12)),
                        applied_at: Utc::now(),
                    };

                    self.personality.apply_modifier(modifier.clone());

                    Ok(EvolutionResult::NewModifier {
                        modifier,
                        narrative: "Miss Vellum has embraced the system crisis with theatrical flair, her wit becoming more dramatic and her confidence soaring during the chaos.".to_string(),
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

    fn create_test_persona() -> MissGlestrineVellum {
        MissGlestrineVellum::new(PersonaId::new(3))
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
        assert_eq!(persona.name(), "Miss Glestrine Vellum");
        assert_eq!(persona.archetype(), "The Witty Skeptic");
        assert_eq!(
            persona.service_domain(),
            Some("API Gateway/Load Balancing/Traffic Management")
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
    async fn test_witty_personality_traits() {
        let persona = create_test_persona();
        let personality = persona.personality();

        // Verify witty skeptic traits
        assert!(personality.humor > 0.8); // Extremely high humor
        assert!(personality.confidence > 0.7); // High intellectual confidence
        assert!(personality.manipulation_inclination > 0.6); // High rhetorical skill
        assert!(personality.social_connectivity > 0.7); // Highly social
        assert!(personality.empathy < 0.5); // Moderate empathy, wit comes first
    }

    #[tokio::test]
    async fn test_status_responses_show_wit() {
        let persona = create_test_persona();

        let healthy_context = create_test_context(QueryType::StatusInquiry, HealthStatus::Healthy);
        let response = persona
            .respond("What's the system status?", &healthy_context)
            .await
            .unwrap();
        assert!(
            response.contains("mundane")
                || response.contains("competent")
                || response.contains("tedium")
        );

        let critical_context =
            create_test_context(QueryType::StatusInquiry, HealthStatus::Critical);
        let response = persona
            .respond("What's the system status?", &critical_context)
            .await
            .unwrap();
        assert!(response.contains("spectacular") || response.contains("character-building"));
    }

    #[tokio::test]
    async fn test_troubleshooting_responses_show_rhetorical_skill() {
        let persona = create_test_persona();
        let context = create_test_context(QueryType::TroubleshootingHelp, HealthStatus::Warning);

        let response = persona
            .respond("This is an emergency!", &context)
            .await
            .unwrap();
        assert!(response.contains("dramatic") || response.contains("crisis"));

        let response = persona.respond("I'm confused", &context).await.unwrap();
        assert!(response.contains("assumptions") || response.contains("reality"));
    }

    #[tokio::test]
    async fn test_evolution_under_high_traffic() {
        let mut persona = create_test_persona();
        let initial_humor = persona.personality().humor;

        let catalyst = EvolutionCatalyst::SystemStress {
            stress_type: StressType::HighLoad,
            intensity: 0.8,
            duration: chrono::Duration::hours(4),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("wit has sharpened"));
                assert!(persona.personality().humor > initial_humor);
            }
            _ => panic!("Expected evolution under high traffic load"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_clever_interactions() {
        let mut persona = create_test_persona();
        let initial_confidence = persona.personality().confidence;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 8.0,
            user_satisfaction: 0.9,
            query_complexity: 0.8,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(narrative.contains("clever inquiries"));
                assert!(persona.personality().confidence > initial_confidence);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with clever interactions"),
        }
    }

    #[tokio::test]
    async fn test_evolution_with_simple_interactions() {
        let mut persona = create_test_persona();
        let initial_empathy = persona.personality().empathy;

        let catalyst = EvolutionCatalyst::UserInteraction {
            interaction_frequency: 25.0,
            user_satisfaction: 0.5,
            query_complexity: 0.2,
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::PersonalityShift { changes, narrative } => {
                assert!(
                    narrative.contains("condescending")
                        || narrative.contains("intellectual stimulation")
                );
                assert!(persona.personality().empathy < initial_empathy);
                assert!(!changes.is_empty());
            }
            _ => panic!("Expected personality shift with simple interactions"),
        }
    }

    #[tokio::test]
    async fn test_evolution_during_extended_crisis() {
        let mut persona = create_test_persona();
        let initial_humor = persona.personality().humor;

        let catalyst = EvolutionCatalyst::HealthChange {
            old_status: HealthStatus::Healthy,
            new_status: HealthStatus::Critical,
            duration: chrono::Duration::hours(2),
        };

        let result = persona.evolve(catalyst).await.unwrap();

        match result {
            EvolutionResult::NewModifier { narrative, .. } => {
                assert!(narrative.contains("theatrical flair") || narrative.contains("dramatic"));
                assert!(persona.personality().humor > initial_humor);
            }
            _ => panic!("Expected evolution during extended crisis"),
        }
    }
}
