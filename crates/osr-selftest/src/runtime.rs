//! Check-runner primitives — `Outcome`, `Check`, `Report`.
//!
//! A check is a named function returning an [`Outcome`]. The
//! runner calls each check in order, collects a [`Report`], and
//! formats it for terminal + JSON output.

use serde::{Deserialize, Serialize};

/// Result of a single check.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum Outcome {
    /// The check ran and its expected post-condition held.
    Pass,
    /// The check ran and failed — carries a human-readable
    /// remediation.
    Fail { reason: String },
    /// The check was skipped (hardware not attached, optional
    /// sensor absent, etc.) — not a failure.
    Skip { reason: String },
}

impl Outcome {
    pub fn pass() -> Self {
        Outcome::Pass
    }
    pub fn fail(reason: impl Into<String>) -> Self {
        Outcome::Fail {
            reason: reason.into(),
        }
    }
    pub fn skip(reason: impl Into<String>) -> Self {
        Outcome::Skip {
            reason: reason.into(),
        }
    }
    pub fn is_pass(&self) -> bool {
        matches!(self, Outcome::Pass)
    }
    pub fn is_fail(&self) -> bool {
        matches!(self, Outcome::Fail { .. })
    }
}

/// A single named check.
#[derive(Clone)]
pub struct Check {
    pub name: &'static str,
    pub run: CheckFn,
}

impl std::fmt::Debug for Check {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Check").field("name", &self.name).finish()
    }
}

pub type CheckFn = fn() -> Outcome;

/// Result of running a suite of checks.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Report {
    pub role: String,
    pub entries: Vec<ReportEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportEntry {
    pub name: String,
    pub outcome: Outcome,
}

impl Report {
    /// Did every check pass (or skip — skips are permitted)?
    pub fn all_pass(&self) -> bool {
        self.entries.iter().all(|e| !e.outcome.is_fail())
    }

    /// Counts for the summary line.
    pub fn counts(&self) -> (usize, usize, usize) {
        let mut pass = 0;
        let mut fail = 0;
        let mut skip = 0;
        for e in &self.entries {
            match &e.outcome {
                Outcome::Pass => pass += 1,
                Outcome::Fail { .. } => fail += 1,
                Outcome::Skip { .. } => skip += 1,
            }
        }
        (pass, fail, skip)
    }

    /// Human-readable report (the terminal output `osr-selftest`
    /// prints by default).
    pub fn format_text(&self) -> String {
        let mut out = String::new();
        out.push_str(&format!("OSR self-test · role={}\n", self.role));
        for e in &self.entries {
            let tag = match &e.outcome {
                Outcome::Pass => "[ ok ]".to_string(),
                Outcome::Fail { .. } => "[FAIL]".to_string(),
                Outcome::Skip { .. } => "[skip]".to_string(),
            };
            out.push_str(&format!("  {tag}  {}\n", e.name));
            if let Outcome::Fail { reason } = &e.outcome {
                out.push_str(&format!("         → {reason}\n"));
            }
            if let Outcome::Skip { reason } = &e.outcome {
                out.push_str(&format!("         ({reason})\n"));
            }
        }
        let (pass, fail, skip) = self.counts();
        out.push_str(&format!(
            "\n  Summary: {pass} pass · {fail} fail · {skip} skip · {}\n",
            if self.all_pass() {
                "OVERALL PASS"
            } else {
                "OVERALL FAIL"
            }
        ));
        out
    }

    /// Structured JSON output for machine consumption (CI, CBM).
    pub fn format_json(&self) -> String {
        serde_json::to_string_pretty(self).unwrap_or_else(|e| format!("{{\"error\":\"{e}\"}}"))
    }
}

/// Run the given suite + produce a [`Report`].
pub fn run_checks(role: &str, checks: &[Check]) -> Report {
    let entries = checks
        .iter()
        .map(|c| ReportEntry {
            name: c.name.to_string(),
            outcome: (c.run)(),
        })
        .collect();
    Report {
        role: role.to_string(),
        entries,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn all_pass_empty_report_is_true() {
        let r = Report {
            role: "test".into(),
            entries: vec![],
        };
        assert!(r.all_pass());
    }

    #[test]
    fn all_pass_false_with_fail() {
        let r = Report {
            role: "test".into(),
            entries: vec![
                ReportEntry {
                    name: "a".into(),
                    outcome: Outcome::Pass,
                },
                ReportEntry {
                    name: "b".into(),
                    outcome: Outcome::fail("boom"),
                },
            ],
        };
        assert!(!r.all_pass());
    }

    #[test]
    fn skip_does_not_fail_overall() {
        let r = Report {
            role: "test".into(),
            entries: vec![
                ReportEntry {
                    name: "a".into(),
                    outcome: Outcome::skip("optional sensor absent"),
                },
                ReportEntry {
                    name: "b".into(),
                    outcome: Outcome::Pass,
                },
            ],
        };
        assert!(r.all_pass());
        assert_eq!(r.counts(), (1, 0, 1));
    }

    #[test]
    fn text_format_contains_pass_marker() {
        let r = Report {
            role: "t-ecu-s".into(),
            entries: vec![ReportEntry {
                name: "test".into(),
                outcome: Outcome::Pass,
            }],
        };
        let text = r.format_text();
        assert!(text.contains("[ ok ]"));
        assert!(text.contains("OVERALL PASS"));
    }
}
