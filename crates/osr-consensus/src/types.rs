//! Domain types matching the TLA+ spec's Entry record and scalars.

use serde::{Deserialize, Serialize};

/// Opaque identifier of a node in the static membership set.
///
/// Must fit in a `u16` for compactness on the wire — a region will
/// never have more than a few tens of wayside nodes participating
/// in a single consensus group.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Ord, PartialOrd, Serialize, Deserialize)]
pub struct NodeId(pub u16);

impl NodeId {
    #[must_use]
    pub const fn new(id: u16) -> Self {
        Self(id)
    }
}

impl core::fmt::Display for NodeId {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "N{}", self.0)
    }
}

/// A Raft term. Monotonically non-decreasing on each node.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Default, Serialize, Deserialize)]
pub struct Term(pub u64);

impl Term {
    #[must_use]
    pub const fn zero() -> Self {
        Self(0)
    }

    #[must_use]
    pub fn succ(self) -> Self {
        Self(self.0.saturating_add(1))
    }
}

/// 1-indexed log index, matching the TLA+ convention.
///
/// Index 0 sentinel represents "no entry" (e.g., prevIdx=0 in an
/// AppendEntries with an empty log).
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Default, Serialize, Deserialize)]
pub struct LogIndex(pub u64);

impl LogIndex {
    #[must_use]
    pub const fn zero() -> Self {
        Self(0)
    }

    #[must_use]
    pub const fn new(i: u64) -> Self {
        Self(i)
    }

    #[must_use]
    pub fn succ(self) -> Self {
        Self(self.0.saturating_add(1))
    }

    #[must_use]
    pub fn pred(self) -> Self {
        Self(self.0.saturating_sub(1))
    }

    /// 0-indexed Rust-vector slot for this Raft index. Returns
    /// `None` for index 0 (sentinel).
    #[must_use]
    pub fn as_vec_offset(self) -> Option<usize> {
        if self.0 == 0 {
            None
        } else {
            Some((self.0 - 1) as usize)
        }
    }
}

/// Entry category for fail-restrictive treatment.
///
/// Safety entries carry load-bearing state (movement authority,
/// switch commands). Advisory entries are informational (position
/// reports, heartbeats).
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Category {
    Safety,
    Advisory,
}

/// A single log entry.
///
/// The payload is opaque to the consensus layer. Callers serialise
/// domain types (`osr_interlocking::log::Entry` in the rail case)
/// into `value` bytes and deserialise on commit.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Entry {
    pub term: Term,
    pub value: Vec<u8>,
    pub category: Category,
}

impl Entry {
    #[must_use]
    pub fn new(term: Term, value: Vec<u8>, category: Category) -> Self {
        Self { term, value, category }
    }

    /// Last-term helper: term of the final entry in a log slice, or
    /// `Term(0)` for an empty log. Mirrors the TLA+ `LastTerm` helper.
    #[must_use]
    pub fn last_term(log: &[Entry]) -> Term {
        log.last().map(|e| e.term).unwrap_or(Term::zero())
    }
}
