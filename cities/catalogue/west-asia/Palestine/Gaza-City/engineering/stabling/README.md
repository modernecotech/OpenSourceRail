# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **20 trainsets at stations + 70 at depots = 90 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0462-0834-s000000 | line-1 | declared-depot | 19 | 1,130.5 | 4 |
| line-2-0913-0374-s013928 | line-2 | declared-depot | 37 | 2,201.5 | 6 |
| line-3-0680-0673-s000000 | line-3 | declared-depot | 14 | 833.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0462-0834-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0525-0713-s003000 | station | forward | revenue | 1 |
| line-1 | line-1-0525-0713-s003000 | station | reverse | revenue | 1 |
| line-1 | line-1-0587-0595-s006015 | station | forward | revenue | 1 |
| line-1 | line-1-0587-0595-s006015 | station | reverse | revenue | 1 |
| line-1 | line-1-0641-0492-s008569 | station | reverse | revenue | 2 |
| line-2 | line-2-0510-0774-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0619-0695-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0619-0695-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0913-0374-s013928 | station | reverse | revenue | 2 |
| line-3 | line-3-0403-0652-s005726 | station | reverse | revenue | 2 |
| line-3 | line-3-0535-0662-s003003 | station | forward | revenue | 1 |
| line-3 | line-3-0535-0662-s003003 | station | reverse | revenue | 1 |
| line-3 | line-3-0680-0673-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0462-0834-s000000 | depot | — | revenue | 16 |
| line-1 | line-1-0462-0834-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0462-0834-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0913-0374-s013928 | depot | — | revenue | 33 |
| line-2 | line-2-0913-0374-s013928 | depot | — | spare | 3 |
| line-2 | line-2-0913-0374-s013928 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0680-0673-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0680-0673-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0680-0673-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/gaza-city-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **90 trainsets at 10 stations**; largest initial station queue **22**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **81 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **70 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0462-0834-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0525-0713-s003000 | forward | revenue | 4 | pending |
| line-1 | line-1-0525-0713-s003000 | reverse | revenue | 4 | pending |
| line-1 | line-1-0587-0595-s006015 | forward | revenue | 4 | pending |
| line-1 | line-1-0587-0595-s006015 | reverse | revenue | 4 | pending |
| line-1 | line-1-0641-0492-s008569 | reverse | revenue | 4 | pending |
| line-1 | line-1-0462-0834-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0525-0713-s003000 | forward | spare | 1 | pending |
| line-1 | line-1-0525-0713-s003000 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0510-0774-s000000 | forward | revenue | 10 | pending |
| line-2 | line-2-0619-0695-s003010 | forward | revenue | 10 | pending |
| line-2 | line-2-0619-0695-s003010 | reverse | revenue | 10 | pending |
| line-2 | line-2-0913-0374-s013928 | reverse | revenue | 9 | pending |
| line-2 | line-2-0913-0374-s013928 | reverse | spare | 1 | pending |
| line-2 | line-2-0510-0774-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0619-0695-s003010 | forward | spare | 1 | pending |
| line-2 | line-2-0619-0695-s003010 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0680-0673-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0535-0662-s003003 | forward | revenue | 5 | pending |
| line-3 | line-3-0535-0662-s003003 | reverse | revenue | 4 | pending |
| line-3 | line-3-0403-0652-s005726 | reverse | revenue | 4 | pending |
| line-3 | line-3-0535-0662-s003003 | reverse | spare | 1 | pending |
| line-3 | line-3-0403-0652-s005726 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**70 trainsets exceed the reference platform envelope**, requiring **4,165.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0462-0834-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0525-0713-s003000 | 10 | 2 | 8 | 476.0 |
| line-1-0587-0595-s006015 | 8 | 2 | 6 | 357.0 |
| line-1-0641-0492-s008569 | 4 | 2 | 2 | 119.0 |
| line-2-0510-0774-s000000 | 11 | 2 | 9 | 535.5 |
| line-2-0619-0695-s003010 | 22 | 2 | 20 | 1,190.0 |
| line-2-0913-0374-s013928 | 10 | 2 | 8 | 476.0 |
| line-3-0403-0652-s005726 | 5 | 2 | 3 | 178.5 |
| line-3-0535-0662-s003003 | 10 | 2 | 8 | 476.0 |
| line-3-0680-0673-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Gaza-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
