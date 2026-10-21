# OpenSourceRail v0.5.2 development — station-powered ferrite maglev

**Fewer moving parts, local manufacture and compact elevated urban routes.**

![OpenSourceRail maglev station concept](../OpenSourceRail%20maglev%20station%20concept.png)

*Illustrative development concept, without physical or manufacturing acceptance.*

Station-mounted linear synchronous motors launch and receive the train.
Interstation propulsion is unpowered; onboard ferrite PM-biased active support,
guidance and passenger services remain independently powered. Removing main
traction equipment from the train shifts electrical plant to stations. Support
coils/drives, cooling, sensing, protection, doors, HVAC and emergency equipment
remain necessary. Contactless running aims to reduce contact noise and wear;
actual losses, acoustic performance and maintenance require measurement.

## Body, civil works and local capability

Baghdad uses six 17 m bodies. The central tare target is 14.2 t/car,
including a 5.2 t equipped structural GFRP body, 3 t ferrite, 30 kWh services
storage and the full 1.8 t growth reserve. Four passenger doors per car are the
body takeoff. Calculated panel stock is distinct from sized members, joints,
complete equipment mass and structural qualification.

The ordinary civil candidate is a 25 m, 0.80 × 1.80 m closed concrete box with
100 mm webs, 150 mm flanges and end infills. Hollow columns/caps and alternative
foundation families are compared by quantity. Necessary passive iron, anchors,
bearings, connections and final survey remain in scope. Ground-specific selection,
prestress/rebar detailing, loads and construction stages remain unqualified.

The research target omits a continuous external walkway. Vertical spiral chutes
are the preferred alternative under investigation, without walkway-removal
approval. Safe landing, assisted evacuation, deployment, stopping/recovery and
fire response must work at every allowed stopping location.

![Vertical spiral escape chute concept](../Vertical%20spiral%20escape%20chute%20concept.png)

*Illustrative concept; no qualified railway device or all-stop evacuation claim.*

The 99% elevated-mainline objective and straight tangents aim to reach constrained
corridors with less surface occupation. Rights, buildings, utilities, access,
wildlife, water, curvature and foundation feasibility govern each route.

Local precast/GFRP production, steel fabrication, cartridge assembly, station
winding cassettes, interiors, wiring, Rust software and integration can build
domestic capability. Prioritise verified British manufacture when selecting UK
machinery. A UK distributor or integrator does not establish manufacturing origin.
Complete local content remains unknown until the bill and input origins exist.

## Operating and cost boundaries

The station operating reference is a jerk-limited 90 s flat 1 km run with
190 s headway. Grade, wind, drag, arrival speed and receiving-brake readiness
remain explicit route gates. A committed coasting train keeps its corridor and
receiving berth reserved until proved full-consist clearance. Receiver failure,
independent stopping/holding and stationary recovery remain design obligations;
a distant station motor cannot restart a train in an unpowered span.

A 45 s charge within a 60 s dwell needs 1.20 MW/train before charger losses under
the hot-services assumption, including the battery energy used during the
remaining dwell. Station electrical cost targets are additional to the incomplete
ordinary civil subtotal. Stations, external grid work, complete evacuation,
recovery, land, qualification, factory capital and financing need their own scope.
No quoted complete railway price or accepted production rate is established.

## Inspect and reproduce the current work

| Current digital capability | Scope |
|---|---|
| City planning | 266 primary packages using explicit geography/demand and recalculated formation, duty, fleet and costs |
| Operating study | Jerk-limited launch/coast/receive, assumed magnetic-band overlap, power, receiving heat and charging |
| Mechanical/civil quantities | Three GFRP cases, magnet-orientation inventories, five beam families, ground sensitivities and a conditional production bottleneck |
| Controls | Independent Rust support and station demand studies, persistent launch reservations and offline negative controls |
| Simulation and media | Partial native CAD/images, assembly visibility videos and source receipts; coupled replay remains a stationary single car with a vertical beam |
| Engineering acceptance | **0 accepted physical releases; design, manufacture and operational gates remain open** |

Ring benchmarks and block-orientation seeds receive no railway lift or mass-saving
credit. Moving six-car magnetic/structural dynamics, hardware timing, complete
manufacturing geometry and physical acceptance remain open. Visibility videos show
final-position parts, without motion, collision or erection-strength simulation.

Use `./osr build` to verify dependencies and rebuild stale implemented studies.
`./osr design station`, `./osr design structure` and `./osr design protocol`
reproduce their separate evidence. `./osr workbench` opens the review UI;
`./osr book` builds the current reader edition. The scheduled runner refreshes
implemented evaluators after source changes; it does not invent physical evidence.

[Open the Workbench](workbench/maglev/index.html),
[review calculations, CAD and videos](design-engine/ferrite-maglev/reference/index.html),
[read implementation and open work](../engineering/ferrite_maglev/README.md),
[review v0.5.2 development notes](releases/v0.5.2.md),
or [download the reader book](../OpenSourceRail-Book.pdf).

Published v0.5.1 remains preserved. This document describes v0.5.2 development on
main and does not announce a new release.

<!-- Generated by tools/automation/generate-public-overview.py; do not hand-edit. -->
