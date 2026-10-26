# OpenSourceRail engineering

**Current development default:** [comfort-first six-car design](../docs/design-engine/current/README.md), selected by [development-baseline.toml](development-baseline.toml). Use `./osr status`, `./osr build`, `./osr verify` and `./osr workbench`. New current adapters live in `engineering/development_baseline/`; the ferrite implementation below is a retained research method, not the default vehicle.


<!-- osr-system-context:start -->
OpenSourceRail develops simple, affordable, locally maintainable urban transport. The development default is six 17 m comfort cars, each with 44 seats plus two wheelchair places and no planned standing; the 120-second service target gives 8,280 normal passengers/hour/direction. All permanent magnets and suspension controls remain onboard; concrete beams carry passive steel facings, while station windings provide launch and receiving power. Lightweight assemblies, repeated civil works and repairable local production support the low-cost ethos. Stable physical operation and manufacturing release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
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
