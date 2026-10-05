# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 88 at depots = 126 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0512-0958-s016444 | line-1 | declared-depot | 38 | 2,261.0 | 8 |
| line-2-0344-0606-s000000 | line-2 | declared-depot | 27 | 1,606.5 | 6 |
| line-3-0738-0736-s000000 | line-3 | declared-depot | 23 | 1,368.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0512-0958-s016444 | station | reverse | revenue | 2 |
| line-1 | line-1-0542-0851-s013950 | station | forward | revenue | 1 |
| line-1 | line-1-0542-0851-s013950 | station | reverse | revenue | 1 |
| line-1 | line-1-0590-0749-s011465 | station | forward | revenue | 1 |
| line-1 | line-1-0590-0749-s011465 | station | reverse | revenue | 1 |
| line-1 | line-1-0637-0647-s008989 | station | forward | revenue | 1 |
| line-1 | line-1-0637-0647-s008989 | station | reverse | revenue | 1 |
| line-1 | line-1-0657-0604-s007952 | station | forward | revenue | 1 |
| line-1 | line-1-0657-0604-s007952 | station | reverse | revenue | 1 |
| line-1 | line-1-0690-0532-s006215 | station | forward | revenue | 1 |
| line-1 | line-1-0690-0532-s006215 | station | reverse | revenue | 1 |
| line-1 | line-1-0809-0277-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0344-0606-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0486-0626-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0486-0626-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0637-0647-s006200 | station | forward | revenue | 1 |
| line-2 | line-2-0637-0647-s006200 | station | reverse | revenue | 1 |
| line-2 | line-2-0687-0654-s007258 | station | forward | revenue | 1 |
| line-2 | line-2-0687-0654-s007258 | station | reverse | revenue | 1 |
| line-2 | line-2-0789-0668-s009414 | station | forward | revenue | 1 |
| line-2 | line-2-0789-0668-s009414 | station | reverse | revenue | 1 |
| line-2 | line-2-0890-0681-s011558 | station | reverse | revenue | 2 |
| line-3 | line-3-0483-0321-s010858 | station | reverse | revenue | 2 |
| line-3 | line-3-0539-0413-s008448 | station | forward | revenue | 1 |
| line-3 | line-3-0539-0413-s008448 | station | reverse | revenue | 1 |
| line-3 | line-3-0596-0506-s006022 | station | forward | revenue | 1 |
| line-3 | line-3-0596-0506-s006022 | station | reverse | revenue | 1 |
| line-3 | line-3-0657-0604-s003452 | station | forward | revenue | 1 |
| line-3 | line-3-0657-0604-s003452 | station | reverse | revenue | 1 |
| line-3 | line-3-0687-0654-s002168 | station | forward | revenue | 1 |
| line-3 | line-3-0687-0654-s002168 | station | reverse | revenue | 1 |
| line-3 | line-3-0738-0736-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0512-0958-s016444 | depot | — | revenue | 33 |
| line-1 | line-1-0512-0958-s016444 | depot | — | spare | 4 |
| line-1 | line-1-0512-0958-s016444 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0344-0606-s000000 | depot | — | revenue | 23 |
| line-2 | line-2-0344-0606-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0344-0606-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0738-0736-s000000 | depot | — | revenue | 19 |
| line-3 | line-3-0738-0736-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0738-0736-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nyala-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **126 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **113 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **88 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0809-0277-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0690-0532-s006215 | forward | revenue | 4 | pending |
| line-1 | line-1-0690-0532-s006215 | reverse | revenue | 4 | pending |
| line-1 | line-1-0657-0604-s007952 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0604-s007952 | reverse | revenue | 4 | pending |
| line-1 | line-1-0637-0647-s008989 | forward | revenue | 4 | pending |
| line-1 | line-1-0637-0647-s008989 | reverse | revenue | 4 | pending |
| line-1 | line-1-0590-0749-s011465 | forward | revenue | 4 | pending |
| line-1 | line-1-0590-0749-s011465 | reverse | revenue | 4 | pending |
| line-1 | line-1-0542-0851-s013950 | forward | revenue | 4 | pending |
| line-1 | line-1-0542-0851-s013950 | reverse | revenue | 4 | pending |
| line-1 | line-1-0512-0958-s016444 | reverse | revenue | 3 | pending |
| line-1 | line-1-0512-0958-s016444 | reverse | spare | 1 | pending |
| line-1 | line-1-0809-0277-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0690-0532-s006215 | forward | spare | 1 | pending |
| line-1 | line-1-0690-0532-s006215 | reverse | spare | 1 | pending |
| line-1 | line-1-0657-0604-s007952 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0344-0606-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0486-0626-s003006 | forward | revenue | 4 | pending |
| line-2 | line-2-0486-0626-s003006 | reverse | revenue | 4 | pending |
| line-2 | line-2-0637-0647-s006200 | forward | revenue | 4 | pending |
| line-2 | line-2-0637-0647-s006200 | reverse | revenue | 4 | pending |
| line-2 | line-2-0687-0654-s007258 | forward | revenue | 3 | pending |
| line-2 | line-2-0687-0654-s007258 | reverse | revenue | 3 | pending |
| line-2 | line-2-0789-0668-s009414 | forward | revenue | 3 | pending |
| line-2 | line-2-0789-0668-s009414 | reverse | revenue | 3 | pending |
| line-2 | line-2-0890-0681-s011558 | reverse | revenue | 3 | pending |
| line-2 | line-2-0687-0654-s007258 | forward | spare | 1 | pending |
| line-2 | line-2-0687-0654-s007258 | reverse | spare | 1 | pending |
| line-2 | line-2-0789-0668-s009414 | forward | spare | 1 | pending |
| line-2 | line-2-0789-0668-s009414 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0738-0736-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0687-0654-s002168 | forward | revenue | 3 | pending |
| line-3 | line-3-0687-0654-s002168 | reverse | revenue | 3 | pending |
| line-3 | line-3-0657-0604-s003452 | forward | revenue | 3 | pending |
| line-3 | line-3-0657-0604-s003452 | reverse | revenue | 3 | pending |
| line-3 | line-3-0596-0506-s006022 | forward | revenue | 3 | pending |
| line-3 | line-3-0596-0506-s006022 | reverse | revenue | 3 | pending |
| line-3 | line-3-0539-0413-s008448 | forward | revenue | 3 | pending |
| line-3 | line-3-0539-0413-s008448 | reverse | revenue | 3 | pending |
| line-3 | line-3-0483-0321-s010858 | reverse | revenue | 3 | pending |
| line-3 | line-3-0687-0654-s002168 | forward | spare | 1 | pending |
| line-3 | line-3-0687-0654-s002168 | reverse | spare | 1 | pending |
| line-3 | line-3-0657-0604-s003452 | forward | spare | 1 | pending |
| line-3 | line-3-0657-0604-s003452 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**76 trainsets exceed the reference platform envelope**, requiring **4,522.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0512-0958-s016444 | 4 | 2 | 2 | 119.0 |
| line-1-0542-0851-s013950 | 8 | 2 | 6 | 357.0 |
| line-1-0590-0749-s011465 | 8 | 2 | 6 | 357.0 |
| line-1-0637-0647-s008989 | 8 | 4 | 4 | 238.0 |
| line-1-0657-0604-s007952 | 9 | 4 | 5 | 297.5 |
| line-1-0690-0532-s006215 | 10 | 2 | 8 | 476.0 |
| line-1-0809-0277-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0344-0606-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0486-0626-s003006 | 8 | 2 | 6 | 357.0 |
| line-2-0637-0647-s006200 | 8 | 4 | 4 | 238.0 |
| line-2-0687-0654-s007258 | 8 | 4 | 4 | 238.0 |
| line-2-0789-0668-s009414 | 8 | 2 | 6 | 357.0 |
| line-2-0890-0681-s011558 | 3 | 2 | 1 | 59.5 |
| line-3-0483-0321-s010858 | 3 | 2 | 1 | 59.5 |
| line-3-0539-0413-s008448 | 6 | 2 | 4 | 238.0 |
| line-3-0596-0506-s006022 | 6 | 2 | 4 | 238.0 |
| line-3-0657-0604-s003452 | 8 | 4 | 4 | 238.0 |
| line-3-0687-0654-s002168 | 8 | 4 | 4 | 238.0 |
| line-3-0738-0736-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Nyala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
