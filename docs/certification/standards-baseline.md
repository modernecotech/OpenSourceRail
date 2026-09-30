# Current standards applicability baseline

This is the single release-facing list of standards used to organise OSR
assurance evidence. It does not claim certification, conformity, or access to
the full normative text. A deployment must freeze the applicable national
adoptions with its independent safety assessor and regulator.

IEC 62278-1:2025 applies its RAMS lifecycle from complete railway systems down
to subsystems and components, including software, but explicitly does not define
product-certification rules or stakeholder approval. OSR therefore uses one
[G0–G4 component assurance lifecycle](README.md#the-five-gates) while keeping
conformity assessment, independent safety assessment and legal authorization as
separate decisions.

| Subject | v0.3 baseline | Use in OSR |
|---|---|---|
| Automated urban guided transport | IEC 62267:2009 / applicable EN adoption | High-level GoA 4 safety requirements; IEC lists a stability date of 2028. |
| RAMS lifecycle | IEC 62278-1:2025 with IEC 62278-2:2025 | Current generic RAMS process. Applicable EN 50126 national mappings remain deployment-controlled. |
| Railway software | EN 50716:2023 | Software-development baseline. It supersedes EN 50128 and EN 50657; legacy references are retained only as transition mappings where a national adoption still requires them. |
| Urban guided transport management and command/control | IEC 62290-1:2025 | Current UGTMS principles and functions across GoA 1–4. |
| Safety-related signalling electronics | EN 50129, applicable national edition | Safety-case structure and signalling electronic-system evidence. |
| Safety-related signalling electronics (international) | IEC 62425:2025 | Functional-safety lifecycle, safety cases, reuse and safety-related tool evidence; deployment mapping to the applicable EN/national adoption is controlled separately. |
| Failure-mode analysis | IEC 60812:2018 | Cross-domain FMEA/FMECA method, documentation, action and maintenance structure. |
| Onboard traction batteries | IEC 62928:2017 | Lithium-ion traction-battery design, operation, safety, data exchange and type/routine-test mapping. |
| Rolling-stock electronic equipment | IEC 60571:2012 | Electronic-equipment requirements and target-hardware/environmental evidence mapping. |
| Rolling-stock shock and vibration | IEC 61373:2026 | Current equipment mounting, shock, random-vibration and structural-integrity test baseline. |
| Structural design basis | EN 1990, applicable national adoption | Reliability, ultimate/serviceability limit states, durability and design working-life basis. |
| Rolling-stock crashworthiness and fire | EN 15227 and EN 45545, applicable parts/editions | Reference requirements for the train design; evidence remains first-article and deployment work. |
| Cybersecurity | IEC 62443-4-2 and EN 50701, applicable editions | Component and railway cybersecurity evidence. |

Publisher records used to maintain this metadata:

- [IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933)
- [IEC 62267:2009](https://webstore.iec.ch/en/publication/6681)
- [IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773)
- [IEC 62425:2025](https://webstore.iec.ch/en/publication/68909)
- [IEC 60812:2018](https://webstore.iec.ch/en/publication/26359)
- [IEC 62928:2017](https://webstore.iec.ch/en/publication/31101)
- [IEC 60571:2012](https://webstore.iec.ch/en/publication/2514)
- [IEC 61373:2026](https://webstore.iec.ch/en/publication/68999)
- [European Commission JRC: EN 1990](https://eurocodes.jrc.ec.europa.eu/EN-Eurocodes/eurocode-basis-structural-design)
- [DIN EN 50716 record](https://www.dinmedia.de/en/standard/din-en-50716/378381071)

The conflicting-national-standard withdrawal date recorded for EN 50716 is
30 October 2026. Because v0.3 is prepared during that transition, project
traceability may name EN 50128 or EN 50657 only as a legacy mapping alongside
EN 50716—not as the current OSR software baseline.

The machine-readable profile is
[`lib/templates/digital-assurance.toml`](../../lib/templates/digital-assurance.toml).
The route/gate/passport profile is
[`lib/templates/component-assurance.toml`](../../lib/templates/component-assurance.toml).
Its generated report is a deterministic pre-build coherence gate: it may find
defects earlier and reduce redesign, but cannot claim conformity or replace
required type, routine, environmental, site, commissioning or independent
assessment evidence.
