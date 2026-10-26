# OpenSourceRail Rust research software

<!-- osr-system-context:start -->
OpenSourceRail develops simple, affordable, locally maintainable urban transport. The development default is six 17 m comfort cars, each with 44 seats plus two wheelchair places and no planned standing; the 120-second service target gives 8,280 normal passengers/hour/direction. All permanent magnets and suspension controls remain onboard; concrete beams carry passive steel facings, while station windings provide launch and receiving power. Lightweight assemblies, repeated civil works and repairable local production support the low-cost ethos. Stable physical operation and manufacturing release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
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
