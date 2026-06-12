# First Adoptable Product

The first adoptable OpenSourceRail product should be the non-safety
owner-operator stack:

```text
Ops Core + simulator + asset register + QA/maintenance/evidence portal
for an existing depot, workshop, or pilot corridor
```

This can be useful before any train-control software is certified. It
helps an operator organize assets, work orders, manufacturing packages,
QA hold points, maintenance schedules, defects/NCR, and acceptance
evidence while the safety-critical stack remains in simulation or shadow
mode.

## Target User

- A public railway owner evaluating a depot, workshop, or pilot corridor.
- A local workshop preparing rolling-stock or infrastructure packages.
- An operator trying to structure maintenance and QA records.
- A university, assessor, or funder reviewing whether OSR evidence is
  coherent enough for a physical pilot.

## Product Scope

| Included | Not included in the first product |
|---|---|
| SQLite-backed Ops Core work orders | Live movement authority or interlocking control |
| Generated asset register | Certified train-control functions |
| Manufacturing schedule and staff tasks | Full EAM/ERP replacement |
| QA gate register and evidence links | Legal certification or safety approval |
| Maintenance schedule per train, station, track section, waypoint, depot, energy site, and tool | Insurance, finance, or procurement guarantee |
| Defect/NCR and audit trail | Mobile field app with signatures/photos |
| Simulator and scenario outputs | Full telemetry-driven predictive maintenance |
| Acceptance evidence matrix | Regulator submission by itself |

## Deployment Shape

1. Select an existing depot, workshop, yard, or short pilot corridor.
2. Load or generate the asset register.
3. Import the baseline manufacturing, QA, and maintenance schedules.
4. Run the SQLite-backed portal.
5. Create work orders from QA, manufacturing, and maintenance rows.
6. Attach evidence links and close work with pass/fail status.
7. Use defects/NCR and audit records to build an acceptance evidence
   pack.
8. Keep train-control in simulator or shadow mode until the deployment
   safety case is independently assessed.

## Current Implementation

| Capability | Current artifact |
|---|---|
| Browser portal | [`operations-portal/README.md`](operations-portal/README.md) |
| Ops Core model | [`operations-portal/ops-core.md`](operations-portal/ops-core.md) |
| SQLite server | [`../scripts/ops-core-server.py`](../scripts/ops-core-server.py) |
| Generated Samawah data | [`operations-portal/data/`](operations-portal/data/) |
| Acceptance report | [`operations-portal/acceptance-evidence-report.md`](operations-portal/acceptance-evidence-report.md) |
| Gap analysis | [`operations-portal/gap-analysis.md`](operations-portal/gap-analysis.md) |
| Construction QA RFC | [`rfcs/0028-construction-quality-assurance.md`](rfcs/0028-construction-quality-assurance.md) |
| Maintenance schedule RFC | [`rfcs/0029-maintenance-schedule-system.md`](rfcs/0029-maintenance-schedule-system.md) |
| Manufacturing schedule RFC | [`rfcs/0030-manufacturing-schedule-system.md`](rfcs/0030-manufacturing-schedule-system.md) |

Run it:

```bash
python3 scripts/generate-qa-maintenance-data.py
python3 scripts/ops-core-server.py --port 8008
```

Then open:

```text
http://127.0.0.1:8008/docs/operations-portal/
```

## Acceptance Criteria

A credible first deployment should be able to show:

- every asset has a stable id and owner;
- every manufacturing package has material/BOM refs and QA verification;
- QA and maintenance rows can become work orders;
- failed inspections create defects/NCR and audit records;
- predecessor work blocks successor release until pass evidence exists;
- evidence can be exported as CSV/JSON and reviewed outside the portal;
- the system runs without commanding trains.

## Why This Is The Wedge

Rail procurement is not won by software novelty alone. This product gives
operators, funders, and assessors something useful and low-risk to adopt:
better asset, QA, maintenance, and acceptance discipline. It also creates
the evidence trail that any later certified OSR train-control or
rolling-stock deployment will need.
