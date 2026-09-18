# OSR Workbench

The Workbench presents City Studio, simulation, OCC replay, ERPNext/Frappe HR,
FUXA supervision and OSR railway assurance under one origin while preserving
their authority boundaries. Shared URL context
links the city, immutable revision, approved baseline, simulation run and
selected asset.

The collapsible **Economic planning sensitivity** panel reads the generated
[`portfolio-summary.json`](../portfolio-summary.json) through a read-only
Workbench endpoint. It shows the current OSR domestic/external capital split
and low/default/high foreign-turnkey comparisons without creating or approving
a financing record.

The **Generate a city digital twin** bar lists all 266 tracked catalogue
cities. One button creates that city's asset register, family-scoped assembly
plan, finite-resource critical path, budget work packages, supplier/order-by
plan, monthly local/imported cash requirements, QA and maintenance records,
then opens the result in Operations. Generation is an allowlisted background
job: the browser cannot supply a command or filesystem path. Output under
`build/workbench/project-twins/` is disposable; reviewed compact baselines stay
with each city under `engineering/project-twin/summary.json`.

![Workbench any-city digital-twin generator](../screenshots/workbench/city-twin-generator.png)

Install and launch it through the root [one-command setup](../../README.md#one-command-linux-setup).

Open <http://127.0.0.1:8090/>. Workbench binds only to localhost; its trusted development identity
is unsuitable for a shared network endpoint. Use the authenticated standalone
Ops Core server for shared operations records. Planning and training modes cannot emit live OCC
commands; live mode does not expose design or simulation modules. Actor and
role fields provide navigation context, not authentication. The versioned
contract is [`context-contract.schema.json`](context-contract.schema.json).
Simulator and OCC replays expose deterministic onboard, infrastructure, and
depot-data evidence for the same run; this is software-in-loop, not hardware.

## Operating platform

**City execution** opens the [business operating platform](../operating/README.md) inside the shell.
ERPNext and Frappe HR own business records and authentication. **Railway works**
retains the OSR engineering baseline, inspections, NCRs and handback evidence.
Set `OSR_ERP_URL` before starting Workbench to use another ERPNext installation.

The [city operating twin](../operating/city-platform.md) joins generic and city-specific
ERP configurations to each engineering baseline. The local `/api/operating/twins`
endpoint reads private ERP feedback snapshots; the operating page shows city,
revision, timestamp, task categories, actual task costs and asset workload. The
Project Twin panel uses an exact city/revision match and requires a unique
operating baseline. Run `./osr erp feedback start` for five-minute refreshes.

## Integrated lifecycle workspace

The Workbench now embeds **Connected assets**, **City execution**, the native
ERPNext/Frappe HR screens and **FUXA supervision** alongside City Studio,
simulation, OCC and railway works. The default lifecycle overview links plan,
design, procurement, manufacture, construction, commissioning, operation,
maintenance and renewal. The generic [module registry](modules.json) supplies
navigation for every city. Existing generic ERP/supervision templates and each
city's `operations/` configuration continue to own deployment-specific settings.

The City selector carries city, environment and asset identity through the shell.
Changing city clears revision, baseline, run and asset context. Railway control
and design views are available only for the workspace passed to
`workbench-server.py --project`; selecting another city does not rebind its
controller. Any catalogue city can use delivery generation and its own operating
bundle. Missing ERP, engineering or supervision packages are shown as unavailable.
ERP project-linked lists use city filters where supported; **City execution** opens
the exact linked ERP project and its **OpenSourceRail → Operating components** actions.
Native FUXA offers its own city/display selector.

Business and maintenance-case links open inside the shell. ERP Project and Issue
**Connected lifecycle** buttons return to it. A linked condition Issue also offers
**Prepare repair**: a native ERP review of Asset, parts/availability, technician and
expected downtime followed by a draft Asset Repair. Its completion remains separate
from the Workbench's railway inspection and handback evidence. Direct tool links remain available
for a separate window. URL context includes an optional `environment` for
simulation/physical asset inspection, independent of railway control mode.

### Authentication and supervisory actions

ERPNext and FUXA keep their native accounts, sessions and permissions. This is a
shared interface, not single sign-on. The ERP image permits framing only by itself
and the named local Workbench origins in
[configure-nginx.py](../../deployment/erpnext/configure-nginx.py). Websocket origin
checks remain enabled. For another deployment, configure `OSR_ERP_URL` and
`OSR_FUXA_URL` and explicitly allow its Workbench origin at the service; cross-site
cookie policies may require a same-site HTTPS deployment.

Connected assets exposes alarm acknowledgement and commands declared by the
asset package. Enter an independently provisioned, scoped integration credential
in **Operator actions**; it stays in page memory and is cleared when leaving.
The gateway enforces identity, city, environment, role, command bounds, lifetime
and controller ownership. The current pilot permits simulated station lighting
only. Requested, accepted, completed, rejected and failed states remain visible
in command history. A transport error requires checking that history before
retrying. Workbench view roles do not grant these permissions.

FreeCAD, Bonsai and QGIS remain desktop editors. The overview exposes versioned,
hash-checked engineering downloads; their [selection bridge](../../tools/integration/desktop_bridge.py)
now opens the selected asset inside the Workbench. Browser execution of those
desktop applications and physical control deployment are not provided here.

### Verification

Browser tests cover city isolation, embedded links, stale telemetry, command
credential handling and the existing design → simulation → OCC → works workflow.
`test_workbench_actions.py` verifies explicit credentials, same-origin mutation
requests, allowlisted endpoints and preservation of gateway denials.
The installed-stack check
[verify-native.mjs](../../deployment/workbench/tests/verify-native.mjs) signs in
through native ERP/FUXA forms, follows an ERP project back to its asset, and
checks a simulation lighting request through controller completion. It requires
the local pilot services and private credentials and intentionally changes simulated
station lighting to 60% and restores it to 75%; it performs no physical command.
The `integrated-stack` CI workflow now creates those services from a clean
checkout, runs this check with the ERP transaction, embedded-condition and FUXA
checks, verifies outage recovery, and destroys the disposable data volumes.

## City-aware navigation and deployment inventory

The overview now includes searchable connected equipment, observation timestamps
and an explicit inventory refresh. It distinguishes local profile files, prepared
engineering/supervision packages, ERP feedback and actual telemetry. Prepared
packages do not establish imported FUXA configuration or physical connectivity.

Native **Projects & automations** opens the uniquely linked city project.
Tasks, procurement, receipts, manufacturing, stock, cases and invoices use native
Project filters. These filters apply to the document's project field; allocations
made only on child lines remain visible in **City execution** actuals. Quality,
maintenance and HR retain their organisation-wide native scope. Missing or
ambiguous feedback prevents a city-filtered workflow from silently opening an
unrelated project's records. Native permissions still apply to every record.

FUXA navigation requests the generated view for the chosen city, environment and
site, preferring the selected asset's site. Verify its displayed city/site name:
FUXA may fall back to its default if the prepared view has not been imported.
Before import, `preview-fuxa` lists the exact package checksums and all device/view
additions, replacements and removals; `import-fuxa` rejects a stale review.
The installed-stack check verifies actual Samawah/Mosul display switching, ERP
project filtering and a simulation analysis evidence record in addition to its
supervisory command check.

## Independent example deployments

The [Samawah acceptance setup](../../deployment/example-city/README.md) runs its own
ERP, FUXA, gateway, controller and Workbench without sharing operating records.
Workbench accepts these operator-defined environment variables:

| Variable | Purpose |
|---|---|
| `OSR_ERP_URL`, `OSR_FUXA_URL` | Native application origins |
| `OSR_INTEGRATION_URL` | Gateway origin for scoped reads and explicit operator requests |
| `OSR_SUPERVISION_CONFIG` | Private integration credential file |
| `OSR_SUPERVISION_ROOT` | Prepared city packages and engineering manifests |
| `OSR_SUPERVISION_PROFILES` | Directory of per-city JSON project/company/preferred-site profiles |
| `OSR_ERP_SNAPSHOT` | Private ERP operating feedback file |

Defaults continue to use the regular local installation. ERP's site configuration
`osr_workbench_origins` controls trusted parent navigation; the frontend's
`frame-ancestors` policy must allow the same origins. The example setup configures
both for port 8190. The simulator accepts matching `--config`, `--controls` and
`--url` arguments, and follows the accepted city's `historian.sampling_seconds`.
