# Safety-case artifacts

This directory collects the machine-checkable evidence that supports
OpenSourceRail's safety claims. Per
[ARCHITECTURE.md §7](../ARCHITECTURE.md#7-safety--certification-strategy)
the safety case is structured in GSN (Goal Structuring Notation),
serialised as TOML, and regenerated on every commit. Today's contents
are the starting point — one verifier (Kani) wired into the SIL-4
interlocking crate.

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
| [osr-atp](../../crates/osr-atp/) | A1–A7 (determinism, expired MA trips, unknown position trips, train mismatch trips, head past MA end trips, overspeed trips, conservatism) | proptest, not yet Kani |
| [osr-brake](../../crates/osr-brake/) | B1–B5 (determinism, emergency union, emergency completeness, WSP conservative, park safe) | proptest, not yet Kani |
| [osr-odometry](../../crates/osr-odometry/) | O1–O5 (determinism, forward non-regression, uncertainty monotone, balise reset, GNSS conservative) | proptest, not yet Kani |
| [osr-vigilance](../../crates/osr-vigilance/) | V1–V6 (determinism, suppression, warning precedes trip, tripped iff emergency, in-window ack clears, trip latches) | proptest, not yet Kani |
| [osr-wayside-points](../../crates/osr-wayside-points/) | W1–W6 | proptest, not yet Kani |
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
2. **Kani harnesses for the other SIL-4 crates** — each has its own
   proptest suite that enumerates the properties; porting them to
   Kani is mechanical.
3. **A refinement proof** from the TLA+ `SMRaft` spec to the Rust
   `osr-consensus` implementation. TLC already checks the spec's
   safety properties; refinement would formally connect the spec to
   the code. TLAPS or a separate tool is a candidate.
4. **GSN safety case compiler** (`osr-safety-case` in RFC 0005
   §4.9) — turns TOML-serialised claims + evidence pointers into a
   rendered safety case. Blocks on tool choice.

## Directory contents

Currently empty apart from this README. As each artifact lands it
will be added:

- `gsn/` — GSN TOML claim files (planned).
- `evidence/` — machine-readable Kani and proptest results
  (planned; currently stdout only).
- `hazard-log/` — identified hazards and mitigations (planned).
