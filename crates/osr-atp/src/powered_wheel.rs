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

#[must_use]
pub fn powered_wheel_evaluate(i: &PoweredWheelInputs, atp: BrakeCommand) -> PoweredWheelOutcome {
    let independent_ready = i.selected_configuration == i.observed_configuration
        && i.authority_valid
        && i.localisation_known
        && i.train_integrity_known
        && i.communications_fresh
        && i.doors_locked
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
    let traction_permissive = independent_ready
        && traction_supply_ready
        && !i.wheel_slide_active
        && (!i.stopped || i.parking_brake_proved)
        && matches!(mechanical_brake, BrakeCommand::Release);
    PoweredWheelOutcome {
        traction_permissive,
        traction_inhibit: !traction_permissive,
        mechanical_brake,
        parking_brake_request: i.stopped && !traction_supply_ready,
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
