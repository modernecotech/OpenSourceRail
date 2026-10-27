# Practical launch alternatives for v0.6 research

The next experiment should compare **station-charged wheel traction** with a
**conductor-fed wheel-traction benchmark**, retaining longer-zone rollers and
cable haulage as separate alternatives. This is an experiment priority, not an
accepted or lowest-cost design. The selected six-car, station-LIM reference and
its illustrations remain unchanged.

This review uses the [selected reference](../../../engineering/development-baseline.toml)
and [current engineering](../current/README.md): six 17 m cars, 276 normal
passengers, 72 km/h, 0.4 m/s² and a 120 s departure target. Replacement hardware
is unweighed. The inherited normal account is 136.032 t/train, plus 10.622 t of
equivalent inertia from counted wheel, axle and brake rotation. These are
comparison inputs, not a completed vehicle mass.

## Acceleration distance comes first

At constant net acceleration, `s = v²/(2a)`. At 0.4 m/s²:

| Speed | Powered acceleration distance | Time |
|---|---:|---:|
| 43.2 km/h | 180 m | 30 s |
| 57.6 km/h | 320 m | 40 s |
| 72 km/h | 500 m | 50 s |

Finite jerk, engagement and release margins can increase these distances.
Higher acceleration is a research hypothesis: ride, seated-passenger restraint,
wheelchair securement, jerk and adhesion limits require evidence. The 0.8 m/s²
samples below do not approve a new passenger limit.

The existing **900 m station winding allowance is shared by launch and receiving
per station and direction**. Calculated full-train engagement zones are about
496 m and 329 m. A compact passenger platform can accompany a longer powered
approach; it does not establish a compact propulsion installation.

## Practical comparisons

| Architecture | What it could simplify | Consequences that must be counted |
|---|---|---|
| Station-charged wheel motors with battery, supercapacitor or hybrid store | Concentrates charging at stops and removes the long LIM primary and moving-fin commutation | Powered bogies, motors/drives/gears, store, collectors, DC/DC, cooling, protection, mounting, mass, axle loads and repeated duty |
| Conductor-fed wheel motors | Conventional comparison without a large traction store | Conductor length, substations, collectors, sectioning, public/maintenance protection and recovery after supply failure |
| Fixed wayside friction rollers on a passive train strip | Familiar stationary motors, tyres and bearings; passive train interface | Long enough contact zone, clamping reactions, wear, contamination, guards, strip joints, coupling loads and failed release |
| Launch-only cable/winch and catch-car | Central motor and mechanical force transfer | Powered stroke, grip, trolley braking, rope return/reset, sheaves, containment, fatigue, rescue and headway |
| Fixed-grip or detachable cable along the corridor | Central drives and lightweight vehicles | Different station/service architecture, full rope path, grips, tensioning, synchronisation, maintenance and shared-drive failure |
| Gravity launch | Uses train potential energy | Large mean-CG height change, ramps, vertical curves, accessibility, equal-height return energy and protected downhill stopping |
| LSM or switched-reluctance linear drive | Alternative electromagnetic interface | New primary/secondary geometry, material, force/current/thermal evidence and the required powered travel |
| Wayside flywheel, spring, battery or hydraulic accumulator | Buffers the station electrical/shaft power pulse | Storage, containment, conversion, controls and losses; a separate force-transfer system still acts over the launch distance |

