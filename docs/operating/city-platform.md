# Reproducible city operating twins

Each city has a reproducible business operating baseline alongside its railway
engineering baseline. ERPNext provides the native operating records. The OSR
integration compiles planning inputs and returns permission-filtered execution
snapshots; it never issues railway release authority.

## Configuration layers

| Layer | Location | Purpose |
|---|---|---|
| Shared configuration | [generic.toml](../../deployment/erpnext/config/generic.toml) | Departments, warehouses, task categories, programme tasks and planning calendar defaults |
| City overrides | `cities/catalogue/<region>/<country>/<city>/operations/erpnext.toml` | Identity, local calendar, organisation, operating release and additional city tasks |
| Compiled package | `build/erpnext/cities/<slug>/` | Effective configuration, complete task plan, dependency graph and checksummed summary |
| ERP execution | Native Project, Task, Department, Warehouse, Cost Center | Actual work, assignments, dates, timesheets, costing and business document workflows |
| Twin feedback | Private `var/erpnext/operating-twins.json` | Observed task/category/asset status, recorded hours, task costs and project-linked business document counts |

All 266 catalogue cities have specific override files. The compiler derives
their actual task and asset scope from their own generated operations bundle;
it does not reuse Samawah's tasks for another city. See the
[Samawah profile](../../cities/catalogue/west-asia/Iraq/Samawah/operations/erpnext.toml)
and [Mosul profile](../../cities/catalogue/west-asia/Iraq/Mosul/operations/erpnext.toml)
for local timezones, illustrative six-day construction calendars and distinct
city work packages. Other profiles inherit the shared planning assumptions
until a city operator supplies overrides.

The [catalogue readiness gate](readiness.md) validates all 266 configurations
against their own tracked asset, manifest and project-twin evidence. Supervision
can compile directly from those reviewable assets for every city. Full ERP task
plans additionally need the deterministic compressed operations payload:
Samawah and Mosul keep it locally in Git, while the other 264 materialise it with
`./osr city <slug>` before import. A manifest is not treated as a substitute for
the task records it hashes.

Tables merge recursively. Lists explicitly replace the shared list. Unknown
keys fail validation. `city_programme` adds city tasks to the shared programme;
each task needs a unique ID. Removing a department requires updating every
task category/programme reference that used it.

The generic company, calendar start date and timezone are unset. The shared
Monday–Saturday calendar and the Iraq examples are planning assumptions,
not claims about an operator's actual roster or approved public holidays.
No employee, supplier, bank, payroll, tax or commissioned asset data is invented.

## Repeatable deployment

```bash
# Creates missing profiles; existing overrides are preserved.
./osr erp city init-configs
./osr erp city validate
./osr readiness --check

# The target company must already exist in ERPNext.
./osr erp city prepare samawah --company 'OpenSourceRail Evaluation'
./osr erp import build/erpnext/cities/samawah/plan.json \
  --company 'OpenSourceRail Evaluation'

./osr erp city prepare mosul --company 'OpenSourceRail Evaluation'
./osr erp import build/erpnext/cities/mosul/plan.json \
  --company 'OpenSourceRail Evaluation'
./osr erp snapshot
```

Replace either slug with any catalogue city. If its generated operations
bundle is missing, run `./osr city <slug>` first, or supply a generated bundle
with `prepare --bundle <path>`. Generation and preparation do not contact ERP.
Review `effective-config.json`, `summary.json` and `plan.json` before import.

To make company binding permanent, add `[organisation] company = "…"` to
the city profile. CLI `--company`, `--start-date` and `--release` overrides are
captured in the effective configuration and its checksum. No credentials
belong in tracked city profiles; use separate private site configuration.

When updating the integration code on an existing site:

```bash
./osr erp backup
./osr erp build
./osr erp up
./osr erp bench migrate
```

## Functions supplied by the city package

- **Manufacturing delivery:** native Tasks with OSR manufacturing identity,
  task types, baseline day offsets and native predecessor relationships.
- **Maintenance planning:** fleet work maps to Fleet Maintenance; other
  assets map to Infrastructure Maintenance. Source cadences, triggers and
  evidence remain attached. Operators turn approved schedules and actual
  commissioned assets into native Asset Maintenance/Repair workflows.
- **Assurance coordination:** native Tasks for QA actions retain the railway
  hold point, asset, evidence and release-authority references. Completing them
  in ERPNext does not close OSR NCRs or approve railway handback.
- **Procurement packages:** requirements are grouped by sourcing route, with
  their earliest order-by and latest required-by day. All original BOM and
  sourcing requirements remain in the source record. Use native Material
  Request/Quotation/Purchase Order forms after resolving real items,
  quantities, suppliers, currency and approvals.
  The [procurement automation](automation-review.md) also converts a selected
  requirement into a native draft Material Request once the operator provides
  its Item, verified stock-unit quantity, date and city warehouse.
