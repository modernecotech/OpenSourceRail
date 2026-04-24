"""`osr_scenario` — derive `scenarios/{slug}.toml` from a
`designs/.../design.toml`.

The design file is the single source of truth for one OSR city; this
module projects the operational subset of it into the wire schema
`crates/osr-sim/src/scenario_file.rs` expects. Re-running the
generator whenever `design.toml` changes keeps the simulator scenario
in sync automatically.

Mapping rules:

- `[[stations]]` rows inherit `charging_power_kw` + `dwell_seconds`
  from their archetype (per
  `lib/templates/stations.toml [archetypes.*]`). Per-station
  overrides in the design file win.
- `[[lines]]` copy verbatim, with per-section `distance_from_prev_m`
  preserved.
- `[[fleets]]` copy verbatim.
- `[[sites]]` expand their `tier` reference into concrete kW/kWh
  fields from `lib/templates/energy-sites.toml [tiers.*]`. Per-
  site overrides in the design file win.
- `[climate]` maps preset → ambient_c + peak_sun_hours. Per-city
  override for peak_sun_hours is preserved.
- `[consist]` is synthesised from the rolling-stock template family
  referenced by each line.
- The scenario `name` comes from `[design.name]`; `start_time` is
  always `06:00` (pre-AM-peak; scenarios can override locally after
  regeneration if needed).

The generator is deterministic: same design.toml in → byte-identical
scenario.toml out. No RNG, no wall-clock side-effects.
"""

from .generator import (
    GeneratorError,
    ScenarioGenerator,
    generate_from_path,
    generate_scenario,
)

__all__ = [
    "GeneratorError",
    "ScenarioGenerator",
    "generate_from_path",
    "generate_scenario",
]
