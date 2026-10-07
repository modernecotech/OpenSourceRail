//! Two logical channels: both must agree to permit; either can latch a trip.
//! Shared code/clock/comparator are common causes, not physical independence.
use crate::deadline::{Guard, Output, Request};
use osr_atp::BrakeCommand;
use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum SafetyChannel {
    A,
    B,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ChannelFeed {
    pub request: Request,
    pub source_valid: bool,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PairFeed {
    pub a: Option<ChannelFeed>,
    pub b: Option<ChannelFeed>,
    pub stopped: bool,
    pub recovery_authorised: bool,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct DualOutput {
    pub output: Output,
    pub channel_a: Output,
    pub channel_b: Output,
    pub discrepancy: bool,
}

#[derive(Clone, Copy, Debug)]
pub struct DualGuard {
    a: Guard,
    b: Guard,
    tripped: bool,
    discrepancy: bool,
}
impl Default for DualGuard {
    fn default() -> Self {
        Self {
            a: Guard::default(),
            b: Guard::default(),
            tripped: true,
            discrepancy: false,
        }
    }
}
impl DualGuard {
    pub fn feed(
        &mut self,
        now: u64,
        pair: PairFeed,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
    ) -> DualOutput {
        self.feed_at(now, pair, feedback_a_healthy, feedback_b_healthy, false)
    }
    /// Both source requests retain their timestamps in the host clock epoch.
    pub fn feed_timestamped(
        &mut self,
        now: u64,
        pair: PairFeed,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
    ) -> DualOutput {
        self.feed_at(now, pair, feedback_a_healthy, feedback_b_healthy, true)
    }
    fn feed_at(
        &mut self,
        now: u64,
        pair: PairFeed,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
        timestamped: bool,
    ) -> DualOutput {
        // Missing channels cannot be filled by copying the survivor. Pair
        // identity is bounded to this synthetic port; source-issued end-to-end
        // identity and independent clocks are still hardware integration work.
        self.discrepancy = match (pair.a, pair.b) {
            (Some(a), Some(b)) => a.request != b.request,
            _ => true,
        };
        if self.discrepancy {
            self.tripped = true;
        }
        for (guard, feed) in [(&mut self.a, pair.a), (&mut self.b, pair.b)] {
            if let Some(feed) = feed {
                if timestamped {
                    guard.feed_timestamped(
                        feed.request,
                        now,
                        pair.stopped,
                        feed.source_valid,
                        pair.recovery_authorised && !self.discrepancy,
                    );
                } else {
                    guard.feed(
                        feed.request,
                        now,
                        pair.stopped,
                        feed.source_valid,
                        pair.recovery_authorised && !self.discrepancy,
                    );
                }
            }
        }
        let result = self.sample(now, feedback_a_healthy, feedback_b_healthy);
        if pair.stopped
            && pair.recovery_authorised
            && !self.discrepancy
            && !result.channel_a.tripped
            && !result.channel_b.tripped
            && result.channel_a.brake != BrakeCommand::Emergency
            && result.channel_b.brake != BrakeCommand::Emergency
        {
            self.tripped = false;
        }
        self.sample(now, feedback_a_healthy, feedback_b_healthy)
    }
    pub fn sample(
        &mut self,
        now: u64,
        feedback_a_healthy: bool,
        feedback_b_healthy: bool,
    ) -> DualOutput {
        let a = self.a.sample(now, feedback_a_healthy);
        let b = self.b.sample(now, feedback_b_healthy);
        if a.tripped || b.tripped || a != b || a.brake == BrakeCommand::Emergency {
            self.tripped = true;
        }
        DualOutput {
            output: if self.tripped {
                Output {
                    brake: BrakeCommand::Emergency,
                    torque_mnm: 0,
                    tripped: true,
                }
            } else {
                a
            },
            channel_a: a,
            channel_b: b,
            discrepancy: self.discrepancy || a != b,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::deadline::DEADLINE_NS;
    fn pair(sequence: u64, now: u64, stopped: bool) -> PairFeed {
        let feed = ChannelFeed {
            request: Request {
                sequence,
                issued_ns: now,
                brake: BrakeCommand::Release,
                torque_mnm: 100,
            },
            source_valid: true,
        };
        PairFeed {
            a: Some(feed),
            b: Some(feed),
            stopped,
            recovery_authorised: true,
        }
    }
    #[test]
    fn both_permit_either_missing_trips_without_moving_recovery() {
        for missing in [SafetyChannel::A, SafetyChannel::B] {
            let mut g = DualGuard::default();
            assert!(!g.feed(1, pair(1, 1, true), true, true).output.tripped);
            let mut p = pair(2, 2, false);
            match missing {
                SafetyChannel::A => p.a = None,
                SafetyChannel::B => p.b = None,
            }
            assert!(g.feed(2, p, true, true).output.tripped);
            assert!(g.feed(3, pair(3, 3, false), true, true).output.tripped);
            assert!(!g.feed(4, pair(4, 4, true), true, true).output.tripped);
        }
    }
    #[test]
    fn disagreement_emergency_invalid_source_and_replay_each_trip() {
        for fault in 0..5 {
            let mut g = DualGuard::default();
            g.feed(1, pair(1, 1, true), true, true);
            let mut p = pair(2, 2, false);
            let b = p.b.as_mut().unwrap();
            match fault {
                0 => b.request.torque_mnm += 1,
                1 => {
                    b.request.brake = BrakeCommand::Emergency;
                    b.request.torque_mnm = 0;
                }
                2 => b.source_valid = false,
                3 => b.request.sequence = 1,
                _ => b.request.issued_ns = 1,
            }
            let result = g.feed(2, p, true, true);
            assert!(result.output.tripped);
            assert_eq!(result.output.brake, BrakeCommand::Emergency);
            assert_eq!(result.output.torque_mnm, 0);
        }
    }
    #[test]
    fn either_feedback_gap_or_clock_rollback_latches() {
        for fault in 0..4 {
            let mut g = DualGuard::default();
            g.feed(10, pair(1, 10, true), true, true);
            let r = match fault {
                0 => g.sample(11, false, true),
                1 => g.sample(11, true, false),
                2 => g.feed(
                    10 + DEADLINE_NS,
                    pair(2, 10 + DEADLINE_NS, false),
                    true,
                    true,
                ),
                _ => g.sample(9, true, true),
            };
            assert!(r.output.tripped);
        }
    }
}
