//! Property tests for osr-balise.

use osr_balise::{
    audit_sightings, BaliseId, BaliseRecord, BaliseRegistry, BaliseType, SightingEvent,
    SightingReport, SurveyedPosition,
};
use proptest::prelude::*;

fn make_record(id: u32) -> BaliseRecord {
    BaliseRecord {
        id: BaliseId(id),
        balise_type: BaliseType::Passive,
        position: SurveyedPosition { section_id: 1, offset_mm: 100 },
        installed_ns: 0,
        last_seen_ns: Some(0),
        stale_after_ns: u64::MAX,
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn unknown_id_yields_unknown_event(id in 0u32..1000) {
        let reg = BaliseRegistry::default();
        let ev = audit_sightings(
            &reg,
            &[SightingReport {
                id: BaliseId(id),
                reported_position: SurveyedPosition { section_id: 1, offset_mm: 0 },
                now_ns: 0,
            }],
            0,
        );
        let is_unknown = ev.iter().any(|e| matches!(e, SightingEvent::Unknown { .. }));
        prop_assert!(is_unknown);
    }

    #[test]
    fn matching_yields_seen(id in 0u32..1000) {
        let mut reg = BaliseRegistry::default();
        reg.insert(make_record(id));
        let ev = audit_sightings(
            &reg,
            &[SightingReport {
                id: BaliseId(id),
                reported_position: SurveyedPosition { section_id: 1, offset_mm: 100 },
                now_ns: 1,
            }],
            1,
        );
        let is_seen = ev.iter().any(|e| matches!(e, SightingEvent::Seen { .. }));
        prop_assert!(is_seen);
    }

    #[test]
    fn determinism(id in 0u32..1000, now in 0u64..1_000_000) {
        let mut reg = BaliseRegistry::default();
        reg.insert(make_record(id));
        let reports = vec![SightingReport {
            id: BaliseId(id),
            reported_position: SurveyedPosition { section_id: 1, offset_mm: 100 },
            now_ns: now,
        }];
        let a = audit_sightings(&reg, &reports, now);
        let b = audit_sightings(&reg, &reports, now);
        prop_assert_eq!(a, b);
    }
}
