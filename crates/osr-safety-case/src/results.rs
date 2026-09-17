//! Result records are a separate gate from graph traceability. They must be
//! supplied by a controlled runner and reviewed independently; this module
//! validates records, it does not execute proofs or authenticate reviewers.
use crate::Case;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Results {
    pub schema: String,
    #[serde(default)]
    pub result: Vec<ResultRecord>,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ResultRecord {
    pub solution: String,
    pub kind: String,
    pub path: String,
    pub anchor: Option<String>,
    pub tool: String,
    pub tool_version: String,
    pub bounds: String,
    pub executed_by: String,
    pub status: String,
    pub exit_code: i32,
    /// Hashes of the evidence source and reviewed implementation/dependency scope.
    pub inputs: BTreeMap<String, String>,
    pub report: String,
    pub report_sha256: String,
    #[serde(skip_serializing)]
    pub acceptance: Option<Acceptance>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Acceptance {
    pub status: String,
    pub reviewer: String,
    pub reference: String,
    /// Acceptance binds to all result fields (including inputs, tool and bounds).
    pub result_sha256: String,
}

#[derive(Debug)]
pub struct EvidenceStatus {
    pub solution: String,
    pub verified: bool,
    pub accepted: bool,
    pub reason: String,
}

fn checked_hash(root: &Path, relative: &str, expected: &str) -> bool {
    let Ok(root) = root.canonicalize() else {
        return false;
    };
    let Ok(path) = root.join(relative).canonicalize() else {
        return false;
    };
    if !path.starts_with(&root) || !path.is_file() || Path::new(relative).is_absolute() {
        return false;
    }
    fs::read(path).is_ok_and(|bytes| format!("{:x}", Sha256::digest(bytes)) == expected)
}

impl ResultRecord {
    pub fn fingerprint(&self) -> String {
        // Fields are fixed and inputs use BTreeMap: canonical TOML is deterministic.
        format!(
            "{:x}",
            Sha256::digest(
                toml::to_string(self)
                    .expect("serializable result")
                    .as_bytes()
            )
        )
    }
}

impl Case {
    /// Assess every declared solution. Missing, failed or stale records never
    /// become successful evidence just because a source path exists.
    pub fn assess_results(
        &self,
        records: &Results,
        root: &Path,
    ) -> Result<Vec<EvidenceStatus>, String> {
        if records.schema != "osr-evidence-results/1" {
            return Err("unknown evidence-result schema".into());
        }
        let mut by_id = BTreeMap::new();
        for record in &records.result {
            if !self.solutions.contains_key(&record.solution)
                || by_id.insert(&record.solution, record).is_some()
            {
                return Err(format!(
                    "unknown or duplicate solution: {}",
                    record.solution
                ));
            }
        }
        Ok(self
            .solutions
            .values()
            .map(|solution| {
                let mut state = EvidenceStatus {
                    solution: solution.id.clone(),
                    verified: false,
                    accepted: false,
                    reason: "no execution result".into(),
                };
                let Some(record) = by_id.get(&solution.id) else {
                    return state;
                };
                let evidence = &solution.evidence;
                let harness_present = evidence.kind != "kani"
                    || evidence.anchor.as_ref().is_some_and(|anchor| {
                        fs::read_to_string(root.join(&evidence.path))
                            .is_ok_and(|source| source.contains(&format!("fn {anchor}(")))
                    });
                let valid = harness_present
                    && record.kind == evidence.kind
                    && record.path == evidence.path
                    && record.anchor == evidence.anchor
                    && record.status == "passed"
                    && record.exit_code == 0
                    && [
                        &record.tool,
                        &record.tool_version,
                        &record.bounds,
                        &record.executed_by,
                    ]
                    .iter()
                    .all(|value| !value.trim().is_empty())
                    && !record.inputs.is_empty()
                    && (evidence.kind == "cite" || record.inputs.contains_key(&evidence.path))
                    && record
                        .inputs
                        .iter()
                        .all(|(path, hash)| checked_hash(root, path, hash))
                    && checked_hash(root, &record.report, &record.report_sha256)
                    && record.report != evidence.path;
                if !valid {
                    state.reason =
                        "failed, incomplete, mismatched or stale execution result".into();
                    return state;
                }
                state.verified = true;
                state.accepted = record.acceptance.as_ref().is_some_and(|acceptance| {
                    acceptance.status == "accepted"
                        && !acceptance.reviewer.trim().is_empty()
                        && acceptance.reviewer != record.executed_by
                        && !acceptance.reference.trim().is_empty()
                        && acceptance.result_sha256 == record.fingerprint()
                });
                state.reason = if state.accepted {
                    "current result with recorded independent acceptance"
                } else {
                    "current successful result; independent acceptance missing"
                }
                .into();
                state
            })
            .collect())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Evidence, Solution};

    #[test]
    fn source_pointer_cannot_substitute_for_current_accepted_execution() {
        let root = tempfile::tempdir().unwrap();
        fs::write(root.path().join("source.rs"), "fn harness() {}\n").unwrap();
        fs::write(root.path().join("report.txt"), "controlled runner report").unwrap();
        let hash = |path| {
            format!(
                "{:x}",
                Sha256::digest(fs::read(root.path().join(path)).unwrap())
            )
        };
        let mut case = Case::default();
        case.solutions.insert(
            "E1".into(),
            Solution {
                id: "E1".into(),
                parent: "G1".into(),
                description: "test".into(),
                evidence: Evidence {
                    kind: "kani".into(),
                    path: "source.rs".into(),
                    anchor: Some("harness".into()),
                    note: None,
                },
            },
        );
        let mut records = Results {
            schema: "osr-evidence-results/1".into(),
            result: vec![],
        };
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].verified);
        records.result.push(ResultRecord {
            solution: "E1".into(),
            kind: "kani".into(),
            path: "source.rs".into(),
            anchor: Some("harness".into()),
            tool: "kani".into(),
            tool_version: "test-version".into(),
            bounds: "unwind 2".into(),
            executed_by: "runner".into(),
            status: "passed".into(),
            exit_code: 0,
            inputs: BTreeMap::from([("source.rs".into(), hash("source.rs"))]),
            report: "report.txt".into(),
            report_sha256: hash("report.txt"),
            acceptance: None,
        });
        let states = case.assess_results(&records, root.path()).unwrap();
        assert!(states[0].verified && !states[0].accepted);
        records.result[0].acceptance = Some(Acceptance {
            status: "accepted".into(),
            reviewer: "assessor".into(),
            reference: "review-1".into(),
            result_sha256: records.result[0].fingerprint(),
        });
        assert!(case.assess_results(&records, root.path()).unwrap()[0].accepted);
        records.result[0].tool_version = "changed-version".into();
        let changed = case.assess_results(&records, root.path()).unwrap();
        assert!(changed[0].verified && !changed[0].accepted);
        records.result[0].tool_version = "test-version".into();
        records.result[0].acceptance.as_mut().unwrap().reviewer = "runner".into();
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].accepted);
        records.result[0].status = "failed".into();
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].verified);
        records.result[0].status = "passed".into();
        records.result[0].anchor = Some("different_harness".into());
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].verified);
        records.result[0].anchor = Some("harness".into());
        records.result[0].bounds.clear();
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].verified);
        records.result[0].bounds = "unwind 2".into();
        records.result[0].exit_code = 1;
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].verified);
        records.result[0].exit_code = 0;
        fs::write(root.path().join("source.rs"), "changed implementation").unwrap();
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].verified);
        records.result[0]
            .inputs
            .insert("source.rs".into(), hash("source.rs"));
        fs::write(root.path().join("report.txt"), "changed result").unwrap();
        assert!(!case.assess_results(&records, root.path()).unwrap()[0].verified);
    }
}
