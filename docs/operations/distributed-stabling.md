# Distributed overnight station stabling

Healthy trainsets should finish service at powered stations near their first
morning trips. The main depot supplies maintenance, inspections and defective
train handling. A requirement to park the whole fleet at depots is not part of
this operating policy.

## Implemented operating model

The simulator now accepts `station_stabling = true` in a `[[fleets]]` block.
Its `dispatch_points` select powered station locations and initial headings.
The loader requires a grid-connected energy site, at least 150 kW charging,
unique station/direction pairs and valid inward headings at radial endpoints.

Optional `spare_count` and `cold_reserve_count` are included in the total
`trainset_count`; omitted counts default to zero. Candidates carry these roles
from the city design. Reserve trains remain parked and can charge, but do not
enter routine service. Automatic reserve activation and defective-train routing
remain to be implemented.

Selected passenger stations can hold trains and request up to 150 kW per train
to a 95% SoC target. Shared site supply/converter limits and pad outages still
apply. After closing, moving trains finish their section and continue to a
selected station; they hold there until service resumes. No train is moved back
to its starting station by resetting its position. Both valid departure
headings receive headway control, including the return direction.

Morning departures remain subject to the published schedule, headway,
energy-reserve, movement-authority and fault gates. A coordinated start does
not override a safety hold or guarantee simultaneous departure in a fault case.
The simulator's physical graph covers interstation sections; platform berths,
station throats and shared junction conflicts still require separate modelling.

## Catalogue candidates and Samawah replay

Every city now carries a source-linked `engineering/stabling/summary.json` and
README. The candidate allocator balances the existing fleet across eligible
station/direction choices, spreading a smaller fleet across the route. It
preserves the retained scenario's non-fleet inputs, fleet counts and service
windows, including existing city-specific charging settings.

For Samawah, the candidate initially allocates **108 trainsets to 20 stations**.
These comprise **97 revenue trains, eight spares and three cold reserves**.
The [01:30–06:00 comparison](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/operating-screen.md)
found:

| Measure | Retained endpoint model | Distributed candidate |
|---|---:|---:|
| Occupied stations at 05:29 | 6 | 20 |
| Largest overnight station queue | 27 | 8 |
| Departures between 02:30 and 05:30 | 4 | 0 |
| All occupied stations restart within 60 seconds of opening | Yes | Yes |
| Planned line/station/direction departures within 60 seconds | 6 / 6 | 34 / 34 |
| Declared reserve trains entering routine service | No roles declared | 0 |
| Invariant violations | 0 | 0 |

Both runs begin at 95% train SoC at 01:30. They test closing, holding, charging
and restart behaviour; they do not establish full-day energy endurance or
correct depot/station energy sizing. The replay records the actual final-night
positions rather than assuming the initial allocation is restored.

## Continuous service-day check

The [two-day replay](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/service-cycle-screen.md)
starts at 05:30 and runs continuously through two complete service days and
their following mornings. Train positions, batteries and site storage are not
reset between days. It **fails the overnight placement check**, despite all
34 planned departure directions restarting within 60 seconds on both mornings.

After day one, six revenue trains remain at the unpowered Line 1 station
`line-1-0814-0268-s019260`; after day two, ten remain there. Their SoC ranges
from 21.3–27.5% and 20.5–27.1%, respectively. This station has no declared
charging power and is excluded from the candidate's stabling locations.
The native departure gate protects energy for the next section, but does not
prove a train can reach the next powered station. Charging reachability and
recovery therefore need explicit treatment before this candidate is accepted.

The largest observed overnight queue reaches **20 trains after day one** and
**13 after day two**. The short replay's eight-train maximum is not a design
capacity for continuous operation. The new report calculates reference
platform space requirements from each actual night allocation and rejects
trains parked outside their line's selected stabling locations. It also checks
complete fleet snapshots, overnight departures and battery reserve retention.
Daytime headway delivery, adverse weather and physical charging access remain
separate acceptance work.

## Remaining physical and operating work

A simulated station queue remains an abstract queue. No surveyed stabling
roads, platform occupancy or charging connectors are created by this allocator.
Each location needs usable track lengths and train assignments, access and
turnout checks, charger-sharing arrangements, CCTV/remote isolation, inspection
release and an evening/morning movement plan. The static reserve roles need
activation rules, inspection duties and defective-train recovery movements.

The allocation reports now compare each station's train inventory with the
reference platform count and usable length, allowing 5 m clearance at each end
of a train. Samawah has **62 train positions beyond that reference envelope**,
equivalent to **3,689 m of additional usable stabling slots** under the initial
allocation. This is an unresolved space requirement, not a finding that new
tracks or depots are necessary. Existing sidings, revised train placement and
actual platform availability must be checked. Reference platform berths are
not verified overnight capacity; the comparison does not model access or
conflicting movements.

Check these station arrangements before proposing additional sidings or depot
sites. Reassess depot and station PV/storage against the resulting duties.
The planning reports keep `passed: false` and deployment release open even when
the separate operating replay passes.

The runnable candidates live under `build/engineering/stabling/`; canonical
city scenarios and their existing acceptance evidence are retained. Promoting
a candidate requires explicit design dispatch inputs and a full city evidence
regeneration, including daytime timetable and energy consequences.

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --all
.venv/bin/python tools/automation/screen-stabling-plan.py --design cities/catalogue/west-asia/Iraq/Samawah/design.toml
.venv/bin/python tools/automation/screen-stabling-cycles.py --design cities/catalogue/west-asia/Iraq/Samawah/design.toml --days 2
```

The replay tool builds the current release simulator and records source,
candidate, binary and raw-output hashes. Full traces and CSVs remain local under
`build/engineering/stabling/`; compact comparison evidence is stored beside the
city's plan.
