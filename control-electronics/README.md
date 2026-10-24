# Maglev control electronics

<!-- osr-system-context:start -->
OpenSourceRail develops an open, locally buildable urban railway with fixed linear motors at stations and, where needed, located boosters. Trains coast between powered zones while onboard ferrite support, guidance and passenger services remain independently powered; passengers transfer between fixed lines at junctions. Simple vehicles, repeated civil works and repairable local production aim for high useful passenger throughput and affordable construction, operation and debt repayment. Current studies and digital workflows support development; an accepted physical railway has not been established.

[Project introduction](../README.md) · [Engineering approach and current status](../engineering/ferrite_maglev/README.md)
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
