//! Fail-closed persistence envelope for the consensus node's stable state.
//!
//! Storage drivers may write the returned bytes to a qualified atomic medium.
//! The envelope detects truncation, trailing bytes, corruption, wrong-node
//! restore and internally inconsistent commit indices.  Its CRC is an error-
//! detection code, not an authenticity mechanism; signed application entries
//! remain the security boundary.

use serde::{Deserialize, Serialize};

use crate::{Config, Entry, LogIndex, NodeId, RaftNode, Role, Term};

const MAGIC: &[u8; 8] = b"OSRRFST1";
const VERSION: u16 = 1;
const HEADER_LEN: usize = MAGIC.len() + 4;
const TRAILER_LEN: usize = 4;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RestoreError {
    Truncated,
    BadMagic,
    LengthMismatch,
    ChecksumMismatch,
    Malformed,
    UnsupportedVersion(u16),
    WrongNode { expected: NodeId, actual: NodeId },
    CommitBeyondLog,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum WriteFault {
    None,
    DiskFull,
    PartialWrite(usize),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum StoreError {
    DiskFull,
    PartialWrite,
}

#[derive(Clone, Debug, Default)]
pub struct StableStore {
    committed: Option<Vec<u8>>,
}

#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct PersistentState {
    version: u16,
    node_id: NodeId,
    current_term: Term,
    voted_for: Option<NodeId>,
    log: Vec<Entry>,
    commit_index: LogIndex,
}

impl StableStore {
    #[must_use]
    pub fn from_node(node: &RaftNode) -> Self {
        Self {
            committed: Some(encode(node)),
        }
    }

    #[must_use]
    pub fn bytes(&self) -> Option<&[u8]> {
        self.committed.as_deref()
    }

    /// Model an atomic replacement. Disk-full and partial-write faults leave
    /// the previously committed image untouched.
    pub fn save(&mut self, node: &RaftNode, fault: WriteFault) -> Result<(), StoreError> {
        let candidate = encode(node);
        match fault {
            WriteFault::None => {
                self.committed = Some(candidate);
                Ok(())
            }
            WriteFault::DiskFull => Err(StoreError::DiskFull),
            WriteFault::PartialWrite(limit) => {
                let _discarded_partial = &candidate[..limit.min(candidate.len())];
                Err(StoreError::PartialWrite)
            }
        }
    }

    /// Deliberately damage the committed medium for a recovery test.
    pub fn corrupt_byte(&mut self, offset: usize) -> bool {
        let Some(bytes) = self.committed.as_mut() else {
            return false;
        };
        let Some(byte) = bytes.get_mut(offset) else {
            return false;
        };
        *byte ^= 0x5a;
        true
    }

    pub fn restore(&self, config: Config, now_ns: u64) -> Result<RaftNode, RestoreError> {
        let bytes = self.committed.as_deref().ok_or(RestoreError::Truncated)?;
        decode(config, now_ns, bytes)
    }
}

#[must_use]
pub fn encode(node: &RaftNode) -> Vec<u8> {
    let state = PersistentState {
        version: VERSION,
        node_id: node.config.me,
        current_term: node.current_term,
        voted_for: node.voted_for,
        log: node.log.clone(),
        commit_index: node.commit_index,
    };
    let payload = serde_json::to_vec(&state).expect("persistent state serialization is infallible");
    let mut bytes = Vec::with_capacity(HEADER_LEN + payload.len() + TRAILER_LEN);
    bytes.extend_from_slice(MAGIC);
    bytes.extend_from_slice(&(payload.len() as u32).to_le_bytes());
    bytes.extend_from_slice(&payload);
    bytes.extend_from_slice(&crc32(&payload).to_le_bytes());
    bytes
}

pub fn decode(config: Config, now_ns: u64, bytes: &[u8]) -> Result<RaftNode, RestoreError> {
    if bytes.len() < HEADER_LEN + TRAILER_LEN {
        return Err(RestoreError::Truncated);
    }
    if &bytes[..MAGIC.len()] != MAGIC {
        return Err(RestoreError::BadMagic);
    }
    let payload_len = u32::from_le_bytes(
        bytes[MAGIC.len()..HEADER_LEN]
            .try_into()
            .map_err(|_| RestoreError::Truncated)?,
    ) as usize;
    let expected_len = HEADER_LEN
        .checked_add(payload_len)
        .and_then(|value| value.checked_add(TRAILER_LEN))
        .ok_or(RestoreError::LengthMismatch)?;
    if bytes.len() != expected_len {
        return Err(RestoreError::LengthMismatch);
    }
    let payload = &bytes[HEADER_LEN..HEADER_LEN + payload_len];
    let recorded = u32::from_le_bytes(
        bytes[HEADER_LEN + payload_len..]
            .try_into()
            .map_err(|_| RestoreError::Truncated)?,
    );
    if crc32(payload) != recorded {
        return Err(RestoreError::ChecksumMismatch);
    }
    let state: PersistentState =
        serde_json::from_slice(payload).map_err(|_| RestoreError::Malformed)?;
    if state.version != VERSION {
        return Err(RestoreError::UnsupportedVersion(state.version));
    }
    if state.node_id != config.me {
        return Err(RestoreError::WrongNode {
            expected: config.me,
            actual: state.node_id,
        });
    }
    if state.commit_index.0 > state.log.len() as u64 {
        return Err(RestoreError::CommitBeyondLog);
    }

    let mut node = RaftNode::new(config, now_ns);
    node.current_term = state.current_term;
    node.voted_for = state.voted_for;
    node.log = state.log;
    node.commit_index = state.commit_index;
    // Every volatile leadership and quorum claim is deliberately discarded.
    node.role = Role::Follower;
    node.last_quorum_confirmed_term = Term::zero();
    node.last_quorum_confirmed_ns = now_ns;
    Ok(node)
}

pub(crate) fn crc32(bytes: &[u8]) -> u32 {
    let mut crc = 0xffff_ffff_u32;
    for byte in bytes {
        crc ^= u32::from(*byte);
        for _ in 0..8 {
            let mask = 0_u32.wrapping_sub(crc & 1);
            crc = (crc >> 1) ^ (0xedb8_8320 & mask);
        }
    }
    !crc
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;

    use super::*;

    fn config(id: u16) -> Config {
        Config::with_defaults(
            NodeId::new(id),
            (0..3).map(NodeId::new).collect::<BTreeSet<_>>(),
        )
    }

    fn envelope(state: &PersistentState) -> Vec<u8> {
        let payload = serde_json::to_vec(state).unwrap();
        let mut bytes = Vec::new();
        bytes.extend_from_slice(MAGIC);
        bytes.extend_from_slice(&(payload.len() as u32).to_le_bytes());
        bytes.extend_from_slice(&payload);
        bytes.extend_from_slice(&crc32(&payload).to_le_bytes());
        bytes
    }

    #[test]
    fn truncation_trailing_bytes_and_magic_fail_closed() {
        let node = RaftNode::new(config(0), 0);
        let bytes = encode(&node);
        assert_eq!(
            decode(config(0), 0, &bytes[..10]).unwrap_err(),
            RestoreError::Truncated
        );
        let mut trailing = bytes.clone();
        trailing.push(0);
        assert_eq!(
            decode(config(0), 0, &trailing).unwrap_err(),
            RestoreError::LengthMismatch
        );
        let mut bad_magic = bytes;
        bad_magic[0] ^= 1;
        assert_eq!(
            decode(config(0), 0, &bad_magic).unwrap_err(),
            RestoreError::BadMagic
        );
    }

    #[test]
    fn unsupported_version_and_commit_beyond_log_fail_closed() {
        let version = PersistentState {
            version: VERSION + 1,
            node_id: NodeId::new(0),
            current_term: Term::zero(),
            voted_for: None,
            log: Vec::new(),
            commit_index: LogIndex::zero(),
        };
        assert_eq!(
            decode(config(0), 0, &envelope(&version)).unwrap_err(),
            RestoreError::UnsupportedVersion(VERSION + 1)
        );
        let inconsistent = PersistentState {
            version: VERSION,
            commit_index: LogIndex::new(1),
            ..version
        };
        assert_eq!(
            decode(config(0), 0, &envelope(&inconsistent)).unwrap_err(),
            RestoreError::CommitBeyondLog
        );
    }

    #[test]
    fn restore_retains_only_stable_fields() {
        let mut node = RaftNode::new(config(0), 0);
        node.current_term = Term(4);
        node.voted_for = Some(NodeId::new(1));
        node.role = Role::Leader;
        node.last_quorum_confirmed_term = Term(4);
        let restored = decode(config(0), 50, &encode(&node)).unwrap();
        assert_eq!(restored.current_term, Term(4));
        assert_eq!(restored.voted_for, Some(NodeId::new(1)));
        assert_eq!(restored.role, Role::Follower);
        assert_eq!(restored.last_quorum_confirmed_term, Term::zero());
        assert!(!restored.quorum_confirmation_fresh());
    }
}
