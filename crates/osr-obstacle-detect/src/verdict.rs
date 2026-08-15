//! Verdict severity — the three outcomes the evaluator can emit,
//! plus the classification that drives the severity choice.

use serde::{Deserialize, Serialize};

/// The four verdicts an [`crate::evaluate`] call can return.
///
/// Ordered from least to most restrictive — the `Ord` derivation
/// makes severity comparison direct: `v1 < v2` means `v2` is more
/// restrictive. Any `EmergencyBrake` dominates any `CrawlOnly`,
/// which dominates any `RestrictedSpeed`, which dominates any
/// `Clear`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub enum ObstacleVerdict {
    /// No obstacle in the current stopping-distance envelope; the
    /// train may run up to its MA-permitted speed.
    Clear,

    /// A sensor-suite degradation calls for a per-tick speed cap at
    /// [`RESTRICTED_SPEED_MMPS`] (40 km/h, the reliable ultrasonic
    /// envelope). The canonical trigger is "LIDAR offline, radar
    /// still healthy": the radar alone covers the 5–200 m band, so
    /// no EB is warranted, but we do not trust a single long-range
    /// channel to let the train run at mainline speed.
    ///
    /// ATO consumes this verdict by holding actual speed ≤ 40 km/h
    /// via the service-brake, not the emergency brake.
    RestrictedSpeed,

    /// Obstacle detected but classifiable as low-severity (paper
    /// bag, small animal, windblown debris) *and* outside the
    /// safety-critical envelope. Reduce speed to
    /// [`CRAWL_SPEED_MMPS`] until the path re-clears.
    CrawlOnly,

    /// Obstacle detected inside the safety envelope, or any safety-
    /// primary sensor is stale, or the 2oo2 cross-check disagrees,
    /// or every long-range sensor is offline above the ultrasonic
    /// speed band. Emergency brake.
    EmergencyBrake,
}

/// Classification of a detected obstacle. Drives severity escalation
/// per verdict's class-severity table (§5.1 of RFC 0015).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ObstacleClass {
    /// A human — the most severe case. Always escalates to
    /// `EmergencyBrake` regardless of range inside the envelope.
    Human,

    /// A large animal (dog, sheep, deer). Same treatment as human in
    /// the near envelope; `CrawlOnly` if further out and the stereo
    /// camera has a clear track.
    LargeAnimal,

    /// A vehicle (level-crossing scenario). Always `EmergencyBrake`.
    Vehicle,

    /// Fallen static debris (a branch, a suitcase). `EmergencyBrake`
    /// if in the rail profile; `CrawlOnly` if adjacent.
    StaticDebris,

    /// Light wind-blown debris (paper, cloth, plastic bag). Never
    /// triggers `EmergencyBrake` on its own — the stereo classifier
    /// rules out the harder classes first.
    LightDebris,

    /// The classifier could not identify the object. Treated as
    /// `StaticDebris` for safety (conservative).
    Unknown,
}

/// Maximum train speed at which ultrasonic-only coverage is safe.
///
/// Rationale: ultrasonic reliable range ≈ 20 m. At 40 km/h
/// (≈ 11 100 mm/s), service-brake stopping distance is ≈ 18 m —
/// inside the ultrasonic band. Any faster, and the train would
/// overrun a detected obstacle before the ultrasonic return is
/// valid.
pub const ULTRASONIC_MAX_SPEED_MMPS: u32 = 11_100;

/// Speed cap applied under [`ObstacleVerdict::RestrictedSpeed`].
///
/// 40 km/h = 11 100 mm/s — identical to [`ULTRASONIC_MAX_SPEED_MMPS`]
/// by construction. The verdict means "trust only the ultrasonic
/// belt for safety," so the cap matches the ultrasonic-safe envelope.
pub const RESTRICTED_SPEED_MMPS: u32 = ULTRASONIC_MAX_SPEED_MMPS;

/// Speed to reduce to under [`ObstacleVerdict::CrawlOnly`].
///
/// 15 km/h = 4 166 mm/s. Matches the recovery-mode cap in RFC 0015
/// §8.2 so the same speed band is always a known-safe fallback.
pub const CRAWL_SPEED_MMPS: u32 = 4_166;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn verdict_ordering_is_severity_monotone() {
        assert!(ObstacleVerdict::Clear < ObstacleVerdict::RestrictedSpeed);
        assert!(ObstacleVerdict::RestrictedSpeed < ObstacleVerdict::CrawlOnly);
        assert!(ObstacleVerdict::CrawlOnly < ObstacleVerdict::EmergencyBrake);
    }

    #[test]
    fn crawl_is_below_ultrasonic_envelope() {
        const { assert!(CRAWL_SPEED_MMPS < ULTRASONIC_MAX_SPEED_MMPS) };
    }

    #[test]
    fn restricted_speed_matches_ultrasonic_envelope() {
        assert_eq!(RESTRICTED_SPEED_MMPS, ULTRASONIC_MAX_SPEED_MMPS);
    }
}
