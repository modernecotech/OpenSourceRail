# RFC 0008 — Baseline Rolling-Stock Reference Design

**Status:** Draft — planning only, no mechanical drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0003 Samawah Reference Deployment](0003-samawah-reference-deployment.md), [RFC 0007 Hardware Reference Designs](0007-hardware-reference-designs.md)

## 1. Summary

OpenSourceRail commits to **four rolling-stock families** — one per
ridership band — from which every deployment picks exactly one per
line. No bespoke consists; every country that adopts the stack
chooses the closest family and builds to that drawing. This RFC
fixes the engineering envelope (dimensions, masses, axle
arrangement, bogie and brake architecture, cab, crashworthiness,
fire, thermal, acoustic) for each family.

The four families are already named in
[`designs/templates/rolling-stock.toml`](../../designs/templates/rolling-stock.toml).
This RFC promotes that schema into a committed engineering envelope.

| Family | Cars | Length | Tare | Capacity | Peak ridership band (pphpd) | Max speed |
|---|---|---|---|---|---|---|
| `tram-2car` | 2 | 42 m | 90 t | 220 | < 5 000 | 19 m/s (70 km/h) |
| `light-metro-3car` | 3 | 65 m | 195 t | 360 | 5 000–10 000 | 25 m/s (90 km/h) — **Samawah reference** |
| `metro-4car` | 4 | 88 m | 260 t | 540 | 10 000–20 000 | 25 m/s (90 km/h) |
| `metro-6car` | 6 | 132 m | 420 t | 900 | 20 000–35 000 | 28 m/s (100 km/h) |

Pphpd = passengers per hour per direction at peak, planning-grade.

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

Four rolling-stock families, but **one architecture** across all of
them. The scaling is width, length, and car count; the
architectural decisions below are shared. Commonality is the bet:
one spares pool, one maintainer-training syllabus, one CAD reuse,
one supplier-qualification set.

### 3.1 Mechanical

