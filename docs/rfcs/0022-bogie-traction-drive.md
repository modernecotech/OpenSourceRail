# RFC 0022 — Bogie + Traction Drive Reference Design

**Status:** Draft — single bogie SKU across every family
**Date:** 2026-04-24
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0015 Driverless Operation](0015-driverless-operation.md), [RFC 0021 Battery Traction](0021-battery-traction.md)

## 1. Summary

Every self-contained OSR car rides on **two standard 2-axle pivoting
bogies**: one powered bogie and one trailer bogie. The powered bogie
has both axles motored, with
**axle-hung PMSM traction motors**, a **single-stage parallel
spur gearbox** at 6.5 : 1, **760 mm new / 680 mm worn wheels**,
**chevron rubber-metal primary suspension**, and **air-spring
secondary suspension** with levelling valves spec'd for 55 °C
continuous operation.

**One bogie SKU** scales across every consist family:

| Family | Powered bogies | Trailer bogies | Continuous power |
|---|---|---|---|
| urban-shuttle-1car | 1 | 1 | 360 kW |
| tram-2car | 2 | 2 | 720 kW |
| light-metro-3car | 3 | 3 | 1 080 kW |
| metro-4car | 4 | 4 | 1 440 kW |
| metro-6car | 6 | 6 | 2 160 kW |

A **trailer bogie** is the same frame + suspension + wheelset
hardware as a motor bogie with the motor + gearbox omitted — so
a trailer SKU is the motor SKU minus two line items. Depots
stock one bogie pattern and one motor pattern. Longer trains are
made by coupling more identical self-contained cars, not by changing
the motorisation pattern.

## 2. Non-goals

- **Not a wheel-hub direct-drive design.** Seductive for 100 %
  low-floor trams; wrong for OSR because (a) spares pipeline is
  limited to ~3 global vendors (Siemens SYNTEGRA, ZF, TSA),
  (b) unsprung mass is actually *higher* once the hub bearing is
  added.
- **Not a Jacobs-bogie articulation.** Jacobs shares one bogie
  between adjacent cars; it saves weight but welds the family
  structure. OSR keeps per-car bogies so a 3-car and a 4-car use
  the same underframe template.
- **Not a structural bogie design.** The parametric CAD gives a
  geometric shell + published interface dimensions; structural
  FEA is a vendor responsibility (Škoda Transportation, CAF,
  Voestalpine VAE — three known suppliers with MENA references).
