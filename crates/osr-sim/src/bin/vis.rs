//! osr-vis — renders a scenario as a self-contained HTML+SVG diagram.
//!
//! Usage:
//!   osr-vis --config cities/catalogue/west-asia/Iraq/Samawah/samawah.toml --out /tmp/samawah.html
//! then open /tmp/samawah.html in any browser.

use clap::Parser;
use osr_sim::{scenario_file, vis};
use std::path::PathBuf;
use std::process::ExitCode;

#[derive(Debug, Parser)]
#[command(
    name = "osr-vis",
    about = "OpenSourceRail — render a scenario as HTML/SVG",
    long_about = "\
Produces a self-contained HTML file that diagrams the network, stations,
and energy sites. Open it in any browser — no server required.
",
    version
)]
struct Cli {
    /// Path to a scenario TOML file. When omitted, falls back to the
    /// bundled Samawah reference scenario.
    #[arg(long)]
    config: Option<PathBuf>,

    /// Output HTML file path.
    #[arg(long, default_value = "network.html")]
    out: PathBuf,
}

fn main() -> ExitCode {
    let cli = Cli::parse();

    let config = if let Some(path) = &cli.config {
        match scenario_file::load_scenario_from_path(path) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("error: loading {}: {}", path.display(), e);
                return ExitCode::from(2);
            }
        }
    } else {
        scenario_file::canonical_samawah_scenario()
    };

    let html = vis::render_html(&config);
    if let Err(e) = std::fs::write(&cli.out, html) {
        eprintln!("error: writing {}: {}", cli.out.display(), e);
        return ExitCode::from(1);
    }
    println!("wrote {}", cli.out.display());
    ExitCode::SUCCESS
}
