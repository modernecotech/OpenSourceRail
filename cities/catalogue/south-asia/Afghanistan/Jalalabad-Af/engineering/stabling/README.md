# Station and depot overnight allocation

Plan: **32 trainsets at stations + 80 at depots = 112 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0399-0533-s011848 | line-1 | storage-at-existing-powered-service-point | 19 | 1,130.5 | 0 |
| line-2-0286-0151-s020965 | line-2 | declared-depot | 37 | 2,201.5 | 17 |
| line-3-0764-0482-s014179 | line-3 | storage-at-existing-powered-service-point | 24 | 1,428.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0399-0533-s011848 | station | reverse | revenue | 2 |
| line-1 | line-1-0552-0553-s008251 | station | forward | revenue | 1 |
| line-1 | line-1-0552-0553-s008251 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0598-s006362 | station | forward | revenue | 1 |
| line-1 | line-1-0601-0598-s006362 | station | reverse | revenue | 1 |
| line-1 | line-1-0691-0599-s004454 | station | forward | revenue | 1 |
| line-1 | line-1-0691-0599-s004454 | station | reverse | revenue | 1 |
| line-1 | line-1-0798-0565-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0286-0151-s020965 | station | reverse | revenue | 2 |
| line-2 | line-2-0460-0316-s015062 | station | forward | revenue | 1 |
| line-2 | line-2-0460-0316-s015062 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0553-s009163 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0553-s009163 | station | reverse | revenue | 1 |
| line-2 | line-2-0574-0641-s007022 | station | forward | revenue | 1 |
| line-2 | line-2-0574-0641-s007022 | station | reverse | revenue | 1 |
| line-2 | line-2-0673-0733-s003998 | station | forward | revenue | 1 |
| line-2 | line-2-0673-0733-s003998 | station | reverse | revenue | 1 |
| line-2 | line-2-0782-0878-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0320-0781-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0437-0609-s004940 | station | forward | revenue | 1 |
| line-3 | line-3-0437-0609-s004940 | station | reverse | revenue | 1 |
| line-3 | line-3-0552-0553-s008134 | station | forward | revenue | 1 |
| line-3 | line-3-0552-0553-s008134 | station | reverse | revenue | 1 |
| line-3 | line-3-0651-0543-s010969 | station | forward | revenue | 1 |
| line-3 | line-3-0651-0543-s010969 | station | reverse | revenue | 1 |
| line-3 | line-3-0764-0482-s014179 | station | reverse | revenue | 2 |
| line-1 | line-1-0399-0533-s011848 | depot | — | revenue | 16 |
| line-1 | line-1-0399-0533-s011848 | depot | — | spare | 2 |
| line-1 | line-1-0399-0533-s011848 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0286-0151-s020965 | depot | — | revenue | 32 |
| line-2 | line-2-0286-0151-s020965 | depot | — | spare | 4 |
| line-2 | line-2-0286-0151-s020965 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0764-0482-s014179 | depot | — | revenue | 20 |
| line-3 | line-3-0764-0482-s014179 | depot | — | spare | 3 |
| line-3 | line-3-0764-0482-s014179 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jalalabad-af-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **112 trainsets at 16 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **100 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **80 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0798-0565-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0691-0599-s004454 | forward | revenue | 4 | pending |
| line-1 | line-1-0691-0599-s004454 | reverse | revenue | 3 | pending |
| line-1 | line-1-0601-0598-s006362 | forward | revenue | 3 | pending |
| line-1 | line-1-0601-0598-s006362 | reverse | revenue | 3 | pending |
| line-1 | line-1-0552-0553-s008251 | forward | revenue | 3 | pending |
| line-1 | line-1-0552-0553-s008251 | reverse | revenue | 3 | pending |
| line-1 | line-1-0399-0533-s011848 | reverse | revenue | 3 | pending |
| line-1 | line-1-0691-0599-s004454 | reverse | spare | 1 | pending |
| line-1 | line-1-0601-0598-s006362 | forward | spare | 1 | pending |
| line-1 | line-1-0601-0598-s006362 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0782-0878-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0673-0733-s003998 | forward | revenue | 5 | pending |
| line-2 | line-2-0673-0733-s003998 | reverse | revenue | 5 | pending |
| line-2 | line-2-0574-0641-s007022 | forward | revenue | 5 | pending |
| line-2 | line-2-0574-0641-s007022 | reverse | revenue | 4 | pending |
| line-2 | line-2-0552-0553-s009163 | forward | revenue | 4 | pending |
| line-2 | line-2-0552-0553-s009163 | reverse | revenue | 4 | pending |
| line-2 | line-2-0460-0316-s015062 | forward | revenue | 4 | pending |
| line-2 | line-2-0460-0316-s015062 | reverse | revenue | 4 | pending |
| line-2 | line-2-0286-0151-s020965 | reverse | revenue | 4 | pending |
| line-2 | line-2-0574-0641-s007022 | reverse | spare | 1 | pending |
| line-2 | line-2-0552-0553-s009163 | forward | spare | 1 | pending |
| line-2 | line-2-0552-0553-s009163 | reverse | spare | 1 | pending |
| line-2 | line-2-0460-0316-s015062 | forward | spare | 1 | pending |
| line-2 | line-2-0460-0316-s015062 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0320-0781-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0437-0609-s004940 | forward | revenue | 4 | pending |
| line-3 | line-3-0437-0609-s004940 | reverse | revenue | 4 | pending |
| line-3 | line-3-0552-0553-s008134 | forward | revenue | 4 | pending |
| line-3 | line-3-0552-0553-s008134 | reverse | revenue | 4 | pending |
| line-3 | line-3-0651-0543-s010969 | forward | revenue | 4 | pending |
| line-3 | line-3-0651-0543-s010969 | reverse | revenue | 3 | pending |
| line-3 | line-3-0764-0482-s014179 | reverse | revenue | 3 | pending |
| line-3 | line-3-0651-0543-s010969 | reverse | spare | 1 | pending |
| line-3 | line-3-0764-0482-s014179 | reverse | spare | 1 | pending |
| line-3 | line-3-0320-0781-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0437-0609-s004940 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**74 trainsets exceed the reference platform envelope**, requiring **4,403.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0399-0533-s011848 | 3 | 2 | 1 | 59.5 |
| line-1-0552-0553-s008251 | 6 | 4 | 2 | 119.0 |
| line-1-0601-0598-s006362 | 8 | 2 | 6 | 357.0 |
| line-1-0691-0599-s004454 | 8 | 2 | 6 | 357.0 |
| line-1-0798-0565-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0286-0151-s020965 | 4 | 2 | 2 | 119.0 |
| line-2-0460-0316-s015062 | 10 | 2 | 8 | 476.0 |
| line-2-0552-0553-s009163 | 10 | 4 | 6 | 357.0 |
| line-2-0574-0641-s007022 | 10 | 2 | 8 | 476.0 |
| line-2-0673-0733-s003998 | 10 | 2 | 8 | 476.0 |
| line-2-0782-0878-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0320-0781-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0437-0609-s004940 | 9 | 2 | 7 | 416.5 |
| line-3-0552-0553-s008134 | 8 | 4 | 4 | 238.0 |
| line-3-0651-0543-s010969 | 8 | 2 | 6 | 357.0 |
| line-3-0764-0482-s014179 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Jalalabad-Af/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
