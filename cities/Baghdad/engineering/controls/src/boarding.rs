//! Offline station visit and handover to the moving protection evaluator.
use super::{
    evaluate_frame, BrakeCommand, Direction, DoorAction, DoorSide, DoorState, Frame, Protection,
    Trace,
};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Phase {
    Secured,
    Berthed,
    Boarding,
    Closing,
    LockSeen,
    Ready,
    TakingLoad,
    Starting,
    Moving,
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
    TakeLoad,
    Advance,
    Reset,
}

// Bound to a single synthetic train visit, independent of the physical design hash.
#[derive(Clone, Copy, PartialEq, Eq)]
struct Visit {
    station: u16,
    train: u16,
    arrival: u32,
    side: DoorSide,
    direction: Direction,
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
    retain_independent_hold: bool,
    dispatch_pulse: bool,
    permit_starting_effort: bool,
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
    load_requested_ms: Option<u64>,
}

const BENCH_TIMEOUT_MS: u64 = 250;
const BENCH_LOAD_TIMEOUT_MS: u64 = 500;

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
            load_requested_ms: None,
        }
    }

    fn trip(&mut self, demand: BrakeCommand) {
        self.phase = Phase::Tripped;
        self.load_requested_ms = None;
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
            && frame.hold_applied
            && frame.brake_healthy
            && frame.brake_profile_valid
            && frame.parking_proved
            && frame.speed_mmps == 0;
        let offside_locked = frame.open_side.is_none_or(|s| s == self.visit.side)
            && frame.unlocked.is_none_or(|index| {
                super::installed_side(index, self.openings_per_side) == self.visit.side
            });
        let load_timely = self.load_requested_ms.is_none_or(|start| {
            now_ms
                .checked_sub(start)
                .is_some_and(|age| age <= BENCH_LOAD_TIMEOUT_MS)
        });
        let starting = self.phase == Phase::Starting;
        let toward_departure = frame.speed_mmps.signum() == self.visit.direction.sign();
        let starting_effort_proved = frame.starting_effort_direction == Some(self.visit.direction);
        let start_proved = (frame.speed_mmps == 0 || toward_departure)
            && (toward_departure
                || (frame.station_verified && frame.platform == Some(self.visit.side)))
            && (frame.speed_mmps == 0 || (!frame.parking_proved && !frame.hold_applied))
            && starting_effort_proved
            && !frame.torque_inhibit_proved;
        let common_healthy = (if starting { start_proved } else { berth_held })
            && offside_locked
            && load_timely
            && frame
                .starting_effort_direction
                .is_none_or(|d| !frame.torque_inhibit_proved && d == self.visit.direction)
            && frame.missing.is_none()
            && frame.authority_valid
            && frame.service_supply
            && !frame.section_isolated
            && (starting || self.phase == Phase::TakingLoad || frame.torque_inhibit_proved);

        // Decide the input to the door crates before any motor request is issued.
        // Local fault clearing is external to this model. It cannot command a door.
        let valid_step = matches!(
            (self.phase, event.request),
            (Phase::Secured, Request::Berth)
                | (Phase::Berthed, Request::Open | Request::Close)
                | (Phase::Boarding, Request::Observe | Request::Close)
                | (Phase::Closing | Phase::LockSeen, Request::VerifyLocks)
                | (Phase::Ready, Request::Dispatch)
                | (Phase::TakingLoad, Request::TakeLoad)
                | (Phase::Starting, Request::Advance)
                | (Phase::Tripped, Request::Observe | Request::Reset)
        );
        let accepted = visit_valid && common_healthy && valid_step;
        frame.command = match (accepted, event.request, frame.brake_demand) {
            (true, Request::Open, BrakeCommand::Release)
                if frame.open_side.is_none() && frame.unlocked.is_none() =>
            {
                DoorAction::Open
            }
            (true, Request::Observe, BrakeCommand::Release) if self.phase == Phase::Boarding => {
                DoorAction::Open
            }
            (true, Request::Close, BrakeCommand::Release) => DoorAction::Close,
            (true, Request::VerifyLocks, BrakeCommand::Release) if self.phase == Phase::Closing => {
                DoorAction::Close
            }
            _ => DoorAction::Hold,
        };
        let protection = match (accepted, self.phase) {
            (true, Phase::Boarding | Phase::Closing) => Protection::Berth(self.visit.side),
            (true, Phase::Starting) if frame.speed_mmps == 0 => {
                Protection::Starting(self.visit.direction)
            }
            _ => Protection::Movement,
        };
        let (observation, all_locked) = evaluate_frame(
            frame,
            self.configuration,
            &mut self.doors,
            self.openings_per_side,
            now_ms.saturating_mul(1_000_000),
            protection,
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
                (Phase::Closing, Request::VerifyLocks) => (),
                (Phase::LockSeen, Request::VerifyLocks) if all_locked => self.phase = Phase::Ready,
                (Phase::Ready, Request::Dispatch) if observation.traction_enable => {
                    self.load_requested_ms = Some(now_ms);
                    self.phase = Phase::TakingLoad
                }
                (Phase::TakingLoad, Request::TakeLoad) if observation.traction_enable => {
                    if starting_effort_proved && !frame.torque_inhibit_proved {
                        self.phase = Phase::Starting;
                    }
                }
                (Phase::Starting, Request::Advance) if observation.traction_enable => {
                    if toward_departure {
                        self.phase = Phase::Moving;
                        self.load_requested_ms = None;
                    }
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
        let dispatch_pulse =
            self.phase == Phase::Starting && matches!(event.request, Request::TakeLoad);
        let held_phase = !matches!(self.phase, Phase::Starting | Phase::Moving);
        Output {
            phase: self.phase,
            brake_request: if self.phase == Phase::Tripped {
                self.latched_brake
            } else {
                observation.brake
            },
            retain_parking_hold: held_phase && frame.speed_mmps == 0,
            retain_independent_hold: held_phase && frame.speed_mmps == 0,
            dispatch_pulse,
            permit_starting_effort: matches!(self.phase, Phase::TakingLoad | Phase::Starting)
                && observation.traction_enable,
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
        assert_eq!(out.retain_parking_hold, out.retain_independent_hold);
        if out.dispatch_pulse {
            assert!(!out.retain_parking_hold && out.permit_starting_effort);
        }
        if out.permit_starting_effort && out.phase == Phase::TakingLoad {
            assert!(frame.hold_applied && frame.parking_proved && out.retain_parking_hold);
        }
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
    for direction in [Direction::Forward, Direction::Reverse] {
        replay_direction(configuration, cars, openings, direction);
    }
}

fn replay_direction(configuration: [u8; 32], cars: usize, openings: usize, direction: Direction) {
    use BrakeCommand::{Emergency, Service};
    use Request::*;
    let visit = Visit {
        station: 17,
        train: 3,
        arrival: 9,
        side: DoorSide::Left,
        direction,
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
    let ready = || {
        let mut b = bench();
        // The moving protection owns approach and the first moving sample after
        // handover. Both use the same physical identity and door-controller states.
        let approach = Frame {
            speed_mmps: 8000 * direction.sign(),
            parking_proved: false,
            hold_applied: false,
            brake_demand: Service(400),
            ..healthy
        };
        let (arriving, _) = evaluate_frame(
            approach,
            configuration,
            &mut b.supervisor.doors,
            openings,
            b.clock * 1_000_000,
            Protection::Movement,
        );
        assert_eq!(arriving.brake, Service(400));
        assert!(!arriving.traction_enable);
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
        let boarding = b.step(Observe, open);
        assert_eq!(
            (boarding.phase, boarding.brake_request),
            (Phase::Boarding, BrakeCommand::Release)
        );
        assert!(boarding.retain_parking_hold && !boarding.observation.traction_enable);
        assert_eq!(b.step(Close, open).phase, Phase::Closing);
        assert_eq!(b.step(VerifyLocks, open).phase, Phase::Closing);
        assert_eq!(b.step(VerifyLocks, healthy).phase, Phase::LockSeen);
        assert_eq!(b.step(VerifyLocks, healthy).phase, Phase::Ready);
        b
    };
    let mut b = ready();
    let takeup = b.step(Dispatch, healthy);
    assert!(takeup.permit_starting_effort && takeup.retain_parking_hold);
    assert!(b.step(TakeLoad, healthy).retain_parking_hold);
    let loaded = Frame {
        starting_effort_direction: Some(direction),
        torque_inhibit_proved: false,
        ..healthy
    };
    assert!(b.step(TakeLoad, loaded).dispatch_pulse);
    let released = Frame {
        parking_proved: false,
        hold_applied: false,
        ..loaded
    };
    assert!(
        b.step(
            Advance,
            Frame {
                parking_proved: false,
                ..loaded
            }
        )
        .permit_starting_effort
    );
    let at_zero = b.step(Advance, released);
    assert!(
        at_zero.permit_starting_effort && !at_zero.retain_parking_hold && !at_zero.dispatch_pulse
    );
    let moving = Frame {
        speed_mmps: 1500 * direction.sign(),
        ..released
    };
    assert_eq!(b.step(Advance, moving).phase, Phase::Moving);
    for (frame, brake, torque) in [
        (moving, BrakeCommand::Release, true),
        (
            Frame {
                unlocked: Some(0),
                ..moving
            },
            Emergency,
            false,
        ),
        (
            Frame {
                speed_mmps: -direction.sign(),
                open_side: Some(visit.side),
                ..moving
            },
            Emergency,
            false,
        ),
    ] {
        b.clock += 10;
        let (actual, _) = evaluate_frame(
            frame,
            configuration,
            &mut b.supervisor.doors,
            openings,
            b.clock * 1_000_000,
            Protection::Movement,
        );
        assert_eq!((actual.brake, actual.traction_enable), (brake, torque));
    }
    assert!(!b.step(TakeLoad, loaded).dispatch_pulse);
    println!("{direction:?} normal visit: approach service braking, 24 platform doors open, parking and independent hold proved, 48 locks sampled twice, starting effort confirmed before handover, moving ATP active");

    // Loss of offside protection, applied hold or any independent brake/ATP
    // proof during a legitimate opening must reach a latched fault.
    for frame in [
        Frame {
            unlocked: Some(openings),
            ..open
        },
        Frame {
            missing: Some(0),
            ..open
        },
        Frame {
            speed_mmps: -direction.sign(),
            ..open
        },
        Frame {
            parking_proved: false,
            ..open
        },
        Frame {
            hold_applied: false,
            ..open
        },
        Frame {
            torque_inhibit_proved: false,
            ..open
        },
        Frame {
            brake_healthy: false,
            ..open
        },
        Frame {
            brake_profile_valid: false,
            ..open
        },
        Frame {
            authority_valid: false,
            ..open
        },
        Frame {
            identity_matches: false,
            ..open
        },
        Frame {
            service_supply: false,
            ..open
        },
        Frame {
            brake_demand: Emergency,
            ..open
        },
        Frame {
            brake_demand: Service(450),
            ..open
        },
    ] {
        let mut b = bench();
        b.step(Berth, healthy);
        b.step(Open, healthy);
        let fault = b.step(Observe, frame);
        let demand = if frame.brake_demand == Service(450) {
            Service(450)
        } else {
            Emergency
        };
        assert_eq!((fault.phase, fault.brake_request), (Phase::Tripped, demand));
        assert_eq!(fault.retain_parking_hold, frame.speed_mmps == 0);
        let keyed = Event {
            local_reset_key: true,
            ..b.event(Reset)
        };
        assert_eq!(b.send(keyed, healthy).phase, Phase::Tripped);
        assert_eq!(b.step(Observe, healthy).brake_request, demand);
        assert_eq!(b.step(Reset, healthy).phase, Phase::Tripped);
        let keyed = Event {
            local_reset_key: true,
            ..b.event(Reset)
        };
        assert_eq!(b.send(keyed, healthy).phase, Phase::Secured);
    }
    for frame in [
        Frame {
            starting_effort_direction: Some(direction.opposite()),
            ..loaded
        },
        Frame {
            hold_applied: false,
            ..loaded
        },
        Frame {
            parking_proved: false,
            ..loaded
        },
        Frame {
            missing: Some(0),
            ..loaded
        },
        Frame {
            unlocked: Some(0),
            ..loaded
        },
        Frame {
            brake_healthy: false,
            ..loaded
        },
        Frame {
            authority_valid: false,
            ..loaded
        },
        Frame {
            speed_mmps: direction.sign(),
            ..loaded
        },
    ] {
        let mut b = ready();
        b.step(Dispatch, healthy);
        let fault = b.step(TakeLoad, frame);
        assert_eq!(
            (fault.phase, fault.brake_request),
            (Phase::Tripped, Emergency)
        );
        assert!(!fault.permit_starting_effort && !fault.dispatch_pulse);
    }
    for frame in [
        Frame {
            starting_effort_direction: Some(direction.opposite()),
            ..released
        },
        Frame {
            starting_effort_direction: None,
            ..released
        },
        Frame {
            brake_healthy: false,
            ..released
        },
        Frame {
            unlocked: Some(0),
            ..released
        },
        Frame {
            speed_mmps: -direction.sign(),
            ..released
        },
        Frame {
            speed_mmps: direction.sign(),
            parking_proved: true,
            ..released
        },
        Frame {
            speed_mmps: direction.sign(),
            hold_applied: true,
            ..released
        },
    ] {
        let mut b = ready();
        b.step(Dispatch, healthy);
        b.step(TakeLoad, loaded);
        let fault = b.step(Advance, frame);
        assert_eq!(
            (fault.phase, fault.brake_request),
            (Phase::Tripped, Emergency)
        );
        assert!(!fault.permit_starting_effort && !fault.dispatch_pulse);
    }
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
    for fault in 0..12 {
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
            10 => event.visit.direction = direction.opposite(),
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
    let mut b = ready();
    b.step(Dispatch, healthy);
    for _ in 0..BENCH_LOAD_TIMEOUT_MS / 10 {
        assert!(b.step(TakeLoad, healthy).retain_parking_hold);
    }
    assert_eq!(b.step(TakeLoad, loaded).phase, Phase::Tripped);
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
    println!("{direction:?} fault replay: wrong-side unlock, motion, brake feedback, transfer, visit, freshness and moving door faults withheld departure");
}

#[cfg(test)]
mod tests {
    #[test]
    fn station_visit_and_injected_faults() {
        super::replay([42; 32], 6, 4);
    }
}
