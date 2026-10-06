//! Explicit commissioning selection. Planning chemistry labels carry no calibration.
use crate::{bms_evaluate, BmsInputs, BmsOutput, BmsParams, BmsState};

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum BatteryChemistry {
    Lfp,
    SodiumIon,
}

/// Evidence supplied by the commissioning authority, never by a chemistry default.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CommissioningProfile {
    pub id: String,
    pub pack_identity: String,
    pub evidence_revision: String,
    pub acceptance_record: String,
    pub chemistry: BatteryChemistry,
    pub qualified: bool,
    pub cell_min_mv: u16,
    pub cell_max_mv: u16,
    pub params: BmsParams,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum CommissioningError {
    IdentityMismatch,
    MissingEvidence,
    NotQualified,
    InvalidCalibration,
}

/// Constructible only through validation. The evaluator's protection path is shared.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ValidatedCommissioningProfile {
    profile: CommissioningProfile,
}

impl CommissioningProfile {
    pub fn select(
        self,
        requested_id: &str,
        requested_pack: &str,
        requested_chemistry: BatteryChemistry,
        requested_revision: &str,
    ) -> Result<ValidatedCommissioningProfile, CommissioningError> {
        if self.id != requested_id
            || self.pack_identity != requested_pack
            || self.chemistry != requested_chemistry
            || self.evidence_revision != requested_revision
        {
            return Err(CommissioningError::IdentityMismatch);
        }
        if self.id.is_empty()
            || self.pack_identity.is_empty()
            || self.evidence_revision.is_empty()
            || self.acceptance_record.is_empty()
        {
            return Err(CommissioningError::MissingEvidence);
        }
        if !self.qualified {
            return Err(CommissioningError::NotQualified);
        }
        let p = &self.params;
        if p.cell_count == 0
            || p.cell_capacity_mah == 0
            || !(self.cell_min_mv <= p.v_trip_min_mv
                && p.v_trip_min_mv < p.v_warn_min_mv
                && p.v_warn_min_mv < p.v_warn_max_mv
                && p.v_warn_max_mv < p.v_trip_max_mv
                && p.v_trip_max_mv <= self.cell_max_mv)
            || !(p.t_trip_min_dc < p.t_warn_min_dc
                && p.t_warn_min_dc < p.t_warn_max_dc
                && p.t_warn_max_dc < p.t_trip_max_dc)
            || p.imbalance_trip_mv == 0
            || p.fault_cooldown_ms == 0
            || p.max_charge_ma == 0
            || p.max_discharge_ma == 0
            || p.max_charge_ma >= p.current_trip_ma
            || p.max_discharge_ma >= p.current_trip_ma
            || p.cycle_fade_ppm_per_efc == 0
            || p.hot_cycle_multiplier == 0
        {
            return Err(CommissioningError::InvalidCalibration);
        }
        Ok(ValidatedCommissioningProfile { profile: self })
    }
}

impl ValidatedCommissioningProfile {
    #[must_use]
    pub fn evaluate(&self, prev: &BmsState, inputs: &BmsInputs<'_>) -> BmsOutput {
        if inputs.cell_voltages_mv.len() != usize::from(self.profile.params.cell_count) {
            let mismatch = BmsInputs {
                cell_voltages_mv: &[],
                ..*inputs
            };
            return bms_evaluate(prev, &mismatch, &self.profile.params);
        }
        bms_evaluate(prev, inputs, &self.profile.params)
    }

    #[must_use]
    pub fn identity(&self) -> (&str, &str, &str) {
        (
            &self.profile.id,
            &self.profile.pack_identity,
            &self.profile.evidence_revision,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn reference() -> CommissioningProfile {
        CommissioningProfile {
            id: "lfp-commissioned-1".into(),
            pack_identity: "pack-001".into(),
            evidence_revision: "test-revision".into(),
            acceptance_record: "test-only".into(),
            chemistry: BatteryChemistry::Lfp,
            qualified: true,
            cell_min_mv: 2500,
            cell_max_mv: 3700,
            params: BmsParams::lfp_default(96, 100_000),
        }
    }
    #[test]
    fn chemistry_change_cannot_reuse_lfp_calibration() {
        assert_eq!(
            reference().select(
                "lfp-commissioned-1",
                "pack-001",
                BatteryChemistry::SodiumIon,
                "test-revision"
            ),
            Err(CommissioningError::IdentityMismatch)
        );
    }
    #[test]
    fn unqualified_and_invalid_profiles_rejected() {
        let mut p = reference();
        p.qualified = false;
        assert_eq!(
            p.select(
                "lfp-commissioned-1",
                "pack-001",
                BatteryChemistry::Lfp,
                "test-revision"
            ),
            Err(CommissioningError::NotQualified)
        );
        let mut p = reference();
        p.params.v_trip_max_mv = 2500;
        assert_eq!(
            p.select(
                "lfp-commissioned-1",
                "pack-001",
                BatteryChemistry::Lfp,
                "test-revision"
            ),
            Err(CommissioningError::InvalidCalibration)
        );
    }
    #[test]
    fn validated_profile_uses_existing_protection() {
        let p = reference()
            .select(
                "lfp-commissioned-1",
                "pack-001",
                BatteryChemistry::Lfp,
                "test-revision",
            )
            .unwrap();
        let voltages = [3200; 96];
        let temps = [250; 96];
        let i = BmsInputs {
            now_ns: 0,
            cell_voltages_mv: &voltages,
            cell_temps_dc: &temps,
            pack_current_ma: 0,
            pack_voltage_mv: 307200,
            off_gas_detected: true,
            external_fire_trip: false,
            hazard_module_id: Some(1),
            hazard_string_id: None,
            external_command: crate::ContactorCommand::RequestClose,
            dt_ns: 100_000_000,
        };
        let out = p.evaluate(&BmsState::initial(800), &i);
        assert_eq!(out.contactor, crate::ContactorState::OpenFault);
        assert_eq!(out.charge_limit_ma, 0);
        assert!(out.pack_isolation_requested);
        let wrong = BmsInputs {
            off_gas_detected: false,
            cell_voltages_mv: &voltages[..95],
            cell_temps_dc: &temps[..95],
            ..i
        };
        assert!(p
            .evaluate(&BmsState::initial(800), &wrong)
            .state
            .faults
            .contains(crate::FaultReason::SensorMismatch));
    }
}
