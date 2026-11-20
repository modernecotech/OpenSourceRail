# Baghdad passenger service and train workings

[Open the timetable card](service-diagrams.html) to follow a train out and back, inspect a passenger transfer or see why a route is on hold. The two networks use independent fleets. The times support an operator workshop. Dispatch requires an approved alignment, stopping plan, safe separation, turnback design and operating rules.

| Planning-day measure | Seven corridors | Independent citywide network |
|---|---:|---:|
| Groups with connected train workings | 7 of 7 | 10 of 14 |
| Diagrammed one-way trips per day, both directions | 3,192 | 4,560 |
| Annual train-km assigned to timed trips | 24,666,408 | 51,966,824 |
| Annual train-km included in the operating budget with paths on hold | 0 | 40,499,371 |
| Sets in connected diagrams | 208 | 423 |
| Additional sets in the peak cycle allowance for paths on hold | 0 | 319 |
| Budgeted active / total fleet | 210 / 242 | 812 / 934 |
| Annual train-km in the operating cost ledger | 24,666,408 | 92,466,195 |

The first-network diagrams reproduce the service distance underlying the $196.978m annual operating estimate. Only 56.2% of the larger network's annual service distance has a connected diagram. Its $780.495m operating estimate includes the four unresolved groups. Both budgets exclude empty depot trips. The citywide reserve of 50.099 km carries no passenger service in either calculation. [System cost results](system-results.json) · [Diagram quantities and holds](service-diagrams.json)

## A citywide timetable with five access sections deferred

Select **Citywide option · Five access sections deferred** on the timetable card. Trains run along all fourteen mapped main routes, including the M05 airport extension. M01, M02 and M04 reverse at their mapped end stations. M09 runs in both directions around the ring. Each ring set stays in its direction, with a three-minute minimum layover at M-134 after each lap. All 26 registered ring stops receive service. The ten other groups use the same workings as the full citywide comparison.

| Group | Operating path | One way or lap | Diagrammed sets | Access section deferred |
|---|---|---:|---:|---|
| M01 | M-001 to M-017 | 48.865 km | 65 | B-A05, 0.499 km to Jadriya west |
| M02 | M-032 to M-045 | 52.588 km | 69 | B-A06, 1.382 km to Jadriya east |
| M04 | M-062 to M-073 | 41.697 km | 56 | B-A02 and B-A03, 0.999 km of mapped Sadr City approaches |
| M09 | One lap from M-134 back to M-134 | 97.187 km | 112 | B-A04, 0.111 km toward Sadr City east |

At the same hourly frequencies this option diagrams **6,384 trips per day, 725 sets and 91,968,471 train-km per year**. Five access sections account for a further 497,724 train-km in the selected budget. The 50.099 km of previously identified reserves remain separate. The $780.495m operating estimate covers the original offer. The mainline option gives **$777.932m per year** at the same per-kilometre energy and non-energy operating rates, keeping all stations, fleet and built track upkeep. Depot positioning, staff relief, actual section power duty and access to the five deferred branches still need operator and supplier evidence. The [workforce planner](../../docs/operator-review/delivery/index.html) prices these service hours and the [finance planner](../../docs/operator-review/finance/index.html?network=metropolitan&operation=metropolitan-mainlines) retains the full citywide capital and renewal programme.

On M04 the straight-line gaps to line-4 exceed the lengths of the two access sections themselves. On M01, M02 and M09 the branch junctions touch the schematic main lines. Establish platform sites, access needs and turnouts before comparing feeder trains, accessible walking connections or through services. The opening option leaves those passenger connections unassigned.

## One train through an ordinary morning

Airport-001 leaves the airport area at 06:00:00, calls at Al Amiriya from 06:03:19 to 06:03:54 and reaches Al Qadisiya at 06:18:57. It leaves for the airport at 06:21:57 after its three-minute turn. It reaches the airport at 06:40:54 and takes another outward trip at 06:50:00. The airport entrance and the location of Um Al Tubol on this route require agreement. At Al Amiriya, the first outward trip could connect with White-T002 at 06:14:07 if a five-minute accessible walk is achievable. That leaves 5 min 48 s to wait after the assumed walk.

Each group offers 228 departures **per direction** across the 18-hour service day. The 150-second peak interval offers 16,800 normal places per hour per direction at 700 places per train. Passenger counts, boarding distribution and seasonal demand remain open. Each trip includes 35 seconds at each intermediate stop within a 38 km/h commercial-speed allowance. Movement time is shared between legs in proportion to their assumed lengths. The calculation checks each scheduled leg against the 72 km/h cap on average. Survey grades, curves, acceleration, braking, traction-supply interruptions and recovery margins could lengthen trips and increase fleet demand. The power and infrastructure budgets remain associated with the selected protected-conductor case. [Vehicle and station interfaces](VEHICLE.md) · [Operating and power assumptions](system.toml)

