# Station and depot overnight allocation

Plan: **40 trainsets at stations + 89 at depots = 129 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0409-0232-s024595 | line-1 | declared-depot | 38 | 2,261.0 | 20 |
| line-2-0124-0683-s017690 | line-2 | storage-at-existing-powered-service-point | 23 | 1,368.5 | 0 |
| line-3-0608-0185-s018294 | line-3 | storage-at-existing-powered-service-point | 28 | 1,666.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0409-0232-s024595 | station | reverse | revenue | 2 |
| line-1 | line-1-0435-0322-s022001 | station | forward | revenue | 1 |
| line-1 | line-1-0435-0322-s022001 | station | reverse | revenue | 1 |
| line-1 | line-1-0450-0427-s019422 | station | forward | revenue | 1 |
| line-1 | line-1-0450-0427-s019422 | station | reverse | revenue | 1 |
| line-1 | line-1-0466-0499-s017523 | station | forward | revenue | 1 |
| line-1 | line-1-0466-0499-s017523 | station | reverse | revenue | 1 |
| line-1 | line-1-0542-0536-s015406 | station | forward | revenue | 1 |
| line-1 | line-1-0542-0536-s015406 | station | reverse | revenue | 1 |
| line-1 | line-1-0595-0608-s013459 | station | forward | revenue | 1 |
| line-1 | line-1-0595-0608-s013459 | station | reverse | revenue | 1 |
| line-1 | line-1-0648-0679-s011501 | station | forward | revenue | 1 |
| line-1 | line-1-0648-0679-s011501 | station | reverse | revenue | 1 |
| line-1 | line-1-1054-1032-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0124-0683-s017690 | station | reverse | revenue | 2 |
| line-2 | line-2-0304-0616-s013369 | station | forward | revenue | 1 |
| line-2 | line-2-0304-0616-s013369 | station | reverse | revenue | 1 |
| line-2 | line-2-0494-0573-s009035 | station | forward | revenue | 1 |
| line-2 | line-2-0494-0573-s009035 | station | reverse | revenue | 1 |
| line-2 | line-2-0542-0536-s007378 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0536-s007378 | station | reverse | revenue | 1 |
| line-2 | line-2-0565-0483-s006017 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0483-s006017 | station | reverse | revenue | 1 |
| line-2 | line-2-0593-0345-s003008 | station | forward | revenue | 1 |
| line-2 | line-2-0593-0345-s003008 | station | reverse | revenue | 1 |
| line-2 | line-2-0676-0236-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0202-0517-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0378-0384-s008161 | station | forward | revenue | 1 |
| line-3 | line-3-0378-0384-s008161 | station | reverse | revenue | 1 |
| line-3 | line-3-0383-0485-s005145 | station | forward | revenue | 1 |
| line-3 | line-3-0383-0485-s005145 | station | reverse | revenue | 1 |
| line-3 | line-3-0439-0285-s011186 | station | forward | revenue | 1 |
| line-3 | line-3-0439-0285-s011186 | station | reverse | revenue | 1 |
| line-3 | line-3-0608-0185-s018294 | station | reverse | revenue | 2 |
| line-1 | line-1-0409-0232-s024595 | depot | — | revenue | 33 |
| line-1 | line-1-0409-0232-s024595 | depot | — | spare | 4 |
| line-1 | line-1-0409-0232-s024595 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0124-0683-s017690 | depot | — | revenue | 19 |
| line-2 | line-2-0124-0683-s017690 | depot | — | spare | 3 |
| line-2 | line-2-0124-0683-s017690 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0608-0185-s018294 | depot | — | revenue | 24 |
| line-3 | line-3-0608-0185-s018294 | depot | — | spare | 3 |
| line-3 | line-3-0608-0185-s018294 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/suez-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **129 trainsets at 20 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **89 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1054-1032-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0648-0679-s011501 | forward | revenue | 4 | pending |
| line-1 | line-1-0648-0679-s011501 | reverse | revenue | 4 | pending |
| line-1 | line-1-0595-0608-s013459 | forward | revenue | 4 | pending |
| line-1 | line-1-0595-0608-s013459 | reverse | revenue | 4 | pending |
| line-1 | line-1-0542-0536-s015406 | forward | revenue | 4 | pending |
| line-1 | line-1-0542-0536-s015406 | reverse | revenue | 4 | pending |
| line-1 | line-1-0466-0499-s017523 | forward | revenue | 3 | pending |
| line-1 | line-1-0466-0499-s017523 | reverse | revenue | 3 | pending |
| line-1 | line-1-0450-0427-s019422 | forward | revenue | 3 | pending |
| line-1 | line-1-0450-0427-s019422 | reverse | revenue | 3 | pending |
| line-1 | line-1-0435-0322-s022001 | forward | revenue | 3 | pending |
| line-1 | line-1-0435-0322-s022001 | reverse | revenue | 3 | pending |
| line-1 | line-1-0409-0232-s024595 | reverse | revenue | 3 | pending |
| line-1 | line-1-0466-0499-s017523 | forward | spare | 1 | pending |
| line-1 | line-1-0466-0499-s017523 | reverse | spare | 1 | pending |
| line-1 | line-1-0450-0427-s019422 | forward | spare | 1 | pending |
| line-1 | line-1-0450-0427-s019422 | reverse | spare | 1 | pending |
| line-1 | line-1-0435-0322-s022001 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0676-0236-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0593-0345-s003008 | forward | revenue | 3 | pending |
| line-2 | line-2-0593-0345-s003008 | reverse | revenue | 3 | pending |
| line-2 | line-2-0565-0483-s006017 | forward | revenue | 3 | pending |
| line-2 | line-2-0565-0483-s006017 | reverse | revenue | 3 | pending |
| line-2 | line-2-0542-0536-s007378 | forward | revenue | 3 | pending |
| line-2 | line-2-0542-0536-s007378 | reverse | revenue | 3 | pending |
| line-2 | line-2-0494-0573-s009035 | forward | revenue | 3 | pending |
| line-2 | line-2-0494-0573-s009035 | reverse | revenue | 3 | pending |
| line-2 | line-2-0304-0616-s013369 | forward | revenue | 2 | pending |
| line-2 | line-2-0304-0616-s013369 | reverse | revenue | 2 | pending |
| line-2 | line-2-0124-0683-s017690 | reverse | revenue | 2 | pending |
| line-2 | line-2-0304-0616-s013369 | forward | spare | 1 | pending |
| line-2 | line-2-0304-0616-s013369 | reverse | spare | 1 | pending |
| line-2 | line-2-0124-0683-s017690 | reverse | spare | 1 | pending |
| line-2 | line-2-0676-0236-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0202-0517-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0383-0485-s005145 | forward | revenue | 5 | pending |
| line-3 | line-3-0383-0485-s005145 | reverse | revenue | 4 | pending |
| line-3 | line-3-0378-0384-s008161 | forward | revenue | 4 | pending |
| line-3 | line-3-0378-0384-s008161 | reverse | revenue | 4 | pending |
| line-3 | line-3-0439-0285-s011186 | forward | revenue | 4 | pending |
| line-3 | line-3-0439-0285-s011186 | reverse | revenue | 4 | pending |
| line-3 | line-3-0608-0185-s018294 | reverse | revenue | 4 | pending |
| line-3 | line-3-0383-0485-s005145 | reverse | spare | 1 | pending |
| line-3 | line-3-0378-0384-s008161 | forward | spare | 1 | pending |
| line-3 | line-3-0378-0384-s008161 | reverse | spare | 1 | pending |
| line-3 | line-3-0439-0285-s011186 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**85 trainsets exceed the reference platform envelope**, requiring **5,057.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0409-0232-s024595 | 3 | 2 | 1 | 59.5 |
| line-1-0435-0322-s022001 | 7 | 2 | 5 | 297.5 |
| line-1-0450-0427-s019422 | 8 | 2 | 6 | 357.0 |
| line-1-0466-0499-s017523 | 8 | 2 | 6 | 357.0 |
| line-1-0542-0536-s015406 | 8 | 4 | 4 | 238.0 |
| line-1-0595-0608-s013459 | 8 | 2 | 6 | 357.0 |
| line-1-0648-0679-s011501 | 8 | 2 | 6 | 357.0 |
| line-1-1054-1032-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0124-0683-s017690 | 3 | 2 | 1 | 59.5 |
| line-2-0304-0616-s013369 | 6 | 2 | 4 | 238.0 |
| line-2-0494-0573-s009035 | 6 | 2 | 4 | 238.0 |
| line-2-0542-0536-s007378 | 6 | 4 | 2 | 119.0 |
| line-2-0565-0483-s006017 | 6 | 2 | 4 | 238.0 |
| line-2-0593-0345-s003008 | 6 | 2 | 4 | 238.0 |
| line-2-0676-0236-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0202-0517-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0378-0384-s008161 | 10 | 2 | 8 | 476.0 |
| line-3-0383-0485-s005145 | 10 | 2 | 8 | 476.0 |
| line-3-0439-0285-s011186 | 9 | 2 | 7 | 416.5 |
| line-3-0608-0185-s018294 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Suez/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
