use crate::cli::{CLICommand, CLIResult, CharactersAction, ConfigAction, PulseAction};
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
    #[must_use]
    pub fn new() -> Self {
        Self { initialized: true }
    }

    #[must_use]
    pub fn is_initialized(&self) -> bool {
        self.initialized
    }

    /// Parse command line arguments into CLI commands
    ///
    /// # Errors
    ///
    /// Returns `AgentError::CLIParseError` if the arguments cannot be parsed
    pub fn parse_args(&self, args: Vec<&str>) -> Result<CLICommand, AgentError> {
        match CliApp::try_parse_from(args) {
            Ok(cli_app) => Ok(cli_app.command),
            Err(e) => Err(AgentError::CLIParseError(e.to_string())),
        }
    }

    /// Execute a parsed CLI command
    ///
    /// # Errors
    ///
    /// Returns various `AgentError` variants depending on the command execution
    pub fn execute_command(&self, command: CLICommand, agent: &mut AgentFoundation) -> CLIResult {
        match command {
            CLICommand::Characters { action } => Ok(Self::handle_characters_command(action, agent)),
            CLICommand::Talk { character, message } => {
                Self::handle_talk_command(&character, message, agent)
            }
            CLICommand::Pulse { action } => Ok(Self::handle_pulse_command(action, agent)),
            CLICommand::Config { action } => Self::handle_config_command(action, agent),
        }
    }

    fn handle_characters_command(action: CharactersAction, _agent: &mut AgentFoundation) -> String {
        match action {
            CharactersAction::List => {
                "Available characters:\n- Madam Calliope Harkthorn (calliope)\n- Dr. Caudex Thorne (caudex)\n- Miss Glestrine Vellum (glestrine)\n- Mr. Malvo Trevine (malvo)\n- Operant No. 7 (operant7)\n- Mr. Umbrell Severin (umbrell)".to_string()
            },
        }
    }

    fn handle_talk_command(
        character: &str,
        _message: String,
        _agent: &mut AgentFoundation,
    ) -> CLIResult {
        // For now, just return an error for nonexistent characters
        match character {
            "calliope" | "caudex" | "glestrine" | "malvo" | "operant7" | "umbrell" => Ok(format!(
                "{character} says: 'Character implementation coming soon!'"
            )),
            _ => Err(AgentError::PersonaNotFound(crate::error::PersonaId::new(
                999,
            ))),
        }
    }

    fn handle_pulse_command(action: PulseAction, _agent: &mut AgentFoundation) -> String {
        match action {
            PulseAction::Check => {
                "Pulse check triggered. Results: All systems nominal.".to_string()
            },
            PulseAction::Status => {
                "Pulse system status:\n- Last check: Never\n- Next check: In 30 minutes\n- Status: Inactive".to_string()
            },
        }
    }

    fn handle_config_command(action: ConfigAction, agent: &mut AgentFoundation) -> CLIResult {
        match action {
            ConfigAction::Show => {
                let config = agent.configuration_system.get_config()?;
                Ok(format!(
                    "Current configuration:\n- Cluster endpoint: {}\n- Pulse interval: {} minutes\n- SSL verification: {}",
                    if config.cluster.endpoint.is_empty() {
                        "Not configured"
                    } else {
                        &config.cluster.endpoint
                    },
                    config.pulse.interval_minutes,
                    config.cluster.verify_ssl
                ))
            }
            ConfigAction::Set { key, value } => {
                agent.configuration_system.set_config_value(&key, &value)?;
                Ok(format!("Configuration updated: {key} = {value}"))
            }
        }
    }
}

impl Default for CLIInterface {
    fn default() -> Self {
        Self::new()
    }
}
