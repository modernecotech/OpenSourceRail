# General arrangement — `light-metro-3car`

## Consist diagram

```
   ←── 17.0 m ──→←── 17.0 m ──→←── 17.0 m ──→

      Car A             Car B             Car C
   ┌─ M bogie ─ doors ─ t bogie ┐┌─ t bogie ─ doors ─ t bogie ┐┌─ t bogie ─ doors ─ M bogie ┐
   │ powered  low-floor centre ││ trailer  low-floor centre ││ powered  low-floor centre │
   │ end car  under-seat batt. ││ car      under-seat batt. ││ end car  under-seat batt. │
   └───────────────────────────┘└───────────────────────────┘└───────────────────────────┘
     M = powered bogie, t = trailer bogie
     Length over couplers = 51.0 m
```

- **Three self-contained cars**, semi-permanently coupled.
- **No driving cabs** — GoA 4 open-glass sensor cowls at both ends
  per RFC 0015, with heated RF-transparent glass, T-OBS sensors, and
  LED headlamp / marker-light clusters.
- **Six bogies total** — two standard 2-axle bogies per car.
- **Powered wheelsets:** one powered bogie at each outer end car,
  giving two powered bogies and four powered axles across the consist.
- **Battery:** 150 kWh sodium-ion per car under the longitudinal
  seats. The centre door zone stays low-floor and clear.
- **Roof:** PV strip per car, split around compact end HVAC modules.

## Key dimensions

| Parameter | Value | Source |
|---|---|---|
| Length over couplers | 51 000 mm | concept envelope: 3 × 17 m car modules |
| Car A length | 17 000 mm | modular car envelope |
| Car B length | 17 000 mm | modular car envelope |
| Car C length | 17 000 mm | modular car envelope |
| Body width (outer) | 2 850 mm | concept envelope, fits UIC 505-1 gauge |
| Height over rail (roof) | 3 450 mm | concept envelope, before roof equipment |
| Floor height (above top-of-rail) | 350 mm centre door/PRM zone; 760 mm high-floor end decks over bogies | low-floor access with standard bogies |
| Bogie wheelbase | 2 100 mm | RFC 0022 single-SKU bogie |
| Wheel diameter (new / worn) | 760 / 680 mm | RFC 0022 |
| Inter-bogie distance (within a car) | 11 000 mm | modular car envelope |
| Coupler face height (above ToR) | 720 mm | Scharfenberg Type 10 dim. |
| Headroom at doors | 2 000 mm | |
| Headroom at seats | 2 100 mm | |
| Passenger-compartment interior width | 2 700 mm | |

## Door positions

One large 1 400 mm-wide double-leaf plug door per car side in the
low-floor centre zone (3 door pairs per side for the consist).
Longer-platform variants scale dwell capacity by adding identical
cars, not by changing the car-side door pattern. Positioned:

- Each car: door centre at 8.5 m from the car end.

All doors are plug-outward doors per RFC 0008 §3.3 with 1 500 mm
clear opening at 2 000 mm height.

## Gauge compliance

UIC 505-1 static envelope:
- Width at floor level: 2 850 mm ≤ 3 150 mm limit ✓
- Height over ToR: 3 450 mm ≤ 4 320 mm limit ✓
- Dynamic outline (+ 80 mm lateral, + 50 mm vertical at max
  cant + sway): 2 930 × 3 500 mm — still inside the 3 150 ×
  4 320 mm boundary ✓

No interference with UIC 505-1 at any of the RFC 0009 track
presets (`heritage-tram` / `standard-urban` / `standard-metro`
/ `mainline-mixed`).

## Platform clearance

- Low-floor centre door and PRM zone at 350 mm ToR platform height.
  Each car steps/rises to high-floor end decks over the standard
  bogies; those raised zones are inside the saloon, away from the
  boarding threshold.
- Horizontal gap at door sill: ≤ 75 mm per UIC 741. Achieved by
  a 40 mm sliding skirt at each door that extends on dwell
  (retracted in motion).
- On curved platforms at RFC 0009 `standard-urban` minimum
  radius (90 m): the door-to-platform horizontal gap grows to
  ~110 mm — requires an 80 mm gap-filler flap at the door sill.

## Mass distribution (AW2, nominal loaded)

| Location | Mass (t) |
|---|---|
| Car A incl. powered + trailer bogie | 40 |
| Car B incl. two trailer bogies | 38 |
| Car C incl. trailer + powered bogie | 40 |
| **Total consist (tare + AW2 passengers)** | **118** |

Tare target = 98 t for the concept-aligned BOM; AW2 load = 19.8 t
(330 passengers × 60 kg average).

Distribution per axle under AW3 (crush load, 420 passengers ×
60 kg = 25.2 t):
- Powered and trailer bogies: ~10–12 t per axle depending on seated
  battery-side loading.

All ≤ 14 t per RFC 0008 §3.1 axle-load constraint ✓.

## Structural loading cases (for v2 FEA)

The design envelope the v2 CAD model is checked against:

- **EN 15227 Cat C-II** collision: 25 km/h train-to-obstacle.
  Cab crush zone absorbs. Anti-climbing features at both ends.
- **EN 12663 Cat P-III** car-body static: compressive end load
  640 kN; diagonal 600 kN. Welded S355 underframe/spaceframe
  carries the load path; composite side and roof panels are
  non-structural weather/aero skins.
- **Vertical accel:** ± 0.5 g normal service; ± 2 g emergency
  brake / collision.
- **Lateral accel:** ± 0.3 g through max-cant curve.

v1 of this doc does not include the FEA result; v2 does.

## Cross-refs
- Bogie detail → [`bogie.md`](bogie.md)
- Body structure → [`body.md`](body.md)
- Traction → [`traction.md`](traction.md)
- Interfaces → [`interfaces.md`](interfaces.md)
