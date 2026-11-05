# Maglev control electronics

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The implemented [Rust control core](../crates/osr-maglev-control/Cargo.toml)
runs offline examples on a development computer or off-the-shelf SBC. The
[development host profile](../deployment/maglev.toml) deliberately has no
physical outputs or hardware addresses. No complete controller board, power
converter or production image is released.

The vehicle requires isolated gap/current/position sensing, fixed-winding
current drives and cooling, independent protection and watchdog functions,
battery power distribution, doors and evacuation interfaces. Onboard fixed
magnetic modules require powered control; passive guideway reaction iron does
not supply operating power.

A hardware design must specify sensor range and uncertainty, sample timing,
isolation, current/voltage protection, heat rejection, EMC, fault containment,
power-loss support, captured-state feedback and authenticated updates. SBC
selection alone does not establish these capabilities.

Reproduce the implemented software checks with `./osr test`. Hardware-in-loop,
measured deadlines, environmental and EMC testing, independent assessment and
physical validation remain open. All design/manufacturing/physical release
flags remain false.
