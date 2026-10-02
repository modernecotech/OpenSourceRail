//! Train host calls the existing interlocking/ATP/ATO/brake components.
use super::*;
use osr_ato::{ato_evaluate, station::*, AtoInputs, AtoParams, AtoState};
use osr_atp::{atp_evaluate, BrakeCommand, BrakeProfile, TrainState};
use osr_brake::{brake_evaluate, BrakeInputs, BrakeParams};
#[derive(Debug, Deserialize)]
#[serde(tag = "command", rename_all = "snake_case", deny_unknown_fields)]
pub enum Command {
    Receive {
        now: u64,
        envelope: SignedBytes,
    },
    Tick {
        now: u64,
        front_progress_mm: u64,
        speed_mmps: i32,
        uncertainty_mm: u32,
        integrity: bool,
        station: StationInputs,
        recovery_authorised: bool,
    },
}
#[derive(Debug, Serialize)]
pub struct Response {
    pub train: TrainId,
    pub commit_index: usize,
    pub authority: Option<osr_interlocking::MovementAuthority>,
    pub atp: Option<osr_atp::AtpOutcome>,
    pub brake: BrakeCommand,
    pub traction_inhibit: bool,
    pub torque_mnm: i32,
    pub recovery_required: bool,
    pub station: StationOutput,
    pub resources: Option<osr_interlocking::resource_log::ResourceLedger>,
    pub packets: Vec<SignedBytes>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
struct LocalState {
    latched: bool,
    last_now: u64,
    last_front_lower: u64,
    station: StationPhase,
    ato: AtoState,
    registered: bool,
    last_publication_ns: u64,
}
#[derive(Debug)]
pub struct Host {
    channel: Channel,
    journal: DiskJournal,
    node: RaftNode,
    derived: DerivedState,
    verifier: ProposalVerifier,
    local: LocalState,
    config: TrainConfig,
    route: RouteId,
    network: Network,
    last_entry_id: Option<EntryId>,
}
impl Host {
    pub fn new(channel: Channel, path: &Path) -> io::Result<Self> {
        let config = channel
            .frozen
            .train_config(TrainId(channel.entity.0))
            .map_err(|e| bad(format!("train configuration: {e:?}")))?;
        let route = channel
            .frozen
            .model()
            .trains
            .iter()
            .find(|t| t.config.owner == config.owner)
            .ok_or_else(|| bad("train"))?
            .permitted_route;
        let cfg = raft_config(&channel.frozen, channel.entity)?;
        let (journal, node) = DiskJournal::open(path, cfg, channel.frozen.configuration(), 1)?;
        let mut verifier =
            ProposalVerifier::with_windows(registry(&channel.frozen)?, INPUT_MAX_AGE_NS, 0);
        let mut derived = DerivedState::default();
        let mut last_entry_id = None;
        for entry in &node.log {
            last_entry_id = Some(apply_entry(&channel, &mut verifier, &mut derived, entry)?);
        }
        let mut local: LocalState = if journal.application.is_empty() {
            LocalState {
                latched: true,
                last_now: 0,
                last_front_lower: 0,
                station: StationPhase::Approach,
                ato: AtoState::default(),
                registered: false,
                last_publication_ns: 0,
            }
        } else {
            serde_json::from_slice(&journal.application).map_err(bad)?
        };
        local.latched = true; // Every cold start requires stopped, fresh, controlled recovery.
        let network = network(&channel.frozen)?;
        Ok(Self {
            channel,
            journal,
            node,
            derived,
            verifier,
            local,
            config,
            route,
            network,
            last_entry_id,
        })
    }
    pub fn handle(&mut self, command: Command) -> io::Result<Response> {
        let mut packets = Vec::new();
        let mut authority = None;
        let mut atp = None;
        let mut torque = 0;
        let mut command_brake = BrakeCommand::Emergency;
        let mut station_output = StationOutput {
            phase: self.local.station,
            charging_enable: false,
            passenger_exchange_enable: false,
            isolate_charger: true,
            departure_permitted: false,
        };
        match command {
            Command::Receive { now, envelope } => {
                let packet = self.channel.receive(&envelope, now, &mut self.journal)?;
                if packet.kind != RuntimeKind::CommittedPrefix {
                    return Err(bad("train accepts only verified committed-prefix views"));
                }
                let prefix: Prefix = postcard::from_bytes(&packet.bytes).map_err(bad)?;
                if prefix.from_index != self.node.log.len()
                    || prefix.commit_index != prefix.from_index + prefix.entries.len()
                    || prefix.commit_index > MAX_LOG_ENTRIES
                {
                    return Err(bad("committed prefix discontinuity/capacity"));
                }
                for entry in &prefix.entries {
                    self.last_entry_id = Some(
                        apply_entry(&self.channel, &mut self.verifier, &mut self.derived, entry)
                            .map_err(|e| io::Error::new(io::ErrorKind::BrokenPipe, e))?,
                    );
                }
                self.node.log.extend(prefix.entries);
                self.node.commit_index = osr_consensus::LogIndex(self.node.log.len() as u64);
                self.node.current_term = self
                    .node
                    .log
                    .last()
                    .map_or(osr_consensus::Term(0), |e| e.term);
            }
            Command::Tick {
                now,
                front_progress_mm,
                speed_mmps,
                uncertainty_mm,
                integrity,
                mut station,
                recovery_authorised,
            } => {
                if now <= self.local.last_now
                    || !(0..=100_000).contains(&speed_mmps)
                    || uncertainty_mm > self.config.maximum_position_uncertainty_mm
                    || front_progress_mm
                        < u64::from(self.config.length_mm) + u64::from(uncertainty_mm)
                    || front_progress_mm.saturating_add(u64::from(uncertainty_mm))
                        < self.local.last_front_lower
                {
                    self.local.latched = true;
                }
                self.local.last_now = now;
                self.local.last_front_lower =
                    front_progress_mm.saturating_sub(u64::from(uncertainty_mm));
                let head = track_ref(&self.channel.frozen, self.route, front_progress_mm)?;
                let tail = track_ref(
                    &self.channel.frozen,
                    self.route,
                    front_progress_mm.saturating_sub(u64::from(self.config.length_mm)),
                )?;
                let ma = osr_interlocking::compute_self_ma_from_state(
                    self.config.owner.train,
                    &self.derived,
                    &self.network,
                    now,
                    self.last_entry_id,
                );
                // Local full-footprint check supplements the same interlocking walk.
                // It never creates authority or obtains occupancy from simulation truth.
                let path = self
                    .channel
                    .frozen
                    .model()
                    .routes
                    .iter()
                    .find(|r| r.id == self.route)
                    .ok_or_else(|| bad("route"))?;
                let front = front_progress_mm.saturating_add(u64::from(uncertainty_mm));
                let rear = front_progress_mm
                    .saturating_sub(u64::from(self.config.length_mm) + u64::from(uncertainty_mm));
                let footprint_ok = integrity
                    && self.derived.resources.as_ref().is_some_and(|ledger| {
                        path.segments
                            .iter()
                            .filter(|s| s.start_mm < front && s.end_mm > rear)
                            .all(|s| {
                                ledger.permits(
                                    self.channel.frozen.model().resources
                                        [usize::from(s.resource.0)]
                                    .section,
                                    self.config.owner.train,
                                    now,
                                )
                            })
                    });
                let grade = path
                    .segments
                    .iter()
                    .map(|s| s.downhill_permille)
                    .max()
                    .unwrap_or(0);
                let decel = self
                    .config
                    .minimum_deceleration_mmps2
                    .saturating_sub((9810 * u32::from(grade)).div_ceil(1000));
                let profile = BrakeProfile::try_new(decel as i32, self.config.reaction_time_ms)
                    .ok_or_else(|| bad("braking profile"))?;
                let measured = TrainState {
                    train_id: self.config.owner.train,
                    head,
                    speed_mmps,
                    speed_uncertainty_mmps: 10,
                    position_uncertainty_mm: uncertainty_mm
                        .saturating_add(self.config.stop_margin_mm),
                };
                let protection = atp_evaluate(&measured, &ma, &profile, &self.network, now);
                let valid = footprint_ok && now < ma.valid_until_ns && ma.has_known_position;
                station.authority_valid = valid;
                station_output = station_step(self.local.station, station);
                self.local.station = station_output.phase;
                if !valid
                    || protection.is_emergency()
                    || (!physical_departure_permitted(station) && speed_mmps > 0)
                {
                    self.local.latched = true;
                }
                if recovery_authorised
                    && speed_mmps == 0
                    && integrity
                    && valid
                    && physical_departure_permitted(station)
                    && !protection.is_emergency()
                {
                    self.local.latched = false;
                }
                let destination = path
                    .stopping_locations
                    .last()
                    .ok_or_else(|| bad("destination"))?
                    .at_mm;
                // Synthetic 10 m plant tuning; actual consist calibration is a HIL gate.
                let ato_params = AtoParams {
                    ki_mnm_per_mmps_s: 0,
                    max_integral_mnm: 0,
                    kp_mnm_per_mmps: 30_000,
                    full_brake_demand_mnm: 500_000,
                    coast_band_mnm: 0,
                    station_approach_decel_mmps2: 500,
                    ..AtoParams::light_metro_default()
                };
                let automatic = ato_evaluate(
                    &self.local.ato,
                    &AtoInputs {
                        now_ns: now,
                        dt_ns: 100_000_000,
                        current_speed_mmps: speed_mmps,
                        envelope_mmps: protection.envelope_mmps.unwrap_or(0),
                        cruise_target_mmps: 8000,
                        distance_to_stop_mm: Some(
                            destination.saturating_sub(front_progress_mm + 1000) as i64,
                        ),
                        at_station: front_progress_mm >= destination.saturating_sub(2000),
                        dwell_remaining_ms: 0,
                        ato_engaged: true,
                    },
                    &ato_params,
                );
                self.local.ato = automatic.state;
                command_brake = if self.local.latched {
                    BrakeCommand::Emergency
                } else if !station_output.departure_permitted {
                    if speed_mmps == 0 {
                        BrakeCommand::Service(1000)
                    } else {
                        BrakeCommand::Emergency
                    }
                } else {
                    match protection.command {
                        BrakeCommand::Release if automatic.service_brake_ppt > 0 => {
                            BrakeCommand::Service(automatic.service_brake_ppt)
                        }
                        other => other,
                    }
                };
                let brake = brake_evaluate(
                    &BrakeInputs {
                        atp_command: command_brake,
                        fire_emergency: false,
                        derailment_emergency: false,
                        remote_assist_emergency: false,
                        obstacle_emergency: false,
                        park_requested: !station_output.departure_permitted,
                        measured_speed_mmps: speed_mmps,
                        wheel_speed_mmps: speed_mmps,
                        regen_available_ppt: 0,
                        now_ns: now,
                    },
                    &BrakeParams::light_metro_default(),
                );
                command_brake = brake.command;
                torque = if brake.traction_cut
                    || self.local.latched
                    || !station_output.departure_permitted
                {
                    0
                } else {
                    automatic.torque_setpoint_mnm.max(0)
                };
                authority = Some(ma);
                atp = Some(protection);
                if now.saturating_sub(self.local.last_publication_ns) >= 300_000_000 {
                    self.local.last_publication_ns = now;
                    if self.derived.trains.get(&self.config.owner.train).is_none() {
                        let mut consist = ConsistDescriptor::reference_3car();
                        consist.length_mm = self.config.length_mm;
                        packets.push(self.channel.proposal(
                            EntryPayload::TrainRegistration(osr_interlocking::TrainRegistration {
                                train_id: self.config.owner.train,
                                consist,
                                initial_position: Position {
                                    track_ref: head,
                                    uncertainty_mm,
                                },
                            }),
                            now,
                            &mut self.journal,
                        )?);
                        self.local.registered = true;
                    }
                    // Measured speed and non-zero bounded uncertainty, not fixed/certain publisher data.
                    packets.push(self.channel.proposal(
                        EntryPayload::TrainPositionReport(osr_interlocking::TrainPositionReport {
                            train_id: self.config.owner.train,
                            head_position: Position {
                                track_ref: head,
                                uncertainty_mm,
                            },
                            tail_position: Position {
                                track_ref: tail,
                                uncertainty_mm,
                            },
                            speed_mmps: i64::from(speed_mmps),
                            speed_uncertainty_mmps: 10,
                            heading: head.direction,
                            contributing_sources: vec![osr_interlocking::PositionSource::Odometry],
                            onboard_time_ns: now,
                            pack_soc_ppt: 800,
                        }),
                        now,
                        &mut self.journal,
                    )?);
                    packets.push(self.channel.proposal(
                        EntryPayload::ResourceControl(ResourceEvent::Integrity {
                            owner: self.config.owner,
                            proved: integrity,
                        }),
                        now,
                        &mut self.journal,
                    )?);
                    for segment in path.segments.iter().filter(|s| s.end_mm > rear) {
                        packets.push(self.channel.proposal(
                            EntryPayload::ResourceControl(ResourceEvent::Reserve {
                                owner: self.config.owner,
                                resource: segment.resource,
                                route: self.route,
                                direction: path.direction,
                            }),
                            now,
                            &mut self.journal,
                        )?);
                    }
                    if let Some(ledger) = &self.derived.resources {
                        for (index, record) in ledger.controller.records().iter().enumerate() {
                            if let Some(grant) =
                                record.grant.filter(|g| g.owner == self.config.owner)
                            {
                                if path.segments.iter().any(|s| {
                                    usize::from(s.resource.0) == index && rear > s.end_mm
                                        || (self.local.latched
                                            && speed_mmps == 0
                                            && s.start_mm > front)
                                }) {
                                    packets.push(self.channel.proposal(
                                        EntryPayload::ResourceControl(ResourceEvent::Withdraw(
                                            grant,
                                        )),
                                        now,
                                        &mut self.journal,
                                    )?);
                                }
                            }
                        }
                    }
                }
            }
        }
        self.journal.application = serde_json::to_vec(&self.local).map_err(bad)?;
        self.journal
            .persist(&self.node)
            .map_err(|e| io::Error::new(io::ErrorKind::BrokenPipe, e))?;
        Ok(Response {
            train: self.config.owner.train,
            commit_index: self.node.log.len(),
            authority,
            atp,
            brake: command_brake,
            traction_inhibit: torque == 0,
            torque_mnm: torque,
            recovery_required: self.local.latched,
            station: station_output,
            resources: self.derived.resources.clone(),
            packets,
        })
    }
}
