//! Stationary, offline handshake. A dispatch pulse ends the fixture at standstill.
use super::{evaluate_frame, BrakeCommand, DoorAction, DoorSide, DoorState, Frame, Trace};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Phase {
    Secured,
    Berthed,
    Boarding,
    Closing,
    LockSeen,
    Ready,
    HandedOver,
    Tripped,
}

#[derive(Clone, Copy)]
enum Request {
    Berth,
    Open,
    Observe,
    Close,
    VerifyLocks,
    Dispatch,
    Reset,
}

// Bound to a single synthetic train visit, independent of the physical design hash.
#[derive(Clone, Copy, PartialEq, Eq)]
struct Visit {
    station: u16,
    train: u16,
    arrival: u32,
    side: DoorSide,
}

#[derive(Clone, Copy)]
struct Event {
    visit: Visit,
    sequence: u64,
    sent_ms: u64,
    request: Request,
    local_reset_key: bool,
}

#[derive(Debug)]
struct Output {
    phase: Phase,
    observation: Trace,
    brake_request: BrakeCommand,
    retain_parking_hold: bool,
    dispatch_pulse: bool,
}

struct Supervisor {
    visit: Visit,
    configuration: [u8; 32],
    doors: Vec<DoorState>,
    openings_per_side: usize,
    phase: Phase,
    latched_brake: BrakeCommand,
    recovery_seen: bool,
    sequence: u64,
    last_clock_ms: Option<u64>,
}

const BENCH_TIMEOUT_MS: u64 = 250;

impl Supervisor {
    fn new(visit: Visit, configuration: [u8; 32], cars: usize, openings_per_side: usize) -> Self {
        Self {
            visit,
            configuration,
            doors: vec![DoorState::default(); cars * 2 * openings_per_side],
            openings_per_side,
            phase: Phase::Tripped,
            latched_brake: BrakeCommand::Emergency,
            recovery_seen: false,
            sequence: 0,
            last_clock_ms: None,
        }
    }

    fn trip(&mut self, demand: BrakeCommand) {
        self.phase = Phase::Tripped;
        self.recovery_seen = false;
        self.latched_brake = match (self.latched_brake, demand) {
            (BrakeCommand::Emergency, _) | (_, BrakeCommand::Emergency) => BrakeCommand::Emergency,
            (BrakeCommand::Service(a), BrakeCommand::Service(b)) => BrakeCommand::Service(a.max(b)),
            (BrakeCommand::Release, b) => b,
            (a, BrakeCommand::Release) => a,
        };
    }

    // Called by a local clock even if no station event arrives. No event can
    // produce a dispatch pulse here. Equipment release has a separate owner.
    fn watch_silence(&mut self, now_ms: u64) {
        if let Some(last) = self.last_clock_ms {
            if now_ms
                .checked_sub(last)
                .is_none_or(|gap| gap > BENCH_TIMEOUT_MS)
            {
                self.trip(BrakeCommand::Emergency);
            }
        }
    }

