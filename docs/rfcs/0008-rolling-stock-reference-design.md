# RFC 0008 — Baseline Rolling-Stock Reference Design

**Status:** Draft — planning only, no mechanical drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0003 Samawah Reference Deployment](0003-samawah-reference-deployment.md), [RFC 0007 Hardware Reference Designs](0007-hardware-reference-designs.md)

## 1. Summary

OpenSourceRail commits to **one modular train architecture** scaled
into five rolling-stock families — one per
ridership band — from which every deployment picks exactly one per
line. No bespoke consists; every country that adopts the stack
chooses the closest family and builds to that drawing. This RFC
fixes the engineering envelope (dimensions, masses, axle
arrangement, bogie and brake architecture, cab, crashworthiness,
fire, thermal, acoustic) for each family.

The families are named in
[`lib/templates/rolling-stock.toml`](../../lib/templates/rolling-stock.toml).
This RFC promotes that schema into a committed engineering envelope.

Each car is a self-contained driverless unit: one powered bogie,
one trailer bogie, under-seat sodium-ion battery, low-floor centre
boarding zone, and its own onboard control stack. Multi-car consists
repeat that module rather than introducing a different traction
architecture.

| Family | Cars | Length | Tare | Seats | AW2 nominal capacity | AW3 crush capacity | Peak ridership band (pphpd) | Onboard battery | Max speed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `urban-shuttle-1car` | 1 | 21 m | 34 t | 20 | 75 | 95 | < 2 500 | 120 kWh | 19 m/s (70 km/h) |
| `tram-2car` | 2 | 39 m | 68 t | 40 | 160 | 210 | < 5 000 | 240 kWh | 19 m/s (70 km/h) |
| `light-metro-3car` | 3 | 51 m | 102 t | 60 | 240 | 320 | 5 000–10 000 | 360 kWh | 25 m/s (90 km/h) — **Samawah reference** |
| `metro-4car` | 4 | 75 m | 136 t | 80 | 320 | 430 | 10 000–20 000 | 480 kWh | 25 m/s (90 km/h) |
| `metro-6car` | 6 | 111 m | 204 t | 120 | 480 | 640 | 20 000–35 000 | 720 kWh | 28 m/s (100 km/h) |

Pphpd = passengers per hour per direction at peak, planning-grade.
AW2 is the normal peak planning load used for capacity and farebox
calculations. AW3 is a short-duration crush-load reference for
structure, suspension, braking, and emergency-egress checks.

## 2. Non-goals

- **Not a bill of materials.** This RFC fixes the envelope; the BOM
  for a specific family is v2 output of the hardware working group.
- **Not a homologation pack.** EN 14363 dynamic tests, EN 15227
  crashworthiness, EN 45545 fire, ISO 3095 noise, EN 12299 comfort —
  every family will need type-approval evidence for a specific
  deployment. This RFC states the design targets; the evidence
  campaigns happen per-deployment.
