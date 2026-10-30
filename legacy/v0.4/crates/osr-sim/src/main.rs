//! OpenSourceRail simulator CLI.

use clap::Parser;
use osr_sim::{scenario_file, sim};
use std::path::PathBuf;
use std::process::ExitCode;

#[derive(Debug, Parser)]
#[command(
    name = "osr-sim",
    about = "OpenSourceRail — urban rail network simulator",
    long_about = "\
Runs a time-stepped simulation of an urban rail network (stations, lines,
fleet, schedule). Scenarios are TOML files emitted by `osr-design` (see
cities/catalogue/<region>/<country>/<city>/<slug>.toml). When --config is omitted,
the bundled Samawah reference scenario is loaded.
",
    version
)]
struct Cli {
    /// Path to a scenario TOML file. When omitted, falls back to the
    /// bundled Samawah reference scenario
    /// (cities/catalogue/west-asia/Iraq/Samawah/samawah.toml).
    #[arg(long)]
    config: Option<PathBuf>,

    /// Simulation duration in seconds.
    #[arg(long, default_value_t = 3600)]
    duration: u32,

    /// Simulation time step in seconds.
    #[arg(long, default_value_t = 1)]
    time_step: u32,

    /// Print a status line every N sim-seconds. Zero disables.
    #[arg(long, default_value_t = 60)]
    status_every: u32,

    /// Optional JSON output path for the event log + summary.
    #[arg(long)]
    json_out: Option<PathBuf>,

    /// Keep aggregate event counts but omit the detailed event trace from
    /// memory and JSON. Intended for full-day acceptance/resilience runs.
    #[arg(long, requires = "json_out")]
    compact_json: bool,

    /// Optional CSV output path for per-train periodic snapshots.
    #[arg(long)]
    csv_out: Option<PathBuf>,

    /// CSV snapshot interval in sim-seconds (default 60).
    #[arg(long, default_value_t = 60)]
    csv_every: u32,

    /// Interval between consensus-backed osr-interlocking MA consistency
    /// checks, in sim-seconds. Zero keeps bounded direct MA state but omits
    /// Raft history and auditing. Default 30.
    #[arg(long, default_value_t = 30)]
    ma_check_every: u32,
}

fn main() -> ExitCode {
    let cli = Cli::parse();

    let config = match load_scenario(&cli) {
        Ok(c) => c,
        Err(msg) => {
            eprintln!("error: {msg}");
            return ExitCode::from(2);
        }
    };

    let runtime = sim::RuntimeConfig {
        duration_s: cli.duration,
        time_step_s: cli.time_step,
        status_every_s: cli.status_every,
        csv_out: cli.csv_out.clone(),
        csv_every_s: cli.csv_every,
        ma_check_every_s: cli.ma_check_every,
    };

    let result = sim::run_with_event_recording(&config, &runtime, !cli.compact_json);
    osr_sim::report::print_summary(&config, &runtime, &result);

    if let Some(path) = &cli.json_out {
        let json = serde_json::to_string_pretty(&result).expect("serialize result");
        if let Err(e) = std::fs::write(path, json) {
            eprintln!("error: writing JSON to {}: {}", path.display(), e);
            return ExitCode::from(1);
        }
        println!("\nJSON trace written to {}", path.display());
    }

    if !result.invariant_violations.is_empty() {
        ExitCode::from(1)
    } else {
        ExitCode::SUCCESS
    }
}

fn load_scenario(cli: &Cli) -> Result<sim::ScenarioConfig, String> {
    if let Some(path) = &cli.config {
        return scenario_file::load_scenario_from_path(path)
            .map_err(|e| format!("loading {}: {}", path.display(), e));
    }
    Ok(scenario_file::canonical_samawah_scenario())
}