Commercial station charging is an established architecture class: CAF describes
battery/supercapacitor stores and charging at stops; Alstom documents static
charging during passenger exchange in Nice. These precedents do not establish
OpenSourceRail component sizes, mass, prices or safety.
[CAF Urbos brochure](https://admin.cafmobility.com/uploads/caf_urbos_tram_light_rail_9e5621d648.pdf),
[Alstom Nice commissioning report](https://www.alstom.com/press-releases-news/2018/7/alstom-inaugurates-first-new-generation-citadis-with-innovative-charging-technology-in-nice).

## Wheel traction: power matters more than a small energy number

At the inherited normal mass and level-track drag hypotheses, the target launch
requires **66.617 kN peak shaft/body-drive effort**, **1.332 MW mechanical
power**, and **8.952 kWh mechanical launch work**. The kinetic-energy subtotal
alone is 8.147 kWh. Actual replacement motor and gearbox inertia are unknown.

At hypothetical 85–90% drive efficiency, launch demand is about 1.48–1.57 MW DC
and 9.95–10.53 kWh. With 70% usable store fraction and 80% end-of-life capacity,
the **energy-only** gross-store bound is 17.8–18.8 kWh. Peak power divided by
that capacity is about **83 per hour**, equivalent to roughly 83 C for a battery.
That is a sizing warning, not a suggested battery. Power, voltage/current,
temperature, repeated duty, reserve and life must size the store together.
Supercapacitors also need voltage-swing, high-current converter, balancing,
enclosure and reserve accounts.

The comparison separately reports launch-only recharge and total recharge plus
hotel power over the 35 s dwell. It credits no regenerative energy and keeps the
existing auxiliary store isolated from traction. A 3, 6 or 12 t hypothetical
train-level added-mass sensitivity is not a weighed assembly; the inherited
passive-secondary account is not silently subtracted.

Wheel adhesion uses a distinct force boundary. The optimistic contact lower
bound is `m*a + resistance`; unknown unpowered-wheel rotation can add to it.
Full retained rotor-inclusive shaft effort is reported separately. With equal
axle loads and hypothetical adhesion 0.10, at least 12 of 24 driven axles are
needed for the level-track target and 17 for the 2% uphill sample under this
optimistic lower bound. Actual load transfer, wheel slip control and adhesion
remain unknown. A small creeping recovery drive does not automatically become
a full-speed propulsion system.

## Mechanical launch: useful, with explicit contact and service limits

For a fixed roller bank of length `Z`, an extremely optimistic continuous strip
across the whole 104.5 m train permits at most `Z + 104.5 m` of powered travel
with any remaining contact. A **100 m bank reaches at most 46.05 km/h** at
0.4 m/s². Reaching 72 km/h needs **at least 395.5 m of bank**; keeping the whole
train inside a distributed bank throughout the launch would need at least
604.5 m. Real coupling gaps and contact/force margins worsen these bounds.
At a hypothetical tyre/strip friction coefficient of 0.2, the nominal peak
effort needs at least 333 kN total clamping normal load. Opposed rollers can
balance net lateral force while both local structural reactions remain.

Intamin documents a 72 km/h friction-wheel coaster launch. That demonstrates a
mechanism application, without establishing performance for this train mass,
comfort, contamination or repeated transit duty.
[Manufacturer project](https://www.intamin.com/project/quantum-accelerator/).

Cable passenger transport has real precedents, but its station and service
configurations differ. For this 2 km case, even ideal powered cruise with
instantaneous acceleration changes gives a minimum trip time of 141.667 s.
A synchronous fixed-grip loop with one train per station pitch therefore needs
at least **176.667 s** between departures including dwell: about 5,624 pphpd.
A single reversible shuttle needs at least **353.333 s** in the same direction.
Both miss 8,280 pphpd in those arrangements. Detachable grips, additional
berths or independently driven sections require different vehicle, platform,
fleet and protection definitions. A launch-only cable still needs the powered
stroke and a complete trolley return/rearming calculation.
[Doppelmayr system variants](https://www.doppelmayr.com/en/systems/automated-people-mover/),
[LEITNER MiniMetro brochure](https://www.leitner.com/fileadmin//user_upload/MiniMetro-we_move_people_en.pdf).

Gravity needs at least **21.99 m of mean train-CG drop** for kinetic energy alone;
the retained launch work corresponds to about 24.16 m. That is not a designed
ramp. Equal-height consecutive stations still need external energy to replace
losses. An accumulator or flywheel can reduce grid peaks but does not shorten
the 500 m output travel at the reference acceleration.

## Reproduce and retain the boundaries

```bash
./osr design railway plan
.venv/bin/python -m engineering.design_search.launch_options plan
.venv/bin/python -m engineering.design_search.launch_options compare
.venv/bin/python -m engineering.design_search.launch_options publish
.venv/bin/python -m engineering.design_search.launch_options verify
```

The separate [campaign](../../../campaigns/practical-launch-comparison.toml)
compares **12 concept hardware options and 144 cheap bound scenarios**. They are
not additional engineered railway bundles. Samples cover three speeds, two
acceleration hypotheses and level/2% uphill conditions. Battery, supercapacitor
and hybrid storage have distinct physical option identities. Friction,
efficiency and operating targets belong to evaluation contexts, not new
hardware. Complete materialized candidate, installed mass, price, selection,
usable force map and physical acceptance remain absent.

[Comparison packet](comparison.json) and [source/payload manifest](manifest.json)
are reproducible from [the evaluator](../../../engineering/design_search/launch_options.py).
The existing [requirement policy](../../../engineering/design_search/requirement_policy.py)
keeps mandatory obligations unknown without evidence. This study neither
registers a native evaluator nor changes the retained P1–P7 contracts.

Next, obtain motor/store/collector drawings and hot/end-of-life power maps;
model changed mass, axle loads and driven/unpowered rotor split; define charge
faults and safe rescue; and test repeated launch, wet adhesion, braking and
loss of supply. Roller and cable alternatives need dedicated contact/grip,
failed release, fatigue, return and recovery tests. Then propagate one revised
canonical bundle through full journeys, body/bogie loads, independent braking,
rails/viaduct/foundations, EBOM/MBOM, assembly, maintenance and equal-service
whole-life cost. None of that qualification is supplied by this bound study.
