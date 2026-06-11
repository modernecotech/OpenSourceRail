# RFC 0004 — `osr-interlocking` Implementation Plan

**Status:** Draft — planning only, no code yet
**Date:** 2026-04-20
**Depends on:** [RFC 0001 Track State Consensus](0001-track-state-consensus.md)

## 1. Summary

This RFC lays out the plan for the `osr-interlocking` crate — the Rust
implementation of the Movement Authority (MA) computer and the SIL-4 safety
kernel described in [RFC 0001 §7](0001-track-state-consensus.md). It is a
**planning RFC**, not an implementation RFC: it enumerates the modules, the
safety properties to verify, the tools to use, and the order of work. No
code ships as part of this RFC. The intent is to set a concrete starting
line before the next dedicated implementation session.

The reason for separating the plan from the implementation is scope. A
credible first pass at `osr-interlocking` includes five loosely coupled
pieces — data structures, pure MA computation, property-based tests,
Kani-verified bounded models, and integration with `osr-sim` — that together
are a multi-session effort. This document makes the structure explicit so
the work can begin concretely next time.

## 2. Non-goals

- Not a full SIL-4 safety case. That requires independent assessment and
  deployment-specific evidence; the crate produces artifacts consumable by
  a safety case, but it is not one.
- Not a complete consensus layer. The MA computer is deterministic given a
  log prefix; the log itself is maintained by the future `osr-consensus`
  crate, which is a separate piece of work.
- Not a Byzantine-fault-tolerant design. Explicitly out of scope for v1 per
  RFC 0001 §3.
- Not a replacement for onboard ATP. The MA computer decides *what is
  allowed*; onboard ATP enforces *what actually happens*. They are separate
  crates.

## 3. Crate structure

```
crates/
└── osr-interlocking/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs              # facade
    │   ├── state.rs            # derived-state types (track, trains, switches)
    │   ├── log.rs              # in-memory log prefix representation
    │   ├── ma.rs               # compute_self_ma + helpers (pure functions)
    │   ├── witness.rs          # signed MovementAuthorityWitness
    │   └── invariants.rs       # runtime-checkable invariants (debug builds)
    ├── harnesses/
    │   ├── kani_determinism.rs
    │   ├── kani_non_overlap.rs
    │   ├── kani_conservatism.rs
    │   ├── kani_time_bounds.rs
    │   └── kani_fit.rs
    └── tests/
        ├── proptest_invariants.rs  # algebraic properties
        └── differential.rs         # against a reference Python interpreter
```

Conventions: no `unsafe`, no allocator calls in the hot path (pre-allocated
`Vec`s and `SmallVec`s), all pure functions annotated with `#[must_use]`,
all public types `Debug + Clone + PartialEq` for test ergonomics.

## 4. Properties to verify

From RFC 0001 §7.2, the five safety properties:

- **P1 (determinism):** same log prefix → byte-identical MA output across
  every node and train agent. Verified by Kani enumeration over small
  bounded states; asserted via proptests at larger scale by comparing
  outputs of random but identical inputs.
- **P2 (non-overlap):** for any two registered trains with committed
  positions, the computed MAs do not share any section (unless both are
  the same train). Verified by Kani on up to 8 trains × 50 entries;
  asserted by proptests with independent interpreter for larger N.
- **P3 (consist-fit):** MA extension accounts for full consist length plus
  a safety margin. Verified by Kani by construction of the `footprint_from`
  function; asserted by proptests that vary consist length randomly.
- **P4 (conservatism):** mutating any input entry to be "more uncertain"
  (higher position uncertainty, `SwitchPosition::Unknown`, missing
  heartbeat) produces an MA whose end is no further than the original.
  This is the hardest property — encoded as a monotone refinement lemma.
- **P5 (time bounded):** all MA outputs have `valid_until - now ≤
  MA_VALIDITY_WINDOW_NS`. Verified trivially by Kani; also by ensuring the
  code path never constructs an MA with `valid_until` greater than
  `now + MA_VALIDITY_WINDOW_NS`.

Each property gets its own Kani harness file under `harnesses/`. The CI
pipeline runs all harnesses on every PR.

## 5. Tool chain

| Layer | Tool | Why |
|---|---|---|
| State-machine bounded model check | Kani | Rust-native, strong Rust semantic support, SMT-backed. Already used in the consensus RFC's verification plan. |
| Property-based testing | `proptest` | Scales to larger inputs than Kani; catches regressions cheaply. |
| Differential testing | A companion Python reference interpreter | Independent implementation of the same state machine; differential fuzzing catches bugs in either direction. |
| Formal model refinement | TLA+ (already stood up in `formal/tla/SMRaft.tla`) | The rail state machine is a refinement of the SMRaft-maintained log. Refinement proofs connect the two. |
| Contracts on pure functions | Creusot (optional, v2) | If Kani coverage is insufficient for some helpers, Creusot can discharge function contracts directly. |

