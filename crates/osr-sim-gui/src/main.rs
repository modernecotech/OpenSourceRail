//! Native binary entry — shim over the library in `lib.rs`.

use clap::Parser;
use osr_sim_gui::SimApp;

#[derive(Parser, Debug)]
#[command(
    name = "osr-sim-gui",
    about = "OpenSourceRail simulator GUI (RFC 0018)."
)]
struct Cli {
    #[arg(long)]
    scenario: Option<String>,
    #[arg(long, default_value_t = 3600)]
    duration_s: u32,
}

fn main() -> eframe::Result<()> {
    let cli = Cli::parse();
    let options = eframe::NativeOptions::default();
    eframe::run_native(
        "OSR Sim GUI",
        options,
        Box::new(move |_cc| Ok(Box::new(SimApp::new(cli.scenario.as_deref(), cli.duration_s)))),
    )
}
