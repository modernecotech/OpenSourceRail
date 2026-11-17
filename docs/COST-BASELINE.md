# v0.7 cost baseline

The single current **synthetic 30 km** planning estimate is **US$737.991 million
installed capital**, or **US$24.600 million per route-km**. It covers two
tracks, twelve stations, 52 six-car trainsets including seven reserve sets,
8,280 offered normal places/hour/direction at a conditional 120 s headway,
and a cable-capstan analysis anchor. Its 30-year whole-life NPV is **US$1.568
billion**. These are model outputs, not a bid or a physically accepted system.
The [source-bound result and quantities](design-engine/line30-current-20261117/README.md)
remain the calculation authority.

| Installed capital group | US$m |
|---|---:|
| Rolling stock and launch interfaces | 225.28 |
| Elevated guideway, foundations, erection and access | 107.70 |
| Launch machinery and traction power | 71.94 |
| Stations, accessibility, controls and turnbacks | 45.18 |
| Auxiliary charging and grid | 11.92 |
| Production buildings, yards and tooling | 10.07 |
| Depot, land and utility relocations | 38.81 |
| Fleet spares and commissioning | 18.68 |
| Recovery assets | 3.31 |
| Prototypes and independent testing | 42.63 |
| Tax and import duty | 14.86 |
| Project risk contingency | 147.60 |

The rounded groups reconcile to the unrounded US$737.991m result within
rounding. The contingency is about 20% of base capital; removing it would
understate risk while the propulsion, civil joint, ground and complete installed
vehicle are unresolved. The guideway group is **not** a price for the proposed
segmented beam: its joint, extra lifts, temporary support and site work are
unpriced. Actual passenger-km lifecycle cost is unknown until patronage and
occupancy are established.

The source calculation contains 32 capital lines in eight accounting scopes.
The [v0.7 architecture screen](design-engine/v07-architecture-decision/README.md)
maps each of those lines exactly once into fourteen procurement scopes that
reconcile to the **same US$737.991m base proxy**. This accounting bridge does
not price the changed architectures: powered bogies, overhead contact,
independent brakes, installed boosters, segmented joints, extra 10 m supports,
supplier inputs and site-specific works still lack matched quantities and
quotes. Every changed-candidate installed and lifecycle total remains null.
The base figure is therefore one planning estimate, not a price for the new
demonstrator packages or a complete candidate-specific bill of quantities.
The [segmented-span cost handoff](design-engine/v07-segmented-span/README.md)
provides counted quote quantities and replacement-versus-increment rules;
supplier unit prices, baseline credits and installed cost deltas remain open.

At the common 30 km/12-station demand screen, the level station-only case
requires 55 sets, the booster case 52 and the powered-wheel case 51, under a
5% moving-time allowance and 15% spare rule. Only the old passive-train unit
rate permits an illustrative **US$12.949m** increment for the three additional
station-only sets; it excludes changed hardware, energy, civil and risk. No
powered-wheel fleet credit or affordability claim is booked. The 700-place
formation is a separate vehicle whose installed mass, doors, dwell, platform,
braking, fleet and price are not yet defined.

The [Samawah planning case](design-engine/v07-affordable-corridor/README.md)
has a separate **US$1.141bn** base installed-capital model and **US$2.259bn**
30-year NPV for 57.873 km. Its long gap uses a powered-axle research fallback,
not an accepted installed architecture. Neither its cost nor its route is
transferred to the synthetic case.

The [Baghdad proposal](proposals/baghdad-v07/README.md) has **no established
OpenSourceRail capital requirement**. US$18.0bn for 148.2 km and US$69.6bn for
605.65 km are conventional-metro scope comparators. They must not be presented
to Amanat Baghdad or financiers as the cost of a locally buildable OpenSourceRail
system. Reprice a surveyed Baghdad alignment from its own civil mix, capacity,
fleet, propulsion, stations, land, grid, procurement and financing inputs.

Unknown installed quantities and unpriced work remain visible, never zero.
The working budget presents one estimate per stated candidate and scope; the
underlying sensitivities are retained for audit in the source packet.
