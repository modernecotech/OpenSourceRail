//! Deadline/latch contract for a separately executed safety-output adapter.
//! OS process isolation is reference evidence, not qualified hardware independence.
use osr_atp::BrakeCommand;
use serde::{Deserialize, Serialize};
pub const DEADLINE_NS: u64 = 100_000_000;
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Request {
    pub sequence: u64,
    pub issued_ns: u64,
    pub brake: BrakeCommand,
    pub torque_mnm: i32,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Output {
    pub brake: BrakeCommand,
    pub torque_mnm: i32,
    pub tripped: bool,
}
#[derive(Clone, Copy, Debug)]
pub struct Guard {
    request: Option<Request>,
    last_sample: u64,
    tripped: bool,
}
impl Default for Guard {
    fn default() -> Self {
        Self {
            request: None,
            last_sample: 0,
            tripped: true,
        }
    }
}
impl Guard {
    pub fn feed(
        &mut self,
        request: Request,
        now: u64,
        stopped: bool,
        source_valid: bool,
        recovery_authorised: bool,
    ) {
        let valid = source_valid
            && request.sequence > 0
            && request.issued_ns == now
            && now > 0
            && now >= self.last_sample
            && self.request.is_none_or(|old| {
                request.sequence > old.sequence && request.issued_ns > old.issued_ns
            })
            && request.torque_mnm >= 0
            && !(request.brake != BrakeCommand::Release && request.torque_mnm > 0);
        if !valid {
            self.tripped = true;
            return;
        }
        self.request = Some(request);
        if stopped && recovery_authorised && request.brake != BrakeCommand::Emergency {
            self.tripped = false;
        }
    }
    pub fn sample(&mut self, now: u64, feedback_healthy: bool) -> Output {
        if !feedback_healthy
            || now < self.last_sample
            || self
                .request
                .is_none_or(|r| now < r.issued_ns || now - r.issued_ns >= DEADLINE_NS)
        {
            self.tripped = true;
        }
        self.last_sample = now;
        match self.request {
            Some(r) if !self.tripped => Output {
                brake: r.brake,
                torque_mnm: r.torque_mnm,
                tripped: false,
            },
            _ => Output {
                brake: BrakeCommand::Emergency,
                torque_mnm: 0,
                tripped: true,
            },
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn missing_frozen_replayed_or_unhealthy_outputs_trip_and_require_stopped_recovery() {
        let mut g = Guard::default();
        assert!(g.sample(1, true).tripped);
        let r = Request {
            sequence: 1,
            issued_ns: 10,
            brake: BrakeCommand::Release,
            torque_mnm: 100,
        };
        g.feed(r, 10, true, true, true);
        assert!(!g.sample(10, true).tripped);
        assert!(g.sample(10 + DEADLINE_NS, true).tripped);
        let r = Request {
            sequence: 2,
            issued_ns: 10 + DEADLINE_NS + 1,
            ..r
        };
        g.feed(r, r.issued_ns, false, true, true);
        assert!(g.sample(r.issued_ns, true).tripped);
        let r = Request {
            sequence: 3,
            issued_ns: r.issued_ns + 1,
            ..r
        };
        g.feed(r, r.issued_ns, true, true, true);
        assert!(!g.sample(r.issued_ns, true).tripped);
        g.feed(r, r.issued_ns, true, true, true);
        assert!(g.sample(r.issued_ns, true).tripped);
    }
}
