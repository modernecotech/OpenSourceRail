# Gateway scaling, backup integrity and evidence follow-through

This implements the first software fixes from the broader review of `a99af132`.
It does not close the entire programme or the remaining formal, engineering,
capacity and deployment gates. [Verification and acceptance status](status/index.html)
keeps recorded commits, test scopes, maturity and canonical gates together and is
available through Workbench's **Verification & gates** module.

## Findings and changes

| Finding | Implemented correction | Verification and limit |
|---|---|---|
| One FUXA device read loaded the entire city and history | Dedicated active-device read with three SELECTs; one indexed statement retrieves latest measurements. Whole-city snapshots use nine SELECTs regardless of equipment count. | Regression enforces query budgets and preserves values, quality, timestamps, active configuration and city/environment boundaries. This is query scaling, not production capacity acceptance. |
| Other-city traffic hid pending ERP deliveries | Persistent city/environment/asset scope, forward migration from existing event payloads, filtering before LIMIT, pending/total counts and cursor pagination. | More than 100 newer other-city events no longer hide the original city's queue. Tests cover migration, pagination, pending state and forbidden HTTP scopes. Delivery retry ordering remains unchanged. |
| Ops Core accepted an unchecked invalid database | Strict manifest schema and membership, mandatory checksummed database, unique safe paths, content checksums, SQLite header/integrity/foreign-key checks and application evidence-file checks. | Original exploit fails. Negative tests cover missing, duplicate, extra, corrupt and unsafe entries. Fresh-directory restore retains application records and rebases evidence paths; it cannot overwrite a deployment. |
| Unbounded lifecycle evidence response | Snapshot contains the latest 20 records per asset, with totals and an older-record cursor. Authenticated pages and UI controls retrieve earlier evidence. | Tests traverse all 45 fixture records without duplication or cross-city access. Existing records remain stored. |
| Broader Kani artifacts absent from release pack | Export and validate every declared harness's manifest, TOML result and log, bound to the exact commit, workflow run and current dependency hashes. | Missing, stale, duplicated, failed and altered results are rejected. The archive preserves original report paths and bytes. No independent acceptance is inferred. |
| Fragmented status presentation | Generated status page in Workbench combines historical CI, generated catalogue results, integration coverage, canonical gates and analysis maturity. | Each CI result retains its commit and source link. Generated candidates never become accepted canonical deployments by aggregation. |

## Executed load rehearsal

The reusable command creates an isolated gateway database and real local HTTP
servers using the production handlers. It interleaves telemetry writes, FUXA tag
adapter polls and multiple operator snapshot/queue reads:

```sh
tools/automation/osr-python tools/automation/supervision-load.py \
  --city samawah --rounds 3 --workers 16 --operators 4 \
  --output build/supervision-load/samawah
```

The output directory must be new. The package, source hashes, timings, request
errors, received sample count and latest effective values are retained in its
report. The command exits unsuccessfully on functional failure. The separate
`polling_target_met` field records whether complete cycles met two seconds;
`functional_passed` alone does not establish that capacity.

The initial review run covered **573 equipment positions and 1,610 measurements**,
with **4,830 telemetry writes, 1,719 FUXA-adapter polls and 24 operator reads**.
All requests completed, all expected samples were retained, changed final values
matched, and SQLite integrity passed. Device reads had approximately **8 ms p95**
response time, while complete cycles took **3.94–4.38 seconds**. The two-second
cycle target was **not met**. These local results include host contention and are
not a controlled production sizing benchmark.

This runs the FUXA polling API, not hundreds of FUXA browser sessions or concurrent
ERP posting. Sustained load, longer historian retention, real controllers, ERP
transactions and coordinated production sizing remain required. Do not lower the
acceptance target or relabel this result as production-ready.

## Bounded telemetry batches and measured follow-through

Gateway image `osr/integration:0.1.2` adds authenticated
`POST /telemetry/batch` with body `{"readings": [<telemetry message>, ...]}`.
A batch contains **1–128** readings and uses the existing 4 MB request bound.
Every member is authorized against the controller's city/environment and source
binding. Readings run in order in one transaction, with the same sequence,
timestamp, units, quality, commissioning and alarm checks as `/telemetry`.
A rejected member rolls back all new readings, alarm changes, audit and delivery
events. A retry must preserve each original message, including its timestamp and
sequence; identical messages return `duplicate: true` without repeating effects.
Response `results` entries correspond to the input order. Clients divide larger
sets into batches; atomicity applies to each batch, not a whole sampling cycle.

