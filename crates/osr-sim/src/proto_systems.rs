//! Deterministic runtime exercise of the canonical track-state wire codec.

use osr_occ::TrainReport as OccTrainReport;
use osr_proto::{
    decode, encode, Direction, Entry, EntryId, Payload, Position, PositionSource, SectionId,
    TrackRef, TrainId, TrainPositionReport,
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default)]
pub struct ProtoSystemsShadow {
    next_entry_id: u64,
    summary: ProtoSystemsSummary,
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProtoSystemsSummary {
    pub frames_encoded: u64,
    pub frames_decoded: u64,
    pub encoded_bytes: u64,
    pub decode_failures: u64,
    pub semantic_mismatches: u64,
}

/// Cross one live TCMS/OCC position report through `osr-proto`. The decoded
/// position, timestamp, speed and SoC become the values delivered to OCC;
/// alarm fields remain on their typed application channel because the current
/// track-state schema deliberately carries position rather than TCMS alarms.
pub fn round_trip_position(
    shadow: &mut ProtoSystemsShadow,
    report: OccTrainReport,
) -> Option<OccTrainReport> {
    shadow.next_entry_id = shadow.next_entry_id.saturating_add(1);
    let direction = Direction::Unspecified;
    let position = Position {
        track_ref: TrackRef {
            section: SectionId(u64::from(report.position_section.unwrap_or(0))),
            offset_mm: 0,
            direction,
        },
        uncertainty_mm: 0,
    };
    let entry = Entry {
        entry_id: EntryId(shadow.next_entry_id),
        term: 1,
        timestamp_ns: report.now_ns,
        leader_signature: Vec::new(),
        payload: Payload::TrainPositionReport(TrainPositionReport {
            train_id: TrainId(u64::from(report.train_id)),
            head_position: position,
            tail_position: position,
            speed_mps: report.speed_mmps as f32 / 1_000.0,
            speed_uncertainty_mps: 0.0,
            heading: direction,
            contributing_sources: vec![PositionSource::Odometry],
            onboard_time_ns: report.now_ns,
            pack_state_of_charge: f32::from(report.soc_ppt) / 1_000.0,
        }),
    };
    let bytes = encode(&entry);
    shadow.summary.frames_encoded = shadow.summary.frames_encoded.saturating_add(1);
    shadow.summary.encoded_bytes = shadow
        .summary
        .encoded_bytes
        .saturating_add(bytes.len() as u64);
    let decoded: Entry = match decode(&bytes) {
        Ok(value) => value,
        Err(_) => {
            shadow.summary.decode_failures = shadow.summary.decode_failures.saturating_add(1);
            return None;
        }
    };
    shadow.summary.frames_decoded = shadow.summary.frames_decoded.saturating_add(1);
    let Payload::TrainPositionReport(position_report) = decoded.payload else {
        shadow.summary.semantic_mismatches = shadow.summary.semantic_mismatches.saturating_add(1);
        return None;
    };
    let decoded_report = OccTrainReport {
        train_id: position_report.train_id.0.min(u64::from(u32::MAX)) as u32,
        now_ns: position_report.onboard_time_ns,
        position_section: {
            let section = position_report
                .head_position
                .track_ref
                .section
                .0
                .min(u64::from(u32::MAX)) as u32;
            (section != 0).then_some(section)
        },
        speed_mmps: (position_report.speed_mps * 1_000.0).round() as i32,
        any_emergency: report.any_emergency,
        worst_alarm: report.worst_alarm,
        soc_ppt: (position_report.pack_state_of_charge * 1_000.0).round() as u16,
    };
    if decoded_report != report {
        shadow.summary.semantic_mismatches = shadow.summary.semantic_mismatches.saturating_add(1);
        return None;
    }
    Some(decoded_report)
}

#[must_use]
pub fn summarise(shadow: &ProtoSystemsShadow) -> ProtoSystemsSummary {
    shadow.summary.clone()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn live_position_shape_round_trips_without_drift() {
        let report = OccTrainReport {
            train_id: 7,
            now_ns: 9_000_000_000,
            position_section: Some(42),
            speed_mmps: 15_000,
            any_emergency: false,
            worst_alarm: 0,
            soc_ppt: 875,
        };
        let mut shadow = ProtoSystemsShadow::default();
        assert_eq!(round_trip_position(&mut shadow, report), Some(report));
        let summary = summarise(&shadow);
        assert_eq!(summary.frames_encoded, 1);
        assert_eq!(summary.frames_decoded, 1);
        assert!(summary.encoded_bytes > 0);
        assert_eq!(summary.decode_failures, 0);
        assert_eq!(summary.semantic_mismatches, 0);
    }
}
