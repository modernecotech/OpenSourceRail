//! Thin reference hosts: pure railway decisions remain in existing crates.
#![forbid(unsafe_code)]
use osr_consensus::{disk::DiskJournal, Category, Config, NodeId, ProposalVerifier, RaftNode};
use osr_core::{
    deployment::{FrozenRailway, ParticipantRole},
    resources::*,
    *,
};
use osr_crypto::{Ed25519PublicKey, Ed25519SigningKey};
use osr_interlocking::{resource_log::ResourceEvent, DerivedState, Entry, EntryPayload};
use osr_proto::{RuntimeKind, RuntimePacket};
use osr_secbus::{sign_bytes, verify_signed, KeyRegistry, SignedBytes};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs,
    io::{self, BufRead, Read, Write},
    path::Path,
};

pub mod clocked_output;
pub mod legacy;
pub mod train;
pub mod wayside;
pub const MAX_LINE: usize = 4 * 1024 * 1024;
pub const MAX_LOG_ENTRIES: usize = 12_000;

pub fn bad(message: impl ToString) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message.to_string())
}
pub fn reference_key(entity: EntityId) -> Ed25519SigningKey {
    // Explicit synthetic, publicly reproducible keys. No operational deployment.
    Ed25519SigningKey::from_seed_bytes(
        &Sha256::digest(format!("osr-reference-key:{}", entity.0)).into(),
    )
}
pub fn load(model: &Path, startup: &Path) -> io::Result<FrozenRailway> {
    FrozenRailway::load_deployment(&fs::read(model)?, &fs::read(startup)?)
        .map_err(|e| bad(format!("configuration: {e:?}")))
}
pub fn registry(frozen: &FrozenRailway) -> io::Result<KeyRegistry> {
    let mut keys = KeyRegistry::new();
    for p in &frozen.model().runtime.participants {
        if !p.revoked {
            keys.insert(
                p.entity,
                Ed25519PublicKey::from_bytes(&p.public_key)
                    .ok_or_else(|| bad("invalid public key"))?,
            );
        }
    }
    Ok(keys)
}
#[derive(Debug)]
pub struct Channel {
    pub frozen: FrozenRailway,
    pub entity: EntityId,
    keys: KeyRegistry,
    key: Ed25519SigningKey,
}
impl Channel {
    pub fn new(frozen: FrozenRailway, entity: EntityId) -> io::Result<Self> {
        let participant = frozen
            .model()
            .runtime
            .participants
            .iter()
            .find(|p| p.entity == entity && !p.revoked)
            .ok_or_else(|| bad("unknown/revoked local identity"))?;
        let key = reference_key(entity);
        if key.public().to_bytes() != participant.public_key {
            return Err(bad("reference key differs from frozen identity"));
        }
        Ok(Self {
            keys: registry(&frozen)?,
            frozen,
            entity,
            key,
        })
    }
    pub fn sign<T: Serialize>(
        &self,
        kind: RuntimeKind,
        value: &T,
        now: u64,
        journal: &mut DiskJournal,
    ) -> io::Result<SignedBytes> {
        journal.sent = journal
            .sent
            .checked_add(1)
            .ok_or_else(|| bad("sequence exhausted"))?;
        let participant = self
            .frozen
            .model()
            .runtime
            .participants
            .iter()
            .find(|p| p.entity == self.entity)
            .ok_or_else(|| bad("local identity"))?;
        let bytes = postcard::to_allocvec(value).map_err(bad)?;
        if bytes.len() > 512 * 1024 {
            return Err(bad(
                "packet capacity; inhibit until controlled restart/repair",
            ));
        }
        let packet = RuntimePacket {
            schema: "osr-runtime/1".into(),
            configuration: self.frozen.configuration(),
            session: participant.session,
            sequence: journal.sent,
            observed_ns: now,
            kind,
            bytes,
        };
        Ok(sign_bytes(
            self.entity,
            postcard::to_allocvec(&packet).map_err(bad)?,
            &self.key,
        ))
    }
    pub fn receive(
        &self,
        signed: &SignedBytes,
        now: u64,
        journal: &mut DiskJournal,
    ) -> io::Result<RuntimePacket> {
        if signed.payload.len() > 768 * 1024 {
            return Err(bad("packet bound"));
        }
        let payload =
            verify_signed(&self.keys, signed).map_err(|e| bad(format!("signature: {e:?}")))?;
        let packet: RuntimePacket = postcard::from_bytes(payload).map_err(bad)?;
        let p = self
            .frozen
            .model()
            .runtime
            .participants
            .iter()
            .find(|p| p.entity == signed.issuer && !p.revoked)
            .ok_or_else(|| bad("issuer"))?;
        if !packet.validate(self.frozen.configuration(), p.session, now)
            || packet.sequence <= journal.received.get(&p.entity.0).copied().unwrap_or(0)
        {
            return Err(bad("configuration/session/time/replay"));
        }
        let expected = match packet.kind {
            RuntimeKind::Raft | RuntimeKind::CommittedPrefix => ParticipantRole::Voter,
            RuntimeKind::Proposal => p.role.clone(),
        };
        if p.role != expected
            || (p.role == ParticipantRole::Voter
                && !self.frozen.model().runtime.voters.contains(&p.entity))
        {
            return Err(bad("sender role"));
        }
        journal.received.insert(p.entity.0, packet.sequence);
        Ok(packet)
    }
    pub fn proposal(
        &self,
        payload: EntryPayload,
        now: u64,
        journal: &mut DiskJournal,
    ) -> io::Result<SignedBytes> {
        let seq = journal
            .sent
            .checked_add(1)
            .ok_or_else(|| bad("entry sequence"))?;
        if seq > u64::from(u32::MAX) || self.entity.0 > u64::from(u32::MAX) {
            return Err(bad("entry ID capacity"));
        }
        let entry = Entry {
            entry_id: EntryId((self.entity.0 << 32) | seq),
            term: 0,
            timestamp_ns: now,
            payload,
        };
        let envelope = osr_consensus::sign_proposal(
            self.entity,
            entry.entry_id,
            now,
            Category::Safety,
            serde_json::to_vec(&entry).map_err(bad)?,
            &self.key,
        )
        .map_err(|e| bad(format!("proposal signature: {e:?}")))?;
        self.sign(RuntimeKind::Proposal, &envelope, now, journal)
    }
    pub fn validate_entry(&self, issuer: EntityId, entry: &Entry) -> io::Result<()> {
        let p = self
            .frozen
            .model()
            .runtime
            .participants
            .iter()
            .find(|p| p.entity == issuer && !p.revoked)
            .ok_or_else(|| bad("issuer"))?;
        let owns = |owner: Owner| {
            p.role == ParticipantRole::Train
                && owner.train.0 == issuer.0
                && self
                    .frozen
                    .model()
                    .trains
                    .iter()
                    .any(|t| t.config.owner == owner)
        };
        let local = |resource: ResourceId| {
            p.role == ParticipantRole::Infrastructure && p.resources.contains(&resource)
        };
        let allowed = match &entry.payload {
            EntryPayload::ResourceControl(event) => match event {
                ResourceEvent::Bootstrap {
                    configuration,
                    model,
                } => {
                    p.role == ParticipantRole::Voter
                        && *configuration == self.frozen.configuration()
                        && model.as_ref() == self.frozen.model()
                }
                ResourceEvent::Reserve { owner, .. } | ResourceEvent::Integrity { owner, .. } => {
                    owns(*owner)
                }
                ResourceEvent::Withdraw(g) => owns(g.owner),
                ResourceEvent::LocalProof(proof) => {
                    local(proof.resource) && proof.controller.0 == 900
                }
                ResourceEvent::Clear(r) | ResourceEvent::Block(r) | ResourceEvent::Reconcile(r) => {
                    local(*r)
                }
                ResourceEvent::Restart(_) => {
                    p.role == ParticipantRole::Infrastructure && p.entity == EntityId(900)
                }
            },
            EntryPayload::TrainRegistration(r) => {
                p.role == ParticipantRole::Train
                    && r.train_id.0 == issuer.0
                    && self.frozen.model().trains.iter().any(|t| {
                        t.config.owner.train == r.train_id
                            && t.config.length_mm == r.consist.length_mm
                            && {
                                let mut expected = ConsistDescriptor::reference_3car();
                                expected.length_mm = t.config.length_mm;
                                expected == r.consist
                            }
                    })
            }
            EntryPayload::TrainPositionReport(r) => {
                p.role == ParticipantRole::Train
                    && r.train_id.0 == issuer.0
                    && r.onboard_time_ns == entry.timestamp_ns
                    && r.heading == r.head_position.track_ref.direction
                    && r.speed_mmps >= 0
                    && r.speed_mmps <= 100_000
                    && r.speed_uncertainty_mmps <= 100_000
                    && valid_report_geometry(&self.frozen, r)
            }
            EntryPayload::SectionIntrusion(r) => {
                p.role == ParticipantRole::Infrastructure
                    && self.frozen.model().resources.iter().any(|resource| {
                        resource.section == r.section && p.resources.contains(&resource.id)
                    })
            }
            EntryPayload::SwitchObservation(_) => {
                p.role == ParticipantRole::Infrastructure && issuer == EntityId(900)
            }
            EntryPayload::SpeedRestriction(r) => {
                p.role == ParticipantRole::Infrastructure
                    && self.frozen.model().resources.iter().any(|resource| {
                        resource.section == r.section && p.resources.contains(&resource.id)
                    })
            }
            _ => false,
        };
        if allowed {
            Ok(())
        } else {
            Err(bad("message type/asset issuer permission"))
        }
    }
}
fn valid_report_geometry(
    frozen: &FrozenRailway,
    r: &osr_interlocking::TrainPositionReport,
) -> bool {
    let Some(train) = frozen
        .model()
        .trains
        .iter()
        .find(|t| t.config.owner.train == r.train_id)
    else {
        return false;
    };
    let Some(route) = frozen
        .model()
        .routes
        .iter()
        .find(|p| p.id == train.permitted_route)
    else {
        return false;
    };
    let progress = |p: Position| -> Option<u64> {
        if p.uncertainty_mm > train.config.maximum_position_uncertainty_mm
            || p.track_ref.direction != route.direction
            || p.track_ref.offset_mm < 0
        {
            return None;
        }
        let resource = frozen
            .model()
            .resources
            .iter()
            .find(|a| a.section == p.track_ref.section)?;
        let segment = route.segments.iter().find(|s| s.resource == resource.id)?;
        let offset = p.track_ref.offset_mm as u64;
        (offset <= segment.end_mm - segment.start_mm).then_some(segment.start_mm + offset)
    };
    let (Some(head), Some(tail)) = (progress(r.head_position), progress(r.tail_position)) else {
        return false;
    };
    let length = u64::from(train.config.length_mm);
    let uncertainty =
        u64::from(r.head_position.uncertainty_mm) + u64::from(r.tail_position.uncertainty_mm);
    head >= tail
        && (head - tail).abs_diff(length) <= uncertainty
        && r.pack_soc_ppt <= 1000
        && !r.contributing_sources.is_empty()
        && r.contributing_sources.len() <= 4
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Prefix {
    pub from_index: usize,
    pub commit_index: usize,
    pub entries: Vec<osr_consensus::Entry>,
}
pub fn apply_entry(
    channel: &Channel,
    verifier: &mut ProposalVerifier,
    state: &mut DerivedState,
    entry: &osr_consensus::Entry,
) -> io::Result<EntryId> {
    let proposal = verifier
        .verify_committed_entry(entry)
        .map_err(|e| bad(format!("committed signature: {e:?}")))?;
    if proposal.category() != Category::Safety {
        return Err(bad("load-bearing position/protection cannot be Advisory"));
    }
    let mut domain: Entry = serde_json::from_slice(proposal.entry_bytes()).map_err(bad)?;
    if domain.entry_id != proposal.entry_id() || domain.timestamp_ns != proposal.timestamp_ns() {
        return Err(bad("committed proposal metadata mismatch"));
    }
    channel.validate_entry(proposal.issuer(), &domain)?;
    domain.term = entry.term.0;
    let identity = domain.entry_id;
    state.apply(&domain);
    Ok(identity)
}
pub fn raft_config(frozen: &FrozenRailway, entity: EntityId) -> io::Result<Config> {
    let me = NodeId(u16::try_from(entity.0).map_err(bad)?);
    let peers = frozen
        .model()
        .runtime
        .voters
        .iter()
        .map(|p| u16::try_from(p.0).map(NodeId).map_err(bad))
        .collect::<io::Result<_>>()?;
    let mut cfg = Config::with_defaults(me, peers);
    cfg.max_append_entries = 12;
    cfg.election_timeout_ns = 300_000_000 + entity.0 % 10 * 70_000_000;
    cfg.heartbeat_interval_ns = 100_000_000;
    cfg.fail_restrictive_window_ns = 1_000_000_000;
    Ok(cfg)
}
pub fn network(frozen: &FrozenRailway) -> io::Result<Network> {
    let mut net = Network::default();
    let routes = frozen
        .model()
        .routes
        .get(..2)
        .ok_or_else(|| bad("reference needs two operating routes"))?;
    if routes[0].direction != Direction::Forward
        || routes[1].direction != Direction::Reverse
        || frozen
            .model()
            .trains
            .iter()
            .any(|t| !routes.iter().any(|r| r.id == t.permitted_route))
    {
        return Err(bad("unsupported reference route profile"));
    }
    for route in routes {
        let mut ids = Vec::new();
        for segment in &route.segments {
            let r = &frozen.model().resources[usize::from(segment.resource.0)];
            ids.push(r.section);
            net.sections.insert(
                r.section,
                Section {
                    id: r.section,
                    from_station: StationId(1),
                    to_station: StationId(2),
                    length_mm: segment.end_mm - segment.start_mm,
                    max_speed_mps: segment.speed_limit_mmps as f32 / 1000.,
                },
            );
        }
        net.lines.push(Line {
            name: route.asset_id.clone(),
            stations: vec![StationId(1), StationId(2)],
            forward_sections: if route.direction == Direction::Forward {
                ids.clone()
            } else {
                Vec::new()
            },
            reverse_sections: if route.direction == Direction::Reverse {
                ids
            } else {
                Vec::new()
            },
            is_ring: false,
        });
    }
    Ok(net)
}
pub fn track_ref(frozen: &FrozenRailway, route: RouteId, progress: u64) -> io::Result<TrackRef> {
    let path = frozen
        .model()
        .routes
        .iter()
        .find(|r| r.id == route)
        .ok_or_else(|| bad("route"))?;
    let s = path
        .segments
        .iter()
        .find(|s| s.start_mm <= progress && progress < s.end_mm)
        .ok_or_else(|| bad("position outside route"))?;
    Ok(TrackRef {
        section: frozen.model().resources[usize::from(s.resource.0)].section,
        offset_mm: (progress - s.start_mm) as i64,
        direction: path.direction,
    })
}
pub fn run_lines<T: for<'a> Deserialize<'a>, R: Serialize>(
    mut handle: impl FnMut(T) -> io::Result<R>,
) -> io::Result<()> {
    let stdin = io::stdin();
    let mut input = stdin.lock();
    let mut stdout = io::stdout().lock();
    loop {
        let mut bytes = Vec::new();
        let count = input
            .by_ref()
            .take((MAX_LINE + 1) as u64)
            .read_until(b'\n', &mut bytes)?;
        if count == 0 {
            break;
        }
        if count > MAX_LINE || bytes.last() != Some(&b'\n') {
            return Err(bad("framing capacity/unterminated input"));
        }
        let answer = serde_json::from_slice(&bytes)
            .map_err(bad)
            .and_then(&mut handle);
        if answer
            .as_ref()
            .is_err_and(|e| e.kind() == io::ErrorKind::BrokenPipe)
        {
            return Err(answer.err().expect("error"));
        }
        let value = match answer {
            Ok(result) => serde_json::json!({"ok":true,"result":result}),
            Err(error) => serde_json::json!({"ok":false,"error":error.to_string()}),
        };
        serde_json::to_writer(&mut stdout, &value).map_err(bad)?;
        stdout.write_all(b"\n")?;
        stdout.flush()?;
    }
    Ok(())
}
pub fn args() -> io::Result<BTreeMap<String, String>> {
    let mut values = BTreeMap::new();
    let mut args = std::env::args().skip(1);
    while let Some(flag) = args.next() {
        values.insert(
            flag,
            args.next().ok_or_else(|| bad("missing argument value"))?,
        );
    }
    Ok(values)
}
pub fn required<'a>(args: &'a BTreeMap<String, String>, key: &str) -> io::Result<&'a str> {
    args.get(key)
        .map(String::as_str)
        .ok_or_else(|| bad(format!("missing {key}")))
}
