# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 37 at depots = 71 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0240-0026-s000000 | line-1 | declared-depot | 15 | 735.0 | 4 |
| line-2-0425-0361-s000000 | line-2 | declared-depot | 8 | 392.0 | 3 |
| line-3-0289-0034-s013281 | line-3 | declared-depot | 14 | 686.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0575-s011615 | station | reverse | revenue | 2 |
| line-1 | line-1-0221-0409-s008245 | station | forward | revenue | 1 |
| line-1 | line-1-0221-0409-s008245 | station | reverse | revenue | 1 |
| line-1 | line-1-0224-0322-s006469 | station | forward | revenue | 1 |
| line-1 | line-1-0224-0322-s006469 | station | reverse | revenue | 1 |
| line-1 | line-1-0229-0151-s003007 | station | forward | revenue | 1 |
| line-1 | line-1-0229-0151-s003007 | station | reverse | revenue | 1 |
| line-1 | line-1-0240-0026-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0099-0457-s007550 | station | reverse | revenue | 2 |
| line-2 | line-2-0221-0409-s004489 | station | forward | revenue | 1 |
| line-2 | line-2-0221-0409-s004489 | station | reverse | revenue | 1 |
| line-2 | line-2-0288-0393-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0288-0393-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0357-0377-s001504 | station | forward | revenue | 1 |
| line-2 | line-2-0357-0377-s001504 | station | reverse | revenue | 1 |
| line-2 | line-2-0425-0361-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0255-0160-s009437 | station | forward | revenue | 1 |
| line-3 | line-3-0255-0160-s009437 | station | reverse | revenue | 1 |
| line-3 | line-3-0272-0297-s006023 | station | forward | revenue | 1 |
| line-3 | line-3-0272-0297-s006023 | station | reverse | revenue | 1 |
| line-3 | line-3-0288-0097-s011368 | station | forward | revenue | 1 |
| line-3 | line-3-0288-0097-s011368 | station | reverse | revenue | 1 |
| line-3 | line-3-0289-0034-s013281 | station | reverse | revenue | 2 |
| line-3 | line-3-0337-0296-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0337-0296-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0357-0377-s001216 | station | forward | revenue | 1 |
| line-3 | line-3-0357-0377-s001216 | station | reverse | revenue | 1 |
| line-3 | line-3-0371-0432-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0240-0026-s000000 | depot | — | revenue | 12 |
| line-1 | line-1-0240-0026-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0240-0026-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0425-0361-s000000 | depot | — | revenue | 6 |
| line-2 | line-2-0425-0361-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0425-0361-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0289-0034-s013281 | depot | — | revenue | 11 |
| line-3 | line-3-0289-0034-s013281 | depot | — | spare | 2 |
| line-3 | line-3-0289-0034-s013281 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/aqaba-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **71 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **63 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **37 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0240-0026-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0229-0151-s003007 | forward | revenue | 3 | pending |
| line-1 | line-1-0229-0151-s003007 | reverse | revenue | 3 | pending |
| line-1 | line-1-0224-0322-s006469 | forward | revenue | 3 | pending |
| line-1 | line-1-0224-0322-s006469 | reverse | revenue | 3 | pending |
| line-1 | line-1-0221-0409-s008245 | forward | revenue | 3 | pending |
| line-1 | line-1-0221-0409-s008245 | reverse | revenue | 2 | pending |
| line-1 | line-1-0215-0575-s011615 | reverse | revenue | 2 | pending |
| line-1 | line-1-0221-0409-s008245 | reverse | spare | 1 | pending |
| line-1 | line-1-0215-0575-s011615 | reverse | spare | 1 | pending |
| line-1 | line-1-0240-0026-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0425-0361-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0357-0377-s001504 | forward | revenue | 2 | pending |
| line-2 | line-2-0357-0377-s001504 | reverse | revenue | 2 | pending |
| line-2 | line-2-0288-0393-s003017 | forward | revenue | 2 | pending |
| line-2 | line-2-0288-0393-s003017 | reverse | revenue | 2 | pending |
| line-2 | line-2-0221-0409-s004489 | forward | revenue | 2 | pending |
| line-2 | line-2-0221-0409-s004489 | reverse | revenue | 2 | pending |
| line-2 | line-2-0099-0457-s007550 | reverse | revenue | 2 | pending |
| line-2 | line-2-0425-0361-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0357-0377-s001504 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0371-0432-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0357-0377-s001216 | forward | revenue | 2 | pending |
| line-3 | line-3-0357-0377-s001216 | reverse | revenue | 2 | pending |
| line-3 | line-3-0337-0296-s003002 | forward | revenue | 2 | pending |
| line-3 | line-3-0337-0296-s003002 | reverse | revenue | 2 | pending |
| line-3 | line-3-0272-0297-s006023 | forward | revenue | 2 | pending |
| line-3 | line-3-0272-0297-s006023 | reverse | revenue | 2 | pending |
| line-3 | line-3-0255-0160-s009437 | forward | revenue | 2 | pending |
| line-3 | line-3-0255-0160-s009437 | reverse | revenue | 2 | pending |
| line-3 | line-3-0288-0097-s011368 | forward | revenue | 2 | pending |
| line-3 | line-3-0288-0097-s011368 | reverse | revenue | 2 | pending |
| line-3 | line-3-0289-0034-s013281 | reverse | revenue | 2 | pending |
| line-3 | line-3-0357-0377-s001216 | forward | spare | 1 | pending |
| line-3 | line-3-0357-0377-s001216 | reverse | spare | 1 | pending |
| line-3 | line-3-0337-0296-s003002 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**25 trainsets exceed the reference platform envelope**, requiring **1,225.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0575-s011615 | 3 | 2 | 1 | 49.0 |
| line-1-0221-0409-s008245 | 6 | 4 | 2 | 98.0 |
| line-1-0224-0322-s006469 | 6 | 2 | 4 | 196.0 |
| line-1-0229-0151-s003007 | 6 | 4 | 2 | 98.0 |
| line-1-0240-0026-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0099-0457-s007550 | 2 | 2 | 0 | 0.0 |
| line-2-0221-0409-s004489 | 4 | 4 | 0 | 0.0 |
| line-2-0288-0393-s003017 | 4 | 2 | 2 | 98.0 |
| line-2-0357-0377-s001504 | 5 | 4 | 1 | 49.0 |
| line-2-0425-0361-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0255-0160-s009437 | 4 | 4 | 0 | 0.0 |
| line-3-0272-0297-s006023 | 4 | 2 | 2 | 98.0 |
| line-3-0288-0097-s011368 | 4 | 2 | 2 | 98.0 |
| line-3-0289-0034-s013281 | 2 | 2 | 0 | 0.0 |
| line-3-0337-0296-s003002 | 5 | 2 | 3 | 147.0 |
| line-3-0357-0377-s001216 | 6 | 4 | 2 | 98.0 |
| line-3-0371-0432-s000000 | 3 | 2 | 1 | 49.0 |

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
