//! Consensus-backed track-state log.
//!
//! Uses a real 3-node `osr-consensus::Cluster`. Entries are
//! serialised to bytes via `serde_json`, proposed to the current
//! Raft leader, and read back from the leader's committed prefix
//! after each tick.
//!
//! # Why 3 nodes?
//!
//! A minimum-meaningful Raft cluster with majority quorum of 2.
//! The sim's MA check doesn't need more; real wayside deployments
//! will scale up once the networking story is in place.
//!
//! # Category mapping
//!
//! - `TrainRegistration` → `Safety` (governs which trains the
//!   interlocking considers authoritative).
//! - `TrainPositionReport` → `Advisory` (high-rate telemetry; not
//!   fail-restrictive).
//!
//! Under nominal operation the consensus cluster always holds fresh
//! quorum confirmation so Safety entries propose successfully.

use std::collections::BTreeSet;

use osr_consensus::{sign_proposal, Category, Cluster, LogIndex, ProposalVerifier};
use osr_core::{EntityId, Position, TrackRef, TrainId};
use osr_crypto::Ed25519SigningKey;
use osr_interlocking::log::{
    Entry, EntryPayload, IntrusionState, PositionSource, SectionIntrusion, TrainDeparture,
    TrainPositionReport, TrainRegistration,
};
use osr_interlocking::DerivedState;
use osr_secbus::KeyRegistry;

use crate::train::Train;

/// A sim-facing wrapper around a three-node consensus cluster.
#[derive(Debug)]
pub struct ConsensusBackend {
    cluster: Cluster,
    signer: Ed25519SigningKey,
    ingress_verifier: ProposalVerifier,
    committed_verifier: ProposalVerifier,
    registered: BTreeSet<TrainId>,
    next_entry_id: u64,
    /// Cached committed-prefix decoded back into `Entry` for the MA
    /// computer to consume. Updated after every `tick`.
    committed: Vec<Entry>,
    /// Cached fold of `committed`. Rebuilt whenever `committed` is
    /// rebuilt in `refresh_committed`, so gate checks stay O(1) in the
    /// prefix length.
    derived: DerivedState,
}

impl ConsensusBackend {
    /// Build a new 3-node cluster and elect a leader. Panics if
    /// the initial election fails — a real deployment would surface
    /// this to an operator, but in the sim it means the tick budget
    /// is too small or the default timeouts are misconfigured.
    #[must_use]
    pub fn new() -> Self {
        // Deterministic simulation-only key. Production keys are minted
        // into secure elements and loaded through a deployment manifest.
        const SIM_AUTHORITY: EntityId = EntityId::new(9_001);
        let signer = Ed25519SigningKey::from_seed_bytes(&[0x5A; 32]);
        let mut registry = KeyRegistry::new();
        registry.insert(SIM_AUTHORITY, signer.public());
        let mut cluster = Cluster::new(3, 100_000_000);
        // Drive ticks at the same cadence the cluster's basic tests
        // use (30 ms × up to 200 ticks = 6 s budget). The fine grain
        // matters: at 150 ms ticks we advance past multiple election
        // timeouts in one call, producing term-race conditions that
        // take several rounds to settle.
        let leader = cluster.run_until_leader(30_000_000, 200);
        assert!(
            leader.is_some(),
            "consensus cluster failed to elect a leader at boot"
        );
        Self {
            cluster,
            signer,
            ingress_verifier: ProposalVerifier::new(registry.clone()),
            committed_verifier: ProposalVerifier::new(registry),
            registered: BTreeSet::new(),
            next_entry_id: 1,
            committed: Vec::new(),
            derived: DerivedState::default(),
        }
    }

    /// Cached derived state — kept in sync with `committed` on every
    /// `refresh_committed`.
    #[must_use]
    pub fn derived_state(&self) -> &DerivedState {
        &self.derived
    }

    /// Number of entries in the committed prefix (after last tick).
    #[must_use]
    pub fn len(&self) -> usize {
        self.committed.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.committed.is_empty()
    }

    /// Committed prefix — suitable for `osr_interlocking::derive_state`.
    #[must_use]
    pub fn entries(&self) -> &[Entry] {
        &self.committed
    }