| Aspect | Choice | Rationale |
|---|---|---|
| Car body | Aluminium large-profile extrusions, bolted at end bulkheads | Locally produced in every target region; welders trained on aluminum are easier to find than on steel stainless pressings. |
| Bogies | Two 2-axle bogies per car, Jacobs on articulated interfaces where feasible | Matches the passenger-capacity targets at ≤ 14 t axle load for all families. |
| Suspension | Primary: chevron rubber. Secondary: steel coil + viscous damper, no air springs | Air springs require compressors + leveling valves that are the top-quartile maintenance line item for operators in our target markets. Coil + damper gives comparable comfort at 30 % of the maintenance burden. |
| Wheel | Monobloc, Ø860 mm new / Ø790 mm condemning | UIC 510-2 reference. Wheel re-profiling on depot lathe every 150 000 km. |
| Gauge | 1 435 mm standard, 1 000 mm metre-gauge variant | Both produced from the same body and bogie frame; only the wheelset axle length changes. See [RFC 0009 §4](0009-track-design-standard.md#4-gauge). |
| Wheel–rail profile pairing | S1002 wheel on UIC60 rail (standard gauge) or Ri60 wheel on Ri60 rail (street-tram gauge) | Standard off-the-shelf profiles; no proprietary geometry. |
| Couplers | Scharfenberg Type 10 automatic + e-coupler for 24 V / CAN-FD / Ethernet | Standard metro coupler; allows rescue of a failed train by any neighbour consist in the fleet. |
| Articulation | Low-floor articulated body between intermediate cars on `light-metro-3car` + `tram-2car`; full bogie-per-car on `metro-4car` / `metro-6car` | Articulation keeps low-floor structure simple at short lengths; drops away above 88 m where tare cost dominates. |
| Axle load | ≤ 14 t loaded (AW3 crush) | Well inside a 22.5 t UIC mainline limit — lets the catenary-free metros share minor infrastructure with legacy rail where needed without overstressing bridges. |
| Crashworthiness | EN 15227 Cat C-II (medium urban) for all families | Addresses metro-to-metro and metro-to-obstacle collisions at up to 25 km/h. Energy absorbers at cab ends + at each articulation; anti-climbing features. |

### 3.2 Propulsion + auxiliary

| Aspect | Choice | Rationale |
|---|---|---|
| Traction motor | Permanent-magnet synchronous, axle-mounted, one per powered wheelset | PMSM efficiency ≥ 96 % at peak. Axle-mount removes gearboxes from every powered bogie, eliminating one of the top maintenance line items. |
| Inverter | 3-phase, silicon-carbide (SiC) MOSFETs, ≥ 98 % efficiency at peak | SiC is commodity-grade in 2026. Water-cooled cold plate, no fans. One inverter per powered bogie. |
| Powered wheelsets | 50 % of the trainset's wheelsets on `tram-2car` / `light-metro-3car`; 75 % on `metro-4car`; 100 % on `metro-6car` | Adhesion headroom drops as passenger load rises; larger consists need more powered axles to maintain gradient performance in rain/dust. |
| Battery | Sodium-ion chemistry (Na-ion) on all families; LFP as a drop-in alternative for operators with established LFP spares | Na-ion is the target: no lithium supply dependency, better low-cost profile, thermal runaway is tamer. LFP is the fallback where Na-ion isn't yet locally serviced. |
| Battery pack topology | String of ≤ 30 modules per pack, two packs per consist (redundant) | Either pack alone delivers enough energy for a safe-stop + inching back to a depot. `osr-bms` ([crates/osr-bms](../../crates/osr-bms/)) manages per-pack contactors. |
| Battery size | Per family per the table in §1 (450 / 900 / 1 200 / 1 800 kWh) | Sized for one full round-trip at RFC 0003 peak headway plus 20 % reserve. |
| Opportunity charging | Overhead pantograph at terminal stations only (RFC 0003 §4.2); no continuous catenary | Catenary-free is a project-wide invariant ([ARCHITECTURE §4 D7](../ARCHITECTURE.md#4-architectural-bets)). Pantograph at 1 500 V DC dock — same interface at every terminal nationwide. |
| Regen | Default on; friction brake blends in below 8 km/h | Matches [`osr-brake`](../../crates/osr-brake/)'s WSP + regen-priority arbitration. |
| Friction brake | Disc brake on every trailing axle, electromagnetic actuation | No pneumatic brake system — removes the compressor-maintenance line item entirely. Electric brake is continuously self-monitoring via `osr-brake`'s WSP + pressure sense loops. |
| Emergency brake | Same discs, different current source (ultra-cap + battery fallback); independent of regen | SIL-4: emergency-brake current cannot fail with any single electronics failure. Tested on every ignition cycle by the `osr-vigilance` start-up check. |
| Aux inverter | 400 V 3-phase AC, 24 V DC, 110 V DC outputs | Runs HVAC, lighting, compressors (if any — per-deployment choice), PIS, comms. `osr-aux-power` drives it. |

### 3.3 Interior

| Aspect | Choice | Rationale |
|---|---|---|
| Floor | Low floor end-to-end (350 mm platform-top), except `metro-6car` which is high-floor (1 100 mm) for platform-compatible interchange | Low floor gives accessible boarding without lifts; matches most developing-world street-platform geometry. High floor on `metro-6car` matches the heavy-metro station archetype (island platform, mezzanine). |
| Door count | 2 × 1 300 mm plug doors per car side | Throughput ≈ 4 passengers / second / door pair at saturated dwell. |
| Door clearance | 1 250 mm wide × 2 000 mm tall opening | Wheelchair + stroller compatible. |
| Seating | Longitudinal bench seating, ≥ 15 % seats priority (elderly, pregnant, wheelchair companion) | Standing-heavy mix maximises peak capacity; matches the pphpd planning band. |
| Wheelchair spaces | 2 per car (4 per `tram-2car`, 6 per `light-metro-3car`, 8 per `metro-4car`, 12 per `metro-6car`) | Per accessibility template ([`designs/templates/accessibility.toml`](../../designs/templates/accessibility.toml)). |
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
| Nose geometry | **Sensor cowl + coupler, no windscreen, no cab door.** Cars are symmetric end-to-end; passenger floor extends to the full car length. | ~14 extra seats per `light-metro-3car` consist; ~€140 k + ~2.3 t saved vs. a cabbed reference |
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
  [`designs/templates/track-geometry.toml`](../../designs/templates/track-geometry.toml).
- Rolling stock → station: platform length = `consist.length_m + station.platform_clearance_m`.
- Rolling stock → line length: max battery SoC swing ≤ 60 % over a
  full round-trip without opportunity charging.

The v2 emitter (RFC 0008 §7 milestone) validates all three
constraints and fails the build on mismatch.

## 5. Family selection policy

The auto-gen pipeline picks a family per line using population and
a simple ridership model:

```text
   population band (city)     pphpd target         chosen family
   ────────────────────────   ───────────────      ───────────────
   ≤ 300 k                    ≤  4 000             tram-2car
   300 k … 1 M                ≤  9 000             light-metro-3car
   1 M … 3 M                  ≤ 18 000             metro-4car
   ≥ 3 M                      ≤ 30 000             metro-6car
```

Pphpd is estimated from population × 0.012 × peak-factor 0.08,
capped at the family's table value. The pipeline writes the
choice into `design.toml` under `[[lines]] rolling_stock =
"<family>"`.

## 6. Pitfalls and decisions

- **Na-ion before LFP.** Na-ion has a shallower cycle life than
  LFP today (≈ 3 000 cycles at 100 % DoD vs LFP's ≈ 6 000). We
  accept that trade because Na-ion doesn't lock a country into
  lithium-chain geopolitics. LFP remains a drop-in.
- **No pneumatic brake.** A pneumatic brake + air reservoir is the
  rail industry's reference design; we replace it with
  electromagnetic disc + battery-backed ultra-cap. The winner is a
  ~40 % maintenance-line-item reduction on trainsets. The risk is
  EN 14198 compliance for the electric brake; the safety case
  carries `osr-brake`'s Kani + proptest evidence.
- **Low floor end-to-end on the smaller families.** This costs a
  few centimetres of ground clearance we could spend on bigger
  bogies or HVAC ducting; we trade it back for accessibility
  without station lifts. The `metro-6car` family goes high-floor
  because its archetype (island platform, mezzanine) already
  provides level boarding via station structure.
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

- [`designs/templates/rolling-stock.toml`](../../designs/templates/rolling-stock.toml) —
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
3. **Cab-end pantograph vs roof-centre pantograph?** Affects
   station canopy design at terminal archetypes. Probably roof-
   centre for acoustic and operational reasons; commit at v1.
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
