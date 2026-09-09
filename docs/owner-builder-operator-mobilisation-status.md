# Owner–Builder–Operator Mobilisation Status

> Status: **unfilled template — not legal, spending, construction, safety or operating authority**.

Project: `unassigned template`

Entity model complete: **no** · Roles ready: **0/13** · Independent parties ready: **0/3** · Gates accepted: **0/8**

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

Use the [setup plan](owner-builder-operator-setup.md) to mobilise the organisation.
Copy [`owner-builder-operator-mobilisation.toml`](../lib/templates/owner-builder-operator-mobilisation.toml)
into a controlled deployment workspace, fill it with evidence references, and retain this repository file as the blank default.
A gate is accepted only when its decision, decision-maker/date and at least one reference for every required evidence item are recorded.
