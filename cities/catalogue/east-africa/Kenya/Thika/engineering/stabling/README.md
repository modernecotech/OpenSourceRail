# Station and depot overnight allocation

Plan: **48 trainsets at stations + 113 at depots = 161 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0016-0869-s029004 | line-1 | declared-depot | 46 | 2,737.0 | 25 |
| line-2-0586-0120-s021310 | line-2 | storage-at-existing-powered-service-point | 30 | 1,785.0 | 0 |
| line-3-0341-0923-s025158 | line-3 | storage-at-existing-powered-service-point | 37 | 2,201.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0016-0869-s029004 | station | reverse | revenue | 2 |
| line-1 | line-1-0388-0608-s019064 | station | forward | revenue | 1 |
| line-1 | line-1-0388-0608-s019064 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0536-s016051 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0536-s016051 | station | reverse | revenue | 1 |
| line-1 | line-1-0561-0543-s014517 | station | forward | revenue | 1 |
| line-1 | line-1-0561-0543-s014517 | station | reverse | revenue | 1 |
| line-1 | line-1-0600-0509-s013042 | station | forward | revenue | 1 |
| line-1 | line-1-0600-0509-s013042 | station | reverse | revenue | 1 |
| line-1 | line-1-0695-0454-s010034 | station | forward | revenue | 1 |
| line-1 | line-1-0695-0454-s010034 | station | reverse | revenue | 1 |
| line-1 | line-1-0718-0368-s007006 | station | forward | revenue | 1 |
| line-1 | line-1-0718-0368-s007006 | station | reverse | revenue | 1 |
| line-1 | line-1-0901-0237-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0534-0301-s017061 | station | forward | revenue | 1 |
| line-2 | line-2-0534-0301-s017061 | station | reverse | revenue | 1 |
| line-2 | line-2-0554-0600-s009823 | station | forward | revenue | 1 |
| line-2 | line-2-0554-0600-s009823 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0543-s011038 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0543-s011038 | station | reverse | revenue | 1 |
| line-2 | line-2-0564-0467-s012838 | station | forward | revenue | 1 |
| line-2 | line-2-0564-0467-s012838 | station | reverse | revenue | 1 |
| line-2 | line-2-0586-0120-s021310 | station | reverse | revenue | 2 |
| line-2 | line-2-0613-0698-s006796 | station | forward | revenue | 1 |
| line-2 | line-2-0613-0698-s006796 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0928-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0670-0778-s003795 | station | forward | revenue | 1 |
| line-2 | line-2-0670-0778-s003795 | station | reverse | revenue | 1 |
| line-3 | line-3-0341-0923-s025158 | station | reverse | revenue | 2 |
| line-3 | line-3-0453-0797-s020598 | station | forward | revenue | 1 |
| line-3 | line-3-0453-0797-s020598 | station | reverse | revenue | 1 |
| line-3 | line-3-0477-0609-s016043 | station | forward | revenue | 1 |
| line-3 | line-3-0477-0609-s016043 | station | reverse | revenue | 1 |
| line-3 | line-3-0561-0543-s013804 | station | forward | revenue | 1 |
| line-3 | line-3-0561-0543-s013804 | station | reverse | revenue | 1 |
| line-3 | line-3-0633-0522-s011905 | station | forward | revenue | 1 |
| line-3 | line-3-0633-0522-s011905 | station | reverse | revenue | 1 |
| line-3 | line-3-0713-0497-s010027 | station | forward | revenue | 1 |
| line-3 | line-3-0713-0497-s010027 | station | reverse | revenue | 1 |
| line-3 | line-3-0812-0413-s007009 | station | forward | revenue | 1 |
| line-3 | line-3-0812-0413-s007009 | station | reverse | revenue | 1 |
| line-3 | line-3-1020-0216-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0016-0869-s029004 | depot | — | revenue | 40 |
| line-1 | line-1-0016-0869-s029004 | depot | — | spare | 5 |
| line-1 | line-1-0016-0869-s029004 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0586-0120-s021310 | depot | — | revenue | 25 |
| line-2 | line-2-0586-0120-s021310 | depot | — | spare | 4 |
| line-2 | line-2-0586-0120-s021310 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0341-0923-s025158 | depot | — | revenue | 32 |
| line-3 | line-3-0341-0923-s025158 | depot | — | spare | 4 |
| line-3 | line-3-0341-0923-s025158 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/thika-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **161 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **145 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **113 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0901-0237-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0718-0368-s007006 | forward | revenue | 4 | pending |
| line-1 | line-1-0718-0368-s007006 | reverse | revenue | 4 | pending |
| line-1 | line-1-0695-0454-s010034 | forward | revenue | 4 | pending |
| line-1 | line-1-0695-0454-s010034 | reverse | revenue | 4 | pending |
| line-1 | line-1-0600-0509-s013042 | forward | revenue | 4 | pending |
| line-1 | line-1-0600-0509-s013042 | reverse | revenue | 4 | pending |
| line-1 | line-1-0561-0543-s014517 | forward | revenue | 4 | pending |
| line-1 | line-1-0561-0543-s014517 | reverse | revenue | 4 | pending |
| line-1 | line-1-0503-0536-s016051 | forward | revenue | 4 | pending |
| line-1 | line-1-0503-0536-s016051 | reverse | revenue | 4 | pending |
| line-1 | line-1-0388-0608-s019064 | forward | revenue | 4 | pending |
| line-1 | line-1-0388-0608-s019064 | reverse | revenue | 4 | pending |
| line-1 | line-1-0016-0869-s029004 | reverse | revenue | 4 | pending |
| line-1 | line-1-0901-0237-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0718-0368-s007006 | forward | spare | 1 | pending |
| line-1 | line-1-0718-0368-s007006 | reverse | spare | 1 | pending |
| line-1 | line-1-0695-0454-s010034 | forward | spare | 1 | pending |
| line-1 | line-1-0695-0454-s010034 | reverse | spare | 1 | pending |
| line-1 | line-1-0600-0509-s013042 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0665-0928-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0670-0778-s003795 | forward | revenue | 3 | pending |
| line-2 | line-2-0670-0778-s003795 | reverse | revenue | 3 | pending |
| line-2 | line-2-0613-0698-s006796 | forward | revenue | 3 | pending |
| line-2 | line-2-0613-0698-s006796 | reverse | revenue | 3 | pending |
| line-2 | line-2-0554-0600-s009823 | forward | revenue | 3 | pending |
| line-2 | line-2-0554-0600-s009823 | reverse | revenue | 3 | pending |
| line-2 | line-2-0561-0543-s011038 | forward | revenue | 3 | pending |
| line-2 | line-2-0561-0543-s011038 | reverse | revenue | 3 | pending |
| line-2 | line-2-0564-0467-s012838 | forward | revenue | 3 | pending |
| line-2 | line-2-0564-0467-s012838 | reverse | revenue | 3 | pending |
| line-2 | line-2-0534-0301-s017061 | forward | revenue | 3 | pending |
| line-2 | line-2-0534-0301-s017061 | reverse | revenue | 3 | pending |
| line-2 | line-2-0586-0120-s021310 | reverse | revenue | 2 | pending |
| line-2 | line-2-0586-0120-s021310 | reverse | spare | 1 | pending |
| line-2 | line-2-0665-0928-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0670-0778-s003795 | forward | spare | 1 | pending |
| line-2 | line-2-0670-0778-s003795 | reverse | spare | 1 | pending |
| line-2 | line-2-0613-0698-s006796 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1020-0216-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0812-0413-s007009 | forward | revenue | 4 | pending |
| line-3 | line-3-0812-0413-s007009 | reverse | revenue | 4 | pending |
| line-3 | line-3-0713-0497-s010027 | forward | revenue | 4 | pending |
| line-3 | line-3-0713-0497-s010027 | reverse | revenue | 4 | pending |
| line-3 | line-3-0633-0522-s011905 | forward | revenue | 4 | pending |
| line-3 | line-3-0633-0522-s011905 | reverse | revenue | 3 | pending |
| line-3 | line-3-0561-0543-s013804 | forward | revenue | 3 | pending |
| line-3 | line-3-0561-0543-s013804 | reverse | revenue | 3 | pending |
| line-3 | line-3-0477-0609-s016043 | forward | revenue | 3 | pending |
| line-3 | line-3-0477-0609-s016043 | reverse | revenue | 3 | pending |
| line-3 | line-3-0453-0797-s020598 | forward | revenue | 3 | pending |
| line-3 | line-3-0453-0797-s020598 | reverse | revenue | 3 | pending |
| line-3 | line-3-0341-0923-s025158 | reverse | revenue | 3 | pending |
| line-3 | line-3-0633-0522-s011905 | reverse | spare | 1 | pending |
| line-3 | line-3-0561-0543-s013804 | forward | spare | 1 | pending |
| line-3 | line-3-0561-0543-s013804 | reverse | spare | 1 | pending |
| line-3 | line-3-0477-0609-s016043 | forward | spare | 1 | pending |
| line-3 | line-3-0477-0609-s016043 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**107 trainsets exceed the reference platform envelope**, requiring **6,366.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0016-0869-s029004 | 4 | 2 | 2 | 119.0 |
| line-1-0388-0608-s019064 | 8 | 2 | 6 | 357.0 |
| line-1-0503-0536-s016051 | 8 | 2 | 6 | 357.0 |
| line-1-0561-0543-s014517 | 8 | 4 | 4 | 238.0 |
| line-1-0600-0509-s013042 | 9 | 2 | 7 | 416.5 |
| line-1-0695-0454-s010034 | 10 | 2 | 8 | 476.0 |
| line-1-0718-0368-s007006 | 10 | 2 | 8 | 476.0 |
| line-1-0901-0237-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0534-0301-s017061 | 6 | 2 | 4 | 238.0 |
| line-2-0554-0600-s009823 | 6 | 2 | 4 | 238.0 |
| line-2-0561-0543-s011038 | 6 | 4 | 2 | 119.0 |
| line-2-0564-0467-s012838 | 6 | 2 | 4 | 238.0 |
| line-2-0586-0120-s021310 | 3 | 2 | 1 | 59.5 |
| line-2-0613-0698-s006796 | 7 | 2 | 5 | 297.5 |
| line-2-0665-0928-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0670-0778-s003795 | 8 | 2 | 6 | 357.0 |
| line-3-0341-0923-s025158 | 3 | 2 | 1 | 59.5 |
| line-3-0453-0797-s020598 | 6 | 2 | 4 | 238.0 |
| line-3-0477-0609-s016043 | 8 | 2 | 6 | 357.0 |
| line-3-0561-0543-s013804 | 8 | 4 | 4 | 238.0 |
| line-3-0633-0522-s011905 | 8 | 2 | 6 | 357.0 |
| line-3-0713-0497-s010027 | 8 | 2 | 6 | 357.0 |
| line-3-0812-0413-s007009 | 8 | 2 | 6 | 357.0 |
| line-3-1020-0216-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Thika/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
