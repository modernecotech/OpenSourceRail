# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 122 at depots = 164 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0512-0958-s016444 | line-1 | declared-depot | 39 | 2,320.5 | 7 |
| line-2-0344-0606-s000000 | line-2 | declared-depot | 33 | 1,963.5 | 7 |
| line-3-0738-0736-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |
| line-4-0562-0554-s000000 | line-4 | declared-depot | 10 | 595.0 | 2 |
| line-5-0437-0586-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0512-0958-s016444 | station | reverse | revenue | 2 |
| line-1 | line-1-0544-0847-s013853 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0847-s013853 | station | reverse | revenue | 1 |
| line-1 | line-1-0643-0634-s008679 | station | forward | revenue | 1 |
| line-1 | line-1-0643-0634-s008679 | station | reverse | revenue | 1 |
| line-1 | line-1-0681-0553-s006709 | station | forward | revenue | 1 |
| line-1 | line-1-0681-0553-s006709 | station | reverse | revenue | 1 |
| line-1 | line-1-0809-0277-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0344-0606-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0437-0586-s002503 | station | forward | revenue | 1 |
| line-2 | line-2-0437-0586-s002503 | station | reverse | revenue | 1 |
| line-2 | line-2-0562-0554-s006268 | station | forward | revenue | 1 |
| line-2 | line-2-0562-0554-s006268 | station | reverse | revenue | 1 |
| line-2 | line-2-0590-0554-s006828 | station | forward | revenue | 1 |
| line-2 | line-2-0590-0554-s006828 | station | reverse | revenue | 1 |
| line-2 | line-2-0681-0553-s008833 | station | forward | revenue | 1 |
| line-2 | line-2-0681-0553-s008833 | station | reverse | revenue | 1 |
| line-2 | line-2-0797-0648-s013162 | station | forward | revenue | 1 |
| line-2 | line-2-0797-0648-s013162 | station | reverse | revenue | 1 |
| line-2 | line-2-0890-0681-s015312 | station | reverse | revenue | 2 |
| line-3 | line-3-0483-0321-s011945 | station | reverse | revenue | 2 |
| line-3 | line-3-0483-0466-s009045 | station | forward | revenue | 1 |
| line-3 | line-3-0483-0466-s009045 | station | reverse | revenue | 1 |
| line-3 | line-3-0590-0554-s005930 | station | forward | revenue | 1 |
| line-3 | line-3-0590-0554-s005930 | station | reverse | revenue | 1 |
| line-3 | line-3-0643-0634-s003652 | station | forward | revenue | 1 |
| line-3 | line-3-0643-0634-s003652 | station | reverse | revenue | 1 |
| line-3 | line-3-0738-0736-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0489-0713-s004154 | station | reverse | revenue | 2 |
| line-4 | line-4-0562-0554-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0437-0586-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0463-0787-s005001 | station | reverse | revenue | 2 |
| line-1 | line-1-0512-0958-s016444 | depot | — | revenue | 34 |
| line-1 | line-1-0512-0958-s016444 | depot | — | spare | 4 |
| line-1 | line-1-0512-0958-s016444 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0344-0606-s000000 | depot | — | revenue | 28 |
| line-2 | line-2-0344-0606-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0344-0606-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0738-0736-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0738-0736-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0738-0736-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0562-0554-s000000 | depot | — | revenue | 8 |
| line-4 | line-4-0562-0554-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0562-0554-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0437-0586-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0437-0586-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0437-0586-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nyala-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **164 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **146 revenue, 13 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **122 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0809-0277-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0681-0553-s006709 | forward | revenue | 6 | pending |
| line-1 | line-1-0681-0553-s006709 | reverse | revenue | 6 | pending |
| line-1 | line-1-0643-0634-s008679 | forward | revenue | 6 | pending |
| line-1 | line-1-0643-0634-s008679 | reverse | revenue | 5 | pending |
| line-1 | line-1-0544-0847-s013853 | forward | revenue | 5 | pending |
| line-1 | line-1-0544-0847-s013853 | reverse | revenue | 5 | pending |
| line-1 | line-1-0512-0958-s016444 | reverse | revenue | 5 | pending |
| line-1 | line-1-0643-0634-s008679 | reverse | spare | 1 | pending |
| line-1 | line-1-0544-0847-s013853 | forward | spare | 1 | pending |
| line-1 | line-1-0544-0847-s013853 | reverse | spare | 1 | pending |
| line-1 | line-1-0512-0958-s016444 | reverse | spare | 1 | pending |
| line-1 | line-1-0809-0277-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0344-0606-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0437-0586-s002503 | forward | revenue | 4 | pending |
| line-2 | line-2-0437-0586-s002503 | reverse | revenue | 4 | pending |
| line-2 | line-2-0562-0554-s006268 | forward | revenue | 4 | pending |
| line-2 | line-2-0562-0554-s006268 | reverse | revenue | 4 | pending |
| line-2 | line-2-0590-0554-s006828 | forward | revenue | 4 | pending |
| line-2 | line-2-0590-0554-s006828 | reverse | revenue | 3 | pending |
| line-2 | line-2-0681-0553-s008833 | forward | revenue | 3 | pending |
| line-2 | line-2-0681-0553-s008833 | reverse | revenue | 3 | pending |
| line-2 | line-2-0797-0648-s013162 | forward | revenue | 3 | pending |
| line-2 | line-2-0797-0648-s013162 | reverse | revenue | 3 | pending |
| line-2 | line-2-0890-0681-s015312 | reverse | revenue | 3 | pending |
| line-2 | line-2-0590-0554-s006828 | reverse | spare | 1 | pending |
| line-2 | line-2-0681-0553-s008833 | forward | spare | 1 | pending |
| line-2 | line-2-0681-0553-s008833 | reverse | spare | 1 | pending |
| line-2 | line-2-0797-0648-s013162 | forward | spare | 1 | pending |
| line-2 | line-2-0797-0648-s013162 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0738-0736-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0643-0634-s003652 | forward | revenue | 5 | pending |
| line-3 | line-3-0643-0634-s003652 | reverse | revenue | 4 | pending |
| line-3 | line-3-0590-0554-s005930 | forward | revenue | 4 | pending |
| line-3 | line-3-0590-0554-s005930 | reverse | revenue | 4 | pending |
| line-3 | line-3-0483-0466-s009045 | forward | revenue | 4 | pending |
| line-3 | line-3-0483-0466-s009045 | reverse | revenue | 4 | pending |
| line-3 | line-3-0483-0321-s011945 | reverse | revenue | 4 | pending |
| line-3 | line-3-0643-0634-s003652 | reverse | spare | 1 | pending |
| line-3 | line-3-0590-0554-s005930 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0554-s005930 | reverse | spare | 1 | pending |
| line-3 | line-3-0483-0466-s009045 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0562-0554-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0489-0713-s004154 | reverse | revenue | 6 | pending |
| line-4 | line-4-0562-0554-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0489-0713-s004154 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0437-0586-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0463-0787-s005001 | reverse | revenue | 7 | pending |
| line-5 | line-5-0437-0586-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0463-0787-s005001 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**106 trainsets exceed the reference platform envelope**, requiring **6,307.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0512-0958-s016444 | 6 | 2 | 4 | 238.0 |
| line-1-0544-0847-s013853 | 12 | 2 | 10 | 595.0 |
| line-1-0643-0634-s008679 | 12 | 4 | 8 | 476.0 |
| line-1-0681-0553-s006709 | 12 | 4 | 8 | 476.0 |
| line-1-0809-0277-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0344-0606-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0437-0586-s002503 | 8 | 4 | 4 | 238.0 |
| line-2-0562-0554-s006268 | 8 | 4 | 4 | 238.0 |
| line-2-0590-0554-s006828 | 8 | 4 | 4 | 238.0 |
| line-2-0681-0553-s008833 | 8 | 4 | 4 | 238.0 |
| line-2-0797-0648-s013162 | 8 | 2 | 6 | 357.0 |
| line-2-0890-0681-s015312 | 3 | 2 | 1 | 59.5 |
| line-3-0483-0321-s011945 | 4 | 2 | 2 | 119.0 |
| line-3-0483-0466-s009045 | 9 | 2 | 7 | 416.5 |
| line-3-0590-0554-s005930 | 10 | 4 | 6 | 357.0 |
| line-3-0643-0634-s003652 | 10 | 4 | 6 | 357.0 |
| line-3-0738-0736-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0489-0713-s004154 | 7 | 2 | 5 | 297.5 |
| line-4-0562-0554-s000000 | 7 | 2 | 5 | 297.5 |
| line-5-0437-0586-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0463-0787-s005001 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Nyala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
