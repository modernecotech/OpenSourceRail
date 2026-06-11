//! UDP-based "real" TCN transport.
//!
//! Same surface as [`crate::MockTcn`] — `publish(topic, payload)` and
//! `recv_one::<P>(topic)` — but backed by a real UDP socket. Designed
//! to be the simplest thing that works on commodity Linux so an
//! operator can move from the in-memory mock to a multi-host bench
//! without changing any payload crate.
//!
//! # Wire format (v1)
//!
//! Each UDP datagram carries exactly one message:
//!
//! ```text
//!   offset  bytes  field
//!   ------  -----  -----
//!   0       2      topic_id (u16, big-endian)
//!   2       1      traffic_class (0 = Safety, 1 = Control, 2 = App)
//!   3       2      payload_len (u16, big-endian)
//!   5       N      payload_bytes (serde_json)
//! ```
//!
//! Maximum datagram size is the MTU minus the IP/UDP headers. In
//! practice with an Ethernet MTU of 1500 we keep payloads ≤ 1460
//! bytes; larger payloads need a separate fragmentation scheme which
//! is deferred to v2.
//!
//! # Reliability
//!
//! UDP is unreliable. The payload-validation discipline of every
//! consumer (RFC 0005 §13 — "a missing frame triggers fail-restrictive
//! timeouts in the consumer") means this is acceptable for
//! operational traffic and, after authentication lands in
//! [`osr-crypto`](../../osr-crypto/), for safety-relevant traffic
//! as well.
//!
//! # Non-goals (v1)
//!
//! - No TSN (IEEE 802.1Qbv) scheduling. That is hardware-layer
//!   behaviour; this crate runs on top of whatever the NIC queue
//!   provides.
//! - No fragmentation.
//! - No mTLS / signing — that goes through [`osr-crypto`] once the
//!   TLS + ed25519 paths land.
//! - No multicast configuration. Multicast is a trivial extension
//!   (bind to a group, `join_multicast_v4`); v1 is unicast to a list
//!   of peer sockets so the test harness is deterministic.

use std::collections::{BTreeMap, VecDeque};
use std::io;
use std::net::{SocketAddr, UdpSocket};
use std::time::Duration;

use crate::mock::TcnError;
use crate::payload::{TcnPayload, TrafficClass};
use crate::registry::{TopicId, TopicRegistry};

/// UDP-backed TCN transport. Holds one bound socket plus a list of
/// unicast peers; every publish sends one datagram per peer.
#[derive(Debug)]
pub struct UdpTcn {
    pub registry: TopicRegistry,
    socket: UdpSocket,
    peers: Vec<SocketAddr>,
    rx_buffer: BTreeMap<TopicId, VecDeque<Vec<u8>>>,
    classes: BTreeMap<TopicId, TrafficClass>,
    published: BTreeMap<TopicId, u64>,
    drops: BTreeMap<TopicId, u64>,
}

/// Maximum payload length carried in one datagram (header aside).
/// Stays conservatively inside a 1500-byte Ethernet MTU.
pub const MAX_PAYLOAD_LEN: usize = 1400;
/// Fixed header size: topic(2) + class(1) + len(2).
pub const HEADER_LEN: usize = 5;

impl UdpTcn {
    /// Bind a new transport to `bind_addr` with `peers` as the list of
    /// unicast targets every publish fans out to. The socket is set
    /// non-blocking so `poll_tick` can be called from an event loop.
    ///
    /// `bind_addr` can be a host:port (`"0.0.0.0:0"` for an
    /// ephemeral port) — useful for tests that want the OS to pick.
    pub fn bind(bind_addr: &str, peers: Vec<SocketAddr>) -> io::Result<Self> {
        let socket = UdpSocket::bind(bind_addr)?;
        socket.set_nonblocking(true)?;
        Ok(Self {
            registry: TopicRegistry::builtin(),
            socket,
            peers,
            rx_buffer: BTreeMap::new(),
            classes: BTreeMap::new(),
            published: BTreeMap::new(),
            drops: BTreeMap::new(),
        })
    }

    /// The local address the transport is bound to. Handy for tests
    /// that ask the OS to pick a port and then hand it to a peer.
    pub fn local_addr(&self) -> io::Result<SocketAddr> {
        self.socket.local_addr()
    }

    /// Add a peer after construction.
    pub fn add_peer(&mut self, peer: SocketAddr) {
        self.peers.push(peer);
    }

