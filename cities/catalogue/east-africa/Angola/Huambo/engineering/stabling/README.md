# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 104 at depots = 136 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0361-1048-s018712 | line-1 | declared-depot | 49 | 2,915.5 | 9 |
| line-2-0486-0817-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0267-0585-s000000 | line-3 | declared-depot | 33 | 1,963.5 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0361-1048-s018712 | station | reverse | revenue | 2 |
| line-1 | line-1-0405-0701-s010827 | station | forward | revenue | 1 |
| line-1 | line-1-0405-0701-s010827 | station | reverse | revenue | 1 |
| line-1 | line-1-0441-0553-s007534 | station | forward | revenue | 1 |
| line-1 | line-1-0441-0553-s007534 | station | reverse | revenue | 1 |
| line-1 | line-1-0474-0418-s004525 | station | forward | revenue | 1 |
| line-1 | line-1-0474-0418-s004525 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0215-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0486-0817-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0550-0697-s003000 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0697-s003000 | station | reverse | revenue | 1 |
| line-2 | line-2-0614-0578-s006016 | station | forward | revenue | 1 |
| line-2 | line-2-0614-0578-s006016 | station | reverse | revenue | 1 |
| line-2 | line-2-0656-0499-s007979 | station | forward | revenue | 1 |
| line-2 | line-2-0656-0499-s007979 | station | reverse | revenue | 1 |
| line-2 | line-2-0698-0421-s009957 | station | reverse | revenue | 2 |
| line-3 | line-3-0267-0585-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0403-0618-s003017 | station | forward | revenue | 1 |
| line-3 | line-3-0403-0618-s003017 | station | reverse | revenue | 1 |
| line-3 | line-3-0540-0650-s006022 | station | forward | revenue | 1 |
| line-3 | line-3-0540-0650-s006022 | station | reverse | revenue | 1 |
| line-3 | line-3-0626-0671-s007916 | station | forward | revenue | 1 |
| line-3 | line-3-0626-0671-s007916 | station | reverse | revenue | 1 |
| line-3 | line-3-0712-0692-s009810 | station | forward | revenue | 1 |
| line-3 | line-3-0712-0692-s009810 | station | reverse | revenue | 1 |
| line-3 | line-3-0883-0735-s013610 | station | reverse | revenue | 2 |
| line-1 | line-1-0361-1048-s018712 | depot | — | revenue | 43 |
| line-1 | line-1-0361-1048-s018712 | depot | — | spare | 5 |
| line-1 | line-1-0361-1048-s018712 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0486-0817-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0486-0817-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0486-0817-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0267-0585-s000000 | depot | — | revenue | 28 |
| line-3 | line-3-0267-0585-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0267-0585-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/huambo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **136 trainsets at 16 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **122 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **104 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0511-0215-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0474-0418-s004525 | forward | revenue | 7 | pending |
| line-1 | line-1-0474-0418-s004525 | reverse | revenue | 7 | pending |
| line-1 | line-1-0441-0553-s007534 | forward | revenue | 7 | pending |
| line-1 | line-1-0441-0553-s007534 | reverse | revenue | 7 | pending |
| line-1 | line-1-0405-0701-s010827 | forward | revenue | 6 | pending |
| line-1 | line-1-0405-0701-s010827 | reverse | revenue | 6 | pending |
| line-1 | line-1-0361-1048-s018712 | reverse | revenue | 6 | pending |
| line-1 | line-1-0405-0701-s010827 | forward | spare | 1 | pending |
| line-1 | line-1-0405-0701-s010827 | reverse | spare | 1 | pending |
| line-1 | line-1-0361-1048-s018712 | reverse | spare | 1 | pending |
| line-1 | line-1-0511-0215-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0474-0418-s004525 | forward | spare | 1 | pending |
| line-1 | line-1-0474-0418-s004525 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0486-0817-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0550-0697-s003000 | forward | revenue | 4 | pending |
| line-2 | line-2-0550-0697-s003000 | reverse | revenue | 4 | pending |
| line-2 | line-2-0614-0578-s006016 | forward | revenue | 4 | pending |
| line-2 | line-2-0614-0578-s006016 | reverse | revenue | 4 | pending |
| line-2 | line-2-0656-0499-s007979 | forward | revenue | 3 | pending |
| line-2 | line-2-0656-0499-s007979 | reverse | revenue | 3 | pending |
| line-2 | line-2-0698-0421-s009957 | reverse | revenue | 3 | pending |
| line-2 | line-2-0656-0499-s007979 | forward | spare | 1 | pending |
| line-2 | line-2-0656-0499-s007979 | reverse | spare | 1 | pending |
| line-2 | line-2-0698-0421-s009957 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0267-0585-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0403-0618-s003017 | forward | revenue | 4 | pending |
| line-3 | line-3-0403-0618-s003017 | reverse | revenue | 4 | pending |
| line-3 | line-3-0540-0650-s006022 | forward | revenue | 4 | pending |
| line-3 | line-3-0540-0650-s006022 | reverse | revenue | 4 | pending |
| line-3 | line-3-0626-0671-s007916 | forward | revenue | 4 | pending |
| line-3 | line-3-0626-0671-s007916 | reverse | revenue | 4 | pending |
| line-3 | line-3-0712-0692-s009810 | forward | revenue | 4 | pending |
| line-3 | line-3-0712-0692-s009810 | reverse | revenue | 4 | pending |
| line-3 | line-3-0883-0735-s013610 | reverse | revenue | 4 | pending |
| line-3 | line-3-0267-0585-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0403-0618-s003017 | forward | spare | 1 | pending |
| line-3 | line-3-0403-0618-s003017 | reverse | spare | 1 | pending |
| line-3 | line-3-0540-0650-s006022 | forward | spare | 1 | pending |
| line-3 | line-3-0540-0650-s006022 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**104 trainsets exceed the reference platform envelope**, requiring **6,188.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0361-1048-s018712 | 7 | 2 | 5 | 297.5 |
| line-1-0405-0701-s010827 | 14 | 2 | 12 | 714.0 |
| line-1-0441-0553-s007534 | 14 | 2 | 12 | 714.0 |
| line-1-0474-0418-s004525 | 16 | 2 | 14 | 833.0 |
| line-1-0511-0215-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0486-0817-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0550-0697-s003000 | 8 | 2 | 6 | 357.0 |
| line-2-0614-0578-s006016 | 8 | 2 | 6 | 357.0 |
| line-2-0656-0499-s007979 | 8 | 2 | 6 | 357.0 |
| line-2-0698-0421-s009957 | 4 | 2 | 2 | 119.0 |
| line-3-0267-0585-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0403-0618-s003017 | 10 | 2 | 8 | 476.0 |
| line-3-0540-0650-s006022 | 10 | 2 | 8 | 476.0 |
| line-3-0626-0671-s007916 | 8 | 2 | 6 | 357.0 |
| line-3-0712-0692-s009810 | 8 | 2 | 6 | 357.0 |
| line-3-0883-0735-s013610 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Huambo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
