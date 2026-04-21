//! OpenSourceRail onboard Passenger Information System.
//!
//! SIL-0 coordinator. Given train state (speed, next station, distance
//! to stop) and system commands (emergency broadcast), decides:
//!
//! - which message every saloon display should show,
//! - whether an audio announcement should play this tick,
//! - whether CCTV recording is enabled.
//!
//! Phase 2c crate 6 of [RFC 0005 §4.2](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! The crate does **not** render or transmit anything — it produces
//! a compact decision that downstream display / audio agents
//! consume. That separation keeps the decision logic easy to test
//! without having to stub out display hardware.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/// What the saloon displays should show.
#[derive(Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub enum DisplayMessage {
    /// Displays blank (e.g., depot, 110 V off).
    #[default]
    Blank,
    /// Cruising toward next station.
    NextStation { station_id: u32, eta_s: u32 },
    /// Train has stopped at the platform.
    ArrivedAt { station_id: u32 },
    /// Approaching the platform — prompt passengers to prepare.
    Approaching { station_id: u32 },
    /// Safety announcement.
    Emergency { code: u16 },
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum AnnouncementKind {
    #[default]
    None,
    NextStation,
    Arrival,
    Emergency,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum PisMode {
    #[default]
    Off,
    Normal,
    Emergency,
}

// ---------------------------------------------------------------------------
// Inputs / params
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PisInputs {
    pub now_ns: u64,
    pub speed_mmps: i32,
    /// Next (or current) station ID.
    pub station_id: Option<u32>,
    /// Distance in mm to the next stop point. `None` when no stop is
    /// in range.
    pub distance_to_stop_mm: Option<i64>,
    /// True when stopped at a platform (speed ≈ 0).
    pub at_station: bool,
    /// External emergency broadcast command (from OCC or driver).
    pub emergency_broadcast: Option<u16>,
    /// Train-wide 110 V rail state — displays need it.
    pub v110_rail_enabled: bool,
    /// 24 V rail state — CCTV (PoE) and audio amplifier are here.
    pub v24_rail_enabled: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PisParams {
    /// Distance threshold at which we switch from `NextStation` to
    /// `Approaching` and fire the arrival announcement (mm).
    pub approach_distance_mm: i64,
    /// Minimum time between repeated announcements (ms).
    pub announce_cooldown_ms: u32,
    /// Speed below which the train is considered stopped at a
    /// platform (mm/s).
    pub stop_speed_mmps: i32,
}

impl PisParams {
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            approach_distance_mm: 500_000, // 500 m
            announce_cooldown_ms: 15_000,
            stop_speed_mmps: 200,
        }
    }
}

