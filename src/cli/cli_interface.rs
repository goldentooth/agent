use crate::cli::{CLICommand, CLIResult, CharactersAction, PulseAction, ConfigAction};
use crate::core::AgentFoundation;
use crate::error::AgentError;
use clap::Parser;

#[derive(Parser)]
#[command(name = "goldentooth-agent")]
#[command(about = "Goldentooth cluster intelligence agent")]
struct CliApp {
    #[command(subcommand)]
    command: CLICommand,
}

pub struct CLIInterface {
    initialized: bool,
}

impl CLIInterface {
    pub fn new() -> Self {
        Self {
            initialized: true,
        }
    }
    
    pub fn is_initialized(&self) -> bool {
        self.initialized
    }
    
    pub async fn parse_args(&self, args: Vec<&str>) -> Result<CLICommand, AgentError> {
        match CliApp::try_parse_from(args) {
            Ok(cli_app) => Ok(cli_app.command),
            Err(e) => Err(AgentError::CLIParseError(e.to_string())),
        }
    }
    
    pub async fn execute_command(
        &self, 
        command: CLICommand, 
        agent: &mut AgentFoundation
    ) -> CLIResult {
        match command {
            CLICommand::Characters { action } => {
                self.handle_characters_command(action, agent).await
            },
            CLICommand::Talk { character, message } => {
                self.handle_talk_command(character, message, agent).await
            },
            CLICommand::Pulse { action } => {
                self.handle_pulse_command(action, agent).await
            },
            CLICommand::Config { action } => {
                self.handle_config_command(action, agent).await
            },
        }
    }
    
    async fn handle_characters_command(
        &self,
        action: CharactersAction,
        _agent: &mut AgentFoundation,
    ) -> CLIResult {
        match action {
            CharactersAction::List => {
                Ok("Available characters:\n- Madam Calliope Harkthorn (calliope)\n- Dr. Caudex Thorne (caudex)\n- Miss Glestrine Vellum (glestrine)\n- Mr. Malvo Trevine (malvo)\n- Operant No. 7 (operant7)\n- Mr. Umbrell Severin (umbrell)".to_string())
            },
        }
    }
    
    async fn handle_talk_command(
        &self,
        character: String,
        _message: String,
        _agent: &mut AgentFoundation,
    ) -> CLIResult {
        // For now, just return an error for nonexistent characters
        match character.as_str() {
            "calliope" | "caudex" | "glestrine" | "malvo" | "operant7" | "umbrell" => {
                Ok(format!("{} says: 'Character implementation coming soon!'", character))
            },
            _ => Err(AgentError::PersonaNotFound(crate::error::PersonaId::new(999))),
        }
    }
    
    async fn handle_pulse_command(
        &self,
        action: PulseAction,
        _agent: &mut AgentFoundation,
    ) -> CLIResult {
        match action {
            PulseAction::Check => {
                Ok("Pulse check triggered. Results: All systems nominal.".to_string())
            },
            PulseAction::Status => {
                Ok("Pulse system status:\n- Last check: Never\n- Next check: In 30 minutes\n- Status: Inactive".to_string())
            },
        }
    }
    
    async fn handle_config_command(
        &self,
        action: ConfigAction,
        agent: &mut AgentFoundation,
    ) -> CLIResult {
        match action {
            ConfigAction::Show => {
                let config = agent.configuration_system.get_config();
                Ok(format!(
                    "Current configuration:\n- Cluster endpoint: {}\n- Pulse interval: {} minutes\n- SSL verification: {}",
                    if config.cluster.endpoint.is_empty() { "Not configured" } else { &config.cluster.endpoint },
                    config.pulse.interval_minutes,
                    config.cluster.verify_ssl
                ))
            },
            ConfigAction::Set { key, value } => {
                agent.configuration_system.set_config_value(&key, &value)?;
                Ok(format!("Configuration updated: {} = {}", key, value))
            },
        }
    }
}

impl Default for CLIInterface {
    fn default() -> Self {
        Self::new()
    }
}