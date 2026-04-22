# General arrangement — `light-metro-3car`

## Consist diagram

```
   ←────── 22.0 m ──────→←── 21.0 m ──→←────── 22.0 m ──────→

      Car A (driving)       Car B (motor)     Car C (driving)
   ┌─ cab ─ bogie 1 ──┐┌─ bogie 2 ──┐┌─ bogie 3 ── cab ─┐
   │ │┐          ┌┐  ││   ┌┐   ┌┐  ││  ┌┐          ┐│ │
   │ ││          ││  ││   ││   ││  ││  ││          ││ │
   │ │┘          └┘  ││   └┘   └┘  ││  └┘          └│ │
   └──────────────────┘└──────────────┘└──────────────────┘
     |art.| = articulation joint above bogie 2 (Jacobs)
     Length over couplers = 65.0 m
```

- **Three cars, two articulation joints** (Car A ↔ Car B,
  Car B ↔ Car C). Car B is a "floating" intermediate car
  supported only by the Jacobs bogie at its centre and the end
  articulation joints into A and C.
- **Two driving cabs** — one at each end of the consist. Either
  cab drives the consist; terminal turnaround is a cab transfer
  (per RFC 0013 §4.1 D5).
- **Three bogies total** — two at Car A / Car C outer ends, one
  Jacobs bogie under the Car B articulation. All 2-axle.
- **Powered wheelsets:** bogies 1 and 3 are powered (50 % powered
  wheelsets per RFC 0008 §3.2). Bogie 2 (Jacobs) is an unpowered
  trailer.

## Key dimensions

| Parameter | Value | Source |
|---|---|---|
| Length over couplers | 65 000 mm | RFC 0008 §1 |
| Car A length (outer) | 22 000 mm | design envelope |
| Car B length (inner) | 21 000 mm | design envelope |
| Car C length (outer) | 22 000 mm | design envelope |
| Body width (outer) | 2 700 mm | fits UIC 505-1 gauge |
| Height over rail (roof) | 3 800 mm | fits UIC 505-1 |
| Floor height (above top-of-rail) | 350 mm | low-floor per RFC 0008 §3.3 |
| Bogie wheelbase | 1 800 mm | small wheelbase for RFC 0009 `standard-urban` min radius 90 m |
| Wheel diameter (nominal / condemning) | 860 / 790 mm | UIC 510-2 |
| Inter-bogie distance (within a car) | 14 000 mm | Car A / Car C |
| Jacobs bogie centre-of-rotation to end articulations | 3 500 mm | |
| Coupler face height (above ToR) | 720 mm | Scharfenberg Type 10 dim. |
| Headroom at doors | 2 000 mm | |
| Headroom at seats | 2 100 mm | |
| Passenger-compartment interior width | 2 580 mm | |

## Door positions

Two 1 300 mm-wide plug doors per car side (total 12 doors per
side for the consist — 12 door pairs = 24 doors). Positioned:

- Car A: door centres at 5.0 m + 17.0 m from the cab end.
- Car B: door centres at 5.0 m + 16.0 m from the Car-A-facing
  end of Car B.
- Car C: mirror of Car A.

All doors are plug-outward doors per RFC 0008 §3.3 with 1 250 mm
clear opening at 2 000 mm height.

## Gauge compliance

UIC 505-1 static envelope:
- Width at floor level: 2 700 mm ≤ 3 150 mm limit ✓
- Height over ToR: 3 800 mm ≤ 4 320 mm limit ✓
- Dynamic outline (+ 80 mm lateral, + 50 mm vertical at max
  cant + sway): 2 780 × 3 850 mm — still inside the 3 150 ×
  4 320 mm boundary ✓

No interference with UIC 505-1 at any of the RFC 0009 track
presets (`heritage-tram` / `standard-urban` / `standard-metro`
/ `mainline-mixed`).

## Platform clearance

- Low-floor at 350 mm ToR platform height ≡ consist floor
  height. Level boarding is gap-and-step free per RFC 0010
  §4.2.
- Horizontal gap at door sill: ≤ 75 mm per UIC 741. Achieved by
  a 40 mm sliding skirt at each door that extends on dwell
  (retracted in motion).
- On curved platforms at RFC 0009 `standard-urban` minimum
  radius (90 m): the door-to-platform horizontal gap grows to
  ~110 mm — requires an 80 mm gap-filler flap at the door sill.

## Mass distribution (AW2, nominal loaded)

| Location | Mass (t) |
|---|---|
| Car A (driving) incl. bogie 1 | 80 |
| Car B (intermediate, motor) incl. ½ of Jacobs | 55 |
| Car C (driving) incl. bogie 3 | 80 |
| **Total consist (tare + AW2 passengers)** | **215** |

Tare = 195 t per RFC 0008 §1; AW2 load = 20 t (360 passengers
× 60 kg average).

Distribution per axle under AW3 (crush load, 540 passengers ×
60 kg = 32 t):
- Bogies 1 + 3 (powered, 2 axles each): ~13.5 t per axle.
- Bogie 2 (Jacobs, 2 axles): ~13 t per axle.

All ≤ 14 t per RFC 0008 §3.1 axle-load constraint ✓.

## Structural loading cases (for v2 FEA)

The design envelope the v2 CAD model is checked against:

- **EN 15227 Cat C-II** collision: 25 km/h train-to-obstacle.
  Cab crush zone absorbs. Anti-climbing features at both ends.
- **EN 12663 Cat P-III** car-body static: compressive end load
  640 kN; diagonal 600 kN. Aluminium extruded profile with
  6 mm skin min.
- **Vertical accel:** ± 0.5 g normal service; ± 2 g emergency
  brake / collision.
- **Lateral accel:** ± 0.3 g through max-cant curve.

v1 of this doc does not include the FEA result; v2 does.

## Cross-refs
- Bogie detail → [`bogie.md`](bogie.md)
- Body structure → [`body.md`](body.md)
- Traction → [`traction.md`](traction.md)
- Interfaces → [`interfaces.md`](interfaces.md)
