//! Time-of-day service schedule.
//!
//! Each line has a `LineSchedule` consisting of ordered time windows, each
//! with a target headway. Service is defined between `service_start_s` and
//! `service_end_s` (seconds since midnight).
//!
//! The sim uses the schedule via a `DispatchThrottle` that tracks the next
//! allowed departure time per (line, dispatch_point, heading).

use osr_core::StationId;
use std::collections::HashMap;

use crate::train::Heading;

/// Convert hours:minutes to seconds since midnight.
pub const fn hm(h: u32, m: u32) -> u32 {
    h * 3600 + m * 60
}

#[derive(Clone, Debug)]
pub struct TimeWindow {
    /// Start of window (seconds since midnight).
    pub start_s: u32,
    /// End of window (seconds since midnight, exclusive).
    pub end_s: u32,
    /// Target headway in seconds during this window.
    pub headway_s: u32,
}

#[derive(Clone, Debug)]
pub struct LineSchedule {
    pub service_start_s: u32,
    pub service_end_s: u32,
    pub windows: Vec<TimeWindow>,
}

impl LineSchedule {
    /// Headway (s) applicable at the given sim-clock time (seconds since
    /// midnight). Returns `None` outside service hours.
    pub fn headway_at(&self, t_since_midnight: u32) -> Option<u32> {
        if t_since_midnight < self.service_start_s || t_since_midnight >= self.service_end_s {
            return None;
        }
        for w in &self.windows {
            if t_since_midnight >= w.start_s && t_since_midnight < w.end_s {
                return Some(w.headway_s);
            }
        }
        None
    }

    /// Is the given sim-clock time within service hours?
    #[allow(dead_code)]
    pub fn in_service(&self, t_since_midnight: u32) -> bool {
        t_since_midnight >= self.service_start_s && t_since_midnight < self.service_end_s
    }

    /// Summary string for header printing (e.g. "4/8/4/10/15 min peak→late").
    pub fn headway_summary(&self) -> String {
        self.windows
            .iter()
            .map(|w| format!("{}m", w.headway_s / 60))
            .collect::<Vec<_>>()
            .join("/")
    }
}

pub type ThrottleKey = (usize, StationId, Heading);

/// Tracks when the next train may depart from each dispatch point.
#[derive(Debug, Default)]
pub struct DispatchThrottle {
    /// Earliest sim-clock time (seconds since midnight) at which the next
    /// train may depart from this (line, station, heading) tuple.
    next_allowed: HashMap<ThrottleKey, u32>,
    /// Set of tuples that are throttled (i.e., configured as dispatch
    /// points). Stations *not* in this set are not throttled.
    throttle_points: std::collections::HashSet<ThrottleKey>,
    /// Train-seconds held at dispatch points while waiting for a schedule slot,
    /// during service hours (fleet oversupplied for the headway).
    pub in_service_held_s: u64,
    /// Train-seconds parked at dispatch points outside service hours
    /// (overnight, or pre-service morning).
    pub out_of_service_held_s: u64,
}

impl DispatchThrottle {
    pub fn new() -> Self {
        Self::default()
    }

    /// Register a throttle point with an initial `next_allowed` time.
    pub fn register(&mut self, key: ThrottleKey, initial_next_allowed: u32) {
        self.throttle_points.insert(key);
        self.next_allowed.insert(key, initial_next_allowed);
    }

    /// Iterator over all registered throttle keys, used for bulk operations
    /// like the midnight reset.
    pub fn registered_keys(&self) -> impl Iterator<Item = ThrottleKey> + '_ {
        self.throttle_points.iter().copied()
    }

    /// Overwrite the next-allowed time for a key. Used at midnight crossings
    /// to re-arm morning dispatches.
    pub fn reset(&mut self, key: ThrottleKey, next_allowed: u32) {
        if self.throttle_points.contains(&key) {
            self.next_allowed.insert(key, next_allowed);
        }
    }

    /// Is this (line, station, heading) a throttle point at all?
    pub fn is_throttle_point(&self, key: &ThrottleKey) -> bool {
        self.throttle_points.contains(key)
    }

    /// May a train depart from this throttle point at the given clock time?
    /// Returns true for non-throttle points (they're always free).
    pub fn can_dispatch(&self, key: &ThrottleKey, t_since_midnight: u32) -> bool {
        match self.next_allowed.get(key) {
            Some(&next) => t_since_midnight >= next,
            None => true, // not a throttle point
        }
    }

    /// Record a dispatch, advancing the next-allowed time by the current
    /// headway. No-op for non-throttle points.
    pub fn mark_dispatched(&mut self, key: &ThrottleKey, t_since_midnight: u32, headway_s: u32) {
        if self.throttle_points.contains(key) {
            // Advance to max(t + headway, current next_allowed + headway) so
            // we don't collapse held-up trains into the same instant.
            let prev = *self.next_allowed.get(key).unwrap_or(&0);
            let base = prev.max(t_since_midnight);
            self.next_allowed.insert(*key, base + headway_s);
        }
    }

    /// Record that a train was held for `dt` seconds at a dispatch point
    /// while service was running (schedule oversubscribed for fleet).
    pub fn record_in_service_held(&mut self, dt: f32) {
        self.in_service_held_s += dt as u64;
    }

    /// Record that a train was held for `dt` seconds at a dispatch point
    /// outside service hours (overnight idle, pre-service morning).
    pub fn record_out_of_service_held(&mut self, dt: f32) {
        self.out_of_service_held_s += dt as u64;
    }
}
