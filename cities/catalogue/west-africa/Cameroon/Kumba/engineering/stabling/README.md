# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 116 at depots = 150 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0051-0779-s020624 | line-1 | declared-depot | 54 | 3,213.0 | 9 |
| line-2-0693-0212-s000000 | line-2 | declared-depot | 29 | 1,725.5 | 6 |
| line-3-0771-0652-s000000 | line-3 | declared-depot | 19 | 1,130.5 | 4 |
| line-4-0559-0461-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0051-0779-s020624 | station | reverse | revenue | 2 |
| line-1 | line-1-0470-0577-s009042 | station | forward | revenue | 1 |
| line-1 | line-1-0470-0577-s009042 | station | reverse | revenue | 1 |
| line-1 | line-1-0561-0562-s006500 | station | forward | revenue | 1 |
| line-1 | line-1-0561-0562-s006500 | station | reverse | revenue | 1 |
| line-1 | line-1-0668-0573-s003741 | station | forward | revenue | 1 |
| line-1 | line-1-0668-0573-s003741 | station | reverse | revenue | 1 |
| line-1 | line-1-0782-0630-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0550-0694-s012740 | station | reverse | revenue | 2 |
| line-2 | line-2-0553-0485-s007407 | station | forward | revenue | 1 |
| line-2 | line-2-0553-0485-s007407 | station | reverse | revenue | 1 |
| line-2 | line-2-0560-0459-s006678 | station | forward | revenue | 1 |
| line-2 | line-2-0560-0459-s006678 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0563-s009413 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0563-s009413 | station | reverse | revenue | 1 |
| line-2 | line-2-0693-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0482-0431-s008138 | station | reverse | revenue | 2 |
| line-3 | line-3-0553-0485-s006165 | station | forward | revenue | 1 |
| line-3 | line-3-0553-0485-s006165 | station | reverse | revenue | 1 |
| line-3 | line-3-0668-0573-s002914 | station | forward | revenue | 1 |
| line-3 | line-3-0668-0573-s002914 | station | reverse | revenue | 1 |
| line-3 | line-3-0771-0652-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0559-0461-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0686-0487-s003371 | station | forward | revenue | 1 |
| line-4 | line-4-0686-0487-s003371 | station | reverse | revenue | 1 |
| line-4 | line-4-0761-0539-s005767 | station | reverse | revenue | 2 |
| line-1 | line-1-0051-0779-s020624 | depot | — | revenue | 48 |
| line-1 | line-1-0051-0779-s020624 | depot | — | spare | 5 |
| line-1 | line-1-0051-0779-s020624 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0693-0212-s000000 | depot | — | revenue | 25 |
| line-2 | line-2-0693-0212-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0693-0212-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0771-0652-s000000 | depot | — | revenue | 16 |
| line-3 | line-3-0771-0652-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0771-0652-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0559-0461-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0559-0461-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0559-0461-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kumba-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **150 trainsets at 17 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **135 revenue, 11 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **116 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0782-0630-s000000 | forward | revenue | 8 | pending |
| line-1 | line-1-0668-0573-s003741 | forward | revenue | 8 | pending |
| line-1 | line-1-0668-0573-s003741 | reverse | revenue | 7 | pending |
| line-1 | line-1-0561-0562-s006500 | forward | revenue | 7 | pending |
| line-1 | line-1-0561-0562-s006500 | reverse | revenue | 7 | pending |
| line-1 | line-1-0470-0577-s009042 | forward | revenue | 7 | pending |
| line-1 | line-1-0470-0577-s009042 | reverse | revenue | 7 | pending |
| line-1 | line-1-0051-0779-s020624 | reverse | revenue | 7 | pending |
| line-1 | line-1-0668-0573-s003741 | reverse | spare | 1 | pending |
| line-1 | line-1-0561-0562-s006500 | forward | spare | 1 | pending |
| line-1 | line-1-0561-0562-s006500 | reverse | spare | 1 | pending |
| line-1 | line-1-0470-0577-s009042 | forward | spare | 1 | pending |
| line-1 | line-1-0470-0577-s009042 | reverse | spare | 1 | pending |
| line-1 | line-1-0051-0779-s020624 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0693-0212-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0560-0459-s006678 | forward | revenue | 5 | pending |
| line-2 | line-2-0560-0459-s006678 | reverse | revenue | 5 | pending |
| line-2 | line-2-0553-0485-s007407 | forward | revenue | 4 | pending |
| line-2 | line-2-0553-0485-s007407 | reverse | revenue | 4 | pending |
| line-2 | line-2-0561-0563-s009413 | forward | revenue | 4 | pending |
| line-2 | line-2-0561-0563-s009413 | reverse | revenue | 4 | pending |
| line-2 | line-2-0550-0694-s012740 | reverse | revenue | 4 | pending |
| line-2 | line-2-0553-0485-s007407 | forward | spare | 1 | pending |
| line-2 | line-2-0553-0485-s007407 | reverse | spare | 1 | pending |
| line-2 | line-2-0561-0563-s009413 | forward | spare | 1 | pending |
| line-2 | line-2-0561-0563-s009413 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0771-0652-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0668-0573-s002914 | forward | revenue | 4 | pending |
| line-3 | line-3-0668-0573-s002914 | reverse | revenue | 4 | pending |
| line-3 | line-3-0553-0485-s006165 | forward | revenue | 4 | pending |
| line-3 | line-3-0553-0485-s006165 | reverse | revenue | 4 | pending |
| line-3 | line-3-0482-0431-s008138 | reverse | revenue | 4 | pending |
| line-3 | line-3-0771-0652-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0668-0573-s002914 | forward | spare | 1 | pending |
| line-3 | line-3-0668-0573-s002914 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0559-0461-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0686-0487-s003371 | forward | revenue | 5 | pending |
| line-4 | line-4-0686-0487-s003371 | reverse | revenue | 4 | pending |
| line-4 | line-4-0761-0539-s005767 | reverse | revenue | 4 | pending |
| line-4 | line-4-0686-0487-s003371 | reverse | spare | 1 | pending |
| line-4 | line-4-0761-0539-s005767 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**102 trainsets exceed the reference platform envelope**, requiring **6,069.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0051-0779-s020624 | 8 | 2 | 6 | 357.0 |
| line-1-0470-0577-s009042 | 16 | 2 | 14 | 833.0 |
| line-1-0561-0562-s006500 | 16 | 4 | 12 | 714.0 |
| line-1-0668-0573-s003741 | 16 | 4 | 12 | 714.0 |
| line-1-0782-0630-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0550-0694-s012740 | 4 | 2 | 2 | 119.0 |
| line-2-0553-0485-s007407 | 10 | 4 | 6 | 357.0 |
| line-2-0560-0459-s006678 | 10 | 4 | 6 | 357.0 |
| line-2-0561-0563-s009413 | 10 | 4 | 6 | 357.0 |
| line-2-0693-0212-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0482-0431-s008138 | 4 | 2 | 2 | 119.0 |
| line-3-0553-0485-s006165 | 8 | 4 | 4 | 238.0 |
| line-3-0668-0573-s002914 | 10 | 4 | 6 | 357.0 |
| line-3-0771-0652-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0559-0461-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0686-0487-s003371 | 10 | 2 | 8 | 476.0 |
| line-4-0761-0539-s005767 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Kumba/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
