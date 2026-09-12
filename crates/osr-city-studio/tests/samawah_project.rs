use std::path::Path;

use osr_city_studio::CityProject;

fn samawah_project() -> CityProject {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../cities/workspaces/samawah");
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

#[test]
fn assignment_requires_service_for_the_whole_period_including_after_midnight() {
    fn copy_tree(source: &Path, target: &Path) {
        std::fs::create_dir_all(target).unwrap();
        for entry in std::fs::read_dir(source).unwrap() {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.is_dir() {
                copy_tree(&path, &target.join(entry.file_name()));
            } else {
                std::fs::copy(path, target.join(entry.file_name())).unwrap();
            }
        }
    }
    let source = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../cities/workspaces/samawah");
    let temporary = tempfile::Builder::new()
        .prefix(".passenger-test-")
        .tempdir_in(source.parent().unwrap())
        .unwrap();
    copy_tree(&source, temporary.path());
    let service = temporary.path().join("services/service-plan.toml");
    let service_text = std::fs::read_to_string(&service).unwrap();
    std::fs::write(&service, service_text.replace("23:30", "02:00")).unwrap();
    let demand = temporary.path().join("demand/od-matrix.toml");
    let text = std::fs::read_to_string(&demand).unwrap();
    std::fs::write(&demand, format!("{text}\n[[periods]]\nid = \"after-midnight\"\nname = \"After midnight\"\nday_type = \"weekday\"\nfrom = \"01:00\"\nto = \"01:59\"\n\n[[periods]]\nid = \"crosses-close\"\nname = \"Crosses closing\"\nday_type = \"weekday\"\nfrom = \"01:30\"\nto = \"03:30\"\n")).unwrap();
    let mut project = CityProject::load(temporary.path()).unwrap();
    let snapshot = project.compile().unwrap();
    let stations: Vec<_> = snapshot
        .stations
        .iter()
        .filter(|s| s.line == "line-1")
        .collect();
    for period in ["after-midnight", "crosses-close"] {
        project
            .create_demand_flow(osr_city_studio::model::DemandFlowCreate {
                period: period.into(),
                origin_station: stations[0].id.clone(),
                destination_station: stations[stations.len() - 1].id.clone(),
                passengers_per_hour: 100,
            })
            .unwrap();
    }
    let snapshot = project.compile().unwrap();
    let valid = snapshot
        .demand_metrics
        .iter()
        .find(|m| m.period == "after-midnight")
        .unwrap();
    let gap = snapshot
        .demand_metrics
        .iter()
        .find(|m| m.period == "crosses-close")
        .unwrap();
    assert!(valid.capacity_pphpd > 0 && valid.journey_minutes.is_some());
    assert_eq!(gap.status, "unavailable");
    assert!(gap.route_stations.is_empty());
    assert!(!snapshot
        .passenger_assignment
        .sections
        .iter()
        .any(|s| s.period == "crosses-close"));
}
