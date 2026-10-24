# OpenSourceRail engineering

<!-- osr-system-context:start -->
OpenSourceRail develops an open, locally buildable urban railway with fixed linear motors at stations and, where needed, located boosters. Trains coast between powered zones while onboard ferrite support, guidance and passenger services remain independently powered; passengers transfer between fixed lines at junctions. Simple vehicles, repeated civil works and repairable local production aim for high useful passenger throughput and affordable construction, operation and debt repayment. Current studies and digital workflows support development; an accepted physical railway has not been established.

[Project introduction](../README.md) · [Engineering approach and current status](ferrite_maglev/README.md)
<!-- osr-system-context:end -->

The [station-powered ferrite maglev package](ferrite_maglev/README.md) owns current
requirements, configuration, mechanical/civil studies, city planning,
manufacturing quantities and the evidence workflow. Station LSMs launch and
receive the train; onboard active PM support and services remain independent
through the unpowered coast.

The [candidate design loop](design_search/README.md) connects bounded specialist
tasks, actual domain evaluators, reproducible comparison and candidate-bound
CAD/BOM/BIM/delivery research packages. It keeps digital execution separate from
physical qualification and never treats unknown equipment as zero mass.

[Operating calculations](ferrite_maglev/station.py) address jerk-limited motion,
magnetic overlap, station power, charging and reservation boundaries.
[Structure and production studies](ferrite_maglev/station_structure.py) calculate
GFRP panel stock, mass budgets, guidebeam/support quantities and bottleneck
capacity. [Native CAD utilities](factory_examples/native.py) construct and reopen
partial material definitions. [Regression tests](analysis/tests/) cover numerical
controls, source/evidence binding, offline Rust integration and publication.

The current [dimensioned six-car dynamics](../docs/design-engine/ferrite-maglev/full-dynamics/README.md)
attempts fourteen cases using actual current-based magnetic/electrical models.
Twelve stop at initial support/current checks and two at curve/gap geometry;
none supplies continued post-fault motion. The older coupled replay covers one
stationary rigid car and vertical beam and remains separate evidence. The
[research closure programme](../docs/design-engine/ferrite-maglev/research-closure/README.md)
orders the next magnetic, propulsion, route and qualification work. No complete
manufacturing design, qualified construction process or physical release is claimed.
