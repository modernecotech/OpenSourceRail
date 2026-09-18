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

## Scope still open

- Two of the prior 11 Kani timeouts passed in targeted local execution after
  removing unused topology fixtures: unregistered-train fail-restrictive behavior
  (`E2.1a`) and the whole-function unregistered-train validity window (`E2.2a`).
  Both functions return before a network lookup; the known-position and graph
  harnesses retain their fixtures. Each reported about six seconds of verification time; the controlled
  runner completed the full commands in 29.4 and 31.7 seconds. Input ranges, assertions and unwind checks are unchanged. **Nine
  previously timed-out properties remain unresolved**, and a new full CI run is
  still required. Consensus refinement and independent acceptance remain open.
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

The coverage register now has **517 entries**: 36 scenario, 64 varied, 135 partial
and 282 gaps. The two new GET routes have regression/HTTP tests but retain gaps in
the complete-city scenario register until qualifying scenario evidence is mapped.
Existing programme gaps are not marked complete by these software fixes.
