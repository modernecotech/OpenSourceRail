# OSR Operations Portal

Static browser portal for city-level operations data:

- OSR Ops Core work orders, inspection evidence, independent handback,
  defects/NCR and audit trail persisted in SQLite, with browser-local fallback.
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

Passing work requires a named inspector and a different named handback
approver. Rejection returns work for rework and open NCRs block closeout. This
is a typed attestation workflow; authentication, RBAC and qualified electronic
signatures remain explicit deployment gaps.

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

Samawah is the default dataset. To open another generated city, pass its
repository-relative operations bundle in the `data` query parameter.

## Static Fallback

The portal can still run as a static site:

```bash
python3 -m http.server 8008
```

In that mode the Ops Core tab falls back to browser local storage. Use
the SQLite server for real operations, shared consoles, backup, or handover
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
