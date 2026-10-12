# Operations Management: Planning, Field Work And Exchange

This implements the six functions identified in the commercial/open-source
review. The code runs in the existing authenticated integration gateway and is
available through **Workbench → Service & field work**. Its outputs are management
plans and execution evidence; railway command, work-start permission, inspection
and handback remain with their existing authorities.

| Review item | Implemented behaviour | Important scope |
|---|---|---|
| 1. Network/resources/possessions | Explicit directed physical edges and paths; track, platform, junction, depot and charger capacities; occupation/headway sweeps; time-bounded possessions; departure and path choices | A passenger interchange does not create a physical crossover. Resources and route connectivity must be supplied and reviewed. |
| 2. Fleet and coordinated recovery | Revenue and positioning/deadhead legs, charger reservations and energy reserves, fixed inspection/maintenance windows and deadlines; combined track/train/charger/staff recovery | Bounded service/train search uses a declared positioning and charging policy. It reports exhaustion and does not claim unrestricted global fleet optimality. |
| 3. Staff roster optimisation | Weighted coverage, previous-assignment preference and workload balancing; explicit OCC, station, maintenance, depot, cleaning, emergency and optional driver roles; competence expiry/revocation, availability, travel, rest, duty-hour/shift-span and break limits | GoA4 services do not invent a driver duty. Results are proposed rosters; native employment, permissions and execution gates still apply. |
| 4. Offline field execution | Assigned, expiring work packs; embedded instructions and typed/unit-qualified readings; hashed PNG/JPEG photos; lookup QR/asset filtering; persistent IndexedDB queue and offline shell; idempotent gateway/ERP delivery | Reconnection checks planning/engineering revision, installed serial, assignment and revocation. Native ERP re-resolves Task, Employee, method and allocation state; receipts await independent inspection. |
| 5. Reliability and RUL | Controlled fault codes; kilometre/cycle exposure and approved resets; failure cohorts, MDBF/MTTR and period trends; linear degradation estimates, residual sensitivity and held-out validation | Missing exposure produces unknown MDBF. No failures produces observed failure-free exposure, not infinity. A forecast needs matching units/family and separately held-out assets; false-alert, missed-failure, error and lead-time gates precede maintenance-review recommendations. |
| 6. Operational exchange | Source-bound operational JSON import/export with topology, possessions, timetables, fleet and roster; GTFS timetable import/export; binary GTFS-Realtime trip updates/cancellations; configured reversible country/operator identity adapters | Imported passenger timetables require physical path mapping. Changed stop patterns require a reviewed replacement static feed. The existing railML geometry subset remains limited; this is not full railML timetable/signalling conformance. |

## Reproduce The Pilot

The [package](fixtures/pilot.json) is an explicitly **synthetic simulation
fixture**, not surveyed Samawah infrastructure, real staff or commissioned assets.
The [combined disruption](fixtures/disruptions.json) closes the direct track,
removes T2 and W1, and disables the first destination charger. The revised plan
retains all three services, uses the connected alternative route and backup
charger, and assigns replacement staff. Inspection remains in the fleet diagram.

```bash
python3 -m pip install -r engineering/operations/test-requirements.txt
python3 tools/automation/operations-pilot.py --check
python3 tools/automation/operations-pilot.py
python3 -m pytest -q tools/automation/tests/test_operations_management.py tools/automation/tests/test_field_operations_native.py
node deployment/workbench/tests/verify-operations.mjs
```

The CLI writes normal/recovery plans, operational JSON, GTFS ZIP and trip-update
protobuf to `build/operations-pilot/`. The browser test starts its own gateway and
Workbench on separate ports, downloads a revised feed, records readings/photo
offline, reloads offline, then reconnects the durable queue. Its report explicitly
records that **native ERP delivery is not exercised** by that isolated browser test.
Python intake tests exercise native orchestration with controlled record doubles;
a real operator/site must verify the provisioned native workflow after migration.

For an isolated interactive workspace:

```bash
python3 tools/automation/operations-pilot.py --serve
```

Open <http://127.0.0.1:8197/docs/operating/operations/> and use the appropriate
role credential from the private `build/operations-pilot/credentials.json` file.
This workspace uses its own SQLite database and does not alter an installed city
stack. Its work pack is test evidence; no ERP worker runs in this isolated server.

## Controlled Inputs And API

The [contracts](../../services/integration/osr_integration/operations/contracts.py)
validate `osr-operations/1`. All intervals are integer seconds relative to a
**timezone-qualified epoch**, with a declared horizon of at most 14 days. The
bounded contract permits up to 80 service requests, 100 trains and 200 workers;
search has an explicit node budget of at most 100,000. These are bounded planning
limits, not a demonstrated production scale or solve-time commitment.

