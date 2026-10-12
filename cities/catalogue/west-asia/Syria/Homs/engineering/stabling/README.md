# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 102 at depots = 142 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0517-0336-s000000 | line-1 | declared-depot | 23 | 1,368.5 | 5 |
| line-2-0863-0415-s000000 | line-2 | declared-depot | 25 | 1,487.5 | 6 |
| line-3-0643-0792-s014803 | line-3 | declared-depot | 35 | 2,082.5 | 7 |
| line-4-0558-0540-s000000 | line-4 | declared-depot | 19 | 1,130.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0517-0336-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0647-0540-s005380 | station | forward | revenue | 1 |
| line-1 | line-1-0647-0540-s005380 | station | reverse | revenue | 1 |
| line-1 | line-1-0660-0561-s005919 | station | forward | revenue | 1 |
| line-1 | line-1-0660-0561-s005919 | station | reverse | revenue | 1 |
| line-1 | line-1-0761-0719-s010103 | station | reverse | revenue | 2 |
| line-2 | line-2-0476-0688-s011760 | station | reverse | revenue | 2 |
| line-2 | line-2-0614-0566-s007486 | station | forward | revenue | 1 |
| line-2 | line-2-0614-0566-s007486 | station | reverse | revenue | 1 |
| line-2 | line-2-0634-0549-s006922 | station | forward | revenue | 1 |
| line-2 | line-2-0634-0549-s006922 | station | reverse | revenue | 1 |
| line-2 | line-2-0647-0540-s006489 | station | forward | revenue | 1 |
| line-2 | line-2-0647-0540-s006489 | station | reverse | revenue | 1 |
| line-2 | line-2-0691-0483-s004630 | station | forward | revenue | 1 |
| line-2 | line-2-0691-0483-s004630 | station | reverse | revenue | 1 |
| line-2 | line-2-0734-0429-s003018 | station | forward | revenue | 1 |
| line-2 | line-2-0734-0429-s003018 | station | reverse | revenue | 1 |
| line-2 | line-2-0863-0415-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0276-0370-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0473-0484-s005686 | station | forward | revenue | 1 |
| line-3 | line-3-0473-0484-s005686 | station | reverse | revenue | 1 |
| line-3 | line-3-0558-0540-s008269 | station | forward | revenue | 1 |
| line-3 | line-3-0558-0540-s008269 | station | reverse | revenue | 1 |
| line-3 | line-3-0613-0565-s009701 | station | forward | revenue | 1 |
| line-3 | line-3-0613-0565-s009701 | station | reverse | revenue | 1 |
| line-3 | line-3-0643-0792-s014803 | station | reverse | revenue | 2 |
| line-4 | line-4-0558-0540-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0634-0549-s001895 | station | forward | revenue | 1 |
| line-4 | line-4-0634-0549-s001895 | station | reverse | revenue | 1 |
| line-4 | line-4-0660-0561-s002514 | station | forward | revenue | 1 |
| line-4 | line-4-0660-0561-s002514 | station | reverse | revenue | 1 |
| line-4 | line-4-0937-0536-s008777 | station | reverse | revenue | 2 |
| line-1 | line-1-0517-0336-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0517-0336-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0517-0336-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0863-0415-s000000 | depot | — | revenue | 21 |
| line-2 | line-2-0863-0415-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0863-0415-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0643-0792-s014803 | depot | — | revenue | 30 |
| line-3 | line-3-0643-0792-s014803 | depot | — | spare | 4 |
| line-3 | line-3-0643-0792-s014803 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0558-0540-s000000 | depot | — | revenue | 16 |
| line-4 | line-4-0558-0540-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0558-0540-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/homs-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **142 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **127 revenue, 11 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **102 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0517-0336-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0647-0540-s005380 | forward | revenue | 5 | pending |
| line-1 | line-1-0647-0540-s005380 | reverse | revenue | 5 | pending |
| line-1 | line-1-0660-0561-s005919 | forward | revenue | 5 | pending |
| line-1 | line-1-0660-0561-s005919 | reverse | revenue | 4 | pending |
| line-1 | line-1-0761-0719-s010103 | reverse | revenue | 4 | pending |
| line-1 | line-1-0660-0561-s005919 | reverse | spare | 1 | pending |
| line-1 | line-1-0761-0719-s010103 | reverse | spare | 1 | pending |
| line-1 | line-1-0517-0336-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0863-0415-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0734-0429-s003018 | forward | revenue | 3 | pending |
| line-2 | line-2-0734-0429-s003018 | reverse | revenue | 3 | pending |
| line-2 | line-2-0691-0483-s004630 | forward | revenue | 3 | pending |
| line-2 | line-2-0691-0483-s004630 | reverse | revenue | 3 | pending |
| line-2 | line-2-0647-0540-s006489 | forward | revenue | 3 | pending |
| line-2 | line-2-0647-0540-s006489 | reverse | revenue | 3 | pending |
| line-2 | line-2-0634-0549-s006922 | forward | revenue | 3 | pending |
| line-2 | line-2-0634-0549-s006922 | reverse | revenue | 3 | pending |
| line-2 | line-2-0614-0566-s007486 | forward | revenue | 3 | pending |
| line-2 | line-2-0614-0566-s007486 | reverse | revenue | 3 | pending |
| line-2 | line-2-0476-0688-s011760 | reverse | revenue | 2 | pending |
| line-2 | line-2-0476-0688-s011760 | reverse | spare | 1 | pending |
| line-2 | line-2-0863-0415-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0734-0429-s003018 | forward | spare | 1 | pending |
| line-2 | line-2-0734-0429-s003018 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0276-0370-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0473-0484-s005686 | forward | revenue | 5 | pending |
| line-3 | line-3-0473-0484-s005686 | reverse | revenue | 5 | pending |
| line-3 | line-3-0558-0540-s008269 | forward | revenue | 5 | pending |
| line-3 | line-3-0558-0540-s008269 | reverse | revenue | 5 | pending |
| line-3 | line-3-0613-0565-s009701 | forward | revenue | 5 | pending |
| line-3 | line-3-0613-0565-s009701 | reverse | revenue | 5 | pending |
| line-3 | line-3-0643-0792-s014803 | reverse | revenue | 5 | pending |
| line-3 | line-3-0276-0370-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0473-0484-s005686 | forward | spare | 1 | pending |
| line-3 | line-3-0473-0484-s005686 | reverse | spare | 1 | pending |
| line-3 | line-3-0558-0540-s008269 | forward | spare | 1 | pending |
| line-3 | line-3-0558-0540-s008269 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0558-0540-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0634-0549-s001895 | forward | revenue | 4 | pending |
| line-4 | line-4-0634-0549-s001895 | reverse | revenue | 4 | pending |
| line-4 | line-4-0660-0561-s002514 | forward | revenue | 4 | pending |
| line-4 | line-4-0660-0561-s002514 | reverse | revenue | 4 | pending |
| line-4 | line-4-0937-0536-s008777 | reverse | revenue | 4 | pending |
| line-4 | line-4-0558-0540-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0634-0549-s001895 | forward | spare | 1 | pending |
| line-4 | line-4-0634-0549-s001895 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**84 trainsets exceed the reference platform envelope**, requiring **4,998.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0517-0336-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0647-0540-s005380 | 10 | 4 | 6 | 357.0 |
| line-1-0660-0561-s005919 | 10 | 4 | 6 | 357.0 |
| line-1-0761-0719-s010103 | 5 | 2 | 3 | 178.5 |
| line-2-0476-0688-s011760 | 3 | 2 | 1 | 59.5 |
| line-2-0614-0566-s007486 | 6 | 4 | 2 | 119.0 |
| line-2-0634-0549-s006922 | 6 | 4 | 2 | 119.0 |
| line-2-0647-0540-s006489 | 6 | 4 | 2 | 119.0 |
| line-2-0691-0483-s004630 | 6 | 2 | 4 | 238.0 |
| line-2-0734-0429-s003018 | 8 | 2 | 6 | 357.0 |
| line-2-0863-0415-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0276-0370-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0473-0484-s005686 | 12 | 2 | 10 | 595.0 |
| line-3-0558-0540-s008269 | 12 | 4 | 8 | 476.0 |
| line-3-0613-0565-s009701 | 10 | 4 | 6 | 357.0 |
| line-3-0643-0792-s014803 | 5 | 2 | 3 | 178.5 |
| line-4-0558-0540-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0634-0549-s001895 | 10 | 4 | 6 | 357.0 |
| line-4-0660-0561-s002514 | 8 | 4 | 4 | 238.0 |
| line-4-0937-0536-s008777 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Homs/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
