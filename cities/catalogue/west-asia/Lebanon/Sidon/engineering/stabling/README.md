# Station and depot overnight allocation

Plan: **28 trainsets at stations + 51 at depots = 79 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0055-0553-s015039 | line-1 | declared-depot | 21 | 1,029.0 | 12 |
| line-2-0587-0461-s009803 | line-2 | storage-at-existing-powered-service-point | 11 | 539.0 | 0 |
| line-3-0041-0657-s012916 | line-3 | storage-at-existing-powered-service-point | 19 | 931.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0055-0553-s015039 | station | reverse | revenue | 2 |
| line-1 | line-1-0322-0385-s007643 | station | forward | revenue | 1 |
| line-1 | line-1-0322-0385-s007643 | station | reverse | revenue | 1 |
| line-1 | line-1-0370-0384-s005527 | station | forward | revenue | 1 |
| line-1 | line-1-0370-0384-s005527 | station | reverse | revenue | 1 |
| line-1 | line-1-0465-0370-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0465-0370-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0585-0374-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0370-0384-s003509 | station | forward | revenue | 1 |
| line-2 | line-2-0370-0384-s003509 | station | reverse | revenue | 1 |
| line-2 | line-2-0442-0433-s005605 | station | forward | revenue | 1 |
| line-2 | line-2-0442-0433-s005605 | station | reverse | revenue | 1 |
| line-2 | line-2-0499-0328-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0519-0412-s007698 | station | forward | revenue | 1 |
| line-2 | line-2-0519-0412-s007698 | station | reverse | revenue | 1 |
| line-2 | line-2-0587-0461-s009803 | station | reverse | revenue | 2 |
| line-3 | line-3-0041-0657-s012916 | station | reverse | revenue | 2 |
| line-3 | line-3-0297-0445-s004620 | station | forward | revenue | 1 |
| line-3 | line-3-0297-0445-s004620 | station | reverse | revenue | 1 |
| line-3 | line-3-0370-0384-s001893 | station | forward | revenue | 1 |
| line-3 | line-3-0370-0384-s001893 | station | reverse | revenue | 1 |
| line-3 | line-3-0380-0462-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0055-0553-s015039 | depot | — | revenue | 18 |
| line-1 | line-1-0055-0553-s015039 | depot | — | spare | 2 |
| line-1 | line-1-0055-0553-s015039 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0587-0461-s009803 | depot | — | revenue | 9 |
| line-2 | line-2-0587-0461-s009803 | depot | — | spare | 1 |
| line-2 | line-2-0587-0461-s009803 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0041-0657-s012916 | depot | — | revenue | 16 |
| line-3 | line-3-0041-0657-s012916 | depot | — | spare | 2 |
| line-3 | line-3-0041-0657-s012916 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sidon-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **79 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **71 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **51 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0585-0374-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0465-0370-s003015 | forward | revenue | 4 | pending |
| line-1 | line-1-0465-0370-s003015 | reverse | revenue | 4 | pending |
| line-1 | line-1-0370-0384-s005527 | forward | revenue | 4 | pending |
| line-1 | line-1-0370-0384-s005527 | reverse | revenue | 3 | pending |
| line-1 | line-1-0322-0385-s007643 | forward | revenue | 3 | pending |
| line-1 | line-1-0322-0385-s007643 | reverse | revenue | 3 | pending |
| line-1 | line-1-0055-0553-s015039 | reverse | revenue | 3 | pending |
| line-1 | line-1-0370-0384-s005527 | reverse | spare | 1 | pending |
| line-1 | line-1-0322-0385-s007643 | forward | spare | 1 | pending |
| line-1 | line-1-0322-0385-s007643 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0499-0328-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0370-0384-s003509 | forward | revenue | 3 | pending |
| line-2 | line-2-0370-0384-s003509 | reverse | revenue | 3 | pending |
| line-2 | line-2-0442-0433-s005605 | forward | revenue | 2 | pending |
| line-2 | line-2-0442-0433-s005605 | reverse | revenue | 2 | pending |
| line-2 | line-2-0519-0412-s007698 | forward | revenue | 2 | pending |
| line-2 | line-2-0519-0412-s007698 | reverse | revenue | 2 | pending |
| line-2 | line-2-0587-0461-s009803 | reverse | revenue | 2 | pending |
| line-2 | line-2-0442-0433-s005605 | forward | spare | 1 | pending |
| line-2 | line-2-0442-0433-s005605 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0380-0462-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0370-0384-s001893 | forward | revenue | 4 | pending |
| line-3 | line-3-0370-0384-s001893 | reverse | revenue | 4 | pending |
| line-3 | line-3-0297-0445-s004620 | forward | revenue | 4 | pending |
| line-3 | line-3-0297-0445-s004620 | reverse | revenue | 4 | pending |
| line-3 | line-3-0041-0657-s012916 | reverse | revenue | 4 | pending |
| line-3 | line-3-0380-0462-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0370-0384-s001893 | forward | spare | 1 | pending |
| line-3 | line-3-0370-0384-s001893 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**45 trainsets exceed the reference platform envelope**, requiring **2,205.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0055-0553-s015039 | 3 | 2 | 1 | 49.0 |
| line-1-0322-0385-s007643 | 8 | 2 | 6 | 294.0 |
| line-1-0370-0384-s005527 | 8 | 4 | 4 | 196.0 |
| line-1-0465-0370-s003015 | 8 | 2 | 6 | 294.0 |
| line-1-0585-0374-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0370-0384-s003509 | 6 | 4 | 2 | 98.0 |
| line-2-0442-0433-s005605 | 6 | 2 | 4 | 196.0 |
| line-2-0499-0328-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0519-0412-s007698 | 4 | 2 | 2 | 98.0 |
| line-2-0587-0461-s009803 | 2 | 2 | 0 | 0.0 |
| line-3-0041-0657-s012916 | 4 | 2 | 2 | 98.0 |
| line-3-0297-0445-s004620 | 8 | 2 | 6 | 294.0 |
| line-3-0370-0384-s001893 | 10 | 4 | 6 | 294.0 |
| line-3-0380-0462-s000000 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Lebanon/Sidon/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
