//! Emit actual controller outputs for configuration-bound fault evidence.
//! Acceptance criteria are held in the engineering requirement records.
use osr_hvac::{thermal_evaluate, IntegratedThermalInputs, IntegratedThermalParams};
use serde::{Deserialize, Serialize};
use std::io::{self, Read};

#[derive(Deserialize)]
struct Case {
    scenario_id: String,
    inputs: IntegratedThermalInputs,
}

#[derive(Serialize)]
struct ResultRow {
    scenario_id: String,
    inputs: IntegratedThermalInputs,
    actual: osr_hvac::IntegratedThermalOutput,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let cases: Vec<Case> = serde_json::from_str(&input)?;
    let params = IntegratedThermalParams::light_metro_hot_climate();
    let results: Vec<ResultRow> = cases
        .into_iter()
        .map(|case| ResultRow {
            scenario_id: case.scenario_id,
            actual: thermal_evaluate(&case.inputs, &params),
            inputs: case.inputs,
        })
        .collect();
    println!("{}", serde_json::to_string(&results)?);
    Ok(())
}
