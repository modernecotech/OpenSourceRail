# Deployment and integration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

This directory contains development compositions and integration adapters for
business records and equipment supervision. They support review and workflow
development; the repository does not provide a qualified v0.6 railway-control
image or a commissioned physical deployment.

- [`erpnext/`](erpnext/README.md) contains ERPNext, Frappe HR and the OpenSourceRail
  business-integration app for draft engineering, workforce, procurement,
  manufacturing, quality and maintenance workflows.
- [`supervision/`](supervision/README.md) contains the gateway and FUXA
  composition for observation, alarm, history and review-linked records.
- [`components.toml`](components.toml) records the software component policy.

The current candidate's draft BOM, manufacturing, assembly, procurement and
controls records are indexed in the
[candidate delivery package](../docs/design-engine/coupled-railway/delivery-index.json).
They are research handoffs, not approved production records or device
configurations. Site-specific roles, company and warehouse masters, permissions,
authenticated device bindings, physical protection, timing and reviewed imports
must be configured and independently accepted before deployment use.

No deployment workflow grants movement authority, physical acceptance,
manufacturing release or passenger-operation approval.