Supply known nodes/coordinates and directed edges with durations, energy and
physical resource IDs; connected path alternatives; service/departure choices;
train location, charge/reserve, route compatibility and maintenance deadline;
chargers and fixed fleet jobs; assessed staff competencies, validity windows and
local rest/travel/break policies. An inspection can explicitly extend the declared
maintenance deadline. The input is an engineering snapshot, not a live permit.

The gateway endpoints are `/operations/<action>`; Workbench forwards the same
allowlist at `/api/operations/<action>`. Every request requires an explicit bearer
credential and authorised city/environment. Browser writes also require the
Workbench origin. View-role selectors do not grant credentials or authority.

| Method / action | Caller / result |
|---|---|
| GET `baseline`, `plan`, `export` | Scoped reads; exports reject stale plans |
| POST `baseline` | Engineer; validated package and compare-and-swap `expected` hash |
| POST `plan` | Engineer/operator/maintainer; expected baseline plus optional possessions/unavailable trains/workers |
| POST `work`, `revoke` | Engineer; issue or revoke a reviewed work pack |
| GET `work`, `field-events` | Technician sees their own records; engineer/operator sees scoped records |
| POST `complete` | Assigned maintainer; typed event queues native evidence exactly once |
| POST `analytics`, `calibrate`, `forecast` | Scoped management analysis; source hashes and validation outcomes retained in gateway audit |
| POST `import`, `import-gtfs` | Engineer; review-only import without changing the baseline |
| POST `operator-exchange` | Provisioned, accepted adapter; unknown or ambiguous mappings rejected |

A work-pack issue supplies `id`, city/environment, `asset_id`, `assigned_to`,
`method_revision`, `erp_task`, `erp_asset`, current `native_modified`, `expires_at`,
`requires_photo`, and reading definitions. Each reading names a kind and required
flag; numeric readings also name exact units and finite bounds. `instructions`
can carry issued plain-text method instructions for offline use. Server-controlled
baseline/revision/serial/hash fields are added at issue, not accepted from callers.
A lookup QR is `osr://asset?city=<city>&environment=<environment>&id=<asset-id>`;
it selects an existing assigned work pack and establishes no new physical binding.

Offline completion status is always `performed-awaiting-inspection`. A 409 conflict
retains device evidence for review; it never overwrites a newer work pack. The ERP
outbox retries transport/server failures; permission, scope and revision rejection
is terminal and requires refreshed work. Lost replies return the original receipt.

## Native ERP And Operator Configuration

Normal app install/migration creates the immutable **OSR Field Execution** DocType.
The adapter [intake](../../deployment/erpnext/apps/osr_erpnext/osr_erpnext/field_operations.py)
uses the existing private `osr_integration_users` scope policy and native document
permissions. An administrator must provision `osr_field_technicians`, mapping each
gateway subject to its actual native `user` and `employee`. The user must have an
open native ToDo assignment to the already **Working** Task. Task/asset/method and
engineering revision, employee/company, serial and current allocation gates must
match. Intake stores private photo attachments and an immutable receipt without
completing/submitting the Task or granting railway handback. Generic Desk/REST
writes cannot forge or alter an intake receipt.

Gateway configuration may contain `operations_adapters`, keyed by adapter ID.
Each `osr-operator-adapter/1` profile names country, operator, revision, accepted
review record, authorised cities/environments and a one-to-one `identities` map.
There are no fabricated PKP PLK, ARTC or other national-system endpoints. A real
transport/schema adapter and national/operator acceptance remain deployment work.

A predictive-model study supplies measured/synthetic provenance in its own
controlled input records, rising-degradation units/family, threshold, warning
horizon and error/false-alert/lead-time limits. Training and held-out asset IDs
must be disjoint; observed non-failure cohorts must cover the warning horizon.
Validation can fail or return insufficient data. Even a passing research model
is marked uncommissioned and cannot automatically issue a maintenance order.
The residual sensitivity band is not a calibrated statistical confidence interval.

## Evidence And Remaining Deployment Work

The [source-bound pilot review](pilot-review.json) retains the actual combined
recovery checks and hashes; regenerate it with `operations-pilot.py --review`.
Code and negative tests cover all six management functions. The fixture is a
software demonstration. Real topology/resources, calibrated running times and
energy, approved labour policies, operator master data, issued methods/permits,
measured condition histories, native-site acceptance, support and security
configuration remain deployment inputs. The [first adoptable product](../../docs/first-adoptable-product.md)
and [existing operating acceptance](../../docs/operating/integration-status.md)
retain their separate commissioning and railway-authority boundaries.

The passenger formats follow the primary [GTFS schedule](https://gtfs.org/documentation/schedule/reference/)
and [GTFS-Realtime](https://gtfs.org/documentation/realtime/reference/) references;
protobuf output is independently decoded with the official
[MobilityData bindings](https://github.com/MobilityData/gtfs-realtime-bindings).
Full [railML timetable exchange](https://www.railml.org/en/subschemas/timetable)
remains a distinct extension rather than an implied capability of OSR's existing
geometry export.
