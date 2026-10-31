# OpenSourceRail Rust control and integration software

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The Rust workspace contains research libraries for ATP, interlocking, OCC,
TCMS, station control, train-to-ground communication, doors, passenger
information, auxiliary power, energy, braking-related protection, event
recording and lifecycle identity. The selected v0.6 candidate reuses control
libraries through [candidate-bound wheel/station interface checks](../engineering/station_rail/controls.py).

These libraries and checks support software development. They do not qualify
physical brakes, sensing, localisation, communications, equipment timing,
hardware interfaces or the operating plant. No safety integrity rating,
manufacturing release or passenger-operation approval is claimed.

Generic alignment and routing libraries operate on planning geometry. Vehicle
dynamics, banking, tolerances, foundations, physical sensing and hardware
integration require candidate-specific evaluation.

Run `cargo test --locked --workspace --all-targets` for workspace Rust checks.
`./osr test` additionally runs the current engineering, publication and browser
checks.
