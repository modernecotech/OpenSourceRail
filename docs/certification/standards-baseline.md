# Current standards applicability baseline

> Generated from `lib/templates/digital-assurance.toml`; do not edit by hand.

This registry records current publisher metadata and how OpenSourceRail routes evidence. It does **not** reproduce normative clauses or claim applicability or conformity. A deployment must obtain licensed text where required and freeze law, jurisdiction, national adoptions, editions, contracts, intended use and assessment bodies.

Metadata was reviewed on **2026-10-02**. The next fail-closed review is due **2026-10-31**.

## Publisher records

| Record | Scope used by OSR | Evidence that remains outside the digital gate |
|---|---|---|
| [`IEC-62278-1-2025`](https://webstore.iec.ch/en/publication/68933) | Lifecycle, system definition, RAMS requirements, change impact and safety-case traceability | site validation, commissioning, operational demonstration, independent assessment |
| [`IEC-62278-2-2025`](https://webstore.iec.ch/en/publication/79793) | Safety process, risk assessment, requirement allocation, integrity allocation and independence | independent assessment, validation evidence, accepted residual risk |
| [`IEC-62267-2009`](https://webstore.iec.ch/en/publication/6681) | GoA4 functional safety and degraded-operation traceability | obstacle and intrusion trials, evacuation, rescue, operational validation |
| [`IEC-62290-1-2025`](https://webstore.iec.ch/en/publication/83773) | Continuous supervision, onboard localisation and command/control functional boundary | communications coverage, localisation calibration, end-to-end train protection test |
| [`IEC-62425-2025`](https://webstore.iec.ch/en/publication/68909) | Safety-case structure, integrity allocation, reuse and safety-related tool boundary | qualified controller, HIL, environmental tests, independent safety assessment |
| [`IEC-62279-2015`](https://webstore.iec.ch/en/publication/22781) | Safety-related software lifecycle, competence, configuration, verification and tool evidence | target-hardware integration, timing and resource evidence, HIL, commissioning |
| [`EN-50716-2023`](https://www.dinmedia.de/en/standard/din-en-50716/378381071) | European software lifecycle, verification, configuration and tool evidence | target-hardware integration, HIL, commissioning |
| [`IEC-62280-2014`](https://webstore.iec.ch/en/publication/6749) | Threat and error model for safety-related communication over transmission systems | production-network fault injection, coverage and latency tests, key and configuration evidence |
| [`IEC-60812-2018`](https://webstore.iec.ch/en/publication/26359) | Failure-mode identification, effects, causes, controls, ranking and maintenance | supplier FMEDA, inspection, fault injection, field feedback |
| [`IEC-62928-2017`](https://webstore.iec.ch/en/publication/31101) | Battery design, operating limits, data exchange and test-plan traceability | type tests, routine tests, thermal propagation, pack and vehicle integration |
| [`IEC-60571-2012`](https://webstore.iec.ch/en/publication/2514) | Electronic-equipment requirements and deterministic test mapping | environmental tests, power transients, EMC, target hardware |
| [`IEC-61373-2026`](https://webstore.iec.ch/en/publication/68999) | Mounting category, load case and permitted simulation/test-exemption traceability | shock test, random vibration test, post-test functional inspection |
| [`IEC-62443-4-1-2018`](https://webstore.iec.ch/en/publication/33615) | Secure development, verification, vulnerability, patch and end-of-life process | product security assessment, deployment hardening, penetration testing, patch exercise |
| [`IEC-62443-4-2-2019`](https://webstore.iec.ch/en/publication/34421) | Component security capability and foundational-requirement evidence mapping | configured component test, network segmentation test, credential and update validation |
| [`ISO-IEC-IEEE-15288-2023`](https://www.iso.org/standard/81702.html) | Common system life-cycle process and acquirer/supplier information exchange framework | project plans, reviews, verification and validation records, transition and disposal evidence |
| [`ISO-9001-2026`](https://www.iso.org/standard/9001) | Organization-wide quality, documented information, operational control, performance evaluation and improvement | implemented QMS, competence records, supplier and production records, internal and external audit |
| [`ISO-22163-2023`](https://www.iso.org/standard/79427.html) | Railway-sector quality management, supplier, project and production evidence structure | implemented railway QMS, process audits, supplier controls, production and special-process qualification |
| [`ISO-55001-2024`](https://www.iso.org/standard/83054.html) | Asset-management objectives, lifecycle decisions, information, performance and improvement | implemented asset management system, asset data and decisions, audits, field performance |
| [`ISO-19650-1-2018`](https://www.iso.org/standard/68078.html) | Whole-life information management, exchange, recording, versioning and organization | project information requirements, accepted information deliveries, as-built and asset information |
| [`ISO-16739-1-2024`](https://www.iso.org/standard/84123.html) | Open IFC exchange for buildings and infrastructure including railways and bridges | accepted model-view and information requirements, as-built model validation, handover verification |
| [`ISO-IEC-17025-2017`](https://www.iso.org/standard/66912.html) | Competence, impartiality, method, calibration, traceability and result-record requirements for test evidence | laboratory scope and accreditation where required, method validation, calibration traceability, raw test records |
| [`EN-1990-DEPLOYMENT`](https://eurocodes.jrc.ec.europa.eu/EN-Eurocodes/eurocode-basis-structural-design) | Ultimate/serviceability limit-state, reliability, durability and design-working-life evidence structure | material certificates, geotechnical investigation, proof/load tests where specified, as-built survey |
| [`EU-CSM-402-2013`](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013R0402) | Significance, hazard record, risk acceptance principles, interfaces and independent assessment for changes when applicable | proposer risk-management file, assessment-body report, hazard closure and accepted change |

## Transition notes

- ISO 9001:2026 is the current ISO quality-management edition as of the review date and replaces ISO 9001:2015.
- ISO 22163:2023 with Amendment 1:2024 remains the current railway QMS publisher record and still names ISO 9001:2015; deployments must agree and record the transition basis rather than silently rewriting its normative reference.
- EN 50716:2023 is the current OSR European software baseline; legacy EN 50128/EN 50657 mappings require a recorded national or contractual reason during the transition.
- EN 1990 is deliberately edition-neutral here because the deployment must select its national adoption and National Annex.
- EU Regulation 402/2013 is included only as an EU/contractually adopted example; it is not automatically applicable outside that jurisdiction.

## Machine-readable controls

The generated [digital standards report](digital-assurance-report.md) maps 23 records through 16 control objectives to 15 hashed repository checks. Its result is evidence coherence only. The [all-component assurance register](component-assurance-register.md) carries the resulting G0–G4 decision boundary to each controlled item.