The native Rust supervisory simulator now publishes these bounded batches.
Telemetry writers queue within the process before taking SQLite's write lock.
Device/snapshot transactions also run one at a time to avoid short concurrent
cursors competing for the Python interpreter; writers use a separate lock and
SQLite retains cross-process isolation. Each view reads current database state.
There is no response cache, added freshness interval or changed quality rule.
The deployed HTTP server and load runner now share the same 128-connection
listener backlog.

The follow-through rehearsal exercised the same **573 positions, 1,610
measurements, 16 clients and four operators** over five cycles. All **8,050
readings**, **2,865 device polls** and **40 operator reads** completed correctly.
Cycles took **1.43–1.76 seconds**; the two-second target passed on this host.
Device-read p95 was **49 ms**, snapshot p95 **458 ms**, and batch-write p95
**66 ms**. These are bounded local observations, not production sizing or
concurrent native ERP/FUXA browser acceptance.

A second city run covered **Mosul: 1,422 positions and 4,009 measurements**.
All **12,027 readings** across three cycles were retained and final values matched,
but cycles took **4.49–4.63 seconds**, missing the same two-second target. It ran
on the shared development host during other verification work. This establishes
functional reuse of the runner, not sufficient capacity for the larger city;
controlled sizing, partitioning and native multi-operator load remain open.

The command defaults to batches of 128. Use `--batch-size 1` for the original
single-reading comparison, and `--require-polling-target` to fail if any cycle
exceeds two seconds. CI retains source-bound load reports and fails on functional
errors; hosted-runner timings remain observations rather than a capacity approval.
Both local pilots were upgraded with private consistent gateway backups and
preserved asset configurations.

ATP envelope square root now uses 32 division-free radix-four steps while
retaining floor rounding. Boundary checks, 10,000 generated full-width `u64`
comparisons against Rust's standard implementation, and all ATP tests pass.
Targeted controlled Kani runs passed severe overspeed (`E4.1f`, 140.1 seconds)
and conservative speed uncertainty (`E4.1g`, 96.5 seconds). Their symbolic input
ranges and assertions are unchanged; unwind increases to 33 to cover all 32
steps and the loop exit. Local proof reports remain unattested and do not replace
exact-commit CI or independent review of the safety-path arithmetic change.

## Optional site polling and current capacity evidence

Gateway `osr/integration:0.1.3` supports `fuxa_polling_scope: "site"` in city
configuration, while the shared default stays `"asset"`. Site polling combines
transport requests within one city/environment/site. Equipment measurement and
alarm tag identities, timestamps, quality and asset links remain separate.
Package changes and whole-project FUXA imports still require hash-bound reviews.
See the [configuration guide](../../deployment/supervision/README.md).

```sh
tools/automation/osr-python tools/automation/supervision-load.py \
  --city mosul --rounds 5 --workers 16 --operators 4 \
  --polling-scope site --output build/supervision-load/mosul-site
```

The runner now starts the gateway in a separate process, matching the deployed
client/server separation; `--in-process` retains the earlier benchmark layout.
It polls actual generated FUXA URLs and checks final tag values and quality
against persisted readings. Reports retain the exported project hash and source
hashes. Comparing these results directly with the earlier shared-interpreter
numbers would combine a benchmark change with the transport improvement.

With the same separate-process layout, the Mosul asset-polling control took
**2.17–2.64 seconds** per cycle. Site polling reduces 1,422 requests to **375**
without removing any of the 4,009 measurements. An earlier five-cycle run took
1.24–1.77 seconds, but the final source-bound run took **1.50–2.24 seconds**:
all 20,045 samples were retained and final FUXA values matched, while **the
two-second target was not met consistently**. These shared-host observations
support the transport change, not production capacity acceptance. Retained
reports: [asset control](status/rehearsals/mosul-asset-control.json) and
[site polling](status/rehearsals/mosul-site.json).

The example-city scenario uses Mosul site polling and Samawah asset polling.
The native browser check compares Mosul's rendered power with current gateway
telemetry, as well as checking city switching and the existing lifecycle handoff.
All ten checks in the [local native browser journey](status/rehearsals/native-ui.json)
passed, and the automation suite passed 340 tests plus 12 subtests. These ran on
the recorded dirty working tree; they do not replace clean-candidate CI.
Full-city native FUXA/ERP/operator concurrency remains a separate acceptance task.