- **Not intercity or freight.** Explicitly out of scope per
  [ARCHITECTURE.md §1](../ARCHITECTURE.md#1-mission).
  The four families span low-pphpd tram up to large metro trunk;
  regional / HSR / freight is a different problem.
- **Not a standards body.** We reference EN / IEC / UIC / ISO
  standards; we do not publish new ones.
- **Not a customisation catalogue.** Interior colour, seat fabric,
  route-branded livery are a per-deployment choice. This RFC fixes
  the structural and electrical architecture only. Vendor choice
  for the COTS interior equipment (windows, HVAC, lighting, PIS
  screens, seats, grab poles, intercom) is documented separately
  as an envelope-reservation cookbook in
  [`hardware/trainset-interiors/cots-catalogue.md`](../../hardware/trainset-interiors/cots-catalogue.md)
  — the car body reserves the volume + bolt pattern + power
  budget; the specific vendor is interchangeable per deployment.

## 3. Unified architecture — every family

Five rolling-stock families, but **one architecture** across all of
them. The scaling is car count, platform length, and capacity; the
architectural decisions below are shared. Commonality is the bet:
one spares pool, one maintainer-training syllabus, one CAD reuse,
one supplier-qualification set.

### 3.1 Mechanical

| Aspect | Choice | Rationale |
|---|---|---|
| Car body | Welded carbon-steel underframe + light spaceframe, with bonded/bolted composite side and roof panels | Keeps the primary structure to cut/bend/weld operations available in ordinary rolling-stock, bus, truck, and ship repair shops. Composite panels carry weather, aerodynamics, insulation, and finish, not crash loads. |
| Suspension | Chevron rubber-metal primary; twin-bellows air-spring secondary with pneumatic levelling valves rated 55 °C continuous | Per [RFC 0022 §5](0022-bogie-traction-drive.md#5-suspension). Chevron primary eliminates hydraulic-damper creep failure at 50 °C ambient; twin-bellows air-spring secondary holds the door-zone floor within ± 5 mm across empty-to-AW3. |
| Wheel | Monobloc, 760 mm new / 680 mm worn | Per [RFC 0022 §3](0022-bogie-traction-drive.md#3-reference-dimensions) — widest global wheel-forging catalogue (Lucchini, Valdunes, CAF, plus tier-2 vendors per RFC 0022 §10). 40 mm re-profiling budget over life on depot lathe. |
| Gauge | 1 435 mm standard gauge | Single upstream gauge keeps wheelsets, switches, platform offsets, spares, and FEA envelopes common across the reference families. See [RFC 0009 §4](0009-track-design-standard.md#4-gauge). |
| Wheel–rail profile pairing | S1002 wheel on UIC60 rail | Standard off-the-shelf profiles; no proprietary geometry. |
| Couplers | Scharfenberg Type 10 automatic + e-coupler for 24 V / CAN-FD / Ethernet | Standard metro coupler; allows rescue of a failed train by any neighbour consist in the fleet. **Brownfield deployments**: SA-3 (Soviet automatic) + screw/buffer couplers from recovered legacy stock are explicitly NOT retrofitted onto OSR consists — see [RFC 0027 §5.3](0027-brownfield-pilot-asset-recovery.md). Recovered SA-3 drawgear goes to the resale stream. |
| Articulation | Semi-permanent couplers between self-contained cars; no Jacobs bogies | Keeps every car removable with its own two standard bogies, battery, traction, doors, BMS, and control equipment. |
| Axle load | ≤ 14 t loaded (AW3 crush) | Well inside a 22.5 t UIC mainline limit — lets the catenary-free metros share minor infrastructure with legacy rail where needed without overstressing bridges. |
| Bogies | Two 2-axle pivoting bogies per self-contained car: one powered bogie, one trailer bogie. Both use the same frame, suspension, wheelset, brake, and pivot; the trailer omits motors and gearbox. See [RFC 0022](0022-bogie-traction-drive.md) for the single-SKU design. | One powered bogie per car keeps the drivetrain simple while retaining enough adhesion for 1 km stop spacing and urban gradients. |
| Traction | Axle-hung PMSM + single-stage parallel spur gearbox, 6.5 : 1. 180 kW continuous / 320 kW peak per axle. Per-family motorisation pattern in [RFC 0022 §8](0022-bogie-traction-drive.md#8-motorisation-pattern-per-family). | Wheel-hub direct-drive was evaluated and rejected — spares pipeline is too thin. Axle-hung is the Mireo / Urbos / Coradia sweet spot. |
| Crashworthiness | EN 15227 Cat C-II (medium urban) for all families | Addresses metro-to-metro and metro-to-obstacle collisions at up to 25 km/h. Energy absorbers at cab ends + at each articulation; anti-climbing features. |

### 3.2 Propulsion + auxiliary

| Aspect | Choice | Rationale |
|---|---|---|
| Traction motor | Permanent-magnet synchronous, axle-mounted, one per powered wheelset | PMSM efficiency ≥ 96 % at peak. Axle-mount removes gearboxes from every powered bogie, eliminating one of the top maintenance line items. |
| Inverter | 3-phase, silicon-carbide (SiC) MOSFETs, ≥ 98 % efficiency at peak | SiC is commodity-grade in 2026. Water-cooled cold plate, no fans. One inverter per powered bogie. |
| Powered wheelsets | 50 % of each car's wheelsets: one powered bogie and one trailer bogie per car | The traction module is identical on every car; larger consists add complete modules instead of new motorisation patterns. |
| Battery | Sodium-ion primary, LFP alternative (RFC 0021 §3). Both chemistries fit the same strake envelope | Na-ion avoids lithium-chain geopolitics and runs hotter; LFP is the drop-in where Na-ion isn't locally serviceable yet. |
| Battery pack topology | Under-seat sodium-ion modules below the longitudinal benches, split into two contactor-isolated strings per car | Keeps the centre aisle and low-floor door zone clear, puts mass low, and lets maintenance lift modules from inside the saloon. |
| Battery size | 120 kWh usable per car, scaled by car count (RFC 0021 §4) | Sized for roughly one route length plus reserve, not for a full day. Normal service energy is replenished by station charging. |
| Charging | Automated conductive station charging at normal passenger stops, buffered by station solar PV + stationary battery. Typical stop spacing is ~1 km and nominal charging dwell is ~60 s. Depots still provide overnight / maintenance charging. **No continuous catenary.** | The train carries only enough battery to bridge the route and station failures, keeping vehicle mass and cost down. |
| Regen | Default on; friction brake blends in below 8 km/h | Matches [`osr-brake`](../../crates/osr-brake/)'s WSP + regen-priority arbitration. |
| Friction brake | Disc brake on every trailing axle, electromagnetic actuation | No pneumatic brake system — removes the compressor-maintenance line item entirely. Electric brake is continuously self-monitoring via `osr-brake`'s WSP + pressure sense loops. |
| Emergency brake | Same discs, different current source (ultra-cap + battery fallback); independent of regen | SIL-4: emergency-brake current cannot fail with any single electronics failure. Tested on every ignition cycle by the `osr-vigilance` start-up check. |
| Aux inverter | 400 V 3-phase AC, 24 V DC, 110 V DC outputs | Runs HVAC, lighting, compressors (if any — per-deployment choice), PIS, comms. `osr-aux-power` drives it. |

### 3.3 Interior

| Aspect | Choice | Rationale |
|---|---|---|
| Floor | Low-floor centre section at the large door zone, with raised floor over the two standard bogies | Gives level boarding where passengers move while avoiding exotic low-floor bogies. |
| Door count | 1 large centre double-door pair per car side on every 17 m self-contained car | The default 1 km stop pattern favours wide, simple openings over many narrow doors. Capacity scales by adding identical cars, not changing the door pattern. |
| Door clearance | 1 250 mm wide × 2 000 mm tall opening | Wheelchair + stroller compatible. |
| Seating | Longitudinal bench seating, ≥ 15 % seats priority (elderly, pregnant, wheelchair companion) | Standing-heavy mix maximises peak capacity; matches the pphpd planning band. |
| Wheelchair spaces | 2 per car (4 per `tram-2car`, 6 per `light-metro-3car`, 8 per `metro-4car`, 12 per `metro-6car`) | Per accessibility template ([`lib/templates/accessibility.toml`](../../lib/templates/accessibility.toml)). |
| HVAC | Design ambient +50 °C (all families) | Matches the Samawah reference envelope and most target-region summers. Dehumidifier + evaporator + reversible heat pump — no resistive heating. Sized per `osr-hvac`'s 25 % hot-climate uplift rule. |
| Fire safety | EN 45545-2 HL2 R1 for body, R7 for seats, R1 for cable | HL2 is the hazard level for metro; R1/R7 are the tests for rigid surfaces and upholstery respectively. |
| Lighting | LED, 300 lx average, with sunset/sunrise dimming | Cut from `osr-lighting`'s evaluator. |

### 3.4 Nose + obstacle-detection (replaces driver cab)

**Per [RFC 0015](0015-driverless-operation.md) every trainset
ships as a GoA 4 (Unattended) system from day one.** There is
no driver cab, no DMI, no master controller, no dead-man
handle. Both ends of the trainset are symmetric; there is no
"leading / trailing" distinction at the rolling-stock level.

| Aspect | Choice | Rationale |
|---|---|---|
| GoA level | **GoA 4 default (RFC 0015).** GoA 2 retrofit possible via the `goa2-cab` feature flag, but not the shipped default for new deployments. | Removes driver capex + driver rostering; eliminates the densest section of RFC 0013 |
| Nose geometry | **Segmented panoramic glass-pane end + sensor cowl + coupler, no cab door.** Cars are symmetric end-to-end; passenger floor extends to the full car length. | ~14 extra seats per `light-metro-3car` consist; ~$150 k + ~2.3 t saved vs. a cabbed reference |
| Obstacle-detection sensor suite | 4× ultrasonic (close-range safety, 0.2–20 m) + solid-state LIDAR (5–200 m, Livox-class) + mmWave radar (5–200 m, all-weather) + stereo camera pair (classifier only). Hosted on the dedicated T-OBS ECU (RFC 0007 §5.5). | Replaces the driver's eyes. Multi-physics architecture so no single sensor failure produces a `Clear` verdict |
| Passenger emergency intercom | ≥ 4 per car (one per car-end, both doors). Press opens audio+video to OCC remote-assist and commands a controlled brake to the next station. | Replaces the cab's emergency plunger at the passenger interface |
| Recovery-mode cabinet | Steel-locked enclosure behind each nose. Keyswitch + wired pendant: forward/reverse, 0–15 km/h throttle, emergency stop. | The *only* manual-control path. Physical, locked, slow-speed — not a full cab |
| Cameras | Forward-view × 2 (nose cowl, part of the sensor suite) + door-sill (one per door) + cabin × 4 per car, all live to OCC | Replaces driver supervision of the cabin; informs OCC remote-assist + fleet-health operators |

### 3.5 Thermal + acoustic

| Aspect | Target |
|---|---|
| Ambient operating range | −25 … +50 °C (all families) |
| Interior noise at 60 km/h | ≤ 74 dB(A) per ISO 3095-2 |
| External noise at 60 km/h, 7.5 m | ≤ 80 dB(A) per ISO 3095-1 |
| Ride comfort (N_MV) | ≤ 2 (good) per EN 12299 |

## 4. Self-consistency with track and station

Every rolling-stock choice below must be compatible with the
track-geometry preset ([RFC 0009](0009-track-design-standard.md))
and the station archetype
([RFC 0010](0010-station-design-standard.md)). The auto-gen
pipeline enforces this via a compatibility matrix:

- Rolling stock → track: `compatible_consists` in
  [`lib/templates/track-geometry.toml`](../../lib/templates/track-geometry.toml).
- Rolling stock → station: platform length = `consist.length_m + station.platform_clearance_m`.
- Rolling stock → line length: pack covers one route length plus
  reserve, while the operations plan must prove station-charging
  energy balance for the normal timetable.

The v2 emitter (RFC 0008 §7 milestone) validates all three
constraints and fails the build on mismatch.

## 5. Family selection policy

The auto-gen pipeline picks a family per line using population and
a simple ridership model:

```text
   population band (city)     pphpd target         chosen family
   ────────────────────────   ───────────────      ───────────────
   ≤ 150 k                    ≤  1 800             urban-shuttle-1car
   150 k … 300 k              ≤  4 000             tram-2car
   300 k … 1 M                ≤  7 000             light-metro-3car
   1 M … 3 M                  ≤ 10 000             metro-4car
   ≥ 3 M                      ≤ 15 000             metro-6car
```

Pphpd is estimated from population × 0.012 × peak-factor 0.08,
then checked against AW2 capacity at short automated headways
(roughly 2–3 min for dense trunks, looser off-peak). The pipeline
writes the choice into `design.toml` under `[[lines]]
rolling_stock = "<family>"`.

## 6. Pitfalls and decisions

- **Na-ion primary, LFP as the drop-in alternative**
  ([RFC 0021 §1](0021-battery-traction.md#1-summary)). Na-ion
  has a shallower cycle life today (~3 000 cycles at 100 % DoD vs
  LFP's ~6 000) — we accept that trade because Na-ion avoids
  locking a country into lithium-chain geopolitics. LFP is the
  drop-in for operators with established LFP spares. The side-
  wall strake envelope accepts either chemistry without car-body
  changes.
- **No pneumatic brake.** A pneumatic brake + air reservoir is the
  rail industry's reference design; we replace it with
  electromagnetic disc + battery-backed ultra-cap. The winner is a
  ~40 % maintenance-line-item reduction on trainsets. The risk is
  EN 14198 compliance for the electric brake; the safety case
  carries `osr-brake`'s Kani + proptest evidence.
- **Low-floor centre, standard bogies.** Full low-floor bogies
  would make the drivetrain and wheelset catalogue more exotic.
  OSR keeps standard bogies at the ends and puts the large
  accessible boarding zone between them.
- **PMSM over induction.** Induction motors are more forgiving of
  field weakening errors and have no rare-earth magnet supply
  concerns. We pick PMSM for the 5-point efficiency advantage, then
  mitigate supply risk with ferrite-assisted PMSM designs (no
  heavy rare earths) being the target v2.
- **SiC over Si IGBTs.** SiC is ~2.5× the die cost of silicon for
  equivalent rating in 2026, but dissipates ~30 % less power —
  letting us shrink the heatsink and water-cooling loop to
  conduction-cooled. Net BOM flat, net mass down, net reliability
  up. This was a close call; revisit in v2.
- **No catenary, period.** Catenary-free is a project invariant;
  the battery sizing in §3.2 is a consequence. This is the single
  most controversial decision — mainstream rail vendors will push
  back. The counter is the CAPEX math in
  [ARCHITECTURE §4 D7](../ARCHITECTURE.md#4-architectural-bets)
  plus the copper-theft track record in target regions.

## 7. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | Shop-drawing package + procurement BOM skeleton for `light-metro-3car` at [`docs/rolling-stock/light-metro-3car/`](../rolling-stock/light-metro-3car/) — general arrangement, bogie, body, traction, interfaces, BOM, compliance matrix (done 2026-04-22). Full stamped CAD + FEA reports remain v2. | RFC 0007 v1 hardware bring-up |
| **v2** ✅ | Emitter enforces `rolling_stock` / track / station compatibility in the auto-gen pipeline — family picked by population band, geometry paired from the compatibility matrix, platform length derived per line (done 2026-04-22) | v0 |
| **v3** | BOM + shop drawings for `tram-2car`, `metro-4car`, `metro-6car` | v1 |
| **v4** | EN 15227 simulation + EN 45545-2 sample tests for the `light-metro-3car` cab module | v1 |
| **v5** | First-article rolling-stock prototype produced by the Samawah pilot operator or equivalent | v1, RFC 0003 §5 |

Each phase owns a separate session. This RFC's v0 deliverable is
only the envelope.

## 8. Relationship to existing work

- [`lib/templates/rolling-stock.toml`](../../lib/templates/rolling-stock.toml) —
  the Lego-block TOML that this RFC formalises.
- [`crates/osr-bms`](../../crates/osr-bms/), [`crates/osr-traction`](../../crates/osr-traction/),
  [`crates/osr-brake`](../../crates/osr-brake/), [`crates/osr-hvac`](../../crates/osr-hvac/),
  [`crates/osr-aux-power`](../../crates/osr-aux-power/),
  [`crates/osr-door-control`](../../crates/osr-door-control/),
  [`crates/osr-lighting`](../../crates/osr-lighting/) — the software
  already targets the architectural envelope above. No software
  change is needed for v0; the compatibility-matrix work is v2.
- [RFC 0007](0007-hardware-reference-designs.md) T-ECU/S and
  T-ECU/A host every safety and app function on every family of
  consist. No variant hardware per family.
- [`osr-sim`](../../crates/osr-sim/) accepts a `ConsistDescriptor`
  with the exact envelope numbers from §1 — energy sizing, max
  speed, traction, braking curve. The simulator is the validation
  bed for every `rolling_stock` + `geometry` pairing before shop
  drawings land.

## 9. Open questions

1. **Automatic couplers on `tram-2car`?** Scharfenberg is overkill
   for a 42 m consist that rarely multi-units. Semi-permanent
   drawbar is a candidate; resolve during v1.
2. **HVAC redundancy split.** Per-car vs per-consist HVAC units?
   Per-car gives graceful degradation (one failure doesn't blacken
   the whole train) but costs more HVAC-unit spares. Per-consist
   is cheaper but harsher in failure. Deployment-specific.
3. **Side-pin vs pantograph-down deployment mix.** Side-pin is the
   default station charger, but some island platforms may need a
   pantograph-down dock. Commit the civil-interface selection rules
   at v1.
4. **Windowed vs camera-only side mirrors?** Camera-only reduces
   wind resistance and external noise; windowed meets more
   conservative certification regimes. Per-deployment choice.
5. **Fire detection density.** `osr-fire-safety` assumes aspirating
   smoke detection in battery bay, traction bay, HVAC plenum; do
   we also deploy it in the passenger cabin (ceiling-mounted
   optical), or rely on passenger reports + manual alarm? Committed
   at v4 alongside EN 45545 testing.

## 10. Done criteria

- [x] Four families named and scoped (§1)
- [x] Unified architecture stated (§3)
- [x] Family selection policy fixed (§5)
- [x] Pitfalls and alternatives explicit (§6)
- [x] Rollout ordered (§7)
- [x] Relationship to existing software + templates named (§8)

The next session picks up at **v2 — emitter compatibility
matrix**. The session after owns v1 — shop drawings for the
`light-metro-3car` family.
