use std::fmt::Write as _;
use std::fs;
use std::path::{Path, PathBuf};

use osr_consensus::fault_harness::{FaultAction, FaultHarness, FaultReport};
use osr_consensus::{Category, NodeId};

const JSON_PATH: &str = "docs/certification/software-resilience-report.json";
const MARKDOWN_PATH: &str = "docs/certification/software-resilience-report.md";

fn tick() -> FaultAction {
    FaultAction::Tick {
        duration_ns: 100_000_000,
    }
}

fn scenario() -> Vec<FaultAction> {
    let node0 = NodeId::new(0);
    let node1 = NodeId::new(1);
    let node2 = NodeId::new(2);
    vec![
        tick(),
        tick(),
        FaultAction::Propose {
            value: b"baseline".to_vec(),
            category: Category::Advisory,
        },
        FaultAction::Checkpoint { node: node2 },
        FaultAction::Delay {
            node: node2,
            ticks: 3,
        },
        FaultAction::DropFrom {
            node: node1,
            enabled: true,
        },
        tick(),
        FaultAction::Heal { node: node1 },
        tick(),
        tick(),
        FaultAction::DiskFull { node: node0 },
        FaultAction::PartialWrite {
            node: node1,
            bytes: 7,
        },
        FaultAction::Checkpoint { node: node2 },
        FaultAction::Crash { node: node2 },
        tick(),
        FaultAction::Restart { node: node2 },
        FaultAction::Telemetry { available: false },
        FaultAction::Propose {
            value: b"telemetry-rejected".to_vec(),
            category: Category::Safety,
        },
        FaultAction::Telemetry { available: true },
        FaultAction::ClockOffset {
            offset_ns: 8_000_000_000,
        },
        FaultAction::Propose {
            value: b"clock-rejected".to_vec(),
            category: Category::Safety,
        },
        FaultAction::ClockOffset { offset_ns: 0 },
        FaultAction::TimeSource { available: false },
        FaultAction::Propose {
            value: b"time-source-rejected".to_vec(),
            category: Category::Safety,
        },
        FaultAction::TimeSource { available: true },
        FaultAction::Partition { node: node0 },
        tick(),
        tick(),
        FaultAction::Heal { node: node0 },
        tick(),
        tick(),
        FaultAction::Checkpoint { node: node0 },
        FaultAction::Checkpoint { node: node1 },
        FaultAction::Checkpoint { node: node2 },
    ]
}

fn markdown(report: &FaultReport) -> String {
    let rejected = report
        .trace
        .iter()
        .filter(|row| row.outcome == "rejected-fail-restrictive")
        .count();
    let mut value = String::new();
    writeln!(value, "# Deterministic Software Resilience Report\n").unwrap();
    writeln!(value, "> In-process design evidence only. Hardware, filesystem, network, clock, HIL and independent-assessment evidence remain required.\n").unwrap();
    writeln!(
        value,
        "- Result: **{}**",
        if report.passed { "PASS" } else { "FAIL" }
    )
    .unwrap();
    writeln!(value, "- Deterministic seed: `{}`", report.seed).unwrap();
    writeln!(
        value,
        "- Fault/recovery actions: **{}**",
        report.trace.len()
    )
    .unwrap();
    writeln!(
        value,
        "- Fail-restrictive safety proposal rejections: **{rejected}**"
    )
    .unwrap();
    writeln!(
        value,
        "- Runtime invariant failures: **{}**",
        report.invariant_failures.len()
    )
    .unwrap();
    writeln!(value, "\n## Checked Boundaries\n").unwrap();
    writeln!(
        value,
        "- node crash, stable-state restart and post-heal convergence;"
    )
    .unwrap();
    writeln!(
        value,
        "- asymmetric message loss, bounded delay, partition and healing;"
    )
    .unwrap();
    writeln!(
        value,
        "- atomic checkpoint behavior under disk-full and partial writes;"
    )
    .unwrap();
    writeln!(value, "- fail-closed rejection of corrupted, truncated, wrong-node and inconsistent stable state;").unwrap();
    writeln!(
        value,
        "- clock-offset, time-source and telemetry health gating for safety proposals; and"
    )
    .unwrap();
    writeln!(value, "- election, log-matching, leader-completeness, state-machine and fail-restrictive consensus invariants after every action.\n").unwrap();
    writeln!(value, "## Trace\n").unwrap();
    writeln!(
        value,
        "| Step | Action | Outcome | Leader | Commit | Safe inputs |"
    )
    .unwrap();
    writeln!(value, "|---:|---|---|---|---:|---|").unwrap();
    for row in &report.trace {
        writeln!(
            value,
            "| {} | `{:?}` | `{}` | {} | {} | {} |",
            row.step,
            row.action,
            row.outcome,
            row.leader
                .map_or_else(|| "none".into(), |id| id.to_string()),
            row.maximum_commit_index.0,
            if row.safe_state { "yes" } else { "no" }
        )
        .unwrap();
    }
    writeln!(value, "\n## Remaining Release Evidence\n").unwrap();
    writeln!(value, "Repeat these cases on the selected storage, processor, RTOS/OS, production transport and clock sources. Add power-cut injection, storage endurance, target-hardware wall-clock soak, WCET/stack/heap measurements, signed binary/update evidence and independent review before release. The separate deterministic multi-day simulator soak is design evidence only.").unwrap();
    value
}

fn atomic_write(path: &Path, bytes: &[u8]) -> std::io::Result<()> {
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    fs::create_dir_all(parent)?;
    let temporary = path.with_extension("tmp");
    fs::write(&temporary, bytes)?;
    fs::rename(temporary, path)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let check = std::env::args()
        .skip(1)
        .any(|argument| argument == "--check");
    let mut harness = FaultHarness::new(3, 100_000_000);
    let report = harness.run(24_301, &scenario());
    let mut json = serde_json::to_vec_pretty(&report)?;
    json.push(b'\n');
    let rendered = markdown(&report).into_bytes();
    for (path, expected) in [
        (PathBuf::from(JSON_PATH), json),
        (PathBuf::from(MARKDOWN_PATH), rendered),
    ] {
        if check {
            let actual = fs::read(&path)?;
            if actual != expected {
                return Err(format!("stale resilience evidence: {}", path.display()).into());
            }
        } else {
            atomic_write(&path, &expected)?;
        }
    }
    println!(
        "software resilience evidence: {} ({} actions)",
        if report.passed { "PASS" } else { "FAIL" },
        report.trace.len()
    );
    if report.passed {
        Ok(())
    } else {
        Err("resilience invariant failure".into())
    }
}
