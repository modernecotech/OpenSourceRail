//! OpenSourceRail wayside track-intrusion detection (SIL-4).
//!
//! Per [RFC 0016](../../docs/rfcs/0016-wayside-track-intrusion.md),
//! GoA 4 deployments need a proactive wayside check on every ROW
//! section: if intrusion (person, animal, debris, vehicle) is
//! detected between trains, the interlocking withholds MA so the
//! next train never arrives at the obstacle.
//!
//! This crate is the SIL-4 evaluator running on the W-SBC. It reads
//! one [`WaysideSensorFrame`] per tick per section and emits an
//! [`IntrusionVerdict`]: `Clear` / `Unknown` / `Present`. The
//! evaluator is pure — all I/O (sensor acquisition, consensus log
//! write, operator alarm) is the caller's job.
//!
//! The evaluator pairs with the onboard `osr-obstacle-detect`
//! evaluator (RFC 0015): the two cover different time horizons.
//! Wayside is *proactive* (before a train enters the section) and
//! onboard is *reactive* (once the train is approaching the obstacle).
//!
//! # Safety properties (I1–I5)
//!
//! - **I1 (in-profile → Present):** any LIDAR or radar detection
//!   inside the ±1500 mm rail profile forces [`IntrusionVerdict::Present`].
//! - **I2 (stale → Unknown):** if any safety-primary sensor frame
//!   is stale beyond [`MAX_SENSOR_STALE_MS`] the verdict is at least
//!   [`IntrusionVerdict::Unknown`] — never `Clear`.
//! - **I3 (fence breach → Present):** a fence-line contact alarm
//!   forces [`IntrusionVerdict::Present`] regardless of other sensor
//!   state.
//! - **I4 (camera-alone ≠ Clear):** classifier-only input, without
//!   safety-primary corroboration, cannot produce `Clear`.
//! - **I5 (monotone freshness):** strictly-fresher inputs never move
//!   the verdict in the less-restrictive direction.
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 + RFC 0016 §5: `#![forbid(unsafe_code)]`, integer-
//! only safety path, stack-only evaluator (no allocation on the hot
//! path), `Debug + Clone + PartialEq` on all public types.

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod sensors;
pub mod verdict;

#[cfg(kani)]
pub mod kani_proofs;

pub use evaluate::{evaluate, IntrusionOutcome, IntrusionParams, TriggerReason};
pub use sensors::{
    CameraClass, CameraReturn, FenceLineState, LidarReturn, RadarReturn, WaysideSensorFrame,
    LATERAL_GATE_MM, MAX_SENSOR_STALE_MS,
};
pub use verdict::IntrusionVerdict;
