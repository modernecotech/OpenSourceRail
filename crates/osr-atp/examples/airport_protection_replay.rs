//! Offline corrected Airport corridor fixture. Outputs are simulated decisions only.
use osr_atp::{atp_evaluate, envelope::BrakeProfile, TrainState};
use osr_core::{
    BrakingCurve, ConsistDescriptor, Direction, EntityId, EntryId, Line, Network, Position,
    Section, SectionId, Station, StationId, TrackRef, TrainClass, TrainId,
};
use osr_interlocking::{
    compute_self_ma,
    log::{
        Entry, EntryPayload, IntrusionState, PositionSource, SectionIntrusion, TrainPositionReport,
        TrainRegistration,
    },
};
use serde::Deserialize;
use serde_json::json;
use std::io::{self, Read};

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    chainages_mm: Vec<i64>,
    length_mm: u32,
    loaded_mass_kg: u32,
    approach_speed_mmps: i32,
    after_coast_speed_mmps: i32,
    coast_distance_mm: i64,
    net_deceleration_mmps2: i32,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut raw = String::new();
    io::stdin().take(16384).read_to_string(&mut raw)?;
    let input: Input = serde_json::from_str(&raw)?;
    assert!(input.chainages_mm.len() == 6 && input.chainages_mm[0] == 0);
    assert!(input
        .chainages_mm
        .windows(2)
        .all(|w| w[1] - w[0] > 1_000_000));
    assert!(input.length_mm > 0 && input.length_mm < 200_000);
    assert!(input.loaded_mass_kg > 0 && input.approach_speed_mmps > 0);
    assert!(input.after_coast_speed_mmps >= input.approach_speed_mmps);
    assert!((0..90_000).contains(&input.coast_distance_mm));
    let profile = BrakeProfile::try_new(input.net_deceleration_mmps2, 0)
        .expect("positive brake deceleration");
    let consist = ConsistDescriptor {
        train_class: TrainClass::Engineering,
        car_count: 6,
        length_mm: input.length_mm,
        mass_kg: input.loaded_mass_kg,
        max_speed_mps: input.approach_speed_mmps as f32 / 1000.0,
        braking: BrakingCurve {
            service: vec![],
            emergency: vec![],
            reaction_time_ms: 0,
        },
        service_accel_mps2: 0.0,
        battery_capacity_wh: 0,
    };
    let mut net = Network::default();
    let mut ids = Vec::new();
    let mut lengths = Vec::new();
    for (i, chainage) in input.chainages_mm.iter().enumerate() {
        let id = StationId::new(i as u64 + 1);
        net.stations.insert(
            id,
            Station {
                id,
                name: format!("Airport-{i:02}"),
                charging_power_kw: 0,
                dwell_seconds: 0,
                is_terminal: i == 0 || i == 5,
                is_depot: false,
            },
        );
        if i > 0 {
            let segment = SectionId::new(i as u64);
            let length = chainage - input.chainages_mm[i - 1];
            net.sections.insert(
                segment,
                Section {
                    id: segment,
                    from_station: StationId::new(i as u64),
                    to_station: id,
                    length_mm: length as u64,
                    max_speed_mps: consist.max_speed_mps.into(),
                },
            );
            ids.push(segment);
            lengths.push(length);
        }
    }
    net.lines.push(Line {
        name: "Forward study fixture".into(),
        stations: (1..=6).map(StationId::new).collect(),
        forward_sections: ids.clone(),
        reverse_sections: vec![],
        is_ring: false,
    });
    let now = 1_000_000_000;
    let follower = TrainId::new(101);
    let leader = TrainId::new(102);
    let reference = |section, offset_mm| TrackRef {
        section,
        offset_mm,
        direction: Direction::Forward,
    };
    let position = |section, offset| Position {
        track_ref: reference(section, offset),
        uncertainty_mm: 0,
    };
    let mut events = Vec::new();
    let mut append = |payload| {
        events.push(Entry {
            entry_id: EntryId::new(events.len() as u64 + 1),
            term: 1,
            timestamp_ns: now,
            payload,
        });
    };
    for &section in &ids {
        append(EntryPayload::SectionIntrusion(SectionIntrusion {
            section,
            state: IntrusionState::Clear,
            issued_by: EntityId(1),
            observed_at_ns: now,
        }));
    }
    // The approach, occupancy and uncertainty are deliberately synthetic.
    let head = lengths[3] - 450_000 + input.coast_distance_mm;
    for (train, section, offset, velocity) in [
        (
            follower,
            ids[3],
            head,
            i64::from(input.after_coast_speed_mmps),
        ),
        (leader, ids[4], 330_000, 0),
    ] {
        append(EntryPayload::TrainRegistration(TrainRegistration {
            train_id: train,
            consist: consist.clone(),
            initial_position: position(section, offset),
        }));
        append(EntryPayload::TrainPositionReport(TrainPositionReport {
            train_id: train,
            head_position: position(section, offset),
            tail_position: position(section, offset - i64::from(input.length_mm)),
            speed_mmps: velocity,
            speed_uncertainty_mmps: 0,
            heading: Direction::Forward,
            contributing_sources: vec![PositionSource::Odometry],
            onboard_time_ns: now,
            pack_soc_ppt: 800,
        }));
    }
    let clear_count = events.len() - 2;
    let state = TrainState {
        train_id: follower,
        head: reference(ids[3], head),
        speed_mmps: input.after_coast_speed_mmps,
        speed_uncertainty_mmps: 0,
        position_uncertainty_mm: 0,
    };
    let clear = compute_self_ma(follower, &events[..clear_count], &net, now);
    let occupied = compute_self_ma(follower, &events, &net, now);
    let leading_ma = compute_self_ma(leader, &events, &net, now);
    let unknown = compute_self_ma(follower, &events[..ids.len()], &net, now);
    let normal = atp_evaluate(&state, &clear, &profile, &net, now);
    let near = atp_evaluate(&state, &occupied, &profile, &net, now);
    let uncertain_state = TrainState {
        position_uncertainty_mm: 5_000,
        speed_uncertainty_mmps: 100,
        ..state.clone()
    };
    let uncertain = atp_evaluate(&uncertain_state, &occupied, &profile, &net, now);
    let expired = atp_evaluate(&state, &clear, &profile, &net, clear.valid_until_ns);
    let mismatch = atp_evaluate(&state, &leading_ma, &profile, &net, now);
    let unknown_result = atp_evaluate(&state, &unknown, &profile, &net, now);
    use osr_atp::TriggerReason::*;
    assert_eq!(clear.end.section, ids[4]);
    assert_eq!(occupied.end.section, ids[3]);
    assert!(normal.is_release() && near.is_emergency() && uncertain.is_emergency());
    assert!(uncertain.envelope_mmps < near.envelope_mmps);
    assert_eq!(expired.reason, MaExpired);
    assert_eq!(mismatch.reason, MaTrainMismatch);
    assert_eq!(unknown_result.reason, NoKnownPosition);
    println!(
        "{}",
        json!({
            "clear_ahead": {"authority": clear, "atp": normal},
            "leader_in_next_section": {"authority": occupied, "atp": near},
            "leader_with_position_and_speed_uncertainty": {"authority": occupied, "atp": uncertain},
            "authority_expired": {"authority": clear, "atp": expired},
            "wrong_train_authority": {"authority": leading_ma, "atp": mismatch},
            "unknown_position": {"authority": unknown, "atp": unknown_result}
        })
    );
    Ok(())
}
