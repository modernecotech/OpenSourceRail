# OpenSourceRail engineering

The [station-powered ferrite maglev package](ferrite_maglev/README.md) owns current
requirements, configuration, mechanical/civil studies, city planning,
manufacturing quantities and the evidence workflow. Station LSMs launch and
receive the train; onboard active PM support and services remain independent
through the unpowered coast.

[Operating calculations](ferrite_maglev/station.py) address jerk-limited motion,
magnetic overlap, station power, charging and reservation boundaries.
[Structure and production studies](ferrite_maglev/station_structure.py) calculate
GFRP panel stock, mass budgets, guidebeam/support quantities and bottleneck
capacity. [Native CAD utilities](factory_examples/native.py) construct and reopen
partial material definitions. [Regression tests](analysis/tests/) cover numerical
controls, source/evidence binding, offline Rust integration and publication.

The current coupled replay covers one stationary rigid car and vertical beam;
it does not demonstrate the moving six-car train. No complete manufacturing
design, qualified construction process or physical release is claimed.
