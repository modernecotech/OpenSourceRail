//! Speed envelope math.
//!
//! Given a train's distance to the end of its Movement Authority and
//! a conservative deceleration, `max_safe_speed_mmps` returns the
//! maximum head speed such that an emergency brake application started
//! *now* (after the driver/ECU reaction time) would bring the train
//! to rest at or before the MA end.
//!
//! The math is integer-only. Floats are tolerated only at
//! [`DecelTable::from_emergency`], which converts the human-authored
//! [`BrakingCurve`] (in SI m/s, m/s²) to fixed-point mm-per-second
//! units, rounding deceleration *down* (safe-side).
//!
//! # Closed form
//!
//! Let `d` be the conservative deceleration (mm/s²), `t` the reaction
//! time (s), and `x` the distance to MA end (mm). The train covers
//! `v·t + v²/(2·d)` before stopping. Solving
//! `v·t + v²/(2·d) ≤ x` for the maximum `v`:
//!
//! ```text
//! v_max = -d·t + sqrt((d·t)² + 2·d·x)
//! ```
//!
//! Implemented in integer arithmetic with saturating ops. Per RFC 0005
//! §7, overflow is not a safety concern because every saturating op is
//! monotone in the safe direction (larger `d·t` → smaller `v_max`,
//! smaller `x` → smaller `v_max`).

use osr_core::ConsistDescriptor;

/// Piecewise-linear emergency deceleration table in safety-path units.
///
/// Keyed by speed in mm/s. Values are deceleration in mm/s².
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DecelTable {
    /// `(speed_mmps, decel_mmps2)` pairs, non-empty.
    pub points: Vec<(i32, i32)>,
    /// Driver/ECU reaction time in milliseconds.
    pub reaction_time_ms: u32,
}

impl DecelTable {
    /// Build from a consist's **emergency** braking curve.
    ///
    /// Safe-side rounding: every `(speed, decel)` pair rounds speed
    /// *up* and deceleration *down* to the nearest mm/s and mm/s²
    /// respectively, producing a slightly pessimistic envelope.
    ///
    /// Returns a table with at least one point; an empty input curve
    /// yields a single fail-restrictive `(0, 1)` entry so that any
    /// caller still gets a finite (but severely restrictive) envelope
    /// rather than an arithmetic edge case.
    #[must_use]
    pub fn from_emergency(consist: &ConsistDescriptor) -> Self {
        let mut points: Vec<(i32, i32)> = consist
            .braking
            .emergency
            .iter()
            .filter(|(s, d)| s.is_finite() && d.is_finite() && *d > 0.0)
            .map(|(s, d)| {
                let s_mmps = (s * 1000.0).ceil() as i32; // round speed up
                let d_mmps2 = (d * 1000.0).floor() as i32; // round decel down
                (s_mmps.max(0), d_mmps2.max(1))
            })
            .collect();
        points.sort_by_key(|(s, _)| *s);
        if points.is_empty() {
            points.push((0, 1));
        }
        Self {
            points,
            reaction_time_ms: consist.braking.reaction_time_ms,
        }
    }

    /// The most conservative (smallest) deceleration over the whole
    /// curve. Used as the single envelope deceleration in v1 to keep
    /// the math closed-form.
    ///
    /// Always ≥ 1 mm/s² to avoid divide-by-zero; an all-zero curve
    /// reduces to a near-immediate-stop envelope.
    #[must_use]
    pub fn conservative_decel_mmps2(&self) -> i32 {
        self.points
            .iter()
            .map(|(_, d)| *d)
            .min()
            .unwrap_or(1)
            .max(1)
    }
}

/// Newton-style integer square root for `u64`.
///
/// Returns `floor(sqrt(n))`. Safe-side for envelope math because we
/// use the result as an *upper bound* on allowed speed; flooring makes
/// the bound slightly tighter.
#[must_use]
pub fn isqrt(n: u64) -> u64 {
    if n < 2 {
        return n;
    }
    let mut x = n;
    // Initial guess: 2^(bits/2)
    let mut y = (x + 1) / 2;
    while y < x {
        x = y;
        y = (x + n / x) / 2;
    }
    x
}

