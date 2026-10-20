#[path = "../examples/support/mod.rs"]
mod support;
use osr_maglev_control::array::*;
use osr_maglev_control::ideal::{interface_power_w, IdealPlant};
use osr_maglev_control::io::{host_tick, ReplayIo};

fn near(a: f64, b: f64, tolerance: f64) {
    assert!((a - b).abs() <= tolerance, "{a} != {b}");
}
fn allocate_demand(w: Wrench) -> Allocation {
    allocate(
        &illustrative_geometry(),
        &[Availability::Available; MODULES],
        w,
        None,
        0.001,
        0.01,
        0.01,
    )
}
#[test]
fn geometry_and_equilibrium_are_independently_checkable() {
    let p = support::params();
    let w = Wrench {
        force_n: [0.0, 0.0, p.mass_kg * p.gravity_m_s2],
        moment_nm: [0.0; 3],
    };
    let a = allocate_demand(w);
    assert!(a.valid && a.within_tolerance);
    for (i, f) in a.forces.iter().enumerate() {
        near(p.stations[i].position_m[0], -5.5 + (i / 2) as f64, 1e-12);
        near(p.stations[i].position_m[1].abs(), 0.88, 1e-12);
        near(f.upward_n, 27_750.0 * 9.81 / 24.0, 1e-7);
        near(f.leftward_n, 0.0, 1e-7);
    }
    near(a.forces.iter().map(|v| v.upward_n).sum(), 272_227.5, 1e-7);
    for m in a.achieved.moment_nm {
        near(m, 0.0, 1e-7);
    }
}
#[test]
fn independent_cross_product_and_interface_power_agree() {
    let geometry = illustrative_geometry();
    let forces = core::array::from_fn(|i| Forces {
        upward_n: 1000.0 + 37.0 * i as f64,
        leftward_n: -120.0 + 11.0 * i as f64,
    });
    let w = resultant(&geometry, &forces);
    let mut independent = [0.0; 6];
    for (s, f) in geometry.iter().zip(forces) {
        let [x, y, z] = s.position_m;
        independent[1] += f.leftward_n;
        independent[2] += f.upward_n;
        independent[3] += y * f.upward_n - z * f.leftward_n;
        independent[4] += -x * f.upward_n;
        independent[5] += x * f.leftward_n;
    }
    assert_eq!(w.force_n, independent[..3]);
    assert_eq!(w.moment_nm, independent[3..]);
    let v = [0.2, 0.01, -0.02, 0.3, 0.04];
    let expected = -w.force_n[2] * v[0]
        + w.moment_nm[0] * v[1]
        + w.moment_nm[1] * v[2]
        + w.force_n[1] * v[3]
        + w.moment_nm[2] * v[4];
    near(interface_power_w(&geometry, &forces, v), expected, 1e-8);
    // A single left/front attachment checks roll/pitch/yaw signs explicitly.
    let mut forces = [Forces::default(); MODULES];
    forces[23] = Forces {
        upward_n: 100.0,
        leftward_n: 10.0,
    };
    let w = resultant(&geometry, &forces);
    assert_eq!(w.force_n, [0.0, 10.0, 100.0]);
    assert_eq!(w.moment_nm, [88.0, -550.0, 55.0]);
}
#[test]
fn five_axis_demand_and_known_failed_station_are_redistributed() {
    let w = Wrench {
        force_n: [0.0, 1000.0, 270_000.0],
        moment_nm: [5000.0, -7000.0, 3000.0],
    };
    let a = allocate_demand(w);
    assert!(a.within_tolerance);
    let mut failed = [Availability::Available; MODULES];
    failed[0] = Availability::Failed {
        residual: Forces {
            upward_n: 500.0,
            leftward_n: -40.0,
        },
    };
    let b = allocate(&illustrative_geometry(), &failed, w, None, 0.001, 0.1, 0.1);
    assert!(b.valid && b.within_tolerance);
    assert_eq!(
        b.forces[0],
        Forces {
            upward_n: 500.0,
            leftward_n: -40.0
        }
    );
    assert!(b.forces[1..]
        .iter()
        .all(|v| v.upward_n >= 0.0 && v.upward_n <= 20_000.0 && v.leftward_n.abs() <= 4000.0));
}
#[test]
fn unavailable_axes_capacity_and_slew_are_visible_in_residuals() {
    let w = Wrench {
        force_n: [1.0, 0.0, 1e6],
        moment_nm: [0.0; 3],
    };
    let a = allocate_demand(w);
    assert!(a.valid && !a.within_tolerance && a.at_limit);
    near(a.residual.force_n[0], 1.0, 0.0);
    near(a.achieved.force_n[2], 480_000.0, 1e-6);
    let old = [Forces {
        upward_n: 100.0,
        leftward_n: 0.0,
    }; MODULES];
    let w = Wrench {
        force_n: [0.0, 0.0, 270_000.0],
        moment_nm: [0.0; 3],
    };
    let a = allocate(
        &illustrative_geometry(),
        &[Availability::Available; MODULES],
        w,
        Some(&old),
        0.001,
        0.1,
        0.1,
    );
    assert!(a.valid && !a.within_tolerance);
    assert!(a.forces.iter().all(|f| f.upward_n <= 2100.0));
}
#[test]
fn all_failed_cannot_claim_support_balance() {
    let failures = [Availability::Failed {
        residual: Forces::default(),
    }; MODULES];
    let a = allocate(
        &illustrative_geometry(),
        &failures,
        Wrench {
            force_n: [0.0, 0.0, 270_000.0],
            moment_nm: [0.0; 3],
        },
        None,
        0.001,
        0.1,
        0.1,
    );
    assert!(a.valid && !a.within_tolerance);
    assert_eq!(a.achieved, Wrench::default());
}
#[test]
fn invalid_numbers_and_degenerate_sensing_do_not_escape() {
    let mut p = support::params();
    p.stations[0].maximum_upward_n = f64::NAN;
    assert!(
        !evaluate_array(ArrayState::default(), &support::frame(1), 1_000_000, &p)
            .physical_output_authorised
    );
    assert_eq!(
        evaluate_array(ArrayState::default(), &support::frame(1), 1_000_000, &p)
            .state
            .latched_fault,
        Some(ArrayFault::Parameters)
    );
    p = support::params();
    for s in &mut p.stations {
        s.position_m = [0.0; 3];
    }
    let o = evaluate_array(ArrayState::default(), &support::frame(1), 1_000_000, &p);
    assert_eq!(o.state.latched_fault, Some(ArrayFault::Geometry));
    assert_eq!(o.support, ArraySupport::LocalFallbackRequired);
    let mut f = support::frame(1);
    f.samples[4].gap_m[1] = f64::NAN;
    assert_eq!(
        evaluate_array(ArrayState::default(), &f, f.issued_ns, &support::params()).support,
        ArraySupport::LocalFallbackRequired
    );
}
#[test]
fn rigid_modes_and_feedback_polarities_match_coordinates() {
    let p = support::params();
    let plant = IdealPlant {
        modes: [0.0001, 0.00002, -0.00003, 0.0002, -0.00001],
        velocity: [0.0; 5],
        mass_kg: p.mass_kg,
        inertia_kg_m2: [20_000.0, 600_000.0, 600_000.0],
        gravity_m_s2: p.gravity_m_s2,
    };
    let mut f = support::frame(1);
    plant.observe(&mut f, &p.stations, p.target_gap_m);
    let o = evaluate_array(ArrayState::default(), &f, f.issued_ns, &p);
    for (a, b) in o.modes.unwrap().into_iter().zip(plant.modes) {
        near(a, b, 1e-12);
    }
    assert!(o.requested.force_n[2] > p.mass_kg * p.gravity_m_s2);
    assert!(o.requested.force_n[1] < 0.0);
    assert!(
        o.requested.moment_nm[0] < 0.0
            && o.requested.moment_nm[1] > 0.0
            && o.requested.moment_nm[2] > 0.0
    );
}
#[test]
fn stop_and_station_failure_keep_fresh_support_but_latch_traction() {
    let p = support::params();
    let mut f = support::frame(1);
    f.stop_requested = true;
    let o = evaluate_array(ArrayState::default(), &f, f.issued_ns, &p);
    assert_eq!(o.support, ArraySupport::StudyForces);
    assert!(o.controlled_stop_required);
    assert!(!o.traction_permitted_in_study);
    let mut f = support::frame(2);
    f.availability[0] = Availability::Failed {
        residual: Forces::default(),
    };
    let o = evaluate_array(o.state, &f, f.issued_ns, &p);
    assert_eq!(o.support, ArraySupport::StudyForces);
    assert_eq!(o.state.latched_fault, Some(ArrayFault::Actuator));
    assert!(o.allocation.unwrap().within_tolerance);
    let mut f = support::frame(3);
    f.reset_requested = true;
    let o = evaluate_array(o.state, &f, f.issued_ns, &p);
    assert!(o.state.stop_latched);
    // Restore force gradually within the stated slew envelope before reset.
    let mut state = o.state;
    for sequence in 4..=20 {
        let mut f = support::frame(sequence);
        f.reset_requested = true;
        f.stopped = true;
        f.secured = true;
        let next = evaluate_array(state, &f, f.issued_ns, &p);
        assert_eq!(next.support, ArraySupport::Secured);
        state = next.state;
    }
    assert!(!state.stop_latched);
    assert_eq!(state.latched_fault, None);
}
#[test]
fn stale_replayed_and_future_frames_require_fallback_without_poisoning_samples() {
    let p = support::params();
    let f = support::frame(1);
    let first = evaluate_array(ArrayState::default(), &f, f.issued_ns, &p);
    for (state, frame, now, fault) in [
        (
            ArrayState::default(),
            f,
            f.issued_ns + 500_001,
            ArrayFault::Deadline,
        ),
        (
            ArrayState::default(),
            f,
            f.issued_ns - 1,
            ArrayFault::ClockOrReplay,
        ),
        (first.state, f, f.issued_ns + 1, ArrayFault::ClockOrReplay),
        (
            first.state,
            support::frame(4),
            4_000_000,
            ArrayFault::Deadline,
        ),
    ] {
        let o = evaluate_array(state, &frame, now, &p);
        assert_eq!(o.support, ArraySupport::LocalFallbackRequired);
        assert_eq!(o.state.latched_fault, Some(fault));
        assert!(!o.physical_output_authorised);
    }
    let mut f = support::frame(2);
    f.support_power_available = false;
    let o = evaluate_array(first.state, &f, f.issued_ns, &p);
    assert_eq!(o.support, ArraySupport::LocalFallbackRequired);
    let f = support::frame(3);
    let o = evaluate_array(o.state, &f, f.issued_ns, &p);
    assert_eq!(o.support, ArraySupport::StudyForces);
    assert!(!o.traction_permitted_in_study);
}
#[test]
fn averaging_cannot_hide_contact_and_host_stub_cannot_authorise_output() {
    let p = support::params();
    let mut f = support::frame(1);
    f.samples[0].gap_m = [0.00299, 0.00301];
    let mut io = ReplayIo {
        now_ns: f.issued_ns,
        frame: f,
        last_recorded: None,
    };
    let o = host_tick(&mut io, ArrayState::default(), &p).unwrap();
    assert_eq!(o.support, ArraySupport::LocalFallbackRequired);
    assert!(!o.physical_output_authorised);
    assert_eq!(io.last_recorded, Some(o));
}
#[test]
fn constant_wrench_conserves_work_energy_and_unforced_momentum() {
    let mut plant = IdealPlant {
        modes: [0.0; 5],
        velocity: [0.2, 0.01, -0.02, 0.3, 0.04],
        mass_kg: 27_750.0,
        inertia_kg_m2: [20_000.0, 600_000.0, 600_000.0],
        gravity_m_s2: 9.81,
    };
    let geometry = illustrative_geometry();
    let forces = core::array::from_fn(|i| Forces {
        upward_n: 11_000.0 + i as f64 * 20.0,
        leftward_n: 100.0 - i as f64,
    });
    let w = resultant(&geometry, &forces);
    let before = plant;
    let energy = plant.mechanical_energy_j();
    assert!(plant.step(w, 0.001));
    let mid = core::array::from_fn(|i| (plant.velocity[i] + before.velocity[i]) * 0.5);
    near(
        plant.mechanical_energy_j() - energy,
        interface_power_w(&geometry, &forces, mid) * 0.001,
        1e-8,
    );
    let balance = Wrench {
        force_n: [0.0, 0.0, plant.mass_kg * plant.gravity_m_s2],
        moment_nm: [0.0; 3],
    };
    let old = plant.velocity;
    assert!(plant.step(balance, 0.1));
    assert_eq!(old, plant.velocity);
}