| Group | Sites or paths used in the diagram | Decision needed |
|---|---|---|
| First network, seven lines | 52 named occurrences in route order and seven nominal line lengths. The cost map register has 37 located occurrences. The geographic review locates a further two and corrects the Adhamiya position. | Resolve the 13 remaining locations, determine which named areas warrant stations, allocate the 64-station budget and survey chainages. Timing assumes equal distances between names on each corridor. |
| M03, M05–M08, M10–M14 | Ordered station screens projected onto each schematic line. M05 runs through the matching end of line-5 onto the airport extension. | Survey the access, confirm stopping sites and terminal and passing layouts, reconcile service with the 280-station budget. |
| M01 and M02 | Jadriya access tracks join the interiors of line-1 and line-2. | Specify the two terminal pairs, branch frequencies and shared-trunk mileage. |
| M04 | B-A02 and B-A03 end about 2.32 and 2.71 km from line-4. | Locate and price the missing connections before routing either path. |
| M09 | B-A04 joins the ring at an intermediate point. | Select ring circulation, branch service frequencies and the junction timetable. |

The ten diagrammed citywide groups use costed route lengths scaled to the 605.652 km programme control. A map touch at the airport establishes a continuous schematic path. Engineering drawings must still locate the switch, platform, access and clearances. [Map review](maps/README.md) · [Station register](station-register.json)

## Where the timetable needs railway design

**Turning and stabling.** Each scheduled departure draws a set from its origin after the preceding arrival and a minimum 180-second turn. The return service has a fixed offset within its departure interval to align the two ends at peak. At 150-second headways a three-minute turn needs at least two positions at each end, before approach, crossover or tail clearance. Each group's start and finish stock balances by terminal. For example the Airport line needs ten sets starting at the airport end and eight at Al Qadisiya. The operator must design depot positioning, midday storage, crossovers, platform occupation, rescue paths and maintenance windows. If all linked sets wait at their arrival platforms until their next departure, the Airport diagram occupies up to eight berths at one end and seven at the other. On the M09 opening option it occupies up to 26 berths in each direction at M-134. These counts include stepped-down off-peak service and the six-second tail clearance at the speed cap. First and last depot moves and crossings remain outside the calculation. This operating pattern requires stabling tracks and stock moves or different train workings to fit a smaller terminal. The diagram table counts trip time plus minimum turns for labour planning. Longer waits and movements to depot need a roster and depot working.

**Train separation.** The screen tests one exclusive block per station pair in each direction. The head travels to the next stop, incurs intermediate dwell, then clears at least 104.5 m of tail, taking at least six seconds even at the speed cap. At a terminal the test allows that minimum tail time without modelling the terminal throat. The Yellow line's most demanding interval needs 268 seconds more than the 150-second peak separation under this block assumption. Under constant time spacing, the worst Yellow station pair needs at least three exclusive blocks. The most demanding M04 and M09 pairs in the opening option each need at least five. This lower bound divides travel and dwell time by the peak interval available after tail clearance. Surveyed speeds, gradients, braking distances and signal overlaps determine where detection and release can actually occur. Rate the selected equipment using braking and approach curves, occupied platform limits, departures under acceleration, switch release and degraded operation. The figures identify where a signalling contractor must show separation.

**Transfers and junctions.** Four first-network and ten citywide intermediate interchange screens link diagrammed groups. They use repeated named places or mapped junction groups. Example connections assume 300 seconds to change platforms. The summary counts seconds of overlapping station occupation if the routes share one conflict area. At Al Bayaa that overlap totals 10,530 seconds over the day for Airport, Green and Yellow trains. Survey cross-platform walking times, determine where the tracks actually conflict and replay the chosen junction geometry. Terminal transfers and groups on hold remain outside this screen. [Full-day group and interchange screens](service-diagrams.json)

## Reproduce or export the workings

The generator reads the selected service offer, current cost results, station register and geographic review. The compact publication stores group patterns, fleet and clearance screens. The timetable card embeds two worked sets per service group. All daily events can be exported on demand using standard Python.

```sh
python3 -m engineering.outline.baghdad_diagrams --check
python3 -m engineering.outline.baghdad_diagrams --events first --train Airport-001
python3 -m engineering.outline.baghdad_diagrams --events metropolitan --group M05
python3 -m engineering.outline.baghdad_diagrams --events metropolitan-mainlines --group M09
.venv/bin/python -m pytest -q engineering/outline/tests/test_baghdad_diagrams.py
```

The CSV gives service group, set, trip, direction, stop and next stop on every leg. Local seconds run from midnight of the departure day, so an arrival after midnight exceeds 86,400. Terminal departure and arrival appear on the two different trips of the same set. Blank register IDs identify calls without a match in the pinned cost-map station register.
