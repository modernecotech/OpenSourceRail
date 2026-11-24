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

## Rehearse an equipment repair

From the repository root, run the read-only environment and input check.

```sh
tools/automation/osr-python tools/automation/v06-platform-native.py preflight
```

The [native integration guide](../docs/integration/v06-platform.md) gives the run
and evidence verification commands for a disposable v0.6 lifecycle fixture.
It follows a simulated condition through ERPNext repair and serial replacement,
including delivery of the queued alarm after an ERP and gateway interruption.
The operator workshop's [supervision replay](../docs/operator-review/screens/README.md)
shows the alarm and serial-history examples without running the integration stack.

The [former Samawah and Mosul example](https://github.com/modernecotech/OpenSourceRail/blob/a0389044828f661fe74ff314aed7fbe26748638a/deployment/example-city/README.md)
used a transactional city Workbench and a separate
[coordinated cold recovery rehearsal](https://github.com/modernecotech/OpenSourceRail/blob/a0389044828f661fe74ff314aed7fbe26748638a/docs/operating/platform-recovery.md).
The [retained example profile](recovery/example-city.json) belongs to that
historical runner. The current fixture checks recovery of a queued event.
Site-wide backup and restore still require a deployment-specific rehearsal.

## Prepare a site

The current candidate's draft BOM, manufacturing, assembly, procurement and
controls records are indexed in the
[candidate delivery package](../docs/design-engine/coupled-railway/delivery-index.json).
They are research handoffs, not approved production records or device
configurations. Site-specific roles, company and warehouse masters, permissions,
authenticated device bindings, physical protection, timing and reviewed imports
must be configured and independently accepted before deployment use.

No deployment workflow grants movement authority, physical acceptance,
manufacturing release or passenger-operation approval.
