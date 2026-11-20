# Baghdad system cost and delivery

**OpenSourceRail digital planning estimate · 17 November 2026 · 2026 US dollars**

The [one candidate input file](system.toml) drives the [calculated result](system-results.json), the [city proposal](PROPOSAL.md) and the Workbench. It sets **zero tunnels, zero underground stations, two elevated tracks throughout**, a six-car 700-place train and protected conductor traction. It couples supply equipment, traction battery, train mass, civil quantities, grid energy, capital, maintenance and renewals. The 605.652 km citywide network is an independent alternative with its own routes, stations, fleet and capital.

| Quantity | Seven-corridor alternative | Independent citywide |
|---|---:|---:|
| Costed guideway / stations budgeted | 148.2 km / 64 | 605.652 km / 280 |
| Guideway with assigned passenger paths | 148.2 km | 555.553 km; 50.099 km reserved without a train path |
| Active trains / full fleet | 210 / 242 | 812 / 934 |
| Depots / control centres / grid sites | 4 / 2 / 30 | 12 / 4 / 100 |
| Two-track elevated beams, 10 m family | 29,640 | 121,156 |
| Separate support/foundation positions | 29,654 | 121,208 |
| Protected conductor | 296.4 track-km | 1,211.304 track-km |
| Annual train distance, declared hourly service offer | 24.666 million km | 92.466 million km |
| Annual delivered grid energy | 524.313 GWh | 1,965.477 GWh |
| **Installed capital** | **$7,865.670m** | **$31,017.749m** |
| Annual operations, energy and maintenance | $196.978m | $780.495m |
| **30-year present cost, 4% real** | **$12,020.636m** | **$47,393.819m** |

These are single point estimates at declared rates. They include a 20% project allowance and are designed for matched option comparison and initial procurement planning. They are not supplier bids, debt commitments or a measured construction alignment.

The drawn first-programme lines total **138.395 km**, while the priced RFI control is **148.2 km**. The citywide map draws **608.460 km**; its 26 physical sections are normalized to the **605.652 km** cost control. The difference is a planning length adjustment, not surveyed track. Six citywide sections (**B-X01–B-X05 and B-I03**, 50.099 km of normalized guideway) are costed as **reserved non-revenue corridors** without assigned train paths. The other **555.553 km** has passenger-path assignments in the 14 service groups. The [station screen register](station-register.json) records 37 mapped first-network access points and 220 citywide stop screens against 64 and 280 station allowances. The 934-train fleet and hourly operating offer are planning assumptions; they do not operate the reserved sections or define stop sequences and junction movements.

The [daily train diagrams](SERVICE-DIAGRAMS.md) account for the entire first-network mileage in the operating estimate. Citywide, 51.967 million annual train-km have timed paths and 40.499 million are still allowed for four unresolved groups. The [workforce calculator](../../docs/operator-review/delivery/README.md) can replace embedded payroll with priced duties for unattended operation or onboard assistance once the operator identifies its existing labour allowances.