    /// Propose a `TrainRegistration` the first time we encounter a train.
    pub fn ensure_registered(&mut self, train: &Train, initial_head: TrackRef, t_s: u32) {
        if self.registered.insert(train.id) {
            let entry = Entry {
                entry_id: osr_core::EntryId::new(self.next_entry_id),
                term: 1,
                timestamp_ns: ts_ns_from_s(t_s),
                payload: EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: train.id,
                    consist: train.consist.clone(),
                    initial_position: Position::certain(initial_head),
                }),
            };
            self.next_entry_id += 1;
            self.propose(&entry, Category::Safety);
        }
    }

    /// Propose a `TrainPositionReport`.
    pub fn emit_position(
        &mut self,
        train: &Train,
        head: TrackRef,
        tail_offset_in_head_section: Option<i64>,
        t_s: u32,
    ) {
        let tail_position = match tail_offset_in_head_section {
            Some(off) => Position::certain(TrackRef {
                section: head.section,
                offset_mm: off.max(0),
                direction: head.direction,
            }),
            None => {
                let tail_off = head
                    .offset_mm
                    .saturating_sub(train.consist.length_mm as i64);
                Position::certain(TrackRef {
                    section: head.section,
                    offset_mm: tail_off.max(0),
                    direction: head.direction,
                })
            }
        };
        let entry = Entry {
            entry_id: osr_core::EntryId::new(self.next_entry_id),
            term: 1,
            timestamp_ns: ts_ns_from_s(t_s),
            payload: EntryPayload::TrainPositionReport(TrainPositionReport {
                train_id: train.id,
                head_position: Position::certain(head),
                tail_position,
                speed_mmps: 15_000,
                speed_uncertainty_mmps: 500,
                heading: head.direction,
                contributing_sources: vec![PositionSource::Gnss, PositionSource::Odometry],
                onboard_time_ns: ts_ns_from_s(t_s).saturating_sub(100),
                pack_soc_ppt: (train.soc.clamp(0.0, 1.0) * 1000.0) as u16,
            }),
        };
        self.next_entry_id += 1;
        self.propose(&entry, Category::Advisory);
    }

    /// Hand a fully platformed train out of the interstation-block control
    /// region and clear its section footprint.  It is registered again when
    /// it next enters a controlled section.
    pub fn emit_platform_handoff(&mut self, train_id: TrainId, t_s: u32) {
        let ts = ts_ns_from_s(t_s);
        let entry = Entry {
            entry_id: osr_core::EntryId::new(self.next_entry_id),
            term: 1,
            timestamp_ns: ts,
            payload: EntryPayload::TrainDeparture(TrainDeparture {
                train_id,
                handed_off_to: None,
                handoff_time_ns: ts,
            }),
        };
        self.next_entry_id += 1;
        self.propose(&entry, Category::Safety);
        self.registered.remove(&train_id);
    }

    /// Emit a `SectionIntrusion` consensus entry (RFC 0016 v3).
    pub fn emit_intrusion(
        &mut self,
        section: osr_core::SectionId,
        state: IntrusionState,
        issued_by: osr_core::EntityId,
        t_s: u32,
    ) {
        let ts = ts_ns_from_s(t_s);
        let entry = Entry {
            entry_id: osr_core::EntryId::new(self.next_entry_id),
            term: 1,
            timestamp_ns: ts,
            payload: EntryPayload::SectionIntrusion(SectionIntrusion {
                section,
                state,
                issued_by,
                observed_at_ns: ts,
            }),
        };
        self.next_entry_id += 1;
        self.propose(&entry, Category::Safety);
    }

    /// Advance the consensus cluster by one sim tick and refresh the
    /// cached committed prefix.
    pub fn tick(&mut self, dt_ns: u64) {
        self.cluster.tick(dt_ns);
        self.refresh_committed();
    }

    /// Propose an entry and synchronously wait for it to commit on the
    /// leader. Post-M5 the sim's gate reads `derived_state()`
    /// immediately after emitting a position report, so the commit must
    /// land before we return — otherwise the next `section_available_to`
    /// query sees an empty state and the gate is permissive. Dropped
    /// silently if there is no current leader or the cluster fails to
    /// commit within the budget.
    fn propose(&mut self, entry: &Entry, cat: Category) {
        const SIM_AUTHORITY: EntityId = EntityId::new(9_001);
        let Some(leader) = self.cluster.leader() else {
            return;
        };
        let Ok(bytes) = serde_json::to_vec(entry) else {
            return;
        };
        let signed = sign_proposal(
            SIM_AUTHORITY,
            entry.entry_id,
            entry.timestamp_ns,
            cat,
            bytes,
            &self.signer,
        )
        .expect("track-state entry serialization is infallible");
        self.cluster
            .propose_signed(
                leader,
                &signed,
                &mut self.ingress_verifier,
                entry.timestamp_ns,
            )
            .expect("sim consensus ingress must authenticate");
        // After propose + drain, the leader's log has the entry at
        // `log_len`. Drive the cluster forward until that index commits
        // on the leader (a majority of acks). 30 ms × 30 ticks = 900 ms
        // — comfortably inside the 3 s MA validity window.
        if let Some(leader_node) = self.cluster.nodes.get(&leader) {
            let expected = leader_node.log_len();
            let _ = self.cluster.run_until_committed(30_000_000, expected, 30);
        }
        self.refresh_committed();
    }

    fn refresh_committed(&mut self) {
        let Some(leader) = self.cluster.leader() else {
            return;
        };
        let node = &self.cluster.nodes[&leader];
        let prefix = node.committed_prefix();
        // Fast path: same length → no change.
        if prefix.len() == self.committed.len() {
            return;
        }
        assert!(
            prefix.len() >= self.committed.len(),
            "committed consensus prefix regressed"
        );
        for slot in &prefix[self.committed.len()..] {
            let verified = self
                .committed_verifier
                .verify_committed_entry(slot)
                .expect("committed entry failed authentication");
            let entry = serde_json::from_slice::<Entry>(verified.entry_bytes())
                .expect("authenticated track-state entry failed to decode");
            self.derived.apply(&entry);
            self.committed.push(entry);
        }
    }

    /// Number of consensus commit events observed so far. Useful for
    /// tests that want to assert the cluster is actually doing work.
    #[must_use]
    pub fn commit_index(&self) -> LogIndex {
        let Some(leader) = self.cluster.leader() else {
            return LogIndex::zero();
        };
        self.cluster.nodes[&leader].commit_index
    }
}

impl Default for ConsensusBackend {
    fn default() -> Self {
        Self::new()
    }
}

fn ts_ns_from_s(t_s: u32) -> u64 {
    (t_s as u64).saturating_mul(1_000_000_000)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn boot_elects_a_leader() {
        let b = ConsensusBackend::new();
        assert!(b.cluster.leader().is_some(), "no leader after boot");
    }
}