// ---------------------------------------------------------------------------
// State / Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct PisState {
    /// ns-since-epoch at which the next announcement may fire (after
    /// cooldown).
    pub next_announce_allowed_ns: u64,
    /// The kind of announcement most recently emitted, used to avoid
    /// spamming the same message while the station-approach window
    /// is still open.
    pub last_announce_kind: AnnouncementKind,
    /// Station id the last announcement referenced, so the same
    /// approach triggers only once per passage.
    pub last_announce_station: Option<u32>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PisOutput {
    pub state: PisState,
    pub mode: PisMode,
    pub display_message: DisplayMessage,
    pub audio_announcement: AnnouncementKind,
    pub cctv_enabled: bool,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

fn eta_s(distance_mm: i64, speed_mmps: i32) -> u32 {
    if speed_mmps <= 0 || distance_mm <= 0 {
        return 0;
    }
    ((distance_mm / i64::from(speed_mmps.max(1))).max(0)) as u32
}

/// One PIS evaluator tick. Pure.
#[must_use]
pub fn pis_evaluate(prev: &PisState, inputs: &PisInputs, params: &PisParams) -> PisOutput {
    // Emergency broadcast dominates all other state.
    if let Some(code) = inputs.emergency_broadcast {
        let announce = if inputs.now_ns >= prev.next_announce_allowed_ns
            || prev.last_announce_kind != AnnouncementKind::Emergency
        {
            AnnouncementKind::Emergency
        } else {
            AnnouncementKind::None
        };
        let next_allowed = inputs
            .now_ns
            .saturating_add(u64::from(params.announce_cooldown_ms) * 1_000_000);
        return PisOutput {
            state: PisState {
                next_announce_allowed_ns: if announce == AnnouncementKind::Emergency {
                    next_allowed
                } else {
                    prev.next_announce_allowed_ns
                },
                last_announce_kind: announce,
                last_announce_station: prev.last_announce_station,
            },
            mode: PisMode::Emergency,
            display_message: DisplayMessage::Emergency { code },
            audio_announcement: announce,
            cctv_enabled: inputs.v24_rail_enabled,
        };
    }

    // Without a display rail, PIS goes dark but CCTV (24 V) can still run.
    if !inputs.v110_rail_enabled {
        return PisOutput {
            state: *prev,
            mode: PisMode::Off,
            display_message: DisplayMessage::Blank,
            audio_announcement: AnnouncementKind::None,
            cctv_enabled: inputs.v24_rail_enabled,
        };
    }

    // Normal service logic.
    let mut new_state = *prev;
    let (display, announce) = match inputs.station_id {
        None => (DisplayMessage::Blank, AnnouncementKind::None),
        Some(sid) => {
            let stopped = inputs.at_station && inputs.speed_mmps.abs() <= params.stop_speed_mmps;
            if stopped {
                // Arrival — one announcement per station passage.
                let first_arrival_at_this_station = prev.last_announce_station != Some(sid)
                    || prev.last_announce_kind != AnnouncementKind::Arrival;
                let ann = if first_arrival_at_this_station
                    && inputs.now_ns >= prev.next_announce_allowed_ns
                {
                    new_state.next_announce_allowed_ns = inputs
                        .now_ns
                        .saturating_add(u64::from(params.announce_cooldown_ms) * 1_000_000);
                    new_state.last_announce_kind = AnnouncementKind::Arrival;
                    new_state.last_announce_station = Some(sid);
                    AnnouncementKind::Arrival
                } else {
                    AnnouncementKind::None
                };
                (DisplayMessage::ArrivedAt { station_id: sid }, ann)
            } else {
                let d = inputs.distance_to_stop_mm.unwrap_or(i64::MAX);
                if d <= params.approach_distance_mm {
                    let first_approach = prev.last_announce_station != Some(sid)
                        || prev.last_announce_kind != AnnouncementKind::NextStation;
                    let ann = if first_approach
                        && inputs.now_ns >= prev.next_announce_allowed_ns
                    {
                        new_state.next_announce_allowed_ns = inputs
                            .now_ns
                            .saturating_add(u64::from(params.announce_cooldown_ms) * 1_000_000);
                        new_state.last_announce_kind = AnnouncementKind::NextStation;
                        new_state.last_announce_station = Some(sid);
                        AnnouncementKind::NextStation
                    } else {
                        AnnouncementKind::None
                    };
                    (DisplayMessage::Approaching { station_id: sid }, ann)
                } else {
                    let eta = eta_s(d, inputs.speed_mmps);
                    (
                        DisplayMessage::NextStation { station_id: sid, eta_s: eta },
                        AnnouncementKind::None,
                    )
                }
            }
        }
    };

    PisOutput {
        state: new_state,
        mode: PisMode::Normal,
        display_message: display,
        audio_announcement: announce,
        cctv_enabled: inputs.v24_rail_enabled,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn nominal(station: u32, dist: i64, speed: i32) -> PisInputs {
        PisInputs {
            now_ns: 0,
            speed_mmps: speed,
            station_id: Some(station),
            distance_to_stop_mm: Some(dist),
            at_station: false,
            emergency_broadcast: None,
            v110_rail_enabled: true,
            v24_rail_enabled: true,
        }
    }

    #[test]
    fn cruising_shows_next_station() {
        let out = pis_evaluate(&PisState::default(), &nominal(42, 2_000_000, 15_000), &PisParams::light_metro_default());
        assert_eq!(out.mode, PisMode::Normal);
        assert!(matches!(out.display_message, DisplayMessage::NextStation { station_id: 42, .. }));
        assert_eq!(out.audio_announcement, AnnouncementKind::None);
    }

    #[test]
    fn approach_within_threshold_announces() {
        let p = PisParams::light_metro_default();
        let out = pis_evaluate(&PisState::default(), &nominal(42, 400_000, 15_000), &p);
        assert!(matches!(out.display_message, DisplayMessage::Approaching { station_id: 42 }));
        assert_eq!(out.audio_announcement, AnnouncementKind::NextStation);
    }

    #[test]
    fn arrived_announces_once() {
        let p = PisParams::light_metro_default();
        let mut i = nominal(42, 0, 0);
        i.at_station = true;
        let first = pis_evaluate(&PisState::default(), &i, &p);
        assert!(matches!(first.display_message, DisplayMessage::ArrivedAt { station_id: 42 }));
        assert_eq!(first.audio_announcement, AnnouncementKind::Arrival);

        // Second tick at the same station: cooldown suppresses repeat.
        let mut i2 = i;
        i2.now_ns = 1_000_000_000;
        let second = pis_evaluate(&first.state, &i2, &p);
        assert_eq!(second.audio_announcement, AnnouncementKind::None);
    }

    #[test]
    fn emergency_broadcast_dominates() {
        let p = PisParams::light_metro_default();
        let mut i = nominal(42, 2_000_000, 15_000);
        i.emergency_broadcast = Some(7);
        let out = pis_evaluate(&PisState::default(), &i, &p);
        assert_eq!(out.mode, PisMode::Emergency);
        assert_eq!(out.display_message, DisplayMessage::Emergency { code: 7 });
        assert_eq!(out.audio_announcement, AnnouncementKind::Emergency);
    }

    #[test]
    fn v110_down_blanks_displays_keeps_cctv() {
        let p = PisParams::light_metro_default();
        let mut i = nominal(42, 1_000_000, 15_000);
        i.v110_rail_enabled = false;
        let out = pis_evaluate(&PisState::default(), &i, &p);
        assert_eq!(out.display_message, DisplayMessage::Blank);
        assert_eq!(out.mode, PisMode::Off);
        assert!(out.cctv_enabled);
    }

    #[test]
    fn v24_down_disables_cctv() {
        let p = PisParams::light_metro_default();
        let mut i = nominal(42, 1_000_000, 15_000);
        i.v24_rail_enabled = false;
        let out = pis_evaluate(&PisState::default(), &i, &p);
        assert!(!out.cctv_enabled);
    }

    #[test]
    fn determinism() {
        let p = PisParams::light_metro_default();
        let i = nominal(42, 800_000, 15_000);
        let a = pis_evaluate(&PisState::default(), &i, &p);
        let b = pis_evaluate(&PisState::default(), &i, &p);
        assert_eq!(a, b);
    }
}
