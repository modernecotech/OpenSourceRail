# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 54 at depots = 98 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0252-0247-s000000 | line-1 | declared-depot | 11 | 539.0 | 4 |
| line-2-0388-0126-s014801 | line-2 | declared-depot | 20 | 980.0 | 5 |
| line-3-0109-0523-s000000 | line-3 | declared-depot | 14 | 686.0 | 5 |
| line-4-0237-0388-s000000 | line-4 | declared-depot | 9 | 441.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0252-0247-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0368-0385-s004647 | station | forward | revenue | 1 |
| line-1 | line-1-0368-0385-s004647 | station | reverse | revenue | 1 |
| line-1 | line-1-0372-0379-s004800 | station | forward | revenue | 1 |
| line-1 | line-1-0372-0379-s004800 | station | reverse | revenue | 1 |
| line-1 | line-1-0374-0378-s004877 | station | forward | revenue | 1 |
| line-1 | line-1-0374-0378-s004877 | station | reverse | revenue | 1 |
| line-1 | line-1-0379-0381-s005002 | station | forward | revenue | 1 |
| line-1 | line-1-0379-0381-s005002 | station | reverse | revenue | 1 |
| line-1 | line-1-0385-0384-s005198 | station | forward | revenue | 1 |
| line-1 | line-1-0385-0384-s005198 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0499-s009960 | station | reverse | revenue | 2 |
| line-2 | line-2-0384-0384-s008544 | station | forward | revenue | 1 |
| line-2 | line-2-0384-0384-s008544 | station | reverse | revenue | 1 |
| line-2 | line-2-0388-0126-s014801 | station | reverse | revenue | 2 |
| line-2 | line-2-0388-0383-s008632 | station | forward | revenue | 1 |
| line-2 | line-2-0388-0383-s008632 | station | reverse | revenue | 1 |
| line-2 | line-2-0405-0744-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0421-0544-s004738 | station | forward | revenue | 1 |
| line-2 | line-2-0421-0544-s004738 | station | reverse | revenue | 1 |
| line-3 | line-3-0109-0523-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0237-0388-s004328 | station | forward | revenue | 1 |
| line-3 | line-3-0237-0388-s004328 | station | reverse | revenue | 1 |
| line-3 | line-3-0368-0385-s007867 | station | forward | revenue | 1 |
| line-3 | line-3-0368-0385-s007867 | station | reverse | revenue | 1 |
| line-3 | line-3-0372-0379-s008021 | station | forward | revenue | 1 |
| line-3 | line-3-0372-0379-s008021 | station | reverse | revenue | 1 |
| line-3 | line-3-0379-0381-s008194 | station | forward | revenue | 1 |
| line-3 | line-3-0379-0381-s008194 | station | reverse | revenue | 1 |
| line-3 | line-3-0383-0383-s008290 | station | forward | revenue | 1 |
| line-3 | line-3-0383-0383-s008290 | station | reverse | revenue | 1 |
| line-3 | line-3-0386-0384-s008399 | station | forward | revenue | 1 |
| line-3 | line-3-0386-0384-s008399 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0386-s012864 | station | reverse | revenue | 2 |
| line-4 | line-4-0237-0388-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0338-0536-s005882 | station | reverse | revenue | 2 |
| line-1 | line-1-0252-0247-s000000 | depot | — | revenue | 8 |
| line-1 | line-1-0252-0247-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0252-0247-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0388-0126-s014801 | depot | — | revenue | 17 |
| line-2 | line-2-0388-0126-s014801 | depot | — | spare | 2 |
| line-2 | line-2-0388-0126-s014801 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0109-0523-s000000 | depot | — | revenue | 11 |
| line-3 | line-3-0109-0523-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0109-0523-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0237-0388-s000000 | depot | — | revenue | 7 |
| line-4 | line-4-0237-0388-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0237-0388-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/arua-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **98 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **87 revenue, 7 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **54 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0252-0247-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0368-0385-s004647 | forward | revenue | 2 | pending |
| line-1 | line-1-0368-0385-s004647 | reverse | revenue | 2 | pending |
| line-1 | line-1-0372-0379-s004800 | forward | revenue | 2 | pending |
| line-1 | line-1-0372-0379-s004800 | reverse | revenue | 2 | pending |
| line-1 | line-1-0374-0378-s004877 | forward | revenue | 2 | pending |
| line-1 | line-1-0374-0378-s004877 | reverse | revenue | 2 | pending |
| line-1 | line-1-0379-0381-s005002 | forward | revenue | 2 | pending |
| line-1 | line-1-0379-0381-s005002 | reverse | revenue | 2 | pending |
| line-1 | line-1-0385-0384-s005198 | forward | revenue | 2 | pending |
| line-1 | line-1-0385-0384-s005198 | reverse | revenue | 1 | pending |
| line-1 | line-1-0550-0499-s009960 | reverse | revenue | 1 | pending |
| line-1 | line-1-0385-0384-s005198 | reverse | spare | 1 | pending |
| line-1 | line-1-0550-0499-s009960 | reverse | spare | 1 | pending |
| line-1 | line-1-0252-0247-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0405-0744-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0421-0544-s004738 | forward | revenue | 4 | pending |
| line-2 | line-2-0421-0544-s004738 | reverse | revenue | 4 | pending |
| line-2 | line-2-0384-0384-s008544 | forward | revenue | 3 | pending |
| line-2 | line-2-0384-0384-s008544 | reverse | revenue | 3 | pending |
| line-2 | line-2-0388-0383-s008632 | forward | revenue | 3 | pending |
| line-2 | line-2-0388-0383-s008632 | reverse | revenue | 3 | pending |
| line-2 | line-2-0388-0126-s014801 | reverse | revenue | 3 | pending |
| line-2 | line-2-0384-0384-s008544 | forward | spare | 1 | pending |
| line-2 | line-2-0384-0384-s008544 | reverse | spare | 1 | pending |
| line-2 | line-2-0388-0383-s008632 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0109-0523-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0237-0388-s004328 | forward | revenue | 2 | pending |
| line-3 | line-3-0237-0388-s004328 | reverse | revenue | 2 | pending |
| line-3 | line-3-0368-0385-s007867 | forward | revenue | 2 | pending |
| line-3 | line-3-0368-0385-s007867 | reverse | revenue | 2 | pending |
| line-3 | line-3-0372-0379-s008021 | forward | revenue | 2 | pending |
| line-3 | line-3-0372-0379-s008021 | reverse | revenue | 2 | pending |
| line-3 | line-3-0379-0381-s008194 | forward | revenue | 2 | pending |
| line-3 | line-3-0379-0381-s008194 | reverse | revenue | 2 | pending |
| line-3 | line-3-0383-0383-s008290 | forward | revenue | 2 | pending |
| line-3 | line-3-0383-0383-s008290 | reverse | revenue | 2 | pending |
| line-3 | line-3-0386-0384-s008399 | forward | revenue | 2 | pending |
| line-3 | line-3-0386-0384-s008399 | reverse | revenue | 2 | pending |
| line-3 | line-3-0549-0386-s012864 | reverse | revenue | 1 | pending |
| line-3 | line-3-0549-0386-s012864 | reverse | spare | 1 | pending |
| line-3 | line-3-0109-0523-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0237-0388-s004328 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0237-0388-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0338-0536-s005882 | reverse | revenue | 5 | pending |
| line-4 | line-4-0338-0536-s005882 | reverse | spare | 1 | pending |
| line-4 | line-4-0237-0388-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**28 trainsets exceed the reference platform envelope**, requiring **1,372.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0252-0247-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0368-0385-s004647 | 4 | 4 | 0 | 0.0 |
| line-1-0372-0379-s004800 | 4 | 4 | 0 | 0.0 |
| line-1-0374-0378-s004877 | 4 | 4 | 0 | 0.0 |
| line-1-0379-0381-s005002 | 4 | 4 | 0 | 0.0 |
| line-1-0385-0384-s005198 | 4 | 4 | 0 | 0.0 |
| line-1-0550-0499-s009960 | 2 | 2 | 0 | 0.0 |
| line-2-0384-0384-s008544 | 8 | 4 | 4 | 196.0 |
| line-2-0388-0126-s014801 | 3 | 2 | 1 | 49.0 |
| line-2-0388-0383-s008632 | 7 | 4 | 3 | 147.0 |
| line-2-0405-0744-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0421-0544-s004738 | 8 | 2 | 6 | 294.0 |
| line-3-0109-0523-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0237-0388-s004328 | 5 | 4 | 1 | 49.0 |
| line-3-0368-0385-s007867 | 4 | 4 | 0 | 0.0 |
| line-3-0372-0379-s008021 | 4 | 4 | 0 | 0.0 |
| line-3-0379-0381-s008194 | 4 | 4 | 0 | 0.0 |
| line-3-0383-0383-s008290 | 4 | 4 | 0 | 0.0 |
| line-3-0386-0384-s008399 | 4 | 4 | 0 | 0.0 |
| line-3-0549-0386-s012864 | 2 | 2 | 0 | 0.0 |
| line-4-0237-0388-s000000 | 7 | 2 | 5 | 245.0 |
| line-4-0338-0536-s005882 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Arua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
