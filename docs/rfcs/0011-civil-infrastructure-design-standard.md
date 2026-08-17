# RFC 0011 — Civil Infrastructure Design Standard

**Status:** Draft — planning only, no structural drawings ship with this RFC
**Date:** 2026-04-22
**Updated:** 2026-08-17 — OSR Rapid Viaduct Kit correction
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0009 Track Design Standard](0009-track-design-standard.md), [RFC 0010 Station Design Standard](0010-station-design-standard.md)

## 1. Summary

OpenSourceRail commits to **two civil classes only — at-grade and
elevated** — with bridges for water crossings as a narrow third
class. **No tunnels.** Every corridor the auto-gen pipeline
produces, and every hand-authored corridor the operator commits,
will sit on one of:

| Class | Share (target) | Description |
|---|---|---|
| **at-grade** | ≥ 70 % | Track sits on prepared subgrade at natural ground level (possibly with minor cut/fill ≤ 3 m). The cheapest and fastest class by 1–2 orders of magnitude. |
| **elevated** | ≤ 25 % | Track sits on a viaduct structure 5–12 m above ground (precast concrete U-girder, standardised span). |
| **bridge** | ≤ 5 % | Over a water crossing or deep gap. Separately engineered special span with site-specific substructure. |

The fourth class the first-pass auto-gen inference used —
**tunnel** (cut-and-cover and bored) — is **removed from the
catalogue**. Where an alignment previously would have gone
underground, it now goes elevated over the same footprint, or
deviates around the constrained zone on at-grade. Operators who
deliberately want a tunnel are forking the project; OpenSourceRail
upstream does not carry tunnel designs, tunnel cost models, or
tunnel-specific signalling / ventilation / evacuation engineering.

## 2. Non-goals

- **Not a tunnel standard.** By construction. The project's cost
  model, the simulator's energy budget, the sensor-tuning for
  GNSS + balise, and the operations rulebook (RFC 0013) are all
  calibrated against above-ground operation. Going underground
  reopens every one of those calibrations.
- **Not a geotechnical rulebook.** Soil survey, pile type,
  foundation depth, seismic detailing — owned by the deploying
  operator's civil team. This RFC fixes the *functional* envelope
  (span range, clearance, load class) not the *method*.
- **Not a bridge design manual.** Spans above 30 m, water crossings,
  turnouts, and exceptional crossings use a separately engineered
  segmental, I-girder, or steel-composite product. They are not a stretched
  version of the standard full-span trough.
- **Not a land-acquisition policy.** How a deployment acquires
  right-of-way (ROW) — expropriation, purchase, existing-rail
  corridor reuse, new-build — is municipal work.
- **Not a standards body.** We reference EN 1990 (Eurocode
  basis), EN 1991-2 (traffic loads on bridges / viaducts),
  EN 1998 (seismic), UIC 777-2 (infrastructure gauge), local
  building codes where deployed. We do not publish new ones.

## 3. Why no tunnels

A planning-grade cost comparison for a 1 km segment in typical
dense-urban conditions across the target regions:

| Class | CAPEX (USD/km) | Build time | Post-build maintenance |
|---|---|---|---|
| At-grade dedicated ROW | 3.0 M OSR floor / 3–6 M conventional | 6–12 months | Low — ballastless slab/embedded trackform |
| Elevated viaduct | 12.0 M OSR floor / 12–25 M conventional | 12–18 months | Medium — bearing + expansion-joint inspection |
| Bridge over water | 18.0 M OSR floor / 15–35 M conventional | 18–24 months | Medium — same as viaduct + scour inspection |
| Cut-and-cover tunnel | 60–120 M conventional | 30–48 months | High — ventilation + pumping + egress drills |
| Bored tunnel | 90–200 M conventional | 48–72 months | High — same as above, plus tunnel-boring-machine commissioning |

Numbers are planning-grade, calibrated against generated deployment
instances including Samawah
context ([RFC 0003 §2.3](0003-samawah-reference-deployment.md)).

A tunnel segment is 10–40× the CAPEX and 4–8× the build-time of an
equivalent at-grade segment. It also brings a permanent
operational overhead: mechanical ventilation, flood pumping, fire
suppression, emergency evacuation plans, and radio-coverage
retrofit. Every one of those is an additional subsystem the
deploying operator must staff and maintain.

