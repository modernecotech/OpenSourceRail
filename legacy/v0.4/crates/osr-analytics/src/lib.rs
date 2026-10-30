//! OpenSourceRail KPI analytics.
//!
//! Pure functions over time-series data (from [`osr_historian`]
//! typically, but any `&[Sample]` works). Produces the operational
//! KPIs the OCC dashboard and monthly reports consume.
//!
//! Phase 2e crate of [RFC 0005 §4.8](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0. All numeric aggregations — no side effects.
//!
//! # Provided KPIs
//!
//! - **Mean / min / max / standard-deviation** over a sample window.
//! - **Headway adherence** — given a target headway and the actual
//!   inter-arrival intervals, the fraction within tolerance.
//! - **Energy per km** — integral of pack power over the window
//!   divided by distance travelled.
//! - **MDBF** (mean distance between failures) — total km over the
//!   window divided by the number of trip events.
//!
//! # Properties
//!
//! - **A1 determinism.**
//! - **A2 mean in [min, max].**
//! - **A3 empty input returns defined sentinel** (None for mean;
//!   0 for counters).
//! - **A4 headway adherence ∈ [0, 1].**

#![forbid(unsafe_code)]

use osr_historian::Sample;
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Basic statistics
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Default, Serialize, Deserialize)]
pub struct BasicStats {
    pub count: usize,
    pub mean: Option<f64>,
    pub min: Option<f64>,
    pub max: Option<f64>,
    pub stddev: Option<f64>,
}

#[must_use]
pub fn basic_stats(samples: &[Sample]) -> BasicStats {
    if samples.is_empty() {
        return BasicStats::default();
    }
    let n = samples.len() as f64;
    let mut sum = 0.0_f64;
    let mut min = f64::INFINITY;
    let mut max = f64::NEG_INFINITY;
    for s in samples {
        sum += s.value;
        if s.value < min {
            min = s.value;
        }
        if s.value > max {
            max = s.value;
        }
    }
    let mean = sum / n;
    let mut var = 0.0_f64;
    for s in samples {
        let d = s.value - mean;
        var += d * d;
    }
    let variance = var / n;
    BasicStats {
        count: samples.len(),
        mean: Some(mean),
        min: Some(min),
        max: Some(max),
        stddev: Some(variance.sqrt()),
    }
}

// ---------------------------------------------------------------------------
// Headway adherence
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Default, Serialize, Deserialize)]
pub struct HeadwayAdherence {
    /// Number of intervals observed.
    pub intervals: usize,
    /// Fraction of intervals within tolerance.
    pub adherence: f64,
}

/// Given arrival timestamps (ns) at a dispatch point and a target
/// headway, compute the fraction of intervals within `tolerance_s`
/// of the target.
#[must_use]
pub fn headway_adherence(
    arrivals_ns: &[u64],
    target_headway_s: u32,
    tolerance_s: u32,
) -> HeadwayAdherence {
    if arrivals_ns.len() < 2 {
        return HeadwayAdherence::default();
    }
    let target_ns = u64::from(target_headway_s) * 1_000_000_000;
    let tolerance_ns = u64::from(tolerance_s) * 1_000_000_000;
    let mut within = 0_usize;
    let mut intervals = 0_usize;
    for w in arrivals_ns.windows(2) {
        let delta = w[1].saturating_sub(w[0]);
        intervals += 1;
        let diff = delta.abs_diff(target_ns);
        if diff <= tolerance_ns {
            within += 1;
        }
    }
    HeadwayAdherence {
        intervals,
        adherence: within as f64 / intervals as f64,
    }
}

// ---------------------------------------------------------------------------
// Energy per km
// ---------------------------------------------------------------------------

/// Compute energy per km over a sample window. `power_samples`
/// are in watts at their `timestamp_ns`; `distance_km` is the
/// distance travelled over the same window.
///
/// Returns Wh / km. `None` when the window is degenerate (no
/// samples or zero distance).
#[must_use]
pub fn energy_per_km(power_samples: &[Sample], distance_km: f64) -> Option<f64> {
    if power_samples.len() < 2 || distance_km <= 0.0 {
        return None;
    }
    // Trapezoidal integral of power over time, in J.
    let mut joules = 0.0_f64;
    for w in power_samples.windows(2) {
        let dt_s = (w[1].timestamp_ns.saturating_sub(w[0].timestamp_ns)) as f64 / 1e9;
        let avg_w = (w[0].value + w[1].value) * 0.5;
        joules += avg_w * dt_s;
    }
    let wh = joules / 3600.0;
    Some(wh / distance_km)
}

// ---------------------------------------------------------------------------
// MDBF
// ---------------------------------------------------------------------------

/// Mean distance between failures. Returns km / failure, or `None`
/// if no failures.
#[must_use]
pub fn mdbf_km(total_km: f64, failure_count: u32) -> Option<f64> {
    if failure_count == 0 {
        None
    } else {
        Some(total_km / f64::from(failure_count))
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn s(ts: u64, v: f64) -> Sample {
        Sample {
            timestamp_ns: ts,
            value: v,
        }
    }

    #[test]
    fn basic_empty_is_default() {
        let b = basic_stats(&[]);
        assert_eq!(b.count, 0);
        assert!(b.mean.is_none());
    }

    #[test]
    fn basic_single_sample() {
        let b = basic_stats(&[s(0, 5.0)]);
        assert_eq!(b.mean, Some(5.0));
        assert_eq!(b.min, Some(5.0));
        assert_eq!(b.max, Some(5.0));
        assert_eq!(b.stddev, Some(0.0));
    }

    #[test]
    fn basic_mean_in_range() {
        let b = basic_stats(&[s(0, 1.0), s(1, 2.0), s(2, 3.0)]);
        assert_eq!(b.mean, Some(2.0));
        assert!(b.stddev.unwrap() > 0.0);
    }

    #[test]
    fn headway_perfect() {
        let arrivals: Vec<u64> = (0..5).map(|i| i * 60_000_000_000).collect();
        let h = headway_adherence(&arrivals, 60, 5);
        assert_eq!(h.intervals, 4);
        assert_eq!(h.adherence, 1.0);
    }

    #[test]
    fn headway_none() {
        let h = headway_adherence(&[1_000_000_000], 60, 5);
        assert_eq!(h.intervals, 0);
        assert_eq!(h.adherence, 0.0);
    }

    #[test]
    fn energy_per_km_basic() {
        // 100 kW for 1 hour = 100 kWh. Over 50 km → 2000 Wh/km.
        let samples = vec![s(0, 100_000.0), s(3_600_000_000_000, 100_000.0)];
        let e = energy_per_km(&samples, 50.0).unwrap();
        assert!((e - 2000.0).abs() < 1.0);
    }

    #[test]
    fn mdbf_zero_failures_is_none() {
        assert_eq!(mdbf_km(1000.0, 0), None);
    }

    #[test]
    fn mdbf_positive() {
        assert_eq!(mdbf_km(1000.0, 4), Some(250.0));
    }
}
