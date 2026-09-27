//! Narrow, observation-only boundary from Rust evaluators to OSR supervision.
//!
//! This crate deliberately defines no command, movement-authority, protection,
//! reset, ERP, or executive-decision type. A consumer may historize these
//! observations and use them as decision evidence; it cannot use this contract
//! to acquire controller authority.

use std::collections::BTreeSet;

use serde::{Deserialize, Serialize};
use thiserror::Error;

pub const SCHEMA: &str = "osr-supervisory-observations/1";
pub const AUTHORITY: &str = "observation-only";
pub const MAX_OBSERVATIONS: usize = 256;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Observation {
    pub equipment_type: String,
    pub measurement: String,
    pub value: f64,
    pub unit: String,
    pub source_crates: Vec<String>,
}

impl Observation {
    #[must_use]
    pub fn new(
        equipment_type: &str,
        measurement: &str,
        value: impl Into<f64>,
        unit: &str,
        source_crates: &[&str],
    ) -> Self {
        Self {
            equipment_type: equipment_type.into(),
            measurement: measurement.into(),
            value: value.into(),
            unit: unit.into(),
            source_crates: source_crates.iter().map(|value| (*value).into()).collect(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ObservationFrame {
    pub schema: String,
    pub environment: String,
    pub authority: String,
    pub key: String,
    pub source_time_ns: u64,
    pub observations: Vec<Observation>,
}

impl ObservationFrame {
    #[must_use]
    pub fn simulation(key: &str, source_time_ns: u64, observations: Vec<Observation>) -> Self {
        Self {
            schema: SCHEMA.into(),
            environment: "simulation".into(),
            authority: AUTHORITY.into(),
            key: key.into(),
            source_time_ns,
            observations,
        }
    }

    pub fn validate(&self) -> Result<(), ContractError> {
        if self.schema != SCHEMA {
            return Err(ContractError::Schema);
        }
        if self.environment != "simulation" {
            return Err(ContractError::Environment);
        }
        if self.authority != AUTHORITY {
            return Err(ContractError::Authority);
        }
        if !valid_key(&self.key) || self.source_time_ns == 0 {
            return Err(ContractError::IdentityOrTime);
        }
        if self.observations.is_empty() || self.observations.len() > MAX_OBSERVATIONS {
            return Err(ContractError::ObservationCount);
        }
        let mut identities = BTreeSet::new();
        for (index, observation) in self.observations.iter().enumerate() {
            if !valid_identifier(&observation.equipment_type)
                || !valid_identifier(&observation.measurement)
                || !observation.value.is_finite()
                || observation.unit.is_empty()
                || observation.unit.len() > 24
                || !observation.unit.is_ascii()
                || observation.source_crates.is_empty()
                || observation.source_crates.len() > 8
                || observation
                    .source_crates
                    .iter()
                    .any(|value| !valid_identifier(value))
                || observation
                    .source_crates
                    .iter()
                    .collect::<BTreeSet<_>>()
                    .len()
                    != observation.source_crates.len()
            {
                return Err(ContractError::InvalidObservation { index });
            }
            if !identities.insert((&observation.equipment_type, &observation.measurement)) {
                return Err(ContractError::DuplicateObservation { index });
            }
        }
        Ok(())
    }
}

fn valid_identifier(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 160
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.' | b':'))
}

fn valid_key(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 160
        && value.bytes().all(|byte| {
            byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.' | b':' | b'|')
        })
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum ContractError {
    #[error("unsupported supervisory observation schema")]
    Schema,
    #[error("only the explicit simulation environment is supported")]
    Environment,
    #[error("supervisory frame attempted to claim authority")]
    Authority,
    #[error("invalid frame identity or source time")]
    IdentityOrTime,
    #[error("supervisory observation count is outside bounds")]
    ObservationCount,
    #[error("invalid observation at index {index}")]
    InvalidObservation { index: usize },
    #[error("duplicate observation at index {index}")]
    DuplicateObservation { index: usize },
}

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_frame() -> ObservationFrame {
        ObservationFrame::simulation(
            "samawah|SAM-ST-001",
            1,
            vec![Observation::new(
                "facilities",
                "lighting_pct",
                80.0,
                "%",
                &["osr-station-scada"],
            )],
        )
    }

    #[test]
    fn valid_frame_round_trips_with_exact_fields() {
        let frame = valid_frame();
        frame.validate().unwrap();
        let encoded = serde_json::to_string(&frame).unwrap();
        assert_eq!(
            serde_json::from_str::<ObservationFrame>(&encoded).unwrap(),
            frame
        );
    }

    #[test]
    fn authority_schema_environment_and_unknown_fields_fail_closed() {
        let mut frame = valid_frame();
        frame.authority = "command".into();
        assert_eq!(frame.validate(), Err(ContractError::Authority));
        frame = valid_frame();
        frame.schema = "osr-supervisory-observations/0".into();
        assert_eq!(frame.validate(), Err(ContractError::Schema));
        frame = valid_frame();
        frame.environment = "production".into();
        assert_eq!(frame.validate(), Err(ContractError::Environment));
        frame = valid_frame();
        frame.source_time_ns = 0;
        assert_eq!(frame.validate(), Err(ContractError::IdentityOrTime));
        let unknown = r#"{"schema":"osr-supervisory-observations/1","environment":"simulation","authority":"observation-only","key":"a","source_time_ns":1,"observations":[],"command":{}}"#;
        assert!(serde_json::from_str::<ObservationFrame>(unknown).is_err());
    }

    #[test]
    fn duplicate_nonfinite_and_empty_frames_fail_closed() {
        let mut frame = valid_frame();
        frame.observations.push(frame.observations[0].clone());
        assert_eq!(
            frame.validate(),
            Err(ContractError::DuplicateObservation { index: 1 })
        );
        frame = valid_frame();
        frame.observations[0].value = f64::NAN;
        assert_eq!(
            frame.validate(),
            Err(ContractError::InvalidObservation { index: 0 })
        );
        frame.observations.clear();
        assert_eq!(frame.validate(), Err(ContractError::ObservationCount));
    }
}
