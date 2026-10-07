//! Autonomous monotonic sampling, separate from blocking input and output I/O.
//! This is a process reference, not a qualified real-time or physical actuator.
use osr_brake::dual::{DualGuard, DualOutput, PairFeed};
use serde::{Deserialize, Serialize};
use std::io;
use std::sync::{
    atomic::{AtomicBool, Ordering},
    mpsc::{self, Receiver, SyncSender},
    Arc, Mutex,
};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

#[derive(Debug, Deserialize)]
#[serde(tag = "command", rename_all = "snake_case", deny_unknown_fields)]
pub enum OutputCommand {
    FeedPair {
        now: u64,
        pair: PairFeed,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
        #[serde(default)]
        clock_epoch: Option<String>,
    },
    Sample {
        now: u64,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
    },
    Clock,
}

#[derive(Clone, Debug, Serialize)]
pub struct OutputSnapshot {
    pub pair: DualOutput,
    pub now_ns: u64,
    pub clock_epoch: String,
    pub autonomous: bool,
    pub error: Option<String>,
}

pub type OutputInput = Option<Result<OutputCommand, String>>;

#[derive(Debug)]
pub struct ClockedOutput {
    pub input: SyncSender<OutputInput>,
    state: Arc<Mutex<OutputSnapshot>>,
    finished: Arc<AtomicBool>,
    sampler: JoinHandle<()>,
}

impl ClockedOutput {
    pub fn start() -> io::Result<Self> {
        let origin = Instant::now();
        let epoch = format!(
            "{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map_err(io::Error::other)?
                .as_nanos()
        );
        let mut guard = DualGuard::default();
        let state = Arc::new(Mutex::new(OutputSnapshot {
            pair: guard.sample(1, false, false),
            now_ns: 1,
            clock_epoch: epoch.clone(),
            autonomous: true,
            error: None,
        }));
        let finished = Arc::new(AtomicBool::new(false));
        let (input, receive) = mpsc::sync_channel(16);
        let sample_state = Arc::clone(&state);
        let sample_finished = Arc::clone(&finished);
        let sampler = thread::Builder::new()
            .name("safety-output-watchdog".into())
            .spawn(move || {
                sample_loop(origin, epoch, receive, sample_state, sample_finished);
            })?;
        Ok(Self {
            input,
            state,
            finished,
            sampler,
        })
    }
    pub fn snapshot(&self) -> OutputSnapshot {
        let (mut state, poisoned) = match self.state.lock() {
            Ok(state) => (state.clone(), false),
            Err(state) => (state.into_inner().clone(), true),
        };
        if poisoned || (self.sampler.is_finished() && !self.finished()) {
            state.pair = DualGuard::default().sample(state.now_ns, false, false);
            state.error = Some("watchdog sampler unavailable".into());
        }
        state
    }
    pub fn finished(&self) -> bool {
        self.finished.load(Ordering::Acquire)
    }
    pub fn join(self) -> io::Result<()> {
        self.sampler
            .join()
            .map_err(|_| io::Error::other("watchdog sampler failed"))
    }
}

