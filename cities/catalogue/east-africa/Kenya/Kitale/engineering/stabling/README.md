# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 63 at depots = 99 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0729-0702-s014613 | line-1 | declared-depot | 21 | 1,029.0 | 5 |
| line-2-0608-0115-s000000 | line-2 | declared-depot | 17 | 833.0 | 4 |
| line-3-0529-0442-s000000 | line-3 | declared-depot | 13 | 637.0 | 4 |
| line-4-0516-0216-s000000 | line-4 | declared-depot | 12 | 588.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0376-0372-s003076 | station | forward | revenue | 1 |
| line-1 | line-1-0376-0372-s003076 | station | reverse | revenue | 1 |
| line-1 | line-1-0383-0371-s003240 | station | forward | revenue | 1 |
| line-1 | line-1-0383-0371-s003240 | station | reverse | revenue | 1 |
| line-1 | line-1-0406-0246-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0526-0447-s006954 | station | forward | revenue | 1 |
| line-1 | line-1-0526-0447-s006954 | station | reverse | revenue | 1 |
| line-1 | line-1-0729-0702-s014613 | station | reverse | revenue | 2 |
| line-2 | line-2-0216-0565-s013431 | station | reverse | revenue | 2 |
| line-2 | line-2-0376-0379-s007940 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0379-s007940 | station | reverse | revenue | 1 |
| line-2 | line-2-0383-0371-s007710 | station | forward | revenue | 1 |
| line-2 | line-2-0383-0371-s007710 | station | reverse | revenue | 1 |
| line-2 | line-2-0516-0216-s003145 | station | forward | revenue | 1 |
| line-2 | line-2-0516-0216-s003145 | station | reverse | revenue | 1 |
| line-2 | line-2-0608-0115-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0068-0325-s011354 | station | reverse | revenue | 2 |
| line-3 | line-3-0231-0325-s007841 | station | forward | revenue | 1 |
| line-3 | line-3-0231-0325-s007841 | station | reverse | revenue | 1 |
| line-3 | line-3-0376-0373-s004312 | station | forward | revenue | 1 |
| line-3 | line-3-0376-0373-s004312 | station | reverse | revenue | 1 |
| line-3 | line-3-0376-0379-s004148 | station | forward | revenue | 1 |
| line-3 | line-3-0376-0379-s004148 | station | reverse | revenue | 1 |
| line-3 | line-3-0526-0447-s000137 | station | forward | revenue | 1 |
| line-3 | line-3-0526-0447-s000137 | station | reverse | revenue | 1 |
| line-3 | line-3-0529-0442-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0287-0262-s007078 | station | reverse | revenue | 2 |
| line-4 | line-4-0516-0216-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0729-0702-s014613 | depot | — | revenue | 18 |
| line-1 | line-1-0729-0702-s014613 | depot | — | spare | 2 |
| line-1 | line-1-0729-0702-s014613 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0608-0115-s000000 | depot | — | revenue | 14 |
| line-2 | line-2-0608-0115-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0608-0115-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0529-0442-s000000 | depot | — | revenue | 10 |
| line-3 | line-3-0529-0442-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0529-0442-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0516-0216-s000000 | depot | — | revenue | 10 |
| line-4 | line-4-0516-0216-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0516-0216-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kitale-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **99 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **88 revenue, 7 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **63 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0406-0246-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0376-0372-s003076 | forward | revenue | 4 | pending |
| line-1 | line-1-0376-0372-s003076 | reverse | revenue | 4 | pending |
| line-1 | line-1-0383-0371-s003240 | forward | revenue | 4 | pending |
| line-1 | line-1-0383-0371-s003240 | reverse | revenue | 3 | pending |
| line-1 | line-1-0526-0447-s006954 | forward | revenue | 3 | pending |
| line-1 | line-1-0526-0447-s006954 | reverse | revenue | 3 | pending |
| line-1 | line-1-0729-0702-s014613 | reverse | revenue | 3 | pending |
| line-1 | line-1-0383-0371-s003240 | reverse | spare | 1 | pending |
| line-1 | line-1-0526-0447-s006954 | forward | spare | 1 | pending |
| line-1 | line-1-0526-0447-s006954 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0608-0115-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0516-0216-s003145 | forward | revenue | 3 | pending |
| line-2 | line-2-0516-0216-s003145 | reverse | revenue | 3 | pending |
| line-2 | line-2-0383-0371-s007710 | forward | revenue | 3 | pending |
| line-2 | line-2-0383-0371-s007710 | reverse | revenue | 3 | pending |
| line-2 | line-2-0376-0379-s007940 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0379-s007940 | reverse | revenue | 3 | pending |
| line-2 | line-2-0216-0565-s013431 | reverse | revenue | 3 | pending |
| line-2 | line-2-0608-0115-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0516-0216-s003145 | forward | spare | 1 | pending |
| line-2 | line-2-0516-0216-s003145 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0529-0442-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0526-0447-s000137 | forward | revenue | 3 | pending |
| line-3 | line-3-0526-0447-s000137 | reverse | revenue | 2 | pending |
| line-3 | line-3-0376-0379-s004148 | forward | revenue | 2 | pending |
| line-3 | line-3-0376-0379-s004148 | reverse | revenue | 2 | pending |
| line-3 | line-3-0376-0373-s004312 | forward | revenue | 2 | pending |
| line-3 | line-3-0376-0373-s004312 | reverse | revenue | 2 | pending |
| line-3 | line-3-0231-0325-s007841 | forward | revenue | 2 | pending |
| line-3 | line-3-0231-0325-s007841 | reverse | revenue | 2 | pending |
| line-3 | line-3-0068-0325-s011354 | reverse | revenue | 2 | pending |
| line-3 | line-3-0526-0447-s000137 | reverse | spare | 1 | pending |
| line-3 | line-3-0376-0379-s004148 | forward | spare | 1 | pending |
| line-3 | line-3-0376-0379-s004148 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0516-0216-s000000 | forward | revenue | 7 | pending |
| line-4 | line-4-0287-0262-s007078 | reverse | revenue | 7 | pending |
| line-4 | line-4-0516-0216-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0287-0262-s007078 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**45 trainsets exceed the reference platform envelope**, requiring **2,205.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0376-0372-s003076 | 8 | 4 | 4 | 196.0 |
| line-1-0383-0371-s003240 | 8 | 4 | 4 | 196.0 |
| line-1-0406-0246-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0526-0447-s006954 | 8 | 4 | 4 | 196.0 |
| line-1-0729-0702-s014613 | 3 | 2 | 1 | 49.0 |
| line-2-0216-0565-s013431 | 3 | 2 | 1 | 49.0 |
| line-2-0376-0379-s007940 | 6 | 4 | 2 | 98.0 |
| line-2-0383-0371-s007710 | 6 | 4 | 2 | 98.0 |
| line-2-0516-0216-s003145 | 8 | 4 | 4 | 196.0 |
| line-2-0608-0115-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0068-0325-s011354 | 2 | 2 | 0 | 0.0 |
| line-3-0231-0325-s007841 | 4 | 2 | 2 | 98.0 |
| line-3-0376-0373-s004312 | 4 | 4 | 0 | 0.0 |
| line-3-0376-0379-s004148 | 6 | 4 | 2 | 98.0 |
| line-3-0526-0447-s000137 | 6 | 4 | 2 | 98.0 |
| line-3-0529-0442-s000000 | 3 | 2 | 1 | 49.0 |
| line-4-0287-0262-s007078 | 8 | 2 | 6 | 294.0 |
| line-4-0516-0216-s000000 | 8 | 2 | 6 | 294.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kitale/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
