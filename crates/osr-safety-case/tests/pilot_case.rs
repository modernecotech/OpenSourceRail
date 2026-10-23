//! Whole pilot source trace never manufactures physical acceptance.
use osr_safety_case::{results::Results, Case};
use std::path::Path;

#[test]
fn project_pilot_claims_have_explicit_paths_and_no_implicit_acceptance() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap();
    let folder = tempfile::tempdir().unwrap();
    std::fs::copy(
        root.join("engineering/ferrite_maglev/data/pilot-assurance-case.toml"),
        folder.path().join("pilot.toml"),
    )
    .unwrap();
    let case = Case::load_dir(folder.path(), root).unwrap();
    assert_eq!(case.goal_count(), 5);
    assert_eq!(case.solution_count(), 11);
    let records = Results {
        schema: "osr-evidence-results/1".into(),
        result: vec![],
    };
    assert!(case
        .assess_results(&records, root)
        .unwrap()
        .iter()
        .all(|s| !s.verified && !s.accepted));
    assert!(case.closed_goals().contains("PILOT-TRACE"));
}
