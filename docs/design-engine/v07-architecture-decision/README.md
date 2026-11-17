# v0.7 equal-service architecture decision screen

**Decision:** advance a sustained powered-wheel **research child** for the first
demonstrator, with continuous grid supply as the initial equipment quotation
path. Keep station launch and a short booster as comparisons. No installed
propulsion, power collection, braking or civil structure is selected for
manufacture. The [input](input.json) and [calculated result](result.json) bind
the selected passive vehicle, source evaluations and all source bytes. The
research configurations do not change that selected physical candidate.

The common service is a **synthetic** 30 km, two-track, 12-station line with
2.727 km equal station spacing, six 17 m cars, 276 normal places/train, 72 km/h,
0.4 m/s² demanded acceleration, 0.6 m/s² stopping target, 35 s dwell and 120 s
headway. A 5% moving-time allowance, 180 s terminal turnback and 15% spare
fleet are applied to every reached case. Mass is the same **incomplete**
22,672 kg/car parent normal account plus rotating equivalent. For powered
children this is an optimistic comparison floor with omitted motor, supply and
storage mass, **not** an exact installed mass or certified structural lower
bound. Those items are not silently installed or priced. Grades are whole-route
constant sensitivities, not a surveyed Baghdad, Samawah or demonstrator profile.

| Supply/propulsion research configuration | Level reach and fleet | 1% climb reach and fleet | 2% climb reach and fleet |
|---|---:|---:|---:|
| 500 m station launch only | Yes; 47 active + 8 spare = **55** | **Stalls** | **Stalls** |
| 500 m launch + one 250 m booster | Yes; 45 + 7 = **52** | Yes; 46 + 7 = **53** | **Stalls** |
| 24 driven axles, continuous supply hypothesis | Demand reaches; 44 + 7 = **51** | Demand reaches; **51** | Demand reaches; **51** |
| 24 driven axles, battery + supercapacitor hypothesis | Same motion demand; **51** | Same motion demand; **51** | Same motion demand; **51** |

A separate **+2,400 kg/car preliminary powered-equipment sensitivity** raises
the comparison normal account to 25,072 kg/car. On the 2.727 km, +2% uphill
leg it raises demand from 93.3 to **102.2 kN**, 1.866 to **2.045 MW mechanical**
and 30.88 to **33.79 kWh mechanical** per train. The predicted 178 s motion
time does not change because the model commands acceleration with unlimited
available force. Added rotating inertia, complete installed mass, actual
adhesion and electrical supply remain unknown. The 51-set fleet is therefore
conditional, not an installed-vehicle timetable.

The separate [electrical supply/drive research](../v07-powered-bogie/README.md)
and [powered-vehicle layout](../v07-powered-vehicle/README.md) must be joined
by a **new physical candidate bundle** before a prototype architecture is
selected. The join must match motor count and rating, vehicle mass and CG,
axle reactions, collector/rail and station datums, protective devices, thermal
duty, independent brake, emergency recovery and all installed cost/renewal
lines. Their current research IDs are recorded in their machine receipts; this
service screen has not inherited their cost, capacity or physical acceptance.

The two powered-wheel rows share one motion calculation but have different
physical supply, charging, protection, mass and renewal obligations. A reached
calculation asserts **required** force and energy, not available adhesion,
drive output, 120 s thermal duty or a safe timetable. The inherited 0.05 brake
adhesion is below the optimistic 0.0832 needed for the independent 0.6 m/s²
stop on a 2% downgrade. Powered-wheel traction on the 2% climb also needs a
measured adhesion and axle-load case. At 20 m/s, 0.6 m/s² and an illustrative
1 s reaction, the optimistic receiving distance after accounting for the full
104.5 m train is **457.8 m**, before brake build-up, position uncertainty and
berth clearance. These are physical selection holds.

## One base cost and the changed-architecture cost gap

The existing [30 km line estimate](../line30-current-20261117/README.md)
prices **US$737.991m installed capital** and **US$1.568bn 30-year NPV** for a
different, level, 1.0 m/s² cable-capstan analysis anchor with **52 trainsets**.
The [14-scope bridge](result.json) accounts for all 32 original capital lines
exactly once, at its single base estimate:

