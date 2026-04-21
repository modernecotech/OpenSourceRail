//! Property tests for osr-tcn — T1 through T5.

use osr_tcn::{MockTcn, TcnPayload, TopicId, TrafficClass};
use proptest::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
struct SafetyMsg {
    value: i64,
    ts: u64,
}
impl TcnPayload for SafetyMsg {
    const CLASS: TrafficClass = TrafficClass::Safety;
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
struct AppMsg {
    text: String,
    code: u32,
}
impl TcnPayload for AppMsg {
    const CLASS: TrafficClass = TrafficClass::App;
}

fn safety_topic(tcn: &MockTcn) -> TopicId {
    tcn.registry.id("osr.train.atp.envelope").unwrap()
}

fn app_topic(tcn: &MockTcn) -> TopicId {
    tcn.registry.id("osr.train.pis.display").unwrap()
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    /// T1 + T2: round-trip identity and FIFO order for Safety class.
    #[test]
    fn t1_t2_safety_roundtrip_fifo(msgs in prop::collection::vec((any::<i64>(), any::<u64>()), 0..50)) {
        let mut tcn = MockTcn::new();
        let t = safety_topic(&tcn);
        for (v, ts) in &msgs {
            tcn.publish(t, &SafetyMsg { value: *v, ts: *ts }).unwrap();
        }
        let drained: Vec<SafetyMsg> = tcn.drain(t);
        let expected: Vec<SafetyMsg> = msgs.iter().map(|(v, ts)| SafetyMsg { value: *v, ts: *ts }).collect();
        prop_assert_eq!(drained, expected);
    }

    /// T3: Safety never silently drops. With default capacity
    /// (256) and fewer publishes, all messages survive.
    #[test]
    fn t3_safety_never_silently_drops(msgs in prop::collection::vec((any::<i64>(), any::<u64>()), 0..100)) {
        let mut tcn = MockTcn::new();
        let t = safety_topic(&tcn);
        for (v, ts) in &msgs {
            tcn.publish(t, &SafetyMsg { value: *v, ts: *ts }).unwrap();
        }
        prop_assert_eq!(tcn.drops(t), 0);
        prop_assert_eq!(tcn.depth(t), msgs.len());
    }

    /// T4: App class drops under back-pressure. Exactly
    /// `excess = n - capacity` drops, and the surviving N entries
    /// are the most recent N.
    #[test]
    fn t4_app_drops_under_backpressure(
        capacity in 1usize..=8,
        msgs in prop::collection::vec(("[a-z]{1,4}", any::<u32>()), 0..30),
    ) {
        let mut tcn = MockTcn::new();
        let t = app_topic(&tcn);
        tcn.set_capacity(t, capacity);
        for (text, code) in &msgs {
            tcn.publish(t, &AppMsg { text: text.clone(), code: *code }).unwrap();
        }
        let expected_drops = msgs.len().saturating_sub(capacity) as u64;
        prop_assert_eq!(tcn.drops(t), expected_drops);
        prop_assert_eq!(tcn.depth(t), msgs.len().min(capacity));
        // The surviving messages should be the most recent.
        let drained: Vec<AppMsg> = tcn.drain(t);
        let expected_tail: Vec<AppMsg> = msgs
            .iter()
            .rev()
            .take(capacity)
            .rev()
            .map(|(t, c)| AppMsg { text: t.clone(), code: *c })
            .collect();
        prop_assert_eq!(drained, expected_tail);
    }

    /// T5: topic isolation — a publish on topic A never appears on
    /// topic B's queue.
    #[test]
    fn t5_topic_isolation(msg in (any::<i64>(), any::<u64>())) {
        let mut tcn = MockTcn::new();
        let a = safety_topic(&tcn);
        let b = tcn.registry.id("osr.train.atp.command").unwrap();
        tcn.publish(a, &SafetyMsg { value: msg.0, ts: msg.1 }).unwrap();
        prop_assert_eq!(tcn.depth(a), 1);
        prop_assert_eq!(tcn.depth(b), 0);
        prop_assert!(tcn.recv_one::<SafetyMsg>(b).is_none());
    }
}
