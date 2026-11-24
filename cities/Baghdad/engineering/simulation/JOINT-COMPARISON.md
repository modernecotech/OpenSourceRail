# Which choices change the service and the price?

This worked comparison uses the issued 12 km line to test what changes when train length, frequency, power supply and viaduct span vary together. The 36 crossed combinations use one hourly passenger demand matrix, a level alignment, 40°C air, 18 service hours and the same six stations with 125 m platforms. Ten further checks change the outage, heat and demand, or body material. A new corridor needs its own requirements.

## Choose the service offer first

The steel formation here carries 350 or 700 normal planning places. The diagram includes full-tail release and terminal occupation. Retiming the 20-minute service uses a ten-minute departure offset at the second terminal. Three reserve sets are a retained procurement assumption. The protected conductor supplies moving trains continuously. Emergency power and braking have separate open requirements.

| Cars | Interval (min) | Places/h/direction | Active + reserve sets | Assisted dwell (s) | Journeys completed/day | Left at close/day¹ | Grid kWh/train-km | Priced capital ($m) | Annual operation ($m) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 15 | 1,400 | 3 + 3 | 35 | 10,977.5 | 23.1 | 3.16 | 780.88 | 10.30 |
| 3 | 20 | 1,050 | 3 + 3 | 35 | 10,965.1 | 35.4 | 3.87 | 780.88 | 10.13 |
| 3 | 30 | 700 | 2 + 3 | 39 | 10,948.4 | 52.1 | 4.28 | 774.13 | 9.91 |
| 6 | 15 | 2,800 | 3 + 3 | 35 | 10,977.4 | 23.2 | 5.40 | 807.86 | 10.43 |
| 6 | 20 | 2,100 | 3 + 3 | 35 | 10,965.2 | 35.4 | 6.38 | 807.86 | 10.24 |
| 6 | 30 | 1,400 | 2 + 3 | 35 | 10,948.3 | 52.2 | 6.77 | 796.62 | 9.98 |

¹ All six rows use the six-site paired supply and 10 m box. Demand is 11,000.6 journeys per day. The closing balance includes arrivals after the last boarding opportunity, queues left by full trains and incomplete trips. Three cars every 15 minutes and six every 30 minutes both offer 1,400 places/h/direction. The shorter interval halves the assumed random-arrival wait from 15 to 7.5 minutes. The three-car offer costs $15.74m less to open and $0.31m more per year to operate. It carries 29 more journeys per day. An operator must specify the acceptable wait, load and coverage before comparing prices.

## What a power bid can change

At six cars every 15 minutes the two supply options complete 144 workings each. The radial and paired cases carry 10,977.405 and 10,977.405 journeys per day respectively. Moving from 30 radial sites to six paired sites changes priced capital by −$316.46m and ordinary annual operating expense by −$1.67m. Both retain the published train and route quantities on this comparison.

Across all 18 matched timetable, formation and span pairs, the absolute opening-price difference between the two supplies ranges from $316.457m to $316.457m. These fixed enquiry prices contain no new conductor or rectifier sizing for a lighter train. The duty model does respond to a lighter or less frequent train. A supplier can price its revised duty and renewal schedule against the resulting envelope.

18 of the 18 normal supply pairs deliver matching simulated service at the stated numerical tolerance of 0.00001 daily journeys. Their duty and current envelopes can inform competing supplier enquiries. At six cars every 15 minutes the difference in gross priced 30-year present value is $406.87m. At 4% real discount from the study origin, an additional constant $26.47m per operating year from year 4 would consume that entire priced difference. Alternatively discount a supplier's actual extra installation, protection, renewals, downtime and upkeep at their due dates. Use the difference once. The paired renewal programme is open and its parent radial scopes have been removed. The break-even figure is a budget for unresolved **net** costs, conditional on meeting the same safety, reliability and service requirements.

| Combined site and feed-path outage, 15 min | Cars | Passenger workings completed / booked | Completed journeys/day | Lowest collector V on energized movements | Peak site current (kA) |
|---|---:|---:|---:|---:|---:|
| paired6 | 3 | 144 / 144 | 10,977.5 | 1474.4 | 0.65 |
| radial30 | 3 | 0 / 144 | 0.0 | 1477.9 | 0.54 |
| paired6 | 6 | 144 / 144 | 10,977.4 | 1465.1 | 1.21 |
| radial30 | 6 | 0 / 144 | 0.0 | 1471.0 | 1.06 |

The outage is one prescribed site and path. Read voltage alongside service completion. The normal price uses ordinary operating energy. Protection coordination, thermal duty, evacuation and local grid evidence remain open for both layouts.

## Where the span comparison stops

