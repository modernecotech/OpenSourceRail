# RFC 0001 — Track State Consensus

**Status:** Draft
**Date:** 2026-04-20
**Depends on:** [docs/ARCHITECTURE.md](../ARCHITECTURE.md) §4 D2

## 1. Summary

OpenSourceRail replaces the centralized zone-controller model of conventional CBTC with a **distributed, replicated log of track state** maintained by wayside nodes via a consensus protocol. Each train computes its own Movement Authority (MA) from the log, cross-validated by two independent wayside nodes. This RFC specifies the log schema, the consensus protocol, the MA computation algorithm, the fault model, and the formal-verification plan.

The design target is **SIL-4 safety** at **<€5k per wayside site** in reference-hardware cost, with **p99 end-to-end MA update latency <200 ms**.

## 2. Motivation

Conventional CBTC (Siemens Trainguard, Alstom Urbalis, Thales SelTrac) concentrates authority in a **Zone Controller (ZC)** — a redundant pair of proprietary computers per line or per large segment. The ZC:

- Is a single logical point of failure. When it fails, the whole zone falls back to degraded manual operation.
- Is a single vendor product. Swapping it out is a multi-year, eight-figure project.
- Is opaque. Its internal state machine is not published; operators cannot inspect it; assessors re-derive correctness per certification.
- Costs €10–50M per line, before rolling-stock ATP costs.

A distributed log replaces the ZC with **N commodity wayside nodes** that collectively hold authoritative state. Any quorum-majority subset continues operating. No single failure stops service. The log is the specification: state is a function of committed entries, and the state machine is public.

This is cheaper, simpler, more resilient, and more auditable — *provided* we can prove the distributed protocol is safe. That proof is the heart of this RFC.

## 3. Non-goals

- **Not a general-purpose database.** The log carries a bounded, well-typed set of rail-domain facts. We do not aim for SQL, secondary indexes, or arbitrary queries.
- **Not Byzantine-fault-tolerant in v1.** Wayside nodes are operated by a single authority, run signed firmware, and attest at boot (see ARCHITECTURE.md §8). We trust them to follow protocol or crash. Byzantine resilience may be added in v2 but it is not required to close the SIL-4 safety case.
- **Not a replacement for ATP onboard.** Onboard Automatic Train Protection (emergency brake on MA violation) remains the last line of defense. The log defines *what is allowed*; onboard ATP enforces *what actually happens*.
- **Not globally consistent across regions.** Consensus is per **region** (§6.1). Region boundaries are handled via a handoff protocol (§7.4), not global consensus.

## 4. Concepts and Vocabulary

| Term | Meaning |
|---|---|
| **Region** | A contiguous operating area of ~5–50 km covered by 5–20 wayside nodes in a single consensus group. |
| **Wayside Node (W-Node)** | SBC running the consensus + interlocking stack at a physical site (station, junction, substation). |
| **Train Agent** | Software on a train's T-ECU that publishes position reports, computes MA, and enforces ATP. |
| **Log** | The append-only, totally-ordered, quorum-committed sequence of facts about the region. |
| **Entry** | A single typed record in the log (§5). |
| **Movement Authority (MA)** | A permission for a specific train to occupy a specific set of track sections up to a specific position, valid until a specific time. |
| **Safety Envelope** | The union of track sections a train may occupy without colliding with anything, given current log state. A train's MA is always a subset of its safety envelope. |
| **Commit** | An entry has been accepted by a quorum majority and is durable. |
| **Fail-safe direction** | In rail, the fail-safe state is "stopped." Any ambiguity must resolve toward more restrictive MA, not less. |

## 5. The Log

The log is a sequence of entries. Each entry has:

- `entry_id`: monotonic u64, unique within region
- `term`: consensus term (Raft-style)
- `timestamp`: TAI nanoseconds, PTP-synced wall clock at the leader
- `kind`: one of the entry types below
- `payload`: typed body
- `signature`: ed25519, signed by the leader's hardware key (for audit; not load-bearing for consensus)

### 5.1 Entry types

