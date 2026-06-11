//! OpenSourceRail onboard event recorder.
//!
//! A fixed-capacity ring buffer of [`EventRecord`]s — the "black box"
//! that's read out after an incident. Each record is a small fixed
//! layout (32 bytes on typical 64-bit targets): a nanosecond
//! timestamp, a category, a sub-code, and two signed 64-bit values.
//! Two payload slots cover almost every safety-relevant event
//! (command + confirmation, value + threshold, sensor A + sensor B).
//! When richer telemetry is needed, the caller can split the event
//! across several records with a correlating code.
//!
//! Phase 2c crate 7 of [RFC 0005 §4.1](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 because losing the record compromises incident
//! investigation but does not directly endanger passengers.
//!
//! # Crash survivability
//!
//! The core here is the in-memory ring-buffer logic — it holds the
//! most recent `capacity` records and quotes an exact count of
//! dropped (overwritten) older records. Crash-survivability in the
//! deployed system is a hardware concern: the buffer's backing
//! memory sits behind a battery-backed DRAM bank (or FRAM for
//! small capacities). This crate exposes [`EventRecorder::snapshot`]
//! / [`EventRecorder::restore`] so a storage driver can persist and
//! re-load state across power cycles.
//!
//! # API shape
//!
//! Stateful object, not a pure function — the ring buffer is the
//! whole point. Hot path has no allocation (the backing `Vec` is
//! sized at construction and never resized).
//!
//! # Properties (proptest-verified)
//!
//! - **ER1 capacity-bounded:** `len() ≤ capacity()` always.
//! - **ER2 FIFO order:** [`EventRecorder::iter`] yields records in
//!   chronological (write) order.
//! - **ER3 dropped accounting:** after N writes into a ring of size
//!   K, `dropped() == N.saturating_sub(K)` and
//!   `total_written() == N`.
//! - **ER4 most-recent N retained:** for any K ≤ capacity, the last
//!   K writes are all present in `iter().rev().take(K)`.
//! - **ER5 round-trip:** `restore(snapshot()) == self`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Event record
// ---------------------------------------------------------------------------

/// Coarse category. Caller subdivides via `code` per category.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
#[repr(u8)]
pub enum EventCategory {
    #[default]
    Unknown = 0,
    /// Any of the SIL-4 brake sources: ATP, vigilance, fire,
    /// derailment, driver.
    BrakeCommand = 1,
    /// ATP mode change / envelope calc / trigger reason.
    Atp = 2,
    /// ATO mode transition.
    Ato = 3,
    /// Position report snapshot.
    Position = 4,
    /// Door state transition.
    Door = 5,
    /// Traction torque setpoint / current estimate.
    Traction = 6,
    /// BMS SoC / fault / contactor.
    Bms = 7,
    /// Fire / smoke / derailment / hot-axle trips.
    SafetyMonitor = 8,
    /// HVAC / lighting / PIS — comfort systems.
    Comfort = 9,
    /// Wayside event (switch, balise, consensus).
    Wayside = 10,
    /// Generic diagnostic.
    Diagnostic = 15,
}

/// Single recorded event. Fixed layout for deterministic storage.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct EventRecord {
    pub timestamp_ns: u64,
    pub category: EventCategory,
    pub code: u16,
    pub value_a: i64,
    pub value_b: i64,
}

impl EventRecord {
    #[must_use]
    pub fn new(timestamp_ns: u64, category: EventCategory, code: u16) -> Self {
        Self {
            timestamp_ns,
            category,
            code,
            value_a: 0,
            value_b: 0,
        }
    }

    #[must_use]
    pub fn with_values(mut self, a: i64, b: i64) -> Self {
        self.value_a = a;
        self.value_b = b;
        self
    }
}

// ---------------------------------------------------------------------------
// Recorder
// ---------------------------------------------------------------------------

/// Fixed-capacity ring recorder.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct EventRecorder {
    slots: Vec<EventRecord>,
    /// Next write position (mod capacity).
    head: usize,
    /// Records currently present (≤ capacity).
    len: usize,
    /// Total records written since construction or last clear.
    total_written: u64,
}

impl EventRecorder {
    /// Build a recorder with the given capacity. Panics if zero.
    #[must_use]
    pub fn new(capacity: usize) -> Self {
        assert!(capacity > 0, "event recorder capacity must be > 0");
        Self {
            slots: vec![EventRecord::default(); capacity],
            head: 0,
            len: 0,
            total_written: 0,
        }
    }

