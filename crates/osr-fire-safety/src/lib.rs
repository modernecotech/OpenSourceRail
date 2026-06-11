//! OpenSourceRail fire-detection and suppression controller.
//!
//! SIL-4 monitor that watches aspirating smoke detectors and heat
//! sensors in the three high-risk enclosures — battery bay,
//! traction bay, HVAC plenum — and:
//!
//! 1. Requests an emergency brake via the [O4 brake-apply topic]
//!    ([`osr_brake::BrakeInputs::fire_emergency`]) on any
//!    confirmed fire signal.
//! 2. Optionally commands activation of the bay-specific
//!    suppression system (FM-200, water mist, etc.).
//! 3. Latches an alarm state that only clears after a full
//!    cooldown AND an explicit ground-crew reset.
//!
//! Phase 2c crate of [RFC 0005 §4.3](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # Detection rule (conservative)
//!
//! A fire is declared at a location when *either*:
//!
//! - smoke PPM > `smoke_trip_ppm`, **or**
//! - enclosure temperature > `heat_trip_dc`, **or**
//! - ΔT (enclosure − ambient) > `heat_diff_trip_dc`.
//!
//! The OR combination is deliberately over-sensitive: a rail
//! vehicle fire is a life-safety event where false-positive cost
//! (one aborted service) is dwarfed by false-negative cost
//! (passenger fatalities).
//!
//! # Properties (proptest-verified)
//!
//! - **F1 determinism:** pure.
//! - **F2 emergency iff any detector trips:** the output's
//!   `emergency_requested` is `true` iff at least one location has
//!   a current trip *or* the latch is still active.
//! - **F3 trip latches:** once `emergency_requested` becomes
//!   `true`, it stays `true` until cooldown elapses and a fresh
//!   reset is requested.
//! - **F4 suppression only for tripped locations:** a bay that is
//!   not in trip state does not have its suppression agent
//!   activated (no collateral discharge).
//! - **F5 contactor-safe suppression:** suppression activation
//!   requires `agent_available == true` for that bay; an empty or
//!   depleted reservoir never "activates."

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Enclosures
// ---------------------------------------------------------------------------

/// The three protected bays per RFC 0005 §4.3.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Bay {
    Battery = 0,
    Traction = 1,
    Hvac = 2,
}

impl Bay {
    pub const ALL: [Bay; 3] = [Bay::Battery, Bay::Traction, Bay::Hvac];

    #[must_use]
    pub fn index(self) -> usize {
        self as usize
    }
}

// ---------------------------------------------------------------------------
// Inputs
// ---------------------------------------------------------------------------

/// Per-bay sensor reading.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BaySensors {
    /// Aspirating smoke sensor reading, parts per million.
    pub smoke_ppm: u32,
    /// Enclosure temperature, tenths of °C.
    pub temp_dc: i16,
    /// `true` when the bay's suppression agent reservoir reads
    /// pressurised and full-ish — a precondition for activating it.
    pub agent_available: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct FireInputs {
    pub now_ns: u64,
    pub battery: BaySensors,
    pub traction: BaySensors,
    pub hvac: BaySensors,
    /// Ambient cabin / external temperature, tenths of °C. Used for
    /// differential trip.
    pub ambient_temp_dc: i16,
    /// `true` when a ground-crew reset button has been pressed.
    /// Only honoured after cooldown has elapsed.
    pub reset_requested: bool,
}

impl FireInputs {
    #[must_use]
    pub fn bay(&self, bay: Bay) -> &BaySensors {
        match bay {
            Bay::Battery => &self.battery,
            Bay::Traction => &self.traction,
            Bay::Hvac => &self.hvac,
        }
    }
}

/// Fixed calibration.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct FireParams {
    pub smoke_trip_ppm: u32,
    pub smoke_warn_ppm: u32,
    pub heat_trip_dc: i16,
    pub heat_warn_dc: i16,
    pub heat_diff_trip_dc: i16,
    /// Once tripped, the latch stays engaged for at least this long.
    pub cooldown_ms: u32,
}

impl FireParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            smoke_trip_ppm: 50,
            smoke_warn_ppm: 20,
            heat_trip_dc: 800,      // 80 °C
            heat_warn_dc: 650,      // 65 °C
            heat_diff_trip_dc: 400, // 40 °C over ambient
            cooldown_ms: 60_000,
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum AlarmLevel {
    #[default]
    Nominal,
    Warning,
    Trip,
}

