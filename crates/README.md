# OpenSourceRail Rust control and integration software

<!-- osr-system-context:start -->
OpenSourceRail develops affordable rail that local companies can build, maintain and improve. The published digital release joins a costed vehicle, civil works, controls, production plan and Workbench journey; Baghdad has separate elevated city planning alternatives. The earlier v0.6 passive-wheel, station-launch design remains research, not the installed drive selection for the v0.7 reference or Baghdad. Each candidate retains its own geometry, mass, service, power, cost and evidence. Safety and accessibility remain requirements. Digital results do not grant fabrication or passenger-operation approval.

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
