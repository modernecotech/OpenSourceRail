use std::path::Path;

use osr_city_studio::CityProject;

fn samawah_project() -> CityProject {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
    CityProject::load(root).expect("load committed Samawah City Studio fixture")
}

#[test]
fn committed_project_compiles_without_validation_errors() {
    let snapshot = samawah_project()
        .compile()
        .expect("compile Samawah project");
    assert_eq!(snapshot.summary.validation_errors, 0);
    assert_eq!(snapshot.summary.station_count, 21);
    assert_eq!(snapshot.summary.locked_station_count, 3);
    assert_eq!(snapshot.summary.manual_station_count, 0);
    assert_eq!(snapshot.summary.manual_line_count, 0);
    assert_eq!(snapshot.lines.len(), 3);
    assert_eq!(snapshot.service_metrics.len(), 9);
    assert!(snapshot.sources.iter().all(|source| source.matches_lock));
}

#[test]
fn committed_revision_is_backward_compatible_and_semantically_comparable() {
    let project = samawah_project();
    let revisions = project.revisions().expect("list committed revisions");
    assert!(revisions
        .iter()
        .any(|revision| revision.revision_id == "osr-1f41358e43a86600"));
    let comparison = project
        .compare_revision("osr-1f41358e43a86600")
        .expect("compare original revision");
    assert!(comparison.stations.is_empty());
    assert!(comparison.controls.is_empty());
    assert!(comparison.lines.is_empty());
    assert!(comparison.services.is_empty());
    assert_eq!(comparison.coordination.len(), 3);
    assert!(comparison
        .coordination
        .iter()
        .all(|issue| issue.kind == "added"));
    assert_eq!(comparison.summary.station_count, 0);
    assert_eq!(comparison.summary.manual_station_count, 0);
}

#[test]
fn project_compilation_is_content_deterministic() {
    let project = samawah_project();
    let first = project.compile().expect("first compilation");
    let second = project.compile().expect("second compilation");
    assert_eq!(first.content_sha256, second.content_sha256);
    assert_eq!(first.revision_id, second.revision_id);
}