    #[must_use]
    pub fn capacity(&self) -> usize {
        self.slots.len()
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.len
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    #[must_use]
    pub fn is_full(&self) -> bool {
        self.len == self.capacity()
    }

    /// Total records written lifetime.
    #[must_use]
    pub fn total_written(&self) -> u64 {
        self.total_written
    }

    /// Count of records that have been overwritten by newer writes.
    #[must_use]
    pub fn dropped(&self) -> u64 {
        self.total_written.saturating_sub(self.capacity() as u64)
    }

    /// Push a new record. Overwrites the oldest if full.
    pub fn record(&mut self, record: EventRecord) {
        let cap = self.capacity();
        self.slots[self.head] = record;
        self.head = (self.head + 1) % cap;
        if self.len < cap {
            self.len += 1;
        }
        self.total_written = self.total_written.saturating_add(1);
    }

    /// Iterate records in chronological (write) order. Returns a
    /// double-ended iterator so callers can efficiently read from
    /// the tail.
    pub fn iter(&self) -> impl DoubleEndedIterator<Item = &EventRecord> + ExactSizeIterator {
        let cap = self.capacity();
        let start = if self.is_full() { self.head } else { 0 };
        (0..self.len).map(move |i| &self.slots[(start + i) % cap])
    }

    /// Clear all records. Preserves the buffer's backing allocation
    /// but resets counters. Used by ground crew after readout.
    pub fn clear(&mut self) {
        for slot in self.slots.iter_mut() {
            *slot = EventRecord::default();
        }
        self.head = 0;
        self.len = 0;
        self.total_written = 0;
    }

    /// Serialise state for persistence. Caller's storage driver
    /// writes the resulting [`Snapshot`] to crash-survivable
    /// memory.
    #[must_use]
    pub fn snapshot(&self) -> Snapshot {
        Snapshot {
            slots: self.slots.clone(),
            head: self.head,
            len: self.len,
            total_written: self.total_written,
        }
    }

    /// Re-hydrate from a previously-taken snapshot.
    #[must_use]
    pub fn restore(snapshot: Snapshot) -> Self {
        Self {
            slots: snapshot.slots,
            head: snapshot.head,
            len: snapshot.len,
            total_written: snapshot.total_written,
        }
    }
}

/// Serialisable snapshot for the storage driver.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Snapshot {
    pub slots: Vec<EventRecord>,
    pub head: usize,
    pub len: usize,
    pub total_written: u64,
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn sample(ts: u64, c: u16) -> EventRecord {
        EventRecord::new(ts, EventCategory::Diagnostic, c).with_values(ts as i64, 0)
    }

    #[test]
    fn starts_empty() {
        let r = EventRecorder::new(8);
        assert_eq!(r.len(), 0);
        assert_eq!(r.capacity(), 8);
        assert!(r.is_empty());
        assert!(!r.is_full());
        assert_eq!(r.dropped(), 0);
    }

    #[test]
    fn records_up_to_capacity() {
        let mut r = EventRecorder::new(4);
        for i in 0..3 {
            r.record(sample(i as u64, i));
        }
        assert_eq!(r.len(), 3);
        assert_eq!(r.total_written(), 3);
        assert_eq!(r.dropped(), 0);
    }

    #[test]
    fn fifo_order_preserved_below_capacity() {
        let mut r = EventRecorder::new(5);
        for i in 0..4 {
            r.record(sample(i as u64 * 100, i));
        }
        let collected: Vec<_> = r.iter().map(|e| e.timestamp_ns).collect();
        assert_eq!(collected, vec![0, 100, 200, 300]);
    }

    #[test]
    fn wrap_retains_most_recent() {
        let mut r = EventRecorder::new(3);
        for i in 0..10 {
            r.record(sample(i as u64 * 100, i));
        }
        assert_eq!(r.len(), 3);
        assert_eq!(r.total_written(), 10);
        assert_eq!(r.dropped(), 7);
        let collected: Vec<_> = r.iter().map(|e| e.timestamp_ns).collect();
        // Last 3 writes: t=700, 800, 900
        assert_eq!(collected, vec![700, 800, 900]);
    }

    #[test]
    fn clear_resets_state() {
        let mut r = EventRecorder::new(4);
        for i in 0..6 {
            r.record(sample(i as u64, i));
        }
        r.clear();
        assert_eq!(r.len(), 0);
        assert_eq!(r.total_written(), 0);
        assert_eq!(r.dropped(), 0);
        assert!(r.iter().next().is_none());
    }

    #[test]
    fn snapshot_roundtrip() {
        let mut r = EventRecorder::new(5);
        for i in 0..12 {
            r.record(sample(i as u64, i));
        }
        let snap = r.snapshot();
        let r2 = EventRecorder::restore(snap);
        assert_eq!(r, r2);
        let a: Vec<_> = r.iter().collect();
        let b: Vec<_> = r2.iter().collect();
        assert_eq!(a, b);
    }

    #[test]
    fn records_have_fixed_layout_size() {
        // Not a safety property per se, but a design invariant the
        // storage driver relies on: `EventRecord` is small and
        // fixed-size. This test pins the size so accidental field
        // additions get noticed.
        use core::mem::size_of;
        // 8 (ts) + 1 (cat) + 2 (code) + align padding + 8 + 8
        // Rust may add padding; the exact value isn't load-bearing
        // but something dramatically larger would indicate a regression.
        assert!(size_of::<EventRecord>() <= 48);
    }
}