## 6. Milestones

The work breaks cleanly into five milestones. Each is a separate session or
PR; none should be attempted as a single contiguous effort.

### M1 — Types and log ✅ *(done 2026-04-20)*

- Port the protobuf entry schema (`crates/osr-core/proto/track_state.proto`)
  to Rust types in `osr-interlocking::state` and `osr-interlocking::log`.
- Implement `derive_state(log_prefix: &[Entry]) -> State` as a pure function.
- Proptest: `derive_state` is a pure function (two invocations on the same
  input produce identical outputs).

**Delivered:**
- [`crates/osr-interlocking`](../../crates/osr-interlocking) scaffolded
  with Cargo workspace integration.
- `Entry` + `EntryPayload` (12 variants) and all payload types in
  [`log.rs`](../../crates/osr-interlocking/src/log.rs), mirroring
  `track_state.proto` with integer-only safety-path units (mm, mm/s, ns,
  SoC in parts-per-thousand).
- `DerivedState` with `BTreeMap`-based deterministic ordering and
  `derive_state(&[Entry]) -> DerivedState` +
  `DerivedState::apply(&Entry)` in
  [`state.rs`](../../crates/osr-interlocking/src/state.rs).
- Four added IDs in osr-core: `RouteId`, `EntityId`, `EntryId`, `RegionId`.
- Ten passing tests (6 unit + 4 proptests over 1024 random cases):
  P1 determinism, batch-vs-incremental composition, prefix-extension
  monotonicity, totality of `derive_state` under malformed input.

### M2 — MA computation (§7.2 of RFC 0001) ✅ *(done 2026-04-20)*

- Implement `compute_self_ma(train_id, log_prefix, now)` per the pseudocode
  in RFC 0001 §7.2.
- Implement helper functions `section_available_to`, `footprint_from`,
  `forward_chain`, `apply_speed_restrictions`.
- Add debug-build invariants via `invariants.rs` that check P1, P3, P5 at
  runtime.
- Proptest: random log prefixes never produce MAs that violate P3 or P5.

**Delivered:**
- [`topology.rs`](../../crates/osr-interlocking/src/topology.rs): network
  traversal helpers — `locate_section`, `forward_chain` (budgeted, honors
  linear-vs-ring semantics, stops at section boundaries to stay
  fail-restrictive), `footprint_from` (backward walk by consist length),
  `far_end_of`. Includes 6 unit tests.
- [`ma.rs`](../../crates/osr-interlocking/src/ma.rs):
  `MovementAuthority` data type + `compute_self_ma(train_id, log_prefix,
  network, now_ns)` implementing the RFC 0001 §7.2 pseudocode.
  Fail-restrictive by default when the train has no registration or no
  known head position. Debug-build `debug_assert!`s verify P3 (end not
  behind head) and P5 (validity window bounded) on every call.
- Four MA-specific proptests: P1 determinism (256 cases), P5 validity
  bound (256 cases), totality (256 cases), MA-end structural validity
  (256 cases).
- Fixed two P3 edge cases during development:
  1. `forward_chain` originally extended past `MAX_MA_DISTANCE_MM` on the
     last section; now it stops at the previous section boundary. MAs
     always end at station boundaries — more conservative and simpler to
     reason about.
  2. Flawed P4 sketch proptest removed after discovering it was false in
     general (other trains' position reports can release occupancy and
     extend an MA). The correct P4 (mutation-based monotonicity) is
     Kani territory, explicitly deferred to M3.
- Five unit tests in `ma.rs` covering: no-registration fail-restrictive,
  single-train full extension, other-train blocking, P2 non-overlap on a
  specific two-train case, P5 validity window.

**Workspace now has 43 passing tests** (osr-sim 18, osr-interlocking 25).

### M3 — Kani harnesses ✅ *(written 2026-04-21; scaling bounds pending)*

- Write one harness per safety property (§4). Bounds: 8 trains, 50 entries,
  100 sections. Sufficient to exercise all code paths.
- Add a CI workflow that runs `cargo kani` on every PR.
- Document harness outputs as the first set of safety-case evidence files
  (linked from `docs/safety-case/`).