    /// Publish a typed payload. Serialises with `serde_json`,
    /// prepends the header, and sends one datagram per peer.
    pub fn publish<P: TcnPayload>(&mut self, topic: TopicId, payload: &P) -> Result<(), TcnError> {
        self.classes.insert(topic, P::CLASS);
        let bytes = serde_json::to_vec(payload).map_err(|_| TcnError::DecodeError)?;
        if bytes.len() > MAX_PAYLOAD_LEN {
            return Err(TcnError::QueueFull);
        }

        let mut datagram = Vec::with_capacity(HEADER_LEN + bytes.len());
        datagram.extend_from_slice(&topic.0.to_be_bytes());
        datagram.push(class_tag(P::CLASS));
        datagram.extend_from_slice(&u16::try_from(bytes.len()).unwrap_or(0).to_be_bytes());
        datagram.extend_from_slice(&bytes);

        for peer in &self.peers {
            match self.socket.send_to(&datagram, peer) {
                Ok(_) => {}
                Err(e) if e.kind() == io::ErrorKind::WouldBlock => {
                    // Kernel buffer full — count as a drop for
                    // App/Control and escalate for Safety.
                    match P::CLASS {
                        TrafficClass::Safety => return Err(TcnError::QueueFull),
                        _ => {
                            *self.drops.entry(topic).or_insert(0) += 1;
                        }
                    }
                }
                Err(_) => {
                    // Any other send error (no route, host down) is
                    // treated as a drop at this layer; the caller
                    // will notice via the consumer-side timeout.
                    *self.drops.entry(topic).or_insert(0) += 1;
                }
            }
        }

        *self.published.entry(topic).or_insert(0) += 1;
        Ok(())
    }

    /// Drain whatever has arrived on the socket into the per-topic
    /// buffers. Returns the number of messages received. Non-blocking
    /// — schedule it on your event loop.
    pub fn poll_tick(&mut self) -> usize {
        let mut buf = [0u8; HEADER_LEN + MAX_PAYLOAD_LEN];
        let mut received = 0;
        loop {
            match self.socket.recv_from(&mut buf) {
                Ok((n, _from)) => {
                    if n < HEADER_LEN {
                        continue;
                    }
                    let topic_raw = u16::from_be_bytes([buf[0], buf[1]]);
                    let _class = buf[2];
                    let len = u16::from_be_bytes([buf[3], buf[4]]) as usize;
                    if HEADER_LEN + len > n {
                        continue;
                    }
                    let bytes = buf[HEADER_LEN..HEADER_LEN + len].to_vec();
                    let topic = TopicId(topic_raw);
                    self.rx_buffer.entry(topic).or_default().push_back(bytes);
                    received += 1;
                }
                Err(e) if e.kind() == io::ErrorKind::WouldBlock => break,
                Err(_) => break,
            }
        }
        received
    }

    /// Block up to `timeout` for at least one message to arrive, then
    /// drain. Helper for tests that want a synchronous round-trip.
    pub fn poll_until(&mut self, timeout: Duration) -> io::Result<usize> {
        self.socket.set_read_timeout(Some(timeout))?;
        let res = {
            let mut buf = [0u8; HEADER_LEN + MAX_PAYLOAD_LEN];
            match self.socket.recv_from(&mut buf) {
                Ok((n, _from)) => {
                    if n >= HEADER_LEN {
                        let topic_raw = u16::from_be_bytes([buf[0], buf[1]]);
                        let len = u16::from_be_bytes([buf[3], buf[4]]) as usize;
                        if HEADER_LEN + len <= n {
                            let bytes = buf[HEADER_LEN..HEADER_LEN + len].to_vec();
                            let topic = TopicId(topic_raw);
                            self.rx_buffer.entry(topic).or_default().push_back(bytes);
                            Ok(1)
                        } else {
                            Ok(0)
                        }
                    } else {
                        Ok(0)
                    }
                }
                Err(e)
                    if e.kind() == io::ErrorKind::WouldBlock
                        || e.kind() == io::ErrorKind::TimedOut =>
                {
                    Ok(0)
                }
                Err(e) => Err(e),
            }
        };
        // Restore non-blocking mode for subsequent poll_tick calls.
        self.socket.set_nonblocking(true)?;
        let _ = self.socket.set_read_timeout(None);
        res.map(|n| {
            let extra = self.poll_tick();
            n + extra
        })
    }

