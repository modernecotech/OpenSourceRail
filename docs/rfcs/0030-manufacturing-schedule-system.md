# RFC 0030 - Manufacturing Schedule System

Status: v1 accepted baseline

## 1. Decision

OpenSourceRail uses one generated **manufacturing schedule system** for
locally built trains and infrastructure. The same city asset register that
feeds QA and maintenance also feeds production work packages for:

- trainsets
- waypoints / W-SBC nodes
- track sections
- switches and crossings
- stations
- depots and the railway production plant
- energy sites
- station systems and signalling/comms nodes
- whole-system baseline and trial-running release

The authoritative template is
[`lib/templates/manufacturing-schedule.toml`](../../lib/templates/manufacturing-schedule.toml).
The generated, spreadsheet-friendly city outputs are created by
[`scripts/generate-qa-maintenance-data.py`](../../scripts/generate-qa-maintenance-data.py).
They include the schedule, material/BOM control rows, and stage QA
verification rows.

## 2. Why

The project is an owner-builder system, so manufacturing cannot be treated
as a black-box supplier milestone. A city needs a practical schedule that
answers:

- what is being built
- which asset id it belongs to
- where the work happens
- which crew roles are accountable
- what staff tasks must be completed
- what materials, inputs, and predecessors are required
- what evidence is needed for QA and commissioning
- which rows should become work orders

The system is deliberately lighter than ERP/MES software. It is designed to
be useful on day one in a local railway production plant, depot, station
site office, or owner engineer console.

## 3. Data Model

Each generated manufacturing row contains:

| Field | Purpose |
|---|---|
| `manufacturing_uid` | Stable city + asset + package id |
| `asset_id`, `asset_name`, `asset_type`, `line` | Links work to the generated asset register |
| `package_id`, `phase`, `sequence` | Work package and ordering |
| `work_center` | Plant, depot, site, bench, or crew location |
| `duration_days` | Planning duration |
| `planned_start_day`, `planned_finish_day` | Project-day schedule window |
| `predecessors`, `predecessor_uids` | Package dependencies and resolved predecessor rows |
| `work_order_title`, `work_order_detail` | Text used when opening an Ops Core work order |
| `staff_roles`, `staff_tasks` | Crew accountability and task detail |
| `bom_refs`, `material_count`, `material_status` | Controlled material/BOM references and generated kit status |
| `materials_or_inputs`, `deliverables` | Human-readable material/input summary and produced output |
| `evidence_required` | QA, commissioning, or handover proof |
| `release_authority` | Person/role allowed to release the work |
| `qa_gate_hint`, `qa_uid`, `verification_uid` | Link to the relevant construction QA action and verification row |
| `priority`, `status` | Work-order priority and schedule state |

The generator also emits:

| Table | Purpose |
|---|---|
| `manufacturing_materials` | One controlled material/BOM row per manufacturing package reference, including BOM source, line id/category, description, quantity basis, cost basis, traceability requirement, and receiving evidence. |
| `manufacturing_verifications` | One QA hold-point row per manufacturing package, linked to the generated QA action by `qa_uid`, with required result, release authority, evidence, and successor-blocking rule. |

Rolling-stock packages reference the generated BOM files:

- [`build/bom/rolling_stock_bom.csv`](../../build/bom/rolling_stock_bom.csv)
- [`build/bom/rolling_stock_cots_fitout_bom.csv`](../../build/bom/rolling_stock_cots_fitout_bom.csv)

Infrastructure packages use controlled `project_kit:*` references until
detailed civil, station, depot, wayside, switch, and energy BOM files are
added. They still produce material-control rows and traceability evidence.

## 4. Scheduling Rule

The baseline schedule uses project-day offsets from notice-to-proceed.
Those offsets are placeholders until a city baseline is approved; they can
be converted to real dates in a spreadsheet or future calendar view.

The generator staggers assets by type:

- depots and production plant start early because they unblock train and
  site work
- stations, civil works, and energy work start before heavy train
  commissioning
- waypoints and station systems follow civil readiness and bench testing
- rolling-stock tasks are serialised by trainset number

This creates a useful first-pass production plan without pretending to be a
resource-levelled Primavera replacement.

## 5. Work Orders

The Operations Portal has a **Manufacturing** tab. Any row can be opened as
an Ops Core work order with:

- source type `manufacturing`
- source uid equal to `manufacturing_uid`
- owner from `release_authority`
- priority from the package
- asset id and asset type from the asset register
- title from `package_id` plus `work_order_title`

Once opened, the work order follows the same lifecycle as maintenance and
QA work:

`open -> assigned -> in_progress -> ready_to_close -> closed`

It can also be placed on `hold`, receive evidence records, create
defects/NCRs, and appear in the audit trail.

The portal enforces two release rules:

- A manufacturing work order cannot be opened while resolved predecessor
  manufacturing rows have not been closed with pass evidence.
- A manufacturing work order cannot move to `ready_to_close` or `closed`
  until it has pass evidence and material/BOM references.

## 6. SQLite Storage

Manufacturing work orders are stored in the existing Ops Core SQLite
tables. No separate manufacturing database is required.

The server creates the database automatically at:

```text
var/ops-core.sqlite3
```

If a browser is used offline or through a static server, local records can
later be reconciled into SQLite through the Storage Reconciliation panel.

## 7. Waypoints

The generator now creates `waypoint` assets for route sections. These are
the practical W-Node / W-SBC production units used by wayside safety,
radio, beacon, intrusion, and section-state functions. They receive:

- manufacturing packages
- QA coverage through `qa-26-wayside-comms-safety`
- maintenance coverage through systems maintenance intervals

Waypoint install packages resolve their track-section predecessor where
the generated asset relationship identifies the parent track section.

## 8. Not Included

This is not a full ERP/MES system. The first version does not include:

- material stock decrementing
- purchase orders
- labour payroll
- finite-capacity resource levelling
- barcoded shop-floor terminals
- earned-value reporting
- detailed non-rolling-stock BOM files beyond controlled project-kit refs

Those can be added later if field operations need them. The baseline target
is simpler: asset-specific manufacturing schedule, controlled material/BOM
rows, staff tasks, QA verification, work orders, evidence, defects/NCR,
and SQLite-backed audit.
