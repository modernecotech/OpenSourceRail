//! Deterministic pre-service execution of every deployable role self-test.
//!
//! These are the software known-answer checks from `osr-selftest`. Physical
//! wiring, sensors and trust-anchor commissioning remain hardware evidence.

use osr_selftest::{runtime, Outcome, Role};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct SelftestSystemsSummary {
    pub roles_run: u32,
    pub checks_passed: u32,
    pub checks_failed: u32,
    pub checks_skipped: u32,
    pub failed_checks: Vec<String>,
}

impl SelftestSystemsSummary {
    #[must_use]
    pub fn release_permitted(&self) -> bool {
        self.roles_run > 0 && self.checks_failed == 0
    }
}

#[must_use]
pub fn run_all_role_checks() -> SelftestSystemsSummary {
    let roles = [Role::TEcuS, Role::TEcuA, Role::TObs, Role::WSbc, Role::SSbc];
    let mut summary = SelftestSystemsSummary::default();
    for role in roles {
        summary.roles_run = summary.roles_run.saturating_add(1);
        let report = runtime::run_checks(role.name(), &role.checks());
        for entry in report.entries {
            match entry.outcome {
                Outcome::Pass => {
                    summary.checks_passed = summary.checks_passed.saturating_add(1);
                }
                Outcome::Fail { reason } => {
                    summary.checks_failed = summary.checks_failed.saturating_add(1);
                    summary.failed_checks.push(format!(
                        "{}: {} — {}",
                        role.name(),
                        entry.name,
                        reason
                    ));
                }
                Outcome::Skip { .. } => {
                    summary.checks_skipped = summary.checks_skipped.saturating_add(1);
                }
            }
        }
    }
    summary
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_role_passes_software_preflight() {
        let first = run_all_role_checks();
        let second = run_all_role_checks();
        assert_eq!(first, second);
        assert_eq!(first.roles_run, 5);
        assert!(first.checks_passed > 0);
        assert_eq!(first.checks_failed, 0);
        assert!(first.release_permitted());
    }
}
