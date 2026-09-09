# Station and depot overnight allocation

Plan: **28 trainsets at stations + 48 at depots = 76 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0549-0917-s016203 | 48 | 2,856.0 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0549-0917-s016203 | station | reverse | revenue | 2 |
| line-1 | line-1-0552-0554-s006754 | station | forward | revenue | 1 |
| line-1 | line-1-0552-0554-s006754 | station | reverse | revenue | 1 |
| line-1 | line-1-0557-0650-s009110 | station | forward | revenue | 1 |
| line-1 | line-1-0557-0650-s009110 | station | reverse | revenue | 1 |
| line-1 | line-1-0606-0725-s011475 | station | forward | revenue | 1 |
| line-1 | line-1-0606-0725-s011475 | station | reverse | revenue | 1 |
| line-1 | line-1-0612-0513-s004472 | station | forward | revenue | 1 |
| line-1 | line-1-0612-0513-s004472 | station | reverse | revenue | 1 |
| line-1 | line-1-0723-0394-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0451-0393-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0515-0488-s003003 | station | forward | revenue | 1 |
| line-2 | line-2-0515-0488-s003003 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0554-s005451 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0554-s005451 | station | reverse | revenue | 1 |
| line-2 | line-2-0590-0601-s007459 | station | forward | revenue | 1 |
| line-2 | line-2-0590-0601-s007459 | station | reverse | revenue | 1 |
| line-2 | line-2-0671-0611-s009469 | station | reverse | revenue | 2 |
| line-3 | line-3-0527-0619-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0552-0554-s001818 | station | forward | revenue | 1 |
| line-3 | line-3-0552-0554-s001818 | station | reverse | revenue | 1 |
| line-3 | line-3-0720-0400-s008357 | station | reverse | revenue | 2 |
| line-1 | line-1-0549-0917-s016203 | depot | — | revenue | 19 |
| line-1 | line-1-0549-0917-s016203 | depot | — | spare | 3 |
| line-1 | line-1-0549-0917-s016203 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0549-0917-s016203 | depot | — | revenue | 10 |
| line-2 | line-1-0549-0917-s016203 | depot | — | spare | 2 |
| line-2 | line-1-0549-0917-s016203 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0549-0917-s016203 | depot | — | revenue | 10 |
| line-3 | line-1-0549-0917-s016203 | depot | — | spare | 1 |
| line-3 | line-1-0549-0917-s016203 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (13 trains), line-3 (12 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **76 trainsets at 14 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **67 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **48 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0723-0394-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0612-0513-s004472 | forward | revenue | 3 | pending |
| line-1 | line-1-0612-0513-s004472 | reverse | revenue | 3 | pending |
| line-1 | line-1-0552-0554-s006754 | forward | revenue | 3 | pending |
| line-1 | line-1-0552-0554-s006754 | reverse | revenue | 3 | pending |
| line-1 | line-1-0557-0650-s009110 | forward | revenue | 3 | pending |
| line-1 | line-1-0557-0650-s009110 | reverse | revenue | 3 | pending |
| line-1 | line-1-0606-0725-s011475 | forward | revenue | 3 | pending |
| line-1 | line-1-0606-0725-s011475 | reverse | revenue | 3 | pending |
| line-1 | line-1-0549-0917-s016203 | reverse | revenue | 3 | pending |
| line-1 | line-1-0612-0513-s004472 | forward | spare | 1 | pending |
| line-1 | line-1-0612-0513-s004472 | reverse | spare | 1 | pending |
| line-1 | line-1-0552-0554-s006754 | forward | spare | 1 | pending |
| line-1 | line-1-0552-0554-s006754 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0451-0393-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0515-0488-s003003 | forward | revenue | 3 | pending |
| line-2 | line-2-0515-0488-s003003 | reverse | revenue | 3 | pending |
| line-2 | line-2-0552-0554-s005451 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0554-s005451 | reverse | revenue | 2 | pending |
| line-2 | line-2-0590-0601-s007459 | forward | revenue | 2 | pending |
| line-2 | line-2-0590-0601-s007459 | reverse | revenue | 2 | pending |
| line-2 | line-2-0671-0611-s009469 | reverse | revenue | 2 | pending |
| line-2 | line-2-0552-0554-s005451 | reverse | spare | 1 | pending |
| line-2 | line-2-0590-0601-s007459 | forward | spare | 1 | pending |
| line-2 | line-2-0590-0601-s007459 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0527-0619-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0552-0554-s001818 | forward | revenue | 4 | pending |
| line-3 | line-3-0552-0554-s001818 | reverse | revenue | 4 | pending |
| line-3 | line-3-0720-0400-s008357 | reverse | revenue | 4 | pending |
| line-3 | line-3-0527-0619-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0552-0554-s001818 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**42 trainsets exceed the reference platform envelope**, requiring **2,499.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0549-0917-s016203 | 3 | 2 | 1 | 59.5 |
| line-1-0552-0554-s006754 | 8 | 4 | 4 | 238.0 |
| line-1-0557-0650-s009110 | 6 | 2 | 4 | 238.0 |
| line-1-0606-0725-s011475 | 6 | 2 | 4 | 238.0 |
| line-1-0612-0513-s004472 | 8 | 2 | 6 | 357.0 |
| line-1-0723-0394-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0451-0393-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0515-0488-s003003 | 6 | 2 | 4 | 238.0 |
| line-2-0552-0554-s005451 | 6 | 4 | 2 | 119.0 |
| line-2-0590-0601-s007459 | 6 | 2 | 4 | 238.0 |
| line-2-0671-0611-s009469 | 2 | 2 | 0 | 0.0 |
| line-3-0527-0619-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0552-0554-s001818 | 9 | 4 | 5 | 297.5 |
| line-3-0720-0400-s008357 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Uyo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
