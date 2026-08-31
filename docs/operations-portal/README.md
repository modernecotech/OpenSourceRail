# OSR Operations Portal

Static browser portal for city-level operations data:

- Authenticated OSR Ops Core work orders, managed inspection photos/files,
  independent handback, controlled document revisions, defects/NCR and sealed
  audit records persisted in SQLite.
- Manufacturing schedule for trains, waypoints/W-SBCs, track sections,
  switches, stations, depots, production plant fixtures, energy sites,
  and station systems.
- Construction QA gates and asset-level QA actions.
- Maintenance schedule expanded to trainsets, stations, track sections,
  waypoints, switches, structures, energy sites, signalling/comms nodes, depots,
  and production-plant tools.
- Asset register with stable ids.
- Revisioned project digital twin with finite-resource CPM, critical path,
  supplier/order-by planning, schedule of values, monthly cash requirements,
  and an IFC/animation-ready construction-state timeline.
- Launch/status panels for existing OCC, simulator, CBM, AFC, historian,
  and Ops Core tooling.

The simplified operating model is documented in
[`ops-core.md`](ops-core.md).

Configured deployments enforce city-scoped roles for planners, maintainers,
inspectors, approvers, document controllers and auditors. Passing work requires
a different authenticated inspector and handback approver; rejection returns
work for rework and open NCRs block closeout. The server seals immutable records
with HMAC-SHA256 content attestations. These provide tamper evidence inside the
deployment but are not qualified electronic signatures or a substitute for an
organisation's legal signature policy.

For the integrated City Studio → simulation → OCC replay → work-order flow,
run the [OSR Workbench](../workbench/README.md). Workbench-created records retain
their revision, approved baseline, run and selected-asset references.

## Generate Data

```bash
python3 tools/automation/generate-qa-maintenance-data.py
```

The default input is the generated Samawah design and scenario:

- `cities/catalogue/west-asia/Iraq/Samawah/design.toml`
- `cities/catalogue/west-asia/Iraq/Samawah/samawah.toml`

Outputs land in `build/generated-operations/samawah/`:

- `samawah-operations.json.gz` plus its small integrity manifest
- `samawah-assets.csv`
- `samawah-manufacturing-schedule.csv`
- `samawah-manufacturing-materials.csv`
- `samawah-manufacturing-verification.csv`
- `samawah-procurement-plan.csv`
- `samawah-budget-work-packages.csv`
- `samawah-cashflow-requirements.csv`
- `samawah-construction-timeline.json`
- `samawah-acceptance-evidence-matrix.csv`
- `samawah-maintenance-schedule.csv`
- `samawah-qa-register.csv`

The Manufacturing tab is generated from
[`../../lib/templates/manufacturing-schedule.toml`](../../lib/templates/manufacturing-schedule.toml)
and documented in
[`../rfcs/0030-manufacturing-schedule-system.md`](../rfcs/0030-manufacturing-schedule-system.md).
Track-section durations are calculated from route metres or single-track ST6
panel quantities, production rate and resource count. The JSON bundle also
contains a line-level `civil_production` plan derived from civil-segment metres,
Pi20/Pi25 bays, foundations, mould/cure cycles, piling rigs, launcher rate,
panel gantries and the working calendar.
Each schedule row includes the asset id, project-day schedule window, work
center, crew roles, staff tasks, controlled BOM/material refs,
dependencies, deliverables, evidence required, release authority, QA
action link, verification row, and priority.

The Project Twin tab uses the same records. Work-centre capacities produce a
finite-resource baseline; a CPM backward pass adds late dates, float and the
critical flag. BOM requirements are deduplicated per asset, connected to their
required-on-site task, and given a source-class planning lead time. Authoritative
city CAPEX is allocated into schedule-of-values work packages, so changing a
task or resource capacity moves its order-by and monthly cash requirement on
regeneration. The cashflow reconciles to the finance summary; it is not an
invoice or funding commitment.
Month `0` contains mobilisation requirements before notice to proceed; negative
order-by days identify long-lead actions that must be resolved before baseline approval.

