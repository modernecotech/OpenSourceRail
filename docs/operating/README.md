# OpenSourceRail operating platform

ERPNext is the business system of record. Frappe HR supplies personnel and
payroll on the same Frappe site. OSR retains railway engineering, control and
assurance. The [operating page](index.html) launches native ERPNext modules;
business forms, permissions and ledgers are maintained by upstream apps.

For the generic configuration, all 266 city override profiles, native operating
tasks and digital-twin feedback, use the [city operating platform](city-platform.md).
The basic import below remains available for older planning packages.

## What replaces what

| Existing OSR component or requirement | Operating owner | OSR responsibility retained |
|---|---|---|
| Project Twin execution, progress and task administration | ERPNext Project, Task, Timesheet | Design generator, finite-resource engineering baseline, source revision and scenario evidence |
| Ops Core purchase orders and procurement actuals | Material Request, Supplier Quotation, Purchase Order | Generated procurement requirements and source BOM references |
| Deliveries and material records | Purchase Receipt, Item, Warehouse, Stock Entry, Serial No / Batch | Railway asset identity and engineering configuration |
| Invoices, payments, budgets and cashflow actuals | Purchase Invoice, Payment Entry, Budget, Cost Center, accounts | Parametric estimates and finance sensitivities remain planning evidence |
| Manufacturing administration | BOM, Workstation, Work Order, Job Card, Quality Inspection | Railway manufacturing definitions, travellers and assurance hold points |
| Routine maintenance administration | Asset, Asset Maintenance, Asset Maintenance Log, Asset Repair | CBM telemetry, defect severity, railway work evidence and independent handback |
| HR and ordinary workforce administration | Frappe HR Employee, Recruitment, Shift Assignment, Attendance, Leave, Payroll, Expense Claim | Railway competence/fitness acceptance and safety-critical roster constraints |
| Ordinary business attachments and approvals | Frappe File, roles, permissions, workflows and document history | Controlled engineering revisions, sealed inspections, NCRs and railway release evidence |
| OCC, signalling, ATP/ATO, train electronics, depot movements, AFC, historian | OpenSourceRail railway components | Entire railway-specific function |

ERPNext's **Work Order** means manufacturing production. Routine maintenance
uses **Asset Maintenance / Asset Repair**, not a manufacturing Work Order.
Frappe HR is a separate app; installing ERPNext alone does not supply payroll.

## Local installation

Requires Docker Engine with Compose and Buildx. The local composition binds
only `127.0.0.1:8080`; MariaDB and Redis have no published ports.

```bash
./osr erp init
./osr erp build
./osr erp up
./osr erp setup
./osr erp status
```

Open <http://127.0.0.1:8080>. Log in as `Administrator` using the generated
`ADMIN_PASSWORD` in `var/erpnext/local.env` (mode 0600, ignored by Git and not
served by OSR). Complete ERPNext's setup wizard for the actual organisation.
Do not replace a real legal entity with the evaluation fixture below.

The image pins ERPNext `v15.121.2` and Frappe HR `v15.64.0` on the maintained
v15 line. It extends the official ERPNext image with the local `osr_erpnext`
app. Frappe comes from that image; `./osr erp bench list-apps` reports the exact
installed versions. The app adds reference fields and a workspace using
installation/migration hooks, with no edits to upstream source.

For rootless Docker installed in `~/bin`, the launcher finds Docker there.
The user service starts at login; persistence without a login requires the
host administrator to configure user lingering. No rootful daemon is needed.

Run `./osr` and select **Operating · ERPNext**. `OSR_ERP_URL` can point the OSR
server at an existing ERP site. Navigation opens a separate ERP login; OSR
actor/role URL parameters grant no ERP permissions. No API keys enter browsers.

## Import a city baseline

```bash
python3 tools/automation/erpnext-plan.py \
  cities/catalogue/west-asia/Iraq/Samawah/operations/samawah-operations.json.gz \
  --output build/erpnext/samawah-plan.json

# After creating your company in ERPNext:
./osr erp import build/erpnext/samawah-plan.json --company 'Your Company'
```

For a local evaluation only, create the explicitly named sample company:

```bash
./osr erp bench execute osr_erpnext.setup.create_evaluation_company
./osr erp import build/erpnext/samawah-plan.json --company 'OpenSourceRail Evaluation'
```

