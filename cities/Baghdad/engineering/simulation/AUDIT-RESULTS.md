# Railway assumption audit results

The original 12 km schematic falls 3.09 km short of the geographic minimum through five stops in order. The revised 17.46 km horizontal study includes 6.73 km of road reference and 10.74 km of proposed connections. Um Al Tubol still needs a site. Investment selection and first-article fabrication remain held.

## Which service can the terminal handle?

Requested journeys respond to changes in expected wait and in-vehicle time. The terminal search tests 30-second phase offsets. The moving replay includes depot movements, track reservations and actual station calls.

| Headway | Booked dwell | Normal places per train | Annual requested journeys | Initial diagram → trial conflicts | Terminal offset | Completed / booked trips on paired supply |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 15 min | 35 s | 700 | 3,852,384 | 72 → 2 | 330 s | 103 / 144 |
| 20 min | 35 s | 700 | 3,399,717 | 54 → 0 | 930 s | 84 / 108 |
| 30 min | 35 s | 700 | 2,647,702 | 37 → 0 | 1308 s | 72 / 72 |

The detailed comparison uses the 30-minute offer with a 1308 s terminal offset and 210 s additional time for the first and last empty movements. These terminal offsets apply to the evaluated offers.

The paired-supply replay gives these maximum arrival delays at each simulation step. 1 s step → 56 s delay, 2 s step → 58 s delay, 4 s step → 58 s delay.

## What happens when a feeder fails?

The two layouts use the same train, stops, demand, dwell and terminal phase. Voltages refer to live collectors. An isolated section can prevent service even when the remaining live collectors have adequate voltage.

| Feed layout | Working condition | Trips finished / booked | Minimum V | Peak site kA | Branch RMS bound kA |
| --- | --- | ---: | ---: | ---: | ---: |
| radial30 | normal | 72 / 72 | 1,485.9 | 1.16 | 0.12 |
| radial30 | hot | 72 / 72 | 1,484.5 | 1.16 | 0.12 |
| radial30 | site_out | 72 / 72 | 1,484.5 | 1.16 | 0.12 |
| radial30 | path_out | 0 / 72 | 1,489.8 | 0.83 | 0.06 |
| radial30 | combined | 0 / 72 | 1,473.6 | 0.88 | 0.07 |
| paired6 | normal | 72 / 72 | 1,492.3 | 1.24 | 0.12 |
| paired6 | hot | 72 / 72 | 1,491.7 | 1.24 | 0.12 |
| paired6 | site_out | 72 / 72 | 1,488.8 | 1.24 | 0.14 |
| paired6 | path_out | 72 / 72 | 1,491.3 | 1.24 | 0.12 |
| paired6 | combined | 72 / 72 | 1,469.9 | 1.32 | 0.15 |

The combined-outage stress replay uses the high installed-mass allocation, a 2% constant grade and the same passenger offer. It tests additional sites and lower conductor resistance on the same route. Peak currents are equipment enquiries. Protection clearing and conductor temperature still require equipment data.

| Stress layout | Trips finished / booked | Minimum live voltage | Peak site kA | Maximum arrival delay |
| --- | ---: | ---: | ---: | ---: |
| radial30 | 0 / 72 | 1466.3 V | 1.45 | No arrivals |
| paired6 | 72 / 72 | 1460.8 V | 2.07 | 58 s |
| paired8 | 72 / 72 | 1466.4 V | 2.05 | 58 s |
| paired6_heavy | 72 / 72 | 1463.4 V | 2.06 | 58 s |

Use `--supply-return` with the feeder ID to check peak and RMS current ratings, protection settings and fault duties. A returned resistance, heat capacity and thermal resistance allow a conservative temperature bound for each working day. A bound above the limit calls for a more detailed thermal trace or direct measurement. [Return format and worked checks](test_audit_power_return.py)

radial30 · **failed** across the evaluated conditions. Checks reporting failure include timetable, aged battery, traction adhesion. Checks awaiting evidence include returned equipment, protected stopping distance, installed door and suspension clearances.

paired6 · **failed** across the evaluated conditions. Checks reporting failure include aged battery, traction adhesion. Checks awaiting evidence include returned equipment, protected stopping distance, installed door and suspension clearances.

## What changes the vehicle and civil enquiry?

The central and high loaded trains weigh 198.64 and 246.04 tonnes under the component allowances. The aged essential battery shows a shortfall of 8.8 kWh. The same duty requires 78.75 kWh nominal before additional hot-weather losses. Select brake hardware after measuring response, force and repeat duty against the protected stopping distance. [Vehicle and braking results](vehicle-audit-guide.md)

With wheel braking unavailable and one independent module out, the high-load 2% downhill trial needs 17.81 kN per remaining module for a 0.6 m/s² net stop. The 14.6 kN comparison gives a 495.7 m stopping distance including the two-second delay. Confirm force, heat and protected distance for the fitted arrangement.

At high load on the 2% upgrade, the declared drive with its heaviest powered axle unavailable has -0.64 kN of static adhesion margin at the assumed coefficient 0.1. This compares the available wheel force with the acceleration and margin requested for that duty.

At the assessed hot capacity factors, the required nominal battery capacities are 78.75 kWh at 100%, 87.50 kWh at 90%, 98.44 kWh at 80%. A supplier must establish the applicable capacity factor and peak discharge rating.

The lowest base-rate 30-year civil quotation case is **20m U 1.55m / shared**. Its whole-stock allowance is $159.23m. There is a 0.91 m residual bay on each track. The workshop and cash accounts exclude design and installation of those closures. Verify the local transport plan, ground, load chart, bearing and prestress designs. [Civil comparison](../mechanical/civil/SPAN-FAMILIES.md)