#[test]
fn an_active_support_bound_stops_traction_even_with_zero_residual() {
    let mut p = support::params();
    for s in &mut p.stations {
        s.maximum_upward_n = p.mass_kg * p.gravity_m_s2 / 24.0;
    }
    let f = support::frame(1);
    let o = evaluate_array(ArrayState::default(), &f, f.issued_ns, &p);
    assert!(o.allocation.unwrap().within_tolerance);
    assert_eq!(o.state.latched_fault, Some(ArrayFault::Saturation));
    assert_eq!(o.support, ArraySupport::StudyForces);
    assert!(!o.traction_permitted_in_study && o.controlled_stop_required);
}

#[test]
fn corrupt_history_and_unsupported_plant_force_are_rejected() {
    let mut previous = [Forces::default(); MODULES];
    previous[0].upward_n = f64::NAN;
    let mut failed = [Availability::Available; MODULES];
    failed[0] = Availability::Failed {
        residual: Forces::default(),
    };
    let a = allocate(
        &illustrative_geometry(),
        &failed,
        Wrench::default(),
        Some(&previous),
        0.001,
        0.1,
        0.1,
    );
    assert!(!a.valid);
    let mut plant = IdealPlant {
        modes: [0.0; 5],
        velocity: [0.0; 5],
        mass_kg: 100.0,
        inertia_kg_m2: [100.0; 3],
        gravity_m_s2: 9.81,
    };
    let old = plant;
    assert!(!plant.step(
        Wrench {
            force_n: [1.0, 0.0, 0.0],
            moment_nm: [0.0; 3]
        },
        0.1
    ));
    assert_eq!(plant, old);
}

