# RFC 0012 — Switches & Crossings (Physical)

**Status:** Draft — planning only, no mechanical drawings ship with this RFC
**Date:** 2026-04-22
**Depends on:** [RFC 0009 Track Design Standard](0009-track-design-standard.md), [RFC 0011 Civil Infrastructure Design Standard](0011-civil-infrastructure-design-standard.md)

## 1. Summary

OpenSourceRail commits to **three turnout tangents** (1:9, 1:14,
1:18.5) across every deployment. This RFC fixes the physical
hardware standard — switch machine, stretcher bars, detectors,
frog, heating — that the [`osr-wayside-points`](../../crates/osr-wayside-points/)
controller operates.

| Tangent | Divergent speed | Preset | Use case |
|---|---|---|---|
| **1:9** | 40 km/h | `standard-urban`, `standard-metro` (station ends) | The bread-and-butter metro turnout |
| **1:14** | 60 km/h | `standard-metro` (mainline crossovers), `mainline-mixed` | High-speed crossover between parallel tracks |
| **1:18.5** | 80 km/h | `mainline-mixed` only | Reserved for shared-corridor operation |

**Minimise switch count. Prefer trailing-point moves over
facing-point moves wherever possible.** Every switch is a
maintenance liability; every facing-point switch on a revenue
corridor is a SIL-4-rated safety asset.

## 2. Non-goals

- **Not a rail-industry standards body.** References EN 13232
  (turnout geometry), EN 13145 (sleepers), EN 13146 (fastening
  tests). No new ones published.
- **Not a level-crossing-gate policy manual.** Legal requirements
  for warning times, signage, barrier type vary per country; this
  RFC specifies the equipment envelope the deployment chooses from.
- **Not a points-heating policy for arctic climates.** Target
  regions hit ≤ 0 °C briefly in some mountain areas; a simple
  resistive points-heating circuit is specified. Sub-arctic
  deployments customise locally.
- **Not a ballast-cleaner or tamper spec.** Maintenance-of-way
  equipment is separately sourced; the turnout standard doesn't
  constrain its choice.

## 3. Why three tangents, not a continuum

Picking three standard turnout geometries covers the full operational
envelope while keeping tooling, inspection, and spares repeatable:

- **1:9** handles every station-throat and depot turnout. 40 km/h
  divergent speed is plenty for a metro that dwells 30 s at every
  stop.
- **1:14** handles mid-line crossovers on dedicated metro ROW where
  the trailing-point move is routine.
- **1:18.5** handles the shared-corridor edge case
  (`mainline-mixed` preset).
Operators never specify intermediate tangents (1:7, 1:10, 1:12).
Simplicity pays: one turnout mould, one stretcher-bar part
number, one switch-machine part number per tangent; three total
across the whole project.

## 4. Switch architecture

### 4.1 Mechanical

| Aspect | Choice |
|---|---|
| **Rail type** | UIC60E2 (60 kg/m) for 1:9 / 1:14 / 1:18.5. Matches the parent rail profile from RFC 0009. |
| **Switch blade** | Flexible switch blade, continuous machined profile; no bolt-on tip. The controlled planning envelopes are 7.8 m for 1:9, 11.8 m for 1:14, and 16.2 m for 1:18.5; the supplier drawing freezes the final machined length. |
| **Stock rail** | Standard-profile rail for length of the switch panel, bolted to the next panel. No welded joints inside the switch area. |
| **Slide chair** | Self-lubricating (graphite-filled bronze) — no daily greasing. Inspection every 30 days. |
| **Stretcher bars** | Two stretcher bars per switch (front + heel). Front bar integrates the position detector per §5. |
| **Frog** | Cast manganese steel, 13 % Mn, no moveable-point frog upstream — adds complexity and a failure mode without enough speed gain at our tangents. Swing-nose frog is an opt-in v2 extension for 1:14 / 1:18.5. |
| **Check rails** | Bolted to the running rail opposite the frog. Fixed-gap (no cold-weather compensation). |
| **Sleepers** | Pre-stressed concrete switch sleepers per EN 13145; spacing compressed from the 600 mm mainline standard to 540 mm through the switch panel. |

### 4.2 Switch machine

Single vendor / single machine family across every deployment:

