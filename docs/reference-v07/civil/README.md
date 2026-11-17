# Civil and station concept: 10 m joint-free beam

**Digital design and cost reference, 17 November 2026.** The [selected
candidate](../digital/selected.toml) uses a one-piece, thirteen-strand 10 m
precast box beam for each track. The [native civil comparison](../digital/civil/README.md)
carries the joined car's bounded axle loading into this beam and records the
original nine-strand study as ancestry. This page gives quantities, a station
interface and a construction method for the synthetic 30 km corridor and a
straight 2 km construction module.

## Selected arrangement

| Item | Reference definition |
|---|---|
| Track | Two separate 1,435 mm conventional rail tracks with direct fastening, one beam per track per 10 m bay |
| Beam | One-piece, simply supported closed concrete box, 10.0 m long, 2.0 m wide, 1.4 m deep, with no field midspan joint |
| Beam stock | 11.3376 m³ concrete and 3.1126 t counted steel per beam; 29.964382 t bare handling mass; at least 37.456 t provisional hook load including 25% rigging allowance |
| Prestress | Thirteen-strand digital selection for the 160-person/car crowd load; tendon path, anchor zones, transfer and reinforcement details require a shop design |
| Supports | Independent bearing seat, pier and foundation for each track; four provisional bearing units per beam; no credit for an unanalysed shared crosshead |
| Foundation costing module | 2.5 m × 2.5 m × 1.0 m footing and 1.0 m × 1.0 m × 6.0 m pier per support, used only to calculate a reference quantity. Under the joined CG-bound gravity sensitivity, about 2.30 m square is required at an assumed 200 kPa bearing resistance; lateral and settlement design require site inputs. |
| Power and access | Allow a rail-side protected maintenance/evacuation path, drainage, return/earthing and overhead traction-power mounts as separately counted assemblies. Do not attach equipment until fixing loads and electrical clearances are designed. |

[Reference elevation and station interface](span-and-station.svg) gives the controlling dimensions. It is a schematic interface drawing, not a shop or structural approval drawing. Track-to-track spacing, walkway envelope, pier height, foundation dimensions, drainage and overhead mounts remain adjustable against the site survey; the 10 m beam length, section and two-track independent support logic are fixed for this costing candidate.

## Counted quantities

Straight, elevated route only; excludes stations, curves, switches, ramps, depots and river crossings. The final bay uses two end supports per track, so a 2 km module has 201 support positions on each track.

| Item | Per route-km | 2 km demonstrator | Calculation |
|---|---:|---:|---|
| One-piece beams and single-piece lifts | 200 | 400 | 2 tracks × 1,000 m ÷ 10 m |
| Independent support/foundation positions | 202 for an isolated 1 km module | 402 | 2 tracks × (bay count + 1); continuous longer runs share boundary supports |
| Bearing units, provisional | 800 | 1,600 | 4 per beam; final bearing schedule may differ |
| Beam concrete | 2,267.52 m³ | 4,535.04 m³ | 11.3376 m³ per beam |
| Counted beam steel | 622.52 t | 1,245.04 t | 3.1126 t per beam |
| Footing concrete, costing module | 1,262.5 m³ for isolated 1 km | 2,512.5 m³ | 6.25 m³ per support |
| Pier concrete, costing module | 1,212 m³ for isolated 1 km | 2,412 m³ | 6.0 m³ per support |
| Rail stock | 4,000 m | 8,000 m | 2 rails × 2 tracks × route length |
| Direct fastener sets | 7,200 | 14,400 | From the source packet's 2 km account |
| Midspan joints and temporary joint towers | 0 | 0 | Joint-free beam selection |

For a continuous 30 km double-track line the preliminary counts are **6,000 beams/lifts and 6,002 independent supports**, before stations and special structures. Do not multiply the isolated 1 km support count by route length: that would double-count module boundary supports. Footing and pier modules are quantity allowances, not a foundation design or a second physical candidate. Reinforcement, bearing plates, anchors, drainage, access, OLE and temporary works are additional installed material and labour; the beam-stock subtotal is not an installed civil mass.

## Representative elevated station

