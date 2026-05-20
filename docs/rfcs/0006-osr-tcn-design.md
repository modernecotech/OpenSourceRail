# RFC 0006 — `osr-tcn` design

**Status:** Draft 1.1 (2026-04-22) — v1 crate landed, v1.5 UDP transport landed
**Depends on:** [RFC 0005 SBC Software Architecture](0005-sbc-software-architecture.md)
**Supersedes part of:** [ARCHITECTURE.md §D5 trainbus description](../ARCHITECTURE.md#d5-rolling-stock)

## 1. Summary

`osr-tcn` is the on-train communications stack. It implements a
narrow, deterministic publish-subscribe layer over IEC 61375-2-3
Ethernet TRDP, providing the bus on which every onboard crate
exchanges state. This RFC specifies the topic namespace, payload
encoding, traffic classes, time synchronisation, and API shape —
before any code is written.

This is Phase 2c's biggest remaining design decision and the only
RFC-level question left for the onboard stack. Every existing
onboard crate produces or consumes data that will flow over TCN-E;
getting the bus shape right *once* is worth an explicit design pass.

## 2. Goals and non-goals

### 2.1 Goals

1. **Deterministic delivery** of safety-relevant messages within a
   bounded latency, using IEEE 802.1 TSN Qbv time-aware scheduling.
2. **Topic-addressed publish/subscribe** — producers don't know
   consumers by name; the topic is the contract.
3. **Zero-allocation publish path** on the Rust side. Safety-tier
   crates (T1/T2 per RFC 0005 §6.1) publish into pre-allocated
   frames without heap traffic.
4. **Compact binary payloads** — integer-only wire format matching
   the safety-path discipline of the producer crates.
5. **Testable in software** — a mock transport drives the same
   crate API so unit tests exercise real publish/subscribe without
   hardware.
6. **PTP time sync** fan-out so every onboard clock reads the same
   `now_ns` to within TSN's accuracy budget (sub-microsecond for
   the safety partition, sub-millisecond for applications).

### 2.2 Non-goals