| Span (m) | Supports / bearings on 12 km | Cage margin at 30% loss, 3 / 6 cars (kN) | 60 t lift allowance minus stock (t) | Priced opening using current civil proxy ($m)² |
|---:|---:|---:|---:|---:|
| 10 | 2,402 / 9,600 | +243 / +244 | +25.8 | 807.86 |
| 20 | 1,202 / 4,800 | -2,937 / -2,932 | -3.7 | 796.53 |
| 25 | 962 / 3,840 | -4,963 / -4,955 | -18.5 | 796.38 |

² This column uses six steel cars and the paired supply. The structural calculation moves the axles of each bounded train across the candidate span. The civil price model scales the parent allowance with span and support count. Once a cage or lift fails, a differently dimensioned section, support, foundation and construction method require a fresh takeoff. The price change shown here cannot be assigned to a redesigned U-girder. The service model has no span-dependent alignment or speed restriction for this straight corridor.

## Check heat, demand and materials

| Paired feed, upside demand at 48°C | Cars | Interval (min) | Completed journeys/day | Denied boarding attempts/day | Assisted dwell (s) | Trial cooling margin (kW thermal) |
|---|---:|---:|---:|---:|---:|---:|
| Steel | 3 | 15 | 20,004.2 | 0.0 | 38 | +1.3 |
| Steel | 3 | 30 | 19,951.5 | 92.7 | 53 | -59.3 |
| Steel | 6 | 15 | 20,004.2 | 0.0 | 35 | +71.7 |
| Steel | 6 | 30 | 19,950.9 | 0.0 | 38 | +2.7 |

The heat and demand changes occur together. Compare formations within this group. Denied attempts count people who could board a later departure. The 3-car, 30-minute trial clears its capacity backlog by closing time but fails the capacity screen during the day. A negative cooling margin requires a changed installed HVAC system, followed by a new auxiliary load, timetable and energy calculation.

| Three cars, 20 min, same paired supply and 10 m span | Loaded train (t) | Grid kWh/train-km | Capital ($m) | Annual operation ($m) |
|---|---:|---:|---:|---:|
| steel | 99.57 | 3.870 | 780.88 | 10.13 |
| aluminium | 96.63 | 3.814 | 786.95 | 10.12 |
| hybrid | 95.96 | 3.801 | 784.93 | 10.12 |

Mass is an installed planning estimate. Alternative joints, repair methods, supplier quotes and a formation-specific controls replay are outstanding. The capital column includes the price model's material premium. Longer life or reduced upkeep needs a priced and evidenced scope.

## Which decisions can this calculation support?

**Operating the declared duty.** 44 of 46 cases complete the booked workings while meeting the modeled voltage, isolation and block checks. The radial combined outages block two directional interstation movements. A voltage reading on an energized part of that line gives no assurance of a through trip. The paired case assumes the surviving ties can be configured safely. Protection settings, clearing times, conductor and rectifier thermal ratings, utility approval and evacuation each need their own evidence.

**Engineering the installed option.** The cage margin applies to the inherited box and tendon arrangement. A negative lifting margin eliminates that stock lift on the assumed chart. A positive stock margin still needs rigging, radius and ground checks. Compare a resized cage, lighter girder, segmental erection or different crane as a new physical option with its own priced operations. Footing pressure uses a trial site limit. Battery ageing, low adhesion and summer cooling margins identify specific redesign and retest work for the named duty. Changing a target requires an agreed operating envelope and demonstrated independent stopping and essential power.

**Setting the service brief.** 3 cases miss the study's one-minute lateness or capacity criterion. The capacity check includes complete workings and fewer than 0.1 denied attempts or passengers left by capacity at closing. The operator must set acceptable waiting, coverage and recovery before the service can be selected. For the 15-minute paired case, one spare set represents $5.09m of direct three-car fleet price or $8.48m for six cars. That gives the price exposure to the three-spare assumption. Any revised reserve needs a maintenance and recovery diagram and repriced depot, renewals and downtime.

**Qualification and cost.** Every case carries an open installed price and unapproved protection. The requirement policy has 6 mandatory criteria awaiting scoped limits or independently reviewed evidence. The modeled failed movements are observed numerical results for their stated duty. The project has no authenticated physical-limit rejection of an entire vehicle, supply or span family from this comparison. The JSON returns the named duty failures, numerical checks, trial margins, missing evidence and open cost scopes individually alongside the original integrated decision.

## Reproduce the comparison

The integrated evaluator returned 0 eligible selections in 46 evaluated cases. Each JSON row retains the physical and evaluation IDs, demand matrix identity, failures and open checks. Conditional prices remain available when an option fails.

```sh
python3 -m cities.Baghdad.engineering.simulation.decision_comparison --check
python3 -m cities.Baghdad.engineering.simulation.decision_comparison --json > build/joint-decisions.json
```

Comparison digest `5ba42d07664a18721e193fcc0d08dd2870fc1f9b9d95e66ffd474030110143af`. [Service, energy and price assumptions](SIMULATION.md) · [Factory and whole-life cost scope](production-guide.md) · [Redesigned girder and support families](../mechanical/civil/SPAN-FAMILIES.md)
