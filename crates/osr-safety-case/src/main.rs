//! `osr-safety-case` — compile a GSN TOML directory to a rendered
//! safety case.
//!
//! Usage:
//!     osr-safety-case <GSN_DIR> [--evidence-root <ROOT>] [--quiet]
//!
//! Exit status:
//! - `0` if the case closes (every goal traces to evidence).
//! - `1` on any validation / parse / IO error, including closure
//!   failure. Intended to be wired into CI as a hard gate.

use std::env;
use std::path::PathBuf;
use std::process::ExitCode;

use osr_safety_case::{render_text, Case};

fn usage() -> &'static str {
    "usage: osr-safety-case <gsn-dir> [--evidence-root <root>] [--quiet]"
}

fn main() -> ExitCode {
    let args: Vec<String> = env::args().skip(1).collect();

    let mut gsn_dir: Option<PathBuf> = None;
    let mut evidence_root: Option<PathBuf> = None;
    let mut quiet = false;

    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--evidence-root" => {
                i += 1;
                let Some(v) = args.get(i) else {
                    eprintln!("missing value for --evidence-root\n{}", usage());
                    return ExitCode::from(1);
                };
                evidence_root = Some(PathBuf::from(v));
            }
            "--quiet" | "-q" => quiet = true,
            "-h" | "--help" => {
                println!("{}", usage());
                return ExitCode::SUCCESS;
            }
            _ if gsn_dir.is_none() && !args[i].starts_with("--") => {
                gsn_dir = Some(PathBuf::from(&args[i]));
            }
            other => {
                eprintln!("unrecognised argument {other:?}\n{}", usage());
                return ExitCode::from(1);
            }
        }
        i += 1;
    }

    let Some(gsn_dir) = gsn_dir else {
        eprintln!("{}", usage());
        return ExitCode::from(1);
    };
    // Default evidence root: two directories up from the gsn dir
    // (e.g. `docs/safety-case/gsn/` → repo root). Users can
    // override with `--evidence-root`.
    let evidence_root = evidence_root.unwrap_or_else(|| {
        gsn_dir
            .parent()
            .and_then(|p| p.parent())
            .and_then(|p| p.parent())
            .map(|p| p.to_path_buf())
            .unwrap_or_else(|| PathBuf::from("."))
    });

    let case = match Case::load_dir(&gsn_dir, &evidence_root) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("safety case failed to compile: {e}");
            return ExitCode::from(1);
        }
    };

    if !quiet {
        println!("{}", render_text(&case));
        println!(
            "OK — case closes ({} goals, {} strategies, {} solutions)",
            case.goal_count(),
            case.strategy_count(),
            case.solution_count(),
        );
    }

    ExitCode::SUCCESS
}
