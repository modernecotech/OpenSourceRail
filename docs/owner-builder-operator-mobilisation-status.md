# Owner–Builder–Operator Mobilisation Status

> Status: **unfilled template — not legal, spending, construction, safety or operating authority**.

Project: `unassigned template`

Entity model complete: **no** · Roles ready: **0/13** · Independent parties ready: **0/3** · Work packages complete: **0/18** · Gates accepted: **0/8**

This template organises mobilisation evidence. It does not create a legal entity, delegate a statutory duty, appoint a competent person, approve expenditure, release construction, certify safety or authorise railway operation.

## Accountable Roles

| ID | Role | Appointment | Competence | Ready |
|---|---|---|---|---|
| `ROLE-OWNER` | owner accountable officer | open | open | no |
| `ROLE-CEO` | chief executive | open | open | no |
| `ROLE-PROGRAMME` | programme director | open | open | no |
| `ROLE-ENGINEERING` | chief engineer and design authority | open | open | no |
| `ROLE-SAFETY` | safety and assurance director | open | open | no |
| `ROLE-OPERATIONS` | operations director | open | open | no |
| `ROLE-ASSET` | asset and maintenance director | open | open | no |
| `ROLE-MANUFACTURING` | manufacturing director | open | open | no |
| `ROLE-INFRASTRUCTURE` | infrastructure director | open | open | no |
| `ROLE-COMMERCIAL` | commercial and local-content director | open | open | no |
| `ROLE-FINANCE` | finance director | open | open | no |
| `ROLE-PEOPLE` | people and competence director | open | open | no |
| `ROLE-DIGITAL` | digital and configuration director | open | open | no |

## Independent Parties

| ID | Party | Organisation / appointment | Ready |
|---|---|---|---|
| `IND-ASSESSOR` | independent safety assessor | open | no |
| `IND-CHECKER` | independent design checker | open | no |
| `IND-AUDITOR` | external auditor | open | no |

## Mobilisation Gates

| Gate | Window | Accountable roles | Evidence | Decision | Accepted |
|---|---|---|---:|---|---|
| `G0` — public mandate | month 0-3 | `ROLE-OWNER` | 0/5 | `open` | no |
| `G1` — entity and controls | month 2-6 | `ROLE-OWNER`, `ROLE-CEO`, `ROLE-FINANCE` | 0/5 | `open` | no |
| `G2` — development baseline | month 4-12 | `ROLE-PROGRAMME`, `ROLE-ENGINEERING`, `ROLE-OPERATIONS`, `ROLE-SAFETY` | 0/5 | `open` | no |
| `G3` — procure and prototype | month 9-18 | `ROLE-PROGRAMME`, `ROLE-COMMERCIAL`, `ROLE-MANUFACTURING`, `ROLE-INFRASTRUCTURE` | 0/5 | `open` | no |
| `G4` — first articles and enabling works | month 15-30 | `ROLE-MANUFACTURING`, `ROLE-INFRASTRUCTURE`, `ROLE-ENGINEERING`, `ROLE-SAFETY` | 0/5 | `open` | no |
| `G5` — construction and operational readiness | programme-derived | `ROLE-PROGRAMME`, `ROLE-OPERATIONS`, `ROLE-ASSET`, `ROLE-SAFETY` | 0/5 | `open` | no |
| `G6` — trial and revenue service | authority-derived | `ROLE-OWNER`, `ROLE-OPERATIONS`, `ROLE-SAFETY` | 0/5 | `open` | no |
| `G7` — stable operation and replication | first 12-24 service months | `ROLE-CEO`, `ROLE-OPERATIONS`, `ROLE-ASSET`, `ROLE-FINANCE` | 0/5 | `open` | no |

## Default Mobilisation Work Programme

Planning horizon: month **0–60**. Overlap is intentional; local approvals, procurement and construction determine the actual baseline.