The mission is "urban rail affordable enough that a developing
nation can finance it domestically." A corridor with any
tunnelling in it is outside that envelope. **The design decision
is: if the alignment can't go at-grade or elevated, the
alignment should deviate around the constraint.** Even at a 20 %
longer corridor, the detour is cheaper than the tunnel it
avoids.

## 4. At-grade — the 70 % case

### 4.1 Envelope

- **Subgrade:** compacted fill or in-situ soil graded to +/-25 mm of
  design. Capping layer of 150 mm crushed stone, then ballastless
  reinforced slab / embedded direct-fixation plinths for the running
  rails. The default urban trackform avoids ballast migration,
  tamping cycles, and loose aggregate at crossings.
- **Earthworks:** cut / fill up to 3 m depth only. Beyond 3 m the
  segment is either:
  - Re-classified to **elevated** (bridge over the gap / viaduct
    over the hill), or
  - Deviated around the constraint.
- **Drainage:** transverse slope >= 2 % either side; longitudinal
  channels every 50 m; culverts at every flow-path crossing.
  Drainage is not optional: a flooded slab undermines fastener
  integrity, corrodes embedded hardware, and damages the subgrade.
- **Fencing:** dedicated ROW is fenced the full length on both
  sides. No uncontrolled pedestrian crossings. Level crossings
  only where a city street intersects and an underpass / overpass
  is prohibitively expensive. See [RFC 0012](0012-switches-and-crossings.md)
  for the level-crossing equipment standard.
- **ROW width:** minimum 10.5 m for double-track at-grade (two
  tracks × 3.5 m wide plus 1 m each side clearance plus fencing
  allowance); 7 m for single-track.

### 4.1.1 Narrow old-town single-track option

Some historic cores and market streets cannot fit a 10.5 m dedicated
double-track reservation without demolition, but also do not justify
viaduct intrusion. OpenSourceRail therefore permits a constrained
single-track at-grade segment as an **at-grade variant**, not a fourth
civil class.

Rules:

- Use only for short constrained sections where double track would
  require demolition or permanent removal of the street's essential
  pedestrian/service function.
- Fit the running way inside the 7 m single-track envelope, with
  protected pedestrian edges and no mixed running with road traffic.
- Provide double-track passing loops only at stations, portals, or
  immediately outside the constrained street.
- Interlocking treats the whole single-track section as one opposing-move
  exclusion zone unless a deployment-specific signalling design divides
  it into shorter protected blocks.
- Timetables must prove the desired headway through the single-track
  section before the option is accepted. At 3-minute peak headway, a
  single-track section longer than roughly 800-1,000 m will usually force
  either lower frequency, directional tidal operation, or a bypass.
- Emergency walkways, evacuation gates, drainage, charging isolation, and
  intrusion detection remain mandatory; the narrow option saves width, not
  safety systems.

The auto-generation pipeline should prefer this option before elevated
only when a tagged old-town / constrained-street corridor is short,
station-loop spacing is feasible, and the resulting timetable still meets
the line's published service class. Otherwise it should stay double-track
or go elevated/deviate.

### 4.2 When at-grade is inappropriate

Even with the default bias to at-grade, certain conditions push
toward elevated:

- The alignment crosses a river wider than 30 m → bridge.
- The alignment crosses a highway or mainline rail at grade that
  cannot be broken by a level crossing (too many crossings per
  hour would make the crossing barrier close more than open) →
  elevated.
- The alignment runs through a dense built-up core where ROW
  acquisition would require demolition of more than 3 buildings
  per 100 m of corridor → elevated or deviate.
- The alignment runs along a street where at-grade light-rail
  running would conflict with road vehicles at every junction →
  elevated or route to a parallel street.

The auto-gen pipeline's civil inference (§6) now maps these
conditions to `Elevated` where it previously would have emitted
`BoredTunnel`.

## 5. Elevated — the 25 % case

### 5.1 Envelope

- **Structure:** paired single-track precast concrete U-troughs. OSR-U25 is
  the primary simply supported product and OSR-U20 is the closure product.
  The planning clear width is 4.5 m (4.9 m external) so the 2.93 m dynamic
  train envelope can coexist with a 1.0 m escape walkway. OSR-U30 is not
  released until project transport, lifting, and structural checks close.
- **Piers:** single-column reinforced concrete, 1.5 m × 2.0 m
  rectangular, heights 5–12 m, pile-cap foundation (piles sized
  per deployment-local geotech).
- **Deck clearance:** 5.0 m vertical under the girder soffit over
  any road; 5.5 m over a truck route; 7.5 m over a rail corridor
  (UIC 777-2 minimum).
