#![cfg(feature = "columnar")]

use osr_design_search::columnar::{
    index_cases, query_candidate, scan_index, verify_index, IndexOptions, MAX_PART_BYTES,
};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

static FIXTURE_COUNTER: AtomicU64 = AtomicU64::new(0);

struct Fixture(PathBuf);

impl Fixture {
    fn new() -> Self {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let sequence = FIXTURE_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "osr-columnar-test-{}-{nonce}-{sequence}",
            std::process::id()
        ));
        fs::create_dir_all(root.join("state/cases")).unwrap();
        Self(root)
    }

    fn state(&self) -> PathBuf {
        self.0.join("state")
    }
    fn index(&self) -> PathBuf {
        self.0.join("index")
    }

    fn add(&self, name: &str, candidate: &str, mass: Option<f64>) {
        let row = serde_json::json!({
            "candidate_id": candidate,
            "row_id": format!("row-{name}"),
            "body_candidate_id": "body-one",
            "bundle_definition_id": "bundle-one",
            "case_context_id": name,
            "family_id": "P1",
            "accounted_mass": {"accounted_tare_kg_per_car": mass},
            "installed_mass_kg": null,
            "physical_journey_completed": false,
            "complete_body_qualified": false,
            "large_unindexed_detail": ["a", "b", "c"]
        });
        fs::write(
            self.state().join("cases").join(format!("{name}.json")),
            serde_json::to_vec(&row).unwrap(),
        )
        .unwrap();
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn count_parts(path: &Path) -> usize {
    fs::read_dir(path).unwrap().count()
}

#[test]
fn indexes_sorted_cases_into_bounded_parts_and_roundtrips_nulls() {
    let f = Fixture::new();
    f.add("c", "candidate-two", None);
    f.add("a", "candidate-one", Some(12_345.25));
    f.add("b", "candidate-one", Some(12_345.5));
    let options = IndexOptions {
        batch_rows: 1,
        part_rows: 2,
    };
    assert_eq!(index_cases(&f.state(), &f.index(), options).unwrap(), 3);
    assert_eq!(count_parts(&f.index()), 2);
    assert_eq!(verify_index(&f.index(), &f.state()).unwrap(), 3);
    let rows = query_candidate(&f.index(), &f.state(), "candidate-one").unwrap();
    assert_eq!(
        rows.iter()
            .map(|row| row.case_path.as_str())
            .collect::<Vec<_>>(),
        ["cases/a.json", "cases/b.json"]
    );
    assert_eq!(rows[0].accounted_tare_kg_per_car, Some(12_345.25));
    assert_eq!(rows[0].installed_mass_kg, None);
    let mut ordinals = Vec::new();
    scan_index(&f.index(), |row| {
        ordinals.push(row.ordinal);
        Ok(())
    })
    .unwrap();
    assert_eq!(ordinals, [0, 1, 2]);
    for entry in fs::read_dir(f.index()).unwrap() {
        assert!(entry.unwrap().metadata().unwrap().len() <= MAX_PART_BYTES);
    }
}

#[test]
fn refuses_changed_case_and_existing_target() {
    let f = Fixture::new();
    f.add("a", "candidate-one", None);
    index_cases(&f.state(), &f.index(), IndexOptions::default()).unwrap();
    assert!(index_cases(&f.state(), &f.index(), IndexOptions::default()).is_err());
    assert_eq!(
        query_candidate(&f.index(), &f.state(), "candidate-one")
            .unwrap()
            .len(),
        1
    );
    fs::write(f.state().join("cases/a.json"), b"{}").unwrap();
    assert!(verify_index(&f.index(), &f.state()).is_err());
    assert!(query_candidate(&f.index(), &f.state(), "candidate-one").is_err());
}

#[test]
fn query_authenticates_only_matching_backing_case() {
    let f = Fixture::new();
    f.add("a", "candidate-one", Some(1.0));
    f.add("b", "candidate-two", Some(2.0));
    index_cases(&f.state(), &f.index(), IndexOptions::default()).unwrap();
    fs::write(f.state().join("cases/b.json"), b"tampered nonmatching case").unwrap();
    let rows = query_candidate(&f.index(), &f.state(), "candidate-one").unwrap();
    assert_eq!(rows.len(), 1);
    assert_eq!(rows[0].case_path, "cases/a.json");
    assert!(query_candidate(&f.index(), &f.state(), "candidate-two").is_err());
}

#[test]
fn rejects_invalid_resource_request_and_unknown_mass() {
    let f = Fixture::new();
    f.add("a", "candidate-one", Some(-1.0));
    assert!(index_cases(&f.state(), &f.index(), IndexOptions::default()).is_err());
    assert!(index_cases(
        &f.state(),
        &f.0.join("other"),
        IndexOptions {
            batch_rows: 129,
            part_rows: 512
        }
    )
    .is_err());
}