| Work package | Months | Planning FTE | Accountable | Depends on | Gate | Evidence | Status |
|---|---:|---:|---|---|---|---:|---|
| `MOB-010` — secure public mandate and accountable sponsorship | 0–3 | 2–4 | `ROLE-OWNER` | start | `G0` | 0/5 | `not-started` |
| `MOB-020` — establish legal entity and owner-company agreement | 1–6 | 2–5 | `ROLE-OWNER` | `MOB-010` | `G1` | 0/5 | `not-started` |
| `MOB-030` — stand up governance finance audit and procurement controls | 1–6 | 3–6 | `ROLE-FINANCE` | `MOB-010` | `G1` | 0/5 | `not-started` |
| `MOB-040` — recruit and authorise core accountable leadership | 1–9 | 2–5 | `ROLE-CEO` | `MOB-010` | `G2` | 0/5 | `not-started` |
| `MOB-050` — deploy CDE configuration cybersecurity and asset-ID controls | 1–8 | 3–7 | `ROLE-DIGITAL` | `MOB-010` | `G2` | 0/5 | `not-started` |
| `MOB-080` — establish safety assurance security and authorisation strategy | 2–18 | 4–9 | `ROLE-SAFETY` | `MOB-010`, `MOB-040` | `G2` | 0/5 | `not-started` |
| `MOB-090` — develop affordability funding cashflow and benefits baseline | 2–15 | 4–8 | `ROLE-FINANCE` | `MOB-010`, `MOB-030` | `G2` | 0/5 | `not-started` |
| `MOB-060` — freeze concept of operations and development requirements | 3–12 | 8–15 | `ROLE-ENGINEERING` | `MOB-010`, `MOB-040` | `G2` | 0/5 | `not-started` |
| `MOB-070` — complete survey ground utility land and consent evidence plan | 3–15 | 6–12 | `ROLE-INFRASTRUCTURE` | `MOB-010` | `G2` | 0/5 | `not-started` |
| `MOB-120` — build workforce apprenticeship and competence pipeline | 4–30 | 4–10 | `ROLE-PEOPLE` | `MOB-040`, `MOB-060` | `G3` | 0/5 | `not-started` |
| `MOB-100` — package procure and qualify delivery supply chain | 8–18 | 6–12 | `ROLE-COMMERCIAL` | `MOB-060`, `MOB-070`, `MOB-080`, `MOB-090` | `G3` | 0/5 | `not-started` |
| `MOB-110` — mobilise factory depot OCC and civil production facilities | 8–20 | 6–14 | `ROLE-MANUFACTURING` | `MOB-060`, `MOB-070` | `G3` | 0/5 | `not-started` |
| `MOB-130` — execute and accept vehicle and reusable-product first articles | 15–30 | 12–25 | `ROLE-MANUFACTURING` | `MOB-100`, `MOB-110`, `MOB-120` | `G4` | 0/5 | `not-started` |
| `MOB-140` — deliver enabling works and site-specific civil construction | 15–36 | 10–20 | `ROLE-INFRASTRUCTURE` | `MOB-070`, `MOB-100` | `G4` | 0/5 | `not-started` |
| `MOB-150` — build operator and complete operational readiness trials | 18–36 | 10–22 | `ROLE-OPERATIONS` | `MOB-080`, `MOB-110`, `MOB-120` | `G5` | 0/5 | `not-started` |
| `MOB-160` — establish maintenance asset information spares and handover | 18–36 | 8–16 | `ROLE-ASSET` | `MOB-130`, `MOB-140` | `G5` | 0/5 | `not-started` |
| `MOB-170` — obtain trial and revenue-service authorisation | 30–42 | 6–12 | `ROLE-OWNER` | `MOB-130`, `MOB-140`, `MOB-150`, `MOB-160` | `G6` | 0/5 | `not-started` |
| `MOB-180` — stabilise service and release replication baseline | 42–60 | 5–10 | `ROLE-CEO` | `MOB-170` | `G7` | 0/5 | `not-started` |

Use the [setup plan](owner-builder-operator-setup.md) to mobilise the organisation.
Copy [`owner-builder-operator-mobilisation.toml`](../lib/templates/owner-builder-operator-mobilisation.toml)
into a controlled deployment workspace, fill it with evidence references, and retain this repository file as the blank default.
A gate is accepted only when its decision, decision-maker/date and at least one reference for every required evidence item are recorded.
