# RFC 0020 — Crashworthiness (EN 15227)

**Status:** Draft — parametric spec only, no FEA ships with this RFC
**Date:** 2026-04-24
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0015 Driverless Operation](0015-driverless-operation.md)

## 1. Summary

Every OSR trainset must survive the EN 15227 crash-reference
scenarios **C-I** (train-to-train) and **C-III** (train-to-obstacle)
without passenger-compartment intrusion. Because OSR is *cabless*
([RFC 0015 §5.1](0015-driverless-operation.md#5-sensor-suite)), the
impact-absorption zone that commercial cabbed designs put in the
driver's cab has to live somewhere else. This RFC publishes the
energy-absorption-zone allocation that replaces it — the values
the mechanical-py parametric car body tracks and that vendors
must meet when supplying an OSR-compatible shell.

OSR v0.1 does **not** ship a full finite-element crash simulation.
What it ships is:

- A parametric energy budget per consist family.
- An allocation of that budget to three absorption zones on each
  end of the trainset.
- A published set of geometric constraints (crumple-zone length,
  anti-climber interface height, under-frame load path) the car
  body must honour.

A deployment must commission an EN 15227-certified FEA vendor to
verify the final design; this RFC gives that vendor a well-defined
target rather than a moving spec.

## 2. Non-goals

- **Not an FEA solver.** We specify targets; we do not solve the
  dynamics. Simcenter / Abaqus / LS-DYNA remains the right tool.
- **Not a material choice.** The body material is aluminium per
  [RFC 0008 §3.2](0008-rolling-stock-reference-design.md#3-unified-architecture--every-family); the RFC applies
  to any ductile alloy that meets EN 15085 weld class CP-C.
- **Not an obstacle-deflection spec.** Track-clearing plough
  (EN 15227 §6.5) lives in `osr-obstacle-detect`'s physical
  hardware spec, not here.

## 3. Reference scenarios

| Scenario | Description | Closing speed | Target |
|---|---|---|---|
| **C-I** | Collision with an identical trainset on tangent track | 36 km/h | No passenger-compartment intrusion; decel ≤ 7.5 g peak |
| **C-III** | Collision with a 15-tonne rigid obstacle (road vehicle at a level crossing) | 36 km/h | No passenger-compartment intrusion; anti-climber engages |
| **C-IV** (informational) | Collision at a level crossing with a light road vehicle | Not binding on urban metro per [RFC 0013 §9](0013-operations-rulebook.md#9-level-crossings) | — |

Scenarios C-II (obstacle on track) and C-V (tram-style) are
covered by deployment-specific assessments. Every OSR trainset
must certify C-I + C-III.

## 4. Energy budget per consist

Under the C-I scenario, two identical trainsets close at 36 km/h →
relative closing energy is `0.5 · 2·m · v²` where `m` is the consist
mass and `v` is 5 m/s per trainset. For the reference families
(RFC 0008 §3.3 seated + standing + interior fit-out):

| Consist | Mass tare + 6 p/m² | C-I closing energy |
|---|---|---|
| tram-2car | ~66 t | 1.65 MJ |
| light-metro-3car | ~120 t | 3.00 MJ |
| metro-4car | ~160 t | 4.00 MJ |
| metro-6car | ~240 t | 6.00 MJ |

These totals govern the absorption-zone sizing in §5.

## 5. Three-zone absorption layout

Each end of the trainset splits its contribution to the closing
energy across **three sequential zones**, each contributing a
known fraction of the total. This is the standard EN 15227
arrangement; what's specific to OSR cabless is that zones 1 + 2
previously lived inside a driver's cab and now live in the sensor-
cowl + forward under-frame section.

| Zone | Location | Share | Mechanism |
|---|---|---|---|
| **Zone 1 — Sacrificial cowl** | Sensor cowl front + anti-climber | 30 % | Controlled-crush foam + metal honeycomb within the cowl; sensors are lost but absorb ~0.45 MJ per end for a 3-car consist |
| **Zone 2 — Under-frame crumple** | Forward 2.5 m of under-frame between cowl and first bogie | 40 % | Tubular steel crumple cans; cuts into depot access but stays clear of passenger envelope |
| **Zone 3 — Anti-override interface** | End wall between under-frame crumple and first door | 30 % | Reinforced bulkhead; redistributes remaining energy into the body torsion ring |

Each end of every consist must provide the summed per-end budget
(half the closing-energy total for C-I, full for C-III).

## 6. Parametric geometry constraints

The mechanical-py car body + sensor cowl enforce these constraints
via the `Crashworthiness` helper in
[osr_mech.rolling_stock.car_body](../../mechanical-py/src/osr_mech/rolling_stock/car_body.py)
(added in v0.1). The CAD geometry **reserves** the zone
envelopes — vendor-supplied shells that fit in must meet the
mechanical targets below.

| Constraint | Value | Rationale |
|---|---|---|
| Zone 1 crumple length (sensor cowl) | ≥ 900 mm | Honeycomb deceleration band at 150 kN/m² crush stress |
| Zone 2 crumple length (under-frame) | ≥ 2 000 mm | Tubular can progressive collapse |
| Anti-climber pin height above rail | 760 mm (± 25) | EN 15227 §6.4 pin-on-pin interface |
| End bulkhead thickness | ≥ 40 mm aluminium or equivalent | Load-path continuity |
| Passenger compartment survival space (post-crash) | Body length ≥ 95 % of original | Egress path integrity |
| Peak longitudinal decel (passenger floor) | ≤ 7.5 g | EN 15227 occupant criterion |

## 7. Verification path

1. **Parametric check** (in-repo, pytest): the car body geometry
   reserves the Zone 1 + Zone 2 volumes. `test_tier1_additions.py`
   covers the envelope reservation.
2. **Static FEA** (external): linear analysis of the crumple-zone
   load paths by a licensed FEA vendor. Outputs: peak stress, first-
   yield energy.
3. **Dynamic FEA** (external): LS-DYNA / Abaqus explicit for each
   scenario. Outputs: decel curves, crush displacement, passenger-
   envelope intrusion check.
4. **Full-scale test** (per EN 15227): one test specimen per consist
   family, at the closing speed. Carried out by the type-approval
   authority; pass/fail gate for revenue service.

OSR-v0.1 closes steps 1 + documents the plan for 2–4. A deployment
budget must include the external FEA + physical-test cost —
typically EUR 1.5–3.0 M per consist family, amortisable across
every trainset in the family.

## 8. Non-OSR obstacle-plough interface

The obstacle-deflection plough (EN 15227 §6.5) fits onto the
sensor-cowl front within the Zone 1 envelope. The plough's 6°
deflection angle + 200 kN rating clears track-level debris without
triggering the cowl's sacrificial crush zone. Interface:

- 4× M24 bolts on a 400 × 200 pattern, pre-tapped in the cowl
  front.
- Plough mass ≤ 120 kg (included in Zone 1 budget).
- Catch pan + drain geometry published in the v0.2 hardware
  release.

## 9. Deployment checklist

- [ ] Commission an EN 15227 FEA analysis from a certified vendor
      (Politecnico di Milano, Newrail, Bombardier Legacy, or
      equivalent) against the §5 zone allocation.
- [ ] Confirm the vendor's crumple-can dimensions fit inside the
      parametric Zone 1 + Zone 2 envelopes.
- [ ] Budget for one full-scale test per consist family.
- [ ] File the type-approval evidence pack with the national rail
      regulator before first revenue day.

## 10. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-04-24 | v1 | Initial draft. Three-zone layout + energy budget + parametric constraints. |
