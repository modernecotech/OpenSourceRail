# Safety-case artifacts

This directory collects the machine-checkable evidence that supports
OpenSourceRail's safety claims. Per
[ARCHITECTURE.md §7](../ARCHITECTURE.md#7-safety--certification-strategy)
the safety case is structured in GSN (Goal Structuring Notation),
serialised as TOML, and regenerated on every commit.

The TOML lives under [`gsn/`](gsn/) and is compiled by the
[`osr-safety-case`](../../crates/osr-safety-case/) crate (RFC 0005 §4.9).
CI gate: [`tests/starter_case_closes.rs`](../../crates/osr-safety-case/tests/starter_case_closes.rs)
fails the build if any goal no longer traces to evidence — that is,
adding a safety-relevant claim or deleting an evidence file breaks CI
until the gap is closed.

Compile the rendered case locally with:

```bash
cargo run -q --bin osr-safety-case -- docs/safety-case/gsn
```

## What's verified today

[RFC 0004 §4](../rfcs/0004-osr-interlocking-plan.md) names five
safety properties of the Movement Authority computer:

| Property | Harness in [`crates/osr-interlocking/src/kani_proofs.rs`](../../crates/osr-interlocking/src/kani_proofs.rs) | Status |
|---|---|---|
| **P1** — determinism | `kani_p1_determinism` | written |
| **P2** — non-overlap | `kani_p2_non_overlap_two_trains` | written (tiny-network bound) |
| **P3** — consist-fit | `kani_p3_consist_fit_single_train` | written |
| **P4** — conservatism | `kani_p4_fail_restrictive_is_not_less_restrictive_than_known` | written (fail-restrictive path only) |
| **P5** — time-bounded | `kani_p5_time_bounded`, `kani_p5_time_bounded_with_known_position` | written |

Also proptest-checked (covering larger inputs unbounded) in
[`tests/proptest_ma.rs`](../../crates/osr-interlocking/tests/proptest_ma.rs)
and [`tests/proptest_determinism.rs`](../../crates/osr-interlocking/tests/proptest_determinism.rs).

Continuously exercised in [`osr-sim`](../../crates/osr-sim/) on every
scenario run: per RFC 0004 M5 the simulator emits `Entry` objects as
trains move, and every section entry is gated by
`osr_interlocking::section_available_to`. The generated Samawah
reference run produces 2400 MAs / 2 h with zero invariant violations
under both the in-memory backend and a 3-node Raft cluster.

Cross-checked against an independent Python reference interpreter
([`tools/reference-ma/`](../../tools/reference-ma/)) per RFC 0004 M4:
[`crates/osr-interlocking/tests/differential.rs`](../../crates/osr-interlocking/tests/differential.rs)
serialises random log prefixes, shells out to
`python3 -m reference_ma`, and asserts byte-identical
`MovementAuthority` JSON. Any divergence between the two twins is a
bug in at least one of them.

**Honest status:** the harnesses compile under `#[cfg(kani)]` and
encode each property formally in Rust, but running them requires a
Kani installation (see below). The P2 and P4 harnesses use
deliberately small bounds — a 2-section network and 1–2 trains — so
Kani can discharge them in a reasonable time. Scaling the bounds to
RFC 0004's targets (8 trains, 50 entries, 100 sections) is left to
contributors with compute budget; the same harness structure extends
directly.

## What the other SIL-4 crates check today

| Crate | Properties | Verification |
|---|---|---|
| [osr-atp](../../crates/osr-atp/) | A1–A7 (determinism, expired MA trips, unknown position trips, train mismatch trips, head past MA end trips, overspeed trips, conservatism) | proptest for A1–A7; Kani harnesses for A1–A7 in [`src/kani_proofs.rs`](../../crates/osr-atp/src/kani_proofs.rs) |
| [osr-brake](../../crates/osr-brake/) | B1–B5 (determinism, emergency union, emergency completeness, WSP conservative, park safe) | proptest + Kani for B1–B5 in [`src/kani_proofs.rs`](../../crates/osr-brake/src/kani_proofs.rs) |
| [osr-odometry](../../crates/osr-odometry/) | O1–O5 (determinism, forward non-regression, uncertainty monotone, balise reset, GNSS conservative) | proptest + Kani for O1–O5 in [`src/kani_proofs.rs`](../../crates/osr-odometry/src/kani_proofs.rs) |
| [osr-wayside-points](../../crates/osr-wayside-points/) | W1–W6 | proptest + Kani for W1–W6 in [`src/kani_proofs.rs`](../../crates/osr-wayside-points/src/kani_proofs.rs) |
| [osr-consensus](../../crates/osr-consensus/) | TLA+ invariants (ElectionSafety, LogMatching, LeaderCompleteness, StateMachineSafety, FailRestrictive) | proptest over cluster harness; TLA+ TLC on the spec, not yet a refinement proof |

## Running Kani

### Install

```bash
cargo install --locked kani-verifier
cargo kani setup
```

`cargo kani setup` downloads ~200 MB of CBMC tooling on first run.

### Run a single harness

```bash
cargo kani -p osr-interlocking --harness kani_p5_time_bounded
```

### Run all harnesses in a crate

```bash
cargo kani -p osr-interlocking
```

### Run all harnesses across the workspace

```bash
cargo kani --workspace
```

Kani runs are expected to take seconds for P1, P3, P5 and minutes for
P2, P4. If P2 or P4 time out (default limit 30 min), narrow the
bounds further inside the harness — Kani's `kani::assume` clauses at
the top of each proof are the knobs to turn.

## CI

The [Kani workflow](../../.github/workflows/kani.yml) runs all
harnesses on every push. It uses GitHub Actions' cache for the Kani
toolchain install so the first minute of each run is just cache
restore. Full verification takes ~10 minutes on the default
`ubuntu-latest` runner.

## What's planned

From RFC 0004 §M3 and the cross-crate safety plan:

1. **Scale the P2 / P4 bounds** toward the RFC's 8 trains × 50
   entries × 100 sections target. Requires either smarter
   abstractions (reducing state-space explosion) or a fleet of
   dedicated CI workers.
2. **Kani harnesses for the other SIL-4 crates** — **done.**
   The four onboard/actuator evaluators (ATP, brake, odometry,
   wayside-points) now ship Kani harnesses alongside their proptest
   suites. The remaining work here is verification throughput —
   scaling bounds toward larger state spaces on dedicated CI.
3. **A refinement proof** from the TLA+ `SMRaft` spec to the Rust
   `osr-consensus` implementation. TLC already checks the spec's
   safety properties; refinement would formally connect the spec to
   the code. TLAPS or a separate tool is a candidate.
4. **GSN safety case compiler** — **done.** The
   [`osr-safety-case`](../../crates/osr-safety-case/) crate compiles
   the TOML claim files in [`gsn/`](gsn/) and the
   [`starter_case_closes`](../../crates/osr-safety-case/tests/starter_case_closes.rs)
   test gates CI on every commit. Current case: 11 goals, 3
   strategies, 14 solutions, all linked to real evidence in-tree.

## Directory contents

- [`gsn/`](gsn/) — GSN TOML claim files. Each file is a coherent
  slice of the case (top-level goals, non-overlap decomposition,
  fail-safety decomposition, consistency decomposition). Compiled by
  `osr-safety-case`.
- `evidence/` — machine-readable Kani and proptest results
  (planned; currently stdout only).
- `hazard-log/` — identified hazards and mitigations (planned).
