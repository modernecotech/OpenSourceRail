# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 98 at depots = 126 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0479-0844-s000000 | line-1 | declared-depot | 23 | 1,368.5 | 5 |
| line-2-0274-0567-s020310 | line-2 | declared-depot | 53 | 3,153.5 | 9 |
| line-3-0676-0728-s000000 | line-3 | declared-depot | 22 | 1,309.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0393-0371-s010196 | station | reverse | revenue | 2 |
| line-1 | line-1-0423-0537-s006616 | station | forward | revenue | 1 |
| line-1 | line-1-0423-0537-s006616 | station | reverse | revenue | 1 |
| line-1 | line-1-0454-0704-s003019 | station | forward | revenue | 1 |
| line-1 | line-1-0454-0704-s003019 | station | reverse | revenue | 1 |
| line-1 | line-1-0479-0844-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0274-0567-s020310 | station | reverse | revenue | 2 |
| line-2 | line-2-0371-0525-s017976 | station | forward | revenue | 1 |
| line-2 | line-2-0371-0525-s017976 | station | reverse | revenue | 1 |
| line-2 | line-2-0469-0483-s015621 | station | forward | revenue | 1 |
| line-2 | line-2-0469-0483-s015621 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0441-s013289 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0441-s013289 | station | reverse | revenue | 1 |
| line-2 | line-2-1084-0152-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0454-0347-s009670 | station | reverse | revenue | 2 |
| line-3 | line-3-0510-0443-s007227 | station | forward | revenue | 1 |
| line-3 | line-3-0510-0443-s007227 | station | reverse | revenue | 1 |
| line-3 | line-3-0566-0540-s004777 | station | forward | revenue | 1 |
| line-3 | line-3-0566-0540-s004777 | station | reverse | revenue | 1 |
| line-3 | line-3-0607-0610-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0607-0610-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0676-0728-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0479-0844-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0479-0844-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0479-0844-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0274-0567-s020310 | depot | — | revenue | 47 |
| line-2 | line-2-0274-0567-s020310 | depot | — | spare | 5 |
| line-2 | line-2-0274-0567-s020310 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0676-0728-s000000 | depot | — | revenue | 19 |
| line-3 | line-3-0676-0728-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0676-0728-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sylhet-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **126 trainsets at 14 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **114 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0479-0844-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0454-0704-s003019 | forward | revenue | 5 | pending |
| line-1 | line-1-0454-0704-s003019 | reverse | revenue | 5 | pending |
| line-1 | line-1-0423-0537-s006616 | forward | revenue | 5 | pending |
| line-1 | line-1-0423-0537-s006616 | reverse | revenue | 4 | pending |
| line-1 | line-1-0393-0371-s010196 | reverse | revenue | 4 | pending |
| line-1 | line-1-0423-0537-s006616 | reverse | spare | 1 | pending |
| line-1 | line-1-0393-0371-s010196 | reverse | spare | 1 | pending |
| line-1 | line-1-0479-0844-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1084-0152-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0567-0441-s013289 | forward | revenue | 7 | pending |
| line-2 | line-2-0567-0441-s013289 | reverse | revenue | 7 | pending |
| line-2 | line-2-0469-0483-s015621 | forward | revenue | 7 | pending |
| line-2 | line-2-0469-0483-s015621 | reverse | revenue | 7 | pending |
| line-2 | line-2-0371-0525-s017976 | forward | revenue | 7 | pending |
| line-2 | line-2-0371-0525-s017976 | reverse | revenue | 7 | pending |
| line-2 | line-2-0274-0567-s020310 | reverse | revenue | 7 | pending |
| line-2 | line-2-0567-0441-s013289 | forward | spare | 1 | pending |
| line-2 | line-2-0567-0441-s013289 | reverse | spare | 1 | pending |
| line-2 | line-2-0469-0483-s015621 | forward | spare | 1 | pending |
| line-2 | line-2-0469-0483-s015621 | reverse | spare | 1 | pending |
| line-2 | line-2-0371-0525-s017976 | forward | spare | 1 | pending |
| line-2 | line-2-0371-0525-s017976 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0676-0728-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0607-0610-s003002 | forward | revenue | 4 | pending |
| line-3 | line-3-0607-0610-s003002 | reverse | revenue | 4 | pending |
| line-3 | line-3-0566-0540-s004777 | forward | revenue | 4 | pending |
| line-3 | line-3-0566-0540-s004777 | reverse | revenue | 4 | pending |
| line-3 | line-3-0510-0443-s007227 | forward | revenue | 3 | pending |
| line-3 | line-3-0510-0443-s007227 | reverse | revenue | 3 | pending |
| line-3 | line-3-0454-0347-s009670 | reverse | revenue | 3 | pending |
| line-3 | line-3-0510-0443-s007227 | forward | spare | 1 | pending |
| line-3 | line-3-0510-0443-s007227 | reverse | spare | 1 | pending |
| line-3 | line-3-0454-0347-s009670 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**98 trainsets exceed the reference platform envelope**, requiring **5,831.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0393-0371-s010196 | 5 | 2 | 3 | 178.5 |
| line-1-0423-0537-s006616 | 10 | 2 | 8 | 476.0 |
| line-1-0454-0704-s003019 | 10 | 2 | 8 | 476.0 |
| line-1-0479-0844-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0274-0567-s020310 | 7 | 2 | 5 | 297.5 |
| line-2-0371-0525-s017976 | 16 | 2 | 14 | 833.0 |
| line-2-0469-0483-s015621 | 16 | 2 | 14 | 833.0 |
| line-2-0567-0441-s013289 | 16 | 2 | 14 | 833.0 |
| line-2-1084-0152-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0454-0347-s009670 | 4 | 2 | 2 | 119.0 |
| line-3-0510-0443-s007227 | 8 | 2 | 6 | 357.0 |
| line-3-0566-0540-s004777 | 8 | 2 | 6 | 357.0 |
| line-3-0607-0610-s003002 | 8 | 2 | 6 | 357.0 |
| line-3-0676-0728-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Sylhet/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
