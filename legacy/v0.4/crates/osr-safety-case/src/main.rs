//! `osr-safety-case` — compile a GSN TOML directory to a rendered
//! safety case.
//!
//! Usage:
//!     osr-safety-case <GSN_DIR> [--evidence-root <ROOT>] [--quiet] [--results <toml>] [--require-verified | --require-accepted]
//!
//! Exit status:
//! - `0` if traceability and any explicitly requested result gate pass.
//! - `1` on any validation / parse / IO error, including closure
//!   failure. Intended to be wired into CI as a hard gate.

use std::env;
use std::path::PathBuf;
use std::process::ExitCode;

use osr_safety_case::{render_text, Case};

fn usage() -> &'static str {
    "usage: osr-safety-case <gsn-dir> [--evidence-root <root>] [--quiet] [--results <toml>] [--require-verified | --require-accepted]"
}

fn main() -> ExitCode {
    let args: Vec<String> = env::args().skip(1).collect();

    let mut gsn_dir: Option<PathBuf> = None;
    let mut evidence_root: Option<PathBuf> = None;
    let mut quiet = false;
    let mut results_path: Option<PathBuf> = None;
    let mut require_verified = false;
    let mut require_accepted = false;

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
            "--results" => {
                i += 1;
                let Some(value) = args.get(i) else {
                    eprintln!("missing value for --results");
                    return ExitCode::from(1);
                };
                results_path = Some(PathBuf::from(value));
            }
            "--require-verified" => require_verified = true,
            "--require-accepted" => require_accepted = true,
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
            "OK — traceability complete; proof results and acceptance are separate ({} goals, {} strategies, {} solutions)",
            case.goal_count(),
            case.strategy_count(),
            case.solution_count(),
        );
    }

    let records = if let Some(path) = results_path {
        match std::fs::read_to_string(path)
            .map_err(|error| error.to_string())
            .and_then(|text| {
                toml::from_str::<osr_safety_case::results::Results>(&text)
                    .map_err(|error| error.to_string())
            }) {
            Ok(records) => records,
            Err(error) => {
                eprintln!("result records: {error}");
                return ExitCode::from(1);
            }
        }
    } else {
        osr_safety_case::results::Results {
            schema: "osr-evidence-results/1".into(),
            result: vec![],
        }
    };
    let statuses = match case.assess_results(&records, &evidence_root) {
        Ok(statuses) => statuses,
        Err(error) => {
            eprintln!("result records: {error}");
            return ExitCode::from(1);
        }
    };
    if !quiet {
        println!(
            "Evidence: {} / {} current successful results; {} independently accepted records",
            statuses.iter().filter(|s| s.verified).count(),
            statuses.len(),
            statuses.iter().filter(|s| s.accepted).count()
        );
    }
    let gaps: Vec<_> = statuses
        .iter()
        .filter(|s| (require_verified && !s.verified) || (require_accepted && !s.accepted))
        .collect();
    if !gaps.is_empty() {
        for gap in gaps {
            eprintln!("{}: {}", gap.solution, gap.reason);
        }
        return ExitCode::from(1);
    }
    ExitCode::SUCCESS
}
