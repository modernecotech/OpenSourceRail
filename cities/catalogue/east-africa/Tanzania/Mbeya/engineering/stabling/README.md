# Station and depot overnight allocation

Plan: **42 trainsets at stations + 70 at depots = 112 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0733-0298-s019814 | line-1 | storage-at-existing-powered-service-point | 25 | 1,487.5 | 0 |
| line-2-0708-0058-s022608 | line-2 | declared-depot | 31 | 1,844.5 | 17 |
| line-3-0781-0464-s010598 | line-3 | storage-at-existing-powered-service-point | 14 | 833.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0448-0937-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0534-0829-s003001 | station | forward | revenue | 1 |
| line-1 | line-1-0534-0829-s003001 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0539-s009494 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0539-s009494 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0700-s006008 | station | forward | revenue | 1 |
| line-1 | line-1-0571-0700-s006008 | station | reverse | revenue | 1 |
| line-1 | line-1-0624-0504-s012032 | station | forward | revenue | 1 |
| line-1 | line-1-0624-0504-s012032 | station | reverse | revenue | 1 |
| line-1 | line-1-0673-0306-s017777 | station | forward | revenue | 1 |
| line-1 | line-1-0673-0306-s017777 | station | reverse | revenue | 1 |
| line-1 | line-1-0696-0396-s015721 | station | forward | revenue | 1 |
| line-1 | line-1-0696-0396-s015721 | station | reverse | revenue | 1 |
| line-1 | line-1-0733-0298-s019814 | station | reverse | revenue | 2 |
| line-2 | line-2-0554-0539-s010503 | station | forward | revenue | 1 |
| line-2 | line-2-0554-0539-s010503 | station | reverse | revenue | 1 |
| line-2 | line-2-0565-0450-s012447 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0450-s012447 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0598-s008460 | station | forward | revenue | 1 |
| line-2 | line-2-0604-0598-s008460 | station | reverse | revenue | 1 |
| line-2 | line-2-0609-0917-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0626-0346-s015449 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0346-s015449 | station | reverse | revenue | 1 |
| line-2 | line-2-0626-0680-s006415 | station | forward | revenue | 1 |
| line-2 | line-2-0626-0680-s006415 | station | reverse | revenue | 1 |
| line-2 | line-2-0671-0218-s019026 | station | forward | revenue | 1 |
| line-2 | line-2-0671-0218-s019026 | station | reverse | revenue | 1 |
| line-2 | line-2-0708-0058-s022608 | station | reverse | revenue | 2 |
| line-3 | line-3-0451-0402-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0506-0499-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0506-0499-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0539-s004613 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0539-s004613 | station | reverse | revenue | 1 |
| line-3 | line-3-0582-0487-s006028 | station | forward | revenue | 1 |
| line-3 | line-3-0582-0487-s006028 | station | reverse | revenue | 1 |
| line-3 | line-3-0781-0464-s010598 | station | reverse | revenue | 2 |
| line-1 | line-1-0733-0298-s019814 | depot | — | revenue | 21 |
| line-1 | line-1-0733-0298-s019814 | depot | — | spare | 3 |
| line-1 | line-1-0733-0298-s019814 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0708-0058-s022608 | depot | — | revenue | 26 |
| line-2 | line-2-0708-0058-s022608 | depot | — | spare | 4 |
| line-2 | line-2-0708-0058-s022608 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0781-0464-s010598 | depot | — | revenue | 11 |
| line-3 | line-3-0781-0464-s010598 | depot | — | spare | 2 |
| line-3 | line-3-0781-0464-s010598 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mbeya-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **112 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **100 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **70 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0448-0937-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0534-0829-s003001 | forward | revenue | 3 | pending |
| line-1 | line-1-0534-0829-s003001 | reverse | revenue | 3 | pending |
| line-1 | line-1-0571-0700-s006008 | forward | revenue | 3 | pending |
| line-1 | line-1-0571-0700-s006008 | reverse | revenue | 3 | pending |
| line-1 | line-1-0554-0539-s009494 | forward | revenue | 3 | pending |
| line-1 | line-1-0554-0539-s009494 | reverse | revenue | 3 | pending |
| line-1 | line-1-0624-0504-s012032 | forward | revenue | 3 | pending |
| line-1 | line-1-0624-0504-s012032 | reverse | revenue | 3 | pending |
| line-1 | line-1-0696-0396-s015721 | forward | revenue | 2 | pending |
| line-1 | line-1-0696-0396-s015721 | reverse | revenue | 2 | pending |
| line-1 | line-1-0673-0306-s017777 | forward | revenue | 2 | pending |
| line-1 | line-1-0673-0306-s017777 | reverse | revenue | 2 | pending |
| line-1 | line-1-0733-0298-s019814 | reverse | revenue | 2 | pending |
| line-1 | line-1-0696-0396-s015721 | forward | spare | 1 | pending |
| line-1 | line-1-0696-0396-s015721 | reverse | spare | 1 | pending |
| line-1 | line-1-0673-0306-s017777 | forward | spare | 1 | pending |
| line-1 | line-1-0673-0306-s017777 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0609-0917-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0626-0680-s006415 | forward | revenue | 3 | pending |
| line-2 | line-2-0626-0680-s006415 | reverse | revenue | 3 | pending |
| line-2 | line-2-0604-0598-s008460 | forward | revenue | 3 | pending |
| line-2 | line-2-0604-0598-s008460 | reverse | revenue | 3 | pending |
| line-2 | line-2-0554-0539-s010503 | forward | revenue | 3 | pending |
| line-2 | line-2-0554-0539-s010503 | reverse | revenue | 3 | pending |
| line-2 | line-2-0565-0450-s012447 | forward | revenue | 3 | pending |
| line-2 | line-2-0565-0450-s012447 | reverse | revenue | 3 | pending |
| line-2 | line-2-0626-0346-s015449 | forward | revenue | 3 | pending |
| line-2 | line-2-0626-0346-s015449 | reverse | revenue | 3 | pending |
| line-2 | line-2-0671-0218-s019026 | forward | revenue | 3 | pending |
| line-2 | line-2-0671-0218-s019026 | reverse | revenue | 3 | pending |
| line-2 | line-2-0708-0058-s022608 | reverse | revenue | 3 | pending |
| line-2 | line-2-0609-0917-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0626-0680-s006415 | forward | spare | 1 | pending |
| line-2 | line-2-0626-0680-s006415 | reverse | spare | 1 | pending |
| line-2 | line-2-0604-0598-s008460 | forward | spare | 1 | pending |
| line-2 | line-2-0604-0598-s008460 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0451-0402-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0506-0499-s003009 | forward | revenue | 3 | pending |
| line-3 | line-3-0506-0499-s003009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0554-0539-s004613 | forward | revenue | 3 | pending |
| line-3 | line-3-0554-0539-s004613 | reverse | revenue | 3 | pending |
| line-3 | line-3-0582-0487-s006028 | forward | revenue | 2 | pending |
| line-3 | line-3-0582-0487-s006028 | reverse | revenue | 2 | pending |
| line-3 | line-3-0781-0464-s010598 | reverse | revenue | 2 | pending |
| line-3 | line-3-0582-0487-s006028 | forward | spare | 1 | pending |
| line-3 | line-3-0582-0487-s006028 | reverse | spare | 1 | pending |
| line-3 | line-3-0781-0464-s010598 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**64 trainsets exceed the reference platform envelope**, requiring **3,808.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0448-0937-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0534-0829-s003001 | 6 | 2 | 4 | 238.0 |
| line-1-0554-0539-s009494 | 6 | 4 | 2 | 119.0 |
| line-1-0571-0700-s006008 | 6 | 2 | 4 | 238.0 |
| line-1-0624-0504-s012032 | 6 | 2 | 4 | 238.0 |
| line-1-0673-0306-s017777 | 6 | 2 | 4 | 238.0 |
| line-1-0696-0396-s015721 | 6 | 2 | 4 | 238.0 |
| line-1-0733-0298-s019814 | 2 | 2 | 0 | 0.0 |
| line-2-0554-0539-s010503 | 6 | 4 | 2 | 119.0 |
| line-2-0565-0450-s012447 | 6 | 2 | 4 | 238.0 |
| line-2-0604-0598-s008460 | 8 | 2 | 6 | 357.0 |
| line-2-0609-0917-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0626-0346-s015449 | 6 | 2 | 4 | 238.0 |
| line-2-0626-0680-s006415 | 8 | 2 | 6 | 357.0 |
| line-2-0671-0218-s019026 | 6 | 2 | 4 | 238.0 |
| line-2-0708-0058-s022608 | 3 | 2 | 1 | 59.5 |
| line-3-0451-0402-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0506-0499-s003009 | 6 | 2 | 4 | 238.0 |
| line-3-0554-0539-s004613 | 6 | 4 | 2 | 119.0 |
| line-3-0582-0487-s006028 | 6 | 2 | 4 | 238.0 |
| line-3-0781-0464-s010598 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Mbeya/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
