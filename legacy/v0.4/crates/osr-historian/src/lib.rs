//! OpenSourceRail time-series historian.
//!
//! Ring-buffer-per-metric store with two retention tiers:
//!
//! - **Raw tier** — fixed ring of recent samples, full sample rate.
//! - **Decimated tier** — older samples kept at 1/N rate to extend
//!   effective retention at bounded memory cost.
//!
//! Queries return a `Vec<Sample>` filtered by timestamp range.
//!
//! Phase 2e crate of [RFC 0005 §4.8](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0: historian loss is a diagnostic inconvenience, not safety.
//! Real deployments pair this with upstream back-pressure so a
//! full ring doesn't silently drop the sample the operator
//! actually needed.
//!
//! # Properties (proptest-verified)
//!
//! - **H1 recent raw retention:** the most-recent `raw_capacity`
//!   samples per metric are always present in the raw tier.
//! - **H2 decimation ratio:** if `decimate_every > 1`, exactly
//!   every Nth sample drops into the decimated tier.
//! - **H3 query bounded by range:** `query(metric, t1, t2)` yields
//!   only samples with `t1 ≤ ts ≤ t2`.
//! - **H4 chronological on query:** samples returned in ascending
//!   timestamp order.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, VecDeque};

#[derive(Copy, Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Sample {
    pub timestamp_ns: u64,
    pub value: f64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HistorianParams {
    pub raw_capacity: usize,
    pub decimated_capacity: usize,
    /// Keep every Nth sample in the decimated tier; 1 = keep all.
    pub decimate_every: u32,
}

impl HistorianParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            raw_capacity: 3_600,       // ~1 h at 1 Hz
            decimated_capacity: 8_640, // ~24 h at every-10th
            decimate_every: 10,
        }
    }
}

#[derive(Clone, Debug)]
pub struct Historian {
    pub params: HistorianParams,
    raw: BTreeMap<String, VecDeque<Sample>>,
    decimated: BTreeMap<String, VecDeque<Sample>>,
    /// Per-metric counter to apply decimation stride.
    insert_count: BTreeMap<String, u64>,
}

impl Default for Historian {
    fn default() -> Self {
        Self::new(HistorianParams::default_metro())
    }
}

impl Historian {
    #[must_use]
    pub fn new(params: HistorianParams) -> Self {
        Self {
            params,
            raw: BTreeMap::new(),
            decimated: BTreeMap::new(),
            insert_count: BTreeMap::new(),
        }
    }

    pub fn ingest(&mut self, metric: &str, sample: Sample) {
        let raw = self.raw.entry(metric.to_string()).or_default();
        let dec = self.decimated.entry(metric.to_string()).or_default();
        let count = self.insert_count.entry(metric.to_string()).or_insert(0);

        // Raw tier — tail-drop oldest on overflow.
        if raw.len() >= self.params.raw_capacity {
            raw.pop_front();
        }
        raw.push_back(sample);

        // Decimated tier: insert every Nth raw sample.
        let stride = self.params.decimate_every.max(1) as u64;
        if *count % stride == 0 {
            if dec.len() >= self.params.decimated_capacity {
                dec.pop_front();
            }
            dec.push_back(sample);
        }
        *count = count.saturating_add(1);
    }

    /// Query samples for a metric in `[t1_ns, t2_ns]`, ascending.
    /// Raw tier preferred; falls back to decimated for older
    /// samples not in raw.
    pub fn query(&self, metric: &str, t1_ns: u64, t2_ns: u64) -> Vec<Sample> {
        let mut out: Vec<Sample> = Vec::new();
        if let Some(raw) = self.raw.get(metric) {
            for s in raw {
                if s.timestamp_ns >= t1_ns && s.timestamp_ns <= t2_ns {
                    out.push(*s);
                }
            }
        }
        if let Some(dec) = self.decimated.get(metric) {
            let raw_oldest = self
                .raw
                .get(metric)
                .and_then(|q| q.front().map(|s| s.timestamp_ns));
            for s in dec {
                if s.timestamp_ns >= t1_ns && s.timestamp_ns <= t2_ns {
                    if let Some(ro) = raw_oldest {
                        if s.timestamp_ns >= ro {
                            continue; // covered by raw tier
                        }
                    }
                    out.push(*s);
                }
            }
        }
        out.sort_by_key(|s| s.timestamp_ns);
        out
    }

    pub fn raw_len(&self, metric: &str) -> usize {
        self.raw.get(metric).map_or(0, VecDeque::len)
    }

    pub fn decimated_len(&self, metric: &str) -> usize {
        self.decimated.get(metric).map_or(0, VecDeque::len)
    }

    pub fn metrics(&self) -> Vec<String> {
        self.raw.keys().cloned().collect()
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ingest_and_query_basic() {
        let mut h = Historian::new(HistorianParams::default_metro());
        for i in 0..10 {
            h.ingest(
                "speed",
                Sample {
                    timestamp_ns: i * 1_000,
                    value: i as f64,
                },
            );
        }
        let out = h.query("speed", 0, u64::MAX);
        assert_eq!(out.len(), 10);
    }

    #[test]
    fn raw_tier_caps_at_capacity() {
        let mut params = HistorianParams::default_metro();
        params.raw_capacity = 5;
        params.decimate_every = 1_000; // never decimate
        let mut h = Historian::new(params);
        for i in 0..20 {
            h.ingest(
                "x",
                Sample {
                    timestamp_ns: i,
                    value: i as f64,
                },
            );
        }
        assert_eq!(h.raw_len("x"), 5);
    }

    #[test]
    fn decimation_works() {
        let mut params = HistorianParams::default_metro();
        params.raw_capacity = 100;
        params.decimated_capacity = 100;
        params.decimate_every = 5;
        let mut h = Historian::new(params);
        for i in 0..20 {
            h.ingest(
                "x",
                Sample {
                    timestamp_ns: i,
                    value: i as f64,
                },
            );
        }
        // 20 samples, every 5th decimated: 20/5 = 4.
        assert_eq!(h.decimated_len("x"), 4);
    }

    #[test]
    fn query_respects_range() {
        let mut h = Historian::new(HistorianParams::default_metro());
        for i in 0..20 {
            h.ingest(
                "x",
                Sample {
                    timestamp_ns: i * 1_000,
                    value: 0.0,
                },
            );
        }
        let out = h.query("x", 5_000, 10_000);
        assert_eq!(out.len(), 6); // 5000, 6000, ..., 10000
    }

    #[test]
    fn query_is_sorted() {
        let mut h = Historian::new(HistorianParams::default_metro());
        h.ingest(
            "x",
            Sample {
                timestamp_ns: 100,
                value: 0.0,
            },
        );
        h.ingest(
            "x",
            Sample {
                timestamp_ns: 50,
                value: 0.0,
            },
        );
        h.ingest(
            "x",
            Sample {
                timestamp_ns: 200,
                value: 0.0,
            },
        );
        let out = h.query("x", 0, u64::MAX);
        for w in out.windows(2) {
            assert!(w[0].timestamp_ns <= w[1].timestamp_ns);
        }
    }

    #[test]
    fn unknown_metric_empty() {
        let h = Historian::new(HistorianParams::default_metro());
        assert!(h.query("nope", 0, u64::MAX).is_empty());
    }
}
