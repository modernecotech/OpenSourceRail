# OpenSourceRail Rust control and integration software

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

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
