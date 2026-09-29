//! Three-source onboard route selection for loss-of-network operation.
//!
//! This crate selects a route intent; it never grants permission to move.
//! `osr-interlocking` and `osr-atp` remain the independent movement-
//! authority and speed-envelope boundary. The three inputs are:
//!
//! 1. a signed, versioned plan stored onboard;
//! 2. a route candidate derived from onboard localisation and sensed topology;
//! 3. an authenticated command-and-control candidate received over the network.
//!
//! Two matching, fresh sources are required. With the network unavailable,
//! the stored plan and sensor-derived candidate can continue to select the
//! route. A single source, stale source, disagreement, invalid signature, or
//! epoch mismatch produces [`RoutingMode::Hold`]. This is diversity at the
//! information-source level, not a claim of hardware independence or SIL.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum RouteSource {
    OnboardPlan,
    SensorDerived,
    NetworkCommand,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RouteCandidate {
    pub route_id: u32,
    pub next_section_id: u64,
    pub plan_epoch: u64,
    pub valid_until_ns: u64,
    pub source: RouteSource,
    /// Stored plans are verified when loaded; network commands require message
    /// authentication; sensor candidates require a healthy localisation chain.
    pub trusted: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RoutingInputs {
    pub now_ns: u64,
    pub network_available: bool,
    pub onboard_plan: Option<RouteCandidate>,
    pub sensor_derived: Option<RouteCandidate>,
    pub network_command: Option<RouteCandidate>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum RoutingMode {
    TripleAgreement,
    OnboardAutonomous,
    TwoSourceAgreement,
    Hold,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct RoutingDecision {
    pub mode: RoutingMode,
    pub route_id: Option<u32>,
    pub next_section_id: Option<u64>,
    pub agreeing_sources: Vec<RouteSource>,
    /// Always true: route selection is deliberately unable to bypass train
    /// protection or create its own permission to move.
    pub movement_authority_required: bool,
    pub reason: &'static str,
}

fn usable(
    candidate: Option<RouteCandidate>,
    expected: RouteSource,
    now_ns: u64,
) -> Option<RouteCandidate> {
    candidate.filter(|row| row.source == expected && row.trusted && row.valid_until_ns >= now_ns)
}

fn same_route(a: RouteCandidate, b: RouteCandidate) -> bool {
    a.route_id == b.route_id
        && a.next_section_id == b.next_section_id
        && a.plan_epoch == b.plan_epoch
}

/// Select a route using a fail-restrictive two-out-of-three vote.
#[must_use]
pub fn select_route(inputs: &RoutingInputs) -> RoutingDecision {
    let plan = usable(inputs.onboard_plan, RouteSource::OnboardPlan, inputs.now_ns);
    let sensor = usable(
        inputs.sensor_derived,
        RouteSource::SensorDerived,
        inputs.now_ns,
    );
    let network = if inputs.network_available {
        usable(
            inputs.network_command,
            RouteSource::NetworkCommand,
            inputs.now_ns,
        )
    } else {
        None
    };

    let winner = match (plan, sensor, network) {
        (Some(a), Some(b), Some(c)) if same_route(a, b) && same_route(b, c) => Some((
            a,
            RoutingMode::TripleAgreement,
            vec![a.source, b.source, c.source],
            "all three route sources agree",
        )),
        (Some(a), Some(b), _) if same_route(a, b) => {
            let mode = if inputs.network_available {
                RoutingMode::TwoSourceAgreement
            } else {
                RoutingMode::OnboardAutonomous
            };
            Some((
                a,
                mode,
                vec![a.source, b.source],
                if inputs.network_available {
                    "stored plan and sensed topology agree"
                } else {
                    "network unavailable; stored plan and sensed topology agree"
                },
            ))
        }
        (Some(a), _, Some(c)) if same_route(a, c) => Some((
            a,
            RoutingMode::TwoSourceAgreement,
            vec![a.source, c.source],
            "stored plan and authenticated network command agree",
        )),
        (_, Some(b), Some(c)) if same_route(b, c) => Some((
            b,
            RoutingMode::TwoSourceAgreement,
            vec![b.source, c.source],
            "sensed topology and authenticated network command agree",
        )),
        _ => None,
    };

    if let Some((route, mode, agreeing_sources, reason)) = winner {
        RoutingDecision {
            mode,
            route_id: Some(route.route_id),
            next_section_id: Some(route.next_section_id),
            agreeing_sources,
            movement_authority_required: true,
            reason,
        }
    } else {
        RoutingDecision {
            mode: RoutingMode::Hold,
            route_id: None,
            next_section_id: None,
            agreeing_sources: Vec::new(),
            movement_authority_required: true,
            reason: "fewer than two fresh trusted sources agree",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn candidate(source: RouteSource) -> RouteCandidate {
        RouteCandidate {
            route_id: 7,
            next_section_id: 42,
            plan_epoch: 3,
            valid_until_ns: 100,
            source,
            trusted: true,
        }
    }

    #[test]
    fn network_loss_continues_with_plan_and_sensor_agreement() {
        let out = select_route(&RoutingInputs {
            now_ns: 50,
            network_available: false,
            onboard_plan: Some(candidate(RouteSource::OnboardPlan)),
            sensor_derived: Some(candidate(RouteSource::SensorDerived)),
            network_command: None,
        });
        assert_eq!(out.mode, RoutingMode::OnboardAutonomous);
        assert_eq!(out.next_section_id, Some(42));
        assert!(out.movement_authority_required);
    }

    #[test]
    fn one_source_or_disagreement_holds() {
        let mut sensor = candidate(RouteSource::SensorDerived);
        sensor.next_section_id = 43;
        let out = select_route(&RoutingInputs {
            now_ns: 50,
            network_available: false,
            onboard_plan: Some(candidate(RouteSource::OnboardPlan)),
            sensor_derived: Some(sensor),
            network_command: None,
        });
        assert_eq!(out.mode, RoutingMode::Hold);
        assert_eq!(out.route_id, None);
    }

    #[test]
    fn stale_or_untrusted_votes_do_not_count() {
        let mut sensor = candidate(RouteSource::SensorDerived);
        sensor.trusted = false;
        let out = select_route(&RoutingInputs {
            now_ns: 101,
            network_available: true,
            onboard_plan: Some(candidate(RouteSource::OnboardPlan)),
            sensor_derived: Some(sensor),
            network_command: Some(candidate(RouteSource::NetworkCommand)),
        });
        assert_eq!(out.mode, RoutingMode::Hold);
    }
}
