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

A condition-created Issue with a reviewed ERP Asset exposes **OpenSourceRail →
Prepare repair**. Preview validates the Issue/project/Asset identity, technician,
city warehouse, stock Item, optional serial/batch bundle and current availability.
Apply creates one unsubmitted native Asset Repair and ToDo assignment; it never
submits stock consumption, closes the Issue or grants railway handback. Repeating
the same reviewed request returns the existing record and preserves operator edits.
The native repair form remains responsible for actions performed, completion,
actual downtime, parts consumption and accounting. Its OSR provenance fields link
back to condition history and the existing lifecycle/serial evidence.
