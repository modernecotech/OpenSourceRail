//! Native binary entry — shim over the library in `lib.rs`.

use clap::Parser;
use osr_occ_gui::OccApp;

#[derive(Parser, Debug)]
#[command(
    name = "osr-occ-gui",
    about = "OpenSourceRail operations-control dispatcher console (RFC 0018)."
)]
struct Cli {
    #[arg(long, default_value = "unidentified dispatcher")]
    operator: String,
    /// Pre-attach a recorded sim run at startup so the default view
    /// is populated.
    #[arg(long)]
    auto_attach: bool,
}

fn main() -> eframe::Result<()> {
    let cli = Cli::parse();
    let options = eframe::NativeOptions::default();
    eframe::run_native(
        "OSR OCC Console",
        options,
        Box::new(move |_cc| {
            Ok(Box::new(OccApp::with_auto_attach(
                cli.operator,
                cli.auto_attach,
            )))
        }),
    )
}
