# RFC 0011 — Civil Infrastructure Design Standard

**Status:** Draft — planning only, no structural drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0003 Samawah Reference Deployment](0003-samawah-reference-deployment.md), [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0009 Track Design Standard](0009-track-design-standard.md), [RFC 0010 Station Design Standard](0010-station-design-standard.md)

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
| **bridge** | ≤ 5 % | Over a water crossing or a deep gap. Same viaduct standard, longer spans, water-bearing piers. |

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
- **Not a bridge design manual.** Water-bearing bridges default
  to the reference viaduct stretched to longer span; anything
  more specialised (cable-stayed, arch) is outside the upstream
  catalogue.
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

| Class | CAPEX (€/km) | Build time | Post-build maintenance |
|---|---|---|---|
| At-grade dedicated ROW | 2–5 M | 6–12 months | Low — routine track + ballast |
| Elevated viaduct | 12–25 M | 12–18 months | Medium — bearing + expansion-joint inspection |
| Bridge over water | 15–35 M | 18–24 months | Medium — same as viaduct + scour inspection |
| Cut-and-cover tunnel | 60–120 M | 30–48 months | High — ventilation + pumping + egress drills |
| Bored tunnel | 90–200 M | 48–72 months | High — same as above, plus tunnel-boring-machine commissioning |

Numbers are planning-grade, calibrated to the Samawah reference
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

- **Subgrade:** compacted fill or in-situ soil graded to ±25 mm of
  design. Capping layer of 150 mm crushed stone, then 300 mm
  ballast below sleeper, or direct-fixed slab where vibration
  demands (station throats, curves sharper than 2× the preset
  minimum).
- **Earthworks:** cut / fill up to 3 m depth only. Beyond 3 m the
  segment is either:
  - Re-classified to **elevated** (bridge over the gap / viaduct
    over the hill), or
  - Deviated around the constraint.
- **Drainage:** transverse slope ≥ 2 % either side; longitudinal
  channels every 50 m; culverts at every flow-path crossing.
  Drainage is not optional — a flooded ballast destroys track
  geometry within hours.
- **Fencing:** dedicated ROW is fenced the full length on both
  sides. No uncontrolled pedestrian crossings. Level crossings
  only where a city street intersects and an underpass / overpass
  is prohibitively expensive. See [RFC 0012](0012-switches-and-crossings.md)
  for the level-crossing equipment standard.
- **ROW width:** minimum 10.5 m for double-track at-grade (two
  tracks × 3.5 m wide plus 1 m each side clearance plus fencing
  allowance); 7 m for single-track.

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

- **Structure:** precast concrete U-girder on 25–40 m simply-
  supported spans, post-tensioned. One reference girder cross-
  section (2.2 m × 1.8 m, double-track) for the entire catalogue;
  operators do not customise.
- **Piers:** single-column reinforced concrete, 1.5 m × 2.0 m
  rectangular, heights 5–12 m, pile-cap foundation (piles sized
  per deployment-local geotech).
- **Deck clearance:** 5.0 m vertical under the girder soffit over
  any road; 5.5 m over a truck route; 7.5 m over a rail corridor
  (UIC 777-2 minimum).
- **Pier spacing:** 30 m nominal; reducible to 25 m at road
  junctions where a longer span would intrude on horizontal
  clearance. 40 m spans are reserved for river crossings.
- **Bearings:** elastomeric + PTFE slider; replaced every 30
  years. No bespoke bearing designs.
- **Expansion joints:** every 60 m along the deck; standard metro
  finger plate.
- **Parapets:** 1.4 m solid concrete panel, continuous, with a
  handrail on the inspection walkway.
- **Walkway:** one-side inspection walkway, 1.0 m wide, escape
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
- **Double-track only.** A single-track elevated girder is
  structurally wasteful (two single girders cost more than one
  double girder). Deployments with a single-track line still
  build the double-track girder and leave one track unlaid until
  capacity demands it.
- **Simply-supported, not continuous.** Continuous spans give a
  small live-load saving at the cost of much more complex
  construction sequencing and bearing design. The simplicity bet
  wins.

## 6. Bridge — the 5 % case

- **Reference class:** same precast U-girder as the elevated
  viaduct, extended to a 40 m span.
- **Pier:** when a pier has to sit in the water, foundation is a
  reinforced-concrete caisson or a pile group with a protection
  cutwater. Scour assessment per EN 1991-2 §13 with a 100-year
  design flood.
- **Navigation clearance:** per the navigable waterway's
  published class; bridge spans lengthen to clear. Very wide /
  navigable rivers (Tigris, Euphrates, Mekong-class) are handled
  by adding piers in the water with the standard girder; a
  custom long-span cable-stayed bridge is explicitly **out of
  scope** for the upstream catalogue — the operator commissions
  a bespoke design and the OSR catalogue ends at the approach.
- **Thermal:** expansion joint at every abutment; in countries
  with > 40 °C seasonal thermal amplitude, additional joints
  mid-span.

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
2. **No `tunnel` field anymore.** The YAML key stays (empty) for
   backward compatibility with existing deployments' scripts, but
   emits `0.0` unconditionally. Future schema version will drop
   it.

## 9. Cost-anchor lookup

Civil CAPEX drives the national-treasury conversation. The
auto-gen pipeline emits `cost_estimate_eur` per line using
lookup:

| Class | €/km planning-grade |
|---|---|
| at-grade | 3 500 000 |
| elevated | 18 000 000 |
| bridge | 25 000 000 |

Rates are deployment-localised via the
[`country-costs.toml`](../../lib/templates/country-costs.toml)
template (labour, materials, finance cost adjustments). The
base rate above is what the upstream catalogue quotes; actual
numbers in any given deployment can be ± 40 %.

A `cost_estimate_total_eur` per city is also emitted. This is
blunt but useful: it is the single number a municipal finance
officer asks for first when evaluating an OpenSourceRail
deployment.

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
- **Lifting.** The 25 m reference girder masses ~60 t. Mobile
  crawler cranes rated 200 t are locally available across
  target regions.
- **Launching.** Where crane access is constrained, launching
  girder or shuttering falsework is used. The upstream catalogue
  assumes crawler-crane erection; launching-girder erection is
  per-deployment.

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
- **Bridges are viaducts with wet piers.** No custom bridge
  designs upstream. If a site demands a genuinely custom bridge,
  that's a local engineering tender — OSR hands off cleanly at
  the approach abutments.
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
| **v3** ✅ (partial) | Parametric U-girder at [`mechanical-py/src/osr_mech/civil/ugirder.py`](../../mechanical-py/src/osr_mech/civil/ugirder.py) with 20 / 25 / 30 m spans under the one-mould constraint (done 2026-04-22); STEP artifacts at [`mechanical-py/catalog/civil/`](../../mechanical-py/catalog/civil/) round-trip into Revit / Tekla / Civil 3D. Precast L-unit platform edge at [`mechanical-py/src/osr_mech/civil/platform_l_unit.py`](../../mechanical-py/src/osr_mech/civil/platform_l_unit.py). Remaining for v3 full-complete: pier + abutment parametric kits + CERN-OHL-S v2 relicensing of the catalogue tree. | v0 |
| **v4** | Worked civil design for Samawah Line 1 (an 11 km at-grade stretch + 2 km elevated over the existing rail corridor + 1 km bridge over the Euphrates approach) | v3, RFC 0003 |
| **v5** | First-article viaduct erected at the Samawah pilot | v3 |

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
