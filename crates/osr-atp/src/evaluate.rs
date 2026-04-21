//! Top-level ATP evaluation.
//!
//! [`atp_evaluate`] is the single public entry point. Given the
//! current train state, the most recent MA, the consist description,
//! the network topology, and the current time, it returns an
//! [`AtpOutcome`] the caller applies to the brake bus.
//!
//! All decisions are fail-restrictive: any input that cannot be
//! validated produces [`BrakeCommand::Emergency`] with a descriptive
//! [`TriggerReason`].

use osr_core::{ConsistDescriptor, Network, TrackRef};
use osr_interlocking::{MovementAuthority, MAX_MA_DISTANCE_MM};
use serde::{Deserialize, Serialize};

use crate::envelope::{max_safe_speed_mmps, DecelTable};
use crate::state::TrainState;

/// Speed in excess of the envelope beyond which ATP trips emergency
/// brake outright. Service brake would arrest the train before the
/// emergency margin is reached under nominal response; exceeding this
/// implies either a sensor fault or a brake failure.
///
/// 500 mm/s (0.5 m/s) is tight enough to catch a genuine overspeed
/// before it matters and loose enough not to chatter against sensor
/// noise at the mm/s uncertainty levels odometry delivers.
pub const OVERSPEED_EMERGENCY_MARGIN_MMPS: i32 = 500;

/// When the margin (envelope speed − measured speed) falls below this
/// value, ATP applies service brake proportional to the gap. Above it,
/// `BrakeCommand::Release` is issued.
pub const SERVICE_BRAKE_MARGIN_MMPS: i32 = 1_500;

/// Commanded brake state.
///
/// The brake crate subscribes to this enum. A transition from
/// [`Release`](Self::Release) to [`Emergency`](Self::Emergency) in
/// consecutive ticks is a valid trajectory; nothing in the ATP
/// prevents it.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum BrakeCommand {
    /// No brake application. Motor torque may be requested by `osr-ato`.
    Release,
    /// Service brake, scaled 0..=1000 in parts-per-thousand of
    /// maximum service effort.
    Service(u16),
    /// Emergency brake. Full friction brake + traction cut.
    Emergency,
}

/// Human-readable reason the ATP produced its output. Diagnostic only.
///
/// A consumer of the brake bus must respond to [`BrakeCommand`], not
/// to [`TriggerReason`] — the reason is intended for event recorders,
/// maintenance diagnosis, and driver-facing messages.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum TriggerReason {
    /// Train is within the envelope; no brake action needed.
    WithinEnvelope,
    /// Train is approaching the envelope; service brake applied.
    EnvelopeApproach,
    /// MA has expired (not renewed within [`osr_interlocking::MA_VALIDITY_WINDOW_NS`]).
    MaExpired,
    /// MA does not carry a known head position (fail-restrictive MA).
    NoKnownPosition,
    /// MA is for a different train than the state reports.
    MaTrainMismatch,
    /// Train's head has advanced past the MA's end, or is on a section
    /// not on the forward chain from its own head.
    HeadPastMaEnd,
    /// Measured speed exceeds the envelope by more than
    /// [`OVERSPEED_EMERGENCY_MARGIN_MMPS`].
    Overspeed,
}

/// Full result of an ATP evaluation.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AtpOutcome {
    pub command: BrakeCommand,
    pub reason: TriggerReason,
    /// Envelope speed at the train's current head position, in mm/s.
    /// `None` on fail-restrictive trips where the envelope wasn't
    /// reached in the decision path.
    pub envelope_mmps: Option<i32>,
    /// Distance to MA end, in mm (uncertainty-adjusted). `None` when
    /// the decision short-circuited before computing it.
    pub distance_to_end_mm: Option<i64>,
}

impl AtpOutcome {
    #[must_use]
    pub fn is_emergency(&self) -> bool {
        matches!(self.command, BrakeCommand::Emergency)
    }
    #[must_use]
    pub fn is_release(&self) -> bool {
        matches!(self.command, BrakeCommand::Release)
    }
    #[must_use]
    pub fn is_service(&self) -> bool {
        matches!(self.command, BrakeCommand::Service(_))
    }
}

fn emergency(reason: TriggerReason) -> AtpOutcome {
    AtpOutcome {
        command: BrakeCommand::Emergency,
        reason,
        envelope_mmps: None,
        distance_to_end_mm: None,
    }
}

