# OpenSourceRail Rust research software

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Historical studies retain their own recorded configurations and results.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The v0.6 reference reuses ATP, interlocking, OCC, TCMS, door and station-control
libraries through [candidate-bound wheel/station interface tests](../engineering/station_rail/controls.py).
Station-led dispatch retains independent onboard protection and brakes. These
executions do not qualify physical braking, localisation or the operating plant.

[`osr-maglev-control`](osr-maglev-control/README.md) retains fixed-module maglev
research, offline SBC replays and advisory evacuation logic. Its
[development profile](../deployment/maglev.toml) configures no physical outputs
or hardware addresses and is not the v0.6 vehicle configuration.

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
