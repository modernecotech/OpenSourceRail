use osr_consensus::{
    sign_proposal, AuthenticatedError, Category, Cluster, Entry as ConsensusEntry, LogIndex,
    ProposalVerifier, Term,
};
use osr_core::{EntityId, EntryId};
use osr_crypto::{ed25519_generate, Ed25519SigningKey};
use osr_interlocking::log::{Entry, EntryPayload, FormatVersion};
use osr_secbus::{KeyRegistry, SignedBytes};

const ISSUER: EntityId = EntityId::new(41);
const NOW_NS: u64 = 120_000_000_000;

fn track_entry(id: u64, timestamp_ns: u64) -> Entry {
    Entry {
        entry_id: EntryId::new(id),
        term: 1,
        timestamp_ns,
        payload: EntryPayload::FormatVersion(FormatVersion {
            current: 2,
            min_compatible: 2,
            schema_sha256_hex: "test".into(),
        }),
    }
}

fn setup() -> (Cluster, Ed25519SigningKey, ProposalVerifier) {
    let key = ed25519_generate();
    let mut registry = KeyRegistry::new();
    registry.insert(ISSUER, key.public());
    let mut cluster = Cluster::new(3, 100_000_000);
    cluster
        .run_until_leader(30_000_000, 200)
        .expect("leader election");
    (cluster, key, ProposalVerifier::new(registry))
}

fn envelope(
    key: &Ed25519SigningKey,
    id: u64,
    timestamp_ns: u64,
    category: Category,
) -> SignedBytes {
    let bytes = serde_json::to_vec(&track_entry(id, timestamp_ns)).expect("entry serialization");
    sign_proposal(ISSUER, EntryId::new(id), timestamp_ns, category, bytes, key)
        .expect("proposal serialization")
}

#[test]
fn honest_signed_entry_commits_and_reverifies_before_decode() {
    let (mut cluster, key, mut ingress) = setup();
    let leader = cluster.leader().unwrap();
    let signed = envelope(&key, 1, NOW_NS, Category::Safety);

    cluster
        .propose_signed(leader, &signed, &mut ingress, NOW_NS)
        .expect("authenticated proposal");
    assert!(cluster.run_until_committed(30_000_000, LogIndex::new(1), 200));

    let mut registry = KeyRegistry::new();
    registry.insert(ISSUER, key.public());
    let consumer = ProposalVerifier::new(registry);
    for node in cluster.nodes.values() {
        let slot = &node.committed_prefix()[0];
        let verified = consumer
            .clone()
            .verify_committed_entry(slot)
            .expect("consumer verification");
        let decoded: Entry =
            serde_json::from_slice(verified.entry_bytes()).expect("decode after verify");
        assert_eq!(decoded.entry_id, EntryId::new(1));
    }
}

#[test]
fn forged_signature_is_rejected_before_log_append() {
    let (mut cluster, key, mut ingress) = setup();
    let leader = cluster.leader().unwrap();
    let mut signed = envelope(&key, 1, NOW_NS, Category::Safety);
    signed.signature[0] ^= 1;

    assert_eq!(
        cluster.propose_signed(leader, &signed, &mut ingress, NOW_NS),
        Err(AuthenticatedError::BadSignature)
    );
    assert_eq!(cluster.nodes[&leader].log_len(), LogIndex::zero());
}

#[test]
fn altered_payload_is_rejected_before_deserialization() {
    let (mut cluster, key, mut ingress) = setup();
    let leader = cluster.leader().unwrap();
    let mut signed = envelope(&key, 1, NOW_NS, Category::Safety);
    signed.payload[0] ^= 1;

    assert_eq!(
        cluster.propose_signed(leader, &signed, &mut ingress, NOW_NS),
        Err(AuthenticatedError::BadSignature)
    );
    assert!(cluster.nodes[&leader].log.is_empty());
}

#[test]
fn replay_and_stale_entries_are_rejected() {
    let (mut cluster, key, mut ingress) = setup();
    let leader = cluster.leader().unwrap();
    let signed = envelope(&key, 1, NOW_NS, Category::Advisory);
    cluster
        .propose_signed(leader, &signed, &mut ingress, NOW_NS)
        .unwrap();
    assert_eq!(
        cluster.propose_signed(leader, &signed, &mut ingress, NOW_NS),
        Err(AuthenticatedError::Replay)
    );

    let stale = envelope(&key, 2, NOW_NS - 61_000_000_000, Category::Advisory);
    assert_eq!(
        cluster.propose_signed(leader, &stale, &mut ingress, NOW_NS),
        Err(AuthenticatedError::Stale)
    );
}

#[test]
fn unknown_issuer_and_future_timestamp_are_rejected() {
    let (mut cluster, key, mut ingress) = setup();
    let leader = cluster.leader().unwrap();
    let mut unknown = envelope(&key, 1, NOW_NS, Category::Advisory);
    unknown.issuer = EntityId::new(999);
    assert_eq!(
        cluster.propose_signed(leader, &unknown, &mut ingress, NOW_NS),
        Err(AuthenticatedError::UnknownIssuer)
    );

    let future = envelope(&key, 1, NOW_NS + 6_000_000_000, Category::Advisory);
    assert_eq!(
        cluster.propose_signed(leader, &future, &mut ingress, NOW_NS),
        Err(AuthenticatedError::FutureTimestamp)
    );
}

#[test]
fn signed_metadata_must_match_the_track_entry() {
    let (mut cluster, key, mut ingress) = setup();
    let leader = cluster.leader().unwrap();
    let bytes = serde_json::to_vec(&track_entry(2, NOW_NS)).unwrap();
    let signed = sign_proposal(
        ISSUER,
        EntryId::new(1),
        NOW_NS,
        Category::Advisory,
        bytes,
        &key,
    )
    .unwrap();
    assert_eq!(
        cluster.propose_signed(leader, &signed, &mut ingress, NOW_NS),
        Err(AuthenticatedError::EntryMetadataMismatch)
    );
}

#[test]
fn committed_category_must_match_the_signed_category() {
    let key = ed25519_generate();
    let mut registry = KeyRegistry::new();
    registry.insert(ISSUER, key.public());
    let signed = envelope(&key, 1, NOW_NS, Category::Safety);
    let encoded = serde_json::to_vec(&signed).unwrap();
    let slot = ConsensusEntry::new(Term(1), encoded, Category::Advisory);
    let mut verifier = ProposalVerifier::new(registry);
    assert_eq!(
        verifier.verify_committed_entry(&slot),
        Err(AuthenticatedError::CategoryMismatch)
    );
}