/// Bitmask of tripped bays.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub struct BayMask(pub u8);

impl BayMask {
    #[must_use]
    pub fn empty() -> Self {
        Self(0)
    }
    pub fn insert(&mut self, bay: Bay) {
        self.0 |= 1u8 << (bay as u8);
    }
    #[must_use]
    pub fn contains(self, bay: Bay) -> bool {
        (self.0 >> (bay as u8)) & 1 == 1
    }
    #[must_use]
    pub fn any(self) -> bool {
        self.0 != 0
    }
}

/// Persistent state.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct FireState {
    /// Bays that have ever tripped since the last reset.
    pub latched_tripped: BayMask,
    /// ns-since-epoch at which the latch may be cleared, provided
    /// no bay is currently tripped and a reset has been requested.
    pub cooldown_until_ns: Option<u64>,
}

/// Per-tick output.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct FireOutput {
    pub state: FireState,
    /// Union of this-tick current trips and any latched trips.
    pub emergency_requested: bool,
    pub alarm: AlarmLevel,
    /// Bays currently in trip state (sensor-active, not just latched).
    pub current_tripped: BayMask,
    /// Per-bay suppression activation commands.
    pub activate_battery: bool,
    pub activate_traction: bool,
    pub activate_hvac: bool,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

fn bay_trips(bay: &BaySensors, ambient_dc: i16, p: &FireParams) -> (bool, bool) {
    let smoke_trip = bay.smoke_ppm >= p.smoke_trip_ppm;
    let heat_trip = bay.temp_dc >= p.heat_trip_dc;
    let diff_trip = bay.temp_dc.saturating_sub(ambient_dc) >= p.heat_diff_trip_dc;
    let trip = smoke_trip || heat_trip || diff_trip;

    let smoke_warn = bay.smoke_ppm >= p.smoke_warn_ppm;
    let heat_warn = bay.temp_dc >= p.heat_warn_dc;
    let warn = trip || smoke_warn || heat_warn;
    (trip, warn)
}

