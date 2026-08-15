//! Sensor input types and calibration.
//!
//! In a real deployment the producers of these types are:
//! - [`SensorTick::wheel_pulses`] — wheel tachometer pulse counter
//!   (Hall-effect or optical), sampled at the ATP tick cadence.
//! - [`GnssFix`] — onboard GNSS receiver, projected onto the track
//!   graph by a map-matcher that sits between the receiver and this
//!   crate.
//! - [`BaliseFix`] — `osr-balise` wayside reader publishes a
//!   detection event over TCN-E when the onboard antenna passes a
//!   balise; that event is translated into a [`BaliseFix`] here.
//!
//! The odometer itself is transport-agnostic: it consumes a ready
//! [`SensorTick`] and does not know how the fields were acquired.

use osr_core::TrackRef;
use serde::{Deserialize, Serialize};

/// Opaque balise identifier. Stable across the network; assigned at
/// commissioning. Stored as a `u32` for compatness on the wire.
///
/// This type is defined locally until the `osr-balise` wayside crate
/// lands (RFC 0005 §4.6), at which point it migrates into `osr-core`.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Ord, PartialOrd, Serialize, Deserialize)]
pub struct BaliseId(pub u32);

impl BaliseId {
    #[must_use]
    pub const fn new(id: u32) -> Self {
        Self(id)
    }
}

/// Where the head-position estimate came from on a given tick.
///
/// Mirrors `osr_interlocking::log::PositionSource` but re-declared
/// here so the odometry crate doesn't take a hard dependency on the
/// interlocking log's enum layout for diagnostic purposes. A
/// caller-side mapping to the log type is trivial.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum PositionSource {
    /// Wheel-tachometer dead reckoning only.
    WheelTachometer,
    /// GNSS-based correction (may be combined with wheel on the same tick).
    Gnss,
    /// Balise-based absolute fix (may be combined with wheel on the same tick).
    Balise,
}

/// Calibration of the wheel tachometer and uncertainty growth model.
///
/// Held constant across ticks; loaded at boot from a depot-provisioned
/// configuration blob.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct OdomCalibration {
    /// Tachometer pulses per physical metre of track travelled.
    /// Typical values: 500–5000 depending on wheel diameter and
    /// encoder resolution. Must be ≥ 1.
    pub pulses_per_meter: u32,
    /// Growth rate of position uncertainty per mm of distance
    /// travelled on wheel dead-reckoning, expressed in parts-per-
    /// million. Example: 10_000 ppm = 1 % of distance becomes
    /// additional uncertainty.
    pub wheel_slip_ppm: u32,
    /// Constant uncertainty added per tick regardless of travel
    /// distance (accounts for clock jitter, quantisation). Typical
    /// 1–5 mm.
    pub uncertainty_floor_per_tick_mm: u32,
    /// Minimum uncertainty the odometer will ever report. Even a
    /// freshly-consumed balise has a finite precision; this is the
    /// floor. Typical 50–100 mm.
    pub min_uncertainty_mm: u32,
    /// Upper clamp on uncertainty. Beyond this value the caller is
    /// expected to treat the position as effectively unknown (the
    /// reported value is saturated at `max_uncertainty_mm`).
    pub max_uncertainty_mm: u32,
}

impl OdomCalibration {
    /// Sensible defaults for a light-metro tachometer.
    ///
    /// Tuned for 0.8 m wheel diameter + 1024 pulses/revolution:
    /// `1024 / (π · 0.8) ≈ 407` pulses per metre, rounded up to 410.
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            pulses_per_meter: 410,
            wheel_slip_ppm: 5_000, // 0.5 % slip budget
            uncertainty_floor_per_tick_mm: 2,
            min_uncertainty_mm: 50,
            max_uncertainty_mm: 50_000, // 50 m before caller should declare unknown
        }
    }

    /// Construct from a physical wheel specification.
    ///
    /// `wheel_circumference_m` is the wheel's rolling circumference
    /// (π × diameter) and `pulses_per_revolution` is the encoder
    /// resolution. Both are typically documented in the consist's
    /// maintenance record.
    ///
    /// Safe-side: rounds `pulses_per_meter` *up*, overestimating
    /// pulse count per physical distance, which makes distance per
    /// pulse smaller and in turn makes integrated distance *shorter*
    /// than physical — the conservative choice for a forward-bounded
    /// safety case.
    #[must_use]
    pub fn from_wheel_spec(
        wheel_circumference_m: f32,
        pulses_per_revolution: u32,
        wheel_slip_ppm: u32,
    ) -> Self {
        let pulses_per_meter =
            ((pulses_per_revolution as f32) / wheel_circumference_m.max(1e-3)).ceil() as u32;
        Self {
            pulses_per_meter: pulses_per_meter.max(1),
            wheel_slip_ppm,
            uncertainty_floor_per_tick_mm: 2,
            min_uncertainty_mm: 50,
            max_uncertainty_mm: 50_000,
        }
    }
}

/// Absolute-position fix from a wayside balise.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BaliseFix {
    pub balise_id: BaliseId,
    /// The known surveyed position of the balise on the track graph.
    pub position: TrackRef,
    /// Reported uncertainty of the balise fix, in millimetres.
    /// Typically ≤ 100 mm for a passive EuroBalise-class transponder.
    pub uncertainty_mm: u32,
}

/// Soft position fix from a GNSS receiver, already map-matched onto
/// the track graph by an upstream projector.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct GnssFix {
    pub projected: TrackRef,
    /// Half-width uncertainty of the projected point, in millimetres.
    /// Typical 2 000–10 000 mm for a consumer-grade module; 500–2 000
    /// for an RTK-corrected receiver.
    pub uncertainty_mm: u32,
}

/// One tick of sensor input to the odometer.
///
/// `timestamp_ns` is the sampling instant (not necessarily "now");
/// `odom_step` treats it as the authoritative time-of-measurement.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SensorTick {
    pub timestamp_ns: u64,
    /// Signed pulse count since the previous tick. Positive values
    /// mean motion in the head's current heading direction; negative
    /// values mean roll-back. Clamped at the boundary of the current
    /// section in v1 (see `advance_along_track`).
    pub wheel_pulses: i32,
    pub gnss: Option<GnssFix>,
    pub balise: Option<BaliseFix>,
}