- **Pier spacing:** 25 m nominal, using 20 m closure bays where constrained.
  Spans above 30 m use OSR-SP or another separately engineered structure.
- **Bearings:** scheduled fixed/guided/free bearings. An interior pier has
  eight bearings in two longitudinal rows; an end support has four.
  Permanent checked jacking interfaces permit replacement.
- **Movement:** a gap occurs at every simply supported span end. The project
  issues a bearing/movement schedule and continuous-welded-rail interaction
  analysis; rail expansion devices are used only where that analysis requires.
- **Parapets:** 1.4 m solid concrete panel, continuous, with a
  handrail on the inspection walkway.
- **Walkway:** integrated one-side inspection/escape ledge, 1.0 m clear, escape
  ramps every 250 m down to at-grade.
- **Acoustic screens:** where residential buildings are within 25
  m horizontally, precast concrete acoustic panel on the near
  parapet, 2.0 m tall, absorption class ≥ A2. Target exterior
  noise at residential façade ≤ 55 dB(A) day, ≤ 45 dB(A) night per
  WHO community-noise guidelines.
- **PV integration:** every viaduct girder accommodates a 6 kW PV
  array per span on south/sun-exposed faces (4 m² per m of span
  length). Feeds the nearest `osr-energy-site` (RFC 0002).

### 5.2 Rationale for one reference girder

- **One mould across the whole project.** The precast yard casts
  one U-girder shape; every span of every viaduct of every
  OpenSourceRail deployment uses that shape. This is the biggest
  single CAPEX / schedule lever in elevated construction and
  matches the "one spares pool, one CAD reuse" principle from
  RFC 0008 / 0009 / 0010.
- **Double-track substructure, repeated single-track girders.** One shared
  hollow/precast-shell cap carries two identical U-troughs at 5.3 m centres. A
  single-track initial line still builds the shared substructure and may
  defer the second girder until capacity demands it.
- **Simply-supported, not continuous.** Continuous spans give a
  small live-load saving at the cost of much more complex
  construction sequencing and bearing design. The simplicity bet
  wins.

## 6. Bridge — the 5 % case

- **Reference class:** separately engineered OSR-SP segmental, I-girder, or
  steel-composite span. The standard full-span U catalogue ends at 30 m.
- **Pier:** when a pier has to sit in the water, foundation is a
  reinforced-concrete caisson or a pile group with a protection
  cutwater. Scour assessment per EN 1991-2 §13 with a 100-year
  design flood.
- **Navigation clearance:** per the navigable waterway's published class.
  The operator commissions the bridge design and the standard OSR-U catalogue
  ends at the approach where the site demands a non-catalogue structure.
- **Thermal:** project-specific bearing, joint, and rail/bridge interaction
  design for the complete temperature, creep, shrinkage, and seismic range.

## 7. Stations-as-structures

Station archetypes from [RFC 0010](0010-station-design-standard.md)
map to civil class as follows:

| Archetype | Typical civil class | Notes |
|---|---|---|
| `halt` | at-grade | No canopy PV. Single side platform on direct-ground footing. |
| `standard` | at-grade | Solar canopy + side platforms. |
| `major` | at-grade | Island platform, larger canopy. |
| `interchange` | elevated + at-grade | One line is on the viaduct, the other at-grade. The two platforms stack vertically at the junction. Never two elevated lines stacked — the second level's wind and seismic loads rule that out of the upstream catalogue. |
| `terminal` | at-grade | End-of-line; turnback tracks sit at grade. |
| `depot-terminal` | at-grade | Yard footprint is large; elevating it is prohibitively expensive. |

**Underground stations are not in the catalogue.** The previous
draft of RFC 0010 used the word "stacked" to describe
`interchange` layouts; this RFC clarifies that stacked means
vertical separation between at-grade and elevated levels at the
junction, **not** between two underground levels.

## 8. Auto-gen pipeline — the civil inference, revised

The civil-class inference in
[`crates/osr-routing/src/civil.rs`](../../crates/osr-routing/src/civil.rs)
currently classifies a cell based on the underlying cost surface.
Under the no-tunnel invariant:

- Cells with cost ≤ 40 → **at-grade** (unchanged).
- Cells with cost 40..100 → **at-grade** (was already; unchanged).
- Cells with cost 100..400 (water) → **bridge** (unchanged).
- Cells with cost ≥ 400 (building / dense built-up) → **elevated**
  (was `BoredTunnel` → now elevated).

