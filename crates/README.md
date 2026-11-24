# OpenSourceRail Rust control and integration software

<!-- osr-system-context:start -->
OpenSourceRail connects locally maintainable railway hardware, design and delivery tools, and train and wayside software. The published v0.7.2 Baghdad opening study includes a service plan, traction assessment and supplier dossier. Current development joins revised route, vehicle, power, civil and purchasing assumptions for v0.8 production preparation; first-article measurements and independent review remain open. The v0.6 passive-wheel vehicle is a separate research selector. Safety and accessibility remain mandatory, and digital results do not grant fabrication or passenger-operation approval.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The control workspace contains modules for ATP, interlocking, the control room,
train control, station dispatch, train-to-ground communication, doors,
passenger information, auxiliary power, braking protection and event records.
Their place in the current wheel railway, equipment counts and cost allocation
are set out in the [control electronics schedule](../control-electronics/README.md).
The passive v0.6 reference uses [wheel and station interface checks](../engineering/station_rail/controls.py).
The maglev controller is retained research and does not drive the current train.

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