fn sample_loop(
    origin: Instant,
    epoch: String,
    input: Receiver<OutputInput>,
    state: Arc<Mutex<OutputSnapshot>>,
    finished: Arc<AtomicBool>,
) {
    let mut guard = DualGuard::default();
    let mut feedback = (false, false);
    let mut error = None;
    loop {
        // A queued flood cannot postpone sampling: every received frame is
        // followed by a real-clock sample. No input frame advances this clock.
        let frame = input.recv_timeout(Duration::from_millis(5));
        let now = Instant::now()
            .checked_duration_since(origin)
            .and_then(|d| u64::try_from(d.as_nanos()).ok())
            .unwrap_or(u64::MAX);
        let mut close = false;
        match frame {
            Ok(Some(Ok(OutputCommand::FeedPair {
                now: source_now,
                pair,
                feedback_a_healthy,
                feedback_b_healthy,
                clock_epoch,
            }))) => {
                let stamps_match = [pair.a, pair.b]
                    .into_iter()
                    .flatten()
                    .all(|feed| feed.request.issued_ns == source_now);
                if clock_epoch.as_deref() != Some(epoch.as_str()) || !stamps_match {
                    feedback = (false, false);
                    error = Some("wrong clock epoch or inconsistent source timestamp".into());
                } else {
                    feedback = (feedback_a_healthy, feedback_b_healthy);
                    guard.feed_timestamped(now, pair, feedback.0, feedback.1);
                    error = None;
                }
            }
            Ok(Some(Ok(OutputCommand::Sample {
                feedback_a_healthy,
                feedback_b_healthy,
                ..
            }))) => {
                feedback = (feedback_a_healthy, feedback_b_healthy);
                error = None;
            }
            Ok(Some(Ok(OutputCommand::Clock))) => {
                error = None;
            }
            Ok(Some(Err(message))) => {
                feedback = (false, false);
                error = Some(message);
            }
            Ok(None) | Err(mpsc::RecvTimeoutError::Disconnected) => {
                feedback = (false, false);
                close = true;
            }
            Err(mpsc::RecvTimeoutError::Timeout) => {}
        }
        let snapshot = OutputSnapshot {
            pair: guard.sample(now, feedback.0, feedback.1),
            now_ns: now,
            clock_epoch: epoch.clone(),
            autonomous: true,
            error: error.clone(),
        };
        *state.lock().expect("watchdog state poisoned") = snapshot;
        if close {
            finished.store(true, Ordering::Release);
            break;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_atp::BrakeCommand;
    use osr_brake::{
        deadline::{Request, DEADLINE_NS},
        dual::ChannelFeed,
    };
    fn feed(host: &ClockedOutput, sequence: u64, stopped: bool) {
        while host.snapshot().now_ns <= 1 {
            thread::sleep(Duration::from_millis(1));
        }
        let clock = host.snapshot();
        let channel = ChannelFeed {
            source_valid: true,
            request: Request {
                sequence,
                issued_ns: clock.now_ns,
                brake: BrakeCommand::Release,
                torque_mnm: 100,
            },
        };
        host.input
            .send(Some(Ok(OutputCommand::FeedPair {
                now: clock.now_ns,
                pair: PairFeed {
                    a: Some(channel),
                    b: Some(channel),
                    stopped,
                    recovery_authorised: true,
                },
                feedback_a_healthy: true,
                feedback_b_healthy: true,
                clock_epoch: Some(clock.clock_epoch),
            })))
            .unwrap();
    }
    fn wait(host: &ClockedOutput, trip: bool) -> OutputSnapshot {
        let end = Instant::now() + Duration::from_secs(2);
        loop {
            let state = host.snapshot();
            if state.pair.output.tripped == trip {
                return state;
            }
            assert!(Instant::now() < end, "watchdog state did not change");
            thread::sleep(Duration::from_millis(1));
        }
    }
    #[test]
    fn input_and_output_inactivity_cannot_stop_sampling_or_hide_expiry() {
        let host = ClockedOutput::start().unwrap();
        feed(&host, 1, true);
        let released = wait(&host, false);
        // No reader/writer participates while the sampler continues independently.
        thread::sleep(Duration::from_millis(150));
        let expired = wait(&host, true);
        assert!(expired.now_ns - released.now_ns >= DEADLINE_NS);
        assert_eq!(expired.pair.output.torque_mnm, 0);
        assert_eq!(expired.pair.output.brake, BrakeCommand::Emergency);
        feed(&host, 2, false);
        thread::sleep(Duration::from_millis(15));
        assert!(host.snapshot().pair.output.tripped);
        feed(&host, 3, true);
        wait(&host, false);
        host.input.send(None).unwrap();
        while !host.finished() {
            thread::sleep(Duration::from_millis(1));
        }
        assert!(host.snapshot().pair.output.tripped);
        host.join().unwrap();
    }
    #[test]
    fn caller_time_and_previous_epoch_do_not_authorise_or_renew_outputs() {
        let host = ClockedOutput::start().unwrap();
        feed(&host, 1, true);
        wait(&host, false);
        for _ in 0..30 {
            host.input
                .send(Some(Ok(OutputCommand::Sample {
                    now: u64::MAX,
                    feedback_a_healthy: true,
                    feedback_b_healthy: true,
                })))
                .unwrap();
            thread::sleep(Duration::from_millis(5));
        }
        assert!(host.snapshot().pair.output.tripped);
        let clock = host.snapshot();
        let channel = ChannelFeed {
            source_valid: true,
            request: Request {
                sequence: 2,
                issued_ns: clock.now_ns,
                brake: BrakeCommand::Release,
                torque_mnm: 100,
            },
        };
        host.input
            .send(Some(Ok(OutputCommand::FeedPair {
                now: clock.now_ns,
                pair: PairFeed {
                    a: Some(channel),
                    b: Some(channel),
                    stopped: true,
                    recovery_authorised: true,
                },
                feedback_a_healthy: true,
                feedback_b_healthy: true,
                clock_epoch: Some("previous-process-epoch".into()),
            })))
            .unwrap();
        thread::sleep(Duration::from_millis(15));
        assert!(host.snapshot().pair.output.tripped);
        assert!(host.snapshot().error.is_some());
        host.input.send(None).unwrap();
        host.join().unwrap();
    }
}