```
TrainPositionReport {
  train_id: TrainId,
  position: Position,           // track-ID + offset, sub-meter resolution
  uncertainty_m: f32,            // 95% CI half-width
  speed_mps: f32,
  speed_uncertainty_mps: f32,
  heading: Heading,
  source_mask: u8,               // which sensors contributed (GNSS/IMU/odo/beacon)
  onboard_time_ns: u64,
}

SwitchCommand {
  switch_id: SwitchId,
  requested_position: SwitchPosition,
  requested_by: EntityId,        // dispatcher or automatic route setter
  lock_until_entry: Option<EntryId>,
}

SwitchObservation {
  switch_id: SwitchId,
  observed_position: SwitchPosition,
  confidence: Confidence,        // Locked | Transitioning | Unknown
  observed_at_ns: u64,
}

RouteRequest {
  route_id: RouteId,
  requested_by: EntityId,
  entry_point: TrackRef,
  exit_point: TrackRef,
  train_id: Option<TrainId>,     // bound when granted
}

RouteGrant {
  route_id: RouteId,
  train_id: TrainId,
  locked_switches: Vec<SwitchId>,
  locked_sections: Vec<SectionId>,
  expires_at_ns: u64,
}

SpeedRestriction {
  section: TrackRef,
  max_speed_mps: f32,
  reason: RestrictionReason,     // permanent | temporary | emergency
  effective_from_ns: u64,
  effective_until_ns: Option<u64>,
}

TrainRegistration {
  train_id: TrainId,
  consist: ConsistDescriptor,    // length, mass, braking curve, classification
  cert_chain: CertChain,
}

Heartbeat {
  from_entity: EntityId,
  health: HealthStatus,
}

MaintenanceOverride {
  section: TrackRef,
  granted_to: EntityId,
  granted_until_ns: u64,
  signed_by: DispatcherSignature,
}
```

All payload schemas live in `crates/osr-core/proto/track_state.proto`. Types are enums with explicit discriminants; forward-compat is handled by `reserved` fields and a strict versioning rule (see §12).

### 5.2 Derived state

From the log, any W-Node (or train agent) deterministically computes:

- **Section occupancy map**: for each section, which train (if any) currently occupies it, with confidence interval.
- **Switch state map**: for each switch, last observed position and lock status.
- **Active routes**: set of currently granted RouteGrants that have not expired or been released.
- **Speed restriction map**: keyed by section.
- **Known trains**: registered consists and last-known positions.

Derived state is a pure function of the committed prefix of the log. Two nodes with the same committed prefix **must** compute identical derived state (this is a verified property).

## 6. Consensus Protocol

### 6.1 Overview

We use **Static-Membership Raft with Fail-Restrictive Timeout** (SMRaft) — a narrow variant of Raft with three modifications tuned for safety-critical use:

1. **Static membership.** Membership changes require a maintenance window; there is no online reconfiguration. This eliminates the trickiest part of Raft (joint consensus) and the hardest part of its correctness proof.
2. **Fail-restrictive timeout.** When a node cannot confirm liveness of a quorum within `T_safe` (default 2 s), it stops emitting new RouteGrants and notifies trains via a "shrinking authority" signal. Existing MAs remain valid until their own expiry. This is the fail-safe direction.
3. **Bounded log growth.** The log is aggressively snapshotted (every `N_snap` entries, default 10k) and old entries are pruned after snapshot durability. Train agents subscribe to live tail only.

SMRaft is Raft with parts removed, not added. The underlying correctness argument rides on Raft's well-studied safety proof (Ongaro's TLA+ spec, verified refinements in Ironfleet).

### 6.2 Region sizing

- **5–20 nodes per region.** Below 5, fault tolerance is too thin (need to tolerate 2 simultaneous failures including scheduled maintenance). Above 20, Raft's serial leader becomes a latency bottleneck for commits.
- **Quorum:** `floor(N/2) + 1`. Standard Raft quorum.
- **Node placement:** one W-Node per station or major junction. Extra nodes collocated in depot and OCC to boost quorum size without adding track-side complexity.

### 6.3 Timing parameters

| Parameter | Default | Rationale |
|---|---|---|
| `heartbeat_interval` | 50 ms | Allows election timeout much shorter than rail dynamic timescales. |
| `election_timeout` | 300–600 ms (randomized) | Median failover ~400 ms. |
| `T_safe` (fail-restrictive) | 2 s | Trains can coast safely for 2 s; anything longer risks MA expiry stacking up. |
| `commit_latency_p99_target` | 50 ms | LAN RTT ×2 plus processing. Achievable on TSN backbone. |
| `MA_refresh_period` | 500 ms | How often a train reevaluates its MA against log tail. |
| `MA_validity_window` | 3 s | How long an MA is valid after issue. Short enough to be self-expiring, long enough to tolerate transient network hiccups. |

All timing parameters are deployment-configurable but ship with conservative defaults.

