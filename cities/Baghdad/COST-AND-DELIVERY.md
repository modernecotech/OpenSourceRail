# Baghdad system cost and delivery

**OpenSourceRail digital planning estimate · 17 November 2026 · 2026 US dollars**

The [one candidate input file](system.toml) drives the [calculated result](system-results.json), the [city proposal](PROPOSAL.md) and the Workbench. It sets **zero tunnels, zero underground stations, two elevated tracks throughout**, a six-car 700-place train and protected conductor traction. It couples supply equipment, traction battery, train mass, civil quantities, grid energy, capital, maintenance and renewals. The 605.652 km total includes the 148.2 km first programme.

| Quantity | First programme | Complete network |
|---|---:|---:|
| Route length / stations | 148.2 km / 64 | 605.652 km / 280 |
| Active trains / full fleet | 210 / 242 | 812 / 934 |
| Depots / control centres / grid sites | 4 / 2 / 30 | 12 / 4 / 100 |
| Two-track elevated beams, 10 m family | 29,640 | 121,156 |
| Separate support/foundation positions | 29,654 | 121,208 |
| Protected conductor | 296.4 track-km | 1,211.304 track-km |
| Annual train distance | 52.429 million km | 202.724 million km |
| Annual delivered grid energy | 1,114.4 GWh | 4,309.1 GWh |
| **Installed capital** | **$7,865.670m** | **$31,017.749m** |
| Annual operations, energy and maintenance | $339.974m | $1,348.404m |
| **30-year present cost, 4% real** | **$14,493.325m** | **$57,214.119m** |

These are single point estimates at declared rates. They include a 20% project allowance and are designed for matched option comparison and initial procurement planning. They are not supplier bids, debt commitments or a measured construction alignment.

## Fourteen installed capital scopes

US$ million, computed by `python3 -m engineering.outline.baghdad_system --write-results` from `system.toml`.

| Scope | First | Complete network |
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

## Matched power options

All cases keep the same route length, timetable, passenger capacity, grade and adhesion assumptions. Their power equipment, mass, civil quantities, energy and renewal costs change together. The lowest **30-year present cost** is the protected conductor candidate. The difference from overhead is modest, so procurement prices and electrical access engineering have a direct effect on the choice.

| Traction supply | First capital | First 30-year | Complete capital | Complete 30-year |
|---|---:|---:|---:|---:|
| Protected conductor, selected | **$7.866bn** | **$14.493bn** | **$31.018bn** | **$57.214bn** |
| Station battery and charging | $8.201bn | $15.238bn | $32.169bn | $59.832bn |
| Limited conductor plus battery | $7.828bn | $14.612bn | $30.923bn | $57.679bn |
| Overhead contact supply, comparator | $7.927bn | $14.560bn | $31.262bn | $57.473bn |

Protected conductor runs along both tracks. Its selected crowd train is **201.092 t** and has no traction battery. All options require 24 driven axles under the declared 0.10 low-adhesion coefficient, 2% adverse grade, 0.6 m/s² acceleration, resistance and traction margin. Station battery needs about **467 kWh/train**, 128 charging ports at **5.97 MW each** and about 14.9 MWh stationary buffer in the first network. Uncoordinated simultaneous charging is outside the provisional site power allocation, so its timetable must sequence charging. Limited conductor uses 25% of route length and about 311 kWh/train. The overhead case is a financial comparator with 1.5 kV DC wires. These are digital sizing results, with sectional isolation, touch protection and emergency access included as requirements for conductor rail.

Annual operation includes $2.60/non-energy train-km, $1m/station-year, delivered power at $0.12/kWh and option-specific maintenance. The 30-year real present cost discounts yearly operation at 4% and includes power-equipment, line-equipment, common systems and fleet renewal events. The [machine-readable result](system-results.json) itemises the year and cost of each renewal.

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

The 20–30 m hook loads exceed the 60 t reference lift control. They require a different crane arrangement and span structure, so their cost rows are value-engineering screens rather than selected build quantities. Pier design must account for loads, bearings, crossheads, segment joints, utilities, road clearance, flood/ground conditions, erection stability and evacuation walkway. The current open-GIS maps do not establish those site quantities. The 10 m digital production plan uses three casting yards and three erection fronts for 148.2 km in five years; the complete network needs seven of each over nine years at eight beams/day per yard and eight lifts/day per front, 250 workdays/year.

## Construction timing and financing basis

| Planning milestone | First programme | Complete network |
|---|---|---|
| Start of programme | 2027 | 2027 |
| Rights, utility coordination, fabrication setup | 2027–2028 | 2027–2029 |
| Parallel civil, stations, electrical and vehicle production | 2028–2030 | 2028–2034 |
| Systems integration and staged opening | 2030–2031 | 2031–2035 |
| Complete network target | 2031 | 2035 |
| Average annual installed capital across programme | $1.573bn/year over five years | $3.446bn/year over nine years |

The full network requires overlapping fronts and approximately 57 additional route-km/year during 2028–2035 beyond the first programme. This schedule is a construction-capacity calculation, with staged openings. Actual land rights, station access, road and river interfaces, utility relocation, supply contracts and finance draw dates need project-specific agreements. The full capital total implies **$23.152bn** of additional works after the first programme, not another $31.018bn. Funding can combine Iraqi public capital, commercial lending and export finance for eligible imported packages. [UKEF Buyer Credit](https://www.gov.uk/guidance/buyer-credit-facility) depends on a specific eligible export contract, bank and borrower; the model does not assume a UKEF commitment.

The open GIS geometry fixes a planning envelope, not a surveyed route. The airport marker is in the terminal area, not the passenger entrance; the map lengths are declared network controls. The calculation can be rerun when the route geometry, sites or supplier rates are set, and rejects changes to its pinned source maps until their identities and dependent calculations are updated. No physical prototype or site survey is represented in this release.