/// Maximum safe head speed given distance to MA end.
///
/// Returns the speed (mm/s, non-negative) such that if the train is
/// travelling at exactly this speed, an emergency brake application
/// initiated *now* — after `reaction_time_ms` of reaction distance —
/// brings it to rest at or before the MA end.
///
/// Integer-only. Saturating arithmetic throughout; on overflow the
/// function returns `i32::MAX` which the caller treats as
/// "no envelope restriction from this input," but this is unreachable
/// under the [`osr_interlocking::MAX_MA_DISTANCE_MM`] bound on `x`.
#[must_use]
pub fn max_safe_speed_mmps(distance_to_end_mm: i64, decel: &DecelTable) -> i32 {
    if distance_to_end_mm <= 0 {
        return 0;
    }
    let d = i64::from(decel.conservative_decel_mmps2()); // mm/s²
    if d <= 0 {
        return 0;
    }
    let t_ms = i64::from(decel.reaction_time_ms); // ms

    // d · t (mm/s): d is mm/s², t is ms, so d · t / 1000 gives mm/s.
    // Safe-side rounding: round d·t UP by using ceil-division so that
    // v_max is tighter (smaller).
    let dt_num = d.saturating_mul(t_ms);
    let dt_mmps = dt_num.saturating_add(999) / 1000;

    // (d·t)² in (mm/s)²
    let dt_sq = dt_mmps.saturating_mul(dt_mmps);

    // 2·d·x in (mm/s)²
    let two_d_x = 2_i64.saturating_mul(d).saturating_mul(distance_to_end_mm);

    // Under-sqrt
    let under = dt_sq.saturating_add(two_d_x);
    if under < 0 {
        return 0; // unreachable in practice; saturating arithmetic guard
    }

    let root = isqrt(under as u64) as i64;
    let v_max = (root.saturating_sub(dt_mmps)).max(0);

    // Clamp to i32; distance_to_end_mm <= MAX_MA_DISTANCE_MM (2 km)
    // and d <= ~5000 mm/s² puts this comfortably under 100_000 mm/s
    // in realistic parameter ranges.
    i32::try_from(v_max).unwrap_or(i32::MAX)
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::ConsistDescriptor;

    #[test]
    fn isqrt_spot_checks() {
        assert_eq!(isqrt(0), 0);
        assert_eq!(isqrt(1), 1);
        assert_eq!(isqrt(2), 1);
        assert_eq!(isqrt(3), 1);
        assert_eq!(isqrt(4), 2);
        assert_eq!(isqrt(99), 9);
        assert_eq!(isqrt(100), 10);
        assert_eq!(isqrt(1_000_000), 1_000);
        // Very large input doesn't underflow or loop forever.
        let n = (1_u64 << 40) - 1;
        let r = isqrt(n);
        assert!(r * r <= n && (r + 1).saturating_mul(r + 1) > n);
    }

    #[test]
    fn decel_table_rounds_safe_side() {
        let consist = ConsistDescriptor::reference_3car();
        // reference_3car has emergency: [(0,1.5),(20,1.4),(28,1.2)]
        let t = DecelTable::from_emergency(&consist);
        assert_eq!(t.points.len(), 3);
        // Speed rounds up, decel rounds down.
        assert_eq!(t.points[0], (0, 1_500));
        assert_eq!(t.points[1], (20_000, 1_400));
        assert_eq!(t.points[2], (28_000, 1_200));
        // Conservative decel is the minimum (1.2 m/s² → 1200 mm/s²).
        assert_eq!(t.conservative_decel_mmps2(), 1_200);
    }

    #[test]
    fn envelope_zero_distance_is_zero_speed() {
        let consist = ConsistDescriptor::reference_3car();
        let t = DecelTable::from_emergency(&consist);
        assert_eq!(max_safe_speed_mmps(0, &t), 0);
        assert_eq!(max_safe_speed_mmps(-1, &t), 0);
    }

    #[test]
    fn envelope_grows_with_distance() {
        let consist = ConsistDescriptor::reference_3car();
        let t = DecelTable::from_emergency(&consist);
        // 100 m ahead.
        let v100 = max_safe_speed_mmps(100_000, &t);
        // 500 m ahead.
        let v500 = max_safe_speed_mmps(500_000, &t);
        // 2 km ahead.
        let v2000 = max_safe_speed_mmps(2_000_000, &t);
        assert!(v100 < v500, "{v100} !< {v500}");
        assert!(v500 < v2000, "{v500} !< {v2000}");
        // Sanity: at 2 km with ~1.2 m/s² decel, v_max ≈ sqrt(2·1.2·2000) ≈ 69 m/s.
        // Minus reaction distance it's still ~65-69 m/s = 65_000-69_000 mm/s.
        assert!(
            (60_000..=72_000).contains(&v2000),
            "v2000 out of expected range: {v2000}"
        );
    }

    #[test]
    fn envelope_reaction_time_tightens_envelope() {
        let mut consist = ConsistDescriptor::reference_3car();
        consist.braking.reaction_time_ms = 0;
        let no_reaction = DecelTable::from_emergency(&consist);
        consist.braking.reaction_time_ms = 2_000; // 2 seconds
        let slow_reaction = DecelTable::from_emergency(&consist);
        let distance = 500_000;
        assert!(
            max_safe_speed_mmps(distance, &no_reaction)
                > max_safe_speed_mmps(distance, &slow_reaction)
        );
    }
}
