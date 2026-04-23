//! `osr-selftest` CLI — the DIY assembly-path commissioning tool.

use std::process::ExitCode;

use clap::Parser;
use osr_selftest::{runtime, Role};

#[derive(Parser, Debug)]
#[command(
    name = "osr-selftest",
    about = "OpenSourceRail per-role post-assembly self-test (RFC 0019)."
)]
struct Cli {
    /// Host-class role. One of: t-ecu-s, t-ecu-a, t-obs, w-sbc, s-sbc.
    #[arg(long)]
    role: String,
    /// Emit JSON instead of the terminal-formatted report.
    #[arg(long)]
    json: bool,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    let Some(role) = Role::from_cli(&cli.role) else {
        eprintln!(
            "error: unknown role '{}'. expected one of: \
             t-ecu-s, t-ecu-a, t-obs, w-sbc, s-sbc",
            cli.role
        );
        return ExitCode::from(2);
    };

    let report = runtime::run_checks(role.name(), &role.checks());

    if cli.json {
        println!("{}", report.format_json());
    } else {
        println!("{}", report.format_text());
    }

    if report.all_pass() {
        ExitCode::from(0)
    } else {
        ExitCode::from(1)
    }
}
