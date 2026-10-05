# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **24 trainsets at stations + 38 at depots = 62 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0328-0422-s000000 | line-1 | declared-depot | 12 | 588.0 | 3 |
| line-2-0479-0445-s012386 | line-2 | declared-depot | 17 | 833.0 | 4 |
| line-3-0619-0416-s000000 | line-3 | declared-depot | 9 | 441.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0328-0422-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0362-0348-s001809 | station | forward | revenue | 1 |
| line-1 | line-1-0362-0348-s001809 | station | reverse | revenue | 1 |
| line-1 | line-1-0378-0314-s002645 | station | forward | revenue | 1 |
| line-1 | line-1-0378-0314-s002645 | station | reverse | revenue | 1 |
| line-1 | line-1-0440-0045-s009051 | station | reverse | revenue | 2 |
| line-2 | line-2-0034-0117-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0272-0273-s006388 | station | forward | revenue | 1 |
| line-2 | line-2-0272-0273-s006388 | station | reverse | revenue | 1 |
| line-2 | line-2-0362-0348-s008985 | station | forward | revenue | 1 |
| line-2 | line-2-0362-0348-s008985 | station | reverse | revenue | 1 |
| line-2 | line-2-0479-0445-s012386 | station | reverse | revenue | 2 |
| line-3 | line-3-0313-0282-s007590 | station | reverse | revenue | 2 |
| line-3 | line-3-0378-0314-s005990 | station | forward | revenue | 1 |
| line-3 | line-3-0378-0314-s005990 | station | reverse | revenue | 1 |
| line-3 | line-3-0499-0374-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0499-0374-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0619-0416-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0328-0422-s000000 | depot | — | revenue | 10 |
| line-1 | line-1-0328-0422-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0328-0422-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0479-0445-s012386 | depot | — | revenue | 14 |
| line-2 | line-2-0479-0445-s012386 | depot | — | spare | 2 |
| line-2 | line-2-0479-0445-s012386 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0619-0416-s000000 | depot | — | revenue | 7 |
| line-3 | line-3-0619-0416-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0619-0416-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nador-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **62 trainsets at 12 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **55 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **38 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0328-0422-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0362-0348-s001809 | forward | revenue | 3 | pending |
| line-1 | line-1-0362-0348-s001809 | reverse | revenue | 3 | pending |
| line-1 | line-1-0378-0314-s002645 | forward | revenue | 3 | pending |
| line-1 | line-1-0378-0314-s002645 | reverse | revenue | 3 | pending |
| line-1 | line-1-0440-0045-s009051 | reverse | revenue | 3 | pending |
| line-1 | line-1-0328-0422-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0362-0348-s001809 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0034-0117-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0272-0273-s006388 | forward | revenue | 4 | pending |
| line-2 | line-2-0272-0273-s006388 | reverse | revenue | 4 | pending |
| line-2 | line-2-0362-0348-s008985 | forward | revenue | 4 | pending |
| line-2 | line-2-0362-0348-s008985 | reverse | revenue | 3 | pending |
| line-2 | line-2-0479-0445-s012386 | reverse | revenue | 3 | pending |
| line-2 | line-2-0362-0348-s008985 | reverse | spare | 1 | pending |
| line-2 | line-2-0479-0445-s012386 | reverse | spare | 1 | pending |
| line-2 | line-2-0034-0117-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0619-0416-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0499-0374-s003002 | forward | revenue | 3 | pending |
| line-3 | line-3-0499-0374-s003002 | reverse | revenue | 3 | pending |
| line-3 | line-3-0378-0314-s005990 | forward | revenue | 2 | pending |
| line-3 | line-3-0378-0314-s005990 | reverse | revenue | 2 | pending |
| line-3 | line-3-0313-0282-s007590 | reverse | revenue | 2 | pending |
| line-3 | line-3-0378-0314-s005990 | forward | spare | 1 | pending |
| line-3 | line-3-0378-0314-s005990 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**30 trainsets exceed the reference platform envelope**, requiring **1,470.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0328-0422-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0362-0348-s001809 | 7 | 4 | 3 | 147.0 |
| line-1-0378-0314-s002645 | 6 | 4 | 2 | 98.0 |
| line-1-0440-0045-s009051 | 3 | 2 | 1 | 49.0 |
| line-2-0034-0117-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0272-0273-s006388 | 8 | 2 | 6 | 294.0 |
| line-2-0362-0348-s008985 | 8 | 4 | 4 | 196.0 |
| line-2-0479-0445-s012386 | 4 | 2 | 2 | 98.0 |
| line-3-0313-0282-s007590 | 2 | 2 | 0 | 0.0 |
| line-3-0378-0314-s005990 | 6 | 4 | 2 | 98.0 |
| line-3-0499-0374-s003002 | 6 | 2 | 4 | 196.0 |
| line-3-0619-0416-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Nador/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