/// Evaluate the ATP for the given train state and MA.
///
/// Pure function. See the crate-level safety properties A1–A7 in
/// [`crate`] docs.
#[must_use]
pub fn atp_evaluate(
    state: &TrainState,
    ma: &MovementAuthority,
    consist: &ConsistDescriptor,
    network: &Network,
    now_ns: u64,
) -> AtpOutcome {
    // A4: MA must be for this train.
    if ma.train_id != state.train_id {
        return emergency(TriggerReason::MaTrainMismatch);
    }

    // A3: MA must carry a known position.
    if !ma.has_known_position {
        return emergency(TriggerReason::NoKnownPosition);
    }

    // A2: MA must not be expired. Strict `>=` — equality already
    // means the window has just elapsed.
    if now_ns >= ma.valid_until_ns {
        return emergency(TriggerReason::MaExpired);
    }

    // A5: compute distance from head to MA end along the topology.
    let Some(raw_distance_mm) = distance_to_ma_end(network, state.head, ma.end) else {
        return emergency(TriggerReason::HeadPastMaEnd);
    };

    // Safe-side: subtract position uncertainty. The head might be
    // `position_uncertainty_mm` further along than measured.
    let distance_to_end_mm =
        raw_distance_mm.saturating_sub(i64::from(state.position_uncertainty_mm));

    if distance_to_end_mm <= 0 {
        return AtpOutcome {
            command: BrakeCommand::Emergency,
            reason: TriggerReason::HeadPastMaEnd,
            envelope_mmps: None,
            distance_to_end_mm: Some(distance_to_end_mm),
        };
    }

    // A6: compute envelope speed and compare.
    let decel = DecelTable::from_emergency(consist);
    let envelope = max_safe_speed_mmps(distance_to_end_mm, &decel);

    // Safe-side speed: add uncertainty (the train might really be
    // going this much faster than measured).
    let measured = state
        .speed_mmps
        .saturating_add(i32::try_from(state.speed_uncertainty_mmps).unwrap_or(i32::MAX));

    let margin = envelope.saturating_sub(measured);

    // Partition into three regions: Release, Service, Emergency.
    if margin < -OVERSPEED_EMERGENCY_MARGIN_MMPS {
        AtpOutcome {
            command: BrakeCommand::Emergency,
            reason: TriggerReason::Overspeed,
            envelope_mmps: Some(envelope),
            distance_to_end_mm: Some(distance_to_end_mm),
        }
    } else if margin < SERVICE_BRAKE_MARGIN_MMPS {
        // Linear ramp across the (-OVERSPEED_EMERGENCY_MARGIN_MMPS,
        // +SERVICE_BRAKE_MARGIN_MMPS) band, clamped to 0..=1000 ppt.
        let span = SERVICE_BRAKE_MARGIN_MMPS + OVERSPEED_EMERGENCY_MARGIN_MMPS;
        let into_band = (SERVICE_BRAKE_MARGIN_MMPS - margin).clamp(0, span);
        let ppt = ((i64::from(into_band) * 1000) / i64::from(span)).clamp(0, 1000) as u16;
        AtpOutcome {
            command: BrakeCommand::Service(ppt),
            reason: TriggerReason::EnvelopeApproach,
            envelope_mmps: Some(envelope),
            distance_to_end_mm: Some(distance_to_end_mm),
        }
    } else {
        AtpOutcome {
            command: BrakeCommand::Release,
            reason: TriggerReason::WithinEnvelope,
            envelope_mmps: Some(envelope),
            distance_to_end_mm: Some(distance_to_end_mm),
        }
    }
}