    fn tick(&mut self, now_ms: u64, event: Event, mut frame: Frame) -> Output {
        // The fixture supplies a monotonic clock and a 250 ms laboratory age limit.
        self.watch_silence(now_ms);
        let address_valid = event.visit == self.visit;
        let stamp_valid = now_ms
            .checked_sub(event.sent_ms)
            .is_some_and(|age| age <= BENCH_TIMEOUT_MS)
            && self.last_clock_ms.is_none_or(|last| now_ms > last);
        let sequence_valid = self.sequence.checked_add(1) == Some(event.sequence);
        // Consume addresses on the correct visit only. A gap trips the model.
        // Recovery requires a fresh local reset beyond the consumed sequence.
        if address_valid && stamp_valid {
            self.sequence = self.sequence.max(event.sequence);
        }
        self.last_clock_ms = Some(self.last_clock_ms.unwrap_or(0).max(now_ms));
        let visit_valid = address_valid && stamp_valid && sequence_valid;
        let berth_held = frame.station_verified
            && frame.platform == Some(self.visit.side)
            && frame.identity_matches
            && frame.parking_proved
            && frame.speed_mmps == 0;
        let common_healthy = berth_held
            && frame.missing.is_none()
            && frame.authority_valid
            && frame.service_supply
            && !frame.section_isolated;

        // Decide the input to the door crates before any motor request is issued.
        // Local fault clearing is external to this model. It cannot command a door.
        let valid_step = matches!(
            (self.phase, event.request),
            (Phase::Secured, Request::Berth)
                | (Phase::Berthed, Request::Open | Request::Close)
                | (Phase::Boarding, Request::Observe | Request::Close)
                | (Phase::Closing | Phase::LockSeen, Request::VerifyLocks)
                | (Phase::Ready, Request::Dispatch)
                | (Phase::Tripped, Request::Observe | Request::Reset)
        );
        let accepted = visit_valid && common_healthy && valid_step;
        frame.command = match (accepted, event.request, frame.brake_demand) {
            (true, Request::Open, BrakeCommand::Release)
                if frame.open_side.is_none() && frame.unlocked.is_none() =>
            {
                DoorAction::Open
            }
            (true, Request::Close, BrakeCommand::Release) => DoorAction::Close,
            _ => DoorAction::Hold,
        };
        let (observation, all_locked) = evaluate_frame(
            frame,
            self.configuration,
            &mut self.doors,
            self.openings_per_side,
            now_ms.saturating_mul(1_000_000),
        );

        if !accepted {
            self.trip(BrakeCommand::Emergency);
        } else if observation.brake != BrakeCommand::Release {
            self.trip(observation.brake);
        } else {
            match (self.phase, event.request) {
                (Phase::Secured, Request::Berth) => self.phase = Phase::Berthed,
                (Phase::Berthed, Request::Open) => self.phase = Phase::Boarding,
                (Phase::Berthed | Phase::Boarding, Request::Close) => self.phase = Phase::Closing,
                (Phase::Closing, Request::VerifyLocks) if all_locked => {
                    self.phase = Phase::LockSeen
                }
                (Phase::LockSeen, Request::VerifyLocks) if all_locked => self.phase = Phase::Ready,
                (Phase::Ready, Request::Dispatch) if observation.traction_enable => {
                    self.phase = Phase::HandedOver
                }
                (Phase::Tripped, Request::Reset)
                    if self.recovery_seen
                        && event.local_reset_key
                        && all_locked
                        && observation.traction_enable =>
                {
                    self.phase = Phase::Secured;
                    self.latched_brake = BrakeCommand::Release;
                }
                (Phase::Tripped, Request::Observe) => {
                    self.recovery_seen = all_locked && observation.traction_enable;
                }
                (_, Request::Observe) | (Phase::Tripped, Request::Reset) => (),
                _ => self.trip(BrakeCommand::Emergency),
            }
        }
        let dispatch_pulse = self.phase == Phase::HandedOver && observation.traction_enable;
        Output {
            phase: self.phase,
            brake_request: if self.phase == Phase::Tripped {
                self.latched_brake
            } else {
                observation.brake
            },
            retain_parking_hold: !dispatch_pulse,
            dispatch_pulse,
            observation,
        }
    }
}

struct Bench {
    supervisor: Supervisor,
    clock: u64,
}

impl Bench {
    fn event(&self, request: Request) -> Event {
        Event {
            visit: self.supervisor.visit,
            sequence: self.supervisor.sequence + 1,
            sent_ms: self.clock + 10,
            request,
            local_reset_key: false,
        }
    }

    fn send(&mut self, event: Event, frame: Frame) -> Output {
        self.clock += 10;
        let out = self.supervisor.tick(self.clock, event, frame);
        assert_eq!(out.retain_parking_hold, !out.dispatch_pulse);
        if out.brake_request != BrakeCommand::Release || out.phase == Phase::Tripped {
            assert!(!out.dispatch_pulse);
        }
        out
    }

    fn step(&mut self, request: Request, frame: Frame) -> Output {
        self.send(self.event(request), frame)
    }
}