This aligns with the rule: "if the corridor can't be at-grade, it
goes above, not below."

Two downstream consequences, surfaced in `design-quality.yaml`:

1. **Elevated fraction as a soft gate.** If the share of
   elevated structure for a line exceeds 30 %, the quality file
   raises a warning. Designs with > 50 % elevated either need
   deviation or are inherently expensive and should prompt
   review.
2. **No tunnel class.** Quality output reports only at-grade, elevated,
   and bridge fractions.

## 9. Cost-anchor lookup

Total CAPEX drives the national-treasury conversation. The
auto-gen pipeline emits a full `[costs]` block per city in
`design.toml`, broken down by bucket below.

The source currency is USD because the marketplace and country-finance
templates quote in USD. Generated `*_eur` fields are converted reporting
views at 0.92 USD->EUR. The canonical machine-readable rates live in
[`capex-costs.toml`](../../lib/templates/capex-costs.toml); this RFC
keeps the narrative summary.

### 9.1 Civil works (USD/km × civil mix)

| Class | USD planning-grade |
|---|---|
| at-grade | 3 000 000 / route-km |
| elevated | 12 000 000 / route-km |
| bridge | 18 000 000 / route-km |
| elevated-interchange premium | 4 500 000 / site |

### 9.2 Stations (RFC 0010 archetype catalogue)

| Archetype | USD planning-grade |
|---|---|
| `halt` | 600 000 |
| `standard` | 2 500 000 |
| `major` | 4 500 000 |
| `terminal` | 4 500 000 |
| `depot-terminal` | 5 000 000 |
| `interchange` | 8 000 000 |
| `interchange-elevated` | 12 000 000 |

The elevated-junction premium in §9.1 covers the viaduct + upper
deck at interchanges; the table above covers the at-grade lower
platform, ground-level pedestrian access, and protected crossing
equipment where needed. Overbridges, lifts, and stairs are not the
standard station assumption; they are carried only by elevated/stacked
sites or local road-barrier overrides.

### 9.3 Depots (RFC 0014 archetype catalogue)

| Archetype | USD planning-grade |
|---|---|
| `main-heavy` | 8 000 000 |
| `secondary-medium` | 3 000 000 |
| `layup-minimal` | 400 000 |

These rates assume RFC 0014 distributed overnight stabling: healthy
trainsets may sleep at powered passenger stations and layups, so the
main-heavy no longer carries parking capacity for every train every
night and `layup-minimal` is a powered-station stabling/isolation kit
rather than a small standalone yard.

### 9.4 Rolling stock (RFC 0008 local-owner production × fleet count)

Rolling-stock city CAPEX uses a local-owner trainset-family planning
unit, not an inflated per-car multiplier and not the raw marketplace BOM
floor. The unit includes direct material, local assembly/labour, nominal
per-train QA/acceptance evidence, and modest local handover logistics.
Fixtures/tooling live in the railway production plant line; warranty,
spares, and routine commissioning support are OPEX.

| Family | USD / trainset local-owner unit |
|---|---:|
| `urban-shuttle-1car` | 280 000 |
| `tram-2car` | 560 000 |
| `light-metro-3car` | 900 000 |
| `metro-4car` | 1 120 000 |
| `metro-6car` | 1 680 000 |

Fleet count = peak-revenue + spare + cold-reserve per RFC 0014 §4.

### 9.5 Railway production plant

Each country carries one lean shared railway production-plant setup allowance
for all city fleets it will build or assemble locally. Cities do not duplicate
this asset in city CAPEX. The national factory is sized to the largest
single-city fleet programme, costed per supported vehicle/car module, reused
through a phased rollout, and kept separate from rolling-stock procurement.

| Item | Planning-grade basis |
|---|---:|
| Base local plant setup | 60 000 USD / vehicle-car module |
| High sensitivity check | 120 000 USD / vehicle-car module |

The allowance covers reusable 1 m fiberglass panel moulds, clip/drill
gauges, basic steel fixtures, plant services, commissioning bay setup,
material handling, and production-readiness work. It excludes a full-length
body mould and production adhesive cure hall. Six parallel two-person crews
can install and release a three-car exterior body in one eight-hour shift
after painted-frame dimensional release; doors, glazing, equipment, bogies,
commissioning, homologation, and first-article testing remain separate work.
Distributed overnight stabling reduces the number of depot-centred
commissioning and parking bays needed in the production/depot complex. A
A three-module increment of supported factory capacity therefore carries
180 000 USD of base plant allowance, while the high sensitivity is 360 000 USD.

