# Station and depot overnight allocation

Plan: **30 trainsets at stations + 41 at depots = 71 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0761-0550-s009675 | line-1 | storage-at-existing-powered-service-point | 13 | 773.5 | 0 |
| line-2-0384-0342-s011570 | line-2 | declared-depot | 15 | 892.5 | 11 |
| line-3-0433-0500-s009427 | line-3 | storage-at-existing-powered-service-point | 13 | 773.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0438-0661-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0503-0587-s003011 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0587-s003011 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0553-s004358 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0553-s004358 | station | reverse | revenue | 1 |
| line-1 | line-1-0651-0539-s007010 | station | forward | revenue | 1 |
| line-1 | line-1-0651-0539-s007010 | station | reverse | revenue | 1 |
| line-1 | line-1-0761-0550-s009675 | station | reverse | revenue | 2 |
| line-2 | line-2-0384-0342-s011570 | station | reverse | revenue | 2 |
| line-2 | line-2-0464-0396-s009459 | station | forward | revenue | 1 |
| line-2 | line-2-0464-0396-s009459 | station | reverse | revenue | 1 |
| line-2 | line-2-0538-0470-s007331 | station | forward | revenue | 1 |
| line-2 | line-2-0538-0470-s007331 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0553-s005218 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0553-s005218 | station | reverse | revenue | 1 |
| line-2 | line-2-0602-0608-s003023 | station | forward | revenue | 1 |
| line-2 | line-2-0602-0608-s003023 | station | reverse | revenue | 1 |
| line-2 | line-2-0701-0650-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0433-0500-s009427 | station | reverse | revenue | 2 |
| line-3 | line-3-0512-0772-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0528-0670-s003013 | station | forward | revenue | 1 |
| line-3 | line-3-0528-0670-s003013 | station | reverse | revenue | 1 |
| line-3 | line-3-0551-0553-s005843 | station | forward | revenue | 1 |
| line-3 | line-3-0551-0553-s005843 | station | reverse | revenue | 1 |
| line-1 | line-1-0761-0550-s009675 | depot | — | revenue | 10 |
| line-1 | line-1-0761-0550-s009675 | depot | — | spare | 2 |
| line-1 | line-1-0761-0550-s009675 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0384-0342-s011570 | depot | — | revenue | 12 |
| line-2 | line-2-0384-0342-s011570 | depot | — | spare | 2 |
| line-2 | line-2-0384-0342-s011570 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0433-0500-s009427 | depot | — | revenue | 11 |
| line-3 | line-3-0433-0500-s009427 | depot | — | spare | 1 |
| line-3 | line-3-0433-0500-s009427 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hodeidah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **71 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **63 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **41 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0438-0661-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0503-0587-s003011 | forward | revenue | 3 | pending |
| line-1 | line-1-0503-0587-s003011 | reverse | revenue | 3 | pending |
| line-1 | line-1-0551-0553-s004358 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0553-s004358 | reverse | revenue | 2 | pending |
| line-1 | line-1-0651-0539-s007010 | forward | revenue | 2 | pending |
| line-1 | line-1-0651-0539-s007010 | reverse | revenue | 2 | pending |
| line-1 | line-1-0761-0550-s009675 | reverse | revenue | 2 | pending |
| line-1 | line-1-0551-0553-s004358 | reverse | spare | 1 | pending |
| line-1 | line-1-0651-0539-s007010 | forward | spare | 1 | pending |
| line-1 | line-1-0651-0539-s007010 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0701-0650-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0602-0608-s003023 | forward | revenue | 3 | pending |
| line-2 | line-2-0602-0608-s003023 | reverse | revenue | 3 | pending |
| line-2 | line-2-0551-0553-s005218 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0553-s005218 | reverse | revenue | 2 | pending |
| line-2 | line-2-0538-0470-s007331 | forward | revenue | 2 | pending |
| line-2 | line-2-0538-0470-s007331 | reverse | revenue | 2 | pending |
| line-2 | line-2-0464-0396-s009459 | forward | revenue | 2 | pending |
| line-2 | line-2-0464-0396-s009459 | reverse | revenue | 2 | pending |
| line-2 | line-2-0384-0342-s011570 | reverse | revenue | 2 | pending |
| line-2 | line-2-0551-0553-s005218 | reverse | spare | 1 | pending |
| line-2 | line-2-0538-0470-s007331 | forward | spare | 1 | pending |
| line-2 | line-2-0538-0470-s007331 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0512-0772-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0528-0670-s003013 | forward | revenue | 3 | pending |
| line-3 | line-3-0528-0670-s003013 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0553-s005843 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0553-s005843 | reverse | revenue | 3 | pending |
| line-3 | line-3-0433-0500-s009427 | reverse | revenue | 3 | pending |
| line-3 | line-3-0528-0670-s003013 | forward | spare | 1 | pending |
| line-3 | line-3-0528-0670-s003013 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**35 trainsets exceed the reference platform envelope**, requiring **2,082.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0438-0661-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0503-0587-s003011 | 6 | 2 | 4 | 238.0 |
| line-1-0551-0553-s004358 | 6 | 4 | 2 | 119.0 |
| line-1-0651-0539-s007010 | 6 | 2 | 4 | 238.0 |
| line-1-0761-0550-s009675 | 2 | 2 | 0 | 0.0 |
| line-2-0384-0342-s011570 | 2 | 2 | 0 | 0.0 |
| line-2-0464-0396-s009459 | 4 | 2 | 2 | 119.0 |
| line-2-0538-0470-s007331 | 6 | 2 | 4 | 238.0 |
| line-2-0551-0553-s005218 | 6 | 4 | 2 | 119.0 |
| line-2-0602-0608-s003023 | 6 | 2 | 4 | 238.0 |
| line-2-0701-0650-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0433-0500-s009427 | 3 | 2 | 1 | 59.5 |
| line-3-0512-0772-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0528-0670-s003013 | 8 | 2 | 6 | 357.0 |
| line-3-0551-0553-s005843 | 6 | 4 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Hodeidah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
