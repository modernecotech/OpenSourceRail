//! Property tests PR1–PR2.

use osr_proto::{
    decode, encode, Direction, Entry, EntryId, Heartbeat, HealthStatus, Payload, Position,
    PositionSource, SectionId, SwitchCommand, SwitchId, SwitchPosition, TrackRef, TrainId,
    TrainPositionReport,
};
use proptest::prelude::*;

fn arb_direction() -> impl Strategy<Value = Direction> {
    prop_oneof![
        Just(Direction::Unspecified),
        Just(Direction::Forward),
        Just(Direction::Reverse),
    ]
}

fn arb_track_ref() -> impl Strategy<Value = TrackRef> {
    (0u64..1000, -1_000_000i64..1_000_000, arb_direction()).prop_map(|(s, o, d)| TrackRef {
        section: SectionId(s),
        offset_mm: o,
        direction: d,
    })
}

fn arb_position() -> impl Strategy<Value = Position> {
    (arb_track_ref(), 0u32..10_000).prop_map(|(r, u)| Position { track_ref: r, uncertainty_mm: u })
}

fn arb_source() -> impl Strategy<Value = PositionSource> {
    prop_oneof![
        Just(PositionSource::Unspecified),
        Just(PositionSource::Gnss),
        Just(PositionSource::Imu),
        Just(PositionSource::Odometry),
        Just(PositionSource::Beacon),
    ]
}

fn arb_train_position() -> impl Strategy<Value = TrainPositionReport> {
    (
        0u64..1_000,
        arb_position(),
        arb_position(),
        0.0f32..120.0,
        arb_direction(),
        prop::collection::vec(arb_source(), 0..=4),
        0u64..1_000_000_000_000,
    )
        .prop_map(|(id, h, t, v, dir, srcs, ts)| TrainPositionReport {
            train_id: TrainId(id),
            head_position: h,
            tail_position: t,
            speed_mps: v,
            speed_uncertainty_mps: 0.1,
            heading: dir,
            contributing_sources: srcs,
            onboard_time_ns: ts,
            pack_state_of_charge: 0.5,
        })
}

fn arb_switch_cmd() -> impl Strategy<Value = SwitchCommand> {
    (0u64..1000, prop_oneof![
        Just(SwitchPosition::Normal),
        Just(SwitchPosition::Reverse),
        Just(SwitchPosition::Transitioning),
        Just(SwitchPosition::Unknown),
    ]).prop_map(|(id, pos)| SwitchCommand {
        switch_id: SwitchId(id),
        requested_position: pos,
        requested_by: osr_proto::EntityId(1),
        lock_until: None,
    })
}

fn arb_payload() -> impl Strategy<Value = Payload> {
    prop_oneof![
        arb_train_position().prop_map(Payload::TrainPositionReport),
        arb_switch_cmd().prop_map(Payload::SwitchCommand),
        Just(Payload::Heartbeat(Heartbeat {
            from_entity: osr_proto::EntityId(0),
            health: HealthStatus::Ok,
            monotonic_seq: 1,
        })),
    ]
}

fn arb_entry() -> impl Strategy<Value = Entry> {
    (0u64..10_000, 0u64..100, 0u64..1_000_000_000_000, arb_payload()).prop_map(
        |(id, term, ts, p)| Entry {
            entry_id: EntryId(id),
            term,
            timestamp_ns: ts,
            leader_signature: vec![],
            payload: p,
        },
    )
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn pr1_round_trip(e in arb_entry()) {
        let bytes = encode(&e);
        let back: Entry = decode(&bytes).unwrap();
        prop_assert_eq!(e, back);
    }

    #[test]
    fn pr2_encoding_deterministic(e in arb_entry()) {
        prop_assert_eq!(encode(&e), encode(&e));
    }
}
