# Station and depot overnight stabling

Two revenue trainsets stay at each selected powered station for coordinated
morning starts. The remaining revenue trains and reserves stay at declared
storage on their own line. Depot parking tracks are sized separately from maintenance and
inspection bays.

For [Samawah](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/README.md),
the plan is:

| Location | Revenue | Spare | Cold reserve | Total |
|---|---:|---:|---:|---:|
| 20 stations, two trains each | 40 | 0 | 0 | 40 |
| Line 1 main depot | 32 | 4 | 1 | 37 |
| Line 2 service-terminal storage | 13 | 2 | 1 | 16 |
| Line 3 service-terminal storage | 12 | 2 | 1 | 15 |
| Fleet | 97 | 8 | 3 | 108 |

The station allocation covers all 34 planned morning departure directions.
The three storage locations require 4,046 m of usable slots in total at
49.5 m per train plus 10 m clearance: 2,201.5 m on Line 1, 952 m on Line 2,
and 892.5 m on Line 3. The main depot's 17 workshop bays remain separate.
Lines 2 and 3 use their existing powered service terminals, with the reusable
layup block defining storage requirements. No additional heavy workshop is
inferred. Storage layout and energy sizing still need engineering verification.

Each line operates independently. Trains stay on their own line for station
launch, depot storage and return movements. The allocator adds no interline
connections, new route geometry or cross-line train transfers. This follows the
[simplicity principle](../rfcs/0013-operations-rulebook.md#3-the-simplicity-principle):
use the existing line and service point, with explicit, repeatable rules.

## Generated plans

Every catalogue city's `engineering/stabling/summary.json` includes a
`hybrid_allocation`: station and depot assignments by line and fleet role,
depot storage positions, usable slot lengths and unresolved access requirements.
The allocator first assigns revenue stock to morning departure directions,
then fills station provision up to two trains, and assigns the remainder and
reserves to storage on the same line. It prefers an existing depot, then the
line’s designated powered service terminal. Stations shared between lines count once.
Where a line lacks enough revenue stock for all morning directions, the report
identifies the uncovered directions instead of creating trains.

`allocation_passed` checks fleet accounting, the station limit, planned depot
positions and morning direction coverage. Depot positions are requirements,
not surveyed capacity. Physical release remains open until track lengths,
turnouts, charging access, security and inspection arrangements are verified.

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --all
```

## Native hybrid operation

The simulator accepts explicit `overnight_allocations` for every fleet, with
station, departure heading, location type, role and train count. Depot stations
also declare `depot_stabling_positions`; `is_depot` and workshop bays alone
provide no storage allowance. The loader checks complete fleet/role inventory,
at most two station homes per shared station, depot capacity, powered dispatch
locations and access on the train's own line. Station batteries can supply
charging without grid import; a grid outage does not itself disable a charger.
Positive installed charging/source capability selects a candidate. The
continuous replay, rather than a universal 150 kW minimum, tests its duty.

At closing, active trains finish their journeys along real sections until they
reach their assigned homes. Return moves retain energy and movement-authority
checks and use the line’s existing peak-service headway for spacing,
independently of the closed passenger timetable. The event log records these
empty movements as `ReturnToStabling`. Passenger service closes at 02:00;
empty returns can continue until trains are stabled before the morning start.
At home, trains berth with the declared morning
heading and top up under the shared site limits. CSV `stabling_location`
distinguishes station, depot and in-transit stock.
Station launch trains get priority, followed by waiting depot revenue trains,
then other trains; train ID resolves ties. Schedule, faults and energy still gate
morning departures. Reserves remain in depot storage.

The [connected eight-train fixture](../../lib/examples/hybrid-stabling.toml)
passes two continuous service cycles: two trains at each of three stations,
one revenue train and one spare at the depot, real depot departures/returns,
charging and no movement-authority invariant violations. Train positions and
batteries are retained between cycles. A repeat-run test also compares the full
per-train CSV byte for byte, event sequence, distance and energy totals. With
the same simulator build, input ordering, scheduled faults and time step, both
runs match exactly. This establishes repeatability for the tested model; it is
not a proof of real-world timing or bitwise equivalence across platforms.
Depot berthing and heading changes are
abstract node operations; yard roads, throats and turnback geometry remain
outside the physical graph.

The generator emits a separate `*-hybrid.toml` where the station launch
allocation is complete. The current catalogue has 182 native candidates;
84 plans still lack revenue trains for every selected morning direction.
Samawah now has a runnable candidate with all 108 train homes on their own
lines. Candidate generation is separate from continuous operating acceptance.

`screen-hybrid-stabling.py` runs full service days and checks each train against
its explicit home, separating station and depot capacity. It checks the
passenger-service closure, battery reserve, parked reserves and station launch
directions. Empty returns during 02:30–05:30 are reported explicitly. Depot departures cannot substitute for missing station launch
stock. The first 30 minutes of depot revenue departures are reported without
requiring every stored train to join service immediately.

```bash
.venv/bin/python tools/automation/screen-hybrid-stabling.py --design cities/catalogue/west-asia/Iraq/Samawah/design.toml --days 2
cargo test -p osr-sim --test hybrid_stabling
cargo run --release --bin osr-sim -- --config lib/examples/hybrid-stabling.toml --duration 173701 --time-step 5 --ma-check-every 0 --csv-out /tmp/hybrid-stabling.csv
```

## City operating evidence

The following line-local hybrid screens pass two continuous service days:

| City | Station / depot trains each night | Station directions restarting within 60 s, each morning |
|---|---:|---:|
| [Samawah](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/hybrid-cycle-screen.md) | 40 / 68 | 34 / 34 |
| [Uíge](../../cities/catalogue/east-africa/Angola/Uige/engineering/stabling/hybrid-cycle-screen.md) | 12 / 15 | 10 / 10 |
| [Quelimane](../../cities/catalogue/east-africa/Mozambique/Quelimane/engineering/stabling/hybrid-cycle-screen.md) | 10 / 13 | 8 / 8 |
| [Edéa](../../cities/catalogue/west-africa/Cameroon/Edea/engineering/stabling/hybrid-cycle-screen.md) | 10 / 10 | 8 / 8 |

All trains reach their assigned homes before opening, depot and station counts
meet the declared allocation, and reserves remain parked. There are no
passenger departures after closure or movement-authority invariant violations.
Empty return movements after 02:30 remain visible in each report. Samawah's
minimum raw SoC is 0.19999853; its reserve comparison uses the existing city
validator's 0.001-percentage-point floating-point tolerance. Physical layouts,
electrical acceptance and daytime headway delivery remain open.

## Retained station-only operating evidence

The existing native candidate is a **station-only benchmark**. It implements
station holding, shared charging up to 150 kW per train toward 95% SoC,
schedule/headway/movement-authority gated starts, and sufficient departure
energy to reach the next selected charger with the 20% reserve. Spare and
cold-reserve roles remain parked and do not enter routine service. Automatic
reserve activation and physical yard routing remain to be implemented.

Samawah's [short overnight replay](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/operating-screen.md)
and [continuous two-day replay](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/service-cycle-screen.md)
pass their holding and restart checks: all 34 planned directions restart within
60 seconds, with no routine reserve departures or invariant violations. The
continuous replay retains positions, train batteries and site storage between
days. Its largest overnight station queues reach 18 and 19 trains, so its
combined acceptance result fails the two-train station limit.

Those failures describe historical station-only benchmarks. Their source hashes
remain attached to the original experiments; the package manifest records
them as diagnostics, including any source drift, outside selected-plan acceptance.
Those failures describe the station-only benchmark. They do not invalidate
the 40-station/68-depot planning split or demonstrate its execution. The earlier
[seven-train redistribution study](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/redistribution-study.md)
is also a station-only counterfactual, rather than the adopted overnight plan.

```bash
.venv/bin/python tools/automation/screen-stabling-plan.py --design cities/catalogue/west-asia/Iraq/Samawah/design.toml
.venv/bin/python tools/automation/screen-stabling-cycles.py --design cities/catalogue/west-asia/Iraq/Samawah/design.toml --days 2
```

Runnable benchmarks and raw traces live under `build/engineering/stabling/`.
Compact reports record source, candidate, binary and raw-output hashes.

## Remaining implementation

Detail storage tracks and access within each line’s service location, then
validate the same-line home-return policy against city evening and morning
timetables while retaining two station launch trains. Verify shared charging, daytime headways, inspection
release, reserve activation and defective-train recovery against those duties.
Reassess depot and station energy sizing from the resulting operation.