The importer creates one native Project per company/city/revision and native
Tasks for manufacturing and maintenance planning rows. Original row JSON,
city, railway asset ID, revision and SHA-256 references remain attached.
Unique source keys make retries skip existing tasks, preserving operator edits.
Changed content under an existing revision fails; a new revision creates a
separate planning project for explicit review. The import is transactional.

`--kind manufacturing` or `--kind maintenance` limits a prepared plan. The
importer carries relative working-day offsets, dependencies, CAD/BOM refs and
cadences in source evidence. It does **not** convert those into approved dates,
recurrence, task dependencies or released production/maintenance orders. Map
the approved calendar, dependencies and resources in ERPNext before execution.
Generated assets are proposed engineering objects, so the importer does not
automatically capitalize them or fabricate Item, Supplier or accounting masters.

Authenticated integrations can POST `{plan, company}` to
`/api/method/osr_erpnext.api.import_plan` using Frappe's token authentication.
The endpoint checks Project/Task creation permissions and Company access.
Use dedicated users with appropriate Company User Permissions and project
access; cities are provenance fields, not automatic tenancy boundaries.

## Cutover and existing records

1. Back up SQLite/evidence with `ops-core-backup.py` and preserve its signing
   key separately. Keep historic records for audit; do not delete them.
2. Configure actual companies, users, company permissions, currency, chart of
   accounts, fiscal years, warehouses, suppliers, items and asset categories.
3. Import a reviewed engineering baseline. Map actual assets and material/BOM
   definitions; commission maintenance schedules and manufacturing orders.
4. Reconcile historic Ops Core purchases, deliveries, invoices, payments and
   progress with ERPNext using its Data Import and accountant-reviewed opening
   records. These collections remain readable in OSR; their mutation is now
   rejected server-side. No automatic ledger migration is supplied.
5. Use ERPNext for all new business records. OSR railway work records continue
   to carry inspections, NCRs, controlled documents and independent handback.

Permission-filtered business snapshots return to the Workbench through the
[city feedback bridge](city-platform.md). No reverse writes to railway state are installed. ERP completion, quality acceptance,
employee attendance or stock receipt never grants railway release authority.
An ERP outage must not stop interlocking, dispatch or railway assurance reads.
This change supplies business applications and a planning handoff, not a
completed migration of an operator's financial or personnel records.

## Operations and recovery

```bash
./osr erp logs
./osr erp backup
./osr erp stop
```

Backups are written to the site's `private/backups` directory in the `sites`
volume. Copy them to private off-host storage along with site configuration
and its encryption key. Verify restore in a separate Compose project before
upgrading. `stop` preserves all volumes. Do not use `down -v` on real records.
For upgrades, back up first, review compatible upstream app versions, rebuild,
then migrate the site. Restore the pre-upgrade database/files with the previous
image for rollback; changing the image alone cannot undo schema migrations.

Before shared hosting, use a dedicated TLS domain, named ERP users, tested role
and company permissions, scheduled backups and restore drills. Configure local
payroll/tax rules for each legal entity. The checked-in localhost stack is an
evaluation/development installation, not a commissioned shared service.

## Further integration and automation

[Reusable operating components](components.md) provide dynamic forms and city
configuration packages for stock, production, quality, maintenance, training,
budgets, service issues and assignment rules.

See the [function review and implementation map](automation-review.md) for
procurement draft creation, automatic work-readiness checks, purchasing lifecycle
feedback and the next stock, production, maintenance and workforce integrations.

## Upstream basis and licensing

- [ERPNext source and supported business modules](https://github.com/frappe/erpnext)
- [Frappe HR source and separate-app installation](https://github.com/frappe/hrms)
- [Official container custom-image guide](https://github.com/frappe/frappe_docker/blob/main/docs/02-setup/02-build-setup.md)
- [Frappe REST API and authentication](https://docs.frappe.io/framework/user/en/api/rest)
- [Docker rootless installation](https://docs.docker.com/engine/security/rootless/)

ERPNext and Frappe HR retain GPL-3.0; Frappe Framework retains MIT. OSR's local
integration source follows the repository Apache-2.0 software license. Upstream
source/license obligations apply when distributing the combined container;
the OSR license does not relicense upstream applications.
