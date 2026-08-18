# General arrangement — `light-metro-3car`

## Consist diagram

```
   ←── 16.5 m ──→←── 16.5 m ──→←── 16.5 m ──→

      Car A             Car B             Car C
   ┌─ M bogie ─ 2 doors ─ t bogie ┐A1┌─ M bogie ─ 2 doors ─ t bogie ┐A2┌─ M bogie ─ 2 doors ─ t bogie ┐
   │ repeated self-contained car │  │ repeated self-contained car │  │ repeated self-contained car │
   │ low-floor centre + battery  │  │ low-floor centre + battery  │  │ low-floor centre + battery  │
   └───────────────────────────┘  └───────────────────────────┘  └───────────────────────────┘
     M = powered bogie, t = trailer bogie
     A1/A2 = semi-permanent articulated gangway modules
     Length over couplers = 49.5 m
```

- **Three self-contained cars**, joined by two semi-permanent
  articulated gangway modules.
- **No driving cabs** — GoA 4 identical A/B-end multi-part fiberglass
  sensor cowls at both ends per RFC 0015, with heated RF-transparent
  glass, T-OBS sensors, and LED headlamp / marker-light clusters.
- **No cab bulkhead** — the front and rear passenger ends are not
  walled off; the saloon remains open to the single panoramic glass
  end pane so passengers see through both driverless ends.
- **Six bogies total** — two standard 2-axle bogies per car.
- **Two articulations total** — lower spherical pivot/drawbar, upper
  roll-yaw-pitch links, double-wall bellows, segmented turntable floor,
  and separated trainline routing at each carbody interface.
- **Powered wheelsets:** one powered bogie per car, giving three
  powered bogies and six powered axles across the consist.
- **Battery:** 180 kWh usable / 225 kWh gross LFP per car under the
  longitudinal seats.
  The 10 m centre door zone stays low-floor and clear.
- **Roof:** PV strip per car, split around compact end HVAC modules.

## Key dimensions

| Parameter | Value | Source |
|---|---|---|
| Length over couplers | 49 500 mm | promoted v2A envelope: 3 × 16.5 m car modules |
| Car A length | 16 500 mm | modular car envelope |
| Car B length | 16 500 mm | modular car envelope |
| Car C length | 16 500 mm | modular car envelope |
| Body width (outer) | 2 850 mm | concept envelope, fits UIC 505-1 gauge |
| Height over rail (roof) | 3 450 mm | concept envelope, before roof equipment |
| Overall running height | 3 900 mm controlled envelope; current CAD reaches 3 868 mm | includes PV, HVAC, mounts, and production tolerance |
| Floor height (above top-of-rail) | 350 mm, 10 m low-floor centre door/PRM zone; 760 mm, ~3 m high-floor end decks over bogies | low-floor access with standard bogies |
| Bogie wheelbase | 2 100 mm | RFC 0022 single-SKU bogie |
| Wheel diameter (new / worn) | 760 / 680 mm | RFC 0022 |
| Inter-bogie distance (within a car) | 12 300 mm | 16.5 m module with 2.1 m bogie inset from each end |
| Articulation module length envelope | 1 120 mm | straddles each carbody interface; does not add to consist length |
| Articulation passage width | 1 650 mm | walk-through gangway target before trim tolerances |
| Articulation yaw/pitch/roll clearance | +/- 12 deg / +/- 6 deg / +/- 5 deg | detailed in [`articulation.md`](articulation.md) |
| Coupler face height (above ToR) | 720 mm | Scharfenberg Type 10 dim. |
| Headroom at doors | 2 000 mm | |
| Headroom at seats | 2 100 mm | |
| Passenger-compartment interior width | 2 700 mm | |

The 16.5 m promoted car module is intentional rather than a placeholder. With
~3 m bogie zones at each end it leaves about 10 m of low-floor centre
span for two door pairs, wheelchair turning circles, and standing
space, while keeping the 3-car train to 49.5 m for the derived 59.5 m OSR
standard platform. Longer 19-20 m cars remain possible as a later
capacity variant, but the v1 base favours workshop-friendly modules
and curve overhang margin.

## Door positions

Two large 1 400 mm-wide double-leaf plug doors per car side in the
10 m low-floor centre zone (6 door pairs per side for the consist).
The two openings fit between the ~3 m high-floor bogie decks at each
end, leaving the middle span for PRM circulation and standing room.
Positioned:

- Each car: door centres at 5.50 m and 11.00 m from the car end.

All doors are plug-outward doors per RFC 0008 §3.3 with a 1 400 mm
nominal structural opening and at least 1 250 mm clear passage after
seals/thresholds at 2 000 mm height.

## Gauge compliance

UIC 505-1 static envelope:
- Width at floor level: 2 850 mm ≤ 3 150 mm limit ✓
- Overall height over ToR: 3 900 mm ≤ 4 320 mm limit ✓
- Dynamic outline (controlled lateral sway and +30 mm vertical excursion):
  2 970 × 3 930 mm — still inside the 3 150 ×
  4 320 mm boundary ✓

No interference with UIC 505-1 at any of the RFC 0009 track
presets (`standard-urban` / `standard-metro`
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
| Car A incl. powered + trailer bogie | 33.45 |
| Car B incl. powered + trailer bogie | 33.45 |
| Car C incl. powered + trailer bogie | 33.45 |
| **Total consist (tare + AW2 passengers)** | **100.35** |

Controlled planning tare = 78.75 t: 75.308 t optimizer subtotal plus a
3.442 t engineering reserve pending drawing-package mass closure. AW2 load = 21.6 t
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

The current screening FEA is linked from the package README. The
full-body lateral-sway screen is still a v2 closure item: the next
body release must add diaphragm/knee-brace detail at the side-frame
and waist-rail load path, then rerun the shell/beam model before
first steel cut.

## Cross-refs
- Bogie detail → [`bogie.md`](bogie.md)
- Body structure → [`body.md`](body.md)
- Identical fiberglass end cowl → [`end-cowl.md`](end-cowl.md)
- Traction → [`traction.md`](traction.md)
- Interfaces → [`interfaces.md`](interfaces.md)
