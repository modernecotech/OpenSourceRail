use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::{BTreeMap, HashSet};
use std::io;

pub const FULL_AVAILABILITY_BPS: u64 = 10_000;
pub const PLAN_SCHEMA: &str = "osr-workforce-plan/1";

#[derive(Debug, Deserialize)]
pub struct Plan {
    pub schema: String,
    pub plan_id: String,
    pub scope: Value,
    pub source_sha256: BTreeMap<String, String>,
    pub rows: Vec<Shift>,
    pub gaps: Vec<Gap>,
}

#[derive(Debug, Deserialize)]
pub struct Shift {
    pub work_id: String,
    pub phase: String,
    pub role: String,
    pub shift: String,
    pub start_minute: Option<u64>,
    pub minutes_per_shift: Option<u64>,
    pub days: Option<u64>,
    pub assigned_posts: Option<u64>,
    pub required_minutes: Option<u64>,
    pub paid_minutes: Option<u64>,
    pub utilisation_bps: u64,
    pub rates_cents_per_hour: Option<[u64; 3]>,
    pub rate_basis: String,
    pub cost_account: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Gap {
    pub phase: String,
    pub work: String,
    pub owner: String,
    pub cost_basis: String,
}

impl Plan {
    pub fn validate(&self) -> io::Result<()> {
        let has_scope = match &self.scope {
            Value::String(text) => !text.trim().is_empty(),
            Value::Object(fields) => !fields.is_empty(),
            _ => false,
        };
        if self.schema != PLAN_SCHEMA || self.plan_id.trim().is_empty() || !has_scope {
            return Err(invalid(
                "A supported schema, plan identity and scope are required",
            ));
        }
        for (source, hash) in &self.source_sha256 {
            if source.trim().is_empty()
                || hash.len() != 64
                || !hash.bytes().all(|b| b.is_ascii_hexdigit())
            {
                return Err(invalid(format!("Invalid source SHA-256 for {source}")));
            }
        }
        let mut identities = HashSet::new();
        for row in &self.rows {
            row.validate()?;
            if !identities.insert(&row.work_id) {
                return Err(invalid(format!("Duplicate work identity {}", row.work_id)));
            }
        }
        for gap in &self.gaps {
            if [&gap.phase, &gap.work, &gap.owner, &gap.cost_basis]
                .iter()
                .any(|v| v.trim().is_empty())
            {
                return Err(invalid(
                    "Each gap requires a phase, work, owner and cost basis",
                ));
            }
        }
        Ok(())
    }
}

impl Shift {
    fn validate(&self) -> io::Result<()> {
        let labels = [
            &self.work_id,
            &self.phase,
            &self.role,
            &self.shift,
            &self.rate_basis,
            &self.cost_account,
        ];
        if labels.iter().any(|v| v.trim().is_empty()) {
            return Err(invalid("Each shift requires a work identity, phase, role, shift, rate basis and cost account"));
        }
        if self.start_minute.is_some_and(|v| v >= 1440)
            || self.minutes_per_shift.is_some_and(|v| v > 1440)
            || self.utilisation_bps > FULL_AVAILABILITY_BPS
        {
            return Err(invalid(format!(
                "Shift timing or utilisation is out of range for {}",
                self.work_id
            )));
        }
        if self
            .rates_cents_per_hour
            .is_some_and(|[low, base, high]| low > base || base > high)
        {
            return Err(invalid(format!(
                "Rates must be ordered low, base, high for {}",
                self.work_id
            )));
        }
        Ok(())
    }
}

pub fn invalid(message: impl Into<String>) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, message.into())
}
