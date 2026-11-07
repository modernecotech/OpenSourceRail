//! Declared research method; not qualified hardware.
mod common;
use common::fixture;
#[test]
fn six_car_receiver_handles_same_hardware_on_off_and_body_mass_sensitivity_at_all_steps() {
    for dt in [0.05, 0.025, 0.0125] {
        for extra in [0., 1018., 1387.3443] {
            let mut on = fixture();
            for l in &mut on.legs {
                let old = l.journey.mass_kg;
                l.journey.mass_kg += extra;
                l.journey.rotating_equivalent_mass_kg += extra * 0.06;
                l.journey.brake_adhesion_force_cap_n *= l.journey.mass_kg / old;
                l.journey.dt_s = dt;
            }
            let mut off = on.clone();
            for l in &mut off.legs {
                l.capture_failed = true;
                l.release_failed = true;
            }
            let a = osr_journey::cycle::evaluate(&on).unwrap();
            let b = osr_journey::cycle::evaluate(&off).unwrap();
            assert_eq!(a.arrived_legs, 8, "dt{dt} extra{extra} state{}", a.state);
            assert_eq!(b.arrived_legs, 8);
            for (on, off) in a.legs.iter().zip(&b.legs) {
                let j = on.journey.as_ref().unwrap();
                let k = off.journey.as_ref().unwrap();
                assert!(
                    j.maximum_absolute_jerk_m_s3 <= 0.5,
                    "dt{dt} extra{extra} {:?}",
                    on.energy.release_control
                );
                assert!(
                    j.elapsed_s <= 210.,
                    "dt{dt} extra{extra} elapsed{}",
                    j.elapsed_s
                );
                assert!(j.final_position_m >= 1498. && j.final_position_m <= 1500.);
                assert!(
                    j.control.as_ref().unwrap().bounds_valid
                        && !j.control.as_ref().unwrap().end_of_authority_violated
                );
                assert_eq!(
                    serde_json::to_value(&j.trace).unwrap(),
                    serde_json::to_value(&k.trace).unwrap()
                );
                assert!(
                    !on.energy
                        .release_control
                        .as_ref()
                        .unwrap()
                        .slew_limit_exceeded
                );
                assert_eq!(
                    on.energy.release_control.as_ref().unwrap().forced_cutoffs,
                    0,
                    "dt{dt} extra{extra}"
                );
            }
            assert!(a.ledger.storage_balance_residual_j.abs() < 1e-5);
            assert!(a.ledger.train_and_storage_balance_residual_j.abs() < 1e-5);
        }
    }
}
