# Deterministic Digital Assurance Report

> Design-screening evidence only. This is not certification, permission to manufacture, or permission to operate.

- Design fingerprint: `daf331f5d6a4cc8786a2fcd28f44783b07dfabf2b7553895b0696b7be7dadc0f`
- Digital pre-build gate: **PASS**
- Physical/revenue release: **BLOCKED**
- Scope: 10 standards records, 11 deterministic checks, 18 system failure modes
- Controlled inventory screened: **279 items**; item-specific reviews open: **279**
- Open physical-evidence rows: **18**

## Authority Boundary

Passing means the named deterministic design evidence is present and internally coherent. It is not certification, standard conformity, physical validation, permission to manufacture, or permission to operate.

Route selection never grants movement authority. Simulation and analysis reduce redesign risk; they do not waive mandatory physical or independent evidence.

## Deterministic Checks

| ID | Check | Standards | Result |
|---|---|---|---|
| `DA-001` | Safety requirements and hazards remain traceable | IEC-62278-1-2025, IEC-62267-2009, IEC-62425-2025 | **PASS** |
| `DA-002` | Train separation and speed supervision remain independent of route selection | IEC-62267-2009, IEC-62290-1-2025, IEC-62425-2025 | **PASS** |
| `DA-003` | Network-loss routing fails restrictively on disagreement | IEC-62290-1-2025, EN-50716-2023 | **PASS** |
| `DA-004` | Cabin and battery cooling allocation prioritises battery protection | IEC-62928-2017, IEC-60571-2012 | **PASS** |
| `DA-005` | Cross-domain FMEA has component, subsystem and system coverage | IEC-60812-2018, IEC-62278-1-2025 | **PASS** |
| `DA-006` | Civil structural screens retain physical release boundary | EN-1990, IEC-62278-1-2025 | **PASS** |
| `DA-007` | Recovery sidings, robots and single-track loops use protected movement functions | IEC-62267-2009, IEC-62290-1-2025 | **PASS** |
| `DA-008` | Physical and independent-assessment gaps remain release-blocking | IEC-62278-1-2025, IEC-62425-2025, IEC-62928-2017, IEC-61373-2026, EN-1990 | **PASS** |
| `DA-009` | Consensus restart and infrastructure faults fail closed | IEC-62278-1-2025, IEC-62425-2025, EN-50716-2023 | **PASS** |
| `DA-010` | Engineering benchmarks and interchange preserve units, CRS and identity | IEC-62278-1-2025, EN-50716-2023, EN-1990, IEC-62928-2017 | **PASS** |
| `DA-011` | Promoted component RFCs retain traceable implementation and release gaps | IEC-62278-1-2025, IEC-60812-2018, IEC-62928-2017, EN-1990 | **PASS** |

## FMEA Coverage

| Domain | Component | Subsystem | System |
|---|---:|---:|---:|
| civil | 1 | 1 | 1 |
| electrical | 1 | 1 | 1 |
| embedded-software | 1 | 1 | 1 |
| mechanical | 1 | 1 | 1 |
| operations | 1 | 1 | 1 |
| thermal | 1 | 1 | 1 |

## Controlled Inventory Screen

Every train product/assembly, station product/assembly, reusable civil type and Rust workspace crate is deterministically included below the JSON report's `inventory_coverage` key. These are preliminary family screens with item-specific analysis and accountable acceptance deliberately open.

| Scope | Items | Open item reviews |
|---|---:|---:|
| civil-type | 19 | 19 |
| software-crate | 59 | 59 |
| station-assembly | 10 | 10 |
| station-product | 45 | 45 |
| train-assembly | 26 | 26 |
| train-product | 120 | 120 |

## Failure Modes

