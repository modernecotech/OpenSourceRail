# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 55 at depots = 95 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0176-0341-s014506 | line-1 | declared-depot | 18 | 882.0 | 5 |
| line-2-0075-0508-s000000 | line-2 | declared-depot | 18 | 882.0 | 5 |
| line-3-0318-0463-s000000 | line-3 | declared-depot | 7 | 343.0 | 3 |
| line-4-0331-0219-s000000 | line-4 | declared-depot | 6 | 294.0 | 2 |
| line-5-0510-0432-s000000 | line-5 | declared-depot | 6 | 294.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0176-0341-s014506 | station | reverse | revenue | 2 |
| line-1 | line-1-0315-0309-s008662 | station | forward | revenue | 1 |
| line-1 | line-1-0315-0309-s008662 | station | reverse | revenue | 1 |
| line-1 | line-1-0331-0219-s006383 | station | forward | revenue | 1 |
| line-1 | line-1-0331-0219-s006383 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0375-s000864 | station | forward | revenue | 1 |
| line-1 | line-1-0511-0375-s000864 | station | reverse | revenue | 1 |
| line-1 | line-1-0512-0371-s000776 | station | forward | revenue | 1 |
| line-1 | line-1-0512-0371-s000776 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0355-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0075-0508-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0264-0427-s005234 | station | forward | revenue | 1 |
| line-2 | line-2-0264-0427-s005234 | station | reverse | revenue | 1 |
| line-2 | line-2-0353-0416-s007526 | station | forward | revenue | 1 |
| line-2 | line-2-0353-0416-s007526 | station | reverse | revenue | 1 |
| line-2 | line-2-0510-0432-s012953 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0432-s012953 | station | reverse | revenue | 1 |
| line-2 | line-2-0511-0375-s014302 | station | forward | revenue | 1 |
| line-2 | line-2-0511-0375-s014302 | station | reverse | revenue | 1 |
| line-2 | line-2-0513-0369-s014439 | station | reverse | revenue | 2 |
| line-3 | line-3-0290-0295-s005200 | station | reverse | revenue | 2 |
| line-3 | line-3-0315-0309-s004561 | station | forward | revenue | 1 |
| line-3 | line-3-0315-0309-s004561 | station | reverse | revenue | 1 |
| line-3 | line-3-0318-0463-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0353-0416-s001390 | station | forward | revenue | 1 |
| line-3 | line-3-0353-0416-s001390 | station | reverse | revenue | 1 |
| line-4 | line-4-0331-0219-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0413-0112-s004154 | station | reverse | revenue | 2 |
| line-5 | line-5-0510-0432-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0537-0562-s004096 | station | reverse | revenue | 2 |
| line-1 | line-1-0176-0341-s014506 | depot | — | revenue | 15 |
| line-1 | line-1-0176-0341-s014506 | depot | — | spare | 2 |
| line-1 | line-1-0176-0341-s014506 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0075-0508-s000000 | depot | — | revenue | 15 |
| line-2 | line-2-0075-0508-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0075-0508-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0318-0463-s000000 | depot | — | revenue | 5 |
| line-3 | line-3-0318-0463-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0318-0463-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0331-0219-s000000 | depot | — | revenue | 4 |
| line-4 | line-4-0331-0219-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0331-0219-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0510-0432-s000000 | depot | — | revenue | 4 |
| line-5 | line-5-0510-0432-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0510-0432-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mbale-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **95 trainsets at 20 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 7 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **55 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0539-0355-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0512-0371-s000776 | forward | revenue | 3 | pending |
| line-1 | line-1-0512-0371-s000776 | reverse | revenue | 3 | pending |
| line-1 | line-1-0511-0375-s000864 | forward | revenue | 3 | pending |
| line-1 | line-1-0511-0375-s000864 | reverse | revenue | 3 | pending |
| line-1 | line-1-0331-0219-s006383 | forward | revenue | 3 | pending |
| line-1 | line-1-0331-0219-s006383 | reverse | revenue | 3 | pending |
| line-1 | line-1-0315-0309-s008662 | forward | revenue | 2 | pending |
| line-1 | line-1-0315-0309-s008662 | reverse | revenue | 2 | pending |
| line-1 | line-1-0176-0341-s014506 | reverse | revenue | 2 | pending |
| line-1 | line-1-0315-0309-s008662 | forward | spare | 1 | pending |
| line-1 | line-1-0315-0309-s008662 | reverse | spare | 1 | pending |
| line-1 | line-1-0176-0341-s014506 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0075-0508-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0264-0427-s005234 | forward | revenue | 3 | pending |
| line-2 | line-2-0264-0427-s005234 | reverse | revenue | 3 | pending |
| line-2 | line-2-0353-0416-s007526 | forward | revenue | 3 | pending |
| line-2 | line-2-0353-0416-s007526 | reverse | revenue | 3 | pending |
| line-2 | line-2-0510-0432-s012953 | forward | revenue | 3 | pending |
| line-2 | line-2-0510-0432-s012953 | reverse | revenue | 3 | pending |
| line-2 | line-2-0511-0375-s014302 | forward | revenue | 2 | pending |
| line-2 | line-2-0511-0375-s014302 | reverse | revenue | 2 | pending |
| line-2 | line-2-0513-0369-s014439 | reverse | revenue | 2 | pending |
| line-2 | line-2-0511-0375-s014302 | forward | spare | 1 | pending |
| line-2 | line-2-0511-0375-s014302 | reverse | spare | 1 | pending |
| line-2 | line-2-0513-0369-s014439 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0318-0463-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0353-0416-s001390 | forward | revenue | 2 | pending |
| line-3 | line-3-0353-0416-s001390 | reverse | revenue | 2 | pending |
| line-3 | line-3-0315-0309-s004561 | forward | revenue | 2 | pending |
| line-3 | line-3-0315-0309-s004561 | reverse | revenue | 2 | pending |
| line-3 | line-3-0290-0295-s005200 | reverse | revenue | 2 | pending |
| line-3 | line-3-0353-0416-s001390 | forward | spare | 1 | pending |
| line-3 | line-3-0353-0416-s001390 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0331-0219-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0413-0112-s004154 | reverse | revenue | 4 | pending |
| line-4 | line-4-0331-0219-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0413-0112-s004154 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0510-0432-s000000 | forward | revenue | 4 | pending |
| line-5 | line-5-0537-0562-s004096 | reverse | revenue | 4 | pending |
| line-5 | line-5-0510-0432-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0537-0562-s004096 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**37 trainsets exceed the reference platform envelope**, requiring **1,813.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0176-0341-s014506 | 3 | 2 | 1 | 49.0 |
| line-1-0315-0309-s008662 | 6 | 4 | 2 | 98.0 |
| line-1-0331-0219-s006383 | 6 | 4 | 2 | 98.0 |
| line-1-0511-0375-s000864 | 6 | 4 | 2 | 98.0 |
| line-1-0512-0371-s000776 | 6 | 4 | 2 | 98.0 |
| line-1-0539-0355-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0075-0508-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0264-0427-s005234 | 6 | 2 | 4 | 196.0 |
| line-2-0353-0416-s007526 | 6 | 4 | 2 | 98.0 |
| line-2-0510-0432-s012953 | 6 | 4 | 2 | 98.0 |
| line-2-0511-0375-s014302 | 6 | 4 | 2 | 98.0 |
| line-2-0513-0369-s014439 | 3 | 2 | 1 | 49.0 |
| line-3-0290-0295-s005200 | 2 | 2 | 0 | 0.0 |
| line-3-0315-0309-s004561 | 4 | 4 | 0 | 0.0 |
| line-3-0318-0463-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0353-0416-s001390 | 6 | 4 | 2 | 98.0 |
| line-4-0331-0219-s000000 | 5 | 2 | 3 | 147.0 |
| line-4-0413-0112-s004154 | 5 | 2 | 3 | 147.0 |
| line-5-0510-0432-s000000 | 5 | 2 | 3 | 147.0 |
| line-5-0537-0562-s004096 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Mbale/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
