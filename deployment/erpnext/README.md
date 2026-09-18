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

The private city feedback export also carries [engineering revision
exposure](../../docs/lifecycle/README.md#engineering-revision-exposure): explicit
nested BOMs, draft/unfinished production, potential purchases and linked stock
movements. It uses native document permissions and preserves coverage warnings.
Workbench displays and downloads these observations. The native Project's
**OpenSourceRail → Revision dispositions** workflow adds assigned, immutable
proposals and independent endorsement/rejection records. Stale or incomplete
exposure cannot receive an endorsement. Recording never executes the proposed
ERP action or grants railway release. Independent native-outcome verification
covers retention, cancellation, direct amendments, production stops, corrective
Job Cards with accepted inspections, performed stock inspections and native
movement traces. Evidence remains immutable and later changes make it stale;
see the [verification workflow and upgrade limits](../../docs/lifecycle/README.md#independent-native-outcome-verification).

After a backup, rebuild/restart the app, run `./osr erp bench migrate` to install
the three disposition record types, then `./osr erp snapshot` to refresh feedback.
Manufacturing Manager, Projects Manager and System Manager roles can use the
workflow subject to project/exposure access; reviewer, proposer and responsible
person must satisfy the independent-review checks. Inspection and trace readers
also need native Quality Manager and Stock User access, respectively.

The [complete example-city test](../example-city/README.md) installs a separate
site and checks actual planning, purchasing, manufacturing, serial movements,
maintenance and Workbench/FUXA behavior. Native regression scripts accept
`OSR_TEST_SITE` (default `osr.localhost`) so the same checks can run in that site.

Condition routing maps `low`, `medium` and `high` alarm priority to native Issue
priority when creating a case. Later events preserve operator triage changes.
Rules without a priority use `medium`; display-only rules do not create cases
on activation or clearance unless an earlier enabled rule already routed the
same incident.