/// Forward-chain distance from `head` to `end` (mm).
///
/// Returns `None` if `end` is not reachable by going forward from
/// `head` within [`MAX_MA_DISTANCE_MM`], or if the head is already
/// past `end` on the same section.
fn distance_to_ma_end(network: &Network, head: TrackRef, end: TrackRef) -> Option<i64> {
    // Same-section fast path.
    if head.section == end.section && head.direction == end.direction {
        let d = end.offset_mm - head.offset_mm;
        return if d >= 0 { Some(d) } else { None };
    }

    // Walk forward, summing section lengths. The forward_chain helper
    // is bounded by MAX_MA_DISTANCE_MM (2 km); MAs cannot end farther
    // ahead than that at the moment they were computed, and the train
    // is always behind or at the MA's origin.
    let chain = osr_interlocking::forward_chain(network, head, MAX_MA_DISTANCE_MM);
    let mut chain_iter = chain.iter().copied();
    let first = chain_iter.next()?;
    debug_assert_eq!(first, head.section);

    // Distance to the far end of the head section.
    let head_len = i64::try_from(network.section(head.section).length_mm).ok()?;
    let mut dist = head_len - head.offset_mm;
    if dist < 0 {
        return None;
    }

    for sid in chain_iter {
        if sid == end.section {
            return Some(dist + end.offset_mm);
        }
        let sec_len = i64::try_from(network.section(sid).length_mm).ok()?;
        dist = dist.saturating_add(sec_len);
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{ConsistDescriptor, Direction, Line, Section, SectionId, Station, StationId, TrainId};
    use osr_interlocking::{MovementAuthority, MA_VALIDITY_WINDOW_NS};

    fn net_3_sections() -> Network {
        let mut net = Network::default();
        for i in 1..=4 {
            net.stations.insert(
                StationId::new(i),
                Station {
                    id: StationId::new(i),
                    name: format!("S{i}"),
                    charging_power_kw: 0,
                    dwell_seconds: 0,
                    is_terminal: false,
                    is_depot: false,
                },
            );
        }
        let mut fwd = vec![];
        let mut rev = vec![];
        for i in 0..3 {
            let f = SectionId::new(1000 + i);
            let r = SectionId::new(2000 + i);
            net.sections.insert(f, Section {
                id: f,
                from_station: StationId::new((i as u64) + 1),
                to_station: StationId::new((i as u64) + 2),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            });
            net.sections.insert(r, Section {
                id: r,
                from_station: StationId::new((i as u64) + 2),
                to_station: StationId::new((i as u64) + 1),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            });
            fwd.push(f);
            rev.push(r);
        }
        net.lines.push(Line {
            name: "L".into(),
            stations: (1..=4).map(StationId::new).collect(),
            forward_sections: fwd,
            reverse_sections: rev,
            is_ring: false,
        });
        net
    }

    fn state_stopped_at(section: u64, offset: i64) -> TrainState {
        TrainState {
            train_id: TrainId::new(7),
            head: TrackRef {
                section: SectionId::new(section),
                offset_mm: offset,
                direction: Direction::Forward,
            },
            speed_mmps: 0,
            speed_uncertainty_mmps: 0,
            position_uncertainty_mm: 0,
        }
    }

    fn nominal_ma(end_section: u64, end_offset: i64, now_ns: u64) -> MovementAuthority {
        MovementAuthority {
            train_id: TrainId::new(7),
            end: TrackRef {
                section: SectionId::new(end_section),
                offset_mm: end_offset,
                direction: Direction::Forward,
            },
            applicable_restrictions: vec![],
            valid_until_ns: now_ns + MA_VALIDITY_WINDOW_NS,
            derived_from_entry_id: None,
            has_known_position: true,
        }
    }

    #[test]
    fn a2_expired_ma_trips_emergency() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        let state = state_stopped_at(1000, 0);
        let mut ma = nominal_ma(1001, 1_000_000, 0);
        ma.valid_until_ns = 1_000;
        let out = atp_evaluate(&state, &ma, &consist, &net, 2_000);
        assert!(out.is_emergency());
        assert_eq!(out.reason, TriggerReason::MaExpired);
    }

    #[test]
    fn a3_unknown_position_trips_emergency() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        let state = state_stopped_at(1000, 0);
        let mut ma = nominal_ma(1001, 1_000_000, 0);
        ma.has_known_position = false;
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        assert!(out.is_emergency());
        assert_eq!(out.reason, TriggerReason::NoKnownPosition);
    }

    #[test]
    fn a4_train_mismatch_trips_emergency() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        let state = state_stopped_at(1000, 0);
        let mut ma = nominal_ma(1001, 1_000_000, 0);
        ma.train_id = TrainId::new(9);
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        assert!(out.is_emergency());
        assert_eq!(out.reason, TriggerReason::MaTrainMismatch);
    }

    #[test]
    fn a5_head_past_ma_end_trips_emergency() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        // Head at 900 m into section 1000, MA end at 500 m into section 1000.
        let state = state_stopped_at(1000, 900_000);
        let ma = nominal_ma(1000, 500_000, 0);
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        assert!(out.is_emergency());
        assert_eq!(out.reason, TriggerReason::HeadPastMaEnd);
    }

    #[test]
    fn a6_overspeed_trips_emergency() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        // Head at 0 into section 1000, MA end at 100 m into section 1000.
        // Very short distance, so envelope speed is low. Measured 30 m/s.
        let mut state = state_stopped_at(1000, 0);
        state.speed_mmps = 30_000;
        let ma = nominal_ma(1000, 100_000, 0);
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        assert!(out.is_emergency(), "{out:?}");
        assert_eq!(out.reason, TriggerReason::Overspeed);
    }

    #[test]
    fn nominal_release_within_envelope() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        // Head at 0, MA end 2 km ahead. Train moving at 10 m/s.
        let mut state = state_stopped_at(1000, 0);
        state.speed_mmps = 10_000;
        let ma = nominal_ma(1001, 1_000_000, 0); // 1 km into section 1001, 2 km ahead
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        assert!(out.is_release(), "{out:?}");
        assert_eq!(out.reason, TriggerReason::WithinEnvelope);
    }

    #[test]
    fn service_brake_in_approach_band() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        // Short remaining distance; pick speed just below envelope
        // so we're in the approach band but not emergency.
        let mut state = state_stopped_at(1000, 0);
        let ma = nominal_ma(1000, 500_000, 0); // 500 m ahead
        let decel = DecelTable::from_emergency(&consist);
        let env = max_safe_speed_mmps(500_000, &decel);
        state.speed_mmps = env - 500; // inside service band
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        assert!(out.is_service(), "{out:?}");
        assert_eq!(out.reason, TriggerReason::EnvelopeApproach);
    }

    #[test]
    fn a1_determinism() {
        let net = net_3_sections();
        let consist = ConsistDescriptor::reference_3car();
        let mut state = state_stopped_at(1000, 100_000);
        state.speed_mmps = 15_000;
        let ma = nominal_ma(1001, 500_000, 0);
        let a = atp_evaluate(&state, &ma, &consist, &net, 1_000);
        let b = atp_evaluate(&state, &ma, &consist, &net, 1_000);
        assert_eq!(a, b);
    }
}
