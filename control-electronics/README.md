# Maglev control electronics

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Maglev documents below are retained historical research, not the selected v0.6 physical design.

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
