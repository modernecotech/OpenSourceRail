# Supplier Technical-Support Readiness

> Generated from `lib/templates/supplier-technical-support-readiness.toml`; do not edit this report directly.

> **Authority boundary:** This register prepares a supplier-backed LM3 design-review and first-article package. Public webpages and discussions are screening inputs only. They do not prove an engineering commitment, manufacturer authorization, a compatible product configuration, accepted design responsibility, price, warranty, railway approval or permission to manufacture or operate.

## Current Decision

**Technical-support ready: NO.** The baseline is not frozen, 0/3 catalogue leads are qualified, 0/8 work packages and 0/8 interfaces are accepted, 0/8 cost buckets are accepted, and 0/7 gates have passed.

Public supplier pages are useful discovery inputs. They do not count as a commitment, controlled configuration, manufacturer authorization or LM3 evidence. A controlled opportunity copy must carry confidential offers and acceptance records.

## Baseline

| Field | Value |
|---|---|
| `configuration_id` | LM3-FA-001 |
| `osr_commit` | — |
| `freeze_record_ref` | — |
| `duty_cycle_ref` | — |
| `route_environment_ref` | — |
| `status` | not-frozen |

## Catalogue Leads

| Lead | Published scope | Status | Qualified |
|---|---|---|---|
| `LEAD-RAILMAC-INTEGRATION` — RailMac / SinoMac railway integration offering | Pre-design, product selection, component supply, installation, commissioning and after-sales support across trains, traction, bogies, brakes, components and maintenance equipment | screening-source-only | no |
| `LEAD-CRRC-SPECIAL-EQUIPMENT` — CRRC Special Purpose Equipment tourism-transport offering | Supplier-published rail-mounted sightseeing vehicles and tourism transport systems | screening-source-only | no |
| `LEAD-OPEN-ALTERNATIVES` — Additional qualified suppliers and engineering partners | Open supplier-neutral candidate set for exact components, systems, laboratories and production support | screening-source-only | no |

## Technical Work Packages

| Package | Discipline | Existing OSR inputs | Evidence / required | Accepted |
|---|---|---:|---:|---|
| `TS-WP-01` — Frozen LM3 system review | systems-engineering | 3 | 0 / 5 | no |
| `TS-WP-02` — Bogie, wheelset, suspension and brake configuration | running-gear-and-braking | 4 | 0 / 6 | no |
| `TS-WP-03` — Traction, battery, charging and thermal configuration | traction-energy | 4 | 0 / 6 | no |
| `TS-WP-04` — Manufacturing and design-for-production review | industrialisation | 3 | 0 / 6 | no |
| `TS-WP-05` — First-article construction and evidence | prototype-and-test | 3 | 0 / 6 | no |
| `TS-WP-06` — Local workshop capability and technology transfer | localisation | 3 | 0 / 6 | no |
| `TS-WP-07` — Maintenance, spares and lifecycle support | supportability | 3 | 0 / 6 | no |
| `TS-WP-08` — Cross-supplier system integration and configuration control | integration | 4 | 0 / 6 | no |

## Cross-Supplier Interfaces

| Interface | Work packages | Evidence / fields | Accepted |
|---|---|---:|---|
| `TS-IF-01` — Wheel rail axle load and route geometry | `TS-WP-01`, `TS-WP-02`, `TS-WP-08` | 0 / 5 | no |
| `TS-IF-02` — Bogie carbody articulation and ride | `TS-WP-02`, `TS-WP-04`, `TS-WP-08` | 0 / 5 | no |
| `TS-IF-03` — Brake train control and adhesion | `TS-WP-02`, `TS-WP-08` | 0 / 5 | no |
| `TS-IF-04` — Motor gearbox wheelset and mechanical drive | `TS-WP-02`, `TS-WP-03`, `TS-WP-08` | 0 / 5 | no |
| `TS-IF-05` — Battery converter motor charger and grid | `TS-WP-03`, `TS-WP-08` | 0 / 5 | no |
| `TS-IF-06` — Thermal fire ventilation and environmental exposure | `TS-WP-03`, `TS-WP-04`, `TS-WP-05` | 0 / 5 | no |
| `TS-IF-07` — Vehicle platform structure and evacuation | `TS-WP-01`, `TS-WP-08` | 0 / 5 | no |
| `TS-IF-08` — Diagnostics maintenance ERP and owner data | `TS-WP-06`, `TS-WP-07`, `TS-WP-08` | 0 / 5 | no |

## Separated Cost Statement

| Bucket | Status | Amount | Scoped | Accepted |
|---|---|---:|---|---|
| `COST-NRE` — Non-recurring engineering and design responsibility | unquoted | — | no | no |
| `COST-TOOLING` — Tooling, fixtures, metrology and workshop preparation | unquoted | — | no | no |
| `COST-FIRST-ARTICLE` — First-article material, construction, inspection and testing | unquoted | — | no | no |
| `COST-REPEAT-UNIT` — Repeat-production train at stated quantity and configuration | unquoted | — | no | no |
| `COST-TRAINING-TRANSFER` — Training, documentation and technology-transfer rights | unquoted | — | no | no |
| `COST-SPARES-SUPPORT` — Initial spares, special tools, warranty and continuing support | unquoted | — | no | no |
| `COST-LOGISTICS-TAX` — Packing, logistics, duties, taxes, currency and local delivery | unquoted | — | no | no |
| `COST-ACCEPTANCE` — Independent review, type evidence, homologation and commissioning support | unquoted | — | no | no |

## Decision Gates

| Gate | Decision | Evidence / required | Passed |
|---|---|---:|---|
| `TS0` — Counterparty and technical-access qualification | open | 0 / 4 | no |
| `TS1` — Frozen review baseline and funded scope | open | 0 / 4 | no |
| `TS2` — Controlled component configurations | open | 0 / 4 | no |
| `TS3` — Interface and design-responsibility acceptance | open | 0 / 4 | no |
| `TS4` — First-article authorization | open | 0 / 4 | no |
| `TS5` — Local capability and lifecycle acceptance | open | 0 / 4 | no |
| `TS6` — Repeat-production decision | open | 0 / 4 | no |

## Controlled Claims

| Claim | Recorded status | Evidence | Claim evidenced |
|---|---|---|---|
| `supplier_support_committed` | unverified | — | no |
| `manufacturer_access_authorized` | unverified | — | no |
| `lm3_configuration_compatible` | unproven | — | no |
| `first_article_authorized` | not-authorized | — | no |
| `local_manufacture_transferred` | unproven | — | no |
| `all_in_repeat_cost` | unproven | — | no |
| `railway_acceptance` | not-granted | — | no |

## How This Uses The Existing Platform

The eight work packages consume the existing LM3 requirements, product tree, supplier anchors, RFQ candidates, mechanical interface register, first-article gates, manufacturing controls, city duty-cycle evidence and ERP/lifecycle identities. Accepted supplier data should update those sources through configuration-controlled changes; it must not be copied into a detached supplier spreadsheet and treated as a second design baseline.
The supplier intake contract is `design/component-catalogue/catalog/buildable-trainset/evidence/rfq-response-template.json` schema 2.0; it carries authority, frozen-baseline, separated-cost, interface-responsibility, local-capability and lifecycle-import fields.

Use `python3 tools/automation/validate-supplier-technical-support.py --check` to reject stale output or invalid references.