| Aspect | Choice |
|---|---|
| **Type** | Electro-mechanical, BLDC motor + planetary gearbox + crank. No hydraulic switch machines — hydraulic packs are top-quartile maintenance items. |
| **Throw force** | 6 kN nominal, 12 kN peak (matches standard metro load at ≤ 25 °C ambient). |
| **Throw time** | ≤ 3 s from rest to locked, including detection settling. |
| **Detection** | Dual-redundant position sensors (A + B, 2oo2 agreement) at the front stretcher bar. Integrated with [`osr-wayside-points`](../../crates/osr-wayside-points/)'s `SwitchObservation` reporting. |
| **Locking** | Mechanical lock at the tip via the front stretcher bar; blade cannot move when locked. No electrical-only locking. |
| **Heating** | 3 kW resistive heating strip along the slide chair + blade foot, thermostatically switched at +5 °C ambient. Powered from the trackside 230 V AC supply; dropped to LVDC aux in depot areas. |
| **Cabinet** | IP67 aluminium enclosure matching the W-SBC form factor ([RFC 0007 §6](0007-hardware-reference-designs.md#6-class-w-sbc-wayside)). Motor + controller share the cabinet. |

### 4.3 Facing vs trailing

- **Facing-point switch (FPS)**: a switch the approaching train
  *has to trust* to guide it onto the right track. SIL-4 asset.
  Every FPS is a permanent W-SBC deployment ([`osr-wayside-points`](../../crates/osr-wayside-points/))
  with consensus-log-backed position observation.
- **Trailing-point switch (TPS)**: a switch a train merges into
  from one of two converging tracks. The train flips the blade
  on its way through; no pre-positioning required. SIL-2 asset —
  the controller still reports position for dispatch awareness,
  but the safety case doesn't rely on it being at any specific
  position when a train approaches.

**Every deployment counts and minimises FPSes.** A typical
linear deployment instance ([RFC 0003](0003-samawah-reference-deployment.md))
has 0 FPSes on a linear line (only crossovers at depot entry,
which are TPSes on the way in and FPSes only if an operator
reverses a train on the mainline — normally handled by the
turnback at the terminal station). Any deployment with > 8
FPSes per line is a design red flag.

## 5. Position detection + integration

Per RFC 0007 §6, every wayside site including switch sites hosts
a W-SBC. The switch-detection chain is:

```text
  front stretcher bar ──► A-channel sensor ──► ADC ──► W-SBC
                           (inductive, fail-open)           │
                           B-channel sensor ──► ADC ──┘
                           (inductive, fail-open)           │
                                                            ▼
                                            osr-wayside-points ──► SwitchObservation ──► consensus log
```

Two channels are redundant by construction. Any disagreement,
or either channel reading "indeterminate," yields
`DetectedPosition::Unknown` — the fail-restrictive behaviour
already encoded in [`osr-wayside-points`](../../crates/osr-wayside-points/)'s W2 proptest + Kani
property.

**No track circuits in the switch zone.** Detection is by
dedicated stretcher-bar sensors. Axle-counters sit outside the
switch panel as a redundant train-detection sensor — not as the
switch-position detector.

## 6. Level crossings

Level crossings remain a specific category handled by
[`osr-level-crossing`](../../crates/osr-level-crossing/). The
physical equipment envelope:

| Element | Spec |
|---|---|
| **Barrier type** | Half-barrier, counterweighted, 4 m arm length (8 m arm at 2-lane crossings). Pneumatic or electro-mechanical drive; no hydraulic. |
| **Barrier descent time** | 8–12 s (meets UIC 762 and most national rules). |
| **Warning lights** | Alternating red flashers + audible warning bell, 30 s pre-barrier activation. |
| **Road approach warning** | 150 m advance warning sign + surface markings. |
| **Train detection** | Redundant axle-counter pairs at entry + exit; feeds `osr-level-crossing`'s five-state FSM. |
| **Emergency stop strip** | 600 mm rubber strip on the road at the rail approach — survives being struck, triggers an emergency barrier lift only via a dispatcher OK. |
| **Canopy / shelter** | Optional on the road side for the approach warning cabinet; not on the rail side. |

Approach warning time is 30 s minimum, per [`osr-level-crossing`](../../crates/osr-level-crossing/)'s
invariant, irrespective of design speed. Operators who want a
longer approach configure per-crossing; upstream defaults to 30 s.

## 7. Crossings (diamonds)

Rail-on-rail diamonds (one track crossing another at grade)
are **not** in the standard catalogue. They are:

- Expensive to maintain (high impact load at the flangeway gaps).
- A top-quartile derailment site.
- A needless complication on a new-build corridor where junctions
  are trivially re-routed around parallel alignments.

If a deployment's geometry seems to demand a diamond, the
alignment should be revisited. **Grade-separated crossings
(elevated over at-grade) are the catalogue answer.** Per RFC 0011
§5 those are standard viaduct spans.

## 8. Turnout geometry table (per tangent)

Planning-grade per EN 13232. Exact radii / lead lengths per
manufacturer's standard drawing.

| Tangent | Angle | Switch lead length | Total envelope | Blade envelope | Through-radius | Turnout sleepers | Divergent speed |
|---|---|---|---|---|---|---:|---|
| 1:9 | 6.3° | 23 m | 27 m | 7.8 m | 190 m | 42 | 40 km/h |
| 1:14 | 4.1° | 37 m | 43 m | 11.8 m | 500 m | 68 | 60 km/h |
| 1:18.5 | 3.1° | 49 m | 60 m | 16.2 m | 900 m | 94 | 80 km/h |

Any deployment using a non-listed tangent is outside the upstream
envelope.

## 9. Auto-gen pipeline

At deployment-generation time, the emitter needs to know where
switches go. Today's pipeline:

- **Terminal stations:** the emitter already tags first/last
  stations as `terminal` ([RFC 0010 §12](0010-station-design-standard.md#12-self-consistency-with-rfc-0008--0009)).
  A future v2 of the emitter can emit a `turnback_switch` entry
  at every `terminal` using tangent 1:9.
- **Depot entries:** the `depot-terminal` archetype gets a depot
  fan of 1:9 turnouts. The fan geometry is parametric in the
  depot stall count (see [RFC 0014](0014-depot-design-standard.md)).
- **Interchange stations:** no switches. Lines cross grade-
  separated; see RFC 0011 §7.

Emitter v2 work is the short follow-on that pairs with RFC 0010
v2 / RFC 0011 v2.

## 10. Pitfalls and decisions

- **Only three tangents in the catalogue.** A deployment team
  pushing for a 1:10 or 1:12 to "match their legacy network" is
  asking for bespoke mould work. The cost math almost always
  favours standardising on 1:9 + slightly-reduced divergent
  speed where needed.
- **Electro-mechanical switch machines, not hydraulic.** Hydraulic
  is smoother and quieter; it is also top-quartile for
  maintenance and has a top-quartile environmental liability
  (pack-oil leaks into track ballast). Electro-mechanical wins
  the mission alignment.
- **Fixed frog, not moveable-point.** Moveable-point frogs are
  smoother at 80 km/h+; at our tangent speeds they don't pay
  back the complexity. Opt-in at 1:14 / 1:18.5 in v2 if the
  acoustic argument becomes dominant.
- **No diamonds.** Grade-separate, or re-route. Operators used
  to network-style legacy rail sometimes push for diamonds on
  psychological grounds ("my country's rail has them"); we
  do not.
- **Level crossings are a necessary evil.** Every road-rail
  level crossing added is a maintenance, safety, and service-
  punctuality liability. The auto-gen emitter counts them per
  km of line; deployments with > 3 level crossings per km are
  flagged as a soft gate for review.

## 11. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** | `lib/templates/switches.toml` updated to match this RFC | v0 |
| **v2** ✅ | Emitter emits turnback at every terminal archetype + one `no-9-mainline` per stall at every `depot-terminal` (yard fan) (done 2026-04-22) | v0, RFC 0010 v2 |
| **v3** | Reference CAD drawings for the 1:9 turnout under CERN-OHL-S v2 | v1 |
| **v4** | Generated switch-bill for the current pilot city model, including terminal turnbacks, depot fans, and any required mainline crossovers | v1, RFC 0003 |

## 12. Relationship to existing work

- [`lib/templates/switches.toml`](../../lib/templates/switches.toml)
  — the Lego-block schema. v1 amends to drop any non-catalogue
  tangents.
- [`crates/osr-wayside-points`](../../crates/osr-wayside-points/) —
  the W-SBC software controller. Already W1–W6 verified
  (RFC 0004 §M4 work). No software change for v0 of this RFC.
- [`crates/osr-level-crossing`](../../crates/osr-level-crossing/)
  — the level-crossing 5-state FSM. Already deployed; this RFC
  pins the physical equipment envelope that feeds it.
- [`crates/osr-interlocking`](../../crates/osr-interlocking/) —
  consumes `SwitchObservation` log entries. Semantics unchanged.

## 13. Open questions

1. **Swing-nose frog opt-in rule.** At what line speed / ridership
   does the acoustic / rail-wear benefit cross over the added
   mechanical complexity? Revisit at v3.
2. **Shared-corridor freight impact.** On `mainline-mixed`, a
   freight train's 22.5 t axle load over a 1:9 switch daily
   accelerates wear substantially. The catalogue's assumption
   is that shared corridors use 1:14 minimum. Verify with a
   real mixed-corridor pilot.
3. **Seasonal-heated switches in hot climates.** +50 °C
   summer ambient can rail-expand beyond the standard switch
   tolerance. Temperature-compensated switch geometry is a
   future addendum for deployment-scale turnout counts.
4. **Single-vendor switch-machine risk.** The project's
   simplicity bet locks the fleet to one machine family. What
   happens if that vendor exits the market? Mitigation: the
   reference drawings under CERN-OHL-S v2 let any replacement
   machine vendor fit into the footprint.

## 14. Done criteria

- [x] Three (plus tram) tangents committed (§1)
- [x] Switch architecture (§4) + detection chain (§5)
- [x] Level-crossing equipment envelope (§6)
- [x] Diamonds out of scope with rationale (§7)
- [x] Geometry table per tangent (§8)
- [x] Auto-gen implications (§9)
- [x] Pitfalls + alternatives (§10)
- [x] Rollout ordered (§11)
- [x] Relationship to software + templates (§12)

The next session picks up at **v1 — `lib/templates/switches.toml`
update**, a short editorial PR.
