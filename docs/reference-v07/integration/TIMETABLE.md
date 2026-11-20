# Core 30 km passenger timetable

From 06:00 to midnight the two terminals each dispatch 288 trains. The planning timetable gives 17,280 passenger train-km per day and 6,307,200 per 365-day year. The 44 numbered workings share 385.0 train-hours in passenger service and 28.8 hours of minimum terminal occupation. The last train arrives at 24:35:06 on the service-day clock.

| Departures from either end | Headway | Trains/hour/direction | Normal places/hour/direction |
|---|---:|---:|---:|
| 06:00–07:00, 09:00–16:00, 18:00–24:00 | 300 s | 12 | 3,312 |
| 07:00–09:00 and 16:00–18:00 | 120 s | 30 | 8,280 |

The operating estimate supplies four peak and fourteen other hours. The clock times locate these hours for a workshop. Both directions stop at every station on the level, equally spaced synthetic line. Each of the eleven running intervals includes 5% motion allowance. The ten intermediate stops each allow 35 seconds. The longer published constant-peak comparison has a different daily service.

| First working from S01 | S01 | S02 | S03 | S04 | S05 | S06 | S07 | S08 | S09 | S10 | S11 | S12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Depart (arrive at S12) | 06:00:00 | 06:03:42 | 06:07:24 | 06:11:06 | 06:14:48 | 06:18:30 | 06:22:12 | 06:25:54 | 06:29:35 | 06:33:17 | 06:36:59 | 06:40:06 |

## Turnbacks and fleet

A trip takes 2406.25 seconds. Two trips and two 180 s reversals take 5,172.50 seconds. At 120 s headways the 44-set cycle allows 107.5 seconds of additional time per round trip. The other 7 sets are the reserve allowance. Each duty starts with a set available at its departure end. The model stages 22 sets per end and reuses the most recent eligible arrival.

Across the day the interval calculation requires 3 independent berth positions at S01 and 3 at S12. A train with at most 300 s until its reverse working stays on its face. Longer layovers use sidings after the minimum turn, with a further 35 s of boarding before departure. This gives 52 intermediate siding movements, plus initial deployment and final stabling. The berth count assumes every position can serve the train’s door side. Timed crossover, empty-stock and route-release paths and a compatible terminal layout are outstanding.

## Two disruption cases

* **Failed ready set.** If T38 fails clear of the running line before its 07:00:00 S01 departure and no replacement is available, 13 subsequent trips on its duty, including that departure, lose their assigned train. A ready, compatible spare in position before departure can inherit that duty, leaving 6 reserves. Failure on the running line additionally requires a protected recovery path and a timed clearance.
* **Blocked face at S12.** With one of its 3 scheduled positions closed all day, 8 scheduled occupation intervals cannot be admitted on time to the remaining positions. The export lists the affected trains and intervals. A supervisor must plan holding points, departures and any accessible transfer. With **only one face available**, 180 s per arrival gives a theoretical ceiling of 20 reversals/hour before dispatch conflicts. Admitting arrivals in time order and dropping those which cannot immediately take the face leaves 60 arrivals without a berth over the day. Price a reduced peak offer and trace its corresponding return workings before diversion or cancellation. An unavailable platform also needs a verified accessible route and passenger management.

Measure loaded dwell, wheelchair boarding, door lock and despatch, full-tail clearance, train reversal and route release at both ends. Survey platform faces, crossing conflicts, sidings, depot access and rescue time. The working diagram supplies planned times and resource demands for these trials. Passenger operating approval remains open.

Use `python3 docs/reference-v07/integration/timetable.py --json` for every numbered train, trip, stop call and affected disruption working. Times are seconds after service-day midnight. Use `--check` to verify this sheet. [Operating-cost service assumptions](../../../engineering/v07_reference_journey.py) · [Level running and fleet control](../../design-engine/v07-architecture-decision/result.json) · [Core cost control](../../design-engine/v07-powered-cost/input.json)

Selected train and corridor `osr-v07-joined-civil-518dad57a3af5046f40c8f4f`. Service evaluation `66624c217e2ee50fbc6acb9850609d35a3e5632fbd2e02f6bfe33c91e1e6366b`.
