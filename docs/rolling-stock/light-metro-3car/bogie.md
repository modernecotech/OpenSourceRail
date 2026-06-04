# Bogies — `light-metro-3car`

Six bogies per consist: two new powered bogies at the outer ends and
four converted freight trailer bogies under the remaining positions.
All bogies use the RFC 0022 suspension, wheelset, brake, and pivot
geometry; the converted trailer variant omits motors and gearbox.

## Bogie envelope (all six, common)

| Parameter | Value |
|---|---|
| Wheelbase (axle-to-axle) | 2 100 mm |
| Wheel diameter, new / worn | 760 / 680 mm |
| Wheelset type | Monobloc, machined per RFC 0022 |
| Wheel profile | S1002 on standard-gauge rail |
| Axle load (AW3, both axles) | ≤ 14 t each |
| Gauge | 1 435 mm standard gauge |
| Track-brake coil (magnetic track brake) | not fitted — per RFC 0008 §3.2 electric-only brake |

## Powered bogie (two per consist)

### Frame

- Welded H-frame, steel S355JR per EN 10025, EN 15085 CL1 welds.
- Length (axle-to-axle) 2 100 mm; width 2 400 mm; depth 300 mm.
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

Twin-bellows air spring + lateral damper (one pair per bogie):
- Air spring: Continental / ContiTech CF-series class, 55 °C
  continuous bellows rating.
- Levelling valves hold the centre door-zone floor within ± 5 mm
  from empty to AW3.
- Damper: KONI 32-series linear, 6 kNs/m at nominal velocity.
- Auxiliary rubber emergency bearer supports the car after air loss.

### Motor mount

Two PMSM axle-hung motors per powered bogie, one per axle. Motor
details in [`traction.md`](traction.md).

### Brake

- **Service + emergency:** axle-mounted brake disc on each axle.
  Caliper electromagnetic actuation — two calipers per disc.
- **Parking:** spring-applied, electromagnetic-release on the
  same caliper; cut-out spring force ≥ 12 kN per caliper.
- **WSP:** wheel-slide protection via the per-axle tacho input +
  `osr-brake` modulation (proptest-verified B4 conservative).

## Converted freight trailer bogie (four per consist)

Reused freight frames are stripped, inspected, and rebuilt to the OSR
wheelset/brake/suspension interface. Differences from the powered
bogie:

- **No motor.** All axles idle.
- **Brake:** same 600 mm disc on each axle for service /
  emergency / park.
- **Mass:** lower than the powered bogie by the omitted motors,
  gearboxes, and inverter cabling.

## Interfaces

- **Bogie-to-body pivot:** centre pin ring bearing, 400 mm
  diameter, PTFE slider.
- **Yaw restraint:** two longitudinal links per bogie with
  elastomeric bushes. No hydraulic yaw dampers (tangent speeds
  ≤ 25 m/s don't demand them on the RFC 0009 preset radii).
- **Power electrical:** 1 500 V DC + 24 V DC + 400 V AC through
  a cableguide at the centre pin; not through the pivot itself.
- **Air:** local secondary-suspension levelling only. No trainwide
  pneumatic brake or door supply per RFC 0008 §3.2.

## Interchangeability

Every powered bogie in every OSR deployment of this family is
identical. The converted trailer bogie shares:
- Frame geometry (drilling pattern).
- Suspension parts.
- Brake disc + caliper.
- Wheel monobloc.

So most bogie spares are shared across powered and trailer variants.

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
