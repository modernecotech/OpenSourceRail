use osr_onboard_routing::{select_route, RouteCandidate, RouteSource, RoutingInputs, RoutingMode};
use proptest::prelude::*;

fn row(
    source: RouteSource,
    route_id: u32,
    section: u64,
    epoch: u64,
    valid_until_ns: u64,
) -> RouteCandidate {
    RouteCandidate {
        route_id,
        next_section_id: section,
        plan_epoch: epoch,
        valid_until_ns,
        source,
        trusted: true,
    }
}

proptest! {
    #[test]
    fn no_single_source_can_select_a_route(route in any::<u32>(), section in any::<u64>()) {
        let out = select_route(&RoutingInputs { now_ns: 10, network_available: false,
            onboard_plan: Some(row(RouteSource::OnboardPlan, route, section, 1, 20)),
            sensor_derived: None, network_command: None });
        prop_assert_eq!(out.mode, RoutingMode::Hold);
    }

    #[test]
    fn accepted_route_always_retains_ma_boundary(route in any::<u32>(), section in any::<u64>(), network in any::<bool>()) {
        let out = select_route(&RoutingInputs { now_ns: 10, network_available: network,
            onboard_plan: Some(row(RouteSource::OnboardPlan, route, section, 1, 20)),
            sensor_derived: Some(row(RouteSource::SensorDerived, route, section, 1, 20)),
            network_command: network.then(|| row(RouteSource::NetworkCommand, route, section, 1, 20)) });
        prop_assert_ne!(out.mode, RoutingMode::Hold);
        prop_assert!(out.movement_authority_required);
    }
}
