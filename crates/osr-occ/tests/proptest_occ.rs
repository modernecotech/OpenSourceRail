//! Property tests OCC1–OCC4.

use osr_occ::{
    occ_evaluate, HoldKey, IncidentSeverity, IncidentState, NewIncident, OccInputs, OccState,
    TrainReport,
};
use proptest::prelude::*;

fn arb_report() -> impl Strategy<Value = TrainReport> {
    (
        0u32..10,
        0u64..1_000_000_000_000,
        0u32..50,
        -30_000i32..30_000,
    )
        .prop_map(|(tid, now, sec, speed)| TrainReport {
            train_id: tid,
            now_ns: now,
            position_section: Some(sec),
            speed_mmps: speed,
            any_emergency: false,
            worst_alarm: 0,
            soc_ppt: 800,
        })
}

fn arb_severity() -> impl Strategy<Value = IncidentSeverity> {
    prop_oneof![
        Just(IncidentSeverity::Info),
        Just(IncidentSeverity::Warning),
        Just(IncidentSeverity::Major),
        Just(IncidentSeverity::Critical),
    ]
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn occ1_determinism(
        reports in prop::collection::vec(arb_report(), 0..10),
        incidents in prop::collection::vec((arb_severity(), 0u32..5), 0..3),
        now in 0u64..10_000_000_000_000,
    ) {
        let new_incidents: Vec<_> = incidents.iter().map(|(s, l)| NewIncident {
            severity: *s,
            line_id: *l,
            description: "x".into(),
        }).collect();
        let inputs = OccInputs {
            now_ns: now,
            train_reports: reports,
            new_incidents,
            close_incident_ids: vec![],
            manual_holds_set: vec![],
            manual_holds_clear: vec![],
        };
        let a = occ_evaluate(&OccState::default(), &inputs);
        let b = occ_evaluate(&OccState::default(), &inputs);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn occ2_stale_update_suppressed(
        old_now in 1_000_000_000u64..1_000_000_000_000,
        delta in 1_000_000u64..500_000_000_000,
    ) {
        let mut prev = OccState::default();
        let e = osr_occ::RosterEntry {
            train_id: 1,
            last_seen_ns: old_now,
            position_section: Some(99),
            speed_mmps: 15_000,
            any_emergency: false,
            worst_alarm: 0,
            soc_ppt: 800,
        };
        prev.roster.insert(1, e);
        let stale = TrainReport {
            train_id: 1,
            now_ns: old_now.saturating_sub(delta),
            position_section: Some(1),
            speed_mmps: 0,
            any_emergency: false,
            worst_alarm: 0,
            soc_ppt: 800,
        };
        let inputs = OccInputs {
            now_ns: old_now,
            train_reports: vec![stale],
            ..Default::default()
        };
        let out = occ_evaluate(&prev, &inputs);
        let entry = out.state.roster.get(&1).unwrap();
        prop_assert_eq!(entry.last_seen_ns, old_now);
        prop_assert_eq!(entry.position_section, Some(99));
    }

    #[test]
    fn occ3_incident_state_matches_closed_ns(
        severity in arb_severity(),
        line in 0u32..10,
    ) {
        let out = occ_evaluate(
            &OccState::default(),
            &OccInputs {
                now_ns: 1,
                new_incidents: vec![NewIncident {
                    severity,
                    line_id: line,
                    description: "x".into(),
                }],
                ..Default::default()
            },
        );
        let id = out.opened_incident_ids[0];
        let inc = &out.state.incidents[&id];
        prop_assert_eq!(inc.state, IncidentState::Open);
        prop_assert!(inc.closed_ns.is_none());

        // Close it.
        let out = occ_evaluate(
            &out.state,
            &OccInputs {
                now_ns: 10,
                close_incident_ids: vec![id],
                ..Default::default()
            },
        );
        let inc = &out.state.incidents[&id];
        prop_assert_eq!(inc.state, IncidentState::Closed);
        prop_assert!(inc.closed_ns.is_some());
    }

    #[test]
    fn occ4_critical_auto_holds_line(line in 0u32..100) {
        let out = occ_evaluate(
            &OccState::default(),
            &OccInputs {
                now_ns: 1,
                new_incidents: vec![NewIncident {
                    severity: IncidentSeverity::Critical,
                    line_id: line,
                    description: "fire".into(),
                }],
                ..Default::default()
            },
        );
        let key = HoldKey { line_id: line, station_id: 0, heading: 0 };
        prop_assert!(out.state.holds.contains_key(&key));
    }
}
