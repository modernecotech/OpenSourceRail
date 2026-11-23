# Baghdad opening operating alternatives

Compare six-car operation at four Airport departures per hour with two per hour and with the Yellow urban corridor at four per hour. Yellow is the first urban demand-survey priority because it shares named stops with the most other corridors. Named interchange opportunities give a survey priority. The actual urban loads and paid trips still need to be measured. [Urban and Airport opening comparison](airport-integration.html)

| Measure | Airport every 15 min | Airport every 30 min | Yellow every 15 min |
|---|---:|---:|---:|
| Route-km | 12 | 12 | 30 |
| Offered places per peak hour and direction | 2,800 | 1,400 | 2,800 |
| Passenger workings per day, both directions | 144 | 72 | 144 |
| Working sets / total with spares | 3 / 6 | 2 / 5 | 7 / 10 |
| Annual offered place-km, million | 441.50 | 220.75 | 1,103.76 |
| Common capital estimate | $624.51m | Open | $1,139.01m |
| Common annual operating estimate | $9.81m | Open | $17.52m |

The 15-minute Airport and Yellow prices use the same provisional corridor allowances and 2026 USD rates. The Airport capital here uses three provisional feed sites. The separately priced 30-site Airport prototype includes feeder upgrades and other case-specific scope. Yellow still needs surveyed terminal and depot arrangements, a route-specific electric supply and local installed bids. [Priced Airport prototype](engineering/prototype/README.md)

The 30-minute timetable reuses the Airport stops, run profiles, one face and one exclusive throat per end, one Airport depot and three spare sets. Its simulated full day clears the block and terminal occupation screen, including positioning and depot movements. The original operating evaluator stops because its payroll estimate exceeds the reduced mileage-based non-energy train operations budget. That evaluator keeps its cost hold. The separate sensitivity below holds that payroll and other fixed costs in the budget.

## Airport cost sensitivity

| Matched three-site planning scope, constant 2026 USD | Airport every 15 min | Airport every 30 min |
|---|---:|---:|
| Annual train-km including non-revenue allowance | 646,488 | 323,244 |
| Fleet purchase, direct | $50.88m | $42.40m |
| Capital including design, testing and project allowance | $624.51m | $613.27m |
| Central annual cost, half of train non-labour variable | $9.76m | $8.92m |
| Annual cost, all / none of train non-labour variable | $9.76m / $9.76m | $8.74m / $9.11m |
| Paid daily journeys to cover central annual cost, at the assumed $0.422 net receipt | 63,358 | 57,904 |

Buying five sets saves $11.24m on this capital basis after applying the same project allowances. Retaining all six sets preserves the $624.51m capital estimate. The nonfleet scopes, including depot, workshop, route and power installation, stay at the same allowance. The annual comparison holds the reference payroll at $1.99m and retains station, workshop and line upkeep costs. The central split assigns half of the remaining train non-labour allowance to mileage. Energy follows train-km at the same assumed cost per kilometre, including the same minimum non-revenue allowance. The 30-minute case saves $0.66m–$1.02m per year in this sensitivity while offering half as many places and departures. Metered traction and hotel loads, roster and contract rates, feeder design, local enabling works, renewal and funding remain open.

## Airport procurement basis

The published 30-site buyer estimate includes Iraqi site and offsite-feed allowances. Keep its 30 source groups, 116 outgoing breaker circuits, 58 ties, 24 protected track-km, six stations, twin-track viaduct and other fixed opening quantities in both cases. The sensitivity binds the archived service, opening and BOM to the dated buyer estimate. [Airport prototype](engineering/prototype/README.md) · [Buyer estimate](engineering/prototype/sourcing-estimate.json)

| Matched 30-site procurement scope, constant 2026 USD | Airport every 15 min | Airport every 30 min |
|---|---:|---:|
| Working / purchased sets | 3 / 6 | 2 / 5 |
| Capital with allowances | $1,124.32m | $1,113.08m |
| Capital retaining all six sets | $1,124.32m | $1,124.32m |
| Central annual operating cost | $13.09m | $12.25m |
| Annual operating cost, all / none of train non-labour variable | $13.09m / $13.09m | $12.07m / $12.43m |
| Paid daily journeys to cover central annual cost at the assumed net receipt | 84,952 | 79,496 |

The projected saving is $11.24m if a set is omitted and $0.66m–$1.03m per year under the mileage and maintenance sensitivity. Site and switch upkeep remains $3.33m per year within the fixed costs. The projection holds the fleet allowance at $8.48m per set, including embedded delivery, and carries route haulage as a fixed lot. Fabrication volume discounts, standalone freight, and spares and workshop contract changes need supplier returns. The lower-frequency service uses the current feeder and priced quantities as assumptions for cost comparison. Its hot circuit, protection, resilience and thermal performance require renewed checks against the new timetable. The original reduced-frequency payroll-envelope refusal remains in the operating comparison. Yellow's $1,139.01m estimate covers its generic comparison scope, with route-specific feeders, site work and financing still open.

| Illustrative passengers per hour on the peak load section in one direction | Spare Airport or Yellow places, every 15 min | Spare Airport places, every 30 min |
|---|---:|---:|
| 700 | 2,100 | 700 |
| 1,400 | 1,400 | 0 |
| 2,100 | 700 | −700 |

These equal load scenarios show the hourly capacity constraint. Compare time- and direction-specific passenger counts, paid journeys, loads after close departure groups, accessible circulation, waits and connections before adopting an operating offer. The table uses offered places. Actual crowding, reliable capacity, fare receipts and avoided road delay require field evidence. The shorter-formation option would need new vehicle, train-control, platform, fleet, civil and power calculations. This comparison varies frequency with the full six-car formation retained.

Generate the source-bound comparison, including the separate candidate/evaluation identities and the exact cost hold. Each case retains its own fleet and service metrics.

```sh
python3 -m cities.Baghdad.operating_alternatives > build/v08-operating-alternatives.json
python3 -m unittest cities.Baghdad.test_operating_alternatives
```
