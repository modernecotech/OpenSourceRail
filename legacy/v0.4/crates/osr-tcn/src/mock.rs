//! In-memory mock transport.
//!
//! Drives the same [`crate::TcnPayload`] + [`crate::TopicId`]
//! surface as the real hardware transport will, with per-class
//! back-pressure semantics.

use std::collections::{BTreeMap, VecDeque};

use crate::payload::{TcnPayload, TrafficClass};
use crate::registry::{TopicId, TopicRegistry};

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum TcnError {
    /// A `Safety`-class publish was rejected because the queue is
    /// full. Should be unreachable under a correctly sized bus; if
    /// seen, it indicates a capacity-planning mistake.
    QueueFull,
    /// Deserialisation of a payload failed (shouldn't happen when
    /// the producer and consumer agree on type).
    DecodeError,
    /// A topic was published or received with a traffic class other
    /// than the class established by its first publisher.
    ClassMismatch,
}

/// Default capacities per traffic class (RFC 0006 §7).
pub const DEFAULT_SAFETY_CAPACITY: usize = 256;
pub const DEFAULT_CONTROL_CAPACITY: usize = 64;
pub const DEFAULT_APP_CAPACITY: usize = 16;

/// Mock TCN transport. Holds one queue per topic; bytes are
/// stored as `Vec<u8>` to keep the type erased, matching what the
/// real transport will do.
#[derive(Clone, Debug)]
pub struct MockTcn {
    pub registry: TopicRegistry,
    queues: BTreeMap<TopicId, VecDeque<Vec<u8>>>,
    /// Traffic class per topic. Set on first publish; enforced
    /// thereafter.
    classes: BTreeMap<TopicId, TrafficClass>,
    /// Per-topic maximum queue length. Sized from the default for
    /// the payload's traffic class unless the caller overrides.
    capacities: BTreeMap<TopicId, usize>,
    /// Per-topic drop counter.
    drops: BTreeMap<TopicId, u64>,
    /// Per-topic publish counter (lifetime).
    published: BTreeMap<TopicId, u64>,
}

impl MockTcn {
    /// Build a mock transport with the built-in topic registry and
    /// default class capacities.
    #[must_use]
    pub fn new() -> Self {
        Self {
            registry: TopicRegistry::builtin(),
            queues: BTreeMap::new(),
            classes: BTreeMap::new(),
            capacities: BTreeMap::new(),
            drops: BTreeMap::new(),
            published: BTreeMap::new(),
        }
    }

    /// Override the queue capacity for a specific topic. Useful for
    /// tests that want to force back-pressure.
    pub fn set_capacity(&mut self, topic: TopicId, capacity: usize) {
        self.capacities.insert(topic, capacity);
        if let Some(q) = self.queues.get_mut(&topic) {
            while q.len() > capacity {
                q.pop_front();
                *self.drops.entry(topic).or_insert(0) += 1;
            }
        }
    }

    fn default_capacity(class: TrafficClass) -> usize {
        match class {
            TrafficClass::Safety => DEFAULT_SAFETY_CAPACITY,
            TrafficClass::Control => DEFAULT_CONTROL_CAPACITY,
            TrafficClass::App => DEFAULT_APP_CAPACITY,
        }
    }

    /// Publish a typed payload onto a topic.
    pub fn publish<P: TcnPayload>(&mut self, topic: TopicId, payload: &P) -> Result<(), TcnError> {
        if let Some(class) = self.classes.get(&topic) {
            if *class != P::CLASS {
                return Err(TcnError::ClassMismatch);
            }
        } else {
            self.classes.insert(topic, P::CLASS);
        }
        let cap = *self
            .capacities
            .entry(topic)
            .or_insert_with(|| Self::default_capacity(P::CLASS));
        let bytes = serde_json::to_vec(payload).map_err(|_| TcnError::DecodeError)?;
        let queue = self.queues.entry(topic).or_default();
        if queue.len() >= cap {
            match P::CLASS {
                TrafficClass::Safety => {
                    // Safety must never drop; if we'd overflow, it's
                    // a hard error the caller has to escalate.
                    return Err(TcnError::QueueFull);
                }
                TrafficClass::Control | TrafficClass::App => {
                    // Drop the oldest to make room (tail-drop-first
                    // preserves the most recent observation).
                    queue.pop_front();
                    *self.drops.entry(topic).or_insert(0) += 1;
                }
            }
        }
        queue.push_back(bytes);
        *self.published.entry(topic).or_insert(0) += 1;
        Ok(())
    }

    /// Receive the oldest queued payload on a topic, if any.
    pub fn recv_one<P: TcnPayload>(&mut self, topic: TopicId) -> Option<Result<P, TcnError>> {
        if self
            .classes
            .get(&topic)
            .is_some_and(|class| *class != P::CLASS)
        {
            return Some(Err(TcnError::ClassMismatch));
        }
        let queue = self.queues.get_mut(&topic)?;
        let bytes = queue.pop_front()?;
        Some(serde_json::from_slice(&bytes).map_err(|_| TcnError::DecodeError))
    }

