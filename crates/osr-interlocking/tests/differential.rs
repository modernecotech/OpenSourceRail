//! RFC 0004 M4 — differential test against a Python reference interpreter.
//!
//! For a random log prefix + network, both the Rust MA computer
//! (`osr_interlocking::compute_self_ma`) and the Python reference
//! interpreter (`tools/reference-ma/`) must produce byte-identical
//! `MovementAuthority` JSON. A divergence is a failure in one of the
//! two implementations.
//!
//! The Python interpreter is invoked as a subprocess (`python3 -m
//! reference_ma`); if the interpreter or the package is unavailable
//! the test is skipped rather than failed, so contributors without
//! Python can still run the rest of the suite.
//!
//! Corpus seeds live under `tests/fuzz-corpus/`. Additions to the
//! corpus should come from cases the proptest or sim has found
//! problematic, so that regressions stay caught cheaply.
//!
//! Skipped when `OSR_SKIP_PY_DIFF=1` is set — the CI uses this on
//! runners without Python3.

use std::env;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use osr_core::{
    BrakingCurve, ConsistDescriptor, Direction, EntityId, EntryId, Line, Network, Position,
    RouteId, Section, SectionId, Station, StationId, SwitchId, TrackRef, TrainClass, TrainId,
};
use osr_interlocking::log::{
    Confidence, Entry, EntryPayload, PositionSource, RestrictionReason, RouteGrant,
    SpeedRestriction, SwitchObservation, SwitchPosition, TrainPositionReport,
    TrainRegistration,
};
use osr_interlocking::{compute_self_ma, MovementAuthority};
use proptest::prelude::*;
use serde::Serialize;

#[derive(Serialize)]
struct Case<'a> {
    network: &'a Network,
    entries: &'a [Entry],
    train_id: TrainId,
    now_ns: u64,
}

/// Returns the `tools/reference-ma/src` directory relative to the
/// crate manifest, or `None` if it can't be located. The differential
/// tests use this to set `PYTHONPATH` on the subprocess.
fn reference_ma_src() -> Option<PathBuf> {
    // CARGO_MANIFEST_DIR points at crates/osr-interlocking/.
    let manifest = env::var("CARGO_MANIFEST_DIR").ok()?;
    let p = Path::new(&manifest).join("../../tools/reference-ma/src");
    if p.exists() {
        p.canonicalize().ok()
    } else {
        None
    }
}

/// Skip the test if Python3 isn't on PATH, the reference_ma package
/// isn't importable, or the environment variable opts us out.
fn skip_if_py_unavailable() -> Option<PathBuf> {
    if env::var("OSR_SKIP_PY_DIFF").is_ok() {
        eprintln!("skip: OSR_SKIP_PY_DIFF set");
        return None;
    }
    let src = reference_ma_src()?;
    // Probe: can we import reference_ma under this PYTHONPATH?
    let probe = Command::new("python3")
        .arg("-c")
        .arg("import reference_ma")
        .env("PYTHONPATH", &src)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    match probe {
        Ok(s) if s.success() => Some(src),
        _ => {
            eprintln!("skip: python3 + reference_ma not available");
            None
        }
    }
}

fn run_python(src: &Path, case_json: &str) -> MovementAuthority {
    let mut child = Command::new("python3")
        .arg("-m")
        .arg("reference_ma")
        .env("PYTHONPATH", src)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn python3");
    child
        .stdin
        .as_mut()
        .unwrap()
        .write_all(case_json.as_bytes())
        .unwrap();
    let out = child.wait_with_output().expect("python3 output");
    if !out.status.success() {
        panic!(
            "python reference_ma failed ({}): {}",
            out.status,
            String::from_utf8_lossy(&out.stderr)
        );
    }
    let stdout = String::from_utf8(out.stdout).expect("utf8 stdout");
    serde_json::from_str(stdout.trim()).unwrap_or_else(|e| {
        panic!("could not parse Python MA output as MovementAuthority: {e}\nraw: {stdout}")
    })
}

