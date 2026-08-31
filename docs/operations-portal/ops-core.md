# OSR Ops Core

OSR Ops Core is the lightweight operating layer for the portal. It keeps
the generated asset register, manufacturing schedule, QA gates, and
maintenance schedule as the source of truth, then adds only the records
needed to run a real railway day without copying a full enterprise EAM
system.

## Operating Loop

1. Generate due work from the city maintenance schedule.
2. Open extra work orders from any manufacturing row, maintenance row,
   QA gate, or manual finding.
3. Move work through `open`, `assigned`, `in_progress`,
   `ready_to_close`, `hold`, and `closed`.
4. Record inspection evidence against the selected work order.
5. Put failed work on hold and raise a defect / NCR.
6. Have a different authenticated verifier approve or reject handback.
7. Resolve defects, close approved work, and export the evidence trail.

## Core Records

| Record | Required fields | Purpose |
|---|---|---|
| Asset | asset id, type, name, line/location | Stable reference for every train, station, track section, switch, energy site, system node, depot, and tool group. |
| Work order | id, source row, asset id, owner, due date, priority, status | Turns a planned manufacturing row, maintenance row, or QA gate into accountable work. |
| Inspection | work order id, result, reading/reference, managed photos/files, authenticated inspector, timestamp and server attestation | Captures proof that work was done and whether it passed. |
| Handback approval | work order, latest passing inspection, decision, authenticated approver, declaration, timestamp and server attestation | Requires an identity-distinct decision before closeout. |
| Defect / NCR | defect id, work order id, asset id, severity, finding, owner, due date, status | Tracks failures until resolved or formally waived. |
| Controlled document | document id, revision, status, superseded record, file SHA-256 and controller attestation | Keeps evidence and drawing revisions append-only and traceable. |
| Audit event | timestamp, action, reference, detail and server attestation | Keeps the operating history exportable, reviewable and tamper-evident. |

## Included

- Asset-specific work orders for trains, waypoints/W-SBCs, stations,
  track, switches, energy, signalling/comms, depots, and
  production-plant tooling.
- One-click conversion from generated manufacturing tasks, maintenance
  tasks, and QA gates.
- Manufacturing work orders carry BOM/material counts, QA action ids,
  verification ids, predecessor ids, and release evidence requirements.
- Manufacturing successor work is blocked until predecessor work orders
  are closed with pass evidence.
- Manufacturing closeout is blocked until the work order has pass
  evidence.
- Daily, weekly, or full-schedule work generation.
- Pass/watch/fail inspection evidence.
- Automatic hold plus defect/NCR creation on failed evidence.
- Password-authenticated, city-scoped RBAC for planner, maintainer, inspector,
  approver, document-controller, auditor and administrator roles.
- Identity-based handback segregation; the authenticated inspector cannot
  approve their own inspection, and open NCRs block closeout server-side.
- Managed content-addressed uploads, append-only document revisions and
  HMAC-SHA256 server attestations for inspections, approvals, documents and
  audit events.
- Online SQLite snapshots plus checksummed evidence backup archives.
- CSV export for work orders, defects, and audit events.
- SQLite storage through `tools/automation/ops-core-server.py` for a simple
  owner-operator deployment.
- Browser-local storage fallback when the portal is served as static
  files only.

## Not Included

- Heavy procurement, finance, HR, or ERP workflows.
- Large CDE workflows with RFIs, submittals and formal transmittals.
- Multi-party contract administration.
- Predictive analytics beyond schedule and condition-trigger placeholders.
- Enterprise organisation hierarchies, OIDC/SSO or MFA.
- Qualified electronic signatures. Server HMAC attestations prove integrity
  within the deployment; they are not a legal trust service.

These can be added later, but the first operating release should stay
small enough that a city railway team can understand it, modify it, and
run it from the same open data that generates the railway design.

## Storage

SQLite is the preferred store for real operation because it gives the
portal a durable file that can be backed up, copied to another console,
or inspected with normal SQLite tools. The default database is:

```text
var/ops-core.sqlite3
```

The browser still receives the same simple JSON state:

```text
workOrders + inspections + approvals + defects + documents + audit + counters
```

That keeps the UI easy to understand while allowing the server to keep
indexed SQLite tables for work orders, defects, inspection evidence,
controlled documents, evidence-file metadata and audit events.

The server creates `var/ops-core.sqlite3` and its tables automatically if
they do not exist. If a browser has local fallback records from earlier
static use, the Ops Core tab's **Storage Reconciliation** panel compares
local records with SQLite records and can merge local-only records into
SQLite.
