# v0.7 reference corridor: one cost and delivery plan

**17 November 2026 | 2026 US dollars | Class C concept estimate**

**Installed capital: US$1,023.5 million, or US$34.12 million per route-km.** The
30-year whole-life present cost is **US$1,665.9 million** at a 4% real discount
rate. This prices one explicit, fully elevated 30 km, two-track, 12-station
*synthetic* corridor with powered wheel bogies and rigid 1.5 kV DC overhead.
It is a design budget for comparing and quoting the candidate, not a Baghdad
alignment price, contracted bid, or passenger-service authority. All fourteen
capital scopes receive an amount; the absent station-launch machinery is a
design exclusion rather than an unpriced item.

The physical parent is powered research candidate
`ac550fe8ff23f20cb1ae5b142f4ef6160afc9de6efe7850754bac96a7789327d`
in the [joined prototype bundle](../../design-engine/v07-prototype-bundle/README.md).
The [joint-free 10 m civil option](../../design-engine/v07-simple-span/README.md)
is the costed civil child. Its structural connection to the powered vehicle is
an analytical load screen; the resulting combination is a **concept budget
configuration**, not a new physically accepted selection. The retained v0.6
passive-wheel selection and its different-candidate US$738.0 million price
control are not repriced here. The exact cost input identity is the SHA-256
`e0fb358988480c0064871e0cea43b86a4b7224998d91b14b90bd71aaea3d11ff`
of [basis.csv](basis.csv). The source packet byte identities below are fixed
to the [cost preparation commit](https://github.com/modernecotech/OpenSourceRail/commit/8557b2b13f)
so a later publication does not relabel this estimate as a new physical
evaluation:

| Source | SHA-256 |
|---|---|
| [Powered prototype result at cost epoch](https://github.com/modernecotech/OpenSourceRail/blob/8557b2b13f/docs/design-engine/v07-prototype-bundle/packet/result.json) | `0f8e75b8a66f9b886c1af1f75ef7bd9fcb55f60190fe586d5e7b6be766011e3f` |
| [Joint-free span plan at cost epoch](https://github.com/modernecotech/OpenSourceRail/blob/8557b2b13f/docs/design-engine/v07-simple-span/plan.json) | `37adb933ca2ab8aa53f5d3c9d4eb7f1147fcb64761ce8b97727e1a4638fad784` |
| [Powered cost handoff at cost epoch](https://github.com/modernecotech/OpenSourceRail/blob/8557b2b13f/docs/design-engine/v07-powered-cost/result.json) | `b905d50e0e4bc3e28b61763d9b7ea89fbcafbacf64443c266320bb261e02dbaa` |

## Service, quantities and price basis

Six 17 m cars provide **276 normal places** per 104.5 m train, including two
wheelchair places per car and no planned standing. The concept uses 24 driven
axles, six roof collectors and twelve independent brake modules per set. The
analytical normal design-load allowance is **25.072 t/car** and crowd structural
control **33.622 t/car**; neither is a weighed installed car. The 2% grade
case asks for **102.23 kN** traction force, **2.045 MW** mechanical peak and at
least **3.037 MW DC/train** input rating. Its independent stopping, power-loss
braking and rescue interfaces remain prototype test items.

The capacity control is **30 trains/hour/direction** at **120 s** peak headway,
35 s dwell and 72 km/h cap: **8,280 offered normal places/hour/direction**.
The analytical fleet is **44 active plus 7 reserve sets**, including 180 s
terminal turnback and 5% motion allowance. Platform clear length is budgeted
at 125 m for the 104.5 m train and its approach/door tolerances. Full-tail
clearance, interlocking, accessible boarding, dwell, grid load and actual
fleet timetable must be demonstrated before the service plan is adopted.

The civil quantity control is **6,000 ten-metre precast beam/lifts**, **6,002
independent pier/footing positions**, **24,000 bearings**, 68,025.6 m³ of beam
concrete, 73,524.5 m³ of assumed footing/pier concrete, 18,195.7 t of counted
beam steel, and 60 track-km of rail, walkways and overhead. The 6,002 count
joins 3,000 bays/track continuously and avoids counting module boundaries
twice. It assumes simple ground supporting spread footings, no tunnel, river
crossing, exceptional property acquisition or station-specific span; those
conditions require remeasurement and a changed estimate.

Unit rates below are **project planning allowances**, inclusive of direct
fabrication, erection and standard installation within the stated scope.
The vehicle allowance is US$5.9 million per powered six-car set, replacing
the old passive-set rate with an explicit traction and collector premium.
The overhead allowance is US$1.2 million/track-km plus six US$3 million
rectifier/grid sites. For context, the [World Bank's railway electrification
study](https://documents1.worldbank.org/curated/en/099063023170016545/pdf/P1748630c1d3630a80876405ecad08e27f8.pdf)
gives about US$1 million/track-km for straightforward overhead layouts; it is
an analogue, not an Iraq or rigid-DC quotation. The [US FTA capital-cost
database](https://www.transit.dot.gov/capital-cost-database) illustrates why
guideway, systems, stations and vehicles are separate priced scopes. Supplier
rates, taxes and ground must replace these allowances for procurement.

## Fourteen-scope capital ledger

| Scope | Quantity and unit rate | US$m |
|---|---:|---:|
| Powered fleet and vehicle interfaces | 51 sets × 5.9m | 300.900 |
| 10 m beams, bearings and detail | 6,000 × 0.014m | 84.000 |
| Piers, spread footings and ordinary groundworks | 6,002 × 0.008m | 48.016 |
| Beam transport and erection | 6,000 lifts × 0.005m | 30.000 |
| Rails, welding and protected access | 60 track-km × 0.5m | 30.000 |
| Station-launch machinery | 0; omitted by powered architecture | 0.000 |
| Overhead, return, feeders, sectioning and grid protection | 60 track-km × 1.2m + 6 substations × 3m | 90.000 |
| Elevated stations, platforms and access | 12 × 8m | 96.000 |
| Terminal turnbacks and line control | 2 × 6m | 12.000 |
| Auxiliary feed and charging | 12 stations × 1.25m | 15.000 |
| Depot, production tooling, land and utilities | 1 complex × 62m | 62.000 |
| Fleet spares, commissioning and recovery assets | 1 programme × 30m | 30.000 |
| Prototype tests, independent assurance and import-tax provision | 1 programme × 55m | 55.000 |
| Project risk contingency | 20% of US$852.916m counted direct cost | 170.583 |
| **Installed capital** | **30 route-km** | **1,023.499** |

The station allowance includes the 125 × 8 m accessible platform deck,
vertical access, lighting, fire and evacuation provisions, and equipment
rooms. The depot row contains a US$42m vehicle/depot works allowance, US$12m
production and maintenance tooling, and US$8m ordinary land/utility provision.
The US$55m test/tax row contains US$20m full-scale qualification and assurance
and US$35m customs/import-tax planning provision. The contingency is applied
**once** to direct capital. Finance interest, debt fees and recoverable VAT
are outside installed capital and must enter a financing model separately.

This is **US$123,611 per offered peak place/hour/direction**. The old 30 km
station-launch price is a different vehicle/civil/power configuration and is
not a transferred cost row. The greater powered fleet, continuous overhead,
more supports and complete station allowance explain this concept's higher
total; a supplier/design iteration must reduce actual cost rather than
deleting required equipment.

## Operation and 30-year whole-life cost

The annual service budget assumes 18 operating hours/day and 365 days/year:
30 trains/hour/direction for four peak hours, 12 for fourteen other hours.
That is **6.3072 million train-km/year**. At **8 kWh/train-km** for traction
and vehicle auxiliaries, plus **12 GWh/year** for twelve stations, the budget
is **62.4576 GWh/year**. An assumed delivered tariff of **US$0.12/kWh** makes
energy **US$7.495m/year**. This is a grid budget, not a measured traction
cycle. The annual O&M ledger adds US$10m fleet maintenance, US$6m civil,
station and overhead maintenance, US$4m control/operations staff, and US$3m
insurance/administration: **US$30.495m/year** in constant 2026 dollars.

The 30-year model books a **US$160m year-15** vehicle/traction/controls major
overhaul and **US$70m year-25** vehicle/civil/overhead renewal. At 4% real,
the annual O&M factor is 17.292; the reconciled present cost is **US$1,665.919m**
including installed capital. For a single planning load assumption of 40%
average use of the 276 normal places, annual carried travel would be
696.315 million passenger-km and whole-life present cost **US$0.138/passenger-km**.
Fare revenue, financing, wider economic benefits and modal demand are not
counted. Actual ridership changes the per-passenger figure, not the capital
ledger.

## Construction and local work

**Programme: 43 months from approved corridor definition to trial-operation
handover.** Month 0–6: surveys, land/utility agreements and detailed package
design. Month 6–24: groundworks, foundations and support piers. Month 8–31:
two precast yards make 6,000 beams at a combined 16 beams/workday (375 workdays
at 20 workdays/month). Month 15–35: two erection fronts place 16 beams/day
combined (375 workdays), with haul/access windows agreed in advance. Month
26–38: rail, protected access and overhead. Month 29–40: stations, depot,
power and controls. Month 40–43: integration, independent testing, training and
trial operation. The critical path is support access → beam erection →
rail/overhead → power and stopping integration → trials. The 43 months include
overlap and a three-month system-integration period, not an added blanket
programme contingency.

Applying the explicit local-work fractions in [basis.csv](basis.csv) gives
**US$410.828m**, or **48.2% of direct capital**, for an *assumed locally
executed work and supply budget*. This is not measured Iraqi value added:
imported motors, control electronics, rail and specialists may be embedded in
locally invoiced packages. Procurement should require bill-of-material origin,
fabrication/QA hours, tooling, training and repair capability for each major
assembly. The 20% risk contingency has no assumed local fraction.

## Cost control and next quotation

The controlled cost input is [basis.csv](basis.csv). `amount_usd_m` equals
`quantity × unit_rate_usd_m`, the fourteen scopes sum to US$1,023.4992m,
and the contingency is 20% of the other thirteen scopes. Read it with any CSV
tool; no specialist runtime or generated report is required. The calculation
can be repeated with:

```sh
awk -F, 'NR>1 { total += $6; if ($1 != "project-risk-contingency") direct += $6 } END { printf "direct=%.3f capital=%.4f\n", direct, total }' docs/reference-v07/cost/basis.csv
```

Before accepting a contractor price, obtain bids for the 51 powered sets and
spares; 6,000 beam/6,002 foundation packages on surveyed ground; station
structure and access; 60 track-km overhead/rail and six grid sites; depot;
and 30-year maintenance and renewals. Quote the same design, currency date,
scope boundaries, tax treatment and delivery months. A site with tunnelling,
river crossings, piling or extensive property takings is a new candidate and
needs its own quantity ledger. No physical qualification is asserted by this
planning cost calculation.
