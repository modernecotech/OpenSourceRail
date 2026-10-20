# OpenSourceRail Rust research software

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
