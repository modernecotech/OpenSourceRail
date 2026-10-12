# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 95 at depots = 133 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0386-0735-s017499 | line-1 | declared-depot | 40 | 2,380.0 | 8 |
| line-2-0695-0574-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0722-0711-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |
| line-4-0646-0802-s000000 | line-4 | declared-depot | 15 | 892.5 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0386-0735-s017499 | station | reverse | revenue | 2 |
| line-1 | line-1-0444-0665-s015326 | station | forward | revenue | 1 |
| line-1 | line-1-0444-0665-s015326 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0595-s013127 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0595-s013127 | station | reverse | revenue | 1 |
| line-1 | line-1-0559-0529-s010959 | station | forward | revenue | 1 |
| line-1 | line-1-0559-0529-s010959 | station | reverse | revenue | 1 |
| line-1 | line-1-0770-0521-s006409 | station | forward | revenue | 1 |
| line-1 | line-1-0770-0521-s006409 | station | reverse | revenue | 1 |
| line-1 | line-1-1075-0511-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0591-0691-s006012 | station | forward | revenue | 1 |
| line-2 | line-2-0591-0691-s006012 | station | reverse | revenue | 1 |
| line-2 | line-2-0646-0802-s009227 | station | forward | revenue | 1 |
| line-2 | line-2-0646-0802-s009227 | station | reverse | revenue | 1 |
| line-2 | line-2-0652-0585-s000963 | station | forward | revenue | 1 |
| line-2 | line-2-0652-0585-s000963 | station | reverse | revenue | 1 |
| line-2 | line-2-0664-0825-s009859 | station | forward | revenue | 1 |
| line-2 | line-2-0664-0825-s009859 | station | reverse | revenue | 1 |
| line-2 | line-2-0668-0828-s009976 | station | reverse | revenue | 2 |
| line-2 | line-2-0695-0574-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0559-0529-s006236 | station | forward | revenue | 1 |
| line-3 | line-3-0559-0529-s006236 | station | reverse | revenue | 1 |
| line-3 | line-3-0595-0487-s007701 | station | reverse | revenue | 2 |
| line-3 | line-3-0652-0585-s003569 | station | forward | revenue | 1 |
| line-3 | line-3-0652-0585-s003569 | station | reverse | revenue | 1 |
| line-3 | line-3-0722-0711-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0464-0887-s006651 | station | reverse | revenue | 2 |
| line-4 | line-4-0646-0802-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0664-0825-s000696 | station | forward | revenue | 1 |
| line-4 | line-4-0664-0825-s000696 | station | reverse | revenue | 1 |
| line-1 | line-1-0386-0735-s017499 | depot | — | revenue | 35 |
| line-1 | line-1-0386-0735-s017499 | depot | — | spare | 4 |
| line-1 | line-1-0386-0735-s017499 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0695-0574-s000000 | depot | — | revenue | 18 |
| line-2 | line-2-0695-0574-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0695-0574-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0722-0711-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0722-0711-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0722-0711-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0646-0802-s000000 | depot | — | revenue | 13 |
| line-4 | line-4-0646-0802-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0646-0802-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/lobito-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **133 trainsets at 19 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **119 revenue, 10 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **95 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1075-0511-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0770-0521-s006409 | forward | revenue | 5 | pending |
| line-1 | line-1-0770-0521-s006409 | reverse | revenue | 5 | pending |
| line-1 | line-1-0559-0529-s010959 | forward | revenue | 5 | pending |
| line-1 | line-1-0559-0529-s010959 | reverse | revenue | 5 | pending |
| line-1 | line-1-0503-0595-s013127 | forward | revenue | 5 | pending |
| line-1 | line-1-0503-0595-s013127 | reverse | revenue | 5 | pending |
| line-1 | line-1-0444-0665-s015326 | forward | revenue | 4 | pending |
| line-1 | line-1-0444-0665-s015326 | reverse | revenue | 4 | pending |
| line-1 | line-1-0386-0735-s017499 | reverse | revenue | 4 | pending |
| line-1 | line-1-0444-0665-s015326 | forward | spare | 1 | pending |
| line-1 | line-1-0444-0665-s015326 | reverse | spare | 1 | pending |
| line-1 | line-1-0386-0735-s017499 | reverse | spare | 1 | pending |
| line-1 | line-1-1075-0511-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0770-0521-s006409 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0695-0574-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0652-0585-s000963 | forward | revenue | 3 | pending |
| line-2 | line-2-0652-0585-s000963 | reverse | revenue | 3 | pending |
| line-2 | line-2-0591-0691-s006012 | forward | revenue | 3 | pending |
| line-2 | line-2-0591-0691-s006012 | reverse | revenue | 3 | pending |
| line-2 | line-2-0646-0802-s009227 | forward | revenue | 3 | pending |
| line-2 | line-2-0646-0802-s009227 | reverse | revenue | 3 | pending |
| line-2 | line-2-0664-0825-s009859 | forward | revenue | 3 | pending |
| line-2 | line-2-0664-0825-s009859 | reverse | revenue | 3 | pending |
| line-2 | line-2-0668-0828-s009976 | reverse | revenue | 3 | pending |
| line-2 | line-2-0695-0574-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0652-0585-s000963 | forward | spare | 1 | pending |
| line-2 | line-2-0652-0585-s000963 | reverse | spare | 1 | pending |
| line-2 | line-2-0591-0691-s006012 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0722-0711-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0652-0585-s003569 | forward | revenue | 4 | pending |
| line-3 | line-3-0652-0585-s003569 | reverse | revenue | 4 | pending |
| line-3 | line-3-0559-0529-s006236 | forward | revenue | 4 | pending |
| line-3 | line-3-0559-0529-s006236 | reverse | revenue | 4 | pending |
| line-3 | line-3-0595-0487-s007701 | reverse | revenue | 3 | pending |
| line-3 | line-3-0595-0487-s007701 | reverse | spare | 1 | pending |
| line-3 | line-3-0722-0711-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0652-0585-s003569 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0646-0802-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0664-0825-s000696 | forward | revenue | 5 | pending |
| line-4 | line-4-0664-0825-s000696 | reverse | revenue | 5 | pending |
| line-4 | line-4-0464-0887-s006651 | reverse | revenue | 4 | pending |
| line-4 | line-4-0464-0887-s006651 | reverse | spare | 1 | pending |
| line-4 | line-4-0646-0802-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**81 trainsets exceed the reference platform envelope**, requiring **4,819.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0386-0735-s017499 | 5 | 2 | 3 | 178.5 |
| line-1-0444-0665-s015326 | 10 | 2 | 8 | 476.0 |
| line-1-0503-0595-s013127 | 10 | 2 | 8 | 476.0 |
| line-1-0559-0529-s010959 | 10 | 4 | 6 | 357.0 |
| line-1-0770-0521-s006409 | 11 | 2 | 9 | 535.5 |
| line-1-1075-0511-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0591-0691-s006012 | 7 | 2 | 5 | 297.5 |
| line-2-0646-0802-s009227 | 6 | 4 | 2 | 119.0 |
| line-2-0652-0585-s000963 | 8 | 4 | 4 | 238.0 |
| line-2-0664-0825-s009859 | 6 | 4 | 2 | 119.0 |
| line-2-0668-0828-s009976 | 3 | 2 | 1 | 59.5 |
| line-2-0695-0574-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0559-0529-s006236 | 8 | 4 | 4 | 238.0 |
| line-3-0595-0487-s007701 | 4 | 2 | 2 | 119.0 |
| line-3-0652-0585-s003569 | 9 | 4 | 5 | 297.5 |
| line-3-0722-0711-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0464-0887-s006651 | 5 | 2 | 3 | 178.5 |
| line-4-0646-0802-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0664-0825-s000696 | 10 | 4 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lobito/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