### 6.4 Leader responsibilities

- Serialize writes and replicate to followers.
- Detect stale followers and emit catch-up stream.
- On term change: followers invalidate any in-flight MA computations and recompute from newly committed prefix.
- The leader does **not** compute MAs. MA computation is decentralized (§7); the leader only maintains the log.

### 6.5 What the protocol guarantees

Given quorum liveness:

- **Agreement:** all nodes agree on the committed prefix.
- **Total order:** entries are totally ordered by `(term, entry_id)`.
- **Durability:** committed entries survive minority failures.
- **Monotonic progress:** committed prefix only grows.

Given loss of quorum:

- **No new commits.** The log stops growing.
- **Existing MAs remain valid until expiry.** Trains with valid MAs continue until the MA window elapses, then stop.
- **No silent split-brain.** A minority partition cannot produce new grants because it cannot reach quorum. This is Raft's defining safety property.

## 7. Train Agent and MA Computation

### 7.1 Train agent architecture

Each train runs a `TrainAgent` on its T-ECU. It has four coordinating tasks:

1. **Publisher**: builds `TrainPositionReport` every 200 ms from sensor fusion; submits to the local W-Node via a regional proxy.
2. **Subscriber**: streams the committed log tail from any two independent W-Nodes (`primary` and `witness`).
3. **MA Computer**: recomputes self-MA on every new committed entry in relevant sections (debounced to `MA_refresh_period`).
4. **ATP Enforcer**: supervises actual train motion against self-MA + wayside-MA; triggers emergency brake on violation.

These four tasks run in isolated Hubris tasks with hardware-enforced memory isolation. Only the ATP Enforcer can command the brake.

### 7.2 The MA computation algorithm

The self-MA is computed deterministically from the log. The algorithm is small enough to fit on a page:

```
fn compute_self_ma(
    train_id: TrainId,
    log_prefix: &[Entry],      // committed entries visible to this train
    now_ns: u64,
) -> MovementAuthority {
    let state = derive_state(log_prefix);

    // 1. Where am I?
    let my_pos = state.position_of(train_id)
        .unwrap_or_else(|| fail_safe_no_position());

    // 2. What sections does my consist currently occupy?
    let my_footprint = footprint_from(my_pos, state.consist(train_id));

    // 3. Which adjacent sections are free to me?
    let candidate_extension = state.forward_chain(my_pos.direction(), MAX_MA_DISTANCE);

    // 4. Clip at first blocker.
    let mut ma_end = my_pos.head();
    for section in candidate_extension {
        if !section_available_to(train_id, section, &state) {
            break;
        }
        ma_end = section.far_end(my_pos.direction());
    }

    // 5. Apply speed restrictions within the authority.
    let restrictions = state.speed_restrictions_between(my_pos.head(), ma_end);

    // 6. Apply time bound.
    let valid_until = now_ns + MA_VALIDITY_WINDOW_NS;

    MovementAuthority {
        train_id,
        end: ma_end,
        restrictions,
        valid_until,
        derived_from_entry_id: log_prefix.last().entry_id,
    }
}

fn section_available_to(train_id: TrainId, s: Section, state: &State) -> bool {
    // A section is available if and only if:
    //   (a) no other train occupies it (with uncertainty margin), AND
    //   (b) it is part of a RouteGrant currently assigned to this train,
    //       OR it is explicitly unreserved and free, AND
    //   (c) every switch in it is observed-locked to the correct position, AND
    //   (d) no MaintenanceOverride blocks it, AND
    //   (e) all adjacent opposing-direction routes are clear.
    // Any uncertainty (unknown switch, unobserved train, stale heartbeat) => NOT available.
    ...
}
```

Five properties must be proven about this function:

- **P1 (determinism):** same input → same output, across nodes and train agents.
- **P2 (non-overlap):** ∀ two trains A, B at the same instant: `ma_end(A)` and `ma_end(B)` do not share any section unless `A == B`.
- **P3 (consist-fit):** MA extension accounts for full consist length including safety margin.
- **P4 (conservatism under missing data):** any missing, stale, or uncertain input produces a more-restrictive MA, never less-restrictive.
- **P5 (time bounded):** `valid_until - now` is bounded above by `MA_VALIDITY_WINDOW_NS`; no path through the function produces an unbounded authority.

These are the core safety properties we formally verify (§11).

### 7.3 Cross-validation

The train agent subscribes to **two** independent W-Nodes. Each independently:

