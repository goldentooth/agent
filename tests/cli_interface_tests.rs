use goldentooth_agent::cli::{CLIInterface, CLICommand, CLIResult, CharactersAction, PulseAction, ConfigAction};
use goldentooth_agent::core::{PersonaId, AgentFoundation};
use goldentooth_agent::error::AgentError;
use clap::Parser;
use tokio_test;

#[derive(Parser, Debug, Clone)]
#[command(name = "goldentooth-agent")]
#[command(about = "Goldentooth cluster intelligence agent")]
struct TestCli {
    #[command(subcommand)]
    command: CLICommand,
}

#[tokio::test]
async fn cli_interface_can_be_created() {
    let cli = CLIInterface::new();
    assert!(cli.is_initialized());
}

#[tokio::test]
async fn cli_interface_can_parse_characters_list_command() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "characters", "list"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_ok());
    
    match result.unwrap() {
        CLICommand::Characters { action } => {
            match action {
                CharactersAction::List => {}, // Expected
                _ => panic!("Expected List action"),
            }
        },
        _ => panic!("Expected Characters command"),
    }
}

#[tokio::test]
async fn cli_interface_can_parse_talk_command() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "talk", "calliope", "What is the cluster status?"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_ok());
    
    match result.unwrap() {
        CLICommand::Talk { character, message } => {
            assert_eq!(character, "calliope");
            assert_eq!(message, "What is the cluster status?");
        },
        _ => panic!("Expected Talk command"),
    }
}

#[tokio::test]
async fn cli_interface_can_parse_pulse_check_command() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "pulse", "check"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_ok());
    
    match result.unwrap() {
        CLICommand::Pulse { action } => {
            match action {
                PulseAction::Check => {}, // Expected
                _ => panic!("Expected Check action"),
            }
        },
        _ => panic!("Expected Pulse command"),
    }
}

#[tokio::test]
async fn cli_interface_can_parse_pulse_status_command() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "pulse", "status"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_ok());
    
    match result.unwrap() {
        CLICommand::Pulse { action } => {
            match action {
                PulseAction::Status => {}, // Expected
                _ => panic!("Expected Status action"),
            }
        },
        _ => panic!("Expected Pulse command"),
    }
}

#[tokio::test]
async fn cli_interface_can_parse_config_show_command() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "config", "show"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_ok());
    
    match result.unwrap() {
        CLICommand::Config { action } => {
            match action {
                ConfigAction::Show => {}, // Expected
                _ => panic!("Expected Show action"),
            }
        },
        _ => panic!("Expected Config command"),
    }
}

#[tokio::test]
async fn cli_interface_can_parse_config_set_command() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "config", "set", "cluster.endpoint", "https://k8s.goldentooth.net"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_ok());
    
    match result.unwrap() {
        CLICommand::Config { action } => {
            match action {
                ConfigAction::Set { key, value } => {
                    assert_eq!(key, "cluster.endpoint");
                    assert_eq!(value, "https://k8s.goldentooth.net");
                },
                _ => panic!("Expected Set action"),
            }
        },
        _ => panic!("Expected Config command"),
    }
}

#[tokio::test]
async fn cli_interface_rejects_invalid_commands() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "invalid-command"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::CLIParseError(_) => {}, // Expected
        _ => panic!("Expected CLIParseError"),
    }
}

#[tokio::test]
async fn cli_interface_requires_character_name_for_talk() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "talk"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_err());
}

#[tokio::test]
async fn cli_interface_requires_message_for_talk() {
    let cli = CLIInterface::new();
    let args = vec!["goldentooth-agent", "talk", "calliope"];
    
    let result = cli.parse_args(args).await;
    assert!(result.is_err());
}

#[tokio::test]
async fn cli_interface_can_execute_characters_list_command() {
    let mut agent = AgentFoundation::new().await.unwrap();
    let cli = CLIInterface::new();
    
    let command = CLICommand::Characters { 
        action: CharactersAction::List 
    };
    
    let result = cli.execute_command(command, &mut agent).await;
    assert!(result.is_ok());
    
    let output = result.unwrap();
    assert!(output.contains("Available characters:"));
}

#[tokio::test]
async fn cli_interface_can_execute_pulse_status_command() {
    let mut agent = AgentFoundation::new().await.unwrap();
    let cli = CLIInterface::new();
    
    let command = CLICommand::Pulse { 
        action: PulseAction::Status 
    };
    
    let result = cli.execute_command(command, &mut agent).await;
    assert!(result.is_ok());
    
    let output = result.unwrap();
    assert!(output.contains("Pulse system status:"));
}

#[tokio::test]
async fn cli_interface_can_execute_config_show_command() {
    let mut agent = AgentFoundation::new().await.unwrap();
    let cli = CLIInterface::new();
    
    let command = CLICommand::Config { 
        action: ConfigAction::Show 
    };
    
    let result = cli.execute_command(command, &mut agent).await;
    assert!(result.is_ok());
    
    let output = result.unwrap();
    assert!(output.contains("Current configuration:"));
}

#[tokio::test]
async fn cli_interface_handles_talk_with_nonexistent_character() {
    let mut agent = AgentFoundation::new().await.unwrap();
    let cli = CLIInterface::new();
    
    let command = CLICommand::Talk {
        character: "nonexistent".to_string(),
        message: "Hello".to_string(),
    };
    
    let result = cli.execute_command(command, &mut agent).await;
    assert!(result.is_err());
    
    match result.unwrap_err() {
        AgentError::PersonaNotFound(_) => {}, // Expected
        _ => panic!("Expected PersonaNotFound error"),
    }
}

#[tokio::test]
async fn cli_interface_provides_helpful_error_messages() {
    let cli = CLIInterface::new();
    let invalid_args = vec!["goldentooth-agent", "talk", "calliope"]; // Missing message
    
    let result = cli.parse_args(invalid_args).await;
    assert!(result.is_err());
    
    let error = result.unwrap_err();
    let error_message = format!("{}", error);
    assert!(error_message.contains("required"));
    assert!(error_message.len() > 10); // Should be a helpful message, not just "error"
}

// Test CLI command definitions
#[derive(Parser, Debug, Clone, PartialEq)]
enum CLICommand {
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

// Types are already defined in the library