| Procurement scope | Base proxy, US$m |
|---|---:|
| Rolling stock and vehicle interfaces | 225.283 |
| Guideway beams, bearings and detail | 59.292 |
| Piers, foundations and groundworks | 19.659 |
| Span haul and erection | 13.905 |
| Rails, welding and protected access | 14.846 |
| Launch machinery and converters | 48.432 |
| Traction grid and protection | 23.506 |
| Stations, platforms and access | 40.212 |
| Turnbacks and line controls | 4.967 |
| Auxiliary charging and grid | 11.923 |
| Production, depot, land and utilities | 48.880 |
| Fleet spares and recovery | 21.994 |
| Prototypes, independent testing and tax | 57.493 |
| Project risk contingency | 147.598 |
| **Exact unrounded total** | **737.991** |

This is **one accounting proxy, not four alternative prices**. At the common
0.4 m/s² screen, station-only requires three more trainsets on level track.
Holding only the old delivered passive-train unit rate fixed makes that fleet
quantity an illustrative **US$12.949m addition**, excluding changed drive,
station, civil, energy, spares and contingency. The booster needs the same 52
sets on level and one more on 1% grade, but its installed booster, feeder,
cooling and civil interfaces remain unpriced. Powered-wheel demand needs one
fewer set on level; **no credit is taken**, because motor, bogie, drive, power
collection, storage, braking and maintenance mass/cost are unknown. All four
candidate installed and lifecycle totals remain **null**. Neither the old
US$737.991m nor a lower fleet count proves that powered bogies are cheaper.

Continuous supply requires an engineered conductor/collector or overhead,
substations, return, protection and evacuation-safe isolation. Station-charged
battery/supercapacitor operation requires high power during a short dwell,
storage mass, cooling, charging equipment and life-cycle replacements. The
electrical package must price those complete installed alternatives before a
whole-life cost winner is selected. Revenue and cost per actual passenger-km
remain unknown without occupancy and patronage.

## Simpler civil alternative to quote

For a straight two-track **2 km** prototype, the current two-piece 20 m span
plan counts 200 complete beams, 400 lifts, 202 independent supports, 800
bearings, 200 structural midspan joints and 200 temporary tower placements.
Two independent simply supported **10 m spans** per 20 m would instead require
400 newly designed beams/lifts, 402 independent supports and an illustrative
1,600 bearings if each 10 m beam uses four. It removes the 200 midspan
structural joints; temporary works still need design. The existing 10 m
*segment* stock is **not** a qualified simply supported beam and its mass,
reinforcement, bearing detail and price cannot be inherited. New foundations,
utility conflicts and construction disruption may outweigh simpler joints.
Both civil installed totals remain null pending matched contractor quotes and
ground investigation.

The 700-place metro formation is a **separate research vehicle**. At 120 s its
offered-capacity arithmetic is 21,000 places/hour/direction, but installed
mass, door count/dwell, platform length, axle loads, braking, fleet and price
are unknown. A theoretical ~304 s interval would offer 8,280 places/hour,
but breaches the retained 120 s headway control. No 276-place vehicle result is
transferred to the 700-place formation.

Next physical and supplier gates: survey both directions and station/soil
conditions; obtain powered-bogie force/current/thermal maps and measured wet
adhesion; prove independent hot/faulted stop, parking, tow and accessible
evacuation; quote one complete vehicle, electrification or charging system,
station modules, each civil option, installation and 30-year replacements.
The controlled [release gate](../../RELEASE-v0.7.md) remains open.

Reproduce the bounded screen (under one second on the reviewed host):

```bash
python3 -m engineering.design_search.equal_service_handoff \
  --input docs/design-engine/v07-architecture-decision/input.json \
  --output docs/design-engine/v07-architecture-decision/result.json --check
python3 -m pytest -q engineering/design_search/tests/test_equal_service_handoff.py
```
