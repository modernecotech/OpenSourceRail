# OpenSourceRail architecture

OpenSourceRail v0.5.2 development uses **station-powered ferrite maglev**. Fixed
station linear synchronous motors launch and receive each train. Interstation
spans have passive magnetic reaction iron and no propulsion supply. Onboard
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

The ordinary civil candidate is a 25 m, 0.80 × 1.80 m box with 100 mm webs,
150 mm flanges and end infills. Hollow columns and caps are explicit quantity
studies. Shallow, single-shaft and pile-group foundations remain alternative
families, selected only with ground and structural evidence. Reaction iron,
anchors, bearings, joints, rail survey and all construction stages remain in scope.

| Layer | Controlled definition | Implemented evidence and boundary |
|---|---|---|
| Service and city | Geography, demand, formation, runtime, headway and station spacing | Planning packages; flat reference is 90 s/km and 190 s headway, with grade/coasting and arrival gates |
| Mechanical | Structural sandwich panels, four doors, ferrite cartridges, support/guidance and services | Quantity takeoffs and partial solids; complete hardpoints, joints, mass/CG/inertia and qualification open |
| Station propulsion | LSM cassettes/groups, phase sensing, bridges, DC supply, receiving braking and charging | Jerk-limited demand, actual assumed magnetic-band overlap and target cost cases; force/current/voltage maps unqualified |
| Civil | Guidebeams, supports, foundations, stations and interfaces | Exact section/end-infill quantities, gross elastic screens and foundation sensitivities; no accepted strength or soil capacity |
| Software | Independent support control and persistent launch/corridor/berth ownership | Offline Rust tests/replays; no qualified sensing, physical actuator adapter or measured hardware timing |
| Industrialisation | Moulds, cure/release, crews, transport, cranes, joints and survey | Conditional bottleneck capacity; no measured production or supplier-price evidence |
| Acceptance | Exact configuration, source, unit/serial identity, tests and reviewers | Source-bound receipts; engineering/manufacturing/physical acceptance remains open |

[Infrastructure policy](../lib/templates/infrastructure.toml),
[configuration](../engineering/ferrite_maglev/reference-configuration.toml),
[operating study](../engineering/ferrite_maglev/station.py) and
[structure study](../engineering/ferrite_maglev/station_structure.py) control the
interfaces. City `city.json` inputs feed the same current compiler.

## Launch, receiving and recovery

A launch reserves the interstation corridor, receiving berth and protective
boundary for one train. Permission expiry does not release committed occupancy.
Release requires complete-consist clearance evidence; lost communications or a
timer cannot establish that clearance. The receiver must remain able to stop a
train after departure. Independent stopping/holding, receiver faults, low-service
energy and stranded-train recovery require their own engineered designs.

Coasting feasibility depends on grade, drag, wind, launch speed and arrival
margin. An unpowered span cannot restart a stationary train from a distant
station. Terminal return geometry, depot movement and rescue equipment remain
explicit requirements. The nominal trajectory does not close these obligations.

At the hot-services assumption, 45 s charging within a 60 s dwell requires
1.20 MW/train before charger losses when the battery serves the remaining dwell.
Station power/charging is a separate priced target from the incomplete civil
subtotal. Complete network economics must include both, plus stations, fleet,
recovery, land, qualification, factory capital and financing.

## Evidence boundary

Ring-field controls and block orientation seeds do not demonstrate railway lift,
thrust or magnet-mass gains. Gross beam sag is distinct from relative magnetic-gap
error. The coupled demonstrator remains one stationary rigid car with ideal
forces and a flexible vertical beam; moving six-car dynamics, flexible bodies,
torsion, joints, soil and calibrated electromagnetic/thermal response remain open.

Native CAD covers partial assemblies. Visibility videos show final-position
parts and an illustrative sequence; they do not establish collision-free motion,
erection or chute deployment. Continuous-walkway removal remains conditional on
accepted onboard and route evacuation, including assisted access and safe landings
at every permitted stop. All release flags remain false. Accepted engineering
and physical releases remain zero.
