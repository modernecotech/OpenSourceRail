//! TCMS status adapter for the Baghdad protected-conductor planning candidate.
//!
//! The generic BMS contactor input is the *service battery* contactor here.
//! Traction is supplied by the guarded line conductor and has separate contact,
//! section and inverter proofs. This status cannot grant ATP authority.

use crate::{tcms_evaluate, ConsistStatus, TcmsInputs};

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProtectedConductorStatus {
    pub selected_configuration: [u8; 32],
    pub observed_configuration: [u8; 32],
    pub contact_shoes_proved: bool,
    pub powered_section_permitted: bool,
    pub section_isolated: bool,
    pub inverter_healthy: bool,
    pub essential_service_supply_ready: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct ProtectedConsistStatus {
    pub base: ConsistStatus,
    pub traction_supply_ready: bool,
    pub traction_permissive: bool,
}

#[must_use]
pub fn evaluate_protected_conductor(
    inputs: &TcmsInputs,
    supply: &ProtectedConductorStatus,
) -> ProtectedConsistStatus {
    let base = tcms_evaluate(inputs);
    let traction_supply_ready = supply.selected_configuration == supply.observed_configuration
        && supply.contact_shoes_proved
        && supply.powered_section_permitted
        && !supply.section_isolated
        && supply.inverter_healthy;
    ProtectedConsistStatus {
        traction_permissive: base.ready_to_move
            && traction_supply_ready
            && supply.essential_service_supply_ready,
        base,
        traction_supply_ready,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn inputs() -> TcmsInputs {
        TcmsInputs {
            doors_interlock_ok: true,
            bms_contactor_closed: true,
            traction_inverter_enabled: true,
            ..TcmsInputs::default()
        }
    }

    fn supply() -> ProtectedConductorStatus {
        ProtectedConductorStatus {
            selected_configuration: [1; 32],
            observed_configuration: [1; 32],
            contact_shoes_proved: true,
            powered_section_permitted: true,
            section_isolated: false,
            inverter_healthy: true,
            essential_service_supply_ready: true,
        }
    }

    #[test]
    fn line_supply_and_service_battery_are_distinct_proofs() {
        assert!(evaluate_protected_conductor(&inputs(), &supply()).traction_permissive);
        let mut no_service = inputs();
        no_service.bms_contactor_closed = false;
        assert!(!evaluate_protected_conductor(&no_service, &supply()).traction_permissive);
        let mut isolated = supply();
        isolated.section_isolated = true;
        let result = evaluate_protected_conductor(&inputs(), &isolated);
        assert!(result.base.ready_to_move);
        assert!(!result.traction_supply_ready);
        assert!(!result.traction_permissive);
    }

    #[test]
    fn contact_configuration_and_inverter_faults_inhibit_traction() {
        for fault in 0..5 {
            let mut s = supply();
            match fault {
                0 => s.observed_configuration = [2; 32],
                1 => s.contact_shoes_proved = false,
                2 => s.powered_section_permitted = false,
                3 => s.inverter_healthy = false,
                _ => s.essential_service_supply_ready = false,
            }
            assert!(!evaluate_protected_conductor(&inputs(), &s).traction_permissive);
        }
    }
}
