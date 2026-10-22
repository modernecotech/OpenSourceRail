# OpenSourceRail architecture

OpenSourceRail v0.5.2 development uses **fixed-zone ferrite maglev**. Fixed
station linear synchronous motors launch and receive each train; located midpoint
accelerators are alternatives for longer suburban legs. Coasting sections outside
these finite powered zones have passive magnetic reaction iron. Onboard
ferrite PM-biased active support and guidance remain powered independently,
alongside passenger services, protection and emergency equipment.

The objective is broad city access with compact elevated guidebeams, fewer
moving running-gear parts and practical local manufacture. A 99% elevated-mainline
planning target still depends on route rights, utilities, ground, curvature,
station access, evacuation and recovery.

## Configuration and interfaces

Baghdad uses six 17 m bodies. The 104.5 m coupled footprint is an assumption until
couplers and gangways are resolved. The central study targets 14.2 t tare/car,
including a 5.2 t equipped GFRP sandwich body, 3 t ferrite, 30 kWh services storage
and 1.8 t growth reserve. Four doors per car are the body-study basis. No complete
weighed body, load-bearing joint set or qualified magnetic circuit establishes
these mass targets.

The ordinary civil candidate is a 25 m, 0.80 × 2.50 m box with 100 mm webs,
150 mm flanges and end infills. Hollow columns and caps are explicit quantity
studies. Shallow, single-shaft and pile-group foundations remain alternative
families, selected only with ground and structural evidence. Reaction iron,
anchors, bearings, joints, rail survey and all construction stages remain in scope.

| Layer | Controlled definition | Implemented evidence and boundary |
|---|---|---|
| Service and city | Geography, demand, formation, runtime, headway and station spacing | Urban minimum target 1.5 km and mean target 2 km; explicitly classified suburban legs 4–5 km with booster alternatives; short interchange conflicts remain visible |
| Mechanical | Structural sandwich panels, four doors, ferrite cartridges, support/guidance and services | Fitted structural/material regions with native interference, drilled hardpoints and partial mass/CG/inertia; complete equipment, joined behavior and qualification open |
| Fixed-zone propulsion | Station/booster LSM cassettes/groups, phase sensing, bridges, DC supply, receiving braking and charging | Separate longer-leg jerk/overlap/rating/service/protection comparisons; measured force/current/voltage/thermal maps unqualified |
| Civil | Guidebeams, supports, foundations, stations and interfaces | Exact section/end-infill quantities, gross elastic screens and foundation sensitivities; no accepted strength or soil capacity |
| Software | Independent support control and persistent launch/corridor/berth ownership | Offline Rust tests/replays; no qualified sensing, physical actuator adapter or measured hardware timing |
| Industrialisation | Moulds, cure/release, crews, transport, cranes, joints and survey | Conditional bottleneck capacity; no measured production or supplier-price evidence |
| Acceptance | Exact configuration, source, unit/serial identity, tests and reviewers | Requirement task chains, typed physical test protocols and source-bound receipts; engineering/manufacturing/physical acceptance remains open |

[Infrastructure policy](../lib/templates/infrastructure.toml),
[configuration](../engineering/ferrite_maglev/reference-configuration.toml),
[operating study](../engineering/ferrite_maglev/station.py) and
[structure study](../engineering/ferrite_maglev/station_structure.py) control the
interfaces. City `city.json` inputs feed the same current compiler. Junctions are
passenger transfers between independent fixed lines, with no mainline train-routing
switch. Straight alignments are the design objective; retained mapped routes and
unselected straight-chord alternatives must keep their site and cost evidence separate.

## Launch, receiving and recovery

The [electrical construction package](design-engine/ferrite-maglev/drive-construction/README.md)
separates three control responsibilities. The car SBC runs supervision and force
allocation; proposed local MCU boards acquire gap/current signals and run fast
loops; independent protection, essential support power and capture handle faults.
Permanent magnets provide bias flux, while active windings correct unstable
attractive suspension and guidance. An ordinary SBC process is not a qualified
20 kHz power-stage controller. The new Rust `drives` layer executes bipolar
current PI and sensored three-phase dq commutation in offline coupon plants.
It has no ADC/PWM adapter or physical-output authority.

The counted construction candidate has one lift coil and two series-opposed
guidance coils per cartridge: 432 coils and 288 bipolar circuits per six-car train.
Its 50-turn compact coil passes declared depth/packing and current screens,
while retaining rejected larger-pack and lower-turn alternatives. Separate
wayside LSM bridges use indexed three-phase winding groups. Their
[BOM](design-engine/ferrite-maglev/drive-construction/bom.csv),
[winding schedule](design-engine/ferrite-maglev/drive-construction/winding-schedule.csv)
and [connections](design-engine/ferrite-maglev/drive-construction/connections.csv)
retain material, converter, sensing, DC and braking quantities. Measured magnetic
maps, complete wiring/PCB drawings, thermal design, installed timing and actuator
dynamics in the moving train remain open. A station propulsion fault must not
remove onboard support.

The [UK procurement supplement](../engineering/ferrite_maglev/README.md#uk-power-module-procurement)
adds Dynex's British manufacturing capability as a first candidate for launch
semiconductors and custom assemblies, retaining an imported comparator and
requiring exact order-origin confirmation. It does not select or qualify a part.

A launch reserves the interstation corridor, receiving berth and protective
boundary for one train. Permission expiry does not release committed occupancy.
Release requires complete-consist clearance evidence; lost communications or a
timer cannot establish that clearance. The receiver must remain able to stop a
train after departure. Independent stopping/holding, receiver faults, low-service
energy and stranded-train recovery require their own engineered designs.

The separate `osr-progressive-departure/1` candidate instead protects a finite
stopping envelope before a stopped departure and renews it from fresh evidence.
Its local multi-train replay includes withheld arrival permission and explicit
reaction/braking transients. It does not replace `StationLaunch` or the city
capacity basis. Restored candidate snapshots remain fenced; operational restart,
distributed handover and physical brake/detector qualification remain open.

Coasting feasibility depends on grade, drag, wind, launch speed and arrival
margin. An unpowered span cannot restart a stationary train from a distant
station. Terminal return geometry, depot movement and rescue equipment remain
explicit requirements. The nominal trajectory does not close these obligations.

The 1 km/90 s authored and 1 km/88 s developed runs remain explicit benchmarks.
They do not verify the new 2 km/5 km operating design. Longer profiles compare
converter ratings, charger power, dwell and larger services packs with their mass
and cost changes. Whole-leg exclusive reservations impose a capacity constraint;
a passing motion calculation cannot clear it. Station and booster power/charging
are separately priced targets from the incomplete civil
subtotal. Complete network economics must include both, plus stations, fleet,
recovery, land, qualification, factory capital and financing.

## Evidence boundary

Ring-field controls and block orientation seeds do not demonstrate railway lift,
thrust or magnet-mass gains. Gross beam sag is distinct from relative magnetic-gap
error. The stationary single-car demonstrator is retained separately from the
moving six-car Rust/beam/coupler model. Both use ideal force channels. Longer
operational profiles need their own moving confirmation; flexible bodies,
torsion, joints, soil and calibrated electromagnetic/thermal response remain open.

Native CAD covers partial assemblies. Visibility videos show final-position
parts and an illustrative sequence; they do not establish collision-free motion,
erection or chute deployment. Continuous-walkway removal remains conditional on
accepted onboard and route evacuation, including assisted access and safe landings
at every permitted stop. All release flags remain false. Accepted engineering
and physical releases remain zero.