For a repository city, the compact Git-reviewable output is
`engineering/project-twin/summary.json`. The complete records live in the
reproducible compressed operations bundle. Planned purchase-order rows are
explicitly `planned-not-issued`; using **Create draft** persists a distinct
actual-side record without altering the generated baseline.

The generated material table links rolling-stock packages to
`build/bom/rolling_stock_bom.csv` and
`build/bom/rolling_stock_cots_fitout_bom.csv`. Infrastructure packages use
controlled `project_kit:*` refs until detailed civil/station/energy BOMs
exist. The verification table links every manufacturing row to a QA action
and marks the QA hold point that blocks successor work.

The acceptance/accreditation evidence basis is generated as
`build/generated-operations/samawah/acceptance-evidence-report.md`. It
summarizes the controlled material/BOM basis, QA gate coverage, release
blocking logic, and links to the evidence matrix CSV.

## Run With SQLite

Serve the repository root and persist Ops Core work orders, inspections,
defects, audit events, purchase orders, deliveries, invoices, payments,
progress updates and project revisions to SQLite:

```bash
python3 tools/automation/ops-core-server.py --port 8008
```

The server creates the database and schema automatically if they do not
exist. The default database path is:

```text
var/ops-core.sqlite3
```

Then open:

```text
http://127.0.0.1:8008/docs/operations-portal/
```

Localhost starts in clearly labelled trusted-development mode. Before shared or
network deployment, create private user accounts and start with the user store:

```bash
python3 tools/automation/ops-user-admin.py var/ops-users.json inspector1 --display-name "Inspector One" --roles inspector --cities samawah
python3 tools/automation/ops-core-server.py --host 0.0.0.0 --port 8008 --users var/ops-users.json
```

Create separate approver and document-controller identities the same way. The
server refuses a non-localhost bind without a configured user store. Put TLS in
front of it for any network deployment; keep `var/ops-users.json` and the
generated signing key private.

## Evidence, Document Control and Backup

Inspection files and photos are stored content-addressed under
`var/ops-evidence/`, with their SHA-256, uploader and immutable record retained
in SQLite. The Controlled Documents panel requires a document id and revision;
a later revision must name the record it supersedes.

Create and verify a consistent SQLite/evidence backup with:

```bash
python3 tools/automation/ops-core-backup.py create backups/ops-core.zip
python3 tools/automation/ops-core-backup.py verify backups/ops-core.zip
```

The archive deliberately excludes the password store and server signing key.
Back those up separately in the deployment's secret vault. Recovery remains an
operator-controlled procedure so the tool cannot overwrite a live database.

Samawah is the default dataset. To open another generated city, pass its
repository-relative operations bundle in the `data` query parameter.

## Static Fallback

The portal can still run as a static site:

```bash
python3 -m http.server 8008
```

In that mode the Ops Core tab falls back to browser local storage and has no
accountable identity or managed files. Use it only for demonstration. Use the
authenticated SQLite server for shared consoles, backup, or handover
evidence. Manufacturing rows become normal Ops Core work orders with
`source_type = manufacturing`, so production tasks share the same evidence,
defect/NCR, audit, and reconciliation path as QA and maintenance work.
The portal blocks successor manufacturing work until predecessor rows are
closed with pass evidence, and it blocks manufacturing closeout until pass
evidence exists for the selected work order.

## Reconcile Local Records

If a console was used in static/local mode before SQLite was available,
open the portal through `ops-core-server.py` and use **Storage
Reconciliation** in the Ops Core tab. It compares SQLite with the
browser-local fallback records and can merge local-only records into
SQLite while keeping the newest record when ids conflict.

Open:

```text
http://127.0.0.1:8008/docs/operations-portal/
```
