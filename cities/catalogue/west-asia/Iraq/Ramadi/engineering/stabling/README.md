# Station and depot overnight allocation

Plan: **44 trainsets at stations + 60 at depots = 104 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0421-0641-s017280 | 60 | 3,570.0 | 16 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0491-0802-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0525-0286-s013987 | station | forward | revenue | 1 |
| line-1 | line-1-0525-0286-s013987 | station | reverse | revenue | 1 |
| line-1 | line-1-0527-0190-s016406 | station | reverse | revenue | 2 |
| line-1 | line-1-0546-0676-s003011 | station | forward | revenue | 1 |
| line-1 | line-1-0546-0676-s003011 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0499-s007914 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0499-s007914 | station | reverse | revenue | 1 |
| line-1 | line-1-0565-0395-s010975 | station | forward | revenue | 1 |
| line-1 | line-1-0565-0395-s010975 | station | reverse | revenue | 1 |
| line-1 | line-1-0590-0549-s006026 | station | forward | revenue | 1 |
| line-1 | line-1-0590-0549-s006026 | station | reverse | revenue | 1 |
| line-2 | line-2-0361-0731-s014321 | station | reverse | revenue | 2 |
| line-2 | line-2-0418-0643-s011674 | station | forward | revenue | 1 |
| line-2 | line-2-0418-0643-s011674 | station | reverse | revenue | 1 |
| line-2 | line-2-0473-0537-s009049 | station | forward | revenue | 1 |
| line-2 | line-2-0473-0537-s009049 | station | reverse | revenue | 1 |
| line-2 | line-2-0554-0499-s006945 | station | forward | revenue | 1 |
| line-2 | line-2-0554-0499-s006945 | station | reverse | revenue | 1 |
| line-2 | line-2-0587-0440-s004970 | station | forward | revenue | 1 |
| line-2 | line-2-0587-0440-s004970 | station | reverse | revenue | 1 |
| line-2 | line-2-0643-0387-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0643-0387-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0654-0283-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0421-0641-s017280 | station | reverse | revenue | 2 |
| line-3 | line-3-0476-0055-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0476-0294-s006395 | station | forward | revenue | 1 |
| line-3 | line-3-0476-0294-s006395 | station | reverse | revenue | 1 |
| line-3 | line-3-0485-0402-s009399 | station | forward | revenue | 1 |
| line-3 | line-3-0485-0402-s009399 | station | reverse | revenue | 1 |
| line-3 | line-3-0495-0477-s011207 | station | forward | revenue | 1 |
| line-3 | line-3-0495-0477-s011207 | station | reverse | revenue | 1 |
| line-3 | line-3-0498-0182-s003382 | station | forward | revenue | 1 |
| line-3 | line-3-0498-0182-s003382 | station | reverse | revenue | 1 |
| line-3 | line-3-0513-0559-s014219 | station | forward | revenue | 1 |
| line-3 | line-3-0513-0559-s014219 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0499-s012569 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0499-s012569 | station | reverse | revenue | 1 |
| line-1 | line-3-0421-0641-s017280 | depot | — | revenue | 18 |
| line-1 | line-3-0421-0641-s017280 | depot | — | spare | 3 |
| line-1 | line-3-0421-0641-s017280 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0421-0641-s017280 | depot | — | revenue | 14 |
| line-2 | line-3-0421-0641-s017280 | depot | — | spare | 2 |
| line-2 | line-3-0421-0641-s017280 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0421-0641-s017280 | depot | — | revenue | 17 |
| line-3 | line-3-0421-0641-s017280 | depot | — | spare | 3 |
| line-3 | line-3-0421-0641-s017280 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (22 trains), line-2 (17 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **104 trainsets at 22 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **93 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **60 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0491-0802-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0546-0676-s003011 | forward | revenue | 3 | pending |
| line-1 | line-1-0546-0676-s003011 | reverse | revenue | 3 | pending |
| line-1 | line-1-0590-0549-s006026 | forward | revenue | 3 | pending |
| line-1 | line-1-0590-0549-s006026 | reverse | revenue | 3 | pending |
| line-1 | line-1-0554-0499-s007914 | forward | revenue | 3 | pending |
| line-1 | line-1-0554-0499-s007914 | reverse | revenue | 3 | pending |
| line-1 | line-1-0565-0395-s010975 | forward | revenue | 3 | pending |
| line-1 | line-1-0565-0395-s010975 | reverse | revenue | 2 | pending |
| line-1 | line-1-0525-0286-s013987 | forward | revenue | 2 | pending |
| line-1 | line-1-0525-0286-s013987 | reverse | revenue | 2 | pending |
| line-1 | line-1-0527-0190-s016406 | reverse | revenue | 2 | pending |
| line-1 | line-1-0565-0395-s010975 | reverse | spare | 1 | pending |
| line-1 | line-1-0525-0286-s013987 | forward | spare | 1 | pending |
| line-1 | line-1-0525-0286-s013987 | reverse | spare | 1 | pending |
| line-1 | line-1-0527-0190-s016406 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0654-0283-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0643-0387-s003006 | forward | revenue | 3 | pending |
| line-2 | line-2-0643-0387-s003006 | reverse | revenue | 3 | pending |
| line-2 | line-2-0587-0440-s004970 | forward | revenue | 3 | pending |
| line-2 | line-2-0587-0440-s004970 | reverse | revenue | 2 | pending |
| line-2 | line-2-0554-0499-s006945 | forward | revenue | 2 | pending |
| line-2 | line-2-0554-0499-s006945 | reverse | revenue | 2 | pending |
| line-2 | line-2-0473-0537-s009049 | forward | revenue | 2 | pending |
| line-2 | line-2-0473-0537-s009049 | reverse | revenue | 2 | pending |
| line-2 | line-2-0418-0643-s011674 | forward | revenue | 2 | pending |
| line-2 | line-2-0418-0643-s011674 | reverse | revenue | 2 | pending |
| line-2 | line-2-0361-0731-s014321 | reverse | revenue | 2 | pending |
| line-2 | line-2-0587-0440-s004970 | reverse | spare | 1 | pending |
| line-2 | line-2-0554-0499-s006945 | forward | spare | 1 | pending |
| line-2 | line-2-0554-0499-s006945 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0476-0055-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0498-0182-s003382 | forward | revenue | 3 | pending |
| line-3 | line-3-0498-0182-s003382 | reverse | revenue | 3 | pending |
| line-3 | line-3-0476-0294-s006395 | forward | revenue | 3 | pending |
| line-3 | line-3-0476-0294-s006395 | reverse | revenue | 3 | pending |
| line-3 | line-3-0485-0402-s009399 | forward | revenue | 2 | pending |
| line-3 | line-3-0485-0402-s009399 | reverse | revenue | 2 | pending |
| line-3 | line-3-0495-0477-s011207 | forward | revenue | 2 | pending |
| line-3 | line-3-0495-0477-s011207 | reverse | revenue | 2 | pending |
| line-3 | line-3-0554-0499-s012569 | forward | revenue | 2 | pending |
| line-3 | line-3-0554-0499-s012569 | reverse | revenue | 2 | pending |
| line-3 | line-3-0513-0559-s014219 | forward | revenue | 2 | pending |
| line-3 | line-3-0513-0559-s014219 | reverse | revenue | 2 | pending |
| line-3 | line-3-0421-0641-s017280 | reverse | revenue | 2 | pending |
| line-3 | line-3-0485-0402-s009399 | forward | spare | 1 | pending |
| line-3 | line-3-0485-0402-s009399 | reverse | spare | 1 | pending |
| line-3 | line-3-0495-0477-s011207 | forward | spare | 1 | pending |
| line-3 | line-3-0495-0477-s011207 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**52 trainsets exceed the reference platform envelope**, requiring **3,094.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0491-0802-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0525-0286-s013987 | 6 | 2 | 4 | 238.0 |
| line-1-0527-0190-s016406 | 3 | 2 | 1 | 59.5 |
| line-1-0546-0676-s003011 | 6 | 2 | 4 | 238.0 |
| line-1-0554-0499-s007914 | 6 | 4 | 2 | 119.0 |
| line-1-0565-0395-s010975 | 6 | 2 | 4 | 238.0 |
| line-1-0590-0549-s006026 | 6 | 2 | 4 | 238.0 |
| line-2-0361-0731-s014321 | 2 | 2 | 0 | 0.0 |
| line-2-0418-0643-s011674 | 4 | 4 | 0 | 0.0 |
| line-2-0473-0537-s009049 | 4 | 2 | 2 | 119.0 |
| line-2-0554-0499-s006945 | 6 | 4 | 2 | 119.0 |
| line-2-0587-0440-s004970 | 6 | 2 | 4 | 238.0 |
| line-2-0643-0387-s003006 | 6 | 2 | 4 | 238.0 |
| line-2-0654-0283-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0421-0641-s017280 | 2 | 2 | 0 | 0.0 |
| line-3-0476-0055-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0476-0294-s006395 | 6 | 2 | 4 | 238.0 |
| line-3-0485-0402-s009399 | 6 | 2 | 4 | 238.0 |
| line-3-0495-0477-s011207 | 6 | 2 | 4 | 238.0 |
| line-3-0498-0182-s003382 | 6 | 2 | 4 | 238.0 |
| line-3-0513-0559-s014219 | 4 | 2 | 2 | 119.0 |
| line-3-0554-0499-s012569 | 4 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Ramadi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
