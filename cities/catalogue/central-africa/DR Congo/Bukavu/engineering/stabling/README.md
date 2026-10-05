# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 125 at depots = 159 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0325-0925-s000000 | line-1 | declared-depot | 33 | 1,963.5 | 7 |
| line-2-0859-1060-s020095 | line-2 | declared-depot | 52 | 3,094.0 | 9 |
| line-3-0764-0574-s000000 | line-3 | declared-depot | 40 | 2,380.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0325-0925-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0401-0809-s003020 | station | forward | revenue | 1 |
| line-1 | line-1-0401-0809-s003020 | station | reverse | revenue | 1 |
| line-1 | line-1-0469-0693-s006032 | station | forward | revenue | 1 |
| line-1 | line-1-0469-0693-s006032 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0575-s009089 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0575-s009089 | station | reverse | revenue | 1 |
| line-1 | line-1-0590-0488-s011345 | station | forward | revenue | 1 |
| line-1 | line-1-0590-0488-s011345 | station | reverse | revenue | 1 |
| line-1 | line-1-0642-0400-s013595 | station | reverse | revenue | 2 |
| line-2 | line-2-0309-0394-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0392-0499-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0392-0499-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0475-0606-s006037 | station | forward | revenue | 1 |
| line-2 | line-2-0475-0606-s006037 | station | reverse | revenue | 1 |
| line-2 | line-2-0572-0729-s009547 | station | forward | revenue | 1 |
| line-2 | line-2-0572-0729-s009547 | station | reverse | revenue | 1 |
| line-2 | line-2-0859-1060-s020095 | station | reverse | revenue | 2 |
| line-3 | line-3-0104-0927-s016891 | station | reverse | revenue | 2 |
| line-3 | line-3-0270-0813-s012083 | station | forward | revenue | 1 |
| line-3 | line-3-0270-0813-s012083 | station | reverse | revenue | 1 |
| line-3 | line-3-0393-0754-s009075 | station | forward | revenue | 1 |
| line-3 | line-3-0393-0754-s009075 | station | reverse | revenue | 1 |
| line-3 | line-3-0517-0694-s006051 | station | forward | revenue | 1 |
| line-3 | line-3-0517-0694-s006051 | station | reverse | revenue | 1 |
| line-3 | line-3-0641-0634-s003027 | station | forward | revenue | 1 |
| line-3 | line-3-0641-0634-s003027 | station | reverse | revenue | 1 |
| line-3 | line-3-0764-0574-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0325-0925-s000000 | depot | — | revenue | 28 |
| line-1 | line-1-0325-0925-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0325-0925-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0859-1060-s020095 | depot | — | revenue | 46 |
| line-2 | line-2-0859-1060-s020095 | depot | — | spare | 5 |
| line-2 | line-2-0859-1060-s020095 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0764-0574-s000000 | depot | — | revenue | 35 |
| line-3 | line-3-0764-0574-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0764-0574-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/bukavu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **159 trainsets at 17 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **143 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **125 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0325-0925-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0809-s003020 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0809-s003020 | reverse | revenue | 4 | pending |
| line-1 | line-1-0469-0693-s006032 | forward | revenue | 4 | pending |
| line-1 | line-1-0469-0693-s006032 | reverse | revenue | 4 | pending |
| line-1 | line-1-0539-0575-s009089 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0575-s009089 | reverse | revenue | 4 | pending |
| line-1 | line-1-0590-0488-s011345 | forward | revenue | 4 | pending |
| line-1 | line-1-0590-0488-s011345 | reverse | revenue | 4 | pending |
| line-1 | line-1-0642-0400-s013595 | reverse | revenue | 4 | pending |
| line-1 | line-1-0325-0925-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0401-0809-s003020 | forward | spare | 1 | pending |
| line-1 | line-1-0401-0809-s003020 | reverse | spare | 1 | pending |
| line-1 | line-1-0469-0693-s006032 | forward | spare | 1 | pending |
| line-1 | line-1-0469-0693-s006032 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0309-0394-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0392-0499-s003010 | forward | revenue | 7 | pending |
| line-2 | line-2-0392-0499-s003010 | reverse | revenue | 7 | pending |
| line-2 | line-2-0475-0606-s006037 | forward | revenue | 7 | pending |
| line-2 | line-2-0475-0606-s006037 | reverse | revenue | 7 | pending |
| line-2 | line-2-0572-0729-s009547 | forward | revenue | 7 | pending |
| line-2 | line-2-0572-0729-s009547 | reverse | revenue | 7 | pending |
| line-2 | line-2-0859-1060-s020095 | reverse | revenue | 7 | pending |
| line-2 | line-2-0309-0394-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0392-0499-s003010 | forward | spare | 1 | pending |
| line-2 | line-2-0392-0499-s003010 | reverse | spare | 1 | pending |
| line-2 | line-2-0475-0606-s006037 | forward | spare | 1 | pending |
| line-2 | line-2-0475-0606-s006037 | reverse | spare | 1 | pending |
| line-2 | line-2-0572-0729-s009547 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0764-0574-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0641-0634-s003027 | forward | revenue | 5 | pending |
| line-3 | line-3-0641-0634-s003027 | reverse | revenue | 5 | pending |
| line-3 | line-3-0517-0694-s006051 | forward | revenue | 5 | pending |
| line-3 | line-3-0517-0694-s006051 | reverse | revenue | 5 | pending |
| line-3 | line-3-0393-0754-s009075 | forward | revenue | 5 | pending |
| line-3 | line-3-0393-0754-s009075 | reverse | revenue | 5 | pending |
| line-3 | line-3-0270-0813-s012083 | forward | revenue | 4 | pending |
| line-3 | line-3-0270-0813-s012083 | reverse | revenue | 4 | pending |
| line-3 | line-3-0104-0927-s016891 | reverse | revenue | 4 | pending |
| line-3 | line-3-0270-0813-s012083 | forward | spare | 1 | pending |
| line-3 | line-3-0270-0813-s012083 | reverse | spare | 1 | pending |
| line-3 | line-3-0104-0927-s016891 | reverse | spare | 1 | pending |
| line-3 | line-3-0764-0574-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0641-0634-s003027 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**125 trainsets exceed the reference platform envelope**, requiring **7,437.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0325-0925-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0401-0809-s003020 | 10 | 2 | 8 | 476.0 |
| line-1-0469-0693-s006032 | 10 | 2 | 8 | 476.0 |
| line-1-0539-0575-s009089 | 8 | 2 | 6 | 357.0 |
| line-1-0590-0488-s011345 | 8 | 2 | 6 | 357.0 |
| line-1-0642-0400-s013595 | 4 | 2 | 2 | 119.0 |
| line-2-0309-0394-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0392-0499-s003010 | 16 | 2 | 14 | 833.0 |
| line-2-0475-0606-s006037 | 16 | 2 | 14 | 833.0 |
| line-2-0572-0729-s009547 | 15 | 2 | 13 | 773.5 |
| line-2-0859-1060-s020095 | 7 | 2 | 5 | 297.5 |
| line-3-0104-0927-s016891 | 5 | 2 | 3 | 178.5 |
| line-3-0270-0813-s012083 | 10 | 2 | 8 | 476.0 |
| line-3-0393-0754-s009075 | 10 | 2 | 8 | 476.0 |
| line-3-0517-0694-s006051 | 10 | 2 | 8 | 476.0 |
| line-3-0641-0634-s003027 | 11 | 2 | 9 | 535.5 |
| line-3-0764-0574-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Bukavu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
