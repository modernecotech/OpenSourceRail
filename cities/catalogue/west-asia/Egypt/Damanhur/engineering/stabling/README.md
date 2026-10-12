# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 142 at depots = 190 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0370-0539-s000000 | line-1 | declared-depot | 20 | 1,190.0 | 5 |
| line-2-0647-1100-s000000 | line-2 | declared-depot | 40 | 2,380.0 | 8 |
| line-3-0354-0950-s021698 | line-3 | declared-depot | 52 | 3,094.0 | 10 |
| line-4-0435-0518-s000000 | line-4 | declared-depot | 19 | 1,130.5 | 4 |
| line-5-0611-0500-s000000 | line-5 | declared-depot | 11 | 654.5 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0370-0539-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0435-0518-s001824 | station | forward | revenue | 1 |
| line-1 | line-1-0435-0518-s001824 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0551-s005031 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0551-s005031 | station | reverse | revenue | 1 |
| line-1 | line-1-0573-0560-s005649 | station | forward | revenue | 1 |
| line-1 | line-1-0573-0560-s005649 | station | reverse | revenue | 1 |
| line-1 | line-1-0654-0592-s007534 | station | forward | revenue | 1 |
| line-1 | line-1-0654-0592-s007534 | station | reverse | revenue | 1 |
| line-1 | line-1-0731-0566-s009405 | station | reverse | revenue | 2 |
| line-2 | line-2-0526-0378-s016176 | station | reverse | revenue | 2 |
| line-2 | line-2-0568-0542-s012548 | station | forward | revenue | 1 |
| line-2 | line-2-0568-0542-s012548 | station | reverse | revenue | 1 |
| line-2 | line-2-0573-0560-s012146 | station | forward | revenue | 1 |
| line-2 | line-2-0573-0560-s012146 | station | reverse | revenue | 1 |
| line-2 | line-2-0598-0656-s010019 | station | forward | revenue | 1 |
| line-2 | line-2-0598-0656-s010019 | station | reverse | revenue | 1 |
| line-2 | line-2-0633-0792-s007009 | station | forward | revenue | 1 |
| line-2 | line-2-0633-0792-s007009 | station | reverse | revenue | 1 |
| line-2 | line-2-0647-1100-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0950-s021698 | station | reverse | revenue | 2 |
| line-3 | line-3-0474-0784-s016845 | station | forward | revenue | 1 |
| line-3 | line-3-0474-0784-s016845 | station | reverse | revenue | 1 |
| line-3 | line-3-0527-0611-s011980 | station | forward | revenue | 1 |
| line-3 | line-3-0527-0611-s011980 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0551-s009678 | station | forward | revenue | 1 |
| line-3 | line-3-0549-0551-s009678 | station | reverse | revenue | 1 |
| line-3 | line-3-0568-0542-s009188 | station | forward | revenue | 1 |
| line-3 | line-3-0568-0542-s009188 | station | reverse | revenue | 1 |
| line-3 | line-3-0611-0500-s007957 | station | forward | revenue | 1 |
| line-3 | line-3-0611-0500-s007957 | station | reverse | revenue | 1 |
| line-3 | line-3-0643-0354-s003985 | station | forward | revenue | 1 |
| line-3 | line-3-0643-0354-s003985 | station | reverse | revenue | 1 |
| line-3 | line-3-0740-0226-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0241-0290-s006655 | station | reverse | revenue | 2 |
| line-4 | line-4-0435-0518-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0611-0500-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0811-0514-s004315 | station | reverse | revenue | 2 |
| line-1 | line-1-0370-0539-s000000 | depot | — | revenue | 17 |
| line-1 | line-1-0370-0539-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0370-0539-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0647-1100-s000000 | depot | — | revenue | 35 |
| line-2 | line-2-0647-1100-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0647-1100-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0950-s021698 | depot | — | revenue | 45 |
| line-3 | line-3-0354-0950-s021698 | depot | — | spare | 6 |
| line-3 | line-3-0354-0950-s021698 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0435-0518-s000000 | depot | — | revenue | 16 |
| line-4 | line-4-0435-0518-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0435-0518-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0611-0500-s000000 | depot | — | revenue | 9 |
| line-5 | line-5-0611-0500-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0611-0500-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/damanhur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **190 trainsets at 24 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **170 revenue, 15 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **142 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0370-0539-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0435-0518-s001824 | forward | revenue | 3 | pending |
| line-1 | line-1-0435-0518-s001824 | reverse | revenue | 3 | pending |
| line-1 | line-1-0547-0551-s005031 | forward | revenue | 3 | pending |
| line-1 | line-1-0547-0551-s005031 | reverse | revenue | 3 | pending |
| line-1 | line-1-0573-0560-s005649 | forward | revenue | 3 | pending |
| line-1 | line-1-0573-0560-s005649 | reverse | revenue | 3 | pending |
| line-1 | line-1-0654-0592-s007534 | forward | revenue | 3 | pending |
| line-1 | line-1-0654-0592-s007534 | reverse | revenue | 3 | pending |
| line-1 | line-1-0731-0566-s009405 | reverse | revenue | 2 | pending |
| line-1 | line-1-0731-0566-s009405 | reverse | spare | 1 | pending |
| line-1 | line-1-0370-0539-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0435-0518-s001824 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0633-0792-s007009 | forward | revenue | 5 | pending |
| line-2 | line-2-0633-0792-s007009 | reverse | revenue | 5 | pending |
| line-2 | line-2-0598-0656-s010019 | forward | revenue | 5 | pending |
| line-2 | line-2-0598-0656-s010019 | reverse | revenue | 5 | pending |
| line-2 | line-2-0573-0560-s012146 | forward | revenue | 5 | pending |
| line-2 | line-2-0573-0560-s012146 | reverse | revenue | 5 | pending |
| line-2 | line-2-0568-0542-s012548 | forward | revenue | 4 | pending |
| line-2 | line-2-0568-0542-s012548 | reverse | revenue | 4 | pending |
| line-2 | line-2-0526-0378-s016176 | reverse | revenue | 4 | pending |
| line-2 | line-2-0568-0542-s012548 | forward | spare | 1 | pending |
| line-2 | line-2-0568-0542-s012548 | reverse | spare | 1 | pending |
| line-2 | line-2-0526-0378-s016176 | reverse | spare | 1 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0633-0792-s007009 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0740-0226-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0643-0354-s003985 | forward | revenue | 5 | pending |
| line-3 | line-3-0643-0354-s003985 | reverse | revenue | 5 | pending |
| line-3 | line-3-0611-0500-s007957 | forward | revenue | 5 | pending |
| line-3 | line-3-0611-0500-s007957 | reverse | revenue | 5 | pending |
| line-3 | line-3-0568-0542-s009188 | forward | revenue | 4 | pending |
| line-3 | line-3-0568-0542-s009188 | reverse | revenue | 4 | pending |
| line-3 | line-3-0549-0551-s009678 | forward | revenue | 4 | pending |
| line-3 | line-3-0549-0551-s009678 | reverse | revenue | 4 | pending |
| line-3 | line-3-0527-0611-s011980 | forward | revenue | 4 | pending |
| line-3 | line-3-0527-0611-s011980 | reverse | revenue | 4 | pending |
| line-3 | line-3-0474-0784-s016845 | forward | revenue | 4 | pending |
| line-3 | line-3-0474-0784-s016845 | reverse | revenue | 4 | pending |
| line-3 | line-3-0354-0950-s021698 | reverse | revenue | 4 | pending |
| line-3 | line-3-0568-0542-s009188 | forward | spare | 1 | pending |
| line-3 | line-3-0568-0542-s009188 | reverse | spare | 1 | pending |
| line-3 | line-3-0549-0551-s009678 | forward | spare | 1 | pending |
| line-3 | line-3-0549-0551-s009678 | reverse | spare | 1 | pending |
| line-3 | line-3-0527-0611-s011980 | forward | spare | 1 | pending |
| line-3 | line-3-0527-0611-s011980 | reverse | spare | 1 | pending |
| line-3 | line-3-0474-0784-s016845 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0435-0518-s000000 | forward | revenue | 10 | pending |
| line-4 | line-4-0241-0290-s006655 | reverse | revenue | 10 | pending |
| line-4 | line-4-0435-0518-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0241-0290-s006655 | reverse | spare | 1 | pending |
| line-4 | line-4-0435-0518-s000000 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0611-0500-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0811-0514-s004315 | reverse | revenue | 6 | pending |
| line-5 | line-5-0811-0514-s004315 | reverse | spare | 1 | pending |
| line-5 | line-5-0611-0500-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**126 trainsets exceed the reference platform envelope**, requiring **7,497.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0370-0539-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0435-0518-s001824 | 7 | 4 | 3 | 178.5 |
| line-1-0547-0551-s005031 | 6 | 4 | 2 | 119.0 |
| line-1-0573-0560-s005649 | 6 | 4 | 2 | 119.0 |
| line-1-0654-0592-s007534 | 6 | 2 | 4 | 238.0 |
| line-1-0731-0566-s009405 | 3 | 2 | 1 | 59.5 |
| line-2-0526-0378-s016176 | 5 | 2 | 3 | 178.5 |
| line-2-0568-0542-s012548 | 10 | 4 | 6 | 357.0 |
| line-2-0573-0560-s012146 | 10 | 4 | 6 | 357.0 |
| line-2-0598-0656-s010019 | 10 | 2 | 8 | 476.0 |
| line-2-0633-0792-s007009 | 11 | 2 | 9 | 535.5 |
| line-2-0647-1100-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0354-0950-s021698 | 4 | 2 | 2 | 119.0 |
| line-3-0474-0784-s016845 | 9 | 2 | 7 | 416.5 |
| line-3-0527-0611-s011980 | 10 | 2 | 8 | 476.0 |
| line-3-0549-0551-s009678 | 10 | 4 | 6 | 357.0 |
| line-3-0568-0542-s009188 | 10 | 4 | 6 | 357.0 |
| line-3-0611-0500-s007957 | 10 | 4 | 6 | 357.0 |
| line-3-0643-0354-s003985 | 10 | 2 | 8 | 476.0 |
| line-3-0740-0226-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0241-0290-s006655 | 11 | 2 | 9 | 535.5 |
| line-4-0435-0518-s000000 | 12 | 2 | 10 | 595.0 |
| line-5-0611-0500-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0811-0514-s004315 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damanhur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