- Streams the log to the train.
- Runs the same MA computation.
- Emits a signed `MovementAuthorityWitness` to the train.

The train agent accepts the **intersection** of:
- Its own self-computed MA,
- Primary W-Node's witness,
- Secondary W-Node's witness.

"Intersection" means: end position = minimum of the three; speed restriction = maximum of the three; validity = minimum of the three. The fail-safe direction again.

Disagreement logs an incident and degrades to the most restrictive value. Persistent disagreement (>3 cycles) triggers a service brake and notifies dispatch — this indicates either a compromised node or a bug, both of which warrant intervention.

### 7.4 Region boundaries

A train traversing a region boundary runs two train agents in parallel for a transition window:

1. `T_in` (approaching boundary): subscribes to region A's log only.
2. `T_cross` (entering approach zone ~500 m before boundary): subscribes to both A and B. Both regions must see a consistent `TrainRegistration` for the train. Both regions compute MAs; train accepts the intersection.
3. `T_out` (fully in region B): unsubscribes from A after A has logged a `TrainDeparture` entry.

This handoff is *not* consensus across regions. It's coordinated publish/subscribe with cross-region authentication. The safety argument is local to each region plus the handoff protocol itself, which is much simpler to verify than global consensus would be.

## 8. Fault Model and Behavior

| Fault | Frequency | System response |
|---|---|---|
| Single W-Node crash | Occasional | Quorum holds; no operational impact. Failed node restarted, rejoins as follower. |
| Leader crash | Occasional | Election in ~300–600 ms; brief commit pause; no MA impact if pause < `MA_VALIDITY_WINDOW`. |
| Quorum loss (partition) | Rare | No new commits. Existing MAs expire over ~3 s; trains coast to stop. Service resumes when quorum reforms. |
| Radio link degradation | Common | Train may miss witness messages; falls back to self-MA with reduced confidence; MA recomputation continues. Persistent loss → brake. |
| Position sensor failure (one modality) | Uncommon | Sensor fusion degrades gracefully; position uncertainty grows; MA shrinks proportionally. |
| Position sensor failure (all modalities) | Rare | Train reports "position lost" to log; all other trains treat section containing unknown train as blocked; the train itself brakes to stop. |
| Byzantine W-Node | Out of scope for v1 | See §3. |
| Train agent crash | Rare | Watchdog brake. Train stops. Onboard spare can be hot-swapped in depot. |
| Rogue dispatcher command | Mitigated | Dispatcher commands go through `MaintenanceOverride` which requires a signed second authorization for safety-critical operations. |

**Invariant under all enumerated faults:** no train ever receives an MA that includes a section occupied by or reserved for another train. This is the central property the safety case argues.

## 9. Latency Budget

End-to-end MA update (position changes → train has updated MA):

| Stage | Budget (p99) | Implementation note |
|---|---|---|
| Onboard sensor fusion update | 20 ms | Runs at 200 ms cadence; jitter <20 ms |
| Position report → W-Node (5G uplink) | 40 ms | Commercial 5G SA; LoRa fallback is slower and not in this path |
| W-Node ingress → leader | 5 ms | TSN backbone |
| Leader commit (quorum replication) | 30 ms | LAN RTT ×2 + processing; budget includes worst-case node |
| Commit → train subscribers | 40 ms | 5G downlink to two witnesses in parallel |
| MA recomputation (onboard) | 5 ms | Deterministic fixed-cost algorithm |
| Witness cross-check | 10 ms | In-memory |
| **Total end-to-end** | **150 ms** | |
| **Target p99** | **200 ms** | 50 ms headroom |

If 5G uplink is unavailable, position reports fall back to LoRa (carrier-independent, but ~500 ms latency). In that mode, MA refresh rate drops and MAs shrink defensively — not a safety concern, but throughput drops until 5G restores.

## 10. Formal Verification Plan

Four layers of verification, each proving different properties:

### 10.1 Protocol layer (TLA+)

A TLA+ specification of SMRaft, refining Ongaro's Raft spec, proves:

- Election safety: at most one leader per term.
- Log matching: identical committed prefixes across nodes.
- Leader completeness: committed entries persist across terms.
- **Fail-restrictive liveness:** under quorum loss, no node emits new RouteGrants; existing MAs are allowed to expire.

### 10.2 State-machine layer (Kani)

Bounded model checking of `derive_state` and `compute_self_ma` with Kani:

