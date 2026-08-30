# Formal specs (TLA+)

This directory holds TLA+ specifications that anchor OpenSourceRail's formal
safety argument.

## Files

| File | Purpose |
|---|---|
| `SMRaft.tla` | Core protocol spec: Static-Membership Raft + Fail-Restrictive Timeout. Referenced by [RFC 0001 §11.1](../../../../docs/rfcs/0001-track-state-consensus.md). |
| `MCSmall.tla` | Minimum-viable TLC harness (3 nodes, 2 values). |
| `MCSmall.cfg` | TLC config for the small harness. |

## Running TLC

Install the TLA+ toolbox (or `tla2tools.jar` from https://github.com/tlaplus/tlaplus).

```
# from this directory
java -jar tla2tools.jar -config MCSmall.cfg MCSmall.tla -workers auto -deadlock
```

Expected outcome on the small harness: all invariants hold, state-space
exploration completes in minutes on a developer workstation.

## What this spec does and does not prove

**Proves** (via TLC on small bounded models + TLAPS on the general spec, once
we write the TLAPS proofs):
- `ElectionSafety`, `LogMatching`, `LeaderCompleteness`, `StateMachineSafety`
  — the classical Raft safety properties, inherited from Ongaro's proof and
  re-checked under our specialization.
- `FailRestrictive` — the novel property introduced by this variant: no
  Safety-category entry is committed under a leader whose quorum confirmation
  is stale.

**Does not prove** (out of scope here; covered elsewhere):
- Refinement from the Rust implementation to this spec (future `SMRaftImpl`
  module once `crates/osr-consensus` exists).
- The rail-domain state machine (non-overlap of MAs, etc.) — that is Kani
  territory, see RFC 0001 §11.2.
- Byzantine behaviour — explicitly out of scope for v1 (RFC 0001 §3).
- Log compaction / snapshotting — orthogonal to safety; separate module.

## Known limitations of the current spec

1. `QuorumConfirmationExpires` is modeled as an explicit action; in the real
   system it is a wall-clock timeout. A timed refinement would sharpen the
   liveness argument but is not needed for the safety properties above.
2. The message bag is unbounded in principle; TLC terminates only because of
   the `MaxTerm` / `MaxLogLen` bounds. Production verification should use
   TLAPS for the unbounded spec.
3. No explicit modeling of crash + restart persistence. Standard Raft arguments
   apply; add a `Restart` action when we want to cover this explicitly.
