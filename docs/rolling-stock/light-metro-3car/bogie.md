# Bogies — `light-metro-3car`

Three bogies per consist. Two driving bogies (bogies 1, 3) with
2 axles, 1 powered axle each + 1 idle. One Jacobs intermediate
bogie (bogie 2) under the Car B articulation, 2 axles both
idle.

## Bogie envelope (all three, common)

| Parameter | Value |
|---|---|
| Wheelbase (axle-to-axle) | 1 800 mm |
| Wheel diameter, new / condemning | 860 / 790 mm |
| Wheelset type | Monobloc, machined per UIC 510-2 |
| Wheel profile | S1002 (1 435 gauge) or Ri60 (1 000 gauge variant) |
| Axle load (AW3, both axles) | ≤ 14 t each |
| Gauge | 1 435 mm (default) / 1 000 mm (variant) |
| Track-brake coil (magnetic track brake) | not fitted — per RFC 0008 §3.2 electric-only brake |

## Driving bogie (bogies 1 and 3)

### Frame

- Welded H-frame, steel S355JR per EN 10025, EN 15085 CL1 welds.
- Length (axle-to-axle) 1 800 mm; width 2 100 mm; depth 300 mm.
- 4 suspension pedestals — 1 per axle end.

### Primary suspension

Chevron rubber springs (one per axle end):
- Vertical stiffness: 1 500 kN/m nominal per spring.
- Lateral stiffness: 5 000 kN/m.
- No shock absorbers at primary level (the chevron's internal
  damping is sufficient).
- Service interval: replace every 10 years or on inspection
  finding; visual inspection every 7 days per RFC 0013 M5.

### Secondary suspension

Steel coil springs + viscous damper (one per bogie end):
- Coil: progressive rate, 80 kN/m at nominal load to 160 kN/m at
  AW3.
- Damper: KONI 32-series linear, 6 kNs/m at nominal velocity.
- **No air spring.** Maintenance-free at the service interval.

### Motor mount

One PMSM axle-mount motor per bogie, on the centre axle of the
driving bogie (the forward-facing axle of bogies 1 and 3 per
the RFC 0008 "50 % powered wheelsets" allocation). Motor details
in [`traction.md`](traction.md).

### Brake

- **Service + emergency:** 600 mm-diameter brake disc on the
  trailing axle of each driving bogie (one disc per bogie).
  Caliper electromagnetic actuation — two calipers per disc.
- **Parking:** spring-applied, electromagnetic-release on the
  same caliper; cut-out spring force ≥ 12 kN per caliper.
- **WSP:** wheel-slide protection via the per-axle tacho input +
  `osr-brake` modulation (proptest-verified B4 conservative).

## Jacobs bogie (bogie 2, under Car B articulation)

Same basic envelope as driving bogie, with differences:

- **No motor.** All axles idle.
- **Articulation pivot:** spherical-plain bearing at the bogie
  centre, ±4° rotation between Car A's end and Car C's end of
  Car B.
- **Brake:** same 600 mm disc on each axle for service /
  emergency / park (2 discs total per Jacobs bogie — redundant
  braking path through the consist's centre).
- **Mass:** 7 t (vs driving bogie 9 t) — the saved motor mass
  reduces unsprung mass under the articulation.

## Interfaces

- **Bogie-to-body pivot:** centre pin ring bearing, 400 mm
  diameter, PTFE slider.
- **Yaw restraint:** two longitudinal links per bogie with
  elastomeric bushes. No hydraulic yaw dampers (tangent speeds
  ≤ 25 m/s don't demand them on the RFC 0009 preset radii).
- **Power electrical:** 1 500 V DC + 24 V DC + 400 V AC through
  a cableguide at the centre pin; not through the pivot itself.
- **Air:** none. (No pneumatic brake system per RFC 0008 §3.2.)

## Interchangeability

Every driving bogie in every OSR deployment of this family is
identical. Bogies 1 and 3 are interchangeable in the shop
(direction of travel is not a bogie property — it's set by the
cab that's active).

The Jacobs bogie is a different SKU from the driving bogie
(no motor mount, no traction contactor block) but shares:
- Frame geometry (drilling pattern).
- Suspension parts.
- Brake disc + caliper.
- Wheel monobloc.

So ~70 % of the bogie spares inventory is shared across the
three bogie types.

## Weld classes (EN 15085)

| Assembly | Class |
|---|---|
| Frame primary welds | CL1 |
| Motor mount welds | CL1 |
| Brake caliper mount | CL1 |
| Cable-guide mount | CL3 |
| Non-structural covers | CL4 |

Per EN 15085, every CL1 weld is radiographically inspected at
the certified shop.

## v2 deliverables (not in v1)

- Dimensioned assembly drawings per EN 15016 / ISO 128.
- FEA: frame stress under AW3 + dynamic accelerations.
- FRA: fatigue-endurance curves over 1M simulated load cycles.
- Weld-quality records template (EN 15085 compliance file).