### 9.6 Systems

| Item | Planning-grade basis |
|---|---|
| Residual train-control wayside (RFC 0015 GoA 4) | 50 000 USD / route-km |
| Station/depot charging microgrid interfaces | 120 000–1 000 000 USD / stop, by station archetype |

RFC 0015 mandates battery-electric operation with station charging:
there is no overhead catenary, third rail, feeder substation, or route
traction-power budget. The energy infrastructure bucket covers the
conductive chargers, local switchgear, inverter interface, and
station/depot microgrid tie-in. PV/storage quantities are sized in the
energy-site catalogue rather than as a continuous per-km rail-power
system.

### 9.7 EPC overhead

Integration + project management is **7 %** of the subtotal across
§9.1 – §9.6.

Rates are deployment-localised via the
[`country-costs.toml`](../../lib/templates/country-costs.toml)
template (labour, materials, finance cost adjustments). The
base rates above are what the upstream catalogue quotes; actual
numbers in any given deployment can be ± 40 %.

`total_usd` is the procurement-basis headline per city. `total_eur` is
also emitted for compatibility with earlier generated schemas.

## 10. Constructability constraints

- **Concrete supply.** Precast concrete yards exist in every
  target region; most can produce the reference U-girder from an
  off-the-shelf mould sold by the major formwork vendors
  (PERI, Meva, Doka). Operators without a nearby precast yard
  bootstrap one — a 5 km² yard with 20 formworks produces enough
  girders for 50 km of viaduct in 18 months.
- **Steel reinforcement.** All target regions have domestic
  rebar mills in the 12–40 mm range we use.
- **Post-tensioning tendons.** Commodity; local supply exists
  in every target region.
- **Lifting and transport.** The widened constant-thickness 25 m CAD envelope
  is about 117 t and is a permit-load component. The project must release the
  route, transporter, lifting points, temporary bracing, crane/launcher,
  tandem-lift controls, wind limits, and contingency landing method.
- **Launching.** Where full-span access is constrained, OSR-US uses match-cast
  2.5–3.0 m segments, post-tensioning, and an overhead launcher with specialist
  geometry, epoxy-joint, tendon-grouting, and staged-load QA.

No restricted-export equipment. No bespoke machinery. The
construction envelope matches what a mid-size regional
civil contractor can mobilise.

## 11. Pitfalls and decisions

- **No tunnels is the non-negotiable decision.** An operator who
  believes their corridor absolutely requires a 3 km tunnel under
  a city centre has exactly two options: (a) deviate the
  alignment; (b) fork the project. Upstream stays on the
  at-grade / elevated / bridge envelope.
- **At-grade dominates even where it's unfashionable.** Modern
  metro vendors push elevated + tunnel because their business
  model prefers CAPEX depth. OSR's mission is the opposite:
  every km pushed to at-grade saves 4–10× cost. A Samawah-
  scale deployment that lands 70 % at-grade is the successful
  design; any design above 50 % elevated is a red flag.
- **One reference viaduct.** Operators who want a different
  girder geometry (ornamental, signature architecture) are free
  to substitute; the upstream catalogue fixes one shape for
  CAPEX / spares reasons, not for aesthetic ones.
- **Special crossings are separate products.** OSR-U25 is not stretched to
  40 m. OSR hands off to OSR-SP or a local engineering tender at the approach.
- **Noise mitigation is structural, not operational.** Acoustic
  screens on viaducts > operational speed restrictions. A 2 m
  concrete panel costs almost nothing and avoids a permanent
  speed-limit loss. Operators sometimes skip this; upstream
  builds it in.
- **Seismic detailing is per deployment.** The reference viaduct
  envelope handles PGA ≤ 0.3 g; above that, the deployment's
  structural team ups the rebar + bearing spec per EN 1998. The
  shape stays the same.

