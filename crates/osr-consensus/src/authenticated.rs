//! Authenticated application ingress for consensus proposals.
//!
//! The Raft state machine deliberately remains an opaque-byte model so
//! it can be compared with the TLA+ specification. Production callers
//! enter through this module: proposal metadata, safety category, and
//! track-state entry bytes are signed as one body, verified before
//! proposal, and verified again by each committed-log consumer.

use std::collections::BTreeMap;

use osr_core::{EntityId, EntryId};
use osr_crypto::Ed25519SigningKey;
use osr_secbus::{sign_bytes, verify_signed, KeyRegistry, SignedBytes, VerifyError};
use serde::{Deserialize, Serialize};

use crate::{Category, Cluster, Entry as ConsensusEntry, NodeId, Role};

/// RFC 0017 v2 maximum accepted age at application ingress.
pub const DEFAULT_MAX_AGE_NS: u64 = 60_000_000_000;
/// Small positive clock skew tolerated between a sender and leader.
pub const DEFAULT_MAX_FUTURE_SKEW_NS: u64 = 5_000_000_000;

/// The signed portion of an application proposal. The category is
/// included so an attacker cannot downgrade a Safety entry to Advisory.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProposalBody {
    pub entry_id: EntryId,
    pub timestamp_ns: u64,
    pub category: Category,
    pub entry_bytes: Vec<u8>,
}

/// A proposal that passed signature, schema, freshness, and replay
/// checks. Fields are exposed read-only through accessors.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct VerifiedProposal {
    issuer: EntityId,
    body: ProposalBody,
}

impl VerifiedProposal {
    #[must_use]
    pub const fn issuer(&self) -> EntityId {
        self.issuer
    }

    #[must_use]
    pub const fn entry_id(&self) -> EntryId {
        self.body.entry_id
    }

    #[must_use]
    pub const fn timestamp_ns(&self) -> u64 {
        self.body.timestamp_ns
    }

    #[must_use]
    pub const fn category(&self) -> Category {
        self.body.category
    }

    #[must_use]
    pub fn entry_bytes(&self) -> &[u8] {
        &self.body.entry_bytes
    }
}

/// Rejection reasons for the authenticated ingress/apply boundary.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AuthenticatedError {
    UnknownIssuer,
    BadSignature,
    MalformedEnvelope,
    InvalidEntryId,
    EntryMetadataMismatch,
    Stale,
    FutureTimestamp,
    Replay,
    NotLeader,
    FailRestrictive,
    CategoryMismatch,
}

impl From<VerifyError> for AuthenticatedError {
    fn from(value: VerifyError) -> Self {
        match value {
            VerifyError::UnknownIssuer => Self::UnknownIssuer,
            VerifyError::BadSignature => Self::BadSignature,
        }
    }
}

#[derive(Deserialize)]
struct TrackEntryMetadata {
    entry_id: EntryId,
    timestamp_ns: u64,
}

/// Stateful replay/freshness verifier. Deployments construct one per
/// ingress or committed-log consumer from the frozen key registry.
#[derive(Clone, Debug)]
pub struct ProposalVerifier {
    registry: KeyRegistry,
    highest_entry_by_issuer: BTreeMap<EntityId, EntryId>,
    max_age_ns: u64,
    max_future_skew_ns: u64,
}

impl ProposalVerifier {
    #[must_use]
    pub fn new(registry: KeyRegistry) -> Self {
        Self {
            registry,
            highest_entry_by_issuer: BTreeMap::new(),
            max_age_ns: DEFAULT_MAX_AGE_NS,
            max_future_skew_ns: DEFAULT_MAX_FUTURE_SKEW_NS,
        }
    }

    #[must_use]
    pub fn with_windows(registry: KeyRegistry, max_age_ns: u64, max_future_skew_ns: u64) -> Self {
        Self {
            registry,
            highest_entry_by_issuer: BTreeMap::new(),
            max_age_ns,
            max_future_skew_ns,
        }
    }

    /// Verify a newly received proposal and record its entry id only
    /// after every check passes.
    pub fn verify_ingress(
        &mut self,
        envelope: &SignedBytes,
        leader_now_ns: u64,
    ) -> Result<VerifiedProposal, AuthenticatedError> {
        self.verify(envelope, Some(leader_now_ns))
    }

    /// Verify an entry read from the committed prefix. Freshness was
    /// already enforced at ingress, so historical committed entries do
    /// not become invalid merely because time advances. Signature,
    /// schema, metadata, and monotonic replay checks still apply.
    pub fn verify_committed(
        &mut self,
        envelope: &SignedBytes,
    ) -> Result<VerifiedProposal, AuthenticatedError> {
        self.verify(envelope, None)
    }

