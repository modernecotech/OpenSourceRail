# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 75 at depots = 105 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0517-0336-s000000 | line-1 | declared-depot | 22 | 1,309.0 | 5 |
| line-2-0863-0415-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0643-0792-s012511 | line-3 | declared-depot | 29 | 1,725.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0517-0336-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0589-0450-s003017 | station | forward | revenue | 1 |
| line-1 | line-1-0589-0450-s003017 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0540-s005380 | station | forward | revenue | 1 |
| line-1 | line-1-0647-0540-s005380 | station | reverse | revenue | 1 |
| line-1 | line-1-0704-0630-s007745 | station | forward | revenue | 1 |
| line-1 | line-1-0704-0630-s007745 | station | reverse | revenue | 1 |
| line-1 | line-1-0761-0719-s010103 | station | reverse | revenue | 2 |
| line-2 | line-2-0476-0688-s010669 | station | reverse | revenue | 2 |
| line-2 | line-2-0561-0628-s008332 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0628-s008332 | station | reverse | revenue | 1 |
| line-2 | line-2-0645-0569-s006011 | station | forward | revenue | 1 |
| line-2 | line-2-0645-0569-s006011 | station | reverse | revenue | 1 |
| line-2 | line-2-0754-0492-s003005 | station | forward | revenue | 1 |
| line-2 | line-2-0754-0492-s003005 | station | reverse | revenue | 1 |
| line-2 | line-2-0863-0415-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0276-0370-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0405-0518-s004404 | station | forward | revenue | 1 |
| line-3 | line-3-0405-0518-s004404 | station | reverse | revenue | 1 |
| line-3 | line-3-0484-0610-s007097 | station | forward | revenue | 1 |
| line-3 | line-3-0484-0610-s007097 | station | reverse | revenue | 1 |
| line-3 | line-3-0564-0701-s009814 | station | forward | revenue | 1 |
| line-3 | line-3-0564-0701-s009814 | station | reverse | revenue | 1 |
| line-3 | line-3-0643-0792-s012511 | station | reverse | revenue | 2 |
| line-1 | line-1-0517-0336-s000000 | depot | — | revenue | 19 |
| line-1 | line-1-0517-0336-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0517-0336-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0863-0415-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0863-0415-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0863-0415-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0643-0792-s012511 | depot | — | revenue | 25 |
| line-3 | line-3-0643-0792-s012511 | depot | — | spare | 3 |
| line-3 | line-3-0643-0792-s012511 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/homs-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **105 trainsets at 15 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **94 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **75 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0517-0336-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0589-0450-s003017 | forward | revenue | 4 | pending |
| line-1 | line-1-0589-0450-s003017 | reverse | revenue | 4 | pending |
| line-1 | line-1-0647-0540-s005380 | forward | revenue | 4 | pending |
| line-1 | line-1-0647-0540-s005380 | reverse | revenue | 4 | pending |
| line-1 | line-1-0704-0630-s007745 | forward | revenue | 3 | pending |
| line-1 | line-1-0704-0630-s007745 | reverse | revenue | 3 | pending |
| line-1 | line-1-0761-0719-s010103 | reverse | revenue | 3 | pending |
| line-1 | line-1-0704-0630-s007745 | forward | spare | 1 | pending |
| line-1 | line-1-0704-0630-s007745 | reverse | spare | 1 | pending |
| line-1 | line-1-0761-0719-s010103 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0863-0415-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0754-0492-s003005 | forward | revenue | 4 | pending |
| line-2 | line-2-0754-0492-s003005 | reverse | revenue | 4 | pending |
| line-2 | line-2-0645-0569-s006011 | forward | revenue | 4 | pending |
| line-2 | line-2-0645-0569-s006011 | reverse | revenue | 4 | pending |
| line-2 | line-2-0561-0628-s008332 | forward | revenue | 4 | pending |
| line-2 | line-2-0561-0628-s008332 | reverse | revenue | 3 | pending |
| line-2 | line-2-0476-0688-s010669 | reverse | revenue | 3 | pending |
| line-2 | line-2-0561-0628-s008332 | reverse | spare | 1 | pending |
| line-2 | line-2-0476-0688-s010669 | reverse | spare | 1 | pending |
| line-2 | line-2-0863-0415-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0754-0492-s003005 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0276-0370-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0405-0518-s004404 | forward | revenue | 5 | pending |
| line-3 | line-3-0405-0518-s004404 | reverse | revenue | 5 | pending |
| line-3 | line-3-0484-0610-s007097 | forward | revenue | 4 | pending |
| line-3 | line-3-0484-0610-s007097 | reverse | revenue | 4 | pending |
| line-3 | line-3-0564-0701-s009814 | forward | revenue | 4 | pending |
| line-3 | line-3-0564-0701-s009814 | reverse | revenue | 4 | pending |
| line-3 | line-3-0643-0792-s012511 | reverse | revenue | 4 | pending |
| line-3 | line-3-0484-0610-s007097 | forward | spare | 1 | pending |
| line-3 | line-3-0484-0610-s007097 | reverse | spare | 1 | pending |
| line-3 | line-3-0564-0701-s009814 | forward | spare | 1 | pending |
| line-3 | line-3-0564-0701-s009814 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**71 trainsets exceed the reference platform envelope**, requiring **4,224.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0517-0336-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0589-0450-s003017 | 8 | 2 | 6 | 357.0 |
| line-1-0647-0540-s005380 | 8 | 4 | 4 | 238.0 |
| line-1-0704-0630-s007745 | 8 | 2 | 6 | 357.0 |
| line-1-0761-0719-s010103 | 4 | 2 | 2 | 119.0 |
| line-2-0476-0688-s010669 | 4 | 2 | 2 | 119.0 |
| line-2-0561-0628-s008332 | 8 | 2 | 6 | 357.0 |
| line-2-0645-0569-s006011 | 8 | 4 | 4 | 238.0 |
| line-2-0754-0492-s003005 | 9 | 2 | 7 | 416.5 |
| line-2-0863-0415-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0276-0370-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0405-0518-s004404 | 10 | 2 | 8 | 476.0 |
| line-3-0484-0610-s007097 | 10 | 2 | 8 | 476.0 |
| line-3-0564-0701-s009814 | 10 | 2 | 8 | 476.0 |
| line-3-0643-0792-s012511 | 4 | 2 | 2 | 119.0 |

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
