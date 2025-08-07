use clap::Parser;

pub type CLIResult = Result<String, crate::error::AgentError>;

#[derive(Parser, Debug, Clone, PartialEq)]
pub enum CLICommand {
    #[command(about = "Manage personas and characters")]
    Characters {
        #[command(subcommand)]
        action: CharactersAction,
    },
    #[command(about = "Talk to a specific character")]
    Talk {
        #[arg(help = "Character name (calliope, caudex, glestrine, malvo, operant7, umbrell)")]
        character: String,
        #[arg(help = "Message to send to the character")]
        message: String,
    },
    #[command(about = "Manage pulse check system")]
    Pulse {
        #[command(subcommand)]
        action: PulseAction,
    },
    #[command(about = "Manage agent configuration")]
    Config {
        #[command(subcommand)]
        action: ConfigAction,
    },
}

#[derive(Parser, Debug, Clone, Copy, PartialEq)]
pub enum CharactersAction {
    #[command(about = "List all available characters")]
    List,
}

#[derive(Parser, Debug, Clone, Copy, PartialEq)]
pub enum PulseAction {
    #[command(about = "Trigger manual pulse check")]
    Check,
    #[command(about = "Show pulse system status")]
    Status,
}

#[derive(Parser, Debug, Clone, PartialEq)]
pub enum ConfigAction {
    #[command(about = "Show current configuration")]
    Show,
    #[command(about = "Set configuration value")]
    Set {
        #[arg(help = "Configuration key (e.g., cluster.endpoint)")]
        key: String,
        #[arg(help = "Configuration value")]
        value: String,
    },
}