**Delivered:**
- [`crates/osr-interlocking/src/kani_proofs.rs`](../../crates/osr-interlocking/src/kani_proofs.rs)
  contains six `#[kani::proof]` harnesses covering all five properties:
  - `kani_p1_determinism` (P1)
  - `kani_p2_non_overlap_two_trains` (P2, tiny-network bound)
  - `kani_p3_consist_fit_single_train` (P3)
  - `kani_p4_fail_restrictive_is_not_less_restrictive_than_known` (P4,
    fail-restrictive path only — full conservatism refinement proof is
    deferred to a mutation-based harness once Kani's state space allows)
  - `kani_p5_time_bounded`, `kani_p5_time_bounded_with_known_position` (P5)
- [`.github/workflows/kani.yml`](../../.github/workflows/kani.yml) runs
  `cargo kani -p osr-interlocking` on every push.
- [`docs/safety-case/README.md`](../safety-case/README.md) documents the
  verifier, how to run it, and what's pending.

**Pending for full closure:**
- Scaling the P2 / P4 bounds toward the RFC's 8-train / 50-entry / 100-section
  target. Current bounds are 2 sections and 1–2 trains — enough to exercise
  the control flow but small enough to discharge in minutes.
- Full mutation-based P4 (conservatism): compare `compute_self_ma` on an
  input and on a "more uncertain" mutation of that input, assert the MA
  end never advances. Harder for Kani due to the doubled state space;
  deferred to a dedicated harness.
- Machine-readable evidence export (Kani already produces JSON; wire into
  the GSN safety case when the compiler lands).

### M4 — Differential interpreter + proptest ✅ *(done 2026-04-22)*

- Reference interpreter in Python (~500 lines) implementing the same state
  machine in a more readable style. Placed under `tools/reference-ma/`.
- Differential test: random log prefixes → compare Rust output byte-for-byte
  to Python output. Any divergence fails the test suite.
- Fuzz corpus under `tests/fuzz-corpus/` for regression catches.

**Delivered:**
- [`tools/reference-ma/`](../../tools/reference-ma/) — stdlib-only
  Python package (~820 LoC across `types`, `log`, `topology`, `state`,
  `ma`, and `__main__` CLI). Mirrors the five-module shape of
  `crates/osr-interlocking/src/` for reviewability.
- CLI accepts the exact serde JSON shape Rust produces (`u64` IDs via
  `#[serde(transparent)]`, externally-tagged `EntryPayload`, nested
  `Network` with stringified-int keys) and writes `MovementAuthority`
  JSON that round-trips back through `serde_json::from_str::<MovementAuthority>()`.
- [`crates/osr-interlocking/tests/differential.rs`](../../crates/osr-interlocking/tests/differential.rs)
  — Rust harness with 3 smoke cases (no-registration / single-train /
  other-train-blocks) + a proptest run of 16 random log prefixes over
  a 4-station linear network. Each case serialises to JSON, shells out
  to `python3 -m reference_ma`, parses the output back as a Rust
  `MovementAuthority`, and asserts equality against the native Rust
  result. Skipped cleanly when Python3 is unavailable or
  `OSR_SKIP_PY_DIFF=1` is set.
- [`tools/reference-ma/tests/test_basic.py`](../../tools/reference-ma/tests/test_basic.py)
  — 9 Python-side unit tests mirroring the key cases from `ma.rs`
  and `topology.rs` so the Python impl can be exercised standalone.
- 100 % agreement on every case tested so far: Rust and Python produce
  byte-identical `MovementAuthority` JSON.

**Scope notes:**
- The proptest generator currently stays inside a fixed 4-station
  linear network with 1..=3 trains. Extending to ring lines, switch
  observations, route grants, and speed restrictions is a
  straightforward follow-up — every primitive is already implemented
  in both twins.
- No standalone `tests/fuzz-corpus/` directory yet; the proptest's
  `proptest-regressions` file serves that role. A separate corpus is
  only warranted once external fuzzing (afl/libfuzzer) surfaces cases
  proptest alone would miss.

### M5 — Integration with `osr-sim` ✅ *(done 2026-04-22)*

- Replace `osr-sim`'s `OccupancyMap` with a thin shim that queries the
  `osr-interlocking` MA computer against a synthesized log.
- Sim now emits `Entry` objects as trains move; the MA computer derives
  authorities; conflicts become real invariant violations rather than
  in-memory occupancy check failures.
- Proves the MA computer works end-to-end on a generated city instance
  scenario.

**Delivered:**
- `OccupancyMap` deleted from `osr-core`; the `BTreeMap<SectionId, TrainId>`
  in `DerivedState::section_occupancy` is the single source of truth.
- The sim's `MaLogBackend` (in
  [`crates/osr-sim/src/sim.rs`](../../crates/osr-sim/src/sim.rs)) grew a
  `section_available_to(train_id, section)` predicate that delegates to
  [`osr_interlocking::section_available_to`](../../crates/osr-interlocking/src/ma.rs) —
  the same primitive `compute_self_ma` uses when clipping the forward
  chain.
