# Station and depot overnight allocation

Plan: **34 trainsets at stations + 55 at depots = 89 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0763-0392-s015726 | line-1 | declared-depot | 23 | 1,368.5 | 14 |
| line-2-0755-0613-s012219 | line-2 | storage-at-existing-powered-service-point | 17 | 1,011.5 | 0 |
| line-3-0436-0420-s011413 | line-3 | storage-at-existing-powered-service-point | 15 | 892.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0413-0831-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0528-0695-s004699 | station | forward | revenue | 1 |
| line-1 | line-1-0528-0695-s004699 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0548-s008298 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0548-s008298 | station | reverse | revenue | 1 |
| line-1 | line-1-0622-0498-s010717 | station | forward | revenue | 1 |
| line-1 | line-1-0622-0498-s010717 | station | reverse | revenue | 1 |
| line-1 | line-1-0658-0424-s013218 | station | forward | revenue | 1 |
| line-1 | line-1-0658-0424-s013218 | station | reverse | revenue | 1 |
| line-1 | line-1-0763-0392-s015726 | station | reverse | revenue | 2 |
| line-2 | line-2-0324-0563-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0440-0601-s003013 | station | forward | revenue | 1 |
| line-2 | line-2-0440-0601-s003013 | station | reverse | revenue | 1 |
| line-2 | line-2-0554-0548-s006728 | station | forward | revenue | 1 |
| line-2 | line-2-0554-0548-s006728 | station | reverse | revenue | 1 |
| line-2 | line-2-0627-0616-s009041 | station | forward | revenue | 1 |
| line-2 | line-2-0627-0616-s009041 | station | reverse | revenue | 1 |
| line-2 | line-2-0755-0613-s012219 | station | reverse | revenue | 2 |
| line-3 | line-3-0436-0420-s011413 | station | reverse | revenue | 2 |
| line-3 | line-3-0514-0476-s009039 | station | forward | revenue | 1 |
| line-3 | line-3-0514-0476-s009039 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0548-s006912 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0548-s006912 | station | reverse | revenue | 1 |
| line-3 | line-3-0627-0572-s004966 | station | forward | revenue | 1 |
| line-3 | line-3-0627-0572-s004966 | station | reverse | revenue | 1 |
| line-3 | line-3-0686-0519-s003006 | station | forward | revenue | 1 |
| line-3 | line-3-0686-0519-s003006 | station | reverse | revenue | 1 |
| line-3 | line-3-0769-0485-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0763-0392-s015726 | depot | — | revenue | 19 |
| line-1 | line-1-0763-0392-s015726 | depot | — | spare | 3 |
| line-1 | line-1-0763-0392-s015726 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0755-0613-s012219 | depot | — | revenue | 14 |
| line-2 | line-2-0755-0613-s012219 | depot | — | spare | 2 |
| line-2 | line-2-0755-0613-s012219 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0436-0420-s011413 | depot | — | revenue | 12 |
| line-3 | line-3-0436-0420-s011413 | depot | — | spare | 2 |
| line-3 | line-3-0436-0420-s011413 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/meknes-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **89 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **79 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **55 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0413-0831-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0528-0695-s004699 | forward | revenue | 3 | pending |
| line-1 | line-1-0528-0695-s004699 | reverse | revenue | 3 | pending |
| line-1 | line-1-0554-0548-s008298 | forward | revenue | 3 | pending |
| line-1 | line-1-0554-0548-s008298 | reverse | revenue | 3 | pending |
| line-1 | line-1-0622-0498-s010717 | forward | revenue | 3 | pending |
| line-1 | line-1-0622-0498-s010717 | reverse | revenue | 3 | pending |
| line-1 | line-1-0658-0424-s013218 | forward | revenue | 3 | pending |
| line-1 | line-1-0658-0424-s013218 | reverse | revenue | 3 | pending |
| line-1 | line-1-0763-0392-s015726 | reverse | revenue | 3 | pending |
| line-1 | line-1-0528-0695-s004699 | forward | spare | 1 | pending |
| line-1 | line-1-0528-0695-s004699 | reverse | spare | 1 | pending |
| line-1 | line-1-0554-0548-s008298 | forward | spare | 1 | pending |
| line-1 | line-1-0554-0548-s008298 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0324-0563-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0440-0601-s003013 | forward | revenue | 3 | pending |
| line-2 | line-2-0440-0601-s003013 | reverse | revenue | 3 | pending |
| line-2 | line-2-0554-0548-s006728 | forward | revenue | 3 | pending |
| line-2 | line-2-0554-0548-s006728 | reverse | revenue | 3 | pending |
| line-2 | line-2-0627-0616-s009041 | forward | revenue | 3 | pending |
| line-2 | line-2-0627-0616-s009041 | reverse | revenue | 3 | pending |
| line-2 | line-2-0755-0613-s012219 | reverse | revenue | 3 | pending |
| line-2 | line-2-0324-0563-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0440-0601-s003013 | forward | spare | 1 | pending |
| line-2 | line-2-0440-0601-s003013 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0769-0485-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0686-0519-s003006 | forward | revenue | 3 | pending |
| line-3 | line-3-0686-0519-s003006 | reverse | revenue | 3 | pending |
| line-3 | line-3-0627-0572-s004966 | forward | revenue | 3 | pending |
| line-3 | line-3-0627-0572-s004966 | reverse | revenue | 2 | pending |
| line-3 | line-3-0554-0548-s006912 | forward | revenue | 2 | pending |
| line-3 | line-3-0554-0548-s006912 | reverse | revenue | 2 | pending |
| line-3 | line-3-0514-0476-s009039 | forward | revenue | 2 | pending |
| line-3 | line-3-0514-0476-s009039 | reverse | revenue | 2 | pending |
| line-3 | line-3-0436-0420-s011413 | reverse | revenue | 2 | pending |
| line-3 | line-3-0627-0572-s004966 | reverse | spare | 1 | pending |
| line-3 | line-3-0554-0548-s006912 | forward | spare | 1 | pending |
| line-3 | line-3-0554-0548-s006912 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**49 trainsets exceed the reference platform envelope**, requiring **2,915.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0413-0831-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0528-0695-s004699 | 8 | 2 | 6 | 357.0 |
| line-1-0554-0548-s008298 | 8 | 4 | 4 | 238.0 |
| line-1-0622-0498-s010717 | 6 | 2 | 4 | 238.0 |
| line-1-0658-0424-s013218 | 6 | 2 | 4 | 238.0 |
| line-1-0763-0392-s015726 | 3 | 2 | 1 | 59.5 |
| line-2-0324-0563-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0440-0601-s003013 | 8 | 2 | 6 | 357.0 |
| line-2-0554-0548-s006728 | 6 | 4 | 2 | 119.0 |
| line-2-0627-0616-s009041 | 6 | 2 | 4 | 238.0 |
| line-2-0755-0613-s012219 | 3 | 2 | 1 | 59.5 |
| line-3-0436-0420-s011413 | 2 | 2 | 0 | 0.0 |
| line-3-0514-0476-s009039 | 4 | 2 | 2 | 119.0 |
| line-3-0554-0548-s006912 | 6 | 4 | 2 | 119.0 |
| line-3-0627-0572-s004966 | 6 | 2 | 4 | 238.0 |
| line-3-0686-0519-s003006 | 6 | 2 | 4 | 238.0 |
| line-3-0769-0485-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Meknes/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