- Determinism (P1): two invocations on the same prefix produce byte-identical outputs.
- Non-overlap (P2): for any pair of registered trains with committed positions, the computed MAs do not share sections.
- Conservatism (P4): mutating an input entry to be "more uncertain" produces an MA whose end is no further than the original.
- Time boundedness (P5): all MA outputs have `valid_until - now ≤ MA_VALIDITY_WINDOW_NS`.

Bounds: up to 8 trains, up to 50 log entries per harness — enough to exercise all code paths. Larger systems rely on the TLA+ protocol argument plus the property that state derivation composes over log suffixes.

### 10.3 Rust-code layer (Creusot where feasible, tests elsewhere)

- Creusot contracts on the pure functions (`section_available_to`, `forward_chain`, `footprint_from`) discharging obligations from the Kani layer.
- Property-based tests (`proptest`) for algebraic invariants (e.g., "MA end is always ≥ current head position").
- Differential testing against a reference interpreter written in a simpler style (likely Python) for the same log inputs.

### 10.4 System layer (simulator)

- `osr-sim` runs full regional simulations with injected faults (node crashes, partitions, sensor glitches, Byzantine-ish data corruption short of full Byzantine fault).
- Invariant monitors in the sim flag any state where two trains could collide within their MAs. Any run that flags an invariant is a test failure.
- Soak tests for 30-day simulated operation with realistic traffic patterns before any hardware pilot.

### 10.5 Evidence linkage

Each Kani harness, TLA+ module, Creusot proof, and sim run emits a structured evidence artifact consumed by the safety-case compiler. The safety case (GSN) claims "P2 holds" link to the specific evidence artifacts that discharge the claim. If a commit invalidates any artifact, CI breaks the build.

## 11. Schema Evolution

Log entries are protobuf. Evolution rules:

- **Never reuse field numbers.** Deprecated fields are `reserved` and held forever.
- **Never change a field's type.** Introduce a new field with a new number.
- **Log format version is part of the log.** The first entry of every region's log is a `FormatVersion`. Entries past a version bump are rejected by nodes running the older version — they must upgrade or be replaced. (Upgrade is a maintenance-window activity.)
- **Schema changes require an RFC.** No in-repo schema changes without review.

The strict discipline is worth the friction. A rail signaling log will be read by tools we haven't written yet, in decades.

## 12. Open Questions

1. **Raft vs. alternatives.** Is there a protocol that's even simpler to formally verify while meeting our needs? Candidates: single-decree Paxos per entry (more messages but simpler proofs), a static-primary protocol with only failover consensus. Needs a focused comparison RFC.
2. **How conservative is "conservative enough" for uncertainty handling?** The exact error model for sensor fusion inputs determines how much MA margin trains leave; this will be tuned empirically in simulation and pilot.
3. **Ed25519 vs. post-quantum signatures.** The log is append-only and will be read for decades. Should signatures be post-quantum from day one? Tentative yes — Dilithium2 costs us ~2 KB per entry, affordable.
4. **Dispatcher override safety.** Maintenance overrides require dispatcher signatures. What's the exact protocol for "I, a human dispatcher, authorize this train into a blocked section for rescue"? Needs its own RFC.
5. **Time source integrity.** PTP sync is assumed. What if the GPS clock source is spoofed or jammed? Trains use their own clocks for MA expiry; disagreements between train-local and log-local time produce restrictive behavior automatically, but this needs to be verified.
6. **Scale testing.** Largest region we've thought through is ~50 km / 20 nodes. What's the upper bound before we need regional subdivision for latency?

## 13. Prior Art

- **Raft** (Ongaro, 2014) — consensus protocol we specialize from.
- **Ironfleet** (Hawblitzel et al., 2015) — formally verified replicated state machines in Dafny; inspiration for our verification layering.
- **PALS / Hurdle** — formal work on distributed real-time control systems in avionics; informs timing argument.
- **Thales SelTrac, Siemens Trainguard, Alstom Urbalis** — the centralized ZC designs we replace.
- **Alstom Axonis, Siemens Trainguard MT with DCS-M** — recent vendor moves toward more decentralized architectures; validate that the industry is trending this way, but still not open.
- **Sun-Ways (track-PV)**, **Stadler FLIRT Akku (BEMU)**, **Hitachi Masaccio** — related innovations on the energy side (see ARCHITECTURE.md §4 D5, D7).

---

*This RFC is a draft. Substantive changes go through PR review with at least one reviewer from each of: distributed-systems, formal-methods, and rail-signaling background.*
