# Roadmap

OpenSourceRail v0.5.2 development coordinates station-powered ferrite maglev across
mechanical, civil, software, manufacturing and city planning. Station LSMs launch
and receive the train; independent onboard support and passenger services remain
active during the unpowered coast. [Implemented work](../engineering/ferrite_maglev/README.md)
and the [current report](design-engine/ferrite-maglev/reference/index.html) identify
the tested digital scope. Accepted engineering and physical releases remain zero.

## Primary maglev closure queue

| Package | Evidence required for closure |
|---|---|
| Requirements and configuration | Approved six-car loads, service/grade envelope, door layout, tolerances and quantitative acceptance criteria |
| GFRP body | Sized orthotropic panels, longitudinal members, magnetic hardpoints, joints, openings and coupler/crash paths; fire, heat, fatigue, repair and weighed equipment closure |
| Magnetic assemblies | Complete shared or separately priced support/guidance/thrust circuits, cartridge retention, capture, sensors and tolerances |
| Magnetic force and loss | Converged finite-geometry/steel/coil maps over gap, phase, current and temperature, followed by rig correlation; no automatic ring-paper gain credit |
| Station propulsion | Selected fixed-group/section topology, phase registration, winding R/L/flux, current/voltage/thermal limits, receiving brakes, fault response and actual purchasing quantities |
| Service energy and charging | Verified hot/normal duty, battery life/reserve, complete dwell charging, power-loss support and recovery mission |
| Civil kit | Prestress/rebar/cover/end blocks, bearings, rail anchors, joints, hollow support connections, ground-specific foundations and every handling/construction stage |
| Launch and protection | Atomic corridor/receiving-berth reservation, persistent committed ownership, proved tail clearance, independent receiving readiness and stopping/holding under faults |
| Coupled dynamics | Moving six-car loads, flexible body, lateral/torsional response, curves, joints and soil with calibrated magnetic/electrical/thermal dynamics |
| Hardware | Isolated I/O, current drives, protection/watchdogs and measured end-to-end timing on selected SBC/MCU equipment |
| City delivery | Grade/coasting arrival margins, surveyed routes/utilities, terminal return geometry, depot/recovery access and evacuation at every stop location |
| Factory and erection | Measured mould/cure cycles, strength releases, delivery/crane-at-radius plans, joint completion, survey acceptance and bottleneck output |
| Economics and origin | Complete origin-traced MBOM, configured supplier offers, station/civil/fleet scope, capital/tooling, maintenance, financing and uncertainty |
| Demonstrator | Manufactured serials and exact revisions, independent inspections, measured system operation and physical acceptance |

The implemented station study adds jerk-limited launch/coast/arrival calculations,
magnetic-band overlap, receiving-brake duty and headway/power/cost sensitivities.
The structure study adds quantity-derived GFRP cases, orientation seeds, five beam
families, support/foundation screens and a two-shift bottleneck model. These are
calculated candidates and production targets; they do not supply the missing
structural, magnetic or measured factory evidence.

The adaptive designer uses preceding results to propose vehicle-mass, beam/span
and actual Rust-gain variants. It preserves ancestry/traces and uses separate
confirmation cases. Its current coupled plant remains a stationary single rigid
car with ideal magnetic forces. A preferred candidate therefore remains a bounded
research result, without automatic promotion to accepted geometry or city criteria.

The dependency runner rebuilds stale implemented studies and holds downstream
outputs after failures. Completing every automated check does not complete the
engineering queue. Published v0.5.1 remains a distinct preserved release; this
revision is documented in [v0.5.2 development notes](releases/v0.5.2.md).
