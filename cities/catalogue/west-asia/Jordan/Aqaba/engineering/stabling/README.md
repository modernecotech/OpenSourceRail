# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 50 at depots = 84 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0215-0575-s014978 | line-1 | declared-depot | 18 | 882.0 | 5 |
| line-2-0425-0361-s000000 | line-2 | declared-depot | 9 | 441.0 | 3 |
| line-3-0371-0432-s000000 | line-3 | declared-depot | 15 | 735.0 | 4 |
| line-4-0228-0522-s000000 | line-4 | declared-depot | 8 | 392.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0575-s014978 | station | reverse | revenue | 2 |
| line-1 | line-1-0228-0522-s013488 | station | forward | revenue | 1 |
| line-1 | line-1-0228-0522-s013488 | station | reverse | revenue | 1 |
| line-1 | line-1-0237-0149-s003017 | station | forward | revenue | 1 |
| line-1 | line-1-0237-0149-s003017 | station | reverse | revenue | 1 |
| line-1 | line-1-0240-0026-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0306-0271-s006029 | station | forward | revenue | 1 |
| line-1 | line-1-0306-0271-s006029 | station | reverse | revenue | 1 |
| line-1 | line-1-0332-0383-s009750 | station | forward | revenue | 1 |
| line-1 | line-1-0332-0383-s009750 | station | reverse | revenue | 1 |
| line-2 | line-2-0099-0457-s007550 | station | reverse | revenue | 2 |
| line-2 | line-2-0332-0383-s002054 | station | forward | revenue | 1 |
| line-2 | line-2-0332-0383-s002054 | station | reverse | revenue | 1 |
| line-2 | line-2-0372-0374-s001179 | station | forward | revenue | 1 |
| line-2 | line-2-0372-0374-s001179 | station | reverse | revenue | 1 |
| line-2 | line-2-0425-0361-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0252-0149-s007621 | station | forward | revenue | 1 |
| line-3 | line-3-0252-0149-s007621 | station | reverse | revenue | 1 |
| line-3 | line-3-0289-0034-s011221 | station | reverse | revenue | 2 |
| line-3 | line-3-0326-0253-s004659 | station | forward | revenue | 1 |
| line-3 | line-3-0326-0253-s004659 | station | reverse | revenue | 1 |
| line-3 | line-3-0371-0432-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0372-0374-s001518 | station | forward | revenue | 1 |
| line-3 | line-3-0372-0374-s001518 | station | reverse | revenue | 1 |
| line-4 | line-4-0037-0638-s005489 | station | reverse | revenue | 2 |
| line-4 | line-4-0228-0522-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0215-0575-s014978 | depot | — | revenue | 15 |
| line-1 | line-1-0215-0575-s014978 | depot | — | spare | 2 |
| line-1 | line-1-0215-0575-s014978 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0425-0361-s000000 | depot | — | revenue | 7 |
| line-2 | line-2-0425-0361-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0425-0361-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0371-0432-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0371-0432-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0371-0432-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0228-0522-s000000 | depot | — | revenue | 6 |
| line-4 | line-4-0228-0522-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0228-0522-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/aqaba-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **84 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **74 revenue, 6 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **50 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0240-0026-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0237-0149-s003017 | forward | revenue | 3 | pending |
| line-1 | line-1-0237-0149-s003017 | reverse | revenue | 3 | pending |
| line-1 | line-1-0306-0271-s006029 | forward | revenue | 3 | pending |
| line-1 | line-1-0306-0271-s006029 | reverse | revenue | 3 | pending |
| line-1 | line-1-0332-0383-s009750 | forward | revenue | 3 | pending |
| line-1 | line-1-0332-0383-s009750 | reverse | revenue | 3 | pending |
| line-1 | line-1-0228-0522-s013488 | forward | revenue | 2 | pending |
| line-1 | line-1-0228-0522-s013488 | reverse | revenue | 2 | pending |
| line-1 | line-1-0215-0575-s014978 | reverse | revenue | 2 | pending |
| line-1 | line-1-0228-0522-s013488 | forward | spare | 1 | pending |
| line-1 | line-1-0228-0522-s013488 | reverse | spare | 1 | pending |
| line-1 | line-1-0215-0575-s014978 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0425-0361-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0372-0374-s001179 | forward | revenue | 3 | pending |
| line-2 | line-2-0372-0374-s001179 | reverse | revenue | 3 | pending |
| line-2 | line-2-0332-0383-s002054 | forward | revenue | 2 | pending |
| line-2 | line-2-0332-0383-s002054 | reverse | revenue | 2 | pending |
| line-2 | line-2-0099-0457-s007550 | reverse | revenue | 2 | pending |
| line-2 | line-2-0332-0383-s002054 | forward | spare | 1 | pending |
| line-2 | line-2-0332-0383-s002054 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0371-0432-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0372-0374-s001518 | forward | revenue | 3 | pending |
| line-3 | line-3-0372-0374-s001518 | reverse | revenue | 3 | pending |
| line-3 | line-3-0326-0253-s004659 | forward | revenue | 3 | pending |
| line-3 | line-3-0326-0253-s004659 | reverse | revenue | 3 | pending |
| line-3 | line-3-0252-0149-s007621 | forward | revenue | 3 | pending |
| line-3 | line-3-0252-0149-s007621 | reverse | revenue | 2 | pending |
| line-3 | line-3-0289-0034-s011221 | reverse | revenue | 2 | pending |
| line-3 | line-3-0252-0149-s007621 | reverse | spare | 1 | pending |
| line-3 | line-3-0289-0034-s011221 | reverse | spare | 1 | pending |
| line-3 | line-3-0371-0432-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0228-0522-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0037-0638-s005489 | reverse | revenue | 5 | pending |
| line-4 | line-4-0228-0522-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0037-0638-s005489 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**32 trainsets exceed the reference platform envelope**, requiring **1,568.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0575-s014978 | 3 | 2 | 1 | 49.0 |
| line-1-0228-0522-s013488 | 6 | 4 | 2 | 98.0 |
| line-1-0237-0149-s003017 | 6 | 4 | 2 | 98.0 |
| line-1-0240-0026-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0306-0271-s006029 | 6 | 4 | 2 | 98.0 |
| line-1-0332-0383-s009750 | 6 | 4 | 2 | 98.0 |
| line-2-0099-0457-s007550 | 2 | 2 | 0 | 0.0 |
| line-2-0332-0383-s002054 | 6 | 4 | 2 | 98.0 |
| line-2-0372-0374-s001179 | 6 | 4 | 2 | 98.0 |
| line-2-0425-0361-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0252-0149-s007621 | 6 | 4 | 2 | 98.0 |
| line-3-0289-0034-s011221 | 3 | 2 | 1 | 49.0 |
| line-3-0326-0253-s004659 | 6 | 4 | 2 | 98.0 |
| line-3-0371-0432-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0372-0374-s001518 | 6 | 4 | 2 | 98.0 |
| line-4-0037-0638-s005489 | 6 | 2 | 4 | 196.0 |
| line-4-0228-0522-s000000 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Aqaba/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
