# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 33 at depots = 63 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0215-0575-s011615 | line-1 | declared-depot | 15 | 735.0 | 4 |
| line-2-0425-0361-s000000 | line-2 | declared-depot | 8 | 392.0 | 3 |
| line-3-0371-0432-s000000 | line-3 | declared-depot | 10 | 490.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0575-s011615 | station | reverse | revenue | 2 |
| line-1 | line-1-0219-0448-s009042 | station | forward | revenue | 1 |
| line-1 | line-1-0219-0448-s009042 | station | reverse | revenue | 1 |
| line-1 | line-1-0224-0322-s006469 | station | forward | revenue | 1 |
| line-1 | line-1-0224-0322-s006469 | station | reverse | revenue | 1 |
| line-1 | line-1-0229-0151-s003007 | station | forward | revenue | 1 |
| line-1 | line-1-0229-0151-s003007 | station | reverse | revenue | 1 |
| line-1 | line-1-0240-0026-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0099-0457-s007550 | station | reverse | revenue | 2 |
| line-2 | line-2-0185-0417-s005276 | station | forward | revenue | 1 |
| line-2 | line-2-0185-0417-s005276 | station | reverse | revenue | 1 |
| line-2 | line-2-0288-0393-s003017 | station | forward | revenue | 1 |
| line-2 | line-2-0288-0393-s003017 | station | reverse | revenue | 1 |
| line-2 | line-2-0364-0375-s001348 | station | forward | revenue | 1 |
| line-2 | line-2-0364-0375-s001348 | station | reverse | revenue | 1 |
| line-2 | line-2-0425-0361-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0289-0034-s009300 | station | reverse | revenue | 2 |
| line-3 | line-3-0298-0136-s006525 | station | forward | revenue | 1 |
| line-3 | line-3-0298-0136-s006525 | station | reverse | revenue | 1 |
| line-3 | line-3-0337-0296-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0337-0296-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0353-0357-s001649 | station | forward | revenue | 1 |
| line-3 | line-3-0353-0357-s001649 | station | reverse | revenue | 1 |
| line-3 | line-3-0371-0432-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0215-0575-s011615 | depot | — | revenue | 12 |
| line-1 | line-1-0215-0575-s011615 | depot | — | spare | 2 |
| line-1 | line-1-0215-0575-s011615 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0425-0361-s000000 | depot | — | revenue | 6 |
| line-2 | line-2-0425-0361-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0425-0361-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0371-0432-s000000 | depot | — | revenue | 8 |
| line-3 | line-3-0371-0432-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0371-0432-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/aqaba-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **63 trainsets at 15 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **56 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **33 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0240-0026-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0229-0151-s003007 | forward | revenue | 3 | pending |
| line-1 | line-1-0229-0151-s003007 | reverse | revenue | 3 | pending |
| line-1 | line-1-0224-0322-s006469 | forward | revenue | 3 | pending |
| line-1 | line-1-0224-0322-s006469 | reverse | revenue | 3 | pending |
| line-1 | line-1-0219-0448-s009042 | forward | revenue | 3 | pending |
| line-1 | line-1-0219-0448-s009042 | reverse | revenue | 2 | pending |
| line-1 | line-1-0215-0575-s011615 | reverse | revenue | 2 | pending |
| line-1 | line-1-0219-0448-s009042 | reverse | spare | 1 | pending |
| line-1 | line-1-0215-0575-s011615 | reverse | spare | 1 | pending |
| line-1 | line-1-0240-0026-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0425-0361-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0364-0375-s001348 | forward | revenue | 2 | pending |
| line-2 | line-2-0364-0375-s001348 | reverse | revenue | 2 | pending |
| line-2 | line-2-0288-0393-s003017 | forward | revenue | 2 | pending |
| line-2 | line-2-0288-0393-s003017 | reverse | revenue | 2 | pending |
| line-2 | line-2-0185-0417-s005276 | forward | revenue | 2 | pending |
| line-2 | line-2-0185-0417-s005276 | reverse | revenue | 2 | pending |
| line-2 | line-2-0099-0457-s007550 | reverse | revenue | 2 | pending |
| line-2 | line-2-0425-0361-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0364-0375-s001348 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0371-0432-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0353-0357-s001649 | forward | revenue | 3 | pending |
| line-3 | line-3-0353-0357-s001649 | reverse | revenue | 2 | pending |
| line-3 | line-3-0337-0296-s003002 | forward | revenue | 2 | pending |
| line-3 | line-3-0337-0296-s003002 | reverse | revenue | 2 | pending |
| line-3 | line-3-0298-0136-s006525 | forward | revenue | 2 | pending |
| line-3 | line-3-0298-0136-s006525 | reverse | revenue | 2 | pending |
| line-3 | line-3-0289-0034-s009300 | reverse | revenue | 2 | pending |
| line-3 | line-3-0353-0357-s001649 | reverse | spare | 1 | pending |
| line-3 | line-3-0337-0296-s003002 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**29 trainsets exceed the reference platform envelope**, requiring **1,421.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0575-s011615 | 3 | 2 | 1 | 49.0 |
| line-1-0219-0448-s009042 | 6 | 2 | 4 | 196.0 |
| line-1-0224-0322-s006469 | 6 | 2 | 4 | 196.0 |
| line-1-0229-0151-s003007 | 6 | 2 | 4 | 196.0 |
| line-1-0240-0026-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0099-0457-s007550 | 2 | 2 | 0 | 0.0 |
| line-2-0185-0417-s005276 | 4 | 2 | 2 | 98.0 |
| line-2-0288-0393-s003017 | 4 | 2 | 2 | 98.0 |
| line-2-0364-0375-s001348 | 5 | 4 | 1 | 49.0 |
| line-2-0425-0361-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0289-0034-s009300 | 2 | 2 | 0 | 0.0 |
| line-3-0298-0136-s006525 | 4 | 2 | 2 | 98.0 |
| line-3-0337-0296-s003002 | 5 | 2 | 3 | 147.0 |
| line-3-0353-0357-s001649 | 6 | 4 | 2 | 98.0 |
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
