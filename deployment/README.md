# Deployment and integration

<!-- osr-system-context:start -->
OpenSourceRail connects locally maintainable railway hardware, design and delivery tools, and train and wayside software. The published v0.7.2 Baghdad opening study includes a service plan, traction assessment and supplier dossier. Current development joins revised route, vehicle, power, civil and purchasing assumptions for v0.8 production preparation; first-article measurements and independent review remain open. The v0.6 passive-wheel vehicle is a separate research selector. Safety and accessibility remain mandatory, and digital results do not grant fabrication or passenger-operation approval.

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
