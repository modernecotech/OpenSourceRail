# Deployment and integration

<!-- osr-system-context:start -->
OpenSourceRail develops affordable rail that local companies can build, maintain and improve. The published digital release joins a costed vehicle, civil works, controls, production plan and Workbench journey; Baghdad has separate elevated city planning alternatives. The earlier v0.6 passive-wheel, station-launch design remains research, not the installed drive selection for the v0.7 reference or Baghdad. Each candidate retains its own geometry, mass, service, power, cost and evidence. Safety and accessibility remain requirements. Digital results do not grant fabrication or passenger-operation approval.

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
