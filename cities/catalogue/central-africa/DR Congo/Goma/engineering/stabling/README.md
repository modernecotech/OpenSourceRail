# Station and depot overnight allocation

Plan: **48 trainsets at stations + 77 at depots = 125 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0681-0770-s023146 | line-1 | declared-depot | 30 | 1,785.0 | 19 |
| line-2-0319-0639-s019967 | line-2 | storage-at-existing-powered-service-point | 25 | 1,487.5 | 0 |
| line-3-0392-0261-s016813 | line-3 | storage-at-existing-powered-service-point | 22 | 1,309.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0237-0086-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0339-0312-s006062 | station | forward | revenue | 1 |
| line-1 | line-1-0339-0312-s006062 | station | reverse | revenue | 1 |
| line-1 | line-1-0425-0412-s009080 | station | forward | revenue | 1 |
| line-1 | line-1-0425-0412-s009080 | station | reverse | revenue | 1 |
| line-1 | line-1-0507-0409-s012094 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0409-s012094 | station | reverse | revenue | 1 |
| line-1 | line-1-0535-0494-s014144 | station | forward | revenue | 1 |
| line-1 | line-1-0535-0494-s014144 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0556-s016183 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0556-s016183 | station | reverse | revenue | 1 |
| line-1 | line-1-0597-0601-s018112 | station | forward | revenue | 1 |
| line-1 | line-1-0597-0601-s018112 | station | reverse | revenue | 1 |
| line-1 | line-1-0644-0690-s021115 | station | forward | revenue | 1 |
| line-1 | line-1-0644-0690-s021115 | station | reverse | revenue | 1 |
| line-1 | line-1-0681-0770-s023146 | station | reverse | revenue | 2 |
| line-2 | line-2-0319-0639-s019967 | station | reverse | revenue | 2 |
| line-2 | line-2-0406-0630-s016897 | station | forward | revenue | 1 |
| line-2 | line-2-0406-0630-s016897 | station | reverse | revenue | 1 |
| line-2 | line-2-0525-0661-s013871 | station | forward | revenue | 1 |
| line-2 | line-2-0525-0661-s013871 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0733-s011631 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0733-s011631 | station | reverse | revenue | 1 |
| line-2 | line-2-0681-0771-s008628 | station | forward | revenue | 1 |
| line-2 | line-2-0681-0771-s008628 | station | reverse | revenue | 1 |
| line-2 | line-2-0737-0802-s007020 | station | forward | revenue | 1 |
| line-2 | line-2-0737-0802-s007020 | station | reverse | revenue | 1 |
| line-2 | line-2-0846-0854-s003512 | station | forward | revenue | 1 |
| line-2 | line-2-0846-0854-s003512 | station | reverse | revenue | 1 |
| line-2 | line-2-0948-0862-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0392-0261-s016813 | station | reverse | revenue | 2 |
| line-3 | line-3-0430-0815-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0480-0707-s003003 | station | forward | revenue | 1 |
| line-3 | line-3-0480-0707-s003003 | station | reverse | revenue | 1 |
| line-3 | line-3-0488-0304-s013639 | station | forward | revenue | 1 |
| line-3 | line-3-0488-0304-s013639 | station | reverse | revenue | 1 |
| line-3 | line-3-0513-0642-s004605 | station | forward | revenue | 1 |
| line-3 | line-3-0513-0642-s004605 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0556-s006997 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0556-s006997 | station | reverse | revenue | 1 |
| line-3 | line-3-0545-0423-s010632 | station | forward | revenue | 1 |
| line-3 | line-3-0545-0423-s010632 | station | reverse | revenue | 1 |
| line-1 | line-1-0681-0770-s023146 | depot | — | revenue | 25 |
| line-1 | line-1-0681-0770-s023146 | depot | — | spare | 4 |
| line-1 | line-1-0681-0770-s023146 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0319-0639-s019967 | depot | — | revenue | 21 |
| line-2 | line-2-0319-0639-s019967 | depot | — | spare | 3 |
| line-2 | line-2-0319-0639-s019967 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0392-0261-s016813 | depot | — | revenue | 18 |
| line-3 | line-3-0392-0261-s016813 | depot | — | spare | 3 |
| line-3 | line-3-0392-0261-s016813 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/goma-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **125 trainsets at 24 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **112 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **77 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **23 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0237-0086-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0339-0312-s006062 | forward | revenue | 3 | pending |
| line-1 | line-1-0339-0312-s006062 | reverse | revenue | 3 | pending |
| line-1 | line-1-0425-0412-s009080 | forward | revenue | 3 | pending |
| line-1 | line-1-0425-0412-s009080 | reverse | revenue | 3 | pending |
| line-1 | line-1-0507-0409-s012094 | forward | revenue | 3 | pending |
| line-1 | line-1-0507-0409-s012094 | reverse | revenue | 3 | pending |
| line-1 | line-1-0535-0494-s014144 | forward | revenue | 3 | pending |
| line-1 | line-1-0535-0494-s014144 | reverse | revenue | 3 | pending |
| line-1 | line-1-0543-0556-s016183 | forward | revenue | 3 | pending |
| line-1 | line-1-0543-0556-s016183 | reverse | revenue | 3 | pending |
| line-1 | line-1-0597-0601-s018112 | forward | revenue | 2 | pending |
| line-1 | line-1-0597-0601-s018112 | reverse | revenue | 2 | pending |
| line-1 | line-1-0644-0690-s021115 | forward | revenue | 2 | pending |
| line-1 | line-1-0644-0690-s021115 | reverse | revenue | 2 | pending |
| line-1 | line-1-0681-0770-s023146 | reverse | revenue | 2 | pending |
| line-1 | line-1-0597-0601-s018112 | forward | spare | 1 | pending |
| line-1 | line-1-0597-0601-s018112 | reverse | spare | 1 | pending |
| line-1 | line-1-0644-0690-s021115 | forward | spare | 1 | pending |
| line-1 | line-1-0644-0690-s021115 | reverse | spare | 1 | pending |
| line-1 | line-1-0681-0770-s023146 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0948-0862-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0846-0854-s003512 | forward | revenue | 3 | pending |
| line-2 | line-2-0846-0854-s003512 | reverse | revenue | 3 | pending |
| line-2 | line-2-0737-0802-s007020 | forward | revenue | 3 | pending |
| line-2 | line-2-0737-0802-s007020 | reverse | revenue | 3 | pending |
| line-2 | line-2-0681-0771-s008628 | forward | revenue | 3 | pending |
| line-2 | line-2-0681-0771-s008628 | reverse | revenue | 3 | pending |
| line-2 | line-2-0580-0733-s011631 | forward | revenue | 3 | pending |
| line-2 | line-2-0580-0733-s011631 | reverse | revenue | 3 | pending |
| line-2 | line-2-0525-0661-s013871 | forward | revenue | 2 | pending |
| line-2 | line-2-0525-0661-s013871 | reverse | revenue | 2 | pending |
| line-2 | line-2-0406-0630-s016897 | forward | revenue | 2 | pending |
| line-2 | line-2-0406-0630-s016897 | reverse | revenue | 2 | pending |
| line-2 | line-2-0319-0639-s019967 | reverse | revenue | 2 | pending |
| line-2 | line-2-0525-0661-s013871 | forward | spare | 1 | pending |
| line-2 | line-2-0525-0661-s013871 | reverse | spare | 1 | pending |
| line-2 | line-2-0406-0630-s016897 | forward | spare | 1 | pending |
| line-2 | line-2-0406-0630-s016897 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0430-0815-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0480-0707-s003003 | forward | revenue | 3 | pending |
| line-3 | line-3-0480-0707-s003003 | reverse | revenue | 3 | pending |
| line-3 | line-3-0513-0642-s004605 | forward | revenue | 3 | pending |
| line-3 | line-3-0513-0642-s004605 | reverse | revenue | 3 | pending |
| line-3 | line-3-0543-0556-s006997 | forward | revenue | 3 | pending |
| line-3 | line-3-0543-0556-s006997 | reverse | revenue | 3 | pending |
| line-3 | line-3-0545-0423-s010632 | forward | revenue | 3 | pending |
| line-3 | line-3-0545-0423-s010632 | reverse | revenue | 2 | pending |
| line-3 | line-3-0488-0304-s013639 | forward | revenue | 2 | pending |
| line-3 | line-3-0488-0304-s013639 | reverse | revenue | 2 | pending |
| line-3 | line-3-0392-0261-s016813 | reverse | revenue | 2 | pending |
| line-3 | line-3-0545-0423-s010632 | reverse | spare | 1 | pending |
| line-3 | line-3-0488-0304-s013639 | forward | spare | 1 | pending |
| line-3 | line-3-0488-0304-s013639 | reverse | spare | 1 | pending |
| line-3 | line-3-0392-0261-s016813 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**67 trainsets exceed the reference platform envelope**, requiring **3,986.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0237-0086-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0339-0312-s006062 | 6 | 2 | 4 | 238.0 |
| line-1-0425-0412-s009080 | 6 | 2 | 4 | 238.0 |
| line-1-0507-0409-s012094 | 6 | 2 | 4 | 238.0 |
| line-1-0535-0494-s014144 | 6 | 2 | 4 | 238.0 |
| line-1-0543-0556-s016183 | 6 | 4 | 2 | 119.0 |
| line-1-0597-0601-s018112 | 6 | 2 | 4 | 238.0 |
| line-1-0644-0690-s021115 | 6 | 2 | 4 | 238.0 |
| line-1-0681-0770-s023146 | 3 | 2 | 1 | 59.5 |
| line-2-0319-0639-s019967 | 2 | 2 | 0 | 0.0 |
| line-2-0406-0630-s016897 | 6 | 2 | 4 | 238.0 |
| line-2-0525-0661-s013871 | 6 | 4 | 2 | 119.0 |
| line-2-0580-0733-s011631 | 6 | 2 | 4 | 238.0 |
| line-2-0681-0771-s008628 | 6 | 4 | 2 | 119.0 |
| line-2-0737-0802-s007020 | 6 | 2 | 4 | 238.0 |
| line-2-0846-0854-s003512 | 6 | 2 | 4 | 238.0 |
| line-2-0948-0862-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0392-0261-s016813 | 3 | 2 | 1 | 59.5 |
| line-3-0430-0815-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0480-0707-s003003 | 6 | 2 | 4 | 238.0 |
| line-3-0488-0304-s013639 | 6 | 2 | 4 | 238.0 |
| line-3-0513-0642-s004605 | 6 | 4 | 2 | 119.0 |
| line-3-0543-0556-s006997 | 6 | 4 | 2 | 119.0 |
| line-3-0545-0423-s010632 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Goma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
