//! OpenSourceRail Static-Membership Raft (SMRaft).
//!
//! This crate implements a Rust refinement of the TLA+ specification
//! at [`formal/tla/SMRaft.tla`](../../../formal/tla/SMRaft.tla), per
//! [RFC 0001 §8](../../../docs/rfcs/0001-track-state-consensus.md)
//! and RFC 0005 §4.6. It is **Phase 2d, crate 1** — the wayside-side
//! replication engine that maintains the authoritative track-state
//! log consumed by [`osr_interlocking`].
//!
//! # Differences from stock Raft
//!
//! These match the TLA+ spec:
//!
//! 1. **Static membership.** The set of nodes is fixed at construction
//!    time. No joint consensus, no online reconfiguration. Simplifies
//!    both the implementation and the safety argument.
//! 2. **No snapshotting in this module.** Log compaction is a
//!    separate concern (handled by a future `osr-consensus-snapshot`
//!    crate).
//! 3. **Entries are classified as `Safety` or `Advisory`.**
//!    Fail-restrictive timeout forbids leaders from committing new
//!    `Safety` entries without a recent quorum confirmation of the
//!    current term. Advisory entries (position reports,
//!    heartbeats) are unrestricted.
//!
//! # API shape
//!
//! The core is a pure state-machine [`step`] function:
//!
//! ```text
//! step(node: &mut RaftNode, event: Event, now_ns: u64) -> Vec<Action>
//! ```
//!
//! All I/O (network, disk, clock) is delegated to the caller.
//! The caller pushes [`Event`]s in (ticks, received messages, client
//! proposes) and drains [`Action`]s out (messages to send, entries
//! to commit). This mirrors the TLA+ action structure: each atomic
//! TLA+ action maps to one or more `Action`s produced by `step`.
//!
//! # Safety properties (targeted)
//!
//! These mirror the TLA+ invariants:
//!
//! - **ElectionSafety** — at most one leader per term.
//! - **LogMatching** — if two logs contain an entry at the same
//!   index with the same term, the logs agree up to that index.
//! - **LeaderCompleteness** — a committed entry appears in every
//!   future leader's log.
//! - **StateMachineSafety** — no two nodes ever apply different
//!   entries at the same committed index.
//! - **FailRestrictive** — under quorum loss, no new `Safety`
//!   entries commit; Advisory entries may still flow.
//!
//! All five are asserted by proptests over randomised multi-node
//! cluster runs (`tests/proptest_safety.rs`). Formal refinement to
//! the TLA+ model via Kani or Creusot is future work (tracked as an
//! open question in RFC 0005 §14).
//!
//! # Coding standard compliance
//!
//! Per RFC 0005 §7 (SIL-4):
//!
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only core path; `Vec<u8>` opaque payloads leave
//!   serialisation to the caller.
//! - `step` is pure: no I/O, no global state, no time besides the
//!   `now_ns` parameter.
//! - All public types `Debug + Clone + PartialEq`.

#![forbid(unsafe_code)]

pub mod authenticated;
pub mod cluster;
pub mod invariants;
pub mod messages;
pub mod node;
pub mod step;
pub mod types;

pub use authenticated::{
    sign_proposal, AuthenticatedError, ProposalBody, ProposalVerifier, VerifiedProposal,
};
pub use cluster::{Cluster, NetworkPolicy};
pub use messages::{
    AppendEntriesRequest, AppendEntriesResponse, Message, RequestVoteRequest, RequestVoteResponse,
};
pub use node::{Config, RaftNode, Role};
pub use step::{step, Action, Event};
pub use types::{Category, Entry, LogIndex, NodeId, Term};