- **Not a heritage-bogie retrofit.** Where a brownfield deployment
  has dormant freight stock (e.g. Samawah's 300–800 stored wagons
  per [RFC 0003 §2.1](0003-samawah-reference-deployment.md#21-physical-asset-anchor--samawah-is-brownfield-not-greenfield)),
  the OSR consist gets a **fresh OSR bogie frame** with **recovered
  axles re-machined to 760 mm**, **recovered axleboxes + bearings**
  (post-NDT), and **new chevron primary + air-spring secondary**.
  Recovered legacy bogies are NOT spliced into the OSR consist —
  see [RFC 0027 §6](0027-brownfield-pilot-asset-recovery.md#6-phase-3--first-article-osr-trainset-1224-months)
  for the component-level mapping.

## 3. Reference dimensions

| Parameter | Value | Rationale |
|---|---|---|
| Bogie wheelbase (axle centres) | 2 100 mm | Balances curve tracking + hunting stability at ≤ 80 km/h |
| Bogie frame length | 3 500 mm | Wheelbase + axle-box footprint + suspension pedestals |
| Bogie frame width (between side beams) | 2 400 mm | Inside the body envelope; leaves 125 mm clearance per side |
| Wheel diameter (new) | 760 mm | Metro-standard — widest global wheel forging catalogue (Lucchini, Valdunes, CAF) |
| Wheel diameter (worn) | 680 mm | 40 mm re-profiling budget over life |
| Track gauge | 1 435 mm (standard) | Per RFC 0009 §2 |
| Axle load (laden) | ≤ 14 t | RFC 0008 §3.1 — comfortable inside UIC mainline limits |
| Pivot height above rail | 580 mm | Low enough for the raised bogie-floor zone to clear with margin |

## 4. Traction drive

### 4.1 Motor

- **Type:** permanent-magnet synchronous (PMSM), axle-hung.
- **Continuous rating:** 180 kW per axle at line voltage (train DC
  link nominal 1 500 V).
- **Peak rating:** 320 kW per axle for acceleration windows
  (≤ 60 seconds duty).
- **Cooling:** forced-air (underframe fan) or water-jacketed
  depending on ambient; high-ambient deployments use water.
- **Reference SKU class:** Traktionssysteme Austria PMM-2, TSA
  TMR-180, or equivalent catalogue unit ≤ 620 kg per motor.

### 4.2 Gearbox

- **Type:** single-stage parallel spur, helical teeth, hollow
  output shaft riding on the wheelset axle.
- **Ratio:** 6.5 : 1.
- **Lubrication:** forced oil circulation, reservoir at the
  gearbox housing, filter + sensor accessible from the pit.
- **Reference SKU class:** Voith BS 540, Flender RGB-400, Siemens
  Flender catalogue.

### 4.3 Why axle-hung + gearbox (not wheel-hub direct-drive)

| Criterion | Axle-hung + gearbox | Wheel-hub direct-drive |
|---|---|---|
| Unsprung mass | Motor mass split between frame (sprung) + axle (unsprung) | Full motor mass is unsprung |
| Spares pipeline | Global catalogue from ≥ 8 suppliers | 3 global suppliers, no MENA |
| Wheel-lathe compatibility | Every depot with a lathe can re-profile | Hub bearing complicates re-profiling |
| Maintenance access | Pit + side | Wheel removal required |
| Efficiency | 96–97 % PMSM × 98 % gearbox = ~94 % | 96 % PMSM × 100 % = 96 % (marginally better) |
| Low-floor compatibility | Raised floor over bogie, low-floor centre door zone | True 100 % low floor possible |

OSR does not need 100 % low-floor compatibility: the large centre
door zone is low floor and level with the platform, while the floor
ramps up over the standard bogies. So the efficiency gap doesn't
offset the spares-pipeline win.

## 5. Suspension

### 5.1 Primary — chevron rubber-metal

- **Type:** chevron-pattern rubber-to-metal block (e.g. Trelleborg
  Meta-C, Metalastik SSB), one per axle box, eight per bogie.
- **Vertical stiffness:** ~3 kN/mm per pack.
- **Lateral + longitudinal:** tuned by pack geometry — no
  separate primary-lateral link required.
- **Maintenance:** zero for the rubber; axle boxes are the only
  touch point.
- **Why chevron:** eliminates the hydraulic-damper creep failure
  mode at 50 °C ambient.

### 5.2 Secondary — air spring

- **Type:** twin-bellows air spring with auxiliary rubber
  emergency bearer (in case of air loss).
- **Levelling valves:** pneumatic height-control, maintains
  the centre door-zone floor within ± 5 mm across empty-to-crush-load.
- **Temperature rating:** 55 °C continuous bellows operation —
  non-negotiable for Samawah.
- **Reference SKU class:** Continental CF-series, ContiTech
  Secondary Air Spring family (both have Gulf refs).
- **Lateral damper:** one per side, hydraulic, resists hunting
  oscillation.

### 5.3 Anti-roll bar

One transverse torsion bar per bogie, linked to the car body via
drop links. Reduces body roll into curves by ~35 %.

## 6. Brake

- **Disc count:** one axle-mounted disc per axle = 2 per bogie.
- **Caliper:** electromagnetic, one per disc.
- **Disc material:** forged carbon steel (replaceable; 400 mm
  diameter × 45 mm thick nominal).
- **Holding brake:** spring-applied, electromagnetic-release on
  the same caliper, fitted to one axle per bogie.
- **Wheel-slide protection:** speed sensor per wheel; `osr-brake`
  WSP loop modulates caliper current.

## 7. Car-underframe interface

- **Pivot:** single central ball joint, 300 mm diameter, 580 mm
  above rail head.
- **Traction link:** single longitudinal ball-joint rod from the
  bogie frame to the car body, takes traction + braking load.
- **Side bearers:** two polymer slide blocks per bogie (no
  spherical roller bearing — cost + maintenance win).
- **Air supply:** two pneumatic lines to the secondary air spring;
  one levelling line. There is no pneumatic or hydraulic brake
  supply. Quick-disconnect cartridge coupling.
- **Electrical:** bogie-frame-mounted terminal cabinet; motor
  three-phase + encoder + resolver cables via quick-connect.

## 8. Motorisation pattern per family

```
urban-shuttle    [M/t]                       — 1 motor bogie, 1 trailer
                  car 1

tram-2car        [M/t]────[M/t]              — 2 motor, 2 trailer
                  car 1    car 2

light-metro-3car [M/t]────[M/t]────[M/t]     — 3 motor, 3 trailer
                  car 1    car 2    car 3

metro-4car       [M/t]────[M/t]────[M/t]────[M/t]
                  car 1    car 2    car 3    car 4

metro-6car       [M/t]────[M/t]────[M/t]────[M/t]────[M/t]────[M/t]
                  car 1    car 2    car 3    car 4    car 5    car 6
```

Every [M/t] car is the same self-contained module: one motor bogie
plus one trailer bogie. The motor bogie is frame + suspension +
wheelset + two motors + gearbox + brake. The trailer bogie is the
same assembly minus the motor + gearbox.

## 9. Verification path

1. **Geometric** (in-repo): parametric CAD + test asserts wheel
   gauge, wheelbase, frame clearance envelope.
2. **Kinematic** ([osr_mech.clearance](../../mechanical-py/src/osr_mech/clearance/)): the
   swept kinematic envelope fits inside the reference track gauge
   on the tightest curve radius (RFC 0009 min 150 m).
3. **Dynamic FEA** (external): vendor does multi-body dynamics
   on Simpack / GENSYS for ride quality + derailment coefficients
   per EN 14363.
4. **Fatigue test** (external): full-scale test per EN 13749 for
   the bogie frame.

## 10. Reference vendors (MENA-serviceable)

- **Bogie frame + assembly:** CAF Signalling, Škoda Transportation,
  Voestalpine VAE, Gmeinder Lokomotiven.
- **PMSM motor:** Traktionssysteme Austria, ABB Traction, Škoda
  Electric.
- **Gearbox:** Voith, Flender (Siemens Group), ZF.
- **Air spring:** Continental AG, ContiTech (same group).
- **Chevron rubber:** Trelleborg, Vulkan Coupling.
- **Wheelset forging:** Lucchini RS (Italy), Valdunes (France),
  CAF (Spain).
- **Brake caliper:** Knorr-Bremse, Wabtec Faiveley.

## 11. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-05-01 | v2 | Rationalised to one powered bogie plus one trailer bogie per self-contained car. |
| 2026-04-24 | v1 | Initial draft. Single-SKU 2-axle Bo-Bo, axle-hung PMSM, chevron + air suspension, motorisation pattern per family. |
