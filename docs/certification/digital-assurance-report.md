# Digital standards-adherence report

> Deterministic evidence-coherence result—not certification, conformity, construction release or permission to operate.

- Design fingerprint: `eb1a9059a0bdc6416236ede0d2788474e666067453ad5b33b7a5e5720a7c104d`
- Digital evidence-coherence gate: **PASS**
- Standards conformity: **NOT-ASSESSED**
- Physical/revenue release: **BLOCKED**
- Scope: **23** publisher records, **5** assurance profiles, **16** control objectives and **15** repository checks
- Inventory: **280** engineering items screened; **280** item reviews remain open
- Registry reviewed: 2026-10-02; next mandatory review: **2026-10-31**

## What the result means

Passing means the named repository evidence is present, hashed, traceable and internally coherent. It is not a clause-by-clause conformity finding, certification, physical validation, permission to manufacture, construction release or permission to operate.

The compiler validates identities, mappings, coverage, evidence paths, hashes, review dates and fail-closed states. It deliberately leaves deployment applicability, licensed clause assessment, physical evidence and every competent decision open.

## Digital thread

```text
publisher record + deployment law + intended use
  → applicability decision and licensed clauses
    → OSR control objective
      → requirement / hazard / design item
        → method + acceptance criterion + configuration
          → raw evidence + hash + reviewer + validity
            → G1–G4 decision and conditions of use
              → change impact / expiry / field feedback
```

## Open applicability inputs

| ID | Deployment input | State |
|---|---|---|
| `APP-JURISDICTION` | Jurisdiction and competent authorities | `deployment-input-open` |
| `APP-INTENDED-USE` | System boundary, intended use and operating concept | `deployment-input-open` |
| `APP-LEGAL` | Railway, building, fire, accessibility, labour, privacy and environmental law | `deployment-input-open` |
| `APP-CONTRACT` | Employer requirements, contracts, funding conditions and adopted technical rules | `deployment-input-open` |
| `APP-CLASSIFICATION` | Safety, security, quality and asset criticality classifications | `deployment-input-open` |
| `APP-ASSESSMENT` | Conformity modules, assessment bodies, independence and authorization route | `deployment-input-open` |

## Assurance profiles

| Profile | Standards | Decision boundary |
|---|---:|---|
| `PROFILE-SYSTEM-SAFETY` — System RAMS, automation and authorization | 5 | Deployment safety authority and competent bodies freeze applicability and acceptance route. |
| `PROFILE-CONTROL-SOFTWARE` — Safety-related control, software and communications | 6 | Safety classification and national/international software route are deployment decisions. |
| `PROFILE-VEHICLE-EQUIPMENT` — Vehicle equipment, battery and environment | 4 | Product and vehicle qualification require exact selected components and physical evidence. |
| `PROFILE-CIVIL-BIM` — Civil structures and lifecycle information | 4 | The project freezes national structural rules, annexes, survey basis and information requirements. |
| `PROFILE-QUALITY-ASSET` — Quality, laboratories, assets and system lifecycle | 5 | Organization, laboratory and certification scopes remain separately assessed. |

## Control objectives

| Control | Gate | Domains | Physical evidence | State |
|---|---|---|---|---|
| `STD-CTRL-001` — System boundary, intended use and applicability | G1 | system, operations, information, quality | depends on child evidence | `mapped-not-assessed` |
| `STD-CTRL-002` — Requirements, interfaces and bidirectional traceability | G3 | system, information, quality | required | `mapped-not-assessed` |
| `STD-CTRL-003` — Hazard identification, FMEA and accepted risk | G4 | system, mechanical, electrical, thermal, embedded-software, civil, operations | required | `mapped-not-assessed` |
| `STD-CTRL-004` — RAMS allocation, automated-operation protection and safety case | G4 | system, embedded-software, operations, quality | required | `mapped-not-assessed` |
| `STD-CTRL-005` — Safety-related software lifecycle and target evidence | G4 | embedded-software, system, quality | required | `mapped-not-assessed` |
| `STD-CTRL-006` — Safety communication, cybersecurity and recovery | G4 | embedded-software, electrical, cybersecurity, information, operations | required | `mapped-not-assessed` |
| `STD-CTRL-007` — Battery, thermal and rolling-stock electronic equipment | G4 | electrical, thermal, mechanical, embedded-software | required | `mapped-not-assessed` |
| `STD-CTRL-008` — Equipment mounting, shock and vibration | G3 | mechanical, electrical | required | `mapped-not-assessed` |
| `STD-CTRL-009` — Civil, geotechnical, hydraulic and structural design basis | G4 | civil, mechanical, system | required | `mapped-not-assessed` |
| `STD-CTRL-010` — BIM and lifecycle information requirements | G3 | information, civil, mechanical, operations | required | `mapped-not-assessed` |
| `STD-CTRL-011` — Quality, supplier, manufacturing and special-process control | G4 | quality, mechanical, electrical, civil, embedded-software, operations | required | `mapped-not-assessed` |
| `STD-CTRL-012` — Test method, laboratory competence and measurement traceability | G4 | quality, information, mechanical, electrical, thermal, civil | required | `mapped-not-assessed` |
| `STD-CTRL-013` — Model, simulation and tool validity | G3 | system, mechanical, electrical, thermal, embedded-software, civil, information | required | `mapped-not-assessed` |
| `STD-CTRL-014` — Verification, validation, commissioning and operational demonstration | G4 | system, mechanical, electrical, thermal, embedded-software, civil, operations, quality | required | `mapped-not-assessed` |
| `STD-CTRL-015` — Asset, maintenance, competence and field-performance management | G4 | operations, quality, information, system | required | `mapped-not-assessed` |
| `STD-CTRL-016` — Configuration, change impact, evidence provenance and decision ledger | G4 | system, information, quality, operations, embedded-software | depends on child evidence | `mapped-not-assessed` |