- **Programme and people:** tasks for governance, business masters, workforce
  planning, maintenance readiness, assurance responsibilities and recovery,
  plus the city's own additional tasks.
- **Organisation:** stable native departments, warehouse locations and a city
  cost centre, scoped by company and city. Task Types are shared. No existing
  roles or user permissions are expanded by the configuration process.
- **Digital-twin feedback:** native Project forms gain an **OpenSourceRail →
  Operating twin** action. Workbench displays matching ERP execution in the
  Project Twin view, and the operating page compares city baselines and asset
  workload. Hours/costs come from native Task costing; these are not the full
  general ledger or the city's generated CAPEX estimate.

Project and Task forms keep their source evidence, checksums and configuration
under an **OpenSourceRail reference** tab, alongside the native business tabs.

Relative working days map to dates only when `calendar.start_date` is set.
Weekends and explicit holidays are skipped, including negative mobilisation
offsets. A non-working anchor rolls forward to the next working day. The
compiler rejects missing dependencies, cycles, duplicate IDs, invalid calendars,
mixed-city records and checksum mismatches. Native ERP dependencies retain
ERPNext's business semantics, including its treatment of cancelled tasks.

## Baselines, upgrades and operator edits

The first operating release (`release = "1"`) upgrades the earlier Project/Task
import in place when source identity and hashes match. It fills empty type,
department and date fields, adds dependencies only when none exist, and
preserves existing task IDs, status, progress, assignments, priorities and
operator-entered planning fields. It also creates the new work categories.
Subsequent identical imports skip configured tasks and reuse city masters.

A changed configuration or source package cannot silently replace an applied
baseline. Increment the city's `release` and prepare again to create a separate
reviewable project baseline. Existing records stay intact. There is no automatic
transfer of actual costs or approval of a new release. Workbench's engineering
view shows execution only when exactly one exported ERP project matches the
city and engineering revision; multiple candidates require explicit review
on the operating page. No release is silently selected as authoritative.

Imports use native document validation, one database transaction and a final
project-total recalculation. A failure rolls back new masters/tasks and metadata.
The importer preloads permitted task identities and uses ERPNext's native
project bulk-update flag to avoid recalculating thousands of records repeatedly.
Use the bench-backed CLI for large city packages; a synchronous HTTP import
can exceed a deployment's request timeout. Native task-tree updates can hold
database locks during large imports, so schedule them outside active task editing.

## Refreshing the integrated twin

```bash
# One private, atomic export. Previous valid feedback survives export failures.
./osr erp snapshot

# Linux user timer: refresh every five minutes, using the local Docker/bench site.
./osr erp feedback start
./osr erp feedback status
./osr erp feedback stop
```

The timer and service are installed under `~/.config/systemd/user/` as
`osr-erp-feedback`. The user session and container runtime must be running.
The snapshot file is mode 0600 in a private directory; OSR's static server
does not expose it. Only the loopback Workbench exposes the aggregate snapshot
endpoint. Shared/network deployments need an authenticated integration service
and their own permissions; this local bridge is not a shared-host auth scheme.
The bundled single-site proxy validates browser WebSocket origins and routes
ERP notification authentication through the internal Compose network. Review
that proxy configuration when adding a public domain or TLS termination.

ERP callers can GET `/api/method/osr_erpnext.city_runtime.city_status?project=…`.
The method checks Project access and uses native permission-filtered lists for
Tasks and business documents. Unavailable document categories are marked
unavailable, not reported as zero. No employee personal details are exported.
The local bench export runs with the site's administrative visibility.

Snapshots show their observation time; the UI labels snapshots older than one
hour. **Refresh view** reads the latest exported file; it does not claim to query
ERP directly. ERP unavailability leaves the previous snapshot available with
its original timestamp and does not affect railway control.

## Verification

```bash
tools/automation/osr-python -m pytest -q \
  tools/automation/tests/test_erpnext_city.py \
  tools/automation/tests/test_erpnext_planning.py
./osr erp city validate
```

The tests cover configuration inheritance, every city's identity, working-day
calendars, dependency rejection, deterministic packages, import fingerprints,
legacy keys and company/release separation. Live validation should additionally
exercise native imports, repeated imports, permission-filtered feedback and
the Project/Workbench views against a private ERP site.

Upstream behaviour: [ERPNext Tasks](https://docs.frappe.io/erpnext/tasks),
[Asset Maintenance](https://docs.frappe.io/erpnext/asset-maintenance).
