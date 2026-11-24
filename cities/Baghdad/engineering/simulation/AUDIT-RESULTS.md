# Railway assumption audit results

The original 12 km schematic falls 3.09 km short of the geographic minimum through five stops in order. The revised 17.46 km horizontal study includes 6.73 km of road reference and 10.74 km of proposed connections. Um Al Tubol still needs a site. Investment selection and first-article fabrication remain held.

## Which service can the terminal handle?

Each offer uses its own waiting-time demand and train diagram. The terminal search tests 30-second phase offsets. The moving replay includes depot movements, track reservations and actual station calls.

| Headway | Annual requested journeys | Initial diagram → revised conflicts | Terminal offset | Completed / booked trips on paired supply |
| --- | ---: | ---: | ---: | ---: |
| 15 min | 3,852,384 | 72 → 2 | 330 s | 103 / 144 |
| 20 min | 3,399,717 | 54 → 0 | 930 s | 84 / 108 |
| 30 min | 2,647,702 | 37 → 0 | 1308 s | 72 / 72 |

The detailed comparison uses the 30-minute offer with a 1308 s terminal offset and 210 s additional time for the first and last empty movements. The published 30-minute trial refines the offset at two-second intervals. Each changed service is replayed before it can be compared.

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

Use `--supply-return` with an exact feeder ID to check supplied peak and RMS current ratings, protection settings and fault duties. The assessment keeps missing equipment and site data open. [Return format and worked checks](test_audit_power_return.py)

## What changes the vehicle and civil enquiry?

The central and high loaded trains weigh 198.64 and 246.04 tonnes under the component allowances. The aged essential battery has a 8.8 kWh shortfall. The same duty requires 78.75 kWh nominal before additional hot-weather losses. Select brake hardware after measuring response, force and repeat duty against the protected stopping distance. [Vehicle and braking results](vehicle-audit-guide.md)

With wheel braking unavailable and one independent module out, the high-load 2% downhill trial needs 17.81 kN per remaining module for a 0.6 m/s² net stop. The 14.6 kN comparison gives a 495.7 m stopping distance including the two-second delay. Confirm force, heat and protected distance for the fitted arrangement.

The lowest base-rate 30-year civil quotation case is **20m U 1.55m / shared**. Its whole-stock allowance is $159.23m. There is a 0.91 m residual bay on each track. The workshop and cash accounts exclude design and installation of those closures. Verify the local transport plan, ground, load chart, bearing and prestress designs. [Civil comparison](../mechanical/civil/SPAN-FAMILIES.md)

## What could the revised supply cost?

These figures apply dated planning rates to the actual site count, track length, assumed switching and simulated current duty. Each figure covers rail-side plant and conductors. The buyer cash accounts below await scope-matched offers.

| Layout | Modelled rail-side subtotal, low / base / high | Annual upkeep sensitivity, low / base / high |
| --- | ---: | ---: |
| radial30 | $285.37m / $285.37m / $285.37m | $1.43m / $2.85m / $5.71m |
| paired6 | $138.95m / $176.70m / $225.81m | $0.69m / $1.77m / $4.52m |

Utility reinforcement, site-specific works, demonstrated protection and scheduled renewals require separate scope and prices. The radial layout also loses through service after a path outage. A price difference alone cannot establish a viable saving.

## What can a buyer price?

| Layout | Fleet sets | Operated / booked train-km per year | Partial capital | Partial 30-year PV |
| --- | ---: | ---: | ---: | ---: |
| radial30 | 6 | 472,167 / 472,167 | $616.87m | $722.84m |
| paired6 | 6 | 472,167 / 472,167 | $616.87m | $722.81m |

The radial30 workshop completes in the following modelled workdays. normal 449, delayed-material 490, reduced-capacity 772, rejected-first-article 501. The owner cash model retains unpriced delay exposures.

The paired6 workshop completes in the following modelled workdays. normal 449, delayed-material 490, reduced-capacity 772, rejected-first-article 501. The owner cash model retains unpriced delay exposures.

The radial30 ledger has 1 opening, 1 annual operation, 1 renewal lots without prices. The owner cash model lists separate unpriced risks.

The paired6 ledger has 1 opening, 1 annual operation, 1 renewal lots without prices. The owner cash model lists separate unpriced risks.

Annual figures extrapolate the modelled day. Match installed scope, service achieved, equipment duties, maintenance and replacements before comparing offers.

## What remains open for release?

| Work | Digital result | Evidence and review still needed |
| --- | --- | --- |
| A01 · Integration | Scoped input register and candidate joins | Review submitted replacements against their exact alignment, formation, equipment and lot scope. |
| A02 · Alignment | Horizontal distance and stop-order screen | Approve surveyed levels, curves, utility and land interfaces, and all station sites. |
| A03 · Passenger service | Fixed-demand control and service-sensitive working days | Authenticate local counts and travel times and calibrate demand response. |
| A04 · Braking | Stopping distance, failed-module force and heat bounds | Measure braking and wheel-slide duty and verify protected stopping distance and recovery. |
| A05 · Vehicle and interfaces | Loaded mass, axle, battery and fit screens | Weigh the equipped article and measure loaded door, suspension, removal and hot aged battery duty. |
| A06 · Electrical supply | Matched ordinary, hot and outage working days | Review equipment duty, protection clearing, return circuits, safe isolation and utility terms. |
| A07 · Civil and erection | Priced stock and erection comparison | Obtain ground and access data, signed lift chart, verified prestress, fatigue, shear, bearing and staged erection designs. |
| A08 · Production and procurement | Ordinary and disrupted workshop schedules | Return matched shop offers, measured process cycles and first-article inspection records. |
| A09 · Economics | Scoped capital and 30-year cash subtotals | Complete unpriced owner, installation and renewal scope and calibrate risk and funding terms. |
| A10 · Independent review and publication | Reproducible review with a native replay receipt for the published defaults | Run the exact edition in a clean installation and obtain independent physical review before release. |

## Reproduce or revise the comparison

[Download the published paired6 budgetary enquiry](audited-enquiry.zip) · [Independent SUMO and grid-side reproduction for the published 15- and 30-minute cases](audit-verification.json) · [Workshop, offers and cash scope](audit-production-guide.md)

The audit records 219 scoped input entries. Run `./osr design railway audit --check` to reproduce this report or `--json` to inspect each input, constraint and result. [Execution plan and acceptance tests](ASSUMPTION-AUDIT.md) · [Route and demand inputs](ALIGNMENT-DEMAND.md)

Evaluation `41800bcc7610a63bebaed2ce786fb828f270a1d5da4eebb7fe8d7749cf37c9ad`
