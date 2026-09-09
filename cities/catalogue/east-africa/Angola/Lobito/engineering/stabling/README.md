# Station and depot overnight allocation

Plan: **30 trainsets at stations + 53 at depots = 83 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0386-0735-s018290 | line-1 | declared-depot | 26 | 1,547.0 | 13 |
| line-2-0668-0828-s011646 | line-2 | storage-at-existing-powered-service-point | 17 | 1,011.5 | 0 |
| line-3-0595-0487-s008120 | line-3 | storage-at-existing-powered-service-point | 10 | 595.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0386-0735-s018290 | station | reverse | revenue | 2 |
| line-1 | line-1-0446-0663-s016266 | station | forward | revenue | 1 |
| line-1 | line-1-0446-0663-s016266 | station | reverse | revenue | 1 |
| line-1 | line-1-0505-0592-s014231 | station | forward | revenue | 1 |
| line-1 | line-1-0505-0592-s014231 | station | reverse | revenue | 1 |
| line-1 | line-1-0565-0552-s012200 | station | forward | revenue | 1 |
| line-1 | line-1-0565-0552-s012200 | station | reverse | revenue | 1 |
| line-1 | line-1-0630-0522-s009317 | station | forward | revenue | 1 |
| line-1 | line-1-0630-0522-s009317 | station | reverse | revenue | 1 |
| line-1 | line-1-0770-0521-s006315 | station | forward | revenue | 1 |
| line-1 | line-1-0770-0521-s006315 | station | reverse | revenue | 1 |
| line-1 | line-1-1075-0511-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0565-0552-s003689 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0552-s003689 | station | reverse | revenue | 1 |
| line-2 | line-2-0601-0621-s006014 | station | forward | revenue | 1 |
| line-2 | line-2-0601-0621-s006014 | station | reverse | revenue | 1 |
| line-2 | line-2-0668-0828-s011646 | station | reverse | revenue | 2 |
| line-2 | line-2-0695-0574-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0565-0552-s006096 | station | forward | revenue | 1 |
| line-3 | line-3-0565-0552-s006096 | station | reverse | revenue | 1 |
| line-3 | line-3-0595-0487-s008120 | station | reverse | revenue | 2 |
| line-3 | line-3-0658-0610-s003020 | station | forward | revenue | 1 |
| line-3 | line-3-0658-0610-s003020 | station | reverse | revenue | 1 |
| line-3 | line-3-0722-0711-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0386-0735-s018290 | depot | — | revenue | 22 |
| line-1 | line-1-0386-0735-s018290 | depot | — | spare | 3 |
| line-1 | line-1-0386-0735-s018290 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0668-0828-s011646 | depot | — | revenue | 14 |
| line-2 | line-2-0668-0828-s011646 | depot | — | spare | 2 |
| line-2 | line-2-0668-0828-s011646 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0595-0487-s008120 | depot | — | revenue | 8 |
| line-3 | line-3-0595-0487-s008120 | depot | — | spare | 1 |
| line-3 | line-3-0595-0487-s008120 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/lobito-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **83 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **74 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **53 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1075-0511-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0770-0521-s006315 | forward | revenue | 3 | pending |
| line-1 | line-1-0770-0521-s006315 | reverse | revenue | 3 | pending |
| line-1 | line-1-0630-0522-s009317 | forward | revenue | 3 | pending |
| line-1 | line-1-0630-0522-s009317 | reverse | revenue | 3 | pending |
| line-1 | line-1-0565-0552-s012200 | forward | revenue | 3 | pending |
| line-1 | line-1-0565-0552-s012200 | reverse | revenue | 3 | pending |
| line-1 | line-1-0505-0592-s014231 | forward | revenue | 3 | pending |
| line-1 | line-1-0505-0592-s014231 | reverse | revenue | 3 | pending |
| line-1 | line-1-0446-0663-s016266 | forward | revenue | 3 | pending |
| line-1 | line-1-0446-0663-s016266 | reverse | revenue | 3 | pending |
| line-1 | line-1-0386-0735-s018290 | reverse | revenue | 3 | pending |
| line-1 | line-1-1075-0511-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0770-0521-s006315 | forward | spare | 1 | pending |
| line-1 | line-1-0770-0521-s006315 | reverse | spare | 1 | pending |
| line-1 | line-1-0630-0522-s009317 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0574-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0565-0552-s003689 | forward | revenue | 4 | pending |
| line-2 | line-2-0565-0552-s003689 | reverse | revenue | 4 | pending |
| line-2 | line-2-0601-0621-s006014 | forward | revenue | 4 | pending |
| line-2 | line-2-0601-0621-s006014 | reverse | revenue | 3 | pending |
| line-2 | line-2-0668-0828-s011646 | reverse | revenue | 3 | pending |
| line-2 | line-2-0601-0621-s006014 | reverse | spare | 1 | pending |
| line-2 | line-2-0668-0828-s011646 | reverse | spare | 1 | pending |
| line-2 | line-2-0695-0574-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0722-0711-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0658-0610-s003020 | forward | revenue | 3 | pending |
| line-3 | line-3-0658-0610-s003020 | reverse | revenue | 3 | pending |
| line-3 | line-3-0565-0552-s006096 | forward | revenue | 3 | pending |
| line-3 | line-3-0565-0552-s006096 | reverse | revenue | 2 | pending |
| line-3 | line-3-0595-0487-s008120 | reverse | revenue | 2 | pending |
| line-3 | line-3-0565-0552-s006096 | reverse | spare | 1 | pending |
| line-3 | line-3-0595-0487-s008120 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**47 trainsets exceed the reference platform envelope**, requiring **2,796.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0386-0735-s018290 | 3 | 2 | 1 | 59.5 |
| line-1-0446-0663-s016266 | 6 | 2 | 4 | 238.0 |
| line-1-0505-0592-s014231 | 6 | 2 | 4 | 238.0 |
| line-1-0565-0552-s012200 | 6 | 4 | 2 | 119.0 |
| line-1-0630-0522-s009317 | 7 | 2 | 5 | 297.5 |
| line-1-0770-0521-s006315 | 8 | 2 | 6 | 357.0 |
| line-1-1075-0511-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0565-0552-s003689 | 8 | 4 | 4 | 238.0 |
| line-2-0601-0621-s006014 | 8 | 2 | 6 | 357.0 |
| line-2-0668-0828-s011646 | 4 | 2 | 2 | 119.0 |
| line-2-0695-0574-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0565-0552-s006096 | 6 | 4 | 2 | 119.0 |
| line-3-0595-0487-s008120 | 3 | 2 | 1 | 59.5 |
| line-3-0658-0610-s003020 | 6 | 2 | 4 | 238.0 |
| line-3-0722-0711-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lobito/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