## Scope still open

- CI at `e9e4ff5cf287` completed all 41 declared Kani harnesses: **34 passed,
  seven timed out**. Both ATP follow-through properties now pass in CI. The
  unresolved properties are interlocking non-overlap and determinism, ATP
  determinism, and odometry determinism, forward non-regression, uncertainty
  monotonicity and GNSS conservatism. Exact-candidate CI, consensus refinement
  and independent acceptance remain open.
- Coordinated cold data recovery now passes the checks described in the
  [recovery guide](platform-recovery.md). Production cutover, resuming jobs and
  controllers, recovery objectives and production identity migration remain open.
- The [controlled cross-bearer workflow](../../engineering/changes/README.md) now
  executes native CAD, quantities, solver reruns, nested BOM revisions, production
  stop and revised manufacturing, retaining superseded screening evidence.
  Full dependency discovery, formal impact assessment and independently accepted
  engineering changes remain open.
- Canonical promotion still requires regenerate → validate → review → publish,
  per-line service, peak headways, passenger/capacity measures and accepted operating
  evidence. The nominal generated-city catalogue does not close these gates.
  `validate-city-service.py` gates full-window and degraded mileage separately for every
  line, and the catalogue collector rejects missing or failed per-line evidence.
  The retained [Samawah generated candidate](status/rehearsals/samawah-per-line/validation.json)
  passes nominal line screens at 90.86%, 103.87% and 103.87% of scheduled mileage.
  Its configured peak ceiling is 7,200 passengers/hour/direction; observed peak
  departures, calibrated demand and crowding remain open. These results do not
  promote the candidate or validate every service window.
  The existing `validate-city-simulation.py` reports retain their original
  aggregate software scope. The batch runner now uses the stricter qualification
  adapter, which reuses that suite and its native per-line observations; an older
  aggregate pass cannot satisfy the new catalogue collector.
  The [canonical Samawah qualification](status/rehearsals/samawah-service-qualification.json)
  fails four degraded cases: line 1 delivers 87.26% under maximum climate load,
  87.54% with combined ageing/heat, 88.77% during the single-pad outage and 88.34%
  with consecutive missed charging stops. Each is below the 89.8% threshold
  including numerical tolerance, despite the aggregate software screen passing.
  These failures remain open; no acceptance threshold or canonical design was changed.
  A [35% adaptive-service trigger candidate](status/rehearsals/samawah-trigger-35/qualification.json)
  changes only `normal_service_soc` from 0.40 to 0.35 in the retained design and
  scenario. It preserves the 20% reserve floor and improves line 1's single-pad
  case from 88.77% to 90.01%, but the heat, combined ageing/heat and missed-stop
  cases still fail. All-site outage delivery falls from 78.27% to 74.55% on that
  line (above its separate 60% emergency floor). The candidate is **not promoted**.
  This comparison demonstrates effective settings changes and their trade-offs.
  [Mosul's stricter qualification](status/rehearsals/mosul-service-qualification.json)
  passes all six nominal lines and seven degraded cases. The all-site grid outage
  fails on line 2 at **51.81%**, below its 59.8% emergency threshold including
  tolerance. The five canonical degraded-case failures are visible in Workbench
  → Verification & gates. The canonical configurations remain unchanged.

Reproduce the stricter qualification without overwriting legacy aggregate evidence:

```sh
tools/automation/osr-python tools/automation/validate-city-service.py \
  --scenario cities/catalogue/west-asia/Iraq/Samawah/samawah.toml \
  --resilience --full-only --output build/samawah-service-qualification.json
# A failing line returns nonzero and retains the complete diagnostic report.
```

Remaining package and programme gates:

- Supplier freezes, inspected articles, measured mass, calibrated analyses, physical
  transports/HIL, construction-stage civil/station checks and independently accepted
  vehicle/site packages require their own evidence and responsible reviewers.
- Commercial reconciliation of exclusions, supplier quotes, commitments and actuals,
  plus named owner/builder/operator appointments and competence, remains open.

The coverage register now has **519 entries**: 36 scenario, 64 varied, 135 partial
and 284 gaps. The two new GET routes and batch POST route have regression/HTTP tests but retain gaps in
the complete-city scenario register until qualifying scenario evidence is mapped.
Existing programme gaps are not marked complete by these software fixes.
