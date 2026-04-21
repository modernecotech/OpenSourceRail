//! Raft RPC message types.
//!
//! Names and field layouts deliberately mirror the TLA+ spec
//! (`formal/tla/SMRaft.tla` §TYPES) for direct cross-checking.

use serde::{Deserialize, Serialize};

use crate::types::{Entry, LogIndex, NodeId, Term};

/// Any Raft RPC message.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Message {
    RequestVoteRequest(RequestVoteRequest),
    RequestVoteResponse(RequestVoteResponse),
    AppendEntriesRequest(AppendEntriesRequest),
    AppendEntriesResponse(AppendEntriesResponse),
}

impl Message {
    #[must_use]
    pub fn from(&self) -> NodeId {
        match self {
            Message::RequestVoteRequest(m) => m.from,
            Message::RequestVoteResponse(m) => m.from,
            Message::AppendEntriesRequest(m) => m.from,
            Message::AppendEntriesResponse(m) => m.from,
        }
    }

    #[must_use]
    pub fn to(&self) -> NodeId {
        match self {
            Message::RequestVoteRequest(m) => m.to,
            Message::RequestVoteResponse(m) => m.to,
            Message::AppendEntriesRequest(m) => m.to,
            Message::AppendEntriesResponse(m) => m.to,
        }
    }

    #[must_use]
    pub fn term(&self) -> Term {
        match self {
            Message::RequestVoteRequest(m) => m.term,
            Message::RequestVoteResponse(m) => m.term,
            Message::AppendEntriesRequest(m) => m.term,
            Message::AppendEntriesResponse(m) => m.term,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RequestVoteRequest {
    pub term: Term,
    pub from: NodeId,
    pub to: NodeId,
    /// Length of the candidate's log.
    pub last_log_index: LogIndex,
    /// Term of the last entry in the candidate's log (or 0 if empty).
    pub last_log_term: Term,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RequestVoteResponse {
    pub term: Term,
    pub from: NodeId,
    pub to: NodeId,
    pub vote_granted: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppendEntriesRequest {
    pub term: Term,
    pub from: NodeId,
    pub to: NodeId,
    /// Index immediately preceding the new entries in the leader's log.
    pub prev_log_index: LogIndex,
    /// Term of the entry at `prev_log_index`, or 0 when `prev_log_index == 0`.
    pub prev_log_term: Term,
    /// Entries being appended (empty = heartbeat).
    pub entries: Vec<Entry>,
    /// Leader's commitIndex.
    pub leader_commit: LogIndex,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppendEntriesResponse {
    pub term: Term,
    pub from: NodeId,
    pub to: NodeId,
    pub success: bool,
    /// On success: the highest index the follower now has.
    /// On failure: unused (0).
    pub match_index: LogIndex,
}
