# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 174 at depots = 218 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0216-0447-s000000 | line-1 | declared-depot | 34 | 2,023.0 | 7 |
| line-2-0674-0383-s000000 | line-2 | declared-depot | 53 | 3,153.5 | 10 |
| line-3-0085-0118-s022908 | line-3 | declared-depot | 60 | 3,570.0 | 10 |
| line-4-0641-0397-s000000 | line-4 | declared-depot | 27 | 1,606.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0216-0447-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0370-0519-s003805 | station | forward | revenue | 1 |
| line-1 | line-1-0370-0519-s003805 | station | reverse | revenue | 1 |
| line-1 | line-1-0436-0550-s005417 | station | forward | revenue | 1 |
| line-1 | line-1-0436-0550-s005417 | station | reverse | revenue | 1 |
| line-1 | line-1-0509-0585-s007165 | station | forward | revenue | 1 |
| line-1 | line-1-0509-0585-s007165 | station | reverse | revenue | 1 |
| line-1 | line-1-0684-0667-s011440 | station | forward | revenue | 1 |
| line-1 | line-1-0684-0667-s011440 | station | reverse | revenue | 1 |
| line-1 | line-1-0799-0721-s014281 | station | reverse | revenue | 2 |
| line-2 | line-2-0418-1069-s021577 | station | reverse | revenue | 2 |
| line-2 | line-2-0454-0858-s016219 | station | forward | revenue | 1 |
| line-2 | line-2-0454-0858-s016219 | station | reverse | revenue | 1 |
| line-2 | line-2-0509-0585-s006562 | station | forward | revenue | 1 |
| line-2 | line-2-0509-0585-s006562 | station | reverse | revenue | 1 |
| line-2 | line-2-0542-0801-s012727 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0801-s012727 | station | reverse | revenue | 1 |
| line-2 | line-2-0572-0488-s003665 | station | forward | revenue | 1 |
| line-2 | line-2-0572-0488-s003665 | station | reverse | revenue | 1 |
| line-2 | line-2-0641-0397-s000870 | station | forward | revenue | 1 |
| line-2 | line-2-0641-0397-s000870 | station | reverse | revenue | 1 |
| line-2 | line-2-0674-0383-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0085-0118-s022908 | station | reverse | revenue | 2 |
| line-3 | line-3-0474-0423-s012191 | station | forward | revenue | 1 |
| line-3 | line-3-0474-0423-s012191 | station | reverse | revenue | 1 |
| line-3 | line-3-0572-0488-s009552 | station | forward | revenue | 1 |
| line-3 | line-3-0572-0488-s009552 | station | reverse | revenue | 1 |
| line-3 | line-3-0798-0638-s003496 | station | forward | revenue | 1 |
| line-3 | line-3-0798-0638-s003496 | station | reverse | revenue | 1 |
| line-3 | line-3-0919-0713-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0463-0287-s006293 | station | forward | revenue | 1 |
| line-4 | line-4-0463-0287-s006293 | station | reverse | revenue | 1 |
| line-4 | line-4-0463-0463-s010880 | station | reverse | revenue | 2 |
| line-4 | line-4-0474-0423-s009973 | station | forward | revenue | 1 |
| line-4 | line-4-0474-0423-s009973 | station | reverse | revenue | 1 |
| line-4 | line-4-0641-0397-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0216-0447-s000000 | depot | — | revenue | 29 |
| line-1 | line-1-0216-0447-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0216-0447-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0674-0383-s000000 | depot | — | revenue | 46 |
| line-2 | line-2-0674-0383-s000000 | depot | — | spare | 6 |
| line-2 | line-2-0674-0383-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0085-0118-s022908 | depot | — | revenue | 53 |
| line-3 | line-3-0085-0118-s022908 | depot | — | spare | 6 |
| line-3 | line-3-0085-0118-s022908 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0641-0397-s000000 | depot | — | revenue | 23 |
| line-4 | line-4-0641-0397-s000000 | depot | — | spare | 3 |
| line-4 | line-4-0641-0397-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/arusha-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **218 trainsets at 22 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **195 revenue, 19 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **174 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0216-0447-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0370-0519-s003805 | forward | revenue | 4 | pending |
| line-1 | line-1-0370-0519-s003805 | reverse | revenue | 4 | pending |
| line-1 | line-1-0436-0550-s005417 | forward | revenue | 4 | pending |
| line-1 | line-1-0436-0550-s005417 | reverse | revenue | 4 | pending |
| line-1 | line-1-0509-0585-s007165 | forward | revenue | 4 | pending |
| line-1 | line-1-0509-0585-s007165 | reverse | revenue | 4 | pending |
| line-1 | line-1-0684-0667-s011440 | forward | revenue | 4 | pending |
| line-1 | line-1-0684-0667-s011440 | reverse | revenue | 4 | pending |
| line-1 | line-1-0799-0721-s014281 | reverse | revenue | 4 | pending |
| line-1 | line-1-0370-0519-s003805 | forward | spare | 1 | pending |
| line-1 | line-1-0370-0519-s003805 | reverse | spare | 1 | pending |
| line-1 | line-1-0436-0550-s005417 | forward | spare | 1 | pending |
| line-1 | line-1-0436-0550-s005417 | reverse | spare | 1 | pending |
| line-1 | line-1-0509-0585-s007165 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0674-0383-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0641-0397-s000870 | forward | revenue | 5 | pending |
| line-2 | line-2-0641-0397-s000870 | reverse | revenue | 5 | pending |
| line-2 | line-2-0572-0488-s003665 | forward | revenue | 5 | pending |
| line-2 | line-2-0572-0488-s003665 | reverse | revenue | 5 | pending |
| line-2 | line-2-0509-0585-s006562 | forward | revenue | 5 | pending |
| line-2 | line-2-0509-0585-s006562 | reverse | revenue | 5 | pending |
| line-2 | line-2-0542-0801-s012727 | forward | revenue | 5 | pending |
| line-2 | line-2-0542-0801-s012727 | reverse | revenue | 5 | pending |
| line-2 | line-2-0454-0858-s016219 | forward | revenue | 5 | pending |
| line-2 | line-2-0454-0858-s016219 | reverse | revenue | 5 | pending |
| line-2 | line-2-0418-1069-s021577 | reverse | revenue | 5 | pending |
| line-2 | line-2-0674-0383-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0641-0397-s000870 | forward | spare | 1 | pending |
| line-2 | line-2-0641-0397-s000870 | reverse | spare | 1 | pending |
| line-2 | line-2-0572-0488-s003665 | forward | spare | 1 | pending |
| line-2 | line-2-0572-0488-s003665 | reverse | spare | 1 | pending |
| line-2 | line-2-0509-0585-s006562 | forward | spare | 1 | pending |
| line-2 | line-2-0509-0585-s006562 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0919-0713-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0798-0638-s003496 | forward | revenue | 8 | pending |
| line-3 | line-3-0798-0638-s003496 | reverse | revenue | 8 | pending |
| line-3 | line-3-0572-0488-s009552 | forward | revenue | 8 | pending |
| line-3 | line-3-0572-0488-s009552 | reverse | revenue | 8 | pending |
| line-3 | line-3-0474-0423-s012191 | forward | revenue | 8 | pending |
| line-3 | line-3-0474-0423-s012191 | reverse | revenue | 8 | pending |
| line-3 | line-3-0085-0118-s022908 | reverse | revenue | 7 | pending |
| line-3 | line-3-0085-0118-s022908 | reverse | spare | 1 | pending |
| line-3 | line-3-0919-0713-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0798-0638-s003496 | forward | spare | 1 | pending |
| line-3 | line-3-0798-0638-s003496 | reverse | spare | 1 | pending |
| line-3 | line-3-0572-0488-s009552 | forward | spare | 1 | pending |
| line-3 | line-3-0572-0488-s009552 | reverse | spare | 1 | pending |
| line-3 | line-3-0474-0423-s012191 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0641-0397-s000000 | forward | revenue | 6 | pending |
| line-4 | line-4-0463-0287-s006293 | forward | revenue | 5 | pending |
| line-4 | line-4-0463-0287-s006293 | reverse | revenue | 5 | pending |
| line-4 | line-4-0474-0423-s009973 | forward | revenue | 5 | pending |
| line-4 | line-4-0474-0423-s009973 | reverse | revenue | 5 | pending |
| line-4 | line-4-0463-0463-s010880 | reverse | revenue | 5 | pending |
| line-4 | line-4-0463-0287-s006293 | forward | spare | 1 | pending |
| line-4 | line-4-0463-0287-s006293 | reverse | spare | 1 | pending |
| line-4 | line-4-0474-0423-s009973 | forward | spare | 1 | pending |
| line-4 | line-4-0474-0423-s009973 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**160 trainsets exceed the reference platform envelope**, requiring **9,520.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0216-0447-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0370-0519-s003805 | 10 | 2 | 8 | 476.0 |
| line-1-0436-0550-s005417 | 10 | 2 | 8 | 476.0 |
| line-1-0509-0585-s007165 | 9 | 4 | 5 | 297.5 |
| line-1-0684-0667-s011440 | 8 | 2 | 6 | 357.0 |
| line-1-0799-0721-s014281 | 4 | 2 | 2 | 119.0 |
| line-2-0418-1069-s021577 | 5 | 2 | 3 | 178.5 |
| line-2-0454-0858-s016219 | 10 | 2 | 8 | 476.0 |
| line-2-0509-0585-s006562 | 12 | 4 | 8 | 476.0 |
| line-2-0542-0801-s012727 | 10 | 2 | 8 | 476.0 |
| line-2-0572-0488-s003665 | 12 | 4 | 8 | 476.0 |
| line-2-0641-0397-s000870 | 12 | 4 | 8 | 476.0 |
| line-2-0674-0383-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0085-0118-s022908 | 8 | 2 | 6 | 357.0 |
| line-3-0474-0423-s012191 | 17 | 4 | 13 | 773.5 |
| line-3-0572-0488-s009552 | 18 | 4 | 14 | 833.0 |
| line-3-0798-0638-s003496 | 18 | 2 | 16 | 952.0 |
| line-3-0919-0713-s000000 | 9 | 2 | 7 | 416.5 |
| line-4-0463-0287-s006293 | 12 | 2 | 10 | 595.0 |
| line-4-0463-0463-s010880 | 5 | 2 | 3 | 178.5 |
| line-4-0474-0423-s009973 | 12 | 4 | 8 | 476.0 |
| line-4-0641-0397-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Arusha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
