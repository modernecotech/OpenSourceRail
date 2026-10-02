//! One OS process per voter or independently identified local I/O controller.
use super::*;
use osr_consensus::{step, Action, Event, Message, Role};

#[derive(Debug, Deserialize)]
#[serde(tag = "command", rename_all = "snake_case", deny_unknown_fields)]
pub enum Command {
    Tick {
        now: u64,
    },
    Receive {
        now: u64,
        envelope: SignedBytes,
    },
    Publish {
        now: u64,
        payloads: Vec<EntryPayload>,
    },
    Observe {
        now: u64,
        from_index: usize,
    },
    StationIo {
        now: u64,
        platform: ResourceId,
        phase: osr_ato::station::StationPhase,
        charge_requested: bool,
        inputs: osr_ato::station::StationInputs,
    },
    Compact {
        now: u64,
    },
}
#[derive(Debug, Serialize)]
pub struct Outgoing {
    pub to: EntityId,
    pub envelope: SignedBytes,
}
#[derive(Debug, Serialize)]
pub struct Response {
    pub entity: EntityId,
    pub role: Role,
    pub term: u64,
    pub commit_index: usize,
    pub resources: Option<osr_interlocking::resource_log::ResourceLedger>,
    pub packets: Vec<Outgoing>,
    pub proposed: usize,
    pub rejected: usize,
    pub station_observation: Option<osr_ato::station::StationInputs>,
    pub charging_enable: bool,
}
#[derive(Debug)]
pub struct Host {
    channel: Channel,
    node: RaftNode,
    journal: DiskJournal,
    state: DerivedState,
    applied: usize,
    verifier: ProposalVerifier,
    ingress: ProposalVerifier,
    ingress_seen: usize,
}
impl Host {
    pub fn new(channel: Channel, path: &Path, now: u64) -> io::Result<Self> {
        let cfg = raft_config(&channel.frozen, channel.entity)?;
        let (journal, node) = DiskJournal::open(path, cfg, channel.frozen.configuration(), now)?;
        let mut verifier =
            ProposalVerifier::with_windows(registry(&channel.frozen)?, INPUT_MAX_AGE_NS, 0);
        let mut state = DerivedState::default();
        for entry in &node.log[..node.commit_index.0 as usize] {
            apply_entry(&channel, &mut verifier, &mut state, entry)?;
        }
        let mut ingress =
            ProposalVerifier::with_windows(registry(&channel.frozen)?, INPUT_MAX_AGE_NS, 0);
        for entry in &node.log {
            let _ = ingress.verify_committed_entry(entry);
        }
        let ingress_seen = node.log.len();
        let applied = node.commit_index.0 as usize;
        Ok(Self {
            channel,
            node,
            journal,
            state,
            applied,
            verifier,
            ingress,
            ingress_seen,
        })
    }
    pub fn handle(&mut self, command: Command) -> io::Result<Response> {
        let mut station_observation = None;
        let mut charging_enable = false;
        let mut packets = Vec::new();
        let mut proposed = 0;
        let mut rejected = 0;
        let now = match &command {
            Command::Tick { now }
            | Command::Receive { now, .. }
            | Command::Publish { now, .. }
            | Command::Observe { now, .. }
            | Command::Compact { now }
            | Command::StationIo { now, .. } => *now,
        };
        if now == 0 {
            return Err(bad("time"));
        }
        let mut actions = Vec::new();
        match command {
            Command::Tick { .. } => {
                if !self
                    .channel
                    .frozen
                    .model()
                    .runtime
                    .voters
                    .contains(&self.channel.entity)
                {
                    return Err(bad("I/O has no voting authority"));
                }
                actions = step(&mut self.node, Event::Tick, now);
            }
            Command::Receive { envelope, .. } => {
                let packet = self.channel.receive(&envelope, now, &mut self.journal)?;
                match packet.kind {
                    RuntimeKind::Raft => {
                        let rpc: Message = postcard::from_bytes(&packet.bytes).map_err(bad)?;
                        if rpc.from().0 as u64 != envelope.issuer.0
                            || rpc.to() != self.node.config.me
                        {
                            return Err(bad("Raft sender/addressee"));
                        }
                        actions = step(&mut self.node, Event::Recv(rpc), now);
                    }
                    RuntimeKind::Proposal => {
                        let signed: SignedBytes =
                            postcard::from_bytes(&packet.bytes).map_err(bad)?;
                        if signed.issuer != envelope.issuer {
                            return Err(bad("nested issuer mismatch"));
                        }
                        // Reconstruct ingress replay protection from the durable entire
                        // log, including uncommitted proposals, before accepting another.
                        let proposal = self
                            .ingress
                            .verify_ingress(&signed, now)
                            .map_err(|e| bad(format!("proposal: {e:?}")))?;
                        if proposal.category() != Category::Safety {
                            return Err(bad("runtime load-bearing event cannot be Advisory"));
                        }
                        let entry: Entry =
                            serde_json::from_slice(proposal.entry_bytes()).map_err(bad)?;
                        if entry.entry_id != proposal.entry_id()
                            || entry.timestamp_ns != proposal.timestamp_ns()
                        {
                            return Err(bad("proposal metadata mismatch"));
                        }
                        self.channel.validate_entry(proposal.issuer(), &entry)?;
                        if self.node.log.len() >= MAX_LOG_ENTRIES {
                            return Err(bad(
                                "log capacity: stop, retain occupancy and plan offline servicing",
                            ));
                        }
                        actions = step(
                            &mut self.node,
                            Event::Propose {
                                value: serde_json::to_vec(&signed).map_err(bad)?,
                                category: Category::Safety,
                            },
                            now,
                        );
                        proposed = 1;
                    }
                    _ => return Err(bad("message kind not accepted by voter")),
                }
            }
            Command::Publish { payloads, .. } => {
                if payloads.len() > 16 {
                    return Err(bad("publication rate/batch bound"));
                }
                for payload in payloads {
                    let signed = self
                        .channel
                        .proposal(payload.clone(), now, &mut self.journal)?;
                    let fake = Entry {
                        entry_id: EntryId(1),
                        term: 0,
                        timestamp_ns: now,
                        payload,
                    };
                    self.channel.validate_entry(self.channel.entity, &fake)?;
                    // The transport/harness chooses a leader; this does not wait for
                    // consensus and does not claim that publication committed.
                    packets.push(Outgoing {
                        to: EntityId(0),
                        envelope: signed,
                    });
                    proposed += 1;
                }
            }
            Command::Observe { from_index, .. } => {
                if self.node.role != Role::Leader {
                    return Err(bad("only current leader publishes committed-prefix views"));
                }
                let committed = self.node.commit_index.0 as usize;
                if from_index > committed {
                    return Err(bad("prefix request beyond commit"));
                }
                // Bounded suffix; clients maintain and verify prefix continuity.
                let end = (from_index + 12).min(committed);
                let prefix = Prefix {
                    from_index,
                    commit_index: end,
                    entries: self.node.log[from_index..end].to_vec(),
                };
                let envelope = self.channel.sign(
                    RuntimeKind::CommittedPrefix,
                    &prefix,
                    now,
                    &mut self.journal,
                )?;
                packets.push(Outgoing {
                    to: EntityId(0),
                    envelope,
                });
            }
            Command::StationIo {
                platform,
                phase,
                charge_requested,
                inputs,
                ..
            } => {
                let p = self
                    .channel
                    .frozen
                    .model()
                    .runtime
                    .participants
                    .iter()
                    .find(|p| p.entity == self.channel.entity)
                    .ok_or_else(|| bad("local identity"))?;
                if p.role != ParticipantRole::Infrastructure
                    || !p.resources.contains(&platform)
                    || !self
                        .channel
                        .frozen
                        .model()
                        .resources
                        .iter()
                        .any(|r| r.id == platform && r.kind == "platform")
                {
                    return Err(bad(
                        "station sensor/output port outside assigned physical assets",
                    ));
                }
                // A local equipment interlock can inhibit charge. It grants no
                // movement permission; the train independently checks departure.
                charging_enable = charge_requested
                    && osr_ato::station::station_step(phase, inputs).charging_enable;
                station_observation = Some(inputs);
            }
            Command::Compact { .. } => self
                .journal
                .compact(&self.node)
                .map_err(|e| io::Error::new(io::ErrorKind::BrokenPipe, e))?,
        }
        for action in actions {
            match action {
                Action::Send(message) => {
                    let envelope =
                        self.channel
                            .sign(RuntimeKind::Raft, &message, now, &mut self.journal)?;
                    packets.push(Outgoing {
                        to: EntityId(message.to().0 as u64),
                        envelope,
                    });
                }
                Action::ProposeRejected { .. } => rejected += 1,
                _ => {}
            }
        }
        // A write failure ends the process before ANY outbound effect is returned.
        // The binary never continues serving with partially mutated unpersisted state.
        self.journal
            .persist(&self.node)
            .map_err(|e| io::Error::new(io::ErrorKind::BrokenPipe, e))?;
        self.ingress_seen = self.ingress_seen.min(self.node.log.len());
        for entry in &self.node.log[self.ingress_seen..] {
            let _ = self.ingress.verify_committed_entry(entry);
        }
        self.ingress_seen = self.node.log.len();
        let committed = self.node.commit_index.0 as usize;
        for entry in &self.node.log[self.applied..committed] {
            apply_entry(&self.channel, &mut self.verifier, &mut self.state, entry)
                .map_err(|e| io::Error::new(io::ErrorKind::BrokenPipe, e))?;
        }
        self.applied = committed;
        Ok(Response {
            entity: self.channel.entity,
            role: self.node.role,
            term: self.node.current_term.0,
            commit_index: committed,
            resources: self.state.resources.clone(),
            packets,
            proposed,
            rejected,
            station_observation,
            charging_enable,
        })
    }
}
