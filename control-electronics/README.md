# Maglev control electronics

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
