//! Bounded JSON interface fixture. It has no hardware outputs or motion plant.
use osr_atp::{
    wheel_station::{wheel_station_evaluate, WheelStationInputs},
    BrakeCommand,
};
use serde::Deserialize;
use std::io::{self, Read};
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    inputs: WheelStationInputs,
    atp: BrakeCommand,
}
fn main() {
    let mut raw = String::new();
    io::stdin().take(16385).read_to_string(&mut raw).unwrap();
    assert!(raw.len() <= 16384, "bounded request");
    let request: Request = serde_json::from_str(&raw).expect("typed wheel/station inputs");
    let outcome = wheel_station_evaluate(&request.inputs, request.atp);
    println!(
        "{}",
        serde_json::json!({"outcome":outcome,"physical_output_authorised":false,
        "scope":"wheel/station interface predicate fixture; brake plant and motion not simulated"})
    );
}
