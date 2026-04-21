//! Topic ID interning.
//!
//! Topics are human-readable dotted strings (`osr.train.atp.envelope`).
//! On the wire they are 16-bit IDs. The registry maintains a
//! deterministic, sorted mapping — populated at boot from a static
//! config — and every ECU in a consist must agree on the same map.
//!
//! v1 uses a `BTreeMap` + `Vec` for O(log n) lookup and stable
//! iteration order. At ~100 topics this is fine; a real deployment
//! would fan the intern table out at ECU bring-up time.

use std::collections::BTreeMap;

/// Opaque, 16-bit topic identifier.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct TopicId(pub u16);

/// String ↔ `TopicId` interner. Strings are stored in insertion
/// order (stable across runs when built from the same static list).
#[derive(Clone, Debug, Default)]
pub struct TopicRegistry {
    by_name: BTreeMap<String, TopicId>,
    names: Vec<String>,
}

impl TopicRegistry {
    /// Empty registry. Callers typically use [`TopicRegistry::builtin`]
    /// instead.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Pre-populated with the canonical topic list from RFC 0006 §5.
    ///
    /// The order is load-bearing — every ECU in the consist must
    /// agree. A future bring-up handshake will verify that agreement
    /// by exchanging SHA-256 hashes of the topic list; for now we
    /// rely on all ECUs linking the same `osr-tcn` version.
    #[must_use]
    pub fn builtin() -> Self {
        let mut r = Self::new();
        for name in BUILTIN_TOPICS {
            r.intern(name);
        }
        r
    }

    /// Intern a topic name, returning its [`TopicId`]. Idempotent:
    /// subsequent calls with the same name return the same ID.
    pub fn intern(&mut self, name: &str) -> TopicId {
        if let Some(id) = self.by_name.get(name) {
            return *id;
        }
        let id = TopicId(u16::try_from(self.names.len()).unwrap_or(u16::MAX));
        self.names.push(name.to_string());
        self.by_name.insert(name.to_string(), id);
        id
    }

    /// Look up a topic name by ID.
    #[must_use]
    pub fn name(&self, id: TopicId) -> Option<&str> {
        self.names.get(id.0 as usize).map(String::as_str)
    }

    /// Look up an ID by name.
    #[must_use]
    pub fn id(&self, name: &str) -> Option<TopicId> {
        self.by_name.get(name).copied()
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.names.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.names.is_empty()
    }
}

/// Canonical topic list from RFC 0006 §5. Append-only: reordering
/// or removing a topic is a breaking change for the whole consist.
pub const BUILTIN_TOPICS: &[&str] = &[
    "osr.train.atp.envelope",
    "osr.train.atp.command",
    "osr.train.brake.apply",
    "osr.train.odom.position",
    "osr.train.odom.speed",
    "osr.train.traction.torque_setpoint",
    "osr.train.traction.current_estimate",
    "osr.train.bms.soc",
    "osr.train.bms.limits",
    "osr.train.bms.fault",
    "osr.train.door.status",
    "osr.train.door.interlock",
    "osr.train.hvac.status",
    "osr.train.lighting.status",
    "osr.train.pis.display",
    "osr.train.pis.announcement",
    "osr.train.dmi.page",
    "osr.train.dmi.driver_input",
    "osr.train.tcms.consist_status",
    "osr.train.monitors.fire",
    "osr.train.monitors.derailment",
    "osr.train.monitors.vigilance",
    "osr.train.monitors.hot_axle",
    "osr.train.monitors.aux_power",
    "osr.train.event.record",
];

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builtin_has_expected_topics() {
        let r = TopicRegistry::builtin();
        assert_eq!(r.len(), BUILTIN_TOPICS.len());
        assert!(r.id("osr.train.atp.envelope").is_some());
    }

    #[test]
    fn intern_is_idempotent() {
        let mut r = TopicRegistry::new();
        let a = r.intern("topic.a");
        let b = r.intern("topic.a");
        assert_eq!(a, b);
    }

    #[test]
    fn insertion_order_preserved() {
        let mut r = TopicRegistry::new();
        let a = r.intern("a");
        let b = r.intern("b");
        let c = r.intern("c");
        assert_eq!(a.0, 0);
        assert_eq!(b.0, 1);
        assert_eq!(c.0, 2);
        assert_eq!(r.name(a), Some("a"));
        assert_eq!(r.name(c), Some("c"));
    }

    #[test]
    fn missing_id_returns_none() {
        let r = TopicRegistry::builtin();
        assert!(r.name(TopicId(9_999)).is_none());
        assert!(r.id("not.a.topic").is_none());
    }
}
