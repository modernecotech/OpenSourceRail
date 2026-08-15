# RFC 0014 — Depot Design Standard

**Status:** Draft — planning only, no site drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0010 Station Design Standard](0010-station-design-standard.md), [RFC 0011 Civil Infrastructure Design Standard](0011-civil-infrastructure-design-standard.md), [RFC 0013 Operations Rulebook](0013-operations-rulebook.md)

## 1. Summary

OpenSourceRail commits to **three depot archetypes** covering the
full range of deployment sizes. Every deployment has exactly one
**main depot** plus optional secondaries and layups. The main
depot co-locates with a `depot-terminal` station
([RFC 0010 §1](0010-station-design-standard.md#1-summary)).

The default operating pattern is **distributed overnight stabling**:
clean, telemetry-healthy trainsets may finish service at powered
passenger stations or layups near their first morning trip instead of
all running empty to a terminal depot. This reduces depot stall
requirements, avoids wasteful dead mileage, and lets first departures
begin across the line at the same time. The main-heavy remains the
maintenance authority; any red defect or scheduled heavy work routes
the trainset back to depot.

| Archetype | Catalogue max stalls | Heavy maintenance | Overhaul throughput | Notes |
|---|---|---|---|---|
| `main-heavy` | 20 | Yes — overhaul bay, wheelset lathe | ≤ 40 trainsets | Larger deployments add a second `main-heavy` |
| `secondary-medium` | 12 | Light only — brake disc, door actuator, HVAC modules | — | Second depot on a long line |
| `layup-minimal` | 6 | None — overnight stabling only | — | Remote-terminal layup |

The **catalogue max** is the upper limit of the template default;
the **per-deployment stall count** comes from the §4 formula
(`stalls = ceil(fleet × 1.25)`). An 8-trainset starter line
lands on 10 stalls in its `main-heavy`, not 20 - the template's
20 is the ceiling, not the target.

Plus one optional type for edge cases:

| Archetype | Purpose |
|---|---|
| `training-wing` | Co-located operations-training facility — OCC dispatcher-console simulators, maintenance-technician workshop mock-ups, and recovery-mode-crew briefing rooms. OSR is GoA 4 driverless ([RFC 0015](0015-driverless-operation.md)), so there are **no revenue-service drivers to train** — the wing exists for dispatchers, maintainers, station staff, and the recovery-mode crew who operate the manual-fallback joystick ([RFC 0015 §8.2](0015-driverless-operation.md#82-recovery-mode-cabinet)). Opt-in on `main-heavy`; not a standalone depot. |

**All depots are at-grade.** Per [RFC 0011 §1](0011-civil-infrastructure-design-standard.md#1-summary)
depots are never elevated — the footprint is too large to
economically put on viaduct. A deployment that can't site its
depot at-grade has an alignment problem, not a depot problem.

## 2. Non-goals

- **Not a workshop management system.** How the depot schedules
  its work — CMMS, parts management, labour planning — is owned
  by the operator and overlays with the `osr-cbm-backend` output.
- **Not an off-line overhaul facility.** Major overhauls (wheel
  reprofiling at 150 000 km, bogie overhaul at 600 000 km, body
  overhaul at 10 years) happen in the `main-heavy` depot's
  overhaul bay. Deployments without a main-heavy either
  contract overhaul out or depot-trip their fleet to a sister
  network.
- **Not a yard-design manual.** Track yard geometry within the
  depot boundary uses RFC 0009's `standard-urban` or (for large
  shunting yards) a depot-specific geometry variant. Detailed
  yard layout per facility.
- **Not an HR / workforce document.** Shift patterns and
  headcount from the ops rulebook (RFC 0013) and the workforce
  template.
- **Not a brownfield-rehabilitation scope.** Where a deployment
  inherits an existing rail workshop (Samawah, Khartoum-Atbara,
  Karachi Cantt, Maputo Machava, etc.), [RFC 0027](0027-brownfield-pilot-asset-recovery.md)
  governs the conversion of the existing site into an OSR depot.
  This RFC's archetypes are the **greenfield** envelope; the
  brownfield path swaps greenfield depot CAPEX ($10.0 M / $4.0 M / $0.6 M) for
  workshop rehabilitation (~$0.5–2 M building + $1–3 M new
  OSR-specific tooling) — an order-of-magnitude saving that the
  per-deployment plan should commit to whenever assets are real.

## 3. Why three archetypes

Depots are where the simplicity bet pays off most. The three-
archetype set covers:

- **`main-heavy`** — the one non-negotiable facility per
  deployment, where heavy maintenance happens.
- **`secondary-medium`** — for deployments whose geography makes
  defect and light-maintenance access to the main depot impractical.
- **`layup-minimal`** — an explicit exception only where a passenger
  station cannot provide secure powered stabling.

No intermediate sizes, no bespoke main-heavy variants. A 30-stall
main-heavy is two `main-heavy` depots side-by-side (common in
megacity deployments) — not a bespoke 30-stall design.

## 4. Fleet-sizing formula

The main depot is sized for concurrent maintenance and inspection, not one
parking stall per train. Healthy sets stable at powered passenger stations:

```text
  main_depot_workshop_bays = max(4, ceil(total_fleet × 0.15))
  secondary_depot_bays = site-specific exception
  service_rotation = 0  # depot service is prohibited in peak windows
  total_fleet = peak_revenue_trainsets + service_rotation + spare + cold_reserve
```

- `peak_revenue_trainsets` = what the schedule requires at peak.
  Sized from the physical round-trip cycle vs. the peak headway:

  ```text
    traversal_energy_kwh = line_length_km × cars × 2.4 × 1.25 × 1.10
    charging_dwell_s = ceil_30s(3600 × traversal_energy_kwh / sum(charger_kw))
    charging_dwell_s = clamp(charging_dwell_s, 120, 600)
    added_dwell_min  = charging_stops × max(charging_dwell_s / 60 - 1, 0)
    one_way_min      = (line_length_km / commercial_speed_kmh) × 60
    round_trip_min   = 2 × one_way_min + 2 × turnback_min + 2 × added_dwell_min
    peak_revenue_trainsets = ceil(round_trip_min × 1.10 / headway_min)
  ```

  v0.2 calibration: `commercial_speed = 35 km/h` (Tehran Line 1 33,
  Cairo Line 3 32, Tokyo Chuo Rapid 38 — the right band for 100 km/h
  max with roughly 1.5 km station spacing), `headway = 3 min`, `turnback =
  3 min` per end (driverless GoA 4 single-tail changeover, RFC 0015).
  Commercial speed carries a one-minute reference stop; the formula adds
  only the calculated charging dwell above that reference. The energy balance
  uses the maximum 25% climate uplift and a 10% charging margin. A final 10%
  cycle recovery allowance protects the published peak frequency.

- `spare` = 1 trainset per 10 revenue trainsets, for planned
  maintenance rotation.
- `cold_reserve` = 1 per line, for unplanned incidents per
  [RFC 0013 §7](0013-operations-rulebook.md#7-incident-categorisation).
- `service_rotation` = zero dedicated sets. Depot service is prohibited in
  the 3-minute peak windows and uses surplus peak-fleet capacity when the
  timetable relaxes to 6 or 12 minutes.

The 12-minute service happens at one designated service depot per line only
in lower-frequency windows. During 07:00–09:00 and 15:00–17:00, trains make
the normal quick terminal turnback, can use the platform connector, and may
deplete the battery further while the 20% section-entry reserve remains
mandatory.
Interior cleaning, exterior/running-gear walk-around, door, coupler and
emergency-equipment release checks, fault-log download, and a 150 kW low-C
recharge run concurrently. A red defect removes the set from rotation and
uses a planned spare; a clear inspection releases it straight back to
revenue service. The opposite terminal may still top up or stable a train,
but does not repeat the full inspection on the same round trip.

The 15% workshop concurrency allowance covers overhaul, defect repair,
incoming inspection, and planned maintenance. Growth beyond the 20-bay
catalogue envelope adds a second common `main-heavy`; it does not restore
fleet-wide depot parking.

Distributed overnight stabling does **not** increase the service-rotation
fleet. End-of-service dispatch assigns healthy trainsets to powered
stations with CCTV monitoring, remote isolation, and at least
150 kW low-C charging access. Morning dispatch releases those sets from
their stabled stations so outer stops do not wait for trains to run out
from the terminal depot. The main-heavy stall formula remains sized for
maintenance, inspection, overhaul, spares, and growth rather than for
parking every healthy set every night.

Example (current generated Samawah output, 3-min peak headway):

- The authoritative generated summary is
  [`designs/west-asia/Iraq/Samawah/README.md`](../../designs/west-asia/Iraq/Samawah/README.md).
- As of the current generated model: `line-1` is 25.6 km / 41
  trainsets, `line-2` is 21.8 km / 36 trainsets, and `line-3` is
  11.0 km / 19 trainsets, for 96 total 3-car trainsets: 86 peak,
  no dedicated depot-service rotation, 7 planned spares, and 3 cold reserves.
- `design.toml` emits the depot archetype, terminal assignment, and
`fleet_stalls` as workshop/inspection bays from the same run. Older 1.25×
fleet-parking examples and hand-calculated 6/4/8
  trainset examples were removed from the docs and must not be copied
  into current deployment documents.

The emitter (RFC 0014 v2) computes this from the design.toml's
`fleet_sizing` block.

## 5. `main-heavy` envelope

### 5.1 Functions

- Overnight stabling of the primary fleet (stall count per §4).
- Daily inspection of every incoming trainset.
- Weekly inspection (7-day service).
- 30-day inspection (A-class service per EN 50126).
- Light repair (door actuator, HVAC module, brake-disc
  replacement, battery module swap).
- Heavy overhaul: bogie swap, wheel reprofiling on depot lathe,
  body-work repaint.
- Wash: automated two-pass wash track.
- Battery-module inspection, coolant service, and sealed-module exchange.

### 5.2 Physical layout

| Area | Target footprint (per consist bay) |
|---|---|
| Stabling track | 1× consist length + 5 m clearance at each end |
| Daily-inspection bay | Roofed, pit-equipped, overhead power, compressed air, data sync drop (TCN-E monitoring) |
| Weekly bay | Pit + roof walkway for upper-body access |
| Overhaul bay | Pit + overhead crane (40 t) + wheel-lathe trench |
| Wash track | Two-pass automatic with water recycling |
| PV canopy | Over stabling + inspection tracks; 4 000 m² target for an 8-stall main-heavy |
| Classroom + office | ≥ 200 m² for operators + trainers |
| Stores | ≥ 600 m² with rack storage for spare modules |

Total `main-heavy` footprint: ~5 000 m² gross for a 10-stall
facility, ~8 000 m² for a 20-stall.

### 5.3 Energy

- PV canopy as above. 10-stall main-heavy → 4 000 m² PV → 600 kWp
  nominal → 3.2 GWh / year (Samawah climate).
- Battery bank: repeated 500 kWh stationary LFP modules, sized by the depot
  timetable and energy study, feeding the RFC 0021 500 kW DC charging modules.
- Grid tie: export surplus at off-peak; import during overcast
  weeks. Per [RFC 0002](0002-energy-sizing.md).
- Every depot is a full `osr-energy-site` instance.

### 5.4 Signalling

- A single W-SBC plus an interlocking zone boundary at the depot
  entry.
- Inside the depot, speed limit 15 km/h, manual operation under
  mode M3 ([RFC 0013 §5](0013-operations-rulebook.md#5-degraded-mode-operations--the-important-part)).
- Shunting signals at each stall entry — mechanical dwarf signals
  driven by `osr-wayside-points` extensions.
- No ATP envelope inside the depot; `osr-atp` disables below
  15 km/h in depot-tagged geofence, per a safety-bounded
  configuration. The operational safety envelope inside the
  depot is line-of-sight + hand-signal coordination.

### 5.5 Access

- Personnel access: turnstile-gated with ID-card entry, separate
  from the fleet access.
- Fleet access: one track connection to the line, TPS-style
  merge per [RFC 0012 §4.3](0012-switches-and-crossings.md#43-facing-vs-trailing)
  (trains go in — it's a trailing move).
- Road access: for parts delivery, emergency services, depot
  staff parking. Minimum one 4 m-wide road connection.
- Rail access for deliveries of new trainsets is via the same
  line connection (new rolling stock rolls in on its own wheels).

## 6. `secondary-medium` envelope

- Functions: overnight stabling for ≤ 16 trainsets, daily
  inspection, weekly inspection, light module swap.
- **No overhaul bay. No wheel lathe. No bogie-lift.** Anything
  heavier is trips back to the main-heavy.
- Footprint: ~2 500 m² for 8 stalls.
- PV canopy: 1 500 m² → 225 kWp nominal.
- Battery bank: 500 kWh.
- Signalling: same as main-heavy but smaller zone.
- Classroom: none. Reuse the nearest `major` station's
  community room if needed.

## 7. `layup-minimal` envelope

- Functions: overnight stabling, low-C top-up, cleaning, and a ground-level
  safety-release walk-around. Trainsets drive in at end of service, can pass
  through the same 12-minute turnaround service if the site is designated
  for its line, sit overnight, and drive out at morning service start. There
  is no pit inspection, repair work, or heavy maintenance.
- Footprint: ~1 000 m² for 4 stalls.
- PV canopy: 600 m² → 90 kWp.
- Battery bank: optional 150 kWh for opportunity charging
  during dwell; the main-heavy is primary.
- Train top-up: 150 kW low-C per occupied stabling road, used while a set is
  held between duties and overnight; passenger-platform fast charging remains
  a separate terminal function.
- Signalling: single W-SBC at the layup entry; rest is manual
  line-of-sight.
- No personnel on-site overnight; the OCC monitors via CCTV.

## 8. Integration with the auto-gen pipeline

Today's emitter picks one `depot-terminal` archetype ([`crates/osr-design/src/emit.rs`](../../crates/osr-design/src/emit.rs),
`compute_archetypes`, priority rule). That choice is where the
main-heavy sits. v2 of the emitter extends this:

1. **Main depot:** co-located with the longest radial line's far
   terminal. The station archetype is `depot-terminal`; the
   depot archetype is `main-heavy`.
2. **Powered station stabling:** every other terminal and selected intermediate
   powered stations receive healthy sets overnight; they do not emit depots.
3. **Secondary/layup exception:** emit only after a site-specific security,
   utility, access, or defect-recovery study shows station stabling is not viable.

Every depot writes a record into `design.toml`:

```toml
[[depots]]
id              = "line1-east-depot"
archetype       = "main-heavy"
at_station      = "line-a-east"
fleet_stalls    = 10
pv_canopy_m2    = 4000
battery_kwh     = 2000
```

The simulator ([`osr-sim`](../../crates/osr-sim/)) reads the depot
records today and the distributed-stabling extension must preserve
these behaviours:

- Charges each trainset at depot pad power while held and overnight.
- Treat powered passenger stations and layups as valid overnight stabling
  points when the distributed-stabling policy is enabled in
  [`lib/templates/depots.toml`](../../lib/templates/depots.toml).
- Holds a returning train for the configured clean/inspect/recharge slot at
  one designated depot per line and emits service-start/service-complete
  evidence.
- Sizes and dispatches the explicit service-rotation fleet separately from
  planned spares and cold reserve.
- Feeds the depot battery bank into the network-wide energy
  balance.

## 9. Pitfalls and decisions

- **At-grade only, per RFC 0011.** Depots are large; elevating
  the footprint is prohibitively expensive. The auto-gen
  emitter rejects depot siting on an elevated section.
- **One reference `main-heavy` everywhere.** Operators with
  unique geography (coastal, mountainside) will push for
  bespoke depots. The upstream catalogue stays at one shape;
  the deployment's civil team handles the site-specific
  adaptation.
- **Wheel lathe at the main-heavy only.** Decentralising lathes
  is tempting (saves depot-trip time) but the operator depth for
  wheel-reprofiling is thin in target regions; centralising at
  one site lets that thin team do all the work.
- **No pit at `layup-minimal`.** A pit adds cost, safety
  maintenance, and lighting — just for overnight parking. Skip.
- **Depot simulation in `osr-sim`.** The sim models depot top-up while held
  plus an explicit service countdown at the designated depot. Cleaning,
  release inspection, diagnostics, and recharge are concurrent; deeper
  maintenance remains a separate availability/CMMS model.
- **Distributed stabling is not distributed maintenance.** Overnight
  passenger-station stabling is allowed only for healthy sets with remote
  isolation and CCTV. Any trainset needing inspection beyond the daily
  release walk-around, fault rectification, wheel work, or battery-module
  exchange goes to the main-heavy.

## 10. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | [`lib/templates/depots.toml`](../../lib/templates/depots.toml) aligned with §§5–7 (PV canopy m², nominal kWp, battery kWh, workshop flags); §1 clarified "catalogue max" vs §4 formula (done 2026-04-22) | v0 |
| **v2** ✅ | Emitter picks depot archetypes (main-heavy at depot-terminal, layup-minimal at other terminals) + writes `[[depots]]` with `fleet_stalls` from the §4 formula (done 2026-04-22) | v0, RFC 0010 v2 |
| **v3** ✅ | `osr-sim` turnaround-service state (clean / inspect / diagnostics / recharge), explicit service-rotation fleet and event evidence (done 2026-08-12) | v2 |
| **v4** | Generated site plan for the current Samawah depot and layup set from `designs/west-asia/Iraq/Samawah/design.toml` | RFC 0003 §5, v3 |
| **v5** | Reference depot CAD under CERN-OHL-S v2 | v4 |

## 11. Relationship to existing work

- [`lib/templates/depots.toml`](../../lib/templates/depots.toml)
  — schema this RFC ratifies.
- [`crates/osr-design/src/emit.rs`](../../crates/osr-design/src/emit.rs)
  — auto-gen emitter. `depot-terminal` detection today; the
  `[[depots]]` block emission is v2.
- [`crates/osr-energy-site`](../../crates/osr-energy-site/) —
  every depot is one `osr-energy-site` instance; existing
  integration holds.
- [`crates/osr-sim`](../../crates/osr-sim/) — modest extension
  for v3; charging semantics already work.
- [RFC 0010](0010-station-design-standard.md) `depot-terminal`
  archetype pairs 1:1 with this RFC's `main-heavy` or a mix of
  main-heavy + layup.

## 12. Open questions

1. **Co-located vs detached training wing.** Some operators
   prefer the training simulator in a quiet city building
   (closer to drivers' homes). The catalogue default is co-
   located with the main depot; per-deployment override.
2. **Decentralised battery swapping.** A future opt-in where
   trainsets exchange their battery pack at depot instead of
   recharging — halves the charging-pad occupancy. Out of
   scope upstream until battery-swap mechanical designs mature.
3. **Night-shift head count.** Ops rulebook §4.5 (RFC 0013)
   fixes the shift structure; what's the minimum overnight
   staff headcount at a `layup-minimal`? Currently zero
   (CCTV-monitored); confirm when the first `layup-minimal`
   deploys.
4. **Depot expansion path.** A `secondary-medium` that outgrows
   its 8 stalls — does it upgrade to `main-heavy` in place, or
   is a second-depot-nearby preferred? Likely the latter given
   construction-on-live-facility complexity.

## 13. Done criteria

- [x] Three archetypes committed (§1)
- [x] Fleet-sizing formula (§4)
- [x] Main-heavy envelope (§5) + secondary-medium (§6) + layup-minimal (§7)
- [x] Auto-gen pipeline integration (§8)
- [x] Pitfalls (§9)
- [x] Rollout ordered (§10)
- [x] Relationship to existing software + templates (§11)

The next session picks up at **v1 — amend
`lib/templates/depots.toml`** to match this RFC exactly.
