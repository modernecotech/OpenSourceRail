# Station and depot overnight stabling

Two revenue trainsets stay at each selected powered station for coordinated
morning starts. The remaining revenue trains and reserves stay at declared
depots. Depot parking tracks are sized separately from maintenance and
inspection bays.

For [Samawah](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/stabling/README.md),
the plan is:

| Location | Revenue | Spare | Cold reserve | Total |
|---|---:|---:|---:|---:|
| 20 stations, two trains each | 40 | 0 | 0 | 40 |
| Existing main depot | 57 | 8 | 3 | 68 |
| Fleet | 97 | 8 | 3 | 108 |

The station allocation covers all 34 planned morning departure directions.
The main depot requires 68 storage positions, or 4,046 m of usable slots at
49.5 m per train plus 10 m clearance. Its 17 workshop bays are a separate
maintenance provision. This is a storage requirement for the declared depot;
its track layout and access from Lines 2 and 3 still need detailing.

## Generated plans

Every catalogue city's `engineering/stabling/summary.json` includes a
`hybrid_allocation`: station and depot assignments by line and fleet role,
depot storage positions, usable slot lengths and unresolved access requirements.
The allocator first assigns revenue stock to morning departure directions,
then fills station provision up to two trains, and assigns the remainder and
reserves to declared depots. Stations shared between lines count once.
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
locations and access on the train's own line.

At closing, active trains finish their journeys along real sections until they
reach their assigned homes. Return moves retain energy and movement-authority
checks and use the largest scheduled headway for spacing, independently of the
closed passenger timetable. This is a conservative run-in policy, not an
optimised evening timetable. At home, trains berth with the declared morning
heading and top up under the shared site limits. CSV `stabling_location`
distinguishes station, depot and in-transit stock. Waiting launch stock gets
priority over recirculating arrivals; schedule, faults and energy still gate
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

The generator emits a separate `*-hybrid.toml` only where allocation and
same-line depot access allow it. Uíge, Quelimane and Edéa currently qualify for
candidate generation; this does not establish service-day acceptance. Other
reports give a reason for withholding the native candidate. Samawah's 40/68
plan remains intact, but Lines 2 and 3 need modelled rail connections to the
Line 1 main depot before its full hybrid operation can run.

```bash
cargo test -p osr-sim --test hybrid_stabling
cargo run --release --bin osr-sim -- --config lib/examples/hybrid-stabling.toml --duration 173701 --time-step 5 --ma-check-every 0 --csv-out /tmp/hybrid-stabling.csv
```

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

Add depot storage tracks and interline access to the physical model, then
validate the conservative home-return policy against city evening and morning
timetables while retaining two station launch trains. Verify shared charging, daytime headways, inspection
release, reserve activation and defective-train recovery against those duties.
Reassess depot and station energy sizing from the resulting operation.
