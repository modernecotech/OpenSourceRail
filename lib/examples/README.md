# Scenario files

OpenSourceRail simulator scenarios are plain-text TOML files describing a
city's rail network: stations, lines, fleets, schedules, and climate. This
directory holds the reference scenarios. **Copy one and edit it** to design
a network for your own city.

## Running a scenario

```
cargo run --release --bin osr-sim -- --config scenarios/my-city.toml \
    --duration 3600 --status-every 300
```

Useful flags:

| Flag | Purpose |
|---|---|
| `--config PATH` | Path to a scenario TOML file |
| `--duration SECS` | How long to simulate (sim-seconds). Multi-day runs are supported — the clock wraps at midnight, dispatch schedules re-arm at service_start, and PV cycles through subsequent days. 86400 = 1 day, 604800 = 1 week. |
| `--time-step SECS` | Simulation tick length (default 1 s) |
| `--status-every SECS` | Print a status snapshot every N sim-seconds; 0 disables |
| `--json-out PATH` | Write the full event trace + summary as JSON |
| `--csv-out PATH` | Write per-train periodic snapshots (time, position, SoC) as CSV, suitable for loading into a spreadsheet or plotting tool |
| `--csv-every SECS` | CSV snapshot interval (default 60 sim-seconds) |

## Visualization

A companion tool `osr-vis` turns a scenario TOML into a self-contained HTML
file showing the network diagram:

```
cargo run --release --bin osr-vis -- --config scenarios/my-city.toml \
    --out /tmp/my-city.html
```

No runtime dependencies — open the HTML file in any browser. Useful for
reviewing station placement, line structure, and energy-site distribution
at a glance.

## Reference scenarios

| File | What it is |
|---|---|
| [`example-simple.toml`](example-simple.toml) | Three-station shuttle, one train. The smallest viable config — copy this as a template for a new city. |
| [`minimal-city.toml`](minimal-city.toml) | Slightly richer fixture exercising every required block. |
| Built-in `samawah` scenario (compiled into `osr-sim` — pass `--scenario samawah`) | Two-line hand-designed reference deployment from RFC 0003. End-to-end test fixture, no TOML required. |
| Built-in `samawah-line1` scenario | Line 1 only; useful for isolating radial-line behaviour. |
| [`designs/west-asia/Iraq/Samawah/samawah.toml`](../../designs/west-asia/Iraq/Samawah/samawah.toml) | The auto-planned three-line `light-metro-3car` Samawah network emitted by `osr-design` from real OSM + WorldPop data. Pass via `--config` to `osr-sim`. |

## File format

A scenario has five top-level sections. Here's the minimum viable shape:

```toml
[scenario]
name = "My City Metro"
start_time = "06:00"        # sim wall-clock start, HH:MM

[climate]
ambient_c = 30.0             # degrees Celsius
peak_sun_hours = 5.0         # for annual PV math (not yet used in 1-day sim)

[[stations]]
id = "terminal-a"            # string ID, used by lines & fleets below
name = "Terminal A"          # human-readable
charging_power_kw = 1000     # 0 or omit for no charging pad
dwell_seconds = 60
is_terminal = true           # trains turn around here (linear lines)
# is_depot = false           # optional; marks a depot location

# ... more [[stations]] ...

[[lines]]
id = "line-1"
name = "Line 1"
is_ring = false              # true for a closed loop
# ring_wrap_length_m = 1600  # required if is_ring = true
stations = [
    { id = "terminal-a", distance_from_prev_m = 0 },
    { id = "stop-1",     distance_from_prev_m = 1500 },
    { id = "terminal-b", distance_from_prev_m = 1500 },
]

[[fleets]]
line = "line-1"              # must match a line id above
trainset_count = 4
dispatch_points = [          # where trains start AND where dispatches are
    { station = "terminal-a", heading = "forward" },
    { station = "terminal-b", heading = "reverse" },
]                            # throttled to honor the schedule
service_start = "05:30"
service_end   = "23:30"
schedule = [
    { from = "05:30", to = "07:00", headway_min = 10 },
    { from = "07:00", to = "22:00", headway_min = 5 },
    { from = "22:00", to = "23:30", headway_min = 15 },
]
```

### Field reference

#### `[scenario]`

- `name` — any string, shown at run start.
- `start_time` — `"HH:MM"`, the sim's wall clock at tick 0. Set it earlier
  than the schedule's `service_start` to watch the morning startup; set it
  later to focus on midday or evening service.

