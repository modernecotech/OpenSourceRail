//! OpenSourceRail onboard obstacle detection (SIL-4, GoA 4).
//!
//! Per [RFC 0015](../../docs/rfcs/0015-driverless-operation.md) every
//! trainset ships as an unattended (GoA 4) system. Without a driver's
//! eyes, an independent sensor suite carries the burden of detecting
//! obstacles in the train's path. This crate is the SIL-4 evaluator
//! that fuses those sensor readings into a single `ObstacleVerdict`
//! per tick, and runs on the dedicated T-OBS host class.
//!
//! The sensor suite is **multi-physics by design** — a failure of
//! any single sensor class never produces a `Clear` verdict on its
//! own:
//!
//! - **Ultrasonic belt** (4 transducers, 0.2–20 m): primary close-
//!   range safety, covers platform-gap and depot envelopes.
//! - **Solid-state LIDAR** (5–200 m): primary mid-range 3D.
//! - **mmWave radar** (5–200 m): all-weather validation; stays
//!   effective through the dust and heat haze that degrades LIDAR.
//! - **Stereo camera** (0–100 m): classification only; *not* in the
//!   safety-primary path. Informs severity (`CrawlOnly` vs
//!   `EmergencyBrake`).
//!
//! The core API is a single pure function — [`evaluate`] — taking an
//! immutable [`SensorFrame`] plus the current speed + MA-end distance
//! and returning [`ObstacleOutcome`]. All I/O (reading sensors,
//! commanding the brake) is delegated to the caller. This matches
//! the pattern established by [`osr_atp::atp_evaluate`] and keeps the
//! safety-critical logic testable, deterministic, and Kani-ready.
//!
//! # Safety properties (O1–O5)
//!
//! - **O1 (obstacle → restrictive verdict):** if any safety-primary
//!   sensor reports a detection inside the stopping-distance envelope
//!   the verdict is at least [`ObstacleVerdict::CrawlOnly`], and is
//!   [`ObstacleVerdict::EmergencyBrake`] unless a confident camera
//!   classification identifies light debris.
//! - **O2 (stale data → EB):** if any safety-primary sensor's last-
//!   update age exceeds [`MAX_SENSOR_STALE_MS`] the verdict is
//!   [`ObstacleVerdict::EmergencyBrake`].
//! - **O3 (channel disagreement → EB):** if the 2oo2 cross-check
//!   with the peer channel disagrees on `Clear`, the verdict is
//!   [`ObstacleVerdict::EmergencyBrake`] (fail-restrictive).
//! - **O4a (all long-range down + fast → EB):** if every long-
//!   range sensor (LIDAR *and* radar) is offline and the train is
//!   above [`ULTRASONIC_MAX_SPEED_MMPS`], the verdict is
//!   [`ObstacleVerdict::EmergencyBrake`].
//! - **O4b (LIDAR degraded → restricted speed):** if LIDAR is
//!   offline or stale (independent of radar state), the verdict is
//!   at least [`ObstacleVerdict::RestrictedSpeed`] — ATO caps the
//!   trainset at 40 km/h so it stays inside the ultrasonic safety
//!   envelope even when the primary long-range channel is down.
//!   Radar alone is not sufficient to clear this restriction.
//! - **O5 (monotone severity):** removing a detection or raising
//!   sensor freshness never moves the verdict in the less-
//!   restrictive direction.
//!
//! Property O1–O5 anchor the Kani harnesses under `#[cfg(kani)]` in
//! the `kani_proofs` module. None are yet formally verified; all are
//! exercised by the proptests under `tests/`.
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 + RFC 0015 §10, this crate follows the SIL-4
//! conventions:
//!
//! - `#![forbid(unsafe_code)]` at crate root.
//! - Integer-only safety path (millimetres, mm/s, milliseconds).
//! - All public types `Debug + Clone + PartialEq`.
//! - No allocation on the hot path: `evaluate` is strictly
//!   stack-based, operates on fixed-size sensor frames, and never
//!   returns a heap-owned value.

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod sensors;
pub mod verdict;

#[cfg(kani)]
pub mod kani_proofs;

pub use evaluate::{evaluate, ObstacleOutcome, TriggerReason};
pub use sensors::{
    CameraDetection, LidarDetection, RadarDetection, SensorFrame, UltrasonicChannel,
    MAX_SENSOR_STALE_MS, ULTRASONIC_CHANNELS,
};
pub use verdict::{
    ObstacleClass, ObstacleVerdict, CRAWL_SPEED_MMPS, RESTRICTED_SPEED_MMPS,
    ULTRASONIC_MAX_SPEED_MMPS,
};
