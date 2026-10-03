# OpenSourceRail Baghdad — concept and FEED offer

This package presents a city-specific, evidence-linked proposal for a Baghdad
urban railway. It is intended to start an owner-led feasibility, requirements
and front-end engineering design (FEED) engagement with the relevant Iraqi and
Baghdad authorities. It is **not** a construction release, supplier quotation,
regulatory approval or safety certificate.

## Offer documents

- [Baghdad system offer (PDF)](Baghdad-OpenSourceRail-System-Offer.pdf)
- [Network design and reproducible engineering evidence](../README.md)
- [Offer evidence manifest](manifest.json)
- [Baghdad operations dashboard](screenshots/baghdad-operations-dashboard.png)
- [Baghdad project twin](screenshots/baghdad-project-twin.png)
- [Baghdad QA gates](screenshots/baghdad-qa-gates.png)
- [Engineering GIS view](../engineering/screenshots/baghdad-qgis-engineering-map.png)
- [Native simulation dashboard](../engineering/screenshots/baghdad-simulation-dashboard.png)
- [SUMO timetable validation](../engineering/screenshots/baghdad-sumo-validation.png)

## Proposed system

The current planning baseline contains 9 lines, 516.5 km of
double-track route, 182 unique stations, 23 interchange
complexes and 831 six-car trainsets. The service plan targets a three-minute
peak headway and a 05:30–02:00 operating day. The civil screen identifies
428.3 km at grade,
75.8 km elevated and
12.4 km of bridge works. Open geospatial screening
must be confirmed by survey, property, utilities, ground, hydraulic and alignment
evidence during FEED.

The energy concept includes 52.1 MW of station/depot
PV, 354.0 MWh of storage,
316.0 MW of connected charging and
1018.6 MW of dedicated solar. Operating energy,
islanding, connections, protection, land and duty remain unaccepted.

City planning CAPEX is USD 7.56 billion before owner-confirmed land,
utilities, tax/duty and escalation. The $8 M depot allowance
is **not reconciled** to surveyed stabling, workshops, energy, fire and security.
The Baghdad manufacturing plant is outside city CAPEX and counted once in the Baghdad-only programme.

## Iraq financing proposal

The [city funding model](../engineering/finance/FUNDING-MODEL.md) and
[Baghdad-only programme](../../IRAQ-FUNDING-PROGRAMME.md) divide eligible Chinese
component invoices, government capital, IQD bonds and IQD bank credit.
Government capital is 25% of total CAPEX, including **USD 896.07 million**
for half the imported-parts budget. Proposed Chinese USD credit covers the other
half. Remaining government capital, bonds and bank credit are in IQD. Full import
basket lender and supplier-origin qualification remains pending. Fees, interest, reserves and
cash support beyond that contribution are separately disclosed funding needs.
They include staged draws, native-currency principal/interest, fees, reserves,
cash support and downside funding gaps. The rates, maturities and 50% invoice
advance are uncommitted appraisal assumptions. The resource-constrained
construction cash schedule is not a five-year funding promise. Monthly and
annual ledgers and charts are generated from the same controlled model.

The programme comparison covers the historical 148 km / USD 18 billion proposal
against this 516.5 km / 182 station planning network.
Total USD capital funding (government USD cash plus Chinese loan) is
USD 1.792 billion; the rest is IQD.
The older all-USD financing basis is the requested comparison scenario, not
verified final contract terms. The modelled fare is IQD 1,317
per paid trip. Population access uses a 46.4%
anchor-weighted planning score, not a surveyed resident catchment. Local
procurement is USD 6.084 billion equivalent;
indicative operating employment is 2,350 FTE. Construction
job counts require validated hours and productivity. The model leaves USD
9.786 billion in additional
cash requirements in the full-network-only case if public funding is capped at the
25% capital contribution. The conditional phased case reduces this to USD
8.320 billion,
with first / last line openings in months
66 /
346.
These are gross nominal liquidity needs, not net lifetime loss. Opening dates
require actual plant, depot, line and safety acceptance; fleet-based phase demand
and the 25% fixed / 75% variable OPEX split remain planning assumptions.

## Rolling stock and CRRC component strategy

The proposed fleet uses the OpenSourceRail six-car battery-electric platform
with a **candidate CRRC component package**. Candidate scope includes traction
motors, converters/inverters, auxiliary conversion and train-control
interfaces, bogies, air springs, dampers, couplers/draft gear, brake equipment
and passenger-information interfaces. These product families are supported by
CRRC's public component catalogue:

- [CRRC components overview](https://www.crrcgc.cc/en/73_5129/73_6648/index.html)
- [CRRC vehicle components](https://www.crrcgc.cc/en/73_5129/73_6648/73_6652/fca468a4-2.html)
- [CRRC electric-control equipment](https://www.crrcgc.cc/en/73_5129/73_6648/73_6650/index.html)
- [CRRC Dalian traction and control](https://www.crrcgc.cc/dldqen/130_7787/index.html)

This repository has no CRRC partnership, endorsement, selected supplier,
quotation or configuration approval. Any CRRC parts remain subject to open and
competitive procurement, supplier offers, interface control, RAMS/FMEA,
cybersecurity, EMC, fire/environmental qualification, hardware-in-the-loop and
first-article testing, factory/site acceptance, spares and obsolescence terms,
licensing and the competent authorities' acceptance.

## Digital delivery and management system

The Baghdad package already instantiates 1,862 assets, 8,012 manufacturing and verification tasks, 15,804 material/procurement rows, 10,785 maintenance tasks and 6,689 QA actions. These feed the project twin, operations portal,
ERPNext/Frappe adapters, supervision/SCADA boundary, maintenance planning,
controlled evidence, QR identity, and multi-model AI advisory council.

The AI council may prepare and independently cross-check reversible management
drafts. It cannot grant movement authority, bypass train protection, command
SCADA, hire or dismiss staff, commit funds, sign contracts, certify work or
exercise legal or safety authority. Named humans retain approval and
accountability, and model identity, inputs, dissent and decision evidence are
recorded.

## Assurance and present release boundary

The deterministic package uses five fail-closed assurance gates:

1. **G0 — identity and source baseline:** configuration, provenance and hashes.
2. **G1 — design assurance:** requirements, hazards, interfaces and applicable standards.
3. **G2 — implementation qualification:** actual supplier/product evidence and tests.
4. **G3 — installed integration:** site, vehicle, system and operational validation.
5. **G4 — independent/legal acceptance:** competent authority and independent assessor decisions.

The GIS, finance generation, native simulation and SUMO timetable checks pass
their planning gates. The city package is deliberately marked **incomplete**
because physical depot and distributed stabling positions have not been
surveyed or verified. Construction release also requires a surveyed
alignment/property/utility baseline; calibrated demand and an operator-owned
timetable; geotechnical, drainage, structural and fire acceptance;
supplier-frozen battery, charger, traction and mechanical equipment; and
independent safety assessment and legal authorization.

## Recommended engagement

1. Establish the Iraqi owner, governance, data room and acceptance authorities.
2. Run a 12–16 week data-validation and corridor-selection phase.
3. Complete survey, demand calibration, depot/stabling option selection and
   system requirements for a priority corridor.
4. Obtain competing supplier packages—including, but not limited to, CRRC—and
   freeze validated component interfaces and whole-life support.
5. Deliver a pilot corridor through G1–G4 before authorizing network rollout.

The PDF is generated from the current city design, engineering summaries and
screenshots by `tools/automation/build-baghdad-offer.py`; `manifest.json`
records the input and output hashes.
