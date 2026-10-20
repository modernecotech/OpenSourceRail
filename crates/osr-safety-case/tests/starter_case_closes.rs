//! Source traceability must not grant current maglev engineering acceptance.
use std::path::{Path, PathBuf};

use osr_safety_case::{results::Results, Case};

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|p| p.parent())
        .expect("workspace root")
        .to_path_buf()
}

#[test]
fn current_maglev_source_traceability_is_distinct_from_execution_acceptance() {
    let root = workspace_root();
    let fixture = tempfile::tempdir().unwrap();
    std::fs::write(
        fixture.path().join("current.toml"),
        r#"
[[goal]]
id = "MAGLEV-CONTROL"
description = "An exact control source can be traced; physical acceptance remains separate"

[[solution]]
id = "MAGLEV-SOURCE"
parent = "MAGLEV-CONTROL"
description = "Current control implementation source"
[solution.evidence]
kind = "proptest"
path = "crates/osr-maglev-control/src/lib.rs"
"#,
    )
    .unwrap();
    let case = Case::load_dir(fixture.path(), &root).unwrap();
    assert!(case.closed_goals().contains("MAGLEV-CONTROL"));
    let records = Results {
        schema: "osr-evidence-results/1".into(),
        result: vec![],
    };
    let states = case.assess_results(&records, &root).unwrap();
    assert_eq!(states.len(), 1);
    assert!(!states[0].verified && !states[0].accepted);
    let profile: toml::Value =
        toml::from_str(&std::fs::read_to_string(root.join("deployment/maglev.toml")).unwrap())
            .unwrap();
    for field in [
        "design_complete",
        "physical_validation",
        "manufacturing_release",
        "physical_release",
    ] {
        assert_eq!(profile["release"][field].as_bool(), Some(false));
    }
}
