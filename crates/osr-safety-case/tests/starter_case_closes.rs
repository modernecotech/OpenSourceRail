//! CI gate per RFC 0005 §4.9: the starter safety case under
//! `docs/safety-case/gsn/` must compile, every goal must trace to
//! evidence, and every non-"cite" evidence path must exist.
//!
//! Every evidence path in the starter case is expected to be a real
//! artefact in-tree — if you add a new goal, you must link it to
//! real evidence before committing, or this test fails.

use std::path::{Path, PathBuf};

use osr_safety_case::Case;

fn workspace_root() -> PathBuf {
    // CARGO_MANIFEST_DIR → crates/osr-safety-case/. Go up twice.
    let manifest =
        std::env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR set by cargo");
    Path::new(&manifest)
        .parent()
        .and_then(|p| p.parent())
        .expect("workspace root")
        .to_path_buf()
}

#[test]
fn starter_case_closes() {
    let root = workspace_root();
    let gsn_dir = root.join("docs/safety-case/gsn");
    assert!(
        gsn_dir.is_dir(),
        "missing starter GSN directory at {}",
        gsn_dir.display()
    );

    let case = Case::load_dir(&gsn_dir, &root).unwrap_or_else(|e| {
        panic!("starter safety case failed to compile: {e}");
    });

    // Sanity: the three root claims from RFC 0004 §7 must be present.
    let roots: Vec<_> = case.root_goals().iter().map(|g| g.id.clone()).collect();
    for expected in ["G1", "G2", "G3"] {
        assert!(
            roots.iter().any(|r| r == expected),
            "missing root goal {expected}; got {roots:?}"
        );
    }

    // The closure check is already inside Case::load_dir; this
    // duplicate call exists as a regression safety net in case the
    // gate is ever removed from the loader.
    let closed = case.closed_goals();
    for g in case.goals.values() {
        assert!(
            closed.contains(&g.id),
            "goal {} did not close against evidence",
            g.id
        );
    }
}