#### `[climate]`

- `ambient_c` — ambient temperature in °C. Drives the HVAC uplift applied to
  traction energy consumption.
- `peak_sun_hours` — average daily peak sun-hours (used by future PV sizing;
  already honored in the energy reports).
- `hvac_uplift_frac` *(optional)* — override the automatic calculation of
  HVAC load. If omitted, a linear curve from 25 °C baseline, capped at 25 %
  at 50 °C, is used.

#### `[consist]` *(optional)*

Overrides the reference 3-car light-metro consist. All fields are optional;
omitted ones fall back to the reference values.

```toml
[consist]
car_count = 3
length_m = 57
mass_kg = 102000
max_speed_kmh = 90
battery_capacity_kwh = 360
passenger_capacity = 330
seat_count = 60
crush_capacity = 420
```

#### `[[stations]]`

Declare each station once. Referenced by `id` from lines and fleets.

- `id` — string ID, unique within the scenario.
- `name` — human-readable; appears in logs and abbreviations.
- `dwell_seconds` — how long trains pause here. Longer at interchanges and
  terminals; short (20–30 s) at mid-line stops.
- `charging_power_kw` *(default 0)* — opportunity-charging capability.
  Terminals typically 1000; mid-line charging stations 300–500.
- `is_terminal` *(default false)* — trains flip direction here on linear
  lines. Rings have no terminals.
- `is_depot` *(default false)* — marks a maintenance/layup site (cosmetic
  for now; future versions use it for overnight charging).

#### `[[lines]]`

- `id`, `name` — identification.
- `is_ring` *(default false)* — true for a closed loop.
- `stations` — inline array of `{ id, distance_from_prev_m }`. The first
  entry must have `distance_from_prev_m = 0`. Subsequent distances are
  metres between consecutive stations.
- `ring_wrap_length_m` — **required for rings**, **forbidden for linear
  lines**. The distance of the closing segment that connects the last
  station back to the first.

#### `[[fleets]]`

- `line` — must match a line `id`.
- `trainset_count` — how many trainsets operate this line.
- `dispatch_points` — an array of `{ station, heading }`. Trains are
  distributed round-robin across this list at start-up, and each entry acts
  as a **throttle point**: trains arriving or re-dispatching here must wait
  their scheduled slot. `heading` is `"forward"` or `"reverse"`, interpreted
  relative to the line's station order.
- `service_start`, `service_end` — `"HH:MM"`. Outside this window,
  dispatches are blocked.
- `schedule` — ordered array of `{ from, to, headway_min }` windows. Any
  point in time within service hours should be covered by exactly one window.

#### `[[sites]]` *(optional)*

Trackside energy sites — each co-located with a station and providing the
energy that the station's charging pads deliver to trains. A site has PV,
battery storage, and an optional grid tie. **Scenarios without any
`[[sites]]` run in "unlimited free charging" mode** (back-compat: the
simulator treats all charging as free energy).

```toml
[[sites]]
station = "east-depot"          # must match a station id with charging
pv_nameplate_kw = 5000          # solar nameplate (AC)
storage_capacity_kwh = 40000    # Na-ion/LFP battery size
storage_max_charge_kw = 10000   # battery inbound rate limit
storage_max_discharge_kw = 10000 # battery outbound rate limit
storage_initial_soc = 0.6       # optional; default 0.5
grid_import_kw = 3000           # 0 = no grid tie
grid_export_kw = 3000           # 0 = no export capability
```

**Energy flow per tick:**
1. **PV generation** — sinusoidal curve peaking at solar noon, integrated so
   the daily total equals `peak_sun_hours × pv_nameplate_kw` kWh.
2. **Storage charging** — PV goes into the battery first, rate-limited by
   `storage_max_charge_kw` and capped by remaining capacity.
3. **Excess PV** — goes to `grid_export_kw` if configured; otherwise
   curtailed (and reported as waste).
4. **Train charging** — draws from battery first (rate-limited by
   `storage_max_discharge_kw`); any shortfall pulled from `grid_import_kw`.

**PV sources not modeled in v1:** right-of-way vertical bifacial panels
and between-rail ("Sun-Ways-style") PV are treated as future extensions.
For now, allocate the ROW PV generation to nearby stations' `pv_nameplate_kw`
or to a dedicated depot site.

#### `[[faults]]` *(optional)*

