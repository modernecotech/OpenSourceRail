//! Battery identity bound to simulation configuration; planning defaults are explicit.
use osr_bms::{BatteryChemistry, CommissioningProfile, ValidatedCommissioningProfile};
use osr_core::TrainId;
use serde::Deserialize;
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BatteryBindingSpec {
    pub train: String,
    pub profile_id: String,
    pub pack_identity: String,
    pub chemistry: BatteryChemistry,
    pub evidence_revision: String,
    pub nominal_pack_voltage_mv: u32,
    pub model_capacity_wh: u32,
    pub profile: CommissioningProfile,
}

#[derive(Clone, Debug)]
pub struct RuntimeBattery {
    pub(crate) profile: ValidatedCommissioningProfile,
    pub(crate) nominal_pack_voltage_mv: u32,
    pub(crate) model_capacity_wh: u32,
}

/// A commissioned run covers every train and cannot fall back for an omitted pack.
pub fn bind_batteries(
    specs: &[BatteryBindingSpec],
    train_count: usize,
    usable_capacity_wh: u32,
) -> Result<BTreeMap<TrainId, RuntimeBattery>, String> {
    if !specs.is_empty() && specs.len() != train_count {
        return Err("commissioned bindings must cover the complete fleet".into());
    }
    let mut result = BTreeMap::new();
    let mut packs = BTreeSet::new();
    for spec in specs {
        let number = spec
            .train
            .strip_prefix('T')
            .and_then(|s| s.parse::<u64>().ok())
            .filter(|n| *n > 0 && *n <= train_count as u64)
            .ok_or_else(|| format!("unknown commissioning train {}", spec.train))?;
        if !packs.insert(spec.pack_identity.clone()) {
            return Err("pack identity is allocated to multiple trains".into());
        }
        let profile = spec
            .profile
            .clone()
            .select(
                &spec.profile_id,
                &spec.pack_identity,
                spec.chemistry,
                &spec.evidence_revision,
            )
            .map_err(|e| format!("{}: {e:?}", spec.train))?;
        let params = profile.params();
        let voltage = u64::from(spec.nominal_pack_voltage_mv);
        let cells = u64::from(params.cell_count);
        let gross_wh = voltage * u64::from(params.cell_capacity_mah) / 1_000_000;
        if voltage < cells * u64::from(spec.profile.cell_min_mv)
            || voltage > cells * u64::from(spec.profile.cell_max_mv)
            || spec.model_capacity_wh != usable_capacity_wh
            || usable_capacity_wh == 0
            || u64::from(usable_capacity_wh) > gross_wh
        {
            return Err(
                "battery voltage/capacity does not match its calibrated pack and consist".into(),
            );
        }
        if result
            .insert(
                TrainId::new(number),
                RuntimeBattery {
                    profile,
                    nominal_pack_voltage_mv: spec.nominal_pack_voltage_mv,
                    model_capacity_wh: spec.model_capacity_wh,
                },
            )
            .is_some()
        {
            return Err("duplicate commissioned train".into());
        }
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn spec(train: &str, pack: &str) -> BatteryBindingSpec {
        BatteryBindingSpec {
            train: train.into(),
            profile_id: "bench-lfp".into(),
            pack_identity: pack.into(),
            chemistry: BatteryChemistry::Lfp,
            evidence_revision: "test-only".into(),
            nominal_pack_voltage_mv: 675_200,
            model_capacity_wh: 540_000,
            profile: CommissioningProfile {
                id: "bench-lfp".into(),
                pack_identity: pack.into(),
                evidence_revision: "test-only".into(),
                acceptance_record: "test-fixture-only".into(),
                chemistry: BatteryChemistry::Lfp,
                qualified: true,
                cell_min_mv: 2500,
                cell_max_mv: 3700,
                params: osr_bms::BmsParams::lfp_default(211, 800_000),
            },
        }
    }
    #[test]
    fn selected_identity_reaches_the_actual_onboard_shadow() {
        let bindings = bind_batteries(&[spec("T1", "pack-one")], 1, 540_000).unwrap();
        let mut scenario = crate::scenario_file::canonical_samawah_scenario();
        scenario.consist.battery_capacity_wh = 540_000;
        let train = crate::train::Train {
            id: TrainId::new(1),
            line_index: 0,
            consist: scenario.consist,
            energy_kwh_per_car_km: 4.0,
            heading: crate::train::Heading::Forward,
            service_role: crate::train::ServiceRole::Revenue,
            overnight_home: None,
            in_depot: false,
            phase: crate::train::TrainPhase::AwaitingDispatch {
                station: osr_core::StationId::new(1),
            },
            soc: 0.8,
            odometer_km: 0.0,
            energy_consumed_kwh: 0.0,
            energy_charged_kwh: 0.0,
            energy_roof_pv_kwh: 0.0,
            min_soc_seen: 0.8,
        };
        let shadow = crate::onboard::OnboardShadow::new_commissioned(
            &train,
            bindings[&TrainId::new(1)].clone(),
        );
        let summary = crate::onboard::summarise(&[shadow], &[train]);
        assert_eq!(summary.commissioned_battery_train_count, 1);
        assert_eq!(summary.per_train[0].bms_cell_count, 211);
        assert_eq!(summary.per_train[0].nominal_pack_voltage_mv, 675_200);
        assert_eq!(
            summary.per_train[0].battery_pack_identity.as_deref(),
            Some("pack-one")
        );
    }
    #[test]
    fn no_missing_pack_chemistry_or_capacity_fallback() {
        assert!(bind_batteries(&[spec("T1", "one")], 2, 540_000).is_err());
        let mut sodium = spec("T1", "one");
        sodium.chemistry = BatteryChemistry::SodiumIon;
        assert!(bind_batteries(&[sodium], 1, 540_000).is_err());
        let mut planning = spec("T1", "one");
        planning.profile.qualified = false;
        assert!(bind_batteries(&[planning], 1, 540_000).is_err());
        assert!(bind_batteries(&[spec("T1", "one")], 1, 432_000).is_err());
        assert!(bind_batteries(&[spec("T1", "same"), spec("T2", "same")], 2, 540_000).is_err());
        assert!(bind_batteries(&[], 2, 540_000).unwrap().is_empty());
    }
}
