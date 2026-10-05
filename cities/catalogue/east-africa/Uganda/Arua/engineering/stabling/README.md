# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 38 at depots = 68 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0252-0247-s000000 | line-1 | declared-depot | 10 | 490.0 | 3 |
| line-2-0388-0126-s013549 | line-2 | declared-depot | 17 | 833.0 | 4 |
| line-3-0109-0523-s000000 | line-3 | declared-depot | 11 | 539.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0252-0247-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0353-0333-s003002 | station | forward | revenue | 1 |
| line-1 | line-1-0353-0333-s003002 | station | reverse | revenue | 1 |
| line-1 | line-1-0409-0380-s004617 | station | forward | revenue | 1 |
| line-1 | line-1-0409-0380-s004617 | station | reverse | revenue | 1 |
| line-1 | line-1-0443-0408-s005599 | station | forward | revenue | 1 |
| line-1 | line-1-0443-0408-s005599 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0499-s008774 | station | reverse | revenue | 2 |
| line-2 | line-2-0388-0126-s013549 | station | reverse | revenue | 2 |
| line-2 | line-2-0405-0744-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0409-0380-s008079 | station | forward | revenue | 1 |
| line-2 | line-2-0409-0380-s008079 | station | reverse | revenue | 1 |
| line-2 | line-2-0414-0414-s007346 | station | forward | revenue | 1 |
| line-2 | line-2-0414-0414-s007346 | station | reverse | revenue | 1 |
| line-2 | line-2-0431-0534-s004805 | station | forward | revenue | 1 |
| line-2 | line-2-0431-0534-s004805 | station | reverse | revenue | 1 |
| line-3 | line-3-0109-0523-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0255-0446-s004056 | station | forward | revenue | 1 |
| line-3 | line-3-0255-0446-s004056 | station | reverse | revenue | 1 |
| line-3 | line-3-0414-0414-s007548 | station | forward | revenue | 1 |
| line-3 | line-3-0414-0414-s007548 | station | reverse | revenue | 1 |
| line-3 | line-3-0443-0408-s008189 | station | forward | revenue | 1 |
| line-3 | line-3-0443-0408-s008189 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0386-s010515 | station | reverse | revenue | 2 |
| line-1 | line-1-0252-0247-s000000 | depot | — | revenue | 8 |
| line-1 | line-1-0252-0247-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0252-0247-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0388-0126-s013549 | depot | — | revenue | 14 |
| line-2 | line-2-0388-0126-s013549 | depot | — | spare | 2 |
| line-2 | line-2-0388-0126-s013549 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0109-0523-s000000 | depot | — | revenue | 9 |
| line-3 | line-3-0109-0523-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0109-0523-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/arua-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **68 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **61 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **38 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0252-0247-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0353-0333-s003002 | forward | revenue | 3 | pending |
| line-1 | line-1-0353-0333-s003002 | reverse | revenue | 2 | pending |
| line-1 | line-1-0409-0380-s004617 | forward | revenue | 2 | pending |
| line-1 | line-1-0409-0380-s004617 | reverse | revenue | 2 | pending |
| line-1 | line-1-0443-0408-s005599 | forward | revenue | 2 | pending |
| line-1 | line-1-0443-0408-s005599 | reverse | revenue | 2 | pending |
| line-1 | line-1-0550-0499-s008774 | reverse | revenue | 2 | pending |
| line-1 | line-1-0353-0333-s003002 | reverse | spare | 1 | pending |
| line-1 | line-1-0409-0380-s004617 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0405-0744-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0431-0534-s004805 | forward | revenue | 3 | pending |
| line-2 | line-2-0431-0534-s004805 | reverse | revenue | 3 | pending |
| line-2 | line-2-0414-0414-s007346 | forward | revenue | 3 | pending |
| line-2 | line-2-0414-0414-s007346 | reverse | revenue | 3 | pending |
| line-2 | line-2-0409-0380-s008079 | forward | revenue | 3 | pending |
| line-2 | line-2-0409-0380-s008079 | reverse | revenue | 3 | pending |
| line-2 | line-2-0388-0126-s013549 | reverse | revenue | 3 | pending |
| line-2 | line-2-0405-0744-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0431-0534-s004805 | forward | spare | 1 | pending |
| line-2 | line-2-0431-0534-s004805 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0109-0523-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0255-0446-s004056 | forward | revenue | 3 | pending |
| line-3 | line-3-0255-0446-s004056 | reverse | revenue | 3 | pending |
| line-3 | line-3-0414-0414-s007548 | forward | revenue | 2 | pending |
| line-3 | line-3-0414-0414-s007548 | reverse | revenue | 2 | pending |
| line-3 | line-3-0443-0408-s008189 | forward | revenue | 2 | pending |
| line-3 | line-3-0443-0408-s008189 | reverse | revenue | 2 | pending |
| line-3 | line-3-0549-0386-s010515 | reverse | revenue | 2 | pending |
| line-3 | line-3-0414-0414-s007548 | forward | spare | 1 | pending |
| line-3 | line-3-0414-0414-s007548 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**26 trainsets exceed the reference platform envelope**, requiring **1,274.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0252-0247-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0353-0333-s003002 | 6 | 2 | 4 | 196.0 |
| line-1-0409-0380-s004617 | 5 | 4 | 1 | 49.0 |
| line-1-0443-0408-s005599 | 4 | 4 | 0 | 0.0 |
| line-1-0550-0499-s008774 | 2 | 2 | 0 | 0.0 |
| line-2-0388-0126-s013549 | 3 | 2 | 1 | 49.0 |
| line-2-0405-0744-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0409-0380-s008079 | 6 | 4 | 2 | 98.0 |
| line-2-0414-0414-s007346 | 6 | 4 | 2 | 98.0 |
| line-2-0431-0534-s004805 | 8 | 2 | 6 | 294.0 |
| line-3-0109-0523-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0255-0446-s004056 | 6 | 2 | 4 | 196.0 |
| line-3-0414-0414-s007548 | 6 | 4 | 2 | 98.0 |
| line-3-0443-0408-s008189 | 4 | 4 | 0 | 0.0 |
| line-3-0549-0386-s010515 | 2 | 2 | 0 | 0.0 |

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