- **Security beyond network segmentation.** mTLS / signing sits in
  [`osr-crypto`](#12-relationship-to-osr-crypto-and-osr-t2g)
  (future) on top of TCN-E. TCN itself is physical-layer secured
  by the partition isolation described in RFC 0005 §9.
- **Dynamic membership.** The consist's ECU inventory is fixed at
  commissioning. No hotplug; no membership negotiation at runtime.
- **Legacy MVB/WTB bridging.** RFC 0005 §10 deprecates both. No
  shim, no retrofit.
- **Train-to-train coupling.** TCN-E is intra-consist. Multi-unit
  coupling is a separate RFC.

## 3. Standards alignment

- **IEC 61375-2-3** — Train Communication Network, Ethernet TRDP
  profile. Defines the message layout and service classes.
- **IEEE 802.1Qbv** — Time-Aware Shaper. Gates output ports on a
  scheduled calendar so safety traffic is never blocked behind
  elephant flows.
- **IEEE 802.1Qbu / 802.3br** — Frame Preemption. Allows a safety
  frame to preempt an in-flight best-effort frame.
- **IEEE 1588-2019 / 802.1AS** — PTP time sync. Sub-microsecond
  accuracy across the bus.
- **IEC 61375-3-4** — Ethernet consist network (bounds the physical
  topology: backbone switches + stub links to ECUs).

## 4. Physical topology (reference)

A 3-car light-metro consist per RFC 0003:

```
  ┌── Cab A (T-ECU/S × 2, T-ECU/A × 1) ──┐
  │                                        │
  │    TSN switch A ── 1 Gbps copper ──┐   │
  │         │                           │   │
  │         │                        ┌──┴────────────┐
  │         │                        │ Inter-car     │ (single fibre pair, PTP)
  │         │                        │   backbone    │
  │         │                        │               │
  │    Axle-end sensors           ──►│               │◄── Door panels
  │    Traction drive             ──►│               │◄── HVAC
  │    BMS                        ──►│               │◄── Event recorder
  │                                  └──┬────────────┘
  │                                     │
  ┌── Cab B (mirror of Cab A) ────────┐ │
  │    TSN switch B ← ─ fibre ─ ← ─ ──┘ │
  │                                     │
  └─────────────────────────────────────┘
```

Every ECU has exactly one link (1 Gbps copper) to its cab's TSN
switch; cab switches link to each other via a fibre pair running
the length of the consist. The backbone tolerates a single fibre
cut (either A or B still reaches everyone via the intact link);
both cut puts the consist into a safe-state stop via ATP time-out.

## 5. Topic namespace

Topics are hierarchical dotted strings. The first segment is the
*producer domain*, the second is the *message class*, subsequent
segments are qualifiers:

```
osr.train.atp.envelope
osr.train.atp.command
osr.train.brake.apply
osr.train.odom.position
osr.train.odom.speed
osr.train.traction.torque_setpoint
osr.train.traction.current_estimate
osr.train.bms.soc
osr.train.bms.limits
osr.train.bms.fault
osr.train.door.status           (per-door idx: osr.train.door.status.3)
osr.train.door.interlock
osr.train.hvac.status
osr.train.lighting.status
osr.train.pis.display
osr.train.pis.announcement
osr.train.dmi.page
osr.train.dmi.driver_input
osr.train.tcms.consist_status
osr.train.monitors.fire
osr.train.monitors.derailment
osr.train.monitors.vigilance
osr.train.monitors.hot_axle
osr.train.monitors.aux_power
osr.train.event.record          (event-recorder entries)
```

**Design choice:** dotted hierarchical topics, not numeric IDs.
Hierarchy lets subscribers use prefix filters
(`osr.train.monitors.*`) without a lookup table. The cost —
slightly larger frames — is not the bottleneck on a 1 Gbps link
with ~100 topics.

On the wire the topic is interned to a 16-bit ID by the publisher's
TCN stack (`osr-tcn` maintains a deterministic string → u16 map
populated at boot from a static config file); consumers see both
the interned ID and, on-demand, the full string. The intern table
is part of the bring-up handshake and must match across every
ECU in the consist.

## 6. Payload encoding

### 6.1 Rule

Every payload is a fixed-size, endian-normalised (little-endian)
byte layout defined as a Rust `#[repr(C)]` struct in a shared
payload crate (`osr-tcn-payloads`, or a module under
`osr-tcn`). Producers serialise by `core::mem::transmute`-less
byte-copying (`bytemuck::bytes_of(&payload)`); consumers the
reverse. This gives the safety crates a zero-allocation,
zero-parsing publish path.

### 6.2 Why not protobuf / CBOR / JSON

- **Variable-size encodings** complicate bounded-latency proofs.
  TSN Qbv reserves a fixed number of bytes per safety slot; a
  fixed-size payload is a natural fit.
- **Schema evolution** happens at the topic level (new topic =
  new schema); we don't need per-field tagging.
- **Test ergonomics:** Rust struct == wire layout makes
  round-trip testing trivial.
- **Certification:** a safety case that says "this byte at this
  offset is the MA validity-window" is far easier to audit than
  one that threads through a protobuf decoder.

### 6.3 Alignment and endianness

- All integer fields little-endian.
- All struct fields `#[repr(C)]`, explicit padding where needed.
- Maximum payload size per TRDP PD (Process Data) message: 1432
  bytes. Most payloads are 16–64 bytes.
- Larger payloads (e.g., CCTV keyframes) go over TRDP MD (Message
  Data) in a separate channel, not addressed in this RFC.

### 6.4 Example payload (MA envelope)

```rust
#[repr(C)]
#[derive(Copy, Clone, Debug, PartialEq, Eq, bytemuck::Pod, bytemuck::Zeroable)]
pub struct AtpEnvelopePayload {
    pub now_ns: u64,
    pub envelope_mmps: i32,
    pub distance_to_end_mm: i64,
    pub has_known_position: u8,
    pub _pad: [u8; 3],
    pub trigger_reason: u8,
    pub _pad2: [u8; 7],
}
// sizeof == 32
```

`bytemuck::Pod` + `Zeroable` give safe transmute semantics without
`unsafe`. The workspace-level `forbid(unsafe_code)` is preserved.

## 7. Traffic classes

Three classes, mapped to 802.1Q priority codes per Qbv gate
schedule:

| Class | PCP | Slot type | Example topics |
|-------|-----|-----------|----------------|
| **Safety** (S) | 7 | Guaranteed slot every 1 ms | `atp.envelope`, `brake.apply`, `odom.position`, `monitors.*` |
| **Control** (C) | 5 | Guaranteed slot every 10 ms | `traction.torque_setpoint`, `bms.limits`, `door.status` |
| **App** (A) | 3 | Best-effort, preemptible | `hvac.status`, `pis.display`, `dmi.page`, `event.record` |

A safety-class publish uses a pre-allocated buffer and transmits
in its next Qbv slot — bounded latency < 1 ms. The publisher's
Rust API must not spin-wait; if the TCN stack's internal queue is
full (which should be unreachable under a correctly sized bus),
the publish returns an error and the caller records a
`TcnError::QueueFull` event.

## 8. Time synchronisation

- **Grandmaster:** the primary T-ECU/S in cab A. Runs a PPS-locked
  oscillator if available; otherwise free-runs its TCXO.
- **Secondary:** the primary T-ECU/S in cab B. Takes over on
  grandmaster timeout (standard IEEE 1588 BMC algorithm).
- **Slaves:** every other ECU. Maintain ≤ 1 µs offset to
  grandmaster for safety-tier timestamps.

The `now_ns` parameter that every evaluator (ATP, ATO, BMS, etc.)
consumes is read from the local PTP-disciplined clock. Callers
must not mix PTP time with monotonic `std::time::Instant` on the
publish path.

## 9. Crate API

### 9.1 Publisher side

```rust
pub struct Tcn {
    // implementation detail
}

impl Tcn {
    pub fn publish<P: TcnPayload>(
        &self,
        topic: TopicId,
        payload: &P,
    ) -> Result<(), TcnError>;
}

pub trait TcnPayload: bytemuck::Pod {
    const CLASS: TrafficClass;
    const SIZE: usize;
}
```

### 9.2 Subscriber side

Two modes:

- **Blocking read** (unit tests, non-hot-path): `recv(topic) -> Option<&P>`.
- **Callback registration** (hot path, safety crates): at init
  time, subscribe with a `fn(&P)` that the stack invokes on
  receipt. The callback runs in the ECU's deterministic tick, not
  in an interrupt handler.

### 9.3 Mock transport for tests

```rust
pub struct MockTcn { /* in-memory bag of (topic, payload) tuples */ }
impl MockTcn {
    pub fn publish<P>(&mut self, topic: TopicId, payload: &P);
    pub fn drain<P>(&mut self, topic: TopicId) -> Vec<P>;
}
```

The mock drives the real crate API — every existing onboard crate
can be fed into it without change. This is how `osr-sim`'s
shadow stack will exercise the full publish/subscribe chain in
the simulator.

## 10. Scope of v1 implementation

The first cut ships:

1. Topic ID interning (static config file → `TopicId` enum).
2. Payload trait + derive macro (or explicit `bytemuck::Pod`
   impls for now — macro is follow-up).
3. In-memory mock transport with traffic-class awareness.
4. Proptest harness verifying:
   - Round-trip encode/decode produces byte-identical output.
   - Safety-class messages are delivered in publish order.
   - Class-A messages may be dropped under backpressure; class-S
     never drops.

Out of scope for v1:

- Real TSN hardware driver — needs a kernel driver story (DPDK
  vs `AF_XDP` vs stock socket). Separate RFC.
- PTP client — use a userspace `ptp4l` + Linux PHC until we
  write a bare-metal one for Hubris.
- `osr-tcn-payloads` split out of `osr-tcn` — reasonable at
  scale, premature now.

## 11. Rollout

| Phase | Deliverable | Dependencies |
|-------|-------------|--------------|
| **v0** | This RFC ratified | — |
| **v1** ✅ | `osr-tcn` crate with mock transport + topic registry + proptests | — |
| **v1.5** ✅ | Real network transport (`UdpTcn`) on commodity UDP — drop-in API replacement for `MockTcn`, loopback round-trip tested; the simplest thing that works for a multi-host bench (done 2026-04-22) | v1 |
| **v2** | Integration into `osr-sim` shadow: publish/subscribe replaces direct field access | v1 |
| **v3** | Real TSN driver (Linux `AF_XDP` first, Hubris bare-metal later) | reference hardware RFC |
| **v4** | PTP client + grandmaster fail-over | v3 |

v1.5 is deliberately a small step past v1. It preserves the MockTcn
contract so downstream crates never see the transport; what changes
is only whether bytes travel through a BTreeMap or through the
kernel UDP stack. This gives operators a working multi-host bench
without pulling in DPDK / AF_XDP complexity, which stays in v3 where
the hardware story is fixed.

## 12. Relationship to `osr-crypto` and `osr-t2g`

- **`osr-crypto`** provides HMAC-signing
  of safety-class payloads for defense-in-depth against a
  compromised ECU. Sign/verify wraps the Pod layout; wire format
  stays fixed-size.
- **`osr-t2g`** sits *outside* TCN and takes its inputs from
  specific TCN topics. TCN frames do not leave the consist;
  ground-bound telemetry is re-serialised (likely in a
  bandwidth-efficient encoding like CBOR) before transmission.

## 13. Open questions

1. **Topic ID collisions across firmware versions.** The intern
   map must be version-stable within a consist or the bus
   silently routes to the wrong subscriber. Solution sketch: the
   intern map is derived from a canonical SHA-256 of the sorted
   topic list; consists bootstrap-verify that all ECUs agree.
2. **Payload schema evolution.** Today: new topic = new schema.
   At some point we'll want to extend an existing payload
   backwards-compatibly. Deferred until a concrete need arises.
3. **Multicast vs unicast.** Most TRDP PD is multicast; control
   flows (e.g., `door.command` from a central door controller to
   specific doors) could be unicast. Current plan: everything
   multicast with subscriber filtering, simplifies the stack.
4. **No-std on Hubris.** `bytemuck::Pod` is `no_std`-friendly;
   the current `std` usage in `osr-tcn` would need the same
   treatment the other SIL-4 crates receive in the no_std
   migration (RFC 0005 §7 ongoing).

## 14. Done criteria

- [ ] RFC ratified by reviewer(s).
- [ ] v1 crate lands with mock transport, topic registry, and
      ≥ 6 proptest-verified properties.
- [ ] Existing SIL-4 crates compile against the `TcnPayload`
      trait for at least one topic each (e.g., `osr-atp`
      exports `AtpEnvelopePayload`).

v1 implementation follows this session after the RFC is stable.
