# OpenSourceRail Rust research software

<!-- osr-system-context:start -->
OpenSourceRail develops an open, locally buildable urban railway with fixed linear motors at stations and, where needed, located boosters. Trains coast between powered zones while onboard ferrite support, guidance and passenger services remain independently powered; passengers transfer between fixed lines at junctions. Simple vehicles, repeated civil works and repairable local production aim for high useful passenger throughput and affordable construction, operation and debt repayment. Current studies and digital workflows support development; an accepted physical railway has not been established.

[Project introduction](../README.md) · [Engineering approach and current status](../engineering/ferrite_maglev/README.md)
<!-- osr-system-context:end -->

[`osr-maglev-control`](osr-maglev-control/README.md) implements fixed-module
maglev control research, offline SBC replays and advisory evacuation logic.
The [development profile](../deployment/maglev.toml) configures no physical
outputs or hardware addresses.

Other workspace packages retain reusable protection arithmetic, resource
reservation, consensus, authentication, networking, BMS, doors, passenger
information, HVAC, lighting, energy, fare and observation functions. They are
unqualified research libraries. Their defaults and synthetic regression
fixtures are not accepted vehicle or hardware configurations.

Generic alignment and routing libraries operate on planning geometry.
Vehicle dynamics, banking, tolerances, foundations, physical sensing and
hardware integration require configuration-specific evaluation.

Run `cargo test --locked --workspace --all-targets` for all retained Rust
unit/property tests. `./osr test` additionally checks the current design,
publication and browser packages. No safety integrity rating, manufacturing
release or physical operating approval is claimed.