fn reference_3car() -> ConsistDescriptor {
    ConsistDescriptor {
        train_class: TrainClass::LightMetro,
        car_count: 3,
        length_mm: 65_000,
        mass_kg: 195_000,
        max_speed_mps: 22.0,
        braking: BrakingCurve {
            service: vec![(0.0, 1.1), (20.0, 1.0), (28.0, 0.9)],
            emergency: vec![(0.0, 1.5), (20.0, 1.4), (28.0, 1.2)],
            reaction_time_ms: 400,
        },
        service_accel_mps2: 1.0,
        has_pantograph: true,
        battery_capacity_wh: 900_000,
    }
}

fn simple_linear_network() -> Network {
    // Same fixture as the Python test suite: 4 stations, 3 forward
    // and 3 reverse sections, each 1 km.
    let mut net = Network::default();
    for i in 1..=4u64 {
        net.stations.insert(
            StationId::new(i),
            Station {
                id: StationId::new(i),
                name: format!("S{i}"),
                charging_power_kw: 0,
                dwell_seconds: 0,
                is_terminal: i == 1 || i == 4,
                is_depot: false,
            },
        );
    }
    let mut fwd = Vec::new();
    let mut rev = Vec::new();
    for i in 0..3u64 {
        let f = SectionId::new(1000 + i);
        let r = SectionId::new(2000 + i);
        net.sections.insert(
            f,
            Section {
                id: f,
                from_station: StationId::new(i + 1),
                to_station: StationId::new(i + 2),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        net.sections.insert(
            r,
            Section {
                id: r,
                from_station: StationId::new(i + 2),
                to_station: StationId::new(i + 1),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        fwd.push(f);
        rev.push(r);
    }
    net.lines.push(Line {
        name: "L".into(),
        stations: (1..=4u64).map(StationId::new).collect(),
        forward_sections: fwd,
        reverse_sections: rev,
        is_ring: false,
    });
    net
}

fn registration_entry(
    entry_id: u64,
    ts_ns: u64,
    train_id: u64,
    section: u64,
    offset_mm: i64,
) -> Entry {
    Entry {
        entry_id: EntryId::new(entry_id),
        term: 1,
        timestamp_ns: ts_ns,
        payload: EntryPayload::TrainRegistration(TrainRegistration {
            train_id: TrainId::new(train_id),
            consist: reference_3car(),
            initial_position: Position {
                track_ref: TrackRef {
                    section: SectionId::new(section),
                    offset_mm,
                    direction: Direction::Forward,
                },
                uncertainty_mm: 0,
            },
        }),
    }
}

/// 4-station ring fixture. Mirrors the ring network the Python twin
/// builds in its unit tests — four sections of 1 km each, forward and
/// reverse, wrapping back to station 1.
fn simple_ring_network() -> Network {
    let mut net = Network::default();
    for i in 1..=4u64 {
        net.stations.insert(
            StationId::new(i),
            Station {
                id: StationId::new(i),
                name: format!("R{i}"),
                charging_power_kw: 0,
                dwell_seconds: 0,
                is_terminal: false,
                is_depot: false,
            },
        );
    }
    let mut fwd = Vec::new();
    let mut rev = Vec::new();
    for i in 0..4u64 {
        let f = SectionId::new(3000 + i);
        let r = SectionId::new(4000 + i);
        let from_idx = i + 1;
        let to_idx = if i + 2 > 4 { 1 } else { i + 2 };
        net.sections.insert(
            f,
            Section {
                id: f,
                from_station: StationId::new(from_idx),
                to_station: StationId::new(to_idx),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        net.sections.insert(
            r,
            Section {
                id: r,
                from_station: StationId::new(to_idx),
                to_station: StationId::new(from_idx),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        fwd.push(f);
        rev.push(r);
    }
    net.lines.push(Line {
        name: "Ring".into(),
        stations: (1..=4u64).map(StationId::new).collect(),
        forward_sections: fwd,
        reverse_sections: rev,
        is_ring: true,
    });
    net
}

fn switch_observation_entry(
    entry_id: u64,
    ts_ns: u64,
    switch_id: u64,
    position: SwitchPosition,
    confidence: Confidence,
) -> Entry {
    Entry {
        entry_id: EntryId::new(entry_id),
        term: 1,
        timestamp_ns: ts_ns,
        payload: EntryPayload::SwitchObservation(SwitchObservation {
            switch_id: SwitchId::new(switch_id),
            observed_position: position,
            confidence,
            observed_at_ns: ts_ns,
        }),
    }
}

fn route_grant_entry(
    entry_id: u64,
    ts_ns: u64,
    route_id: u64,
    train_id: u64,
    locked_sections: Vec<u64>,
) -> Entry {
    Entry {
        entry_id: EntryId::new(entry_id),
        term: 1,
        timestamp_ns: ts_ns,
        payload: EntryPayload::RouteGrant(RouteGrant {
            route_id: RouteId::new(route_id),
            train_id: TrainId::new(train_id),
            locked_switches: vec![],
            locked_sections: locked_sections.into_iter().map(SectionId::new).collect(),
            expires_at_ns: ts_ns.saturating_add(10_000_000_000),
        }),
    }
}

fn speed_restriction_entry(
    entry_id: u64,
    ts_ns: u64,
    section: u64,
    max_speed_mmps: i64,
    reason: RestrictionReason,
) -> Entry {
    Entry {
        entry_id: EntryId::new(entry_id),
        term: 1,
        timestamp_ns: ts_ns,
        payload: EntryPayload::SpeedRestriction(SpeedRestriction {
            section: SectionId::new(section),
            from_offset_mm: 0,
            to_offset_mm: 1_000_000,
            max_speed_mmps,
            reason,
            effective_from_ns: 0,
            effective_until_ns: None,
            issued_by: EntityId::new(1),
        }),
    }
}

fn position_entry(
    entry_id: u64,
    ts_ns: u64,
    train_id: u64,
    section: u64,
    head_offset_mm: i64,
) -> Entry {
    Entry {
        entry_id: EntryId::new(entry_id),
        term: 1,
        timestamp_ns: ts_ns,
        payload: EntryPayload::TrainPositionReport(TrainPositionReport {
            train_id: TrainId::new(train_id),
            head_position: Position {
                track_ref: TrackRef {
                    section: SectionId::new(section),
                    offset_mm: head_offset_mm,
                    direction: Direction::Forward,
                },
                uncertainty_mm: 0,
            },
            tail_position: Position {
                track_ref: TrackRef {
                    section: SectionId::new(section),
                    offset_mm: 0,
                    direction: Direction::Forward,
                },
                uncertainty_mm: 0,
            },
            speed_mmps: 15_000,
            speed_uncertainty_mmps: 500,
            heading: Direction::Forward,
            contributing_sources: vec![PositionSource::Gnss, PositionSource::Odometry],
            onboard_time_ns: ts_ns,
            pack_soc_ppt: 1000,
        }),
    }
}

fn cross_check(network: &Network, entries: &[Entry], train_id: TrainId, now_ns: u64) {
    let src = match skip_if_py_unavailable() {
        Some(p) => p,
        None => return,
    };
    let case = Case {
        network,
        entries,
        train_id,
        now_ns,
    };
    let case_json = serde_json::to_string(&case).expect("serialise case");
    let py_ma = run_python(&src, &case_json);
    let rs_ma: MovementAuthority = compute_self_ma(train_id, entries, network, now_ns);
    assert_eq!(rs_ma, py_ma, "MA divergence.\nRust: {rs_ma:#?}\nPy:   {py_ma:#?}");
}

#[test]
fn smoke_no_registration_fail_restrictive() {
    let net = simple_linear_network();
    cross_check(&net, &[], TrainId::new(42), 0);
}

#[test]
fn smoke_single_train_full_extension() {
    let net = simple_linear_network();
    let entries = vec![registration_entry(1, 0, 1, 1000, 65_000)];
    cross_check(&net, &entries, TrainId::new(1), 0);
}

#[test]
fn smoke_other_train_blocks() {
    let net = simple_linear_network();
    let entries = vec![
        registration_entry(1, 0, 1, 1000, 65_000),
        registration_entry(2, 0, 2, 1001, 65_000),
        position_entry(3, 0, 2, 1001, 65_000),
    ];
    cross_check(&net, &entries, TrainId::new(1), 0);
}

#[test]
fn smoke_ring_network() {
    let net = simple_ring_network();
    let entries = vec![registration_entry(1, 0, 1, 3000, 65_000)];
    cross_check(&net, &entries, TrainId::new(1), 0);
}

#[test]
fn smoke_switch_observation_in_log() {
    let net = simple_linear_network();
    let entries = vec![
        registration_entry(1, 0, 1, 1000, 65_000),
        // Switch observations currently have no blocking effect on the
        // forward chain in osr-interlocking's v1 — they update state,
        // and the Python twin folds them identically. Exercising them
        // here catches any serde-shape or state-application drift.
        switch_observation_entry(2, 100, 99, SwitchPosition::Normal, Confidence::Locked),
        switch_observation_entry(3, 200, 99, SwitchPosition::Unknown, Confidence::Unknown),
    ];
    cross_check(&net, &entries, TrainId::new(1), 500);
}

#[test]
fn smoke_route_grant_blocks_another_trains_ma() {
    let net = simple_linear_network();
    // Train 1 at the start of section 1000. Train 2 holds a route
    // grant locking section 1001 — train 1's MA must stop at the end
    // of 1000.
    let entries = vec![
        registration_entry(1, 0, 1, 1000, 0),
        route_grant_entry(2, 10, 7, 2, vec![1001]),
    ];
    cross_check(&net, &entries, TrainId::new(1), 1_000);
}

#[test]
fn smoke_speed_restriction_reflected_in_ma() {
    let net = simple_linear_network();
    let entries = vec![
        registration_entry(1, 0, 1, 1000, 65_000),
        speed_restriction_entry(
            2,
            100,
            1000,
            15_000,
            RestrictionReason::Weather,
        ),
    ];
    cross_check(&net, &entries, TrainId::new(1), 500);
}

/// Which miscellaneous entry to append. Each variant exercises a
/// different `apply_entry` branch in both the Rust and Python twins.
#[derive(Copy, Clone, Debug)]
enum ExtraEntry {
    SwitchObs { switch_id: u64, normal: bool, locked: bool },
    RouteGrant { train: u64, section: u64 },
    SpeedRestriction { section: u64, max_mmps: i64 },
}

fn arb_extra() -> impl Strategy<Value = ExtraEntry> {
    prop_oneof![
        (1u64..=5, any::<bool>(), any::<bool>())
            .prop_map(|(s, n, l)| ExtraEntry::SwitchObs { switch_id: s, normal: n, locked: l }),
        (1u64..=3, 1000u64..=1002)
            .prop_map(|(t, s)| ExtraEntry::RouteGrant { train: t, section: s }),
        (1000u64..=1002, 1_000i64..=20_000)
            .prop_map(|(s, v)| ExtraEntry::SpeedRestriction { section: s, max_mmps: v }),
    ]
}

/// Random log-prefix generator: one registration per unique train id
/// (1..=3), one position report per train, and 0..=4 miscellaneous
/// entries (switch observations, route grants, speed restrictions).
/// The miscellaneous entries exercise every `apply_entry` branch
/// relevant to the MA computer — switches (state only), route grants
/// (blocking), speed restrictions (collected in the output MA).
fn arb_entries() -> impl Strategy<Value = Vec<Entry>> {
    let per_train = (1u64..=3u64, 0u64..3u64, 70_000i64..=900_000i64);
    let trains = prop::collection::vec(per_train, 1..=3);
    let extras = prop::collection::vec(arb_extra(), 0..=4);

    (trains, extras).prop_map(|(trains, extras)| {
        let mut entries = Vec::new();
        let mut next_id: u64 = 1;
        let mut seen = std::collections::BTreeSet::new();

        for (train, section_idx, head_offset) in &trains {
            if seen.insert(*train) {
                entries.push(registration_entry(next_id, 0, *train, 1000, 65_000));
                next_id += 1;
                let section = 1000 + *section_idx;
                entries.push(position_entry(next_id, 1_000_000, *train, section, *head_offset));
                next_id += 1;
            }
        }

        let mut ts: u64 = 2_000_000;
        for (i, extra) in extras.iter().enumerate() {
            let ts_i = ts + (i as u64) * 1_000;
            match *extra {
                ExtraEntry::SwitchObs { switch_id, normal, locked } => {
                    let pos = if normal {
                        SwitchPosition::Normal
                    } else {
                        SwitchPosition::Reverse
                    };
                    let conf = if locked {
                        Confidence::Locked
                    } else {
                        Confidence::Observed
                    };
                    entries.push(switch_observation_entry(next_id, ts_i, switch_id, pos, conf));
                }
                ExtraEntry::RouteGrant { train, section } => {
                    entries.push(route_grant_entry(
                        next_id,
                        ts_i,
                        10 + next_id,
                        train,
                        vec![section],
                    ));
                }
                ExtraEntry::SpeedRestriction { section, max_mmps } => {
                    entries.push(speed_restriction_entry(
                        next_id,
                        ts_i,
                        section,
                        max_mmps,
                        RestrictionReason::Temporary,
                    ));
                }
            }
            next_id += 1;
        }
        ts = ts.saturating_add(1_000_000);
        let _ = ts;

        entries
    })
}

proptest! {
    #![proptest_config(ProptestConfig {
        // Each round-trip spawns a Python subprocess — keep the case
        // budget modest. The goal is "any structural divergence"; the
        // proof of no-divergence is Kani's territory.
        cases: 16,
        .. ProptestConfig::default()
    })]

    #[test]
    fn prop_rust_and_python_agree_linear(entries in arb_entries()) {
        let net = simple_linear_network();
        cross_check(&net, &entries, TrainId::new(1), 2_000_000_000);
    }
}

/// Ring-network flavour of the same proptest — the forward chain
/// wraps, so any off-by-one on wrap handling surfaces here. Uses
/// a separate generator bound to the ring's section ids (3000..=3003).
fn arb_entries_ring() -> impl Strategy<Value = Vec<Entry>> {
    let per_train = (1u64..=3u64, 0u64..4u64, 70_000i64..=900_000i64);
    prop::collection::vec(per_train, 1..=3).prop_map(|trains| {
        let mut entries = Vec::new();
        let mut next_id: u64 = 1;
        let mut seen = std::collections::BTreeSet::new();

        for (train, section_idx, head_offset) in &trains {
            if seen.insert(*train) {
                entries.push(registration_entry(next_id, 0, *train, 3000, 65_000));
                next_id += 1;
                let section = 3000 + *section_idx;
                entries.push(position_entry(next_id, 1_000_000, *train, section, *head_offset));
                next_id += 1;
            }
        }
        entries
    })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 8, .. ProptestConfig::default() })]

    #[test]
    fn prop_rust_and_python_agree_ring(entries in arb_entries_ring()) {
        let net = simple_ring_network();
        cross_check(&net, &entries, TrainId::new(1), 2_000_000_000);
    }
}
