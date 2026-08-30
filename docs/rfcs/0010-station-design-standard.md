# RFC 0010 — Station Design Standard

**Status:** Draft — planning only, no architectural drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0009 Track Design Standard](0009-track-design-standard.md)

## 1. Summary

OpenSourceRail commits to **six base station archetypes plus the
controlled `interchange-elevated` variant** covering every stop in every
deployment. The catalogue entries already exist as a
schema in
[`lib/templates/stations.toml`](../../lib/templates/stations.toml);
this RFC promotes them into a committed architectural envelope with
platform geometry, passenger-flow throughput, accessibility, fire
egress, and canopy-PV integration spelled out.

Station placement follows a light-metro spacing rule: ordinary
same-line stations target **1.6 km** spacing in the highest-demand centre,
with ordinary spacing widening to **3 km** in the wider urban area and up to
**7 km** on suburban approaches / the lowest-demand outer fringe. This is
selected from the demand raster rather than applied as a blanket suburban
spacing, unless a deployment explicitly selects a tram-like stop pattern. In city centres,
nearby cross-line platforms should be consolidated into one interchange
complex rather than emitted as separate station assets. The validation
gate uses a 600 m walkable transfer envelope for ordinary cross-line
approaches and a 600 m station-complex consolidation rule.

| Archetype | Platforms | Layout | Canopy | Charging | Dwell | Role |
|---|---|---|---|---|---|---|
| `halt` | 1 | side | solar-canopy | 250 kW | 60 s | rural / low-demand stop |
| `standard` | 2 | side | solar-canopy | 500 kW | 60 s | default urban / suburban |
| `major` | 2 | island | solar-canopy | 500 kW | 60 s | anchor stop (hospital / mall / centre) |
| `interchange` | 4 | same-grade transfer | solar-canopy | 500 kW | 60 s | two-line junction |
| `interchange-elevated` | 4 | stacked | solar-canopy | 500 kW | 60 s | elevated variant of `interchange` |
| `terminal` | 2 | side | solar-canopy | 1 000 kW | 60 s | end-of-line with turnback |
| `depot-terminal` | 2 | side | solar-canopy | 1 000 kW | 240 s | end-of-line + fleet depot |

Platform length is **not** fixed by the archetype — it is derived
at design-emission time from the line's rolling-stock choice:

```text
  platform_length_m = consist.length_m + station.platform_clearance_m
```

with `platform_clearance_m` defaulting to 6 m for `halt` and 10 m
elsewhere. This keeps archetypes consist-agnostic and prevents
drift between the rolling stock, the station, and the line plan.

## 2. Non-goals

- **Not a full architectural spec.** Column spacing, façade
  materials, HVAC layout, and wayfinding graphics are architect-
  of-record decisions per deployment. This RFC fixes the functional
  envelope the archetype must meet.
- **Not a fare-system spec.** `osr-afc` + `osr-tvm` handle the
  ticketing logic. This RFC specifies the *number* of gate lanes
  and TVMs per archetype, nothing about payment UX.
- **Not a passenger-experience spec.** Seat count per platform,
  vending machine placement, retail integration — operator
  choices.
- **Not an emergency-management plan.** Emergency egress calculation
  is specified; the incident response procedures that use those
  egress paths live in the operations rulebook (separate, per
  deployment).
- **Not a land-use spec.** Parking, bus-bay integration, TOD
  (transit-oriented development) are municipal planning work
  outside OSR's scope.

## 3. Why six base archetypes, not a continuum

A continuum of allowable station designs — pick your platform
length, pick your canopy, pick your fare gate count — fractures
the per-spare-part economics and the simulator validation. Six base
archetypes and one controlled elevation variant cover the real distribution of stops:

- `halt` for rural / low-demand points where a full station would
  over-build.