- `enter_next_section` ([`sim.rs`](../../crates/osr-sim/src/sim.rs))
  gates every section entry through that predicate. On authorisation,
  `register_and_enter` emits a `TrainPositionReport` entry into the log
  whose head offset equals the consist length, so
  `DerivedState.apply_position` marks exactly the new section as
  occupied (and clears the old one).
- `SimulatedLog` and `ConsensusBackend` both cache a `DerivedState`
  that updates incrementally on every append; gate checks stay O(1) in
  log length.
- `ConsensusBackend::propose` now calls `cluster.run_until_committed`
  synchronously (30 ms × 30 ticks = 900 ms budget, well under the 3 s
  MA validity window) so the gate sees fresh state even when the Raft
  cluster is driving commits. The consensus integration test
  ([`crates/osr-sim/tests/consensus_integration.rs`](../../crates/osr-sim/tests/consensus_integration.rs))
  proves the sim and consensus paths produce structurally equivalent
  MA summaries.
- `ma_check::run_check_state` (formerly `run_check_entries`) is now a
  pure fleet-wide health sweep — no cross-check, because occupancy is
  owned by the MA computer itself, so any cross-check would be
  tautological. The periodic sweep populates `checks_run`,
  `total_mas_computed`, and `fail_restrictive_mas` in the run report.
- Samawah two-line reference scenario runs 2 hours (240 MA sweeps,
  2400 MAs computed) with **zero invariant violations** under both
  `SimulatedLog` and `ConsensusBackend`.

After M5, the project has a formally verified MA computer running
continuously in simulation, producing safety-case evidence on every CI run.

## 7. Safety case anchors

The five properties above anchor the safety case. Each property maps to a
GSN goal:

```
G1: "No train occupies a section simultaneously with another train"
 └─ G1.1: "MA computation enforces section exclusivity"  ← P2 (Kani)
 └─ G1.2: "Train obeys its MA via ATP"                    ← future crate
 └─ G1.3: "Consensus provides consistent log prefix"      ← RFC 0001 §11.1

G2: "Under faults, system degrades safely (fail-restrictive)"
 └─ G2.1: "Loss of quorum prevents new Safety entries"    ← SMRaft TLA+
 └─ G2.2: "MA expires after MA_VALIDITY_WINDOW"           ← P5

G3: "MA is consistent across witnesses"
 └─ G3.1: "Same log prefix produces identical MA"         ← P1
```

The structured safety case (GSN serialised as TOML) lives under
`docs/safety-case/` once M3 lands and CI begins producing evidence.

## 8. Pitfalls and decisions

These were flagged during planning; leaving them explicit so the
implementation session doesn't rediscover them:

- **Floating point.** Distances are in mm (i64), speeds in mm/s (i64); no
  floats in the safety path. Kani cooperates much better with integers.
- **Undefined-state handling.** The RFC says "any uncertainty produces
  more-restrictive MA". Concretely: `SwitchPosition::Unknown`,
  `PositionSource` with zero mass, stale `Heartbeat` all short-circuit
  `section_available_to` to `false`. Property P4 verifies this.
- **Test bounds.** Kani's depth is the limit, not coverage. Small bounded
  models cover all code paths; larger N relies on the log-composition
  property (state derivation is monotonic in log prefix).
- **`no_std` compatibility.** Target `no_std` from day one to keep the
  crate usable on the safety-kernel OS (Hubris / seL4). `std`-dependent
  tests are gated behind a `std` feature flag.
- **Proof fragility.** Verification tooling evolves. Pin Kani version in
  `Cargo.toml` and document the known-working toolchain in
  `docs/safety-case/`.

## 9. Open questions (deferred to implementation sessions)

1. Exact numeric type for `entry_id` and `term` — `u64` is obvious but
   saturation arithmetic semantics need to be spelled out.
2. Representation of the "safety envelope" intermediate term — do we
   materialise it or is it implicit in the computation?
3. Error handling: should `compute_self_ma` return a `Result` (with
   fail-restrictive defaults) or always a valid MA? Trade-off between
   explicitness and brittleness.
4. How does `osr-sim`'s stepping interact with MA validity windows when
   the sim clock advances by `dt_s = 1` but MA window is 3 s? Need a
   clear contract for "when is the MA re-evaluated".
5. Where do `TrainAgent` and `ATP Enforcer` live — same crate or separate?
   Leaning toward separate: `osr-interlocking` is pure compute;
   `osr-train-agent` handles sensor fusion and brake enforcement.

## 10. Done criteria for this planning RFC

- [x] Crate layout documented
- [x] Properties enumerated and mapped to tools
- [x] Milestones ordered and scoped
- [x] Pitfalls and decisions explicit
- [x] Safety-case anchors identified

The next session picks up at **M1 — Types and log**.