Inject scheduled fault events to stress-test your network: dust storms that
cut PV output, grid outages that force sites into islanded operation,
charging-pad failures at specific stations. Useful for verifying that your
storage sizing survives the conditions RFC 0002 §5.4 calls out.

```toml
[[faults]]
name = "morning dust storm"
kind = "dust_event"
from = "07:00"
to   = "11:00"
day  = 1                       # optional, defaults to 1
pv_output_factor = 0.3         # 30% of normal PV → 70% loss

[[faults]]
name = "substation fire"
kind = "grid_outage"
from = "13:00"
to   = "16:00"
# station = "east-depot"       # omit for system-wide outage

[[faults]]
name = "AMU pad service"
kind = "charging_pad_outage"
from = "14:00"
to   = "18:00"
station = "al-muthanna-university"
```

**Fault kinds:**
- `dust_event` — scales PV output at affected sites. `pv_output_factor` is
  required (0.0 to 1.0). Omit `station` for a system-wide event.
- `grid_outage` — disables grid import and export at affected sites. Sites
  ride through on PV + storage. Omit `station` for a whole-grid failure.
- `charging_pad_outage` — disables a station's charging pad. Requires
  `station`. Trains dwelling there can't charge.

**Fault timing:**
- `from` and `to` are `"HH:MM"` on the specified `day` (1-based).
- `day = 1` means the first day of the sim; `day = 2` means the second, etc.
- Faults with windows entirely before sim start are silently skipped.

**Compositional behavior:**
- Multiple simultaneous dust events compose multiplicatively.
- The per-fault effects are independent: a dust event and a grid outage at
  the same site both apply.

At end of run, each fault that fired is listed in the `────── Faults ──────`
section of the summary. The per-site table shows the effects: sites with
blocked grid export show zero in the `grid→` column; sites with dust events
show reduced `PV kWh`.

## Common patterns

### A simple shuttle

See [`example-simple.toml`](example-simple.toml). Two terminals, one mid
stop, one train doing lazy back-and-forth.

### A proper metro line

Build it like Samawah's Line 1: ~10 stations, two terminals marked
`is_terminal = true`, a couple of mid-line `charging_power_kw = 500` pads,
a higher-power pad at each terminal.

### A ring

See line-2 in the built-in `samawah` scenario, or any auto-planned
megacity design at `designs/.../<City>/<slug>.toml` whose population
band carries a ring (e.g. Baghdad's line-9). Set `is_ring = true`
and `ring_wrap_length_m` to close the loop. Typical ring fleets
dispatch both clockwise and counterclockwise from 1–2 major
interchange stations.

### Multiple lines sharing interchanges

An interchange station is defined once and referenced by `id` in both lines'
`stations` arrays. In Samawah, Eastern Bridge and Al-Muthanna University
appear in both `line-1` and `line-2`.

## Troubleshooting

Validation errors are printed with the context of what went wrong. Common
ones:

- **"duplicate station id"** — the same `id` appears twice in `[[stations]]`.
- **"station '…' referenced by … is not defined"** — a line or fleet refers
  to an `id` you didn't declare.
- **"line '…' is a ring but missing ring_wrap_length_m"** — set the wrap
  distance.
- **"dispatch point station '…' is not on line '…'"** — the `station` in
  `dispatch_points` must be in the line's `stations` list.
- **"schedule window …–… has headway_min = 0"** — headways must be positive.
- **"site for station '…' has storage_initial_soc=X.Y; must be in [0.0, 1.0]"**
  — SoC is a 0–1 fraction, not a percentage.
- **"duplicate site for station '…'"** — each station may have at most one
  `[[sites]]` entry.
- **"unknown fault kind '…'"** — use `dust_event`, `grid_outage`, or
  `charging_pad_outage`.
- **"fault '…' (dust_event) requires pv_output_factor in [0.0, 1.0]"** —
  dust events must specify how much PV is lost (as a fraction, not a
  percentage).
- **"fault '…' (charging_pad_outage) requires a 'station'"** — pad outages
  must name the specific station.

## Contributing scenarios

If you develop a scenario for a real city you'd like to share, PRs to this
directory are welcome. Please include:

- A header comment naming the city and the design intent.
- A note on what data the alignment and station properties are based on
  (surveyed, desk study, or indicative).
- Expected ridership if you have it.

The goal is to build up a library of concrete urban rail designs that other
cities can learn from.