    /// Drain all queued payloads on a topic in FIFO order.
    pub fn drain<P: TcnPayload>(&mut self, topic: TopicId) -> Vec<P> {
        let mut out = Vec::new();
        while let Some(Ok(p)) = self.recv_one::<P>(topic) {
            out.push(p);
        }
        out
    }

    /// Number of queued payloads on a topic.
    #[must_use]
    pub fn depth(&self, topic: TopicId) -> usize {
        self.queues.get(&topic).map_or(0, VecDeque::len)
    }

    /// Lifetime drop count for a topic.
    #[must_use]
    pub fn drops(&self, topic: TopicId) -> u64 {
        self.drops.get(&topic).copied().unwrap_or(0)
    }

    /// Lifetime publish count for a topic.
    #[must_use]
    pub fn published(&self, topic: TopicId) -> u64 {
        self.published.get(&topic).copied().unwrap_or(0)
    }
}

impl Default for MockTcn {
    fn default() -> Self {
        Self::new()
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use serde::{Deserialize, Serialize};

    #[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
    struct TestSafetyPayload {
        value: i32,
        ts: u64,
    }
    impl TcnPayload for TestSafetyPayload {
        const CLASS: TrafficClass = TrafficClass::Safety;
    }

    #[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
    struct TestAppPayload {
        text: String,
    }
    impl TcnPayload for TestAppPayload {
        const CLASS: TrafficClass = TrafficClass::App;
    }

    fn topic(tcn: &MockTcn, name: &str) -> TopicId {
        tcn.registry.id(name).expect("topic")
    }

    #[test]
    fn publish_and_receive() {
        let mut tcn = MockTcn::new();
        let t = topic(&tcn, "osr.train.atp.envelope");
        let p = TestSafetyPayload { value: 42, ts: 100 };
        tcn.publish(t, &p).unwrap();
        let got: TestSafetyPayload = tcn.recv_one(t).unwrap().unwrap();
        assert_eq!(got, p);
    }

    #[test]
    fn fifo_order() {
        let mut tcn = MockTcn::new();
        let t = topic(&tcn, "osr.train.atp.envelope");
        for i in 0..5 {
            tcn.publish(t, &TestSafetyPayload { value: i, ts: 0 })
                .unwrap();
        }
        let drained: Vec<_> = tcn.drain::<TestSafetyPayload>(t);
        assert_eq!(
            drained.iter().map(|p| p.value).collect::<Vec<_>>(),
            vec![0, 1, 2, 3, 4]
        );
    }

    #[test]
    fn safety_errors_on_overflow() {
        let mut tcn = MockTcn::new();
        let t = topic(&tcn, "osr.train.atp.envelope");
        tcn.set_capacity(t, 3);
        for i in 0..3 {
            tcn.publish(t, &TestSafetyPayload { value: i, ts: 0 })
                .unwrap();
        }
        // 4th publish fails.
        let err = tcn.publish(t, &TestSafetyPayload { value: 99, ts: 0 });
        assert_eq!(err, Err(TcnError::QueueFull));
    }

    #[test]
    fn app_drops_oldest_on_overflow() {
        let mut tcn = MockTcn::new();
        let t = topic(&tcn, "osr.train.pis.display");
        tcn.set_capacity(t, 3);
        for i in 0..5 {
            tcn.publish(
                t,
                &TestAppPayload {
                    text: format!("{i}"),
                },
            )
            .unwrap();
        }
        assert_eq!(tcn.depth(t), 3);
        assert_eq!(tcn.drops(t), 2);
        let drained: Vec<_> = tcn.drain::<TestAppPayload>(t);
        // Oldest two dropped; [2, 3, 4] remain.
        assert_eq!(
            drained.iter().map(|p| p.text.clone()).collect::<Vec<_>>(),
            vec!["2", "3", "4"]
        );
    }

    #[test]
    fn topic_isolation() {
        let mut tcn = MockTcn::new();
        let a = topic(&tcn, "osr.train.atp.envelope");
        let b = topic(&tcn, "osr.train.atp.command");
        tcn.publish(a, &TestSafetyPayload { value: 1, ts: 0 })
            .unwrap();
        assert!(tcn.recv_one::<TestSafetyPayload>(b).is_none());
        assert!(tcn.recv_one::<TestSafetyPayload>(a).unwrap().is_ok());
    }

    #[test]
    fn depth_and_counters_track() {
        let mut tcn = MockTcn::new();
        let t = topic(&tcn, "osr.train.atp.envelope");
        for i in 0..3 {
            tcn.publish(t, &TestSafetyPayload { value: i, ts: 0 })
                .unwrap();
        }
        assert_eq!(tcn.depth(t), 3);
        assert_eq!(tcn.published(t), 3);
        assert_eq!(tcn.drops(t), 0);
    }
}
