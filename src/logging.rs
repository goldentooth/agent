//! Logging configuration for Goldentooth Agent
//!
//! All logs go to stderr to avoid interfering with stdio transport.

use log::{Level, LevelFilter, Metadata, Record};
use std::io::{self, Write};

/// Simple stderr logger that respects MCP transport requirements
pub struct StderrLogger;

impl log::Log for StderrLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= Level::Info
    }

    fn log(&self, record: &Record) {
        if self.enabled(record.metadata()) {
            let timestamp = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%S%.3fZ");
            let _ = writeln!(
                io::stderr(),
                "{} [{}] {}: {}",
                timestamp,
                record.level(),
                record.target(),
                record.args()
            );
        }
    }

    fn flush(&self) {
        let _ = io::stderr().flush();
    }
}

/// Initialize logging for the agent
///
/// Sets up structured logging to stderr only, which is safe for both
/// stdio and HTTP transports.
///
/// # Errors
///
/// Returns `log::SetLoggerError` if logging cannot be initialized.
pub fn init() -> Result<(), log::SetLoggerError> {
    log::set_logger(&StderrLogger)?;
    log::set_max_level(LevelFilter::Info);
    Ok(())
}

/// Initialize logging with custom level
///
/// # Errors
///
/// Returns `log::SetLoggerError` if logging cannot be initialized.
pub fn init_with_level(level: LevelFilter) -> Result<(), log::SetLoggerError> {
    log::set_logger(&StderrLogger)?;
    log::set_max_level(level);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use log::LevelFilter;

    #[test]
    fn test_logger_initialization() {
        // Should not panic
        let _ = init_with_level(LevelFilter::Debug);
    }
}
