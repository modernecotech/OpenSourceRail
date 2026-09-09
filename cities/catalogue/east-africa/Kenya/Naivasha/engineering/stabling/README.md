# Station and depot overnight allocation

Plan: **26 trainsets at stations + 53 at depots = 79 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0728-0413-s014154 | line-1 | storage-at-existing-powered-service-point | 21 | 1,029.0 | 0 |
| line-2-0354-0390-s009970 | line-2 | storage-at-existing-powered-service-point | 12 | 588.0 | 0 |
| line-3-0122-0114-s014860 | line-3 | declared-depot | 20 | 980.0 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0204-0204-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0316-0332-s003915 | station | forward | revenue | 1 |
| line-1 | line-1-0316-0332-s003915 | station | reverse | revenue | 1 |
| line-1 | line-1-0386-0374-s005818 | station | forward | revenue | 1 |
| line-1 | line-1-0386-0374-s005818 | station | reverse | revenue | 1 |
| line-1 | line-1-0728-0413-s014154 | station | reverse | revenue | 2 |
| line-2 | line-2-0354-0390-s009970 | station | reverse | revenue | 2 |
| line-2 | line-2-0386-0374-s008743 | station | forward | revenue | 1 |
| line-2 | line-2-0386-0374-s008743 | station | reverse | revenue | 1 |
| line-2 | line-2-0456-0355-s006845 | station | forward | revenue | 1 |
| line-2 | line-2-0456-0355-s006845 | station | reverse | revenue | 1 |
| line-2 | line-2-0706-0380-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0122-0114-s014860 | station | reverse | revenue | 2 |
| line-3 | line-3-0262-0224-s010714 | station | forward | revenue | 1 |
| line-3 | line-3-0262-0224-s010714 | station | reverse | revenue | 1 |
| line-3 | line-3-0386-0374-s006595 | station | forward | revenue | 1 |
| line-3 | line-3-0386-0374-s006595 | station | reverse | revenue | 1 |
| line-3 | line-3-0435-0449-s004369 | station | forward | revenue | 1 |
| line-3 | line-3-0435-0449-s004369 | station | reverse | revenue | 1 |
| line-3 | line-3-0586-0588-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0728-0413-s014154 | depot | — | revenue | 18 |
| line-1 | line-1-0728-0413-s014154 | depot | — | spare | 2 |
| line-1 | line-1-0728-0413-s014154 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0354-0390-s009970 | depot | — | revenue | 10 |
| line-2 | line-2-0354-0390-s009970 | depot | — | spare | 1 |
| line-2 | line-2-0354-0390-s009970 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0122-0114-s014860 | depot | — | revenue | 17 |
| line-3 | line-3-0122-0114-s014860 | depot | — | spare | 2 |
| line-3 | line-3-0122-0114-s014860 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/naivasha-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **79 trainsets at 13 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **71 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **53 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0204-0204-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0316-0332-s003915 | forward | revenue | 5 | pending |
| line-1 | line-1-0316-0332-s003915 | reverse | revenue | 4 | pending |
| line-1 | line-1-0386-0374-s005818 | forward | revenue | 4 | pending |
| line-1 | line-1-0386-0374-s005818 | reverse | revenue | 4 | pending |
| line-1 | line-1-0728-0413-s014154 | reverse | revenue | 4 | pending |
| line-1 | line-1-0316-0332-s003915 | reverse | spare | 1 | pending |
| line-1 | line-1-0386-0374-s005818 | forward | spare | 1 | pending |
| line-1 | line-1-0386-0374-s005818 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0706-0380-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0456-0355-s006845 | forward | revenue | 3 | pending |
| line-2 | line-2-0456-0355-s006845 | reverse | revenue | 3 | pending |
| line-2 | line-2-0386-0374-s008743 | forward | revenue | 3 | pending |
| line-2 | line-2-0386-0374-s008743 | reverse | revenue | 3 | pending |
| line-2 | line-2-0354-0390-s009970 | reverse | revenue | 3 | pending |
| line-2 | line-2-0706-0380-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0456-0355-s006845 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0586-0588-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0435-0449-s004369 | forward | revenue | 4 | pending |
| line-3 | line-3-0435-0449-s004369 | reverse | revenue | 4 | pending |
| line-3 | line-3-0386-0374-s006595 | forward | revenue | 3 | pending |
| line-3 | line-3-0386-0374-s006595 | reverse | revenue | 3 | pending |
| line-3 | line-3-0262-0224-s010714 | forward | revenue | 3 | pending |
| line-3 | line-3-0262-0224-s010714 | reverse | revenue | 3 | pending |
| line-3 | line-3-0122-0114-s014860 | reverse | revenue | 3 | pending |
| line-3 | line-3-0386-0374-s006595 | forward | spare | 1 | pending |
| line-3 | line-3-0386-0374-s006595 | reverse | spare | 1 | pending |
| line-3 | line-3-0262-0224-s010714 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**47 trainsets exceed the reference platform envelope**, requiring **2,303.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0204-0204-s000000 | 5 | 2 | 3 | 147.0 |
| line-1-0316-0332-s003915 | 10 | 2 | 8 | 392.0 |
| line-1-0386-0374-s005818 | 10 | 4 | 6 | 294.0 |
| line-1-0728-0413-s014154 | 4 | 2 | 2 | 98.0 |
| line-2-0354-0390-s009970 | 3 | 2 | 1 | 49.0 |
| line-2-0386-0374-s008743 | 6 | 4 | 2 | 98.0 |
| line-2-0456-0355-s006845 | 7 | 2 | 5 | 245.0 |
| line-2-0706-0380-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0122-0114-s014860 | 3 | 2 | 1 | 49.0 |
| line-3-0262-0224-s010714 | 7 | 2 | 5 | 245.0 |
| line-3-0386-0374-s006595 | 8 | 4 | 4 | 196.0 |
| line-3-0435-0449-s004369 | 8 | 2 | 6 | 294.0 |
| line-3-0586-0588-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Naivasha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
