# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 157 at depots = 205 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1067-0037-s028370 | line-1 | declared-depot | 67 | 3,986.5 | 12 |
| line-2-1078-0047-s000000 | line-2 | declared-depot | 62 | 3,689.0 | 11 |
| line-3-0360-0400-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0400-1028-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0507-0771-s006806 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0771-s006806 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0719-s008221 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0719-s008221 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0660-s009820 | station | forward | revenue | 1 |
| line-1 | line-1-0583-0660-s009820 | station | reverse | revenue | 1 |
| line-1 | line-1-0632-0588-s011748 | station | forward | revenue | 1 |
| line-1 | line-1-0632-0588-s011748 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0476-s014758 | station | forward | revenue | 1 |
| line-1 | line-1-0708-0476-s014758 | station | reverse | revenue | 1 |
| line-1 | line-1-0784-0365-s017760 | station | forward | revenue | 1 |
| line-1 | line-1-0784-0365-s017760 | station | reverse | revenue | 1 |
| line-1 | line-1-0872-0235-s021265 | station | forward | revenue | 1 |
| line-1 | line-1-0872-0235-s021265 | station | reverse | revenue | 1 |
| line-1 | line-1-1067-0037-s028370 | station | reverse | revenue | 2 |
| line-1 | line-1-1069-0041-s028257 | station | forward | revenue | 1 |
| line-1 | line-1-1069-0041-s028257 | station | reverse | revenue | 1 |
| line-2 | line-2-0192-0706-s026550 | station | reverse | revenue | 2 |
| line-2 | line-2-0317-0641-s022988 | station | forward | revenue | 1 |
| line-2 | line-2-0317-0641-s022988 | station | reverse | revenue | 1 |
| line-2 | line-2-0442-0542-s019416 | station | forward | revenue | 1 |
| line-2 | line-2-0442-0542-s019416 | station | reverse | revenue | 1 |
| line-2 | line-2-0488-0505-s018102 | station | forward | revenue | 1 |
| line-2 | line-2-0488-0505-s018102 | station | reverse | revenue | 1 |
| line-2 | line-2-0594-0421-s015075 | station | forward | revenue | 1 |
| line-2 | line-2-0594-0421-s015075 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0337-s012060 | station | forward | revenue | 1 |
| line-2 | line-2-0700-0337-s012060 | station | reverse | revenue | 1 |
| line-2 | line-2-1066-0038-s000350 | station | forward | revenue | 1 |
| line-2 | line-2-1066-0038-s000350 | station | reverse | revenue | 1 |
| line-2 | line-2-1069-0041-s000253 | station | forward | revenue | 1 |
| line-2 | line-2-1069-0041-s000253 | station | reverse | revenue | 1 |
| line-2 | line-2-1078-0047-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0360-0400-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0442-0542-s003622 | station | forward | revenue | 1 |
| line-3 | line-3-0442-0542-s003622 | station | reverse | revenue | 1 |
| line-3 | line-3-0494-0634-s006001 | station | forward | revenue | 1 |
| line-3 | line-3-0494-0634-s006001 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0719-s008186 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0719-s008186 | station | reverse | revenue | 1 |
| line-3 | line-3-0626-0864-s011905 | station | reverse | revenue | 2 |
| line-1 | line-1-1067-0037-s028370 | depot | — | revenue | 59 |
| line-1 | line-1-1067-0037-s028370 | depot | — | spare | 7 |
| line-1 | line-1-1067-0037-s028370 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1078-0047-s000000 | depot | — | revenue | 54 |
| line-2 | line-2-1078-0047-s000000 | depot | — | spare | 7 |
| line-2 | line-2-1078-0047-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0360-0400-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0360-0400-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0360-0400-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/zarqa-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **205 trainsets at 24 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **185 revenue, 17 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **157 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0400-1028-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0507-0771-s006806 | forward | revenue | 5 | pending |
| line-1 | line-1-0507-0771-s006806 | reverse | revenue | 5 | pending |
| line-1 | line-1-0543-0719-s008221 | forward | revenue | 5 | pending |
| line-1 | line-1-0543-0719-s008221 | reverse | revenue | 5 | pending |
| line-1 | line-1-0583-0660-s009820 | forward | revenue | 5 | pending |
| line-1 | line-1-0583-0660-s009820 | reverse | revenue | 5 | pending |
| line-1 | line-1-0632-0588-s011748 | forward | revenue | 4 | pending |
| line-1 | line-1-0632-0588-s011748 | reverse | revenue | 4 | pending |
| line-1 | line-1-0708-0476-s014758 | forward | revenue | 4 | pending |
| line-1 | line-1-0708-0476-s014758 | reverse | revenue | 4 | pending |
| line-1 | line-1-0784-0365-s017760 | forward | revenue | 4 | pending |
| line-1 | line-1-0784-0365-s017760 | reverse | revenue | 4 | pending |
| line-1 | line-1-0872-0235-s021265 | forward | revenue | 4 | pending |
| line-1 | line-1-0872-0235-s021265 | reverse | revenue | 4 | pending |
| line-1 | line-1-1069-0041-s028257 | forward | revenue | 4 | pending |
| line-1 | line-1-1069-0041-s028257 | reverse | revenue | 4 | pending |
| line-1 | line-1-1067-0037-s028370 | reverse | revenue | 4 | pending |
| line-1 | line-1-0632-0588-s011748 | forward | spare | 1 | pending |
| line-1 | line-1-0632-0588-s011748 | reverse | spare | 1 | pending |
| line-1 | line-1-0708-0476-s014758 | forward | spare | 1 | pending |
| line-1 | line-1-0708-0476-s014758 | reverse | spare | 1 | pending |
| line-1 | line-1-0784-0365-s017760 | forward | spare | 1 | pending |
| line-1 | line-1-0784-0365-s017760 | reverse | spare | 1 | pending |
| line-1 | line-1-0872-0235-s021265 | forward | spare | 1 | pending |
| line-1 | line-1-0872-0235-s021265 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1078-0047-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-1069-0041-s000253 | forward | revenue | 5 | pending |
| line-2 | line-2-1069-0041-s000253 | reverse | revenue | 5 | pending |
| line-2 | line-2-1066-0038-s000350 | forward | revenue | 5 | pending |
| line-2 | line-2-1066-0038-s000350 | reverse | revenue | 5 | pending |
| line-2 | line-2-0700-0337-s012060 | forward | revenue | 5 | pending |
| line-2 | line-2-0700-0337-s012060 | reverse | revenue | 5 | pending |
| line-2 | line-2-0594-0421-s015075 | forward | revenue | 5 | pending |
| line-2 | line-2-0594-0421-s015075 | reverse | revenue | 4 | pending |
| line-2 | line-2-0488-0505-s018102 | forward | revenue | 4 | pending |
| line-2 | line-2-0488-0505-s018102 | reverse | revenue | 4 | pending |
| line-2 | line-2-0442-0542-s019416 | forward | revenue | 4 | pending |
| line-2 | line-2-0442-0542-s019416 | reverse | revenue | 4 | pending |
| line-2 | line-2-0317-0641-s022988 | forward | revenue | 4 | pending |
| line-2 | line-2-0317-0641-s022988 | reverse | revenue | 4 | pending |
| line-2 | line-2-0192-0706-s026550 | reverse | revenue | 4 | pending |
| line-2 | line-2-0594-0421-s015075 | reverse | spare | 1 | pending |
| line-2 | line-2-0488-0505-s018102 | forward | spare | 1 | pending |
| line-2 | line-2-0488-0505-s018102 | reverse | spare | 1 | pending |
| line-2 | line-2-0442-0542-s019416 | forward | spare | 1 | pending |
| line-2 | line-2-0442-0542-s019416 | reverse | spare | 1 | pending |
| line-2 | line-2-0317-0641-s022988 | forward | spare | 1 | pending |
| line-2 | line-2-0317-0641-s022988 | reverse | spare | 1 | pending |
| line-2 | line-2-0192-0706-s026550 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0360-0400-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0442-0542-s003622 | forward | revenue | 5 | pending |
| line-3 | line-3-0442-0542-s003622 | reverse | revenue | 4 | pending |
| line-3 | line-3-0494-0634-s006001 | forward | revenue | 4 | pending |
| line-3 | line-3-0494-0634-s006001 | reverse | revenue | 4 | pending |
| line-3 | line-3-0543-0719-s008186 | forward | revenue | 4 | pending |
| line-3 | line-3-0543-0719-s008186 | reverse | revenue | 4 | pending |
| line-3 | line-3-0626-0864-s011905 | reverse | revenue | 4 | pending |
| line-3 | line-3-0442-0542-s003622 | reverse | spare | 1 | pending |
| line-3 | line-3-0494-0634-s006001 | forward | spare | 1 | pending |
| line-3 | line-3-0494-0634-s006001 | reverse | spare | 1 | pending |
| line-3 | line-3-0543-0719-s008186 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**143 trainsets exceed the reference platform envelope**, requiring **8,508.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0400-1028-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0507-0771-s006806 | 10 | 2 | 8 | 476.0 |
| line-1-0543-0719-s008221 | 10 | 4 | 6 | 357.0 |
| line-1-0583-0660-s009820 | 10 | 2 | 8 | 476.0 |
| line-1-0632-0588-s011748 | 10 | 2 | 8 | 476.0 |
| line-1-0708-0476-s014758 | 10 | 2 | 8 | 476.0 |
| line-1-0784-0365-s017760 | 10 | 2 | 8 | 476.0 |
| line-1-0872-0235-s021265 | 10 | 2 | 8 | 476.0 |
| line-1-1067-0037-s028370 | 4 | 2 | 2 | 119.0 |
| line-1-1069-0041-s028257 | 8 | 4 | 4 | 238.0 |
| line-2-0192-0706-s026550 | 5 | 2 | 3 | 178.5 |
| line-2-0317-0641-s022988 | 10 | 2 | 8 | 476.0 |
| line-2-0442-0542-s019416 | 10 | 4 | 6 | 357.0 |
| line-2-0488-0505-s018102 | 10 | 2 | 8 | 476.0 |
| line-2-0594-0421-s015075 | 10 | 2 | 8 | 476.0 |
| line-2-0700-0337-s012060 | 10 | 2 | 8 | 476.0 |
| line-2-1066-0038-s000350 | 10 | 4 | 6 | 357.0 |
| line-2-1069-0041-s000253 | 10 | 4 | 6 | 357.0 |
| line-2-1078-0047-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0360-0400-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0442-0542-s003622 | 10 | 4 | 6 | 357.0 |
| line-3-0494-0634-s006001 | 10 | 2 | 8 | 476.0 |
| line-3-0543-0719-s008186 | 9 | 4 | 5 | 297.5 |
| line-3-0626-0864-s011905 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Zarqa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
