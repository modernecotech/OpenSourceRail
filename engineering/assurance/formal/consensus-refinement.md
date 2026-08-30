# SMRaft-to-Rust refinement argument

This document records the v0.3 abstraction map between
[`SMRaft.tla`](tla/SMRaft.tla) and `osr-consensus`. It is a reviewable
refinement argument and test plan, **not a machine-checked refinement proof**.
That distinction remains a release gate for any stronger safety claim.

## Abstraction relation

One TLA server is one Rust `RaftNode`. `Server` is `Config.peers`; TLA sequences
are Rust `Vec<Entry>` with `LogIndex` preserving the model's one-based index;
`messages` are the network's queued `Action::Send` values; and `allCommitted`
is observed through committed actions/prefixes in a simulated cluster.

| TLA+ state/action | Rust representation or handler | Current evidence |
|---|---|---|
| `currentTerm`, `votedFor`, `state` | `RaftNode.current_term`, `voted_for`, `role` | Unit and cluster property tests |
| `log`, `commitIndex` | `log`, `commit_index` | Invariant and randomized cluster tests |
| `nextIndex`, `matchIndex` | `next_index`, `match_index` | Replication tests |
| `votesGranted` | `votes_granted` | Election tests |
| `lastQuorumConfirmedTerm` | `last_quorum_confirmed_term`; Rust also has bounded wall-clock freshness | Fail-restrictive tests |
| `Timeout`, `RequestVote`, `BecomeLeader` | `on_tick`, `start_election`, `emit_request_votes`, `become_leader` | Rust tests plus TLC model exploration |
| `HandleRequestVote*` | `handle_request_vote*` | Rust tests plus TLC model exploration |
| `AppendEntries`, `HandleAppendEntries*` | `emit_append_entries*`, `handle_append_entries*` | Rust tests plus TLC model exploration |
| `AdvanceCommitIndex` | `advance_commit_index` | Safety-invariant tests |
| `ClientRequest` | `propose` | Category and quorum-freshness tests |

## Assumptions that must remain explicit

- static membership; no joint consensus or online reconfiguration;
- no log compaction in this module;
- persistent term, vote and log writes complete atomically before dependent
  network output in the integrating host;
- authenticated transport and issuer policy are outside the abstract TLA model;
- Rust time is monotonic and the deployment validates timer bounds;
- finite TLC bounds establish bounded model results, not an unbounded theorem.

## v0.3 closure work

1. Run TLC for the checked configuration and archive its result.
2. Run the interlocking suite and a fast fail-restrictive ATP release property
   in CI; archive full bounded ATP runs separately once topology unwind limits
   and tool versions have been frozen and reviewed.
3. Maintain this action/state map under code review.
4. Add a tool-backed trace/refinement proof or an assessor-accepted refinement
   argument covering initialization, every step action and stuttering.

Items 1–3 are repository evidence. Full ATP bounded-proof completion and item
4 remain open in the certification gap register. They prevent the project from
describing ATP coverage as exhaustive or consensus refinement as formally
proved.