The following high-load options cover 17.460 km of identical double-track scope. The remaining 0.91 m and site works need their own price. The haul and erection ceiling is the most each placement could cost to match the lowest modelled base 30-year present value, holding other rates fixed.

| Standard girder and piers | Placements | Hook demand at working radius | Base 30-year PV | Haul and erection ceiling per placement |
| --- | ---: | ---: | ---: | ---: |
| 10m U 1.15m / separate | 3,492 | 37.74 t at 12 m | $199.72m | Cannot match even with free haul and erection |
| 10m U 1.15m / shared | 3,492 | 37.74 t at 12 m | $197.81m | Cannot match even with free haul and erection |
| 15m U 1.32m / separate | 2,328 | 59.90 t at 12 m | $170.44m | $3,642 |
| 15m U 1.32m / shared | 2,328 | 59.90 t at 12 m | $168.27m | $4,574 |
| 20m U 1.55m / shared | 1,746 | 89.85 t at 12 m | $165.76m | $9,322 |

## What could the revised supply cost?

These figures apply dated planning rates to the actual site count, track length, assumed switching and simulated current duty. Each figure covers rail-side plant and conductors. The buyer cash accounts below await scope-matched offers.

| Layout | Modelled rail-side subtotal, low / base / high | Annual upkeep sensitivity, low / base / high |
| --- | ---: | ---: |
| radial30 | $285.37m / $285.37m / $285.37m | $1.43m / $2.85m / $5.71m |
| paired6 | $138.95m / $176.70m / $225.81m | $0.69m / $1.77m / $4.52m |

Utility reinforcement, site-specific works, demonstrated protection and scheduled renewals require separate scope and prices.

Service differs between the layouts under a feed-path outage, a combined site and path outage, the high-mass combined outage. Their priced subtotals cannot establish a break-even feeder price.

## What can a buyer price?

| Layout | Fleet sets | Operated / booked train-km per year | Partial capital | Partial 30-year PV |
| --- | ---: | ---: | ---: | ---: |
| radial30 | 6 | 472,167 / 472,167 | $616.87m | $722.84m |
| paired6 | 6 | 472,167 / 472,167 | $616.87m | $722.81m |

The radial30 workshop completes in the following modelled workdays. normal 449, delayed-material 490, reduced-capacity 772, rejected-first-article 501, 48h-mould-dwell 601. The owner cash model retains unpriced delay exposures.
Under reduced-capacity, service starts in project year 5. Moving the priced flows changes their base present value by $-23.24m. Delay claims and financing effects remain open.

The paired6 workshop completes in the following modelled workdays. normal 449, delayed-material 490, reduced-capacity 772, rejected-first-article 501, 48h-mould-dwell 601. The owner cash model retains unpriced delay exposures.
Under reduced-capacity, service starts in project year 5. Moving the priced flows changes their base present value by $-23.24m. Delay claims and financing effects remain open.

The radial30 ledger has 1 opening, 1 annual operation, 1 renewal lots without prices. The owner cash model lists separate unpriced risks.

The paired6 ledger has 1 opening, 1 annual operation, 1 renewal lots without prices. The owner cash model lists separate unpriced risks.

Annual figures extrapolate the modelled day. Match installed scope, service achieved, equipment duties, maintenance and replacements before comparing offers.

## What remains open for release?

| Work | Digital result | Evidence and review still needed |
| --- | --- | --- |
| A01 · Integration | Scoped input register and candidate joins | Review submitted replacements against their exact alignment, formation, equipment and lot scope. |
| A02 · Alignment | Horizontal distance and stop-order screen | Approve surveyed levels, curves, utility and land interfaces, and all station sites. |
| A03 · Passenger service | Service-sensitive working days | Authenticate local counts and travel times and calibrate demand response. |
| A04 · Braking | Stopping distance, failed-module force and heat bounds | Match the Airport train protection curve to measured brake response and wheel-slide duty. Survey the stopping limit and overlap, then verify recovery. |
| A05 · Vehicle and interfaces | Loaded mass, axle, battery and fit screens | Weigh the equipped article and measure loaded door, suspension, removal and hot aged battery duty. |
| A06 · Electrical supply | Matched ordinary, hot and outage working days | Confirm source and branch thermal response, protection clearing, return circuits, safe isolation and utility terms. |
| A07 · Civil and erection | Priced stock and erection comparison | Obtain ground and access data, signed lift chart, verified prestress, fatigue, shear, bearing and staged erection designs. |
| A08 · Production and procurement | Ordinary and disrupted workshop schedules | Return matched shop offers, measured process cycles and first-article inspection records. |
| A09 · Economics | Scoped capital and 30-year cash subtotals | Complete unpriced owner, installation and renewal scope and calibrate risk and funding terms. |
| A10 · Independent review and publication | Reproducible review with a native replay receipt for the published defaults | Run the exact edition in a clean installation and obtain independent physical review before release. |

## Reproduce or revise the comparison

[Six-site paired enquiry](audited-enquiry.zip) · [30-site radial enquiry](audited-enquiry-radial30.zip) · [Independent SUMO and grid-side reproduction for the published 15- and 30-minute cases](audit-verification.json) · [Workshop, offers and cash scope](audit-production-guide.md)

The audit records 357 scoped input entries. Run `./osr design railway audit --check` to reproduce this report or `--json` to inspect each input, constraint and result. [Execution plan and acceptance tests](ASSUMPTION-AUDIT.md) · [Route and demand inputs](ALIGNMENT-DEMAND.md)

Evaluation `ef2047b30ebbfec5c2b55a6fcda70091111fb68ca6a54c563c6d6c130ad42ec1`
