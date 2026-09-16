# ERPNext operating deployment

This composition runs ERPNext, Frappe HR, the OSR reference integration,
MariaDB, Redis, workers, scheduler, websocket server and nginx frontend.

Use the root `./osr erp` launcher. Setup, ownership, import and backup procedures
are in the [operating platform guide](../../docs/operating/README.md).
Secrets and local configuration live under `var/erpnext/`, outside this tree.
The generated [catalogue readiness report](../../docs/operating/readiness.md)
validates all city profiles and component packages and identifies which full
task payloads still need on-demand materialisation before import.

The local Workbench embeds native ERP screens with native authentication. The proxy
allows framing only by the explicitly listed Workbench origins; see the
[Workbench integration guide](../../docs/workbench/README.md#integrated-lifecycle-workspace).