- `standard` is the bread-and-butter urban stop.
- `major` for generator stops (hospital, mall, transit square).
- `interchange` for where two OSR lines meet. The default is a
  same-grade transfer with direct pedestrian access; the controlled
  `interchange-elevated` variant lifts one line when geometry or
  road conflicts make that unavoidable (see [RFC 0011 §7](0011-civil-infrastructure-design-standard.md#7-stations-as-structures)).
- `terminal` for end-of-line with turnback tracks.
- `depot-terminal` for end-of-line + the fleet parking + the
  maintenance shop.

On the current generated Samawah model
([RFC 0003](0003-samawah-reference-deployment.md)), the station mix is
3 `halt`, 6 `standard`, 15 `major`, 5 `terminal`, 1
`depot-terminal`, and 3 `interchange-elevated` stops. The archetype
catalogue stays shared; each generated city only selects counts and
site adaptations.

## 4. Platform

### 4.1 Length

Derived, not fixed. For every consist/archetype pair:

| Consist (RFC 0008) | consist length | clearance | platform length |
|---|---|---|---|
| `urban-shuttle-1car` | 21 m | 6 m (halt) / 10 m (others) | 27 / 31 m |
| `tram-2car` | 39 m | 6 / 10 m | 45 / 49 m |
| `light-metro-3car` | 49.5 m | 6 / 10 m | 55.5 / 59.5 m |
| `metro-4car` | 75 m | 10 m | 85 m |
| `metro-6car` | 111 m | 10 m | 121 m |

### 4.2 Height

Defined by the rolling-stock family the line uses:

- Every OSR rolling-stock family uses the same **low-floor centre
  door zone** at 350 mm above top-of-rail (ToR), with raised floor
  over the standard bogies. For at-grade stations, the platform
  walking surface is set at the local pedestrian pavement level; the
  rail/top-of-rail datum sits 350 mm below that surface inside the
  drained guideway channel. In other words, the platform is flat with
  the street/sidewalk, while level boarding is kept by lowering the
  rail datum through the station bay rather than raising passengers
  onto a separate platform structure.
- Elevated or stacked stations keep the same 350 mm platform-to-ToR
  boarding datum, but those cases are the exception and are driven by
  alignment conflicts rather than the station archetype default.
  Gap-fillers are only needed on tight curved platforms where the
  horizontal gap exceeds the accessibility limit.

Mixed-consist lines are not supported (RFC 0008 §5 fixes one
family per line). A line that carries mixed heights is a safety
red flag rejected at design-emission time.

### 4.3 Width

| Archetype | Minimum usable width | Notes |
|---|---|---|
| `halt` | 2.5 m | Single-platform, assumes ≤ 5 boardings/min at peak. |
| `standard` (side) | 3.5 m per side platform | Per-platform; total station width with two side platforms + track = 3.5 + 1.435 + 3.5 = 8.4 m minimum. |
| `major` (island) | 6.0 m island platform | One platform serves both directions; drops footprint versus side-side. |
| `interchange` (same-grade transfer) | 4.5 m per platform | Transfer paths stay at pedestrian grade where the alignment permits. |
| `terminal` | 4.0 m per side platform | Accommodates peak alighting surge from inbound terminal runs. |
| `depot-terminal` | 4.0 m per side platform | Same as terminal. |

Minimum widths are derived from peak boarding flow at the
archetype's design pphpd plus egress (§6) and wheelchair circulation
(§7). Operators may go wider; below the minimum is rejected.

### 4.4 Edge treatment

- **Platform edge coping:** tactile paving 600 mm deep along the
  full platform edge per ISO 23599 (compliant with regional
  disability-access regulations).
- **Horizontal gap:** ≤ 75 mm between platform edge and vehicle
  sill at the consist's door — UIC 741 normal.
- **Vertical gap:** ≤ 50 mm between platform and sill — same.
- **Platform screen doors (PSD):** optional on every archetype,
  required on `metro-4car` and `metro-6car` from v1. Full-height
  PSDs preferred over half-height for environmental reasons (HVAC
  doesn't bleed to open-air). `osr-psd` ([crates/osr-psd](../../crates/osr-psd/))
  handles the controller.

## 5. Access and circulation

At-grade stations default to **direct pedestrian-level access**:
sidewalk / forecourt → fare line or validator plinth → platform, with
no lift, stair, ramp, or overbridge. A local ramp is only required where
the surrounding street itself has a level mismatch; it is not part of
the OSR standard station kit.

Grade-separated circulation is required only for elevated stations,
stacked transfer sites, or road/ROW constraints that a local authority
will not permit as a protected same-grade crossing:

| Mode | Capacity | When required |
|---|---|---|
| Direct paved path | Site-limited | Default for `halt`, `standard`, `major`, `terminal`, and `depot-terminal` when at grade. |
| Protected pedestrian crossing | ≤ 60 pax/min per 1.5 m width | Used when passengers must cross a track/road at pedestrian level; interlocked with the signalling system. |
| Ramp (max 1:20 preferred, 1:12 absolute max) | ≤ 60 pax/min per 1.5 m width | Local street/forecourt level mismatches only. |
| Stair | ≤ 80 pax/min per 1.5 m width | Elevated or stacked stations only. |
| Escalator (one-way, 0.5 m/s) | 100 pax/min per unit | Elevated/stacked `interchange`, `terminal`, or high-demand local overrides. |
| Elevator (≥ 1 100 × 1 400 mm car) | 10 pax/min per car | Elevated or stacked stations; not required for flat at-grade platforms. |

Total upward capacity at peak must exceed expected alighting
rate + 25 % reserve. The auto-gen emitter computes this at design
time.

## 6. Egress

Emergency egress capacity is fixed at **4 minutes** from the
furthest passenger on the platform to a safe point of discharge.
This matches NFPA 130 and the industry consensus for tunnel/station
design.

Minimum effective egress width per direction:

- `halt`: 1.0 m (one direction of travel only — the passenger
  exits to street level directly).
- `standard`: 2.0 m aggregate.
- `major`: 3.0 m aggregate.
- `interchange`: 4.0 m aggregate, redundant on each level.
- `terminal`: 3.0 m aggregate, with distinct primary + emergency
  routes.
- `depot-terminal`: same as terminal.

A single exit is never the only path. Even a `halt` must have two
evacuation directions — either two opposite-side street accesses
or a platform exit + a walk-path along the rail reserve.

## 7. Accessibility

All archetypes meet these minima (per the accessibility template
[`lib/templates/accessibility.toml`](../../lib/templates/accessibility.toml)):

- **Step-free path** from street to platform on every approach.
- **Tactile paving** at every platform edge, validator/fare-line
  approach, and stair/escalator landings where such vertical
  circulation exists.
- **Audio + visual** train-arrival announcements on every platform.
- **Seating** on every platform — `halt` excepted.
- **Wheelchair space** at 1 per 30 m of platform length; co-located
  with door-2 of every consist for quickest dwell.
- **Ticket gate accessibility:** at least one gate per direction
  is a wide wheelchair gate (≥ 900 mm).

## 8. Fare gates + TVMs

| Archetype | Fare-gate lanes per direction | TVMs per direction |
|---|---|---|
| `halt` | 0 (open) | 0 — buy via app / TVM at neighbouring standard station |
| `standard` | 2 | 1 |
| `major` | 3 | 2 |
| `interchange` | 4 (each level) | 2 per level |
| `terminal` | 3 | 2 |
| `depot-terminal` | 3 | 2 |

Gates are driven by [`osr-afc`](../../crates/osr-afc/); TVMs by
[`osr-tvm`](../../crates/osr-tvm/). At `halt` stations the line is
still revenue-positive because fare inspection happens on-board by
a roving inspector or via QR-scan-on-boarding
(GoA 4).

## 9. Canopy and solar

Every archetype carries a **solar canopy** over the platform — the
primary PV source the `osr-energy-site` controller dispatches from.
Site canopy/PV area targets from the template:

| Archetype | Canopy area |
|---|---|
| `halt` | 400 m² |
| `standard` | 1 800 m² |
| `major` | 2 000 m² |
| `interchange` | 2 800 m² |
| `interchange-elevated` | 3 200 m² |
| `terminal` | 2 400 m² |
| `depot-terminal` | 1 500 m² (smaller canopy — yard PV dominates) |

The area target is the total station-site shade/PV allowance. The
parametric passenger-platform canopy covers the circulation zone;
auxiliary forecourt or concourse modules close any difference to the
site target and must be listed separately in the station BOM.

The controlled auxiliary product is an **8.5 m × 22 m (187 m²)**
solar-roof bay derived from the reviewed station-spanning truss envelope.
Adjacent bays share 22 m transverse frames: `N` roof modules use `N + 1`
frames and `2 × (N + 1)` column foundations. The BOM rounds module count
up, so installed shade/PV area never falls below the template target.
Parametric review geometry and quantity functions live in
[`design/component-catalogue/src/osr_mech/station/auxiliary_canopy.py`](../../design/component-catalogue/src/osr_mech/station/auxiliary_canopy.py).

Canopy design envelope:

- **Prefabricated bolt-together steel portal frames.** No on-site
  welding, no wet concrete beyond pad footings. One standard 6 m
  bay module (HEA 200 column + HEA 180 cantilever rafter + SHS 100
  bracing) replicates along the platform. Hot-dip galvanised in the
  fabrication shop. Detailed parametric geometry at
  [`design/component-catalogue/src/osr_mech/station/portal.py`](../../design/component-catalogue/src/osr_mech/station/portal.py);
  FreeCAD/CAD-review artifacts under
  [`design/component-catalogue/catalog/`](../../design/component-catalogue/catalog/).
- **Solar-integrated roof sandwich panel.** One factory-bonded
  panel per bay: CIGS or lightweight c-Si PV on standing-seam
  galvanised steel, polyurethane foam core, white-coated underside.
  Delivered pre-terminated with MC4 connectors; bays plug into
  each other to form a single DC string. ~200 W/m², ~20 kg/m².
  See [`design/component-catalogue/src/osr_mech/station/solar_roof.py`](../../design/component-catalogue/src/osr_mech/station/solar_roof.py).
- **Cantilever-from-rear geometry.** Columns sit at the platform
  rear edge only (no columns at the platform edge); the rafter
  cantilevers 3.5 m + 0.7 m eave over the platform. Middle third
  of the platform is column-free for passenger circulation by
  construction, not by careful placement.
- **Roof: 1:15 mono-pitch (3.8°) toward the track shoulder.**
  Rainwater runs off directly onto the track drainage;
  integrated gutter only at the rear column face. In the dry
  target regions we do not bank on rain; the mono-pitch handles
  the occasional storm without integrated gutters at all.
- **Shading coefficient target: ≥ 90 % midday-summer coverage**
  of the platform.
- **No station building.** Fare gates on rolled-steel plinths at
  the platform entry; PIS / CCTV / lighting / radio mount to
  the canopy columns. The whole station is the canopy + the
  ground-level platform slab/guideway channel + the plinth — no
  masonry, no curtain wall, no on-site architecture.

Erection: the current `standard × light-metro-3car` parametric kit has
10 bays per platform. Each platform frame contains approximately 3.3 t
of steel before roof panels and services and fits within a normal
articulated-lorry payload. It is erected in 3–5 days with a small
crew and a 30 t crawler crane. No structural engineer is needed
on site — the deployment partner picks the kit size from the
catalogue; load envelopes are published in the source docstrings.

Canopy-PV sizing math lives in [RFC 0002](0002-energy-sizing.md);
`design/component-catalogue/src/osr_mech/station/canopy.py` exposes
`canopy_kwp(archetype, consist)` which `osr-energy-site` can
consume directly. One `standard × light-metro-3car` platform canopy
(10 bays) produces ~43 kWp; a two-side-platform station therefore has
about 86 kWp over its passenger platforms before auxiliary site PV.

## 10. Passenger-flow model

The auto-gen emitter computes expected peak passenger flow per
station using:

```
  boarding_per_hour = demand_at_station × population_capture_radius
                       × modal_share × peak_factor
```

with planning-grade defaults:

- `demand_at_station`: from the `osr-routing` raster (0..1 normalised).
- `population_capture_radius`: 500 m walking, 1 500 m bike+feeder bus.
- `modal_share`: 8 % of catchment population per day.
- `peak_factor`: 0.12 (peak hour share of all-day boardings).

Outputs per station:

- Expected peak boardings/minute.
- Required platform width (from §4.3) — must fit.
- Required vertical-circulation capacity (from §5) — must fit.
- Required egress capacity (from §6) — must fit.

Mismatch surfaces in `design-quality.yaml` as a hard gate, just
like station-spacing does today.

## 11. Thermal + environmental

- Outdoor stations (the common case in the target regions):
  passive cooling via canopy shade + cross-ventilation. No HVAC
  on the platform; just on enclosed spaces such as a TVM kiosk,
  staff room, or control cabinet where the operator chooses to add one.
- Underground stations (where the civil segment classifies as
  tunnel): mechanical ventilation required; emergency smoke
  extraction per NFPA 130; cooling by chiller or absorption unit
  fed from the depot-scale PV.
- Interior noise (outdoor platform): ≤ 80 dB(A) during train
  approach at 80 km/h per ISO 3095-1.
- Lighting: 100 lx on platform at night per EN 12464-2.

## 12. Self-consistency with RFC 0008 + 0009

The auto-gen pipeline enforces:

- `station.platform_length_m` = `consist.length_m + station.platform_clearance_m`
- `station.platform_to_tor_height_mm` = `consist.floor_height_mm`
- At-grade station walking surfaces remain at the local pedestrian
  datum; only the rail/guideway channel drops to satisfy the
  platform-to-ToR height.
- Every `interchange` archetype on line A also exists in line B's
  station list (otherwise the operator has two adjacent but
  disconnected stations, a common error).
- Every `terminal` archetype is at a line endpoint (not mid-line).
- Every `depot-terminal` sits at a line endpoint and is tagged
  `is_depot = true`.

Mismatch fails the `design-quality.yaml` hard gate.

## 13. Pitfalls and decisions

- **Level boarding is a hard requirement.** Some operators push
  back on the platform-height cost (either low-floor needs floor
  adaption on existing infrastructure, or high-floor needs taller
  platforms). We absorb that cost because level boarding is the
  single biggest accessibility win — it's not optional.
- **Solar canopy is mandatory on non-halt archetypes.** This is
  a project-wide bet, not a station-level choice. Operators who
  want to skip the canopy must fork the project; upstream keeps
  the bet.
- **Platform screen doors are optional below `metro-4car`.** PSDs
  are a top-quartile CAPEX line; for `tram-2car` and most
  `light-metro-3car` cases the simpler yellow-line + tactile
  edge is sufficient. Above that capacity, PSDs become
  mandatory — the risk/benefit crosses over.
- **No island platform at `standard`.** Island platforms halve
  platform width for equal footprint but require passengers to
  choose direction before descending, which slows wayfinding.
  We reserve them for `major` and above where the throughput
  win dominates.
- **Depot-terminal is a single archetype.** Some operators have
  depot-only facilities (freight, maintenance) separate from
  passenger terminals; those are out of scope — OSR deployments
  co-locate the two. This is a simplicity bet; a future
  depot-only archetype is opt-in.

## 14. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | Architectural envelope + canopy structural first-pass + accessibility + services + compliance matrix for the shared `standard` archetype at [`docs/stations/standard-archetype/`](../stations/standard-archetype/) (done 2026-04-22). Deployment station lists come from the generated city model before procurement. | RFC 0003 |
| **v2** ✅ | Emitter: terminal / interchange auto-detection + platform-length derivation from consist + depot-terminal promotion at the farthest radial endpoint (done 2026-04-22). **Architectural drawing register** for the `standard` archetype at [`docs/stations/standard-archetype/drawing-register.md`](../stations/standard-archetype/drawing-register.md) — 43 drawings across A/S/M/E/F/T disciplines with scale + size + v1-envelope cross-refs. Quality-gate failure on compatibility mismatch is deferred to v3. | v0, RFC 0008 v2, RFC 0009 v2 |
| **v3** ✅ | Parametric prefab catalogue landed at [`design/component-catalogue/`](../../design/component-catalogue/): platform and auxiliary canopy modules, solar-roof panels, ground-level slab/guideway-channel edge modules, elevated L-units, and separate fare/TVM plinths all resolve into generated BOMs and travelers. `STANDARD × light-metro-3car` emits a 10-bay / ~43 kWp canopy per platform plus seven 187 m² auxiliary bays. Tracked CAD review artifacts use compact FreeCAD/PNG outputs; local neutral exports can be generated when a partner toolchain needs them. | v1 |
| **v4** | Platform-flow simulator extension in `osr-sim` — peak-hour passenger flow against archetype capacity | v2 |
| **v5** | First-article station for a deployment instance | v1, RFC 0003 §5 |

## 15. Relationship to existing work

- [`lib/templates/stations.toml`](../../lib/templates/stations.toml) —
  the Lego-block schema this RFC ratifies.
- [`lib/templates/platform-doors.toml`](../../lib/templates/platform-doors.toml) —
  PSD calibration defaults.
- [`lib/templates/accessibility.toml`](../../lib/templates/accessibility.toml) —
  the accessibility envelope §7 references.
- [`crates/osr-design/src/emit.rs`](../../crates/osr-design/src/emit.rs) —
  already picks a station archetype (halt/standard/major) from
  demand thresholds. v2 adds terminal/interchange detection,
  per-archetype platform length, and the compatibility gate.
- [`crates/osr-psd`](../../crates/osr-psd/), [`crates/osr-afc`](../../crates/osr-afc/),
  [`crates/osr-tvm`](../../crates/osr-tvm/),
  [`crates/osr-pis-station`](../../crates/osr-pis-station/),
  [`crates/osr-station-scada`](../../crates/osr-station-scada/)
  — the station-side software already targets this envelope.

## 16. Open questions

1. **`interchange` at 3-line junctions.** Stacked 4-platform works
   for 2 lines crossing. A 3-line junction needs a different
   archetype; extend to `mega-interchange` when an actual
   deployment needs it.
2. **Outdoor air-quality filtering** for stations near heavy road
   traffic (common in target corridors). HEPA-grade canopies are
   a real market niche; candidate v4 addendum.
3. **Depot-terminal scaling.** For deployments with more than 20
   trainsets, the 1 500 m² canopy + yard footprint may
   under-serve. Introduce a `mega-depot` archetype at that
   threshold.
4. **Retail footprint.** Some operators depend on retail concessions
   for revenue. The `standard` archetype should accommodate ≈ 50 m²
   optional retail without redesign; confirm at v3.
5. **Overnight stabling** at `terminal` vs `depot-terminal`. The
   line's fleet parks overnight at the depot-terminal, not at a
   normal terminal. How does the auto-gen pipeline enforce this
   when the population distribution picks two terminals and no
   obvious depot site?

## 17. Done criteria

- [x] Six base archetypes plus the controlled elevated-interchange variant committed (§1)
- [x] Platform geometry envelope (§4) + access/circulation (§5) + egress (§6)
- [x] Accessibility minima (§7) + fare-gate sizing (§8) + canopy-PV sizing (§9)
- [x] Passenger-flow model (§10)
- [x] Self-consistency rules with RFC 0008/0009 (§12)
- [x] Pitfalls + alternatives explicit (§13)
- [x] Rollout ordered (§14)
- [x] Relationship to existing software + templates (§15)

The next session picks up at **v2 — emitter upgrade**, a shared
deliverable with RFC 0008 v2 and RFC 0009 v2 (same
[`emit.rs`](../../crates/osr-design/src/emit.rs) file).
