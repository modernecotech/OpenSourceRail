//! Candidate-bound traction permissive for a continuously powered wheel train.
//!
//! ATP retains movement-authority and speed-envelope enforcement. This adapter
//! inhibits traction on contact, section or inverter faults and requests the
//! independent mechanical brake. It does not qualify the physical equipment.

use crate::BrakeCommand;

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PoweredWheelInputs {
    pub selected_configuration: [u8; 32],
    pub observed_configuration: [u8; 32],
    pub authority_valid: bool,
    pub localisation_known: bool,
    pub train_integrity_known: bool,
    pub communications_fresh: bool,
    pub doors_locked: bool,
    pub independent_brake_healthy: bool,
    pub independent_brake_profile_valid: bool,
    pub essential_service_supply_ready: bool,
    pub contact_shoes_proved: bool,
    pub powered_section_permitted: bool,
    pub section_isolated: bool,
    pub inverter_healthy: bool,
    pub traction_fault_latched: bool,
    pub stopped: bool,
    pub parking_brake_proved: bool,
    pub wheel_slide_active: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct PoweredWheelOutcome {
    pub traction_permissive: bool,
    pub traction_inhibit: bool,
    pub mechanical_brake: BrakeCommand,
    pub parking_brake_request: bool,
    pub rescue_required_if_stopped: bool,
}

/// Independent feedback for a requested passenger stop. The caller binds the
/// platform side and the released openings to the current authenticated visit.
#[derive(Clone, Copy, Debug)]
pub struct SecuredBerth {
    pub visit_and_platform_proved: bool,
    pub unreleased_doors_locked: bool,
    pub all_controllers_present: bool,
    pub independent_hold_applied: bool,
    pub inverter_inhibit_proved: bool,
}

/// Existing movement protection, including the all-doors-locked requirement.
#[must_use]
pub fn powered_wheel_evaluate(i: &PoweredWheelInputs, atp: BrakeCommand) -> PoweredWheelOutcome {
    evaluate(i, atp, Mode::Movement)
}

/// At a secured passenger stop the released doors may be unlocked. Traction
/// remains inhibited even if every door still reports locked.
#[must_use]
pub fn powered_wheel_at_berth(
    i: &PoweredWheelInputs,
    atp: BrakeCommand,
    berth: SecuredBerth,
) -> PoweredWheelOutcome {
    evaluate(i, atp, Mode::Berth(berth))
}

/// Receiving drive after a locked, authorised handover. At zero speed the
/// drive must already have taken the load before parking can be released.
#[must_use]
pub fn powered_wheel_starting(
    i: &PoweredWheelInputs,
    atp: BrakeCommand,
    starting_effort_proved: bool,
) -> PoweredWheelOutcome {
    evaluate(
        i,
        atp,
        Mode::Starting {
            starting_effort_proved,
        },
    )
}

#[derive(Clone, Copy)]
enum Mode {
    Movement,
    Berth(SecuredBerth),
    Starting { starting_effort_proved: bool },
}

fn evaluate(i: &PoweredWheelInputs, atp: BrakeCommand, mode: Mode) -> PoweredWheelOutcome {
    let state_protected = match mode {
        Mode::Movement => i.doors_locked,
        Mode::Starting {
            starting_effort_proved,
        } => i.stopped && i.doors_locked && starting_effort_proved,
        Mode::Berth(b) => {
            i.stopped
                && i.parking_brake_proved
                && b.visit_and_platform_proved
                && b.unreleased_doors_locked
                && b.all_controllers_present
                && b.independent_hold_applied
                && b.inverter_inhibit_proved
        }
    };
    let independent_ready = i.selected_configuration == i.observed_configuration
        && i.authority_valid
        && i.localisation_known
        && i.train_integrity_known
        && i.communications_fresh
        && state_protected
        && i.independent_brake_healthy
        && i.independent_brake_profile_valid
        && i.essential_service_supply_ready;
    let traction_supply_ready = i.contact_shoes_proved
        && i.powered_section_permitted
        && !i.section_isolated
        && i.inverter_healthy
        && !i.traction_fault_latched;
    let mechanical_brake = if !independent_ready {
        BrakeCommand::Emergency
    } else if !traction_supply_ready || i.wheel_slide_active {
        match atp {
            BrakeCommand::Emergency => BrakeCommand::Emergency,
            _ => BrakeCommand::Service(1000),
        }
    } else {
        atp
    };
    let traction_permissive = !matches!(mode, Mode::Berth(_))
        && independent_ready
        && traction_supply_ready
        && !i.wheel_slide_active
        && (!i.stopped
            || i.parking_brake_proved
            || matches!(
                mode,
                Mode::Starting {
                    starting_effort_proved: true
                }
            ))
        && matches!(mechanical_brake, BrakeCommand::Release);
    PoweredWheelOutcome {
        traction_permissive,
        traction_inhibit: !traction_permissive,
        mechanical_brake,
        parking_brake_request: i.stopped
            && (matches!(mode, Mode::Berth(_)) || !traction_supply_ready),
        rescue_required_if_stopped: i.stopped && !traction_supply_ready,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ready() -> PoweredWheelInputs {
        PoweredWheelInputs {
            selected_configuration: [1; 32],
            observed_configuration: [1; 32],
            authority_valid: true,
            localisation_known: true,
            train_integrity_known: true,
            communications_fresh: true,
            doors_locked: true,
            independent_brake_healthy: true,
            independent_brake_profile_valid: true,
            essential_service_supply_ready: true,
            contact_shoes_proved: true,
            powered_section_permitted: true,
            section_isolated: false,
            inverter_healthy: true,
            traction_fault_latched: false,
            stopped: true,
            parking_brake_proved: true,
            wheel_slide_active: false,
        }
    }

    #[test]
    fn passenger_stop_requires_independent_berth_and_motion_proofs() {
        let berth = SecuredBerth {
            visit_and_platform_proved: true,
            unreleased_doors_locked: true,
            all_controllers_present: true,
            independent_hold_applied: true,
            inverter_inhibit_proved: true,
        };
        let mut i = ready();
        i.doors_locked = false;
        for demand in [
            BrakeCommand::Release,
            BrakeCommand::Service(450),
            BrakeCommand::Emergency,
        ] {
            let out = powered_wheel_at_berth(&i, demand, berth);
            assert_eq!(out.mechanical_brake, demand);
            assert!(out.parking_brake_request && out.traction_inhibit && !out.traction_permissive);
        }
        for fault in [
            SecuredBerth {
                visit_and_platform_proved: false,
                ..berth
            },
            SecuredBerth {
                unreleased_doors_locked: false,
                ..berth
            },
            SecuredBerth {
                all_controllers_present: false,
                ..berth
            },
            SecuredBerth {
                independent_hold_applied: false,
                ..berth
            },
            SecuredBerth {
                inverter_inhibit_proved: false,
                ..berth
            },
        ] {
            assert_eq!(
                powered_wheel_at_berth(&i, BrakeCommand::Release, fault).mechanical_brake,
                BrakeCommand::Emergency
            );
        }
        for fault in [
            PoweredWheelInputs {
                stopped: false,
                ..i.clone()
            },
            PoweredWheelInputs {
                parking_brake_proved: false,
                ..i.clone()
            },
            PoweredWheelInputs {
                train_integrity_known: false,
                ..i.clone()
            },
            PoweredWheelInputs {
                communications_fresh: false,
                ..i.clone()
            },
            PoweredWheelInputs {
                localisation_known: false,
                ..i.clone()
            },
            PoweredWheelInputs {
                independent_brake_healthy: false,
                ..i.clone()
            },
        ] {
            assert_eq!(
                powered_wheel_at_berth(&fault, BrakeCommand::Release, berth).mechanical_brake,
                BrakeCommand::Emergency
            );
        }
        assert_eq!(
            powered_wheel_evaluate(&i, BrakeCommand::Release).mechanical_brake,
            BrakeCommand::Emergency
        );
    }

    #[test]
    fn starting_effort_bridges_parking_release_only_at_zero_speed() {
        let i = PoweredWheelInputs {
            parking_brake_proved: false,
            ..ready()
        };
        assert!(!powered_wheel_evaluate(&i, BrakeCommand::Release).traction_permissive);
        assert!(powered_wheel_starting(&i, BrakeCommand::Release, true).traction_permissive);
        assert_eq!(
            powered_wheel_starting(&i, BrakeCommand::Release, false).mechanical_brake,
            BrakeCommand::Emergency
        );
        for fault in [
            PoweredWheelInputs {
                stopped: false,
                ..i.clone()
            },
            PoweredWheelInputs {
                authority_valid: false,
                ..i.clone()
            },
            PoweredWheelInputs {
                doors_locked: false,
                ..i.clone()
            },
        ] {
            let result = powered_wheel_starting(&fault, BrakeCommand::Release, true);
            assert!(result.traction_inhibit);
            assert_eq!(result.mechanical_brake, BrakeCommand::Emergency);
        }
    }

    #[test]
    fn selected_train_requires_atp_release_and_proved_contact() {
        assert!(powered_wheel_evaluate(&ready(), BrakeCommand::Release).traction_permissive);
        for command in [BrakeCommand::Service(1), BrakeCommand::Emergency] {
            assert!(!powered_wheel_evaluate(&ready(), command).traction_permissive);
        }
        let mut mismatched = ready();
        mismatched.observed_configuration = [2; 32];
        let result = powered_wheel_evaluate(&mismatched, BrakeCommand::Release);
        assert_eq!(result.mechanical_brake, BrakeCommand::Emergency);
        assert!(result.traction_inhibit);
    }

    #[test]
    fn contact_section_and_inverter_faults_stop_on_independent_brake() {
        for fault in 0..5 {
            let mut i = ready();
            i.stopped = false;
            match fault {
                0 => i.contact_shoes_proved = false,
                1 => i.powered_section_permitted = false,
                2 => i.section_isolated = true,
                3 => i.inverter_healthy = false,
                _ => i.traction_fault_latched = true,
            }
            let result = powered_wheel_evaluate(&i, BrakeCommand::Release);
            assert!(result.traction_inhibit);
            assert_eq!(result.mechanical_brake, BrakeCommand::Service(1000));
            assert!(!result.parking_brake_request);
            i.stopped = true;
            let stopped = powered_wheel_evaluate(&i, BrakeCommand::Release);
            assert!(stopped.parking_brake_request);
            assert!(stopped.rescue_required_if_stopped);
        }
    }

    #[test]
    fn essential_supply_or_brake_fault_demands_emergency_stop() {
        for fault in 0..3 {
            let mut i = ready();
            i.stopped = false;
            match fault {
                0 => i.essential_service_supply_ready = false,
                1 => i.independent_brake_healthy = false,
                _ => i.independent_brake_profile_valid = false,
            }
            let result = powered_wheel_evaluate(&i, BrakeCommand::Release);
            assert!(result.traction_inhibit);
            assert_eq!(result.mechanical_brake, BrakeCommand::Emergency);
        }
    }
}
