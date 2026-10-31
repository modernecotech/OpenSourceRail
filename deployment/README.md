# Deployment and integration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open.

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