    /// Dequeue the oldest received payload on `topic`, if any. Same
    /// signature as `MockTcn::recv_one`.
    pub fn recv_one<P: TcnPayload>(&mut self, topic: TopicId) -> Option<Result<P, TcnError>> {
        let queue = self.rx_buffer.get_mut(&topic)?;
        let bytes = queue.pop_front()?;
        Some(serde_json::from_slice(&bytes).map_err(|_| TcnError::DecodeError))
    }

    /// Drain all received payloads on a topic.
    pub fn drain<P: TcnPayload>(&mut self, topic: TopicId) -> Vec<P> {
        let mut out = Vec::new();
        while let Some(Ok(p)) = self.recv_one::<P>(topic) {
            out.push(p);
        }
        out
    }

    #[must_use]
    pub fn depth(&self, topic: TopicId) -> usize {
        self.rx_buffer.get(&topic).map_or(0, VecDeque::len)
    }

    #[must_use]
    pub fn published(&self, topic: TopicId) -> u64 {
        self.published.get(&topic).copied().unwrap_or(0)
    }

    #[must_use]
    pub fn drops(&self, topic: TopicId) -> u64 {
        self.drops.get(&topic).copied().unwrap_or(0)
    }
}

fn class_tag(c: TrafficClass) -> u8 {
    match c {
        TrafficClass::Safety => 0,
        TrafficClass::Control => 1,
        TrafficClass::App => 2,
    }
}

// ---------------------------------------------------------------------------
// Tests — two local transports round-tripping a payload on the loopback.
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

    fn pair() -> (UdpTcn, UdpTcn) {
        let a = UdpTcn::bind("127.0.0.1:0", vec![]).expect("bind a");
        let b = UdpTcn::bind("127.0.0.1:0", vec![]).expect("bind b");
        let a_addr = a.local_addr().expect("a addr");
        let b_addr = b.local_addr().expect("b addr");
        let mut a = a;
        let mut b = b;
        a.add_peer(b_addr);
        b.add_peer(a_addr);
        (a, b)
    }

    fn topic_id(tcn: &UdpTcn, name: &str) -> TopicId {
        tcn.registry.id(name).expect("topic")
    }

    #[test]
    fn roundtrip_single_payload() {
        let (mut a, mut b) = pair();
        let t = topic_id(&a, "osr.train.atp.envelope");
        let p = TestSafetyPayload {
            value: 42,
            ts: 1_000,
        };
        a.publish(t, &p).expect("publish");
        // Give the kernel one round-trip on the loopback; 100 ms is
        // generous under any scheduling jitter.
        let n = b.poll_until(Duration::from_millis(100)).expect("poll");
        assert!(n >= 1, "expected at least one message, got {n}");
        let got: TestSafetyPayload = b.recv_one(t).expect("queued").expect("decode");
        assert_eq!(got, p);
    }

    #[test]
    fn fifo_per_topic() {
        let (mut a, mut b) = pair();
        let t = topic_id(&a, "osr.train.atp.envelope");
        for i in 0..5 {
            a.publish(t, &TestSafetyPayload { value: i, ts: 0 })
                .expect("publish");
        }
        // Poll repeatedly until all 5 land or we time out overall.
        let mut received = 0;
        for _ in 0..20 {
            received += b.poll_until(Duration::from_millis(50)).unwrap_or(0);
            if received >= 5 {
                break;
            }
        }
        assert!(received >= 5, "only got {received}/5");
        let drained: Vec<_> = b.drain::<TestSafetyPayload>(t);
        assert_eq!(
            drained.iter().map(|p| p.value).collect::<Vec<_>>(),
            vec![0, 1, 2, 3, 4]
        );
    }

    #[test]
    fn topic_isolation() {
        let (mut a, mut b) = pair();
        let t1 = topic_id(&a, "osr.train.atp.envelope");
        let t2 = topic_id(&a, "osr.train.atp.command");
        a.publish(t1, &TestSafetyPayload { value: 1, ts: 0 })
            .expect("publish");
        let _ = b.poll_until(Duration::from_millis(100)).unwrap_or(0);
        assert!(b.recv_one::<TestSafetyPayload>(t2).is_none());
        assert!(b.recv_one::<TestSafetyPayload>(t1).is_some());
    }
}