## Repository evidence checks

| ID | Check | Controls | Machine result | Conformity |
|---|---|---|---|---|
| `DA-001` | Safety requirements and hazards remain traceable | STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-002` | Train separation and speed supervision remain independent of route selection | STD-CTRL-004, STD-CTRL-005 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-003` | Network-loss routing fails restrictively on disagreement | STD-CTRL-004, STD-CTRL-005, STD-CTRL-006 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-004` | Cabin and battery cooling allocation prioritises battery protection | STD-CTRL-003, STD-CTRL-007 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-005` | Cross-domain FMEA has component, subsystem and system coverage | STD-CTRL-002, STD-CTRL-003 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-006` | Civil structural screens retain survey and physical release boundaries | STD-CTRL-009, STD-CTRL-012, STD-CTRL-013, STD-CTRL-014 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-007` | Recovery sidings, robots and single-track loops retain protected movement functions | STD-CTRL-003, STD-CTRL-004, STD-CTRL-014 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-008` | Physical and independent-assessment gaps remain release-blocking | STD-CTRL-007, STD-CTRL-008, STD-CTRL-009, STD-CTRL-012, STD-CTRL-014, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-009` | Consensus restart and infrastructure faults fail closed | STD-CTRL-005, STD-CTRL-006, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-010` | Engineering benchmarks and interchange preserve units, CRS and identity | STD-CTRL-002, STD-CTRL-007, STD-CTRL-009, STD-CTRL-010, STD-CTRL-013, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-011` | Promoted component RFCs retain traceable implementation and release gaps | STD-CTRL-002, STD-CTRL-003, STD-CTRL-007, STD-CTRL-009, STD-CTRL-011, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-012` | Multi-day normal, peak, degraded and recovery profiles retain bounded logical state | STD-CTRL-004, STD-CTRL-005, STD-CTRL-013, STD-CTRL-014 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-013` | Every controlled engineering and operational-platform item has a fail-closed assurance passport | STD-CTRL-001, STD-CTRL-003, STD-CTRL-011, STD-CTRL-015, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-014` | BIM federation and IDS checks use current IFC4.3 lifecycle identities | STD-CTRL-010, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |
| `DA-015` | Quality, lifecycle and laboratory evidence retain competence and approval boundaries | STD-CTRL-011, STD-CTRL-012, STD-CTRL-015, STD-CTRL-016 | `evidence-linked-and-hashed` | `not-assessed` |

## Standards registry

| Record | Publisher / edition | Status at review | Jurisdiction | Next review |
|---|---|---|---|---|
| [`IEC-62278-1-2025`](https://webstore.iec.ch/en/publication/68933) | IEC / 2025 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-62278-2-2025`](https://webstore.iec.ch/en/publication/79793) | IEC / 2025 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-62267-2009`](https://webstore.iec.ch/en/publication/6681) | IEC / 2009 | current-publisher-record-stability-2028 | international-reference | 2027-01-02 |
| [`IEC-62290-1-2025`](https://webstore.iec.ch/en/publication/83773) | IEC / 2025 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-62425-2025`](https://webstore.iec.ch/en/publication/68909) | IEC / 2025 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-62279-2015`](https://webstore.iec.ch/en/publication/22781) | IEC / 2015 | current-publisher-record-stability-2030 | international-reference | 2027-01-02 |
| [`EN-50716-2023`](https://www.dinmedia.de/en/standard/din-en-50716/378381071) | CEN-CENELEC national adoption record / 2023 | current-European-baseline-transition-from-EN-50128-and-EN-50657 | European-or-contractual-candidate | 2026-10-31 |
| [`IEC-62280-2014`](https://webstore.iec.ch/en/publication/6749) | IEC / 2014 | current-publisher-record-stability-2028 | international-reference | 2027-01-02 |
| [`IEC-60812-2018`](https://webstore.iec.ch/en/publication/26359) | IEC / 2018 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-62928-2017`](https://webstore.iec.ch/en/publication/31101) | IEC / 2017 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-60571-2012`](https://webstore.iec.ch/en/publication/2514) | IEC / 2012 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-61373-2026`](https://webstore.iec.ch/en/publication/68999) | IEC / 2026 | current-publisher-record | international-reference | 2027-01-02 |
| [`IEC-62443-4-1-2018`](https://webstore.iec.ch/en/publication/33615) | IEC / 2018 | current-publisher-record-edition-2-under-development | international-reference | 2027-01-02 |
| [`IEC-62443-4-2-2019`](https://webstore.iec.ch/en/publication/34421) | IEC / 2019 with COR1:2022 | current-publisher-record | international-reference | 2027-01-02 |
| [`ISO-IEC-IEEE-15288-2023`](https://www.iso.org/standard/81702.html) | ISO/IEC/IEEE / 2023 | current-publisher-record | international-reference | 2027-01-02 |
| [`ISO-9001-2026`](https://www.iso.org/standard/9001) | ISO / 2026 | current-publisher-record-replaces-2015 | management-system-candidate | 2026-12-16 |
| [`ISO-22163-2023`](https://www.iso.org/standard/79427.html) | ISO / 2023 with Amd 1:2024 | current-publisher-record-references-ISO-9001-2015-transition-review-required | railway-quality-candidate | 2026-12-16 |
| [`ISO-55001-2024`](https://www.iso.org/standard/83054.html) | ISO / 2024 | current-publisher-record | management-system-candidate | 2027-01-02 |
| [`ISO-19650-1-2018`](https://www.iso.org/standard/68078.html) | ISO / 2018 | current-confirmed-2024-revision-under-development | international-reference | 2026-12-31 |
| [`ISO-16739-1-2024`](https://www.iso.org/standard/84123.html) | ISO / 2024 | current-publisher-record-replaces-2018 | international-reference | 2027-01-02 |
| [`ISO-IEC-17025-2017`](https://www.iso.org/standard/66912.html) | ISO/IEC / 2017 | current-confirmed-2023 | conformity-assessment-candidate | 2027-01-02 |
| [`EN-1990-DEPLOYMENT`](https://eurocodes.jrc.ec.europa.eu/EN-Eurocodes/eurocode-basis-structural-design) | CEN national adoption selected by deployment / deployment-selected edition and national annex | applicability-and-national-adoption-open | European-or-contractual-candidate | 2027-01-02 |
| [`EU-CSM-402-2013`](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013R0402) | European Union / Regulation 402/2013 as amended | current-EU-legal-source-jurisdiction-limited | EU-or-contractually-adopted-only | 2027-01-02 |

## FMEA coverage

| Domain | Component | Subsystem | System |
|---|---:|---:|---:|
| civil | 1 | 1 | 1 |
| electrical | 1 | 1 | 1 |
| embedded-software | 1 | 1 | 1 |
| mechanical | 1 | 1 | 1 |
| operations | 1 | 1 | 1 |
| thermal | 1 | 1 | 1 |

## Evidence and change control

Every evidence object must carry 16 metadata fields. Current repository links are machine state `generated-unreviewed`; no link is silently promoted to reviewed or accepted.

The JSON report contains a path-level `change_impact_index` for 157 hashed inputs. Comparing reports identifies changed paths and reopens mapped controls rather than averaging them into a green parent score.

## Interpretation

The deterministic evidence-coherence gate passed. Standards applicability, clause-level assessment, physical tests, site evidence, independent assessment and regulatory acceptance remain open.

## Connected engineering

The [connected engineering example](connected-engineering.md) and [generated report](connected-engineering-report.md) bind battery-cooling failure propagation, requirement criteria, controller scenarios, planned physical tests, synthetic production records and installed occurrences to exact design revisions. The JSON includes dependency traversal and explicit blocked deployment decisions.

The [subsystem qualification workflow](subsystem-qualification.md) adds quantitative RAMS screens, controlled rig measurements, model correlation, manufacturing equivalence and six separate decision-readiness states. Physical evidence and deployment decisions remain open.

The [civil reference demonstration](../../engineering/assurance/civil-reference/README.md) adds 20/25 m double-track bays, connection and erection controls, measured-result release interfaces and a connected construction/service FMEA. Its graph and controlled source hashes are included in this report and change-impact traversal; site inputs, physical qualification and independent release remain pending.

The [train-centred prototype](../../engineering/assurance/tacs/README.md) adds the actual process reference around existing interlocking/ATP/ATO/brake, bounded formal protocol and shared sensor-to-separation/interaction FMEA. Model and firmware changes invalidate execution evidence and traverse procedures and blocked release decisions; physical and operational qualification remain pending.
