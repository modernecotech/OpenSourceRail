# RFC 0014 — Depot Design Standard

**Status:** Draft — planning only, no site drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0003 Samawah Reference Deployment](0003-samawah-reference-deployment.md), [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0010 Station Design Standard](0010-station-design-standard.md), [RFC 0011 Civil Infrastructure Design Standard](0011-civil-infrastructure-design-standard.md), [RFC 0013 Operations Rulebook](0013-operations-rulebook.md)

## 1. Summary

OpenSourceRail commits to **three depot archetypes** covering the
full range of deployment sizes. Every deployment has exactly one
**main depot** plus optional secondaries and layups. The main
depot co-locates with a `depot-terminal` station
([RFC 0010 §1](0010-station-design-standard.md#1-summary)).

| Archetype | Catalogue max stalls | Heavy maintenance | Overhaul throughput | Notes |
|---|---|---|---|---|
| `main-heavy` | 20 | Yes — overhaul bay, wheelset lathe | ≤ 40 trainsets | Larger deployments add a second `main-heavy` |
| `secondary-medium` | 12 | Light only — brake disc, door actuator, HVAC modules | — | Second depot on a long line |
| `layup-minimal` | 6 | None — overnight stabling only | — | Remote-terminal layup |

The **catalogue max** is the upper limit of the template default;
the **per-deployment stall count** comes from the §4 formula
(`stalls = ceil(fleet × 1.25)`). A Samawah-class 8-trainset line
lands on 10 stalls in its `main-heavy`, not 20 — the template's
20 is the ceiling, not the target.

Plus one optional type for edge cases:

| Archetype | Purpose |
|---|---|
| `training-wing` | Co-located driver-training simulators + classroom. Opt-in on `main-heavy`; not a standalone depot. |

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

## 3. Why three archetypes

Depots are where the simplicity bet pays off most. The three-
archetype set covers:

- **`main-heavy`** — the one non-negotiable facility per
  deployment, where heavy maintenance happens.
- **`secondary-medium`** — for deployments whose geography makes
  it uneconomic to depot-trip the entire fleet back to the main
  depot every night (long line, ≥ 30 km between termini).
- **`layup-minimal`** — for deployments that just need somewhere
  safe to park the fleet overnight at the opposite terminal.

No intermediate sizes, no bespoke main-heavy variants. A 30-stall
main-heavy is two `main-heavy` depots side-by-side (common in
megacity deployments) — not a bespoke 30-stall design.

## 4. Fleet-sizing formula

The depot stall count is parametric in the line's rolling-stock
fleet:

```text
  main_depot_stalls = ceil(fleet_on_line × 1.25)
  secondary_depot_stalls = ceil(fleet_remote × 1.25)
  total_fleet = peak_revenue_trainsets + 2 × (spare + cold_reserve)
```

- `peak_revenue_trainsets` = what the schedule requires at peak.
- `spare` = 1 trainset per 10 revenue trainsets, for planned
  maintenance rotation.
- `cold_reserve` = 1 per line, for unplanned incidents per
  [RFC 0013 §7](0013-operations-rulebook.md#7-incident-categorisation).

The 1.25× multiplier on stall count accounts for:
- One stall always occupied by a trainset in overhaul (bogie out,
  wheel lathe, body paint).
- One stall used for incoming-inspection (daily arrivals from
  revenue service).
- Growth headroom (15 %) for ridership uplift over the depot's
  20-year useful life without needing to build a second depot.

Example (Samawah reference):

- Line 1: 6 peak + 1 spare + 1 cold-reserve = 8 trainsets. Depot
  stalls = 10.
- Line 2: 4 peak + 1 spare + 1 cold-reserve = 6 trainsets.
  Layup-only at the Line 2 end-of-line; stalls = 5 in a
  `layup-minimal`.
- Total deployment: 14 trainsets, 1 `main-heavy` (Line 1 end),
  1 `layup-minimal` (Line 2 end). 10 + 5 = 15 stalls total.

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
- Sand / battery-electrolyte top-up (Na-ion additive kit every
  1 000 cycles).

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
- Battery bank: 2 MWh Na-ion (or LFP) to absorb PV surplus and
  feed trainset opportunity charging via depot-side 1 500 V DC
  charging rails.
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

- Functions: overnight stabling only. Trainsets drive in at end
  of service, sit overnight, drive out at morning service start.
  No inspection, no maintenance.
- Footprint: ~1 000 m² for 4 stalls.
- PV canopy: 600 m² → 90 kWp.
- Battery bank: optional 150 kWh for opportunity charging
  during dwell; the main-heavy is primary.
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
2. **Secondary depot:** for multi-line deployments where a
   second terminal is > 20 km from the main depot, emit a
   `secondary-medium` at that terminal.
3. **Layup-minimal:** for any other terminal on the fleet ≥ 6
   trainsets, emit a `layup-minimal` to avoid empty turnback
   drive-arounds.

Every depot writes a record into `design.toml`:

```toml
[[depots]]
id              = "line1-east-depot"
archetype       = "main-heavy"
at_station      = "samawah-line1-east"
fleet_stalls    = 10
pv_canopy_m2    = 4000
battery_kwh     = 2000
```

The simulator ([`osr-sim`](../../crates/osr-sim/)) reads these
and:

- Charges each trainset at depot pad power during overnight
  dwell.
- Rotates "on maintenance" flag across one stall per day.
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
- **Depot simulation in `osr-sim`.** The sim today models depots
  as "stations with high dwell + charging." RFC 0014 v3 adds a
  proper depot state (fleet stabled, fleet in-maintenance,
  fleet in-service) so the daily maintenance rotation is
  reflected in fleet-availability numbers.

## 10. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | [`designs/templates/depots.toml`](../../designs/templates/depots.toml) aligned with §§5–7 (PV canopy m², nominal kWp, battery kWh, workshop flags); §1 clarified "catalogue max" vs §4 formula (done 2026-04-22) | v0 |
| **v2** ✅ | Emitter picks depot archetypes (main-heavy at depot-terminal, layup-minimal at other terminals) + writes `[[depots]]` with `fleet_stalls` from the §4 formula (done 2026-04-22) | v0, RFC 0010 v2 |
| **v3** | `osr-sim` depot state machine (stabled / maint / service) | v2 |
| **v4** | Worked site plan for Samawah main-heavy (Line 1 east terminal) + layup-minimal (Line 2 furthest stop) | RFC 0003 §5, v3 |
| **v5** | Reference depot CAD under CERN-OHL-S v2 | v4 |

## 11. Relationship to existing work

- [`designs/templates/depots.toml`](../../designs/templates/depots.toml)
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
`designs/templates/depots.toml`** to match this RFC exactly.
