# ERPNext operating deployment

This composition runs ERPNext, Frappe HR, the OSR reference integration,
MariaDB, Redis, workers, scheduler, websocket server and nginx frontend.

Use the root `./osr erp` launcher. Setup, ownership, import and backup procedures
are in the [operating platform guide](../../docs/operating/README.md).
Secrets and local configuration live under `var/erpnext/`, outside this tree.

MariaDB stores its data in the persistent `db-data` volume and temporary InnoDB
files in a separate bounded 512 MiB `/tmp` filesystem (mode 1777). A healthy
container and a successful `/api/method/ping` response are separate checks from
the city planning validators. If MariaDB reports missing temporary files, retain
the data volume and restore temporary storage; do not reinitialise the database.

The [Baghdad detailed engineering register](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/detail/README.md)
lists reference parts and ERP handover requirements. These rows are not live
Items, submitted BOMs or approved Work Orders; import only a released, priced
family MBOM with real company, warehouse, operator and supplier inputs.
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

The [Baghdad qualification package](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/qualification/README.md)
provides ten source-bound evidence Tasks, including the independently operated
first-section option. Preview with `bench --site SITE execute
osr_erpnext.qualification.import_tasks --kwargs '{"package_path":"/path/to/erpnext-tasks.json"}'`;
set `"apply": True` for a reviewed local import; this installed Bench CLI parses Python literals in `--kwargs`. The importer
creates open native Tasks and refreshes descriptions by stable subject. It
preserves actual assignment, project, dates, priority and status when repeating
an import; it never completes an evidence task or grants acceptance. Assign a
named accountable person through ERP; role labels are not user assignments.
Physical result verification uses independently supplied reviewer keys and signed
source/criteria-bound results. Generated templates contain no measurements,
quotations, signatures or operating release. Local task mappings belong in
`var/erpnext/`, rather than the public proposal archive.

The [Baghdad workforce pilot](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/delivery-baseline/WORKFORCE-COMPETENCE.md)
maps workload, recruitment and practical assessment to native HR records. Run
`bench --site SITE execute osr_erpnext.workforce.administration_readiness`
to inspect local schemas and the caller's read permissions. This does not prove
that anyone has been appointed or authorised. The bench-only
`osr_erpnext.workforce.preview_assignment` accepts `project`, `task`, `employee`
and `authorisation_file`; the private File must belong to that active Employee
and its controlled JSON packet must match the Project baseline and Task.
HR Manager or System Manager plus native read permissions are required. Preview
at planning and again at task start, with current resource evidence. It creates
no assignment, permit, competence record or railway release. Keep native worker
records and private attachments out of public exports. The six delivery evidence
drafts use the existing Task importer and preserve actual owners/status.
