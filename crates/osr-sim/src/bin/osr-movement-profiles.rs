//! Export the simulator's controlled section timing, without claiming timetable release.
use osr_sim::{
    physics::kinematic_profile,
    scenario_file::{load_scenario_from_path, ScenarioFile},
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args()
        .nth(1)
        .ok_or("usage: osr-movement-profiles SCENARIO.toml")?;
    let raw: ScenarioFile = toml::from_str(&std::fs::read_to_string(&path)?)?;
    let config = load_scenario_from_path(std::path::Path::new(&path))?;
    let mut rows = Vec::new();
    for line in &config.network.lines {
        for (id, heading) in line
            .forward_sections
            .iter()
            .map(|id| (id, "forward"))
            .chain(line.reverse_sections.iter().map(|id| (id, "reverse")))
        {
            let section = config.network.section(*id);
            let speed = section.max_speed_mps.min(config.consist.max_speed_mps);
            let profile = kinematic_profile(
                section.length_mm as f32 / 1000.0,
                speed,
                config.consist.service_accel_mps2,
                config.consist.service_decel_mps2(),
            );
            let from = raw.stations[section.from_station.0 as usize - 1].id.clone();
            let to = raw.stations[section.to_station.0 as usize - 1].id.clone();
            rows.push(serde_json::json!({"line":line.name,"heading":heading,"from_station":from,"to_station":to,
                "distance_m":profile.length_m,"travel_seconds":profile.total_s,
                "peak_speed_mps":profile.v_peak_mps,"acceleration_mps2":profile.accel_mps2,
                "deceleration_mps2":profile.decel_mps2}));
        }
    }
    println!(
        "{}",
        serde_json::to_string_pretty(&serde_json::json!({"schema":1,
        "basis":"osr-sim scenario loader and rest-to-rest section movement model",
        "timetable_accepted":false,"sections":rows}))?
    );
    Ok(())
}