Use a **125 m long × 8 m wide central platform** for the existing 104.5 m six-car research formation. The platform length allocates 20.5 m total stopping/edge margin; the final stopping tolerance, accessible boarding gap and door positions are controlled by vehicle/station interface drawings. Both tracks flank the platform, with each train's one-sided doors facing the island. A station has its own supporting frame and foundations; the standard running beam is not assumed to carry the platform or concourse. Provide two independent egress paths, accessible lift access plus protected stairs, lighting, drainage, fire provisions, communications, passenger protection and safe maintenance isolation. Allow overhead-line continuity and sectionalisation through the station. Station foundations, concourse, vertical circulation and equipment are separate cost items.

The station is an interface template, not a universal Baghdad site design. Platforms must be straight and approximately level in this concept; site-specific geometry, passenger demand, crowd egress, flood level, security, utility diversions and land determine the actual footprint and price. A higher-capacity formation changes the platform and civil candidate and requires a new quantity take-off.

## Fabrication and erection sequence

1. Survey utilities, soil, levels, drainage, crane standing areas, road haul route, track centres and station transitions. Establish rail, bearing and overhead datums.
2. Approve site-specific support, foundation, temporary works, lift insert, bearing and rail-fixing drawings. Cast foundations and piers; test concrete strength and survey seats.
3. Match fixed beam moulds to the controlled section. Cast, cure and inspect 10 m units; record material lots, strand force, transfer, cracks, dimensional checks and lift insert proof.
4. Haul one beam per provisional 35 t-payload trip. Confirm carrier axle loads, route permits and turns. Confirm crane chart at actual radius, lift rigging, weather and ground-bearing pressure before each lift.
5. Land and brace each beam, install bearings and continuous rail, then survey line, level, twist, gauge and clearances. Fit walkway, drainage, earthing/return and overhead supports to approved inserts.
6. Build station frames and platform interfaces, connect access and power, then proof-load a representative span and measure deflection, twist, bearing movement and support settlement before prototype construction release.

**Planning production rate:** four beams per factory day across parallel moulds and eight beam lifts per site day across two erection fronts. For 2 km, 400 beams require 100 factory days and 50 lifting days. Four support completions/day across foundation crews require about 101 site days. These work packages overlap after the first cured units and supports. Allow a 12-month concept programme: months 1–2 survey/design/permits; 3–7 precast and foundations; 6–9 erection; 8–11 rail, power, access and station equipment; 12 controlled tests and handover. This is a resource-loaded planning target, not a contractor commitment. A 30 km line requires multiple production fronts, depots and station works, so its duration is not 15 times the 2 km module.

## Load envelope and engineering handoff

The car uses 25.072 t/car normal and 33.622 t/car crowd sizing loads. The
earlier equal-axle study gave 0.586 MNm live moment. The [joined digital car
placement bound](../digital/vehicle/README.md) permits a 155.77 kN static
crowd axle; a physically consistent high/low bogie pose raises the 10 m live
moment to **1.107 MNm**. The thirteen-strand candidate satisfies its declared
gross longitudinal service screen and has **1.576 mm** native gross-elastic
midspan deflection. The modelled two-span gravity support sensitivity is about
**928 kN** before pier and footing self-weight. Local seats, prestress transfer,
cracking, fatigue and lateral/braking load combinations remain outside this
global beam model.

Before issuing fabrication drawings, specify the actual wheel loads and dynamic/lateral/braking combinations; analyse local rail seat, shear, torsion, fatigue, cracking, prestress transfer and handling; design bearings, anchors and track/OLE fixings; check foundation bearing, settlement, flood/scour and seismic response; and close temporary stability, crane-at-radius and protected access. The selected wheel system has no magnetic-gap limit; rail twist and overhead contact geometry remain controlled interfaces. A representative prototype needs measured proof-load response and independent structural/construction review.

**Source identity.** The [selected digital record](../digital/selected.toml)
names revised beam component `34161ebcca2e35599cc5896a23b763cc35d3809107dd6b0c9f2ff98516a68160`
and its parent. The [native civil packet](../digital/civil/result.json) binds the
joined car, beam model and solver. The earlier [simple-span packet](../../design-engine/v07-simple-span/plan.json)
and [20 m segmented comparison](../../design-engine/v07-affordable-corridor/evidence/civil-20261117-box20-segmented-001/README.md)
remain separate alternatives.

Reproduce the selected digital beam with
`python3 -m engineering.design_search.v07_joined_civil_fem check --output docs/reference-v07/digital/civil`.
Its native model is a gross-elastic beam and its prestress screen is analytical;
the design awaits fabrication detail and physical qualification.