/// Evaluate one fire-detection tick. Pure.
#[must_use]
pub fn fire_evaluate(prev: &FireState, inputs: &FireInputs, params: &FireParams) -> FireOutput {
    // --- 1. Per-bay trip evaluation ----------------------------------
    let (b_trip, b_warn) = bay_trips(&inputs.battery, inputs.ambient_temp_dc, params);
    let (t_trip, t_warn) = bay_trips(&inputs.traction, inputs.ambient_temp_dc, params);
    let (h_trip, h_warn) = bay_trips(&inputs.hvac, inputs.ambient_temp_dc, params);

    let mut current_tripped = BayMask::empty();
    if b_trip {
        current_tripped.insert(Bay::Battery);
    }
    if t_trip {
        current_tripped.insert(Bay::Traction);
    }
    if h_trip {
        current_tripped.insert(Bay::Hvac);
    }

    // --- 2. Update latch ---------------------------------------------
    let mut latched_tripped = BayMask(prev.latched_tripped.0 | current_tripped.0);

    // --- 3. Cooldown handling ----------------------------------------
    let mut cooldown_until_ns = prev.cooldown_until_ns;
    if current_tripped.any() {
        let new_deadline = inputs
            .now_ns
            .saturating_add(u64::from(params.cooldown_ms) * 1_000_000);
        cooldown_until_ns = Some(match cooldown_until_ns {
            Some(existing) => existing.max(new_deadline),
            None => new_deadline,
        });
    }

    let cooldown_expired = match cooldown_until_ns {
        Some(until) => inputs.now_ns >= until,
        None => true,
    };
    if inputs.reset_requested && cooldown_expired && !current_tripped.any() {
        cooldown_until_ns = None;
        latched_tripped = BayMask::empty();
    }

    let emergency_requested = latched_tripped.any();

    let alarm = if emergency_requested {
        AlarmLevel::Trip
    } else if b_warn || t_warn || h_warn {
        AlarmLevel::Warning
    } else {
        AlarmLevel::Nominal
    };

    // --- 4. Suppression activation -----------------------------------
    // A bay's agent activates only when that specific bay is currently
    // tripped AND its agent reservoir is available. Latched-but-not-
    // currently-tripped bays do not re-activate their agent (single
    // discharge per event).
    let activate_battery = b_trip && inputs.battery.agent_available;
    let activate_traction = t_trip && inputs.traction.agent_available;
    let activate_hvac = h_trip && inputs.hvac.agent_available;

    FireOutput {
        state: FireState {
            latched_tripped,
            cooldown_until_ns,
        },
        emergency_requested,
        alarm,
        current_tripped,
        activate_battery,
        activate_traction,
        activate_hvac,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn clean_bay() -> BaySensors {
        BaySensors {
            smoke_ppm: 0,
            temp_dc: 250,
            agent_available: true,
        }
    }

    fn clean_inputs(now_ns: u64) -> FireInputs {
        FireInputs {
            now_ns,
            battery: clean_bay(),
            traction: clean_bay(),
            hvac: clean_bay(),
            ambient_temp_dc: 250,
            reset_requested: false,
        }
    }

    #[test]
    fn nominal_operation_is_quiet() {
        let out = fire_evaluate(
            &FireState::default(),
            &clean_inputs(0),
            &FireParams::default_metro(),
        );
        assert!(!out.emergency_requested);
        assert_eq!(out.alarm, AlarmLevel::Nominal);
        assert!(!out.activate_battery);
    }

    #[test]
    fn smoke_in_battery_bay_trips() {
        let p = FireParams::default_metro();
        let mut i = clean_inputs(0);
        i.battery.smoke_ppm = 100;
        let out = fire_evaluate(&FireState::default(), &i, &p);
        assert!(out.emergency_requested);
        assert!(out.current_tripped.contains(Bay::Battery));
        assert!(out.activate_battery);
        assert!(!out.activate_traction);
        assert_eq!(out.alarm, AlarmLevel::Trip);
    }

    #[test]
    fn high_temp_in_traction_bay_trips() {
        let p = FireParams::default_metro();
        let mut i = clean_inputs(0);
        i.traction.temp_dc = 850;
        let out = fire_evaluate(&FireState::default(), &i, &p);
        assert!(out.emergency_requested);
        assert!(out.current_tripped.contains(Bay::Traction));
    }

    #[test]
    fn differential_temp_trips() {
        let p = FireParams::default_metro();
        let mut i = clean_inputs(0);
        i.ambient_temp_dc = 200;
        i.hvac.temp_dc = 620; // 42 °C over ambient > 40 °C threshold
        let out = fire_evaluate(&FireState::default(), &i, &p);
        assert!(out.current_tripped.contains(Bay::Hvac));
    }

    #[test]
    fn trip_latches_through_cooldown() {
        let p = FireParams::default_metro();
        // Trigger.
        let mut i = clean_inputs(0);
        i.battery.smoke_ppm = 200;
        let s0 = fire_evaluate(&FireState::default(), &i, &p).state;
        assert!(s0.cooldown_until_ns.is_some());

        // Sensor clears at t=1s — cooldown (60s) still active.
        let i = clean_inputs(1_000_000_000);
        let out = fire_evaluate(&s0, &i, &p);
        assert!(out.emergency_requested);
        // Reset requested but cooldown not expired — still latched.
        let mut i = clean_inputs(30_000_000_000);
        i.reset_requested = true;
        let out = fire_evaluate(&s0, &i, &p);
        assert!(out.emergency_requested);
        // Reset after cooldown — clears.
        let mut i = clean_inputs(70_000_000_000);
        i.reset_requested = true;
        let out = fire_evaluate(&s0, &i, &p);
        assert!(!out.emergency_requested);
    }

    #[test]
    fn suppression_gated_on_agent_availability() {
        let p = FireParams::default_metro();
        let mut i = clean_inputs(0);
        i.traction.smoke_ppm = 100;
        i.traction.agent_available = false;
        let out = fire_evaluate(&FireState::default(), &i, &p);
        assert!(out.emergency_requested);
        assert!(!out.activate_traction);
    }

    #[test]
    fn determinism() {
        let p = FireParams::default_metro();
        let mut i = clean_inputs(1_234_567);
        i.battery.temp_dc = 500;
        let a = fire_evaluate(&FireState::default(), &i, &p);
        let b = fire_evaluate(&FireState::default(), &i, &p);
        assert_eq!(a, b);
    }
}