pub(super) fn replay(configuration: [u8; 32], cars: usize, openings: usize) {
    use BrakeCommand::{Emergency, Service};
    use Request::*;
    let visit = Visit {
        station: 17,
        train: 3,
        arrival: 9,
        side: DoorSide::Left,
    };
    let healthy = Frame::default();
    let bench = || {
        let mut b = Bench {
            supervisor: Supervisor::new(visit, configuration, cars, openings),
            clock: 500,
        };
        // Restart cannot turn a previous trip into a dispatchable train.
        assert_eq!(b.step(Berth, healthy).phase, Phase::Tripped);
        assert_eq!(b.step(Observe, healthy).brake_request, Emergency);
        let keyed = Event {
            local_reset_key: true,
            ..b.event(Reset)
        };
        assert_eq!(b.send(keyed, healthy).phase, Phase::Secured);
        b
    };
    let open = Frame {
        open_side: Some(visit.side),
        ..healthy
    };
    let mut b = bench();
    assert_eq!(b.step(Berth, healthy).phase, Phase::Berthed);
    let opened = b.step(Open, healthy);
    assert_eq!(
        (
            opened.observation.opening_left,
            opened.observation.opening_right
        ),
        (24, 0)
    );
    assert!(opened.retain_parking_hold);
    // Real feedback now shows all 24 platform-side doors physically open.
    let trip = b.step(Observe, open);
    assert_eq!(
        (trip.phase, trip.observation.brake, trip.brake_request),
        (Phase::Tripped, Emergency, Emergency)
    );
    assert_eq!(b.step(Reset, open).phase, Phase::Tripped);
    // Local recovery supplies independently closed/locked feedback. Clearing
    // the initiating fault or an unauthorised reset must not release the train.
    let premature = Event {
        local_reset_key: true,
        ..b.event(Reset)
    };
    assert_eq!(b.send(premature, healthy).phase, Phase::Tripped);
    assert_eq!(b.step(Observe, healthy).brake_request, Emergency);
    assert_eq!(b.step(Reset, healthy).phase, Phase::Tripped);
    let reset = Event {
        local_reset_key: true,
        ..b.event(Reset)
    };
    let cleared = b.send(reset, healthy);
    assert_eq!(cleared.phase, Phase::Secured);
    assert!(!cleared.dispatch_pulse);
    assert_eq!(b.step(Berth, healthy).phase, Phase::Berthed);
    assert_eq!(b.step(Close, healthy).phase, Phase::Closing);
    assert_eq!(b.step(VerifyLocks, healthy).phase, Phase::LockSeen);
    assert_eq!(b.step(VerifyLocks, healthy).phase, Phase::Ready);
    assert!(b.step(Dispatch, healthy).dispatch_pulse);
    assert!(!b.step(Dispatch, healthy).dispatch_pulse);
    println!("boarding sequence: 24 opening feedbacks retained ATP emergency; local recovery, keyed reset, new berth, two locked frames and fresh dispatch required");

    let ready = || {
        let mut b = bench();
        for req in [Berth, Open, Close, VerifyLocks, VerifyLocks] {
            assert!(!b.step(req, healthy).dispatch_pulse);
        }
        assert_eq!(b.supervisor.phase, Phase::Ready);
        b
    };
    assert!(ready().step(Dispatch, healthy).dispatch_pulse);
    for demand in [Service(450), Emergency] {
        let mut b = ready();
        let tripped = b.step(
            Dispatch,
            Frame {
                brake_demand: demand,
                ..healthy
            },
        );
        assert_eq!(
            (tripped.phase, tripped.brake_request),
            (Phase::Tripped, demand)
        );
        assert_eq!(b.step(Observe, healthy).brake_request, demand);
        let reset = Event {
            local_reset_key: true,
            ..b.event(Reset)
        };
        assert_eq!(
            b.send(
                reset,
                Frame {
                    brake_demand: Emergency,
                    ..healthy
                }
            )
            .brake_request,
            Emergency
        );
    }
    for fault in 0..11 {
        let mut b = bench();
        b.step(Berth, healthy);
        let mut event = b.event(Open);
        let mut frame = healthy;
        match fault {
            0 => event.visit.station += 1,
            1 => event.visit.train += 1,
            2 => event.visit.arrival += 1,
            3 => event.visit.side = DoorSide::Right,
            4 => event.sequence -= 1,
            5 => event.sequence += 1,
            6 => event.sent_ms -= 251,
            7 => event.sent_ms += 1,
            8 => frame.parking_proved = false,
            9 => frame.speed_mmps = -1,
            _ => frame.unlocked = Some(0),
        }
        let rejected = b.send(event, frame);
        assert_eq!(
            (
                rejected.phase,
                rejected.observation.opening_left,
                rejected.observation.opening_right
            ),
            (Phase::Tripped, 0, 0)
        );
    }
    let mut b = bench();
    assert_eq!(b.step(Dispatch, healthy).phase, Phase::Tripped);
    let mut b = ready();
    assert_eq!(
        b.step(
            Dispatch,
            Frame {
                missing: Some(47),
                ..healthy
            }
        )
        .phase,
        Phase::Tripped
    );
    let mut b = ready();
    b.supervisor.watch_silence(b.clock + BENCH_TIMEOUT_MS);
    assert_eq!(b.supervisor.phase, Phase::Ready);
    b.supervisor.watch_silence(b.clock + BENCH_TIMEOUT_MS + 1);
    assert_eq!(b.supervisor.phase, Phase::Tripped);
    println!("dispatch sequence: closed-door cancellation permitted once; independent service/emergency, eleven event/berth faults, early dispatch, silent controller and station watchdog held");
}
