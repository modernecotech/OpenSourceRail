# General arrangement — `light-metro-3car`

## Consist diagram

```
   ←── 17.0 m ──→←── 17.0 m ──→←── 17.0 m ──→

      Car A             Car B             Car C
   ┌─ M bogie ─ 2 doors ─ t bogie ┐A1┌─ t bogie ─ 2 doors ─ t bogie ┐A2┌─ t bogie ─ 2 doors ─ M bogie ┐
   │ powered  low-floor centre │  │ trailer  low-floor centre │  │ powered  low-floor centre │
   │ end car  under-seat batt. │  │ car      under-seat batt. │  │ end car  under-seat batt. │
   └───────────────────────────┘  └───────────────────────────┘  └───────────────────────────┘
     M = powered bogie, t = trailer bogie
     A1/A2 = semi-permanent articulated gangway modules
     Length over couplers = 51.0 m
```

- **Three self-contained cars**, joined by two semi-permanent
  articulated gangway modules.
- **No driving cabs** — GoA 4 identical A/B-end multi-part fiberglass
  sensor cowls at both ends per RFC 0015, with heated RF-transparent
  glass, T-OBS sensors, and LED headlamp / marker-light clusters.
- **No cab bulkhead** — the front and rear passenger ends are not
  walled off; the saloon remains open to the segmented glass end panes
  so passengers see through both driverless ends.
- **Six bogies total** — two standard 2-axle bogies per car.
- **Two articulations total** — lower spherical pivot/drawbar, upper
  roll-yaw-pitch links, double-wall bellows, segmented turntable floor,
  and separated trainline routing at each carbody interface.
- **Powered wheelsets:** one powered bogie at each outer end car,
  giving two powered bogies and four powered axles across the consist.
- **Battery:** 150 kWh sodium-ion per car under the longitudinal
  seats. The 10 m centre door zone stays low-floor and clear.
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
| Floor height (above top-of-rail) | 350 mm, 10 m low-floor centre door/PRM zone; 760 mm, ~3 m high-floor end decks over bogies | low-floor access with standard bogies |
| Bogie wheelbase | 2 100 mm | RFC 0022 single-SKU bogie |
| Wheel diameter (new / worn) | 760 / 680 mm | RFC 0022 |
| Inter-bogie distance (within a car) | 11 000 mm | modular car envelope |
| Articulation module length envelope | 1 120 mm | straddles each carbody interface; does not add to consist length |
| Articulation passage width | 1 650 mm | walk-through gangway target before trim tolerances |
| Articulation yaw/pitch/roll clearance | +/- 12 deg / +/- 6 deg / +/- 5 deg | detailed in [`articulation.md`](articulation.md) |
| Coupler face height (above ToR) | 720 mm | Scharfenberg Type 10 dim. |
| Headroom at doors | 2 000 mm | |
| Headroom at seats | 2 100 mm | |
| Passenger-compartment interior width | 2 700 mm | |

The 17 m car module is intentional rather than a placeholder. With
~3 m bogie zones at each end it leaves about 10 m of low-floor centre
span for two door pairs, wheelchair turning circles, and standing
space, while keeping the 3-car train to 51 m for the 67 m OSR standard
platform. Longer 19-20 m cars remain possible as a later capacity
variant, but the v1 base favours workshop-friendly modules and curve
overhang margin.

## Door positions

Two large 1 400 mm-wide double-leaf plug doors per car side in the
10 m low-floor centre zone (6 door pairs per side for the consist).
The two openings fit between the ~3 m high-floor bogie decks at each
end, leaving the middle span for PRM circulation and standing room.
Positioned:

- Each car: door centres at 5.67 m and 11.33 m from the car end.

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
  Each car has about 10 m of low-floor length between the standard
  bogie zones. The ~3 m raised end decks sit directly over the bogies;
  those raised zones are inside the saloon, away from the boarding
  thresholds.
- Horizontal gap at door sill: ≤ 75 mm per UIC 741. Achieved by
  a 40 mm sliding skirt at each door that extends on dwell
  (retracted in motion).
- On curved platforms at RFC 0009 `standard-urban` minimum
  radius (90 m): the door-to-platform horizontal gap grows to
  ~110 mm — requires an 80 mm gap-filler flap at the door sill.

## Mass distribution (AW2, nominal loaded)

| Location | Mass (t) |
|---|---|
| Car A incl. powered + trailer bogie | 41 |
| Car B incl. two trailer bogies | 38 |
| Car C incl. trailer + powered bogie | 41 |
| **Total consist (tare + AW2 passengers)** | **120** |

Tare target = 98 t for the concept-aligned BOM; AW2 load = 21.6 t
(360 passengers × 60 kg average).

Distribution per axle under AW3 (crush load, 480 passengers ×
60 kg = 28.8 t):
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
- Identical fiberglass end cowl → [`end-cowl.md`](end-cowl.md)
- Traction → [`traction.md`](traction.md)
- Interfaces → [`interfaces.md`](interfaces.md)
