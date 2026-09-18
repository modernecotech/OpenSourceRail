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

## Scope still open

- CI at `1d6663c6fbf2` completed all 41 declared Kani harnesses: **32 passed,
  nine timed out**. This confirmed both unregistered-train fixture fixes
  (`E2.1a`, `E2.2a`) in the previous change. The two additional ATP properties
  above passed locally against the new arithmetic, leaving **seven previously
  timed-out properties unresolved**: interlocking non-overlap and determinism,
  ATP determinism, and odometry determinism, forward non-regression, uncertainty
  monotonicity and GNSS conservatism. A bulk topology-construction experiment
  still timed out after 300 seconds and was discarded. Exact-candidate CI,
  consensus refinement and independent acceptance remain open.
- Ops Core and the earlier ERP fresh-volume rehearsals do not establish a single
  coordinated recovery of ERP, gateway queues, FUXA, Ops Core, files and keys.
  Recovery objectives, rollback reconciliation and production identity remain open.
- Full CAD dependency discovery, quantities, solver reruns, production consequences
  and superseded formal evidence still need one complete controlled change scenario.
- Canonical promotion still requires regenerate → validate → review → publish,
  per-line service, peak headways, passenger/capacity measures and accepted operating
  evidence. The nominal generated-city catalogue does not close these gates.
- Supplier freezes, inspected articles, measured mass, calibrated analyses, physical
  transports/HIL, construction-stage civil/station checks and independently accepted
  vehicle/site packages require their own evidence and responsible reviewers.
- Commercial reconciliation of exclusions, supplier quotes, commitments and actuals,
  plus named owner/builder/operator appointments and competence, remains open.

The coverage register now has **518 entries**: 36 scenario, 64 varied, 135 partial
and 283 gaps. The two new GET routes and batch POST route have regression/HTTP tests but retain gaps in
the complete-city scenario register until qualifying scenario evidence is mapped.
Existing programme gaps are not marked complete by these software fixes.
