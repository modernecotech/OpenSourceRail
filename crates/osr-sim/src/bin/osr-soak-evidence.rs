use std::fmt::Write as _;
use std::fs;
use std::path::{Path, PathBuf};

use osr_sim::soak::{run_suite, ResourceSnapshot, SoakConfig, SoakReport};

const JSON_PATH: &str = "docs/certification/software-soak-report.json";
const MARKDOWN_PATH: &str = "docs/certification/software-soak-report.md";

fn markdown(report: &SoakReport) -> String {
    let mut value = String::new();
    writeln!(value, "# Deterministic Multi-Day Software Soak Report\n").unwrap();
    writeln!(value, "> Software design evidence only. This accelerated simulation is not target-hardware endurance, WCET evidence, certification, or permission to operate.\n").unwrap();
    writeln!(
        value,
        "- Result: **{}**",
        if report.passed { "PASS" } else { "FAIL" }
    )
    .unwrap();
    writeln!(
        value,
        "- Duration: **{} simulated days per profile**",
        report.configuration.days
    )
    .unwrap();
    writeln!(
        value,
        "- Fixed simulation step: **{} seconds**",
        report.configuration.time_step_s
    )
    .unwrap();
    writeln!(value, "- Profiles: normal, peak, degraded and recovery").unwrap();
    writeln!(
        value,
        "- Growth measure: retained logical state at the halfway and final checkpoints\n"
    )
    .unwrap();
    writeln!(value, "## Profile Results\n").unwrap();
    writeln!(
        value,
        "| Profile | Seed | Result | Min SoC | Train-km | Faults | Invariant failures |"
    )
    .unwrap();
    writeln!(value, "|---|---:|---|---:|---:|---:|---:|").unwrap();
    for profile in &report.profiles {
        writeln!(
            value,
            "| {} | `{}` | **{}** | {:.3} | {:.1} | {} | {} |",
            profile.profile.name(),
            profile.seed,
            if profile.passed { "PASS" } else { "FAIL" },
            profile.minimum_train_soc,
            profile.total_train_km,
            profile.faults_fired,
            profile.invariant_failures,
        )
        .unwrap();
    }
    writeln!(value, "\n## Retained-State Growth\n").unwrap();
    writeln!(value, "Every final value is checked against the declared bound. A smaller checkpoint value may grow only until that cap is reached.\n").unwrap();
    writeln!(value, "| Profile | Resource | Halfway | Final | Bound |").unwrap();
    writeln!(value, "|---|---|---:|---:|---:|").unwrap();
    for profile in &report.profiles {
        let rows = snapshot_rows(&profile.checkpoint, &profile.final_state, &profile.bounds);
        for (name, halfway, final_value, bound) in rows {
            writeln!(
                value,
                "| {} | {} | {} | {} | {} |",
                profile.profile.name(),
                name,
                halfway,
                final_value,
                bound
            )
            .unwrap();
        }
    }
    writeln!(value, "\n## Assertions\n").unwrap();
    for profile in &report.profiles {
        writeln!(value, "### {}\n", profile.profile.name()).unwrap();
        for assertion in &profile.assertions {
            writeln!(value, "- PASS — {assertion}").unwrap();
        }
        for failure in &profile.failures {
            writeln!(value, "- FAIL — {failure}").unwrap();
        }
        writeln!(value).unwrap();
    }
    writeln!(value, "## Remaining Release Evidence\n").unwrap();
    for item in &report.remaining_release_evidence {
        writeln!(value, "- {item}").unwrap();
    }
    value
}

fn snapshot_rows<'a>(
    checkpoint: &'a ResourceSnapshot,
    final_state: &'a ResourceSnapshot,
    bounds: &'a osr_sim::soak::ResourceBounds,
) -> [(&'static str, u64, u64, u64); 9] {
    [
        (
            "detailed events",
            checkpoint.detailed_events_retained,
            final_state.detailed_events_retained,
            bounds.detailed_events_retained,
        ),
        (
            "event-count keys",
            checkpoint.event_count_keys,
            final_state.event_count_keys,
            bounds.event_count_keys,
        ),
        (
            "event records",
            checkpoint.event_records_retained,
            final_state.event_records_retained,
            bounds.event_records_retained,
        ),
        (
            "T2G payloads",
            checkpoint.t2g_payloads_retained,
            final_state.t2g_payloads_retained,
            bounds.t2g_payloads_retained,
        ),
        (
            "historian metrics",
            checkpoint.historian_metrics_retained,
            final_state.historian_metrics_retained,
            bounds.historian_metrics_retained,
        ),
        (
            "historian samples",
            checkpoint.historian_samples_retained,
            final_state.historian_samples_retained,
            bounds.historian_samples_retained,
        ),
        (
            "CBM components",
            checkpoint.cbm_components_tracked,
            final_state.cbm_components_tracked,
            bounds.cbm_components_tracked,
        ),
        (
            "work orders",
            checkpoint.work_orders_retained,
            final_state.work_orders_retained,
            bounds.work_orders_retained,
        ),
        (
            "compact result bytes",
            checkpoint.compact_result_bytes,
            final_state.compact_result_bytes,
            bounds.compact_result_bytes,
        ),
    ]
}

fn atomic_write(path: &Path, bytes: &[u8]) -> std::io::Result<()> {
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    fs::create_dir_all(parent)?;
    let temporary = path.with_extension("tmp");
    fs::write(&temporary, bytes)?;
    fs::rename(temporary, path)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let arguments = std::env::args().skip(1).collect::<Vec<_>>();
    let check = arguments.iter().any(|argument| argument == "--check");
    let full = arguments.iter().any(|argument| argument == "--full");
    if arguments
        .iter()
        .any(|argument| !matches!(argument.as_str(), "--check" | "--full"))
    {
        return Err("usage: osr-soak-evidence [--check] [--full]".into());
    }
    if check && full {
        return Err(
            "--check validates the tracked fast report and cannot be combined with --full".into(),
        );
    }
    let configuration = if full {
        SoakConfig::full()
    } else {
        SoakConfig::fast()
    };
    let report = run_suite(configuration);
    let mut json = serde_json::to_vec_pretty(&report)?;
    json.push(b'\n');
    let rendered = markdown(&report).into_bytes();
    let targets = if full {
        [
            (
                PathBuf::from("build/assurance/software-soak-report.json"),
                json,
            ),
            (
                PathBuf::from("build/assurance/software-soak-report.md"),
                rendered,
            ),
        ]
    } else {
        [
            (PathBuf::from(JSON_PATH), json),
            (PathBuf::from(MARKDOWN_PATH), rendered),
        ]
    };
    for (path, expected) in targets {
        if check {
            let actual = fs::read(&path)?;
            if actual != expected {
                return Err(format!("stale soak evidence: {}", path.display()).into());
            }
        } else {
            atomic_write(&path, &expected)?;
        }
    }
    println!(
        "software soak evidence: {} ({} profiles × {} simulated days)",
        if report.passed { "PASS" } else { "FAIL" },
        report.profiles.len(),
        report.configuration.days,
    );
    if report.passed {
        Ok(())
    } else {
        Err("software soak invariant or resource-bound failure".into())
    }
}
