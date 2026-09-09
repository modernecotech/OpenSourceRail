# Station and depot overnight allocation

Plan: **38 trainsets at stations + 64 at depots = 102 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0933-0407-s017459 | 64 | 3,808.0 | 16 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0431-0673-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0515-0619-s003018 | station | forward | revenue | 1 |
| line-1 | line-1-0515-0619-s003018 | station | reverse | revenue | 1 |
| line-1 | line-1-0559-0554-s005270 | station | forward | revenue | 1 |
| line-1 | line-1-0559-0554-s005270 | station | reverse | revenue | 1 |
| line-1 | line-1-0633-0594-s007140 | station | forward | revenue | 1 |
| line-1 | line-1-0633-0594-s007140 | station | reverse | revenue | 1 |
| line-1 | line-1-0725-0594-s009030 | station | forward | revenue | 1 |
| line-1 | line-1-0725-0594-s009030 | station | reverse | revenue | 1 |
| line-1 | line-1-0938-0541-s014730 | station | forward | revenue | 1 |
| line-1 | line-1-0938-0541-s014730 | station | reverse | revenue | 1 |
| line-1 | line-1-1002-0556-s016349 | station | reverse | revenue | 2 |
| line-2 | line-2-0437-0770-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0485-0682-s003011 | station | forward | revenue | 1 |
| line-2 | line-2-0485-0682-s003011 | station | reverse | revenue | 1 |
| line-2 | line-2-0559-0554-s007478 | station | forward | revenue | 1 |
| line-2 | line-2-0559-0554-s007478 | station | reverse | revenue | 1 |
| line-2 | line-2-0572-0613-s006028 | station | forward | revenue | 1 |
| line-2 | line-2-0572-0613-s006028 | station | reverse | revenue | 1 |
| line-2 | line-2-0620-0530-s009045 | station | forward | revenue | 1 |
| line-2 | line-2-0620-0530-s009045 | station | reverse | revenue | 1 |
| line-2 | line-2-0723-0472-s012068 | station | forward | revenue | 1 |
| line-2 | line-2-0723-0472-s012068 | station | reverse | revenue | 1 |
| line-2 | line-2-0933-0407-s017459 | station | reverse | revenue | 2 |
| line-3 | line-3-0578-0800-s013439 | station | reverse | revenue | 2 |
| line-3 | line-3-0669-0719-s010031 | station | forward | revenue | 1 |
| line-3 | line-3-0669-0719-s010031 | station | reverse | revenue | 1 |
| line-3 | line-3-0757-0717-s007018 | station | forward | revenue | 1 |
| line-3 | line-3-0757-0717-s007018 | station | reverse | revenue | 1 |
| line-3 | line-3-0878-0642-s003518 | station | forward | revenue | 1 |
| line-3 | line-3-0878-0642-s003518 | station | reverse | revenue | 1 |
| line-3 | line-3-0999-0567-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0933-0407-s017459 | depot | — | revenue | 18 |
| line-1 | line-2-0933-0407-s017459 | depot | — | spare | 3 |
| line-1 | line-2-0933-0407-s017459 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0933-0407-s017459 | depot | — | revenue | 19 |
| line-2 | line-2-0933-0407-s017459 | depot | — | spare | 3 |
| line-2 | line-2-0933-0407-s017459 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0933-0407-s017459 | depot | — | revenue | 16 |
| line-3 | line-2-0933-0407-s017459 | depot | — | spare | 2 |
| line-3 | line-2-0933-0407-s017459 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (22 trains), line-3 (19 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **102 trainsets at 19 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **91 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **64 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0431-0673-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0515-0619-s003018 | forward | revenue | 3 | pending |
| line-1 | line-1-0515-0619-s003018 | reverse | revenue | 3 | pending |
| line-1 | line-1-0559-0554-s005270 | forward | revenue | 3 | pending |
| line-1 | line-1-0559-0554-s005270 | reverse | revenue | 3 | pending |
| line-1 | line-1-0633-0594-s007140 | forward | revenue | 3 | pending |
| line-1 | line-1-0633-0594-s007140 | reverse | revenue | 3 | pending |
| line-1 | line-1-0725-0594-s009030 | forward | revenue | 3 | pending |
| line-1 | line-1-0725-0594-s009030 | reverse | revenue | 2 | pending |
| line-1 | line-1-0938-0541-s014730 | forward | revenue | 2 | pending |
| line-1 | line-1-0938-0541-s014730 | reverse | revenue | 2 | pending |
| line-1 | line-1-1002-0556-s016349 | reverse | revenue | 2 | pending |
| line-1 | line-1-0725-0594-s009030 | reverse | spare | 1 | pending |
| line-1 | line-1-0938-0541-s014730 | forward | spare | 1 | pending |
| line-1 | line-1-0938-0541-s014730 | reverse | spare | 1 | pending |
| line-1 | line-1-1002-0556-s016349 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0437-0770-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0485-0682-s003011 | forward | revenue | 3 | pending |
| line-2 | line-2-0485-0682-s003011 | reverse | revenue | 3 | pending |
| line-2 | line-2-0572-0613-s006028 | forward | revenue | 3 | pending |
| line-2 | line-2-0572-0613-s006028 | reverse | revenue | 3 | pending |
| line-2 | line-2-0559-0554-s007478 | forward | revenue | 3 | pending |
| line-2 | line-2-0559-0554-s007478 | reverse | revenue | 3 | pending |
| line-2 | line-2-0620-0530-s009045 | forward | revenue | 3 | pending |
| line-2 | line-2-0620-0530-s009045 | reverse | revenue | 3 | pending |
| line-2 | line-2-0723-0472-s012068 | forward | revenue | 2 | pending |
| line-2 | line-2-0723-0472-s012068 | reverse | revenue | 2 | pending |
| line-2 | line-2-0933-0407-s017459 | reverse | revenue | 2 | pending |
| line-2 | line-2-0723-0472-s012068 | forward | spare | 1 | pending |
| line-2 | line-2-0723-0472-s012068 | reverse | spare | 1 | pending |
| line-2 | line-2-0933-0407-s017459 | reverse | spare | 1 | pending |
| line-2 | line-2-0437-0770-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0999-0567-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0878-0642-s003518 | forward | revenue | 4 | pending |
| line-3 | line-3-0878-0642-s003518 | reverse | revenue | 3 | pending |
| line-3 | line-3-0757-0717-s007018 | forward | revenue | 3 | pending |
| line-3 | line-3-0757-0717-s007018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0669-0719-s010031 | forward | revenue | 3 | pending |
| line-3 | line-3-0669-0719-s010031 | reverse | revenue | 3 | pending |
| line-3 | line-3-0578-0800-s013439 | reverse | revenue | 3 | pending |
| line-3 | line-3-0878-0642-s003518 | reverse | spare | 1 | pending |
| line-3 | line-3-0757-0717-s007018 | forward | spare | 1 | pending |
| line-3 | line-3-0757-0717-s007018 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**60 trainsets exceed the reference platform envelope**, requiring **3,570.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0431-0673-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0515-0619-s003018 | 6 | 2 | 4 | 238.0 |
| line-1-0559-0554-s005270 | 6 | 4 | 2 | 119.0 |
| line-1-0633-0594-s007140 | 6 | 2 | 4 | 238.0 |
| line-1-0725-0594-s009030 | 6 | 2 | 4 | 238.0 |
| line-1-0938-0541-s014730 | 6 | 2 | 4 | 238.0 |
| line-1-1002-0556-s016349 | 3 | 2 | 1 | 59.5 |
| line-2-0437-0770-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0485-0682-s003011 | 6 | 2 | 4 | 238.0 |
| line-2-0559-0554-s007478 | 6 | 4 | 2 | 119.0 |
| line-2-0572-0613-s006028 | 6 | 2 | 4 | 238.0 |
| line-2-0620-0530-s009045 | 6 | 2 | 4 | 238.0 |
| line-2-0723-0472-s012068 | 6 | 2 | 4 | 238.0 |
| line-2-0933-0407-s017459 | 3 | 2 | 1 | 59.5 |
| line-3-0578-0800-s013439 | 3 | 2 | 1 | 59.5 |
| line-3-0669-0719-s010031 | 6 | 2 | 4 | 238.0 |
| line-3-0757-0717-s007018 | 8 | 2 | 6 | 357.0 |
| line-3-0878-0642-s003518 | 8 | 2 | 6 | 357.0 |
| line-3-0999-0567-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/El-Obeid/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