| ID | Domain / level | Item | Failure mode | S/O/D | RPN | Physical evidence |
|---|---|---|---|---:|---:|---|
| `FMEA-CIV-C01` | civil / component | pier bearing | seizure, uplift or excessive displacement | 5/2/3 | 30 | open — required |
| `FMEA-CIV-S01` | civil / subsystem | single-track passing loop | point not detected locked or train exceeds loop | 5/2/2 | 20 | open — required |
| `FMEA-CIV-Y01` | civil / system | bridge and foundation system | scour, settlement or strength/serviceability exceedance | 5/2/3 | 30 | open — required |
| `FMEA-ELC-C01` | electrical / component | battery cell or module | overtemperature or internal short | 5/2/2 | 20 | open — required |
| `FMEA-ELC-S01` | electrical / subsystem | auxiliary power | common DC branch loss | 4/2/2 | 16 | open — required |
| `FMEA-ELC-Y01` | electrical / system | vehicle electrical protection | insulation or bonding failure | 5/2/3 | 30 | open — required |
| `FMEA-MEC-C01` | mechanical / component | axle bearing | seizure or overheating | 5/2/2 | 20 | open — required |
| `FMEA-MEC-S01` | mechanical / subsystem | friction and regenerative brake | insufficient commanded deceleration | 5/2/2 | 20 | open — required |
| `FMEA-MEC-Y01` | mechanical / system | train recovery interface | coupler or drawbar overload | 4/2/2 | 16 | open — required |
| `FMEA-OPS-C01` | operations / component | remote shunt robot | radio loss or unintended traction | 5/2/2 | 20 | open — required |
| `FMEA-OPS-S01` | operations / subsystem | corridor recovery | nearest robot or siding unavailable | 4/2/2 | 16 | open — required |
| `FMEA-OPS-Y01` | operations / system | unattended railway | automation failure combined with unavailable remote assistance | 5/2/3 | 30 | open — required |
| `FMEA-SW-C01` | embedded-software / component | localisation sensor adapter | stale or implausible measurement accepted | 5/2/2 | 20 | open — required |
| `FMEA-SW-S01` | embedded-software / subsystem | onboard route selector | common-mode plan and sensor error | 5/2/3 | 30 | open — required |
| `FMEA-SW-Y01` | embedded-software / system | distributed train protection | network partition plus inconsistent state | 5/2/2 | 20 | open — required |
| `FMEA-THM-C01` | thermal / component | battery coolant hose or seal | leak or pressure loss | 4/2/2 | 16 | open — required |
| `FMEA-THM-S01` | thermal / subsystem | combined thermal pack | common compressor unavailable | 4/2/2 | 16 | open — required |
| `FMEA-THM-Y01` | thermal / system | high-ambient vehicle duty | heat rejection below combined demand | 4/3/2 | 24 | open — required |

## Standards Profile

| Standard | Digital use | Physical evidence retained |
|---|---|---|
| [IEC-62278-1-2025](https://webstore.iec.ch/en/publication/68933) | Lifecycle, system definition, RAMS requirements, change impact and safety-case traceability | site validation, commissioning, operational demonstration, independent assessment |
| [IEC-62267-2009](https://webstore.iec.ch/en/publication/6681) | GoA4 functional safety and degraded-operation traceability | obstacle and intrusion trials, evacuation, rescue, operational validation |
| [IEC-62290-1-2025](https://webstore.iec.ch/en/publication/83773) | Continuous supervision, onboard localisation and command/control functional boundary | communications coverage, localisation calibration, end-to-end train protection test |
| [IEC-62425-2025](https://webstore.iec.ch/en/publication/68909) | Safety-case structure, integrity allocation, reuse and safety-related tool boundary | qualified controller, HIL, environmental tests, independent safety assessment |
| [EN-50716-2023](https://www.dinmedia.de/en/standard/din-en-50716/378381071) | Software lifecycle, verification, configuration and tool evidence | target-hardware integration, HIL, commissioning |
| [IEC-60812-2018](https://webstore.iec.ch/en/publication/26359) | Failure-mode identification, effects, causes, controls, ranking and maintenance | supplier FMEDA, inspection, fault injection, field feedback |
| [IEC-62928-2017](https://webstore.iec.ch/en/publication/31101) | Battery design, operating limits, data exchange and test-plan traceability | type tests, routine tests, thermal propagation, pack and vehicle integration |
| [IEC-60571-2012](https://webstore.iec.ch/en/publication/2514) | Electronic-equipment requirements and deterministic test mapping | environmental tests, power transients, EMC, target hardware |
| [IEC-61373-2026](https://webstore.iec.ch/en/publication/68999) | Mounting-category and load-case definition | shock test, random vibration test, post-test functional inspection |
| [EN-1990](https://eurocodes.jrc.ec.europa.eu/EN-Eurocodes/eurocode-basis-structural-design) | Ultimate/serviceability limit-state and reliability evidence structure | material certificates, geotechnical investigation, proof/load tests where specified, as-built survey |

## Interpretation

The deterministic design gate passed. Physical tests, site evidence, independent assessment and regulatory acceptance remain open and cannot be replaced by this report.
