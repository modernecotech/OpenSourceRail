//! OpenSourceRail onboard odometry & position fusion.
//!
//! This crate fuses the onboard sensor suite — wheel tachometers,
//! GNSS (outdoors only), and wayside balise detections — into a
//! single authoritative `OdomState` describing the train's head
//! position, speed, and associated uncertainties. The output is
//! consumed directly by [`osr_atp`] and, at a lower cadence, serialised
//! into `TrainPositionReport` entries for the consensus log.
//!
//! This crate is **Phase 2a, crate 2** of RFC 0005 — the second
//! onboard SBC crate. Where [`osr_atp`] is the safety *enforcer*,
//! [`osr_odometry`] is the safety *sensor-fusion*: both are SIL-4.
//!
//! # API shape
//!
//! The core API is a single pure function — [`odom_step`] — taking
//! the previous [`OdomState`], the odometer's fixed [`OdomCalibration`],
//! a [`SensorTick`] of raw readings, and the network topology. It
//! returns the updated [`OdomState`].
//!
//! Because the function is pure, the caller holds the state across
//! ticks. This makes every invocation trivially mockable, repeatable,
//! and amenable to property-based testing.
//!
//! # Fusion priority
//!
//! Each tick is resolved in a strict priority order, most-trusted
//! first:
//!
//! 1. **Balise fix** — absolute position at a known wayside point.
//!    Resets uncertainty to the balise's reported precision
//!    (typically ≤ 100 mm). Sets `contributing_sources` to `Balise`.
//! 2. **GNSS fix** — soft correction if tighter than current
//!    uncertainty. If the reported GNSS uncertainty is strictly less
//!    than the previous position uncertainty, the position is
//!    replaced by the GNSS estimate and uncertainty tightens. If
//!    wider, GNSS is ignored. Sets `contributing_sources` to `Gnss`.
//! 3. **Wheel dead reckoning** — always applied. Integrates signed
//!    pulse count into forward distance via `cal.pulses_per_meter`
//!    and advances the head along the topology by that distance.
//!    Uncertainty grows by `cal.wheel_slip_ppm · distance / 1e6 +
//!    cal.uncertainty_floor_per_tick_mm`. Sets `contributing_sources`
//!    to `WheelTachometer`.
//!
//! The three mechanisms compose: a tick with both a balise and a
//! wheel count applies the wheel advance first (to project forward
//! from the prior state) and then snaps to the balise (which will
//! typically be a small correction). In practice a balise detection
//! occurs at a single instant and the snap effectively overwrites the
//! dead-reckoned position; the uncertainty tightens accordingly.
//!
//! # Safety properties (targeted)
//!
//! These anchor future Kani harnesses per RFC 0005 §7:
//!
//! - **O1 (determinism):** [`odom_step`] is a pure function; identical
//!   inputs produce byte-identical outputs.
//! - **O2 (forward non-regression):** non-negative wheel pulses, no
//!   balise or GNSS correction, same direction → head's *section* is
//!   the same or later in the forward chain, and offset within a
//!   section is non-decreasing until the section boundary is crossed.
//! - **O3 (uncertainty monotone without fix):** in the absence of a
//!   balise or tightening GNSS fix, position uncertainty never
//!   decreases tick to tick.
//! - **O4 (balise resets uncertainty):** a valid balise fix sets
//!   `position_uncertainty_mm` to the balise's reported value,
//!   regardless of prior uncertainty.
//! - **O5 (GNSS soft-correction is conservative):** a GNSS fix whose
//!   reported uncertainty exceeds the current uncertainty is ignored;
//!   uncertainty never loosens as a result of a GNSS tick.
//!
//! # Out of v1 scope
//!
//! - **IMU integration.** An accelerometer-based short-term estimate
//!   of speed is a candidate for v2 (improves speed estimate during
//!   brief wheel-slip). The current [`SensorTick`] does not carry IMU
//!   data; adding it is additive.
//! - **Wheel-slip / anti-slide detection.** Belongs in the traction
//!   control and brake firmware (`osr-traction`, `osr-brake`). Here
//!   wheel pulses are trusted subject to uncertainty growth.
//! - **Full Kalman filter.** The simple priority-based fusion is
//!   sufficient for urban rail duty cycles where balise spacing is
//!   100–500 m and GNSS is only occasionally available. A Kalman
//!   upgrade is a drop-in replacement behind the same API.
//! - **Backward-motion bookkeeping across section boundaries.** A
//!   train with negative wheel pulses that would roll off the start
//!   of its section is clipped to offset 0 and uncertainty grows.
//!   Deliberate reversing is handled at a higher level by flipping
//!   the train's direction before rolling.
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 (SIL-4):
//!
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only safety path (mm, mm/s, mm/s², ns, ppm). The one
//!   float boundary is [`OdomCalibration::from_wheel_spec`], which
//!   converts a human-authored wheel circumference (m) and pulses/rev
//!   into an integer `pulses_per_meter`.
//! - All public types `Debug + Clone + PartialEq`.
//! - No allocation on the hot path ([`odom_step`] allocates only for
//!   the forward-chain walk, which is bounded).

#![forbid(unsafe_code)]

pub mod fusion;
pub mod sensors;
pub mod state;

#[cfg(kani)]
pub mod kani_proofs;

pub use fusion::{advance_along_track, odom_step};
pub use sensors::{BaliseFix, BaliseId, GnssFix, OdomCalibration, PositionSource, SensorTick};
pub use state::OdomState;