## 12. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** | `osr-routing::civil` updated to drop tunnel classes (in this RFC's commit) | v0 |
| **v2** ✅ | Emit `[costs]` block (at_grade / elevated / bridge / total_eur) per city in the auto-gen output, using the §9 rate table (done 2026-04-22) | v1 |
| **v2.1** ✅ | Extend `[costs]` to the full CAPEX stack — stations (RFC 0010 archetypes), depots (RFC 0014 archetypes), rolling stock (RFC 0008 families), GoA 4 onboard autonomy/residual wayside train control, station/depot charging microgrids, and EPC overhead. USD is the procurement basis and EUR values are explicit converted views. | v2 |
| **v2.2** ✅ | Move the source cost basis to USD direct-procurement planning rates, add `*_usd` fields, keep `*_eur` mirrors, and drop EPC overhead to 7 % (done 2026-06-04). | v2.1 |
| **v2.3** ✅ | Add the railway production-plant setup bucket, now 60 000 USD per vehicle/car module with 120 000 USD retained as a high sensitivity check after 1 m clip-on fiberglass body and distributed-stabling scope reductions (updated 2026-08-15). | v2.2 |
| **v2.4** ✅ | Replace duplicated city production plants with one shared national factory sized to the largest city fleet programme; city CAPEX is zero for this bucket and national briefs carry the asset once. Add imported-value and local-capital financing boundaries. | v2.3 |
| **v3** ✅ | Parametric OSR-U25/U20 clearance geometry, structural-feature placeholders, OSR-US segmental and OSR-SP special-span families are controlled under [`mechanical-py/src/osr_mech/civil/`](../../mechanical-py/src/osr_mech/civil/). Shared 5–12 m piers use widened hollow/precast-shell caps, eight-bearing interior schedules, four-bearing end supports, jacking interfaces, and pile-cap/monopile foundation envelopes. The controlled design-basis, load, egress, movement, erection, first-article, and quantity packages live under [`docs/civil/`](../civil/). | v0 |
| **v4** | Surveyed civil design package for the first pilot line, generated from the current city model | v3, RFC 0003 |
| **v5** | First-article viaduct erected for a deployment instance | v3 |

## 13. Relationship to existing work

- [`lib/templates/structures.toml`](../../lib/templates/structures.toml)
  — the Lego-block schema. v1 of this RFC removes the
  `cut-and-cover-tunnel` and `bored-tunnel` entries.
- [`crates/osr-routing/src/civil.rs`](../../crates/osr-routing/src/civil.rs)
  — the inference function. v1 of this RFC collapses the top
  threshold to `Elevated` (was `BoredTunnel`) and removes the
  `CutAndCoverTunnel` and `BoredTunnel` variants from `CivilClass`.
- [`crates/osr-design/src/emit.rs`](../../crates/osr-design/src/emit.rs)
  — the quality YAML emitter. v1 stops counting tunnel length
  (always zero now) and adds the elevated-fraction soft gate.
- RFC 0009 §5 and RFC 0010 §13 reference tunnel alignment /
  stacked-underground interchange respectively — both amended
  in this commit to match the no-tunnel invariant.
- [`lib/templates/platform-doors.toml`](../../lib/templates/platform-doors.toml)
  references "tunnel stations"; that line is updated to describe
  full-height PSDs as an **optional** upgrade for climate-sealed
  stations regardless of civil class.

## 14. Open questions

1. **Grade-separated level crossings** — a road underpass below
   an at-grade rail corridor counts as a structure; does it get
   its own civil class? v1 folds it into the road authority's
   scope, not rail's.
2. **Cut-and-fill extent limits.** 3 m is arbitrary. Real
   deployments in hilly terrain may need 5 m cuts. Revisit with
   a hilly-pilot case study.
3. **Acoustic screen effectiveness in hot climates.** Concrete
   screens expand/contract; joints need seasonal inspection.
   How does that feed the CBM schedule? Candidate `osr-cbm-*`
   extension.
4. **Wooden / bamboo viaduct for ultra-low-cost deployments?**
   Real regional-rail projects in parts of South and Southeast
   Asia have used timber structures historically. Out of scope
   upstream; a local fork can layer that on.
5. **Green-roof viaducts** — planting integrated into the deck
   for heat-island mitigation. Candidate v4 addendum.

## 15. Done criteria

- [x] Two classes only — at-grade + elevated — with bridges narrow (§1)
- [x] No-tunnel rationale explicit with cost comparison (§3)
- [x] At-grade envelope specified (§4)
- [x] Elevated envelope specified, one reference girder (§5)
- [x] Bridge class as a viaduct variant (§6)
- [x] Stations-as-structures mapping (§7)
- [x] Civil inference updated (§8)
- [x] Cost anchors named (§9)
- [x] Constructability constraints stated (§10)
- [x] Pitfalls + alternatives (§11)
- [x] Rollout ordered (§12)
- [x] Relationship to existing code + templates (§13)

The next session picks up at **v2 — cost estimates in auto-gen
output** (a short follow-on to the v1 tunnel-removal already
landed in this commit).
