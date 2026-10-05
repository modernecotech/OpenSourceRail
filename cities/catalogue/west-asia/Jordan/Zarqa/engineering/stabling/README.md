# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 160 at depots = 202 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1067-0037-s027658 | line-1 | declared-depot | 69 | 4,105.5 | 12 |
| line-2-1078-0047-s000000 | line-2 | declared-depot | 63 | 3,748.5 | 11 |
| line-3-0360-0400-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0400-1028-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0507-0771-s006518 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0771-s006518 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0660-s009532 | station | forward | revenue | 1 |
| line-1 | line-1-0583-0660-s009532 | station | reverse | revenue | 1 |
| line-1 | line-1-0632-0588-s011460 | station | forward | revenue | 1 |
| line-1 | line-1-0632-0588-s011460 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0476-s014470 | station | forward | revenue | 1 |
| line-1 | line-1-0708-0476-s014470 | station | reverse | revenue | 1 |
| line-1 | line-1-0784-0365-s017472 | station | forward | revenue | 1 |
| line-1 | line-1-0784-0365-s017472 | station | reverse | revenue | 1 |
| line-1 | line-1-0872-0234-s020997 | station | forward | revenue | 1 |
| line-1 | line-1-0872-0234-s020997 | station | reverse | revenue | 1 |
| line-1 | line-1-1067-0037-s027658 | station | reverse | revenue | 2 |
| line-2 | line-2-0192-0706-s025557 | station | reverse | revenue | 2 |
| line-2 | line-2-0340-0622-s021365 | station | forward | revenue | 1 |
| line-2 | line-2-0340-0622-s021365 | station | reverse | revenue | 1 |
| line-2 | line-2-0414-0564-s019264 | station | forward | revenue | 1 |
| line-2 | line-2-0414-0564-s019264 | station | reverse | revenue | 1 |
| line-2 | line-2-0488-0505-s017155 | station | forward | revenue | 1 |
| line-2 | line-2-0488-0505-s017155 | station | reverse | revenue | 1 |
| line-2 | line-2-0594-0421-s014128 | station | forward | revenue | 1 |
| line-2 | line-2-0594-0421-s014128 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0337-s011113 | station | forward | revenue | 1 |
| line-2 | line-2-0700-0337-s011113 | station | reverse | revenue | 1 |
| line-2 | line-2-0843-0224-s007012 | station | forward | revenue | 1 |
| line-2 | line-2-0843-0224-s007012 | station | reverse | revenue | 1 |
| line-2 | line-2-1078-0047-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0360-0400-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0427-0517-s003000 | station | forward | revenue | 1 |
| line-3 | line-3-0427-0517-s003000 | station | reverse | revenue | 1 |
| line-3 | line-3-0494-0634-s006001 | station | forward | revenue | 1 |
| line-3 | line-3-0494-0634-s006001 | station | reverse | revenue | 1 |
| line-3 | line-3-0561-0751-s009013 | station | forward | revenue | 1 |
| line-3 | line-3-0561-0751-s009013 | station | reverse | revenue | 1 |
| line-3 | line-3-0626-0864-s011905 | station | reverse | revenue | 2 |
| line-1 | line-1-1067-0037-s027658 | depot | — | revenue | 61 |
| line-1 | line-1-1067-0037-s027658 | depot | — | spare | 7 |
| line-1 | line-1-1067-0037-s027658 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1078-0047-s000000 | depot | — | revenue | 55 |
| line-2 | line-2-1078-0047-s000000 | depot | — | spare | 7 |
| line-2 | line-2-1078-0047-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0360-0400-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0360-0400-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0360-0400-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/zarqa-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **202 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **182 revenue, 17 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **160 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0400-1028-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0507-0771-s006518 | forward | revenue | 6 | pending |
| line-1 | line-1-0507-0771-s006518 | reverse | revenue | 6 | pending |
| line-1 | line-1-0583-0660-s009532 | forward | revenue | 6 | pending |
| line-1 | line-1-0583-0660-s009532 | reverse | revenue | 6 | pending |
| line-1 | line-1-0632-0588-s011460 | forward | revenue | 6 | pending |
| line-1 | line-1-0632-0588-s011460 | reverse | revenue | 6 | pending |
| line-1 | line-1-0708-0476-s014470 | forward | revenue | 5 | pending |
| line-1 | line-1-0708-0476-s014470 | reverse | revenue | 5 | pending |
| line-1 | line-1-0784-0365-s017472 | forward | revenue | 5 | pending |
| line-1 | line-1-0784-0365-s017472 | reverse | revenue | 5 | pending |
| line-1 | line-1-0872-0234-s020997 | forward | revenue | 5 | pending |
| line-1 | line-1-0872-0234-s020997 | reverse | revenue | 5 | pending |
| line-1 | line-1-1067-0037-s027658 | reverse | revenue | 5 | pending |
| line-1 | line-1-0708-0476-s014470 | forward | spare | 1 | pending |
| line-1 | line-1-0708-0476-s014470 | reverse | spare | 1 | pending |
| line-1 | line-1-0784-0365-s017472 | forward | spare | 1 | pending |
| line-1 | line-1-0784-0365-s017472 | reverse | spare | 1 | pending |
| line-1 | line-1-0872-0234-s020997 | forward | spare | 1 | pending |
| line-1 | line-1-0872-0234-s020997 | reverse | spare | 1 | pending |
| line-1 | line-1-1067-0037-s027658 | reverse | spare | 1 | pending |
| line-1 | line-1-0400-1028-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1078-0047-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0843-0224-s007012 | forward | revenue | 5 | pending |
| line-2 | line-2-0843-0224-s007012 | reverse | revenue | 5 | pending |
| line-2 | line-2-0700-0337-s011113 | forward | revenue | 5 | pending |
| line-2 | line-2-0700-0337-s011113 | reverse | revenue | 5 | pending |
| line-2 | line-2-0594-0421-s014128 | forward | revenue | 5 | pending |
| line-2 | line-2-0594-0421-s014128 | reverse | revenue | 5 | pending |
| line-2 | line-2-0488-0505-s017155 | forward | revenue | 5 | pending |
| line-2 | line-2-0488-0505-s017155 | reverse | revenue | 5 | pending |
| line-2 | line-2-0414-0564-s019264 | forward | revenue | 5 | pending |
| line-2 | line-2-0414-0564-s019264 | reverse | revenue | 5 | pending |
| line-2 | line-2-0340-0622-s021365 | forward | revenue | 5 | pending |
| line-2 | line-2-0340-0622-s021365 | reverse | revenue | 5 | pending |
| line-2 | line-2-0192-0706-s025557 | reverse | revenue | 5 | pending |
| line-2 | line-2-0843-0224-s007012 | forward | spare | 1 | pending |
| line-2 | line-2-0843-0224-s007012 | reverse | spare | 1 | pending |
| line-2 | line-2-0700-0337-s011113 | forward | spare | 1 | pending |
| line-2 | line-2-0700-0337-s011113 | reverse | spare | 1 | pending |
| line-2 | line-2-0594-0421-s014128 | forward | spare | 1 | pending |
| line-2 | line-2-0594-0421-s014128 | reverse | spare | 1 | pending |
| line-2 | line-2-0488-0505-s017155 | forward | spare | 1 | pending |
| line-2 | line-2-0488-0505-s017155 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0360-0400-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0427-0517-s003000 | forward | revenue | 5 | pending |
| line-3 | line-3-0427-0517-s003000 | reverse | revenue | 4 | pending |
| line-3 | line-3-0494-0634-s006001 | forward | revenue | 4 | pending |
| line-3 | line-3-0494-0634-s006001 | reverse | revenue | 4 | pending |
| line-3 | line-3-0561-0751-s009013 | forward | revenue | 4 | pending |
| line-3 | line-3-0561-0751-s009013 | reverse | revenue | 4 | pending |
| line-3 | line-3-0626-0864-s011905 | reverse | revenue | 4 | pending |
| line-3 | line-3-0427-0517-s003000 | reverse | spare | 1 | pending |
| line-3 | line-3-0494-0634-s006001 | forward | spare | 1 | pending |
| line-3 | line-3-0494-0634-s006001 | reverse | spare | 1 | pending |
| line-3 | line-3-0561-0751-s009013 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**156 trainsets exceed the reference platform envelope**, requiring **9,282.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0400-1028-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0507-0771-s006518 | 12 | 2 | 10 | 595.0 |
| line-1-0583-0660-s009532 | 12 | 2 | 10 | 595.0 |
| line-1-0632-0588-s011460 | 12 | 2 | 10 | 595.0 |
| line-1-0708-0476-s014470 | 12 | 2 | 10 | 595.0 |
| line-1-0784-0365-s017472 | 12 | 2 | 10 | 595.0 |
| line-1-0872-0234-s020997 | 12 | 4 | 8 | 476.0 |
| line-1-1067-0037-s027658 | 6 | 2 | 4 | 238.0 |
| line-2-0192-0706-s025557 | 5 | 2 | 3 | 178.5 |
| line-2-0340-0622-s021365 | 10 | 2 | 8 | 476.0 |
| line-2-0414-0564-s019264 | 10 | 2 | 8 | 476.0 |
| line-2-0488-0505-s017155 | 12 | 2 | 10 | 595.0 |
| line-2-0594-0421-s014128 | 12 | 2 | 10 | 595.0 |
| line-2-0700-0337-s011113 | 12 | 2 | 10 | 595.0 |
| line-2-0843-0224-s007012 | 12 | 4 | 8 | 476.0 |
| line-2-1078-0047-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0360-0400-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0427-0517-s003000 | 10 | 2 | 8 | 476.0 |
| line-3-0494-0634-s006001 | 10 | 2 | 8 | 476.0 |
| line-3-0561-0751-s009013 | 9 | 2 | 7 | 416.5 |
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
