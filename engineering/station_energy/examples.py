"""Explicit synthetic sensitivity cases, not equipment performance data."""
from copy import deepcopy

SCHEMA = 'osr-station-energy-request/1'


def reference_case():
    """Reproduce the proposal's ideal 160 t / 5 m/s / 70% illustration."""
    return dict(id='illustrative-160t-5ms-70pct-200m',
        effective_mass_kg=160000.0, physical_mass_kg=160000.0,
        capture_speed_m_s=5.0, capture_deceleration_m_s2=0.8,
        capture_stroke_m=100.0, capture_profile='controlled-constant',
        forward_transfer=True, efficiency_capture=0.7, efficiency_store=1.0,
        efficiency_release=1.0, store_capacity_j=64000000.0,
        store_initial_j=0.0, store_reserve_j=0.0, standing_loss_w=0.0,
        dwell_s=30.0, launch_request_j=1400000.0, release_duration_s=10.0,
        booster_offset_m=0.0, booster_length_m=200.0, target_speed_m_s=20.0,
        resistance_n=0.0, grade_fraction=0.0, booster_efficiency=0.9,
        reset_s=10.0, headway_s=200.0, capture_force_limit_n=None,
        max_booster_acceleration_m_s2=1.2, available_booster_force_n=None,
        source_power_limit_w=None, independent_brake_deceleration_m_s2=0.8)


def request():
    """120 ordinary envelopes plus three deliberately unsuccessful controls.

    Efficiencies are hypothetical combined recovery cases, encoded in capture
    efficiency with unit store/release efficiencies. They are not attributed to
    a spring, hydraulic accumulator, flywheel or any supplier. Target speeds
    are research variables, not a required 72 km/h cruise speed.
    """
    cases = []
    for speed in (40, 50, 60, 72):
        for length in (100, 200, 300):
            no_capture = reference_case()
            no_capture.update(id=f'v{speed}-no-capture-l{length}',
                target_speed_m_s=speed / 3.6, booster_length_m=float(length),
                capture_speed_m_s=0.0, launch_request_j=0.0,
                efficiency_capture=1.0, release_duration_s=0.0)
            cases.append(no_capture)
            for capture in (2, 5, 10):
                for efficiency in (0.5, 0.7, 0.85):
                    case = reference_case()
                    case.update(id=f'v{speed}-c{capture}-e{round(100*efficiency)}-l{length}',
                        target_speed_m_s=speed / 3.6, booster_length_m=float(length),
                        capture_speed_m_s=float(capture), efficiency_capture=efficiency,
                        launch_request_j=0.5*case['effective_mass_kg']*capture**2*efficiency)
                    cases.append(case)
    wrong_direction = reference_case()
    wrong_direction.update(id='control-spring-without-forward-transfer',
        capture_profile='unpreloaded-spring', forward_transfer=False)
    uphill_offset = reference_case()
    uphill_offset.update(id='control-unreachable-uphill-offset',
        grade_fraction=0.02, booster_offset_m=200.0)
    reset = reference_case()
    reset.update(id='control-resource-conflict', reset_s=250.0)
    cases.extend((wrong_direction, uphill_offset, reset))
    return dict(schema=SCHEMA, cases=deepcopy(cases))