    /// Decode and verify the signed envelope stored in a committed
    /// consensus entry, including the signed-vs-Raft category match.
    pub fn verify_committed_entry(
        &mut self,
        entry: &ConsensusEntry,
    ) -> Result<VerifiedProposal, AuthenticatedError> {
        let envelope: SignedBytes = serde_json::from_slice(&entry.value)
            .map_err(|_| AuthenticatedError::MalformedEnvelope)?;
        let proposal = self.verify_committed(&envelope)?;
        if proposal.category() != entry.category {
            return Err(AuthenticatedError::CategoryMismatch);
        }
        Ok(proposal)
    }

    fn verify(
        &mut self,
        envelope: &SignedBytes,
        leader_now_ns: Option<u64>,
    ) -> Result<VerifiedProposal, AuthenticatedError> {
        let payload = verify_signed(&self.registry, envelope)?;
        let body: ProposalBody =
            serde_json::from_slice(payload).map_err(|_| AuthenticatedError::MalformedEnvelope)?;
        if body.entry_id.0 == 0 {
            return Err(AuthenticatedError::InvalidEntryId);
        }

        let metadata: TrackEntryMetadata = serde_json::from_slice(&body.entry_bytes)
            .map_err(|_| AuthenticatedError::MalformedEnvelope)?;
        if metadata.entry_id != body.entry_id || metadata.timestamp_ns != body.timestamp_ns {
            return Err(AuthenticatedError::EntryMetadataMismatch);
        }

        if let Some(now_ns) = leader_now_ns {
            if body.timestamp_ns > now_ns.saturating_add(self.max_future_skew_ns) {
                return Err(AuthenticatedError::FutureTimestamp);
            }
            if now_ns.saturating_sub(body.timestamp_ns) > self.max_age_ns {
                return Err(AuthenticatedError::Stale);
            }
        }

        if self
            .highest_entry_by_issuer
            .get(&envelope.issuer)
            .is_some_and(|highest| body.entry_id <= *highest)
        {
            return Err(AuthenticatedError::Replay);
        }

        self.highest_entry_by_issuer
            .insert(envelope.issuer, body.entry_id);
        Ok(VerifiedProposal {
            issuer: envelope.issuer,
            body,
        })
    }
}

/// Sign the metadata, category, and serialized track-state entry as one
/// opaque envelope.
pub fn sign_proposal(
    issuer: EntityId,
    entry_id: EntryId,
    timestamp_ns: u64,
    category: Category,
    entry_bytes: Vec<u8>,
    key: &Ed25519SigningKey,
) -> Result<SignedBytes, AuthenticatedError> {
    let body = ProposalBody {
        entry_id,
        timestamp_ns,
        category,
        entry_bytes,
    };
    let payload = serde_json::to_vec(&body).map_err(|_| AuthenticatedError::MalformedEnvelope)?;
    Ok(sign_bytes(issuer, payload, key))
}

impl Cluster {
    /// Verify and append an authenticated application proposal. The
    /// consensus log stores the signed envelope so each consumer can
    /// independently verify it before deserializing the track entry.
    pub fn propose_signed(
        &mut self,
        at: NodeId,
        envelope: &SignedBytes,
        verifier: &mut ProposalVerifier,
        leader_now_ns: u64,
    ) -> Result<(), AuthenticatedError> {
        let Some(node) = self.nodes.get(&at) else {
            return Err(AuthenticatedError::NotLeader);
        };
        if node.role != Role::Leader {
            return Err(AuthenticatedError::NotLeader);
        }

        // Verify without mutating replay state if the core would reject
        // a Safety proposal for stale quorum confirmation.
        let category_hint = verify_signed(&verifier.registry, envelope)
            .map_err(AuthenticatedError::from)
            .and_then(|payload| {
                serde_json::from_slice::<ProposalBody>(payload)
                    .map(|body| body.category)
                    .map_err(|_| AuthenticatedError::MalformedEnvelope)
            })?;
        if category_hint == Category::Safety && !node.quorum_confirmation_fresh() {
            return Err(AuthenticatedError::FailRestrictive);
        }

        let proposal = verifier.verify_ingress(envelope, leader_now_ns)?;
        let value =
            serde_json::to_vec(envelope).map_err(|_| AuthenticatedError::MalformedEnvelope)?;
        self.propose(at, value, proposal.category());
        Ok(())
    }
}