The Airport opening takes off a six-stop railway with dedicated facilities at **$793.177m** plus site and terminal works still to price. The citywide mainline operating option defers passenger service on five short access sections. At 91.968 million annual train-km it costs **$777.932m/year** under the existing rates and full capital scope, versus **$780.495m/year** for the full budgeted service. Wages, surveyed designs and supplier prices are inputs for the next estimate. [Airport opening](AIRPORT-OPENING.md) · [Citywide service and staffing](SERVICE-DIAGRAMS.md#a-citywide-timetable-with-five-access-sections-deferred)

## Fourteen installed capital scopes

US$ million, computed by `python3 -m engineering.outline.baghdad_system --write-results` from `system.toml`.

| Scope | First | Independent citywide |
|---|---:|---:|
| Elevated viaduct, piers and foundations | 1,331.238 | 5,440.396 |
| Accessible stations | 832.000 | 3,640.000 |
| Track, fastenings and maintenance walkways | 237.120 | 969.043 |
| Signalling and communications | 177.840 | 726.782 |
| Wayside braking, protection and recovery | 88.920 | 363.391 |
| Protected conductor and sectionalisation | 316.920 | 1,298.469 |
| Grid supply and charging equipment | 240.000 | 800.000 |
| Vehicle fleet | 2,052.160 | 7,920.320 |
| Depots and control centres | 260.000 | 740.000 |
| Land, utilities and construction disruption | 296.400 | 1,211.304 |
| Tooling, recovery and local production setup | 99.280 | 282.261 |
| Design and assurance, 8% of direct | 474.550 | 1,871.357 |
| Testing and commissioning, 2.5% of direct | 148.297 | 584.799 |
| Project allowance, 20% of subtotal | 1,310.945 | 5,169.625 |
| **Installed total** | **7,865.670** | **31,017.749** |

Direct viaduct cost starts with $9m/route-km for the 10 m separate-track family and applies the train-mass-linked structural quantity factor in the [civil evaluator](../../engineering/outline/baghdad_viaduct.py). The first network's 29,640 beams and 29,654 positions count both tracks and line ends; guideway, drainage and foundations are included in that scope. Each other scope's rate and quantity rule is in the input file and calculator, including $13m/station, $8m/grid site and $8.48m/selected trainset. Revenue, debt, tax, foreign exchange and financing fees are separate from this engineering capital estimate.

### Reserved citywide guideway

The 50.099 km reserve accounts for **10,026 beams** and **10,038 support positions** in the 10 m separate-support case. The model assigns **$845.811m** of direct capital to these sections, including civil works, track and walkway, conductor, provisions for signalling and recovery, land and utilities, and the route-based part of tooling and recovery. Design, testing and risk allowances bring the allocation to **$1,121.545m within the $31,017.749m total**. Conductor upkeep on the reserve accounts for **$2.004m/year**. The rest of the estimate includes network-wide assets such as fleet, stations, grid sites and section switches. Deciding whether to build or defer the reserve would require a new network design and estimate.

The citywide total represents **$51.214m per costed guideway kilometre** and **$55.832m per kilometre with an assigned passenger path**. Both ratios use the full installed capital numerator. The seven-corridor estimate has no reserve and uses the same length in both ratios. The [calculated result](system-results.json) reconciles the allocation and the remaining capital.

### Control equipment within the estimate

The [control equipment schedule](../../control-electronics/README.md) counts
protection, radios, car and door controllers, brake controllers, station
dispatch, section gateways, grid protection and control-room equipment. These
planning amounts are **inside** the capital scopes above; they are not
additional costs.

| Parent capital scope and equipment allocation, US$ million | First | Independent citywide |
|---|---:|---:|
| Vehicle fleet electronics | 75.020 | 289.540 |
| Station dispatch controllers | 7.680 | 33.600 |
| Signalling, train detection and section control | 14.136 | 59.092 |
| Grid protection gateways | 4.500 | 15.000 |
| Control-room equipment | 1.200 | 2.400 |
| **Total already included in capital** | **102.536** | **399.632** |

The unit allowances and fleet, station, section and grid quantities are in
`system.toml`; the calculated allocation is in `system-results.json`. Equipment
suppliers can quote each assembly against the [train and platform interfaces](VEHICLE.md).

## Matched power options

All cases keep the same declared route length, hourly service offer, passenger capacity, grade and adhesion assumptions. Their power equipment, mass, civil quantities, energy and renewal costs change together. Protected conductor is the lowest **30-year present cost under the stated planning rates**. Its advantage over overhead is $52.288m for the first programme and $202.307m for the independent citywide network, about 0.43% of each total. Increasing only the protected-conductor equipment allowance by $0.124m/track-km (first) or $0.118m/track-km (citywide) removes that advantage. A 20% conductor equipment rate increase reverses the modeled ranking in both networks. The [calculated sensitivity](system-results.json) also varies maintenance, losses and renewal cost. These are planning price screens, not supplier quotations or a proven procurement choice.

| Traction supply | First capital | First 30-year | Complete capital | Complete 30-year |
|---|---:|---:|---:|---:|
| Protected conductor, selected | **$7.866bn** | **$12.021bn** | **$31.018bn** | **$47.394bn** |
| Station battery and charging | $8.201bn | $12.703bn | $32.126bn | $49.717bn |
| Limited conductor plus battery | $7.828bn | $12.080bn | $30.882bn | $47.575bn |
| Overhead contact supply, comparator | $7.927bn | $12.073bn | $31.262bn | $47.596bn |

Protected conductor runs along both tracks. Its selected crowd train is **201.092 t** and has no traction battery. All options require 24 driven axles under the declared 0.10 low-adhesion coefficient, 2% adverse grade, 0.6 m/s² acceleration, resistance and traction margin. Station battery needs about **467 kWh/train**, 128 charging ports at **5.97 MW each** and about 14.9 MWh stationary buffer in the first network. Uncoordinated simultaneous charging is outside the provisional site power allocation, so its timetable must sequence charging. Limited conductor uses 25% of route length and about 311 kWh/train. The overhead case is a financial comparator with 1.5 kV DC wires. These are digital sizing results, with sectional isolation, touch protection and emergency access included as requirements for conductor rail.

For the selected conductor train, a **1.5 kV evaluation voltage** gives a 3.336 kA one-train current request at the declared traction duty; at 90% of that voltage it is 3.707 kA, or 7.413 kA for two coincident trains. The [electrical screen](system-results.json) also gives 31.459 GWh/year and 117.929 GWh/year of grid-chain losses for the two service allowances. This voltage is a calculation setting, not an installed conductor or feeder selection. Section ratings, feeder and return impedance, voltage drop, fault clearing, touch protection and thermal duty require a physical electrical design. The independent 65 kWh service battery has 52 kWh declared usable against 50.4 kWh required with reserve; hot-weather and aging limits are not established by that small arithmetic margin.

Annual operation includes $2.60/non-energy train-km, $1m/station-year, delivered power at $0.12/kWh and option-specific maintenance. The declared 06:00–24:00 offer runs four hours at 24, eight at 12 and six at 6 trains/hour/direction per passenger service group. This is 228 departures per group and direction daily, with three minutes allowed at each terminal. The electrical peak-to-mean frequency factor is 1.895, covered by a 1.9 planning grid factor. The reserved 50.099 km carries no service. Intermediate stop dwells, junction paths, depot movements and demand are not represented. The 30-year real present cost discounts yearly operation at 4% and includes power-equipment, line-equipment, common systems and fleet renewal events. The [machine-readable result](system-results.json) itemises the year and cost of each renewal.

## Viaduct and construction

The selected 10 m family holds the existing repeatable reference geometry as a **digital cost control**. The comparison below changes only span length and support family for the same first-network train and route. Longer spans reduce placements and foundations in the planning arithmetic, but their lift weights and structural demands differ. Their lower indicative totals are not interchangeable with the selected structural family.

| Span and support family | Beams | Foundations | Indicative installed system capital | Beam hook-mass surrogate |
|---|---:|---:|---:|---:|
| **10 m, separate supports** | **29,640** | **29,654** | **$7.866bn** | **37.3 t** |
| 10 m, common pier | 29,640 | 14,827 | $7.944bn | 37.3 t |
| 20 m, separate supports | 14,820 | 14,834 | $7.709bn | 74.7 t |
| 20 m, common pier | 14,820 | 7,417 | $7.748bn | 74.7 t |
| 25 m, separate supports | 11,856 | 11,870 | $7.678bn | 93.3 t |
| 25 m, common pier | 11,856 | 5,935 | $7.709bn | 93.3 t |
| 30 m, separate supports | 9,886 | 9,900 | $7.657bn | 112.0 t |
| 30 m, common pier | 9,886 | 4,950 | $7.683bn | 112.0 t |

The 20–30 m hook loads exceed the 60 t reference lift control. They require a different crane arrangement and span structure, so their cost rows are value-engineering screens rather than selected build quantities. A same-section, uniform-load screen now shows bending demand rising with span length squared and deflection demand with length to the fourth power; it is not a moving-train structural design. Pier design must account for loads, bearings, crossheads, segment joints, utilities, road clearance, flood/ground conditions, erection stability and evacuation walkway. The current open-GIS maps do not establish those site quantities. At eight beams or lifts per productive day and 250 nominal workdays per year, the 2028–2030 civil window needs **five yards and five fronts only with no ramp or downtime**; 2028–2034 needs **nine of each** on that basis. The [monthly casting, release and erection schedule](system-results.json) applies an 80% first-year ramp, 90% later availability and a one-month curing/inspection/transport release lag. It closes the declared beam counts within the stated windows with **six yards and six fronts** for 29,640 first-network beams and **ten of each** for 121,156 citywide beams. Access and road-closure calendars are not in the schedule. Added facility and shift costs remain unpriced rather than zero.

The [matched quotation return](BUYER-COMPARISON.md#compare-a-matched-cash-return) links first-article stock, beam, platform and yard quantities to the seven-corridor estimate. Buyers can replace a matched fleet, station or civil allowance and trace the resulting design, commissioning and project percentages. A partial article retains an open installed cost until the remaining scope is priced.

## Construction timing and financing basis

| Planning milestone | Seven-corridor alternative | Independent citywide |
|---|---|---|
| Start of programme | 2027 | 2027 |
| Rights, utility coordination, fabrication setup | 2027–2028 | 2027–2029 |
| Parallel civil, stations, electrical and vehicle production | 2028–2030 | 2028–2034 |
| Systems integration and staged opening | 2030–2031 | 2031–2035 |
| Target completion | 2031 | 2035 |
| Average annual installed capital across programme | $1.573bn/year over five years | $3.446bn/year over nine years |

### Annual construction capital draw

The following allocation turns each independently selected installed capital total into a planning cash schedule. Figures are US$ million in 2026 prices. Neither alternative assumes that the other is built.

| Year | Seven-corridor alternative | Independent citywide alternative |
|---|---:|---:|
| 2027 | 393.284 | 930.532 |
| 2028 | 1,179.851 | 2,171.242 |
| 2029 | 2,359.701 | 3,101.775 |
| 2030 | 2,359.701 | 4,032.307 |
| 2031 | 1,573.133 | 4,652.662 |
| 2032 | 0 | 5,273.017 |
| 2033 | 0 | 4,652.662 |
| 2034 | 0 | 3,722.130 |
| 2035 | 0 | 2,481.422 |
| **Total** | **7,865.670** | **31,017.749** |

The first programme is allocated 5%, 15%, 30%, 30% and 20% over 2027–2031. The independent citywide network is allocated 3%, 7%, 10%, 13%, 15%, 17%, 15%, 12% and 8% over 2027–2035. These are cash planning weights, not contracts or a claim that finance has been raised. Interest during construction, lender fees, UKEF premium, exchange effects and any operating support are outside installed capital and require agreed financing terms.

The [calculated cash-flow view](system-results.json) discounts each annual capital draw to the start of **2027** at the same 4% real comparison rate. This makes capital present cost **$7,151.919m** for seven corridors and **$26,100.617m** citywide. If full operation begins only after each programme finishes, and the same 30-year operation and renewal stream then follows, the corresponding **2027 present cost** is **$10,566.998m** and **$37,606.227m**. These figures use different time origins from the headline $12,020.636m and $47,393.819m 30-year comparisons, which place installed capital at the start of full service. They do not represent savings or financing offers. Staged openings, interest, debt repayment, premiums, exchange and revenue remain outside this view.

The independent citywide programme requires overlapping construction fronts and an average of about 67 route-km/year across nine years. Its map includes through-service airport, Sadr City and Jadriya access sections. Actual land rights, station access, road and river interfaces, utility relocation, supply contracts and finance draw dates require project-specific agreements. Funding can combine Iraqi public capital, commercial lending and export finance for eligible imported packages. [UKEF Buyer Credit](https://www.gov.uk/guidance/buyer-credit-facility) depends on a specific eligible export contract, bank and borrower; the model does not assume a UKEF commitment.

## Local production and design rights

The independent citywide estimate allocates **US$282.261m** to tooling, recovery and local-production setup. At the declared procurement planning fractions in [the model](system.toml), **US$12,599.029m** of its **US$25,848.124m** capital before the project allowance is addressable by Iraqi contracts. The 20% project allowance is not assigned a country of origin. These are target contract values already included in the **US$31,017.749m** capital total, not extra investment or a forecast cash saving.

| Locally addressable package | Planning value, US$ million |
|---|---:|
| Viaduct and foundations | 3,808.277 |
| Vehicles and local assembly | 2,772.112 |
| Stations | 2,184.000 |
| Land, utilities and disruption | 847.913 |
| Design and assurance | 748.543 |
| Depots and control centres | 444.000 |
| Track and walkways | 436.069 |
| Power, protection and signalling | 912.499 |
| Tooling and commissioning | 445.615 |
| **Total planning Iraqi contract opportunity** | **12,599.029** |

Contract packages should give an Iraqi public design custodian and participating factories editable drawings, CAD, parts lists, control source, tooling and repair information, plus perpetual rights to make, modify and re-procure under the applicable [OpenSourceRail licences](../../LICENSE.md). Newly funded design rights and any supplier background royalties must be settled in each tender. Third-party mapping and component rights remain separate. The capital estimate makes no speculative royalty-savings deduction.

The open GIS geometry fixes a planning envelope, not a surveyed route. The airport marker is in the terminal area, not the passenger entrance; route lengths are declared network controls. The calculations can be rerun when route geometry, sites or supplier rates are set. No physical prototype or site survey is represented in this release.

## Debt and buyer affordability

The [financing comparison](PROPOSAL.md#what-the-city-would-need-to-pay) follows these construction draws through 30 operating years. Rebuild its [annual schedules](financing-scenarios.json) with `python3 cities/Baghdad/financing.py`. The [procurement schedule](BUYER-COMPARISON.md) defines the cash, financed and local-production returns for vendor comparison.