#[test]
fn train_egress_hold_reaches_all_twenty_four_support_channels() {
    use osr_maglev_control::egress::{self, Phase, State};
    let door = egress::Output {
        state: State {
            phase: Phase::FaultHold,
            ..State::default()
        },
        missing_prerequisites: 128, // assistance missing
        traction_inhibit_required_in_study: true,
        support_must_be_maintained_in_study: true,
        further_entry_permitted_in_study: false,
        physical_output_authorised: false,
    };
    let hold = egress::train_hold(&[door; 36], 36, true, false);
    let mut frame = support::frame(1);
    frame.stop_requested = hold.traction_inhibit_required_in_study;
    let result = evaluate_array(ArrayState::default(), &frame, 1_000_000, &support::params());
    assert!(!result.traction_permitted_in_study);
    assert_eq!(result.support, ArraySupport::StudyForces);
    assert_eq!(result.allocation.unwrap().forces.len(), 24);
    assert!(!result.physical_output_authorised);
    frame = support::frame(2);
    frame.stop_requested = true;
    frame.support_power_available = false;
    let lost = evaluate_array(result.state, &frame, 2_000_000, &support::params());
    assert_eq!(lost.support, ArraySupport::LocalFallbackRequired);
    assert!(!lost.traction_permitted_in_study);
    assert!(!lost.physical_output_authorised);
}
