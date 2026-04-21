//! Speed-profile helpers.
//!
//! The station-approach profile gives the maximum speed a train can
//! be travelling at a given distance from the stop point such that
//! a constant deceleration `a` brings it to rest exactly at the stop:
//!
//! `v(d) = sqrt(2 · a · d)`.

/// Station-approach target speed at distance `d_mm` ahead, if we
/// must stop at `d_mm = 0` using deceleration `decel_mmps2`.
///
/// Returns `i32::MAX` if distance is very large (saturation), and 0
/// for non-positive distances.
#[must_use]
pub fn station_approach_speed_mmps(distance_to_stop_mm: i64, decel_mmps2: i32) -> i32 {
    if distance_to_stop_mm <= 0 || decel_mmps2 <= 0 {
        return 0;
    }
    // v² = 2 · a · d  (a in mm/s², d in mm → v² in mm²/s²)
    let v_sq = 2_i64
        .saturating_mul(i64::from(decel_mmps2))
        .saturating_mul(distance_to_stop_mm);
    if v_sq <= 0 {
        return 0;
    }
    let v = isqrt(v_sq as u64);
    i32::try_from(v.min(i32::MAX as u64)).unwrap_or(i32::MAX)
}

fn isqrt(n: u64) -> u64 {
    if n < 2 {
        return n;
    }
    let mut x = n;
    let mut y = (x + 1) / 2;
    while y < x {
        x = y;
        y = (x + n / x) / 2;
    }
    x
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_distance_zero_speed() {
        assert_eq!(station_approach_speed_mmps(0, 1000), 0);
        assert_eq!(station_approach_speed_mmps(-100, 1000), 0);
    }

    #[test]
    fn monotonic_in_distance() {
        let a = station_approach_speed_mmps(1_000, 1000);
        let b = station_approach_speed_mmps(10_000, 1000);
        let c = station_approach_speed_mmps(100_000, 1000);
        assert!(a < b && b < c);
    }

    #[test]
    fn matches_closed_form() {
        // v = sqrt(2 · 1000 · 100_000) = sqrt(2e8) ≈ 14_142
        let v = station_approach_speed_mmps(100_000, 1000);
        assert!((14_100..=14_200).contains(&v), "v={v}");
    }
}
