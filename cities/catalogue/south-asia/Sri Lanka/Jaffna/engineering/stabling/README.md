# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 117 at depots = 145 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0619-0561-s000000 | line-1 | declared-depot | 24 | 1,428.0 | 5 |
| line-2-0216-0107-s019806 | line-2 | declared-depot | 53 | 3,153.5 | 9 |
| line-3-0089-1001-s000000 | line-3 | declared-depot | 40 | 2,380.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0097-0569-s010993 | station | reverse | revenue | 2 |
| line-1 | line-1-0252-0571-s007435 | station | forward | revenue | 1 |
| line-1 | line-1-0252-0571-s007435 | station | reverse | revenue | 1 |
| line-1 | line-1-0428-0566-s003861 | station | forward | revenue | 1 |
| line-1 | line-1-0428-0566-s003861 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0563-s001337 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0563-s001337 | station | reverse | revenue | 1 |
| line-1 | line-1-0619-0561-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0216-0107-s019806 | station | reverse | revenue | 2 |
| line-2 | line-2-0428-0566-s007051 | station | forward | revenue | 1 |
| line-2 | line-2-0428-0566-s007051 | station | reverse | revenue | 1 |
| line-2 | line-2-0460-0650-s005083 | station | forward | revenue | 1 |
| line-2 | line-2-0460-0650-s005083 | station | reverse | revenue | 1 |
| line-2 | line-2-0544-0867-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0089-1001-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0310-0793-s007002 | station | forward | revenue | 1 |
| line-3 | line-3-0310-0793-s007002 | station | reverse | revenue | 1 |
| line-3 | line-3-0460-0650-s011667 | station | forward | revenue | 1 |
| line-3 | line-3-0460-0650-s011667 | station | reverse | revenue | 1 |
| line-3 | line-3-0553-0563-s014552 | station | forward | revenue | 1 |
| line-3 | line-3-0553-0563-s014552 | station | reverse | revenue | 1 |
| line-3 | line-3-0600-0518-s016006 | station | reverse | revenue | 2 |
| line-1 | line-1-0619-0561-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0619-0561-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0619-0561-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0216-0107-s019806 | depot | — | revenue | 47 |
| line-2 | line-2-0216-0107-s019806 | depot | — | spare | 5 |
| line-2 | line-2-0216-0107-s019806 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0089-1001-s000000 | depot | — | revenue | 35 |
| line-3 | line-3-0089-1001-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0089-1001-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jaffna-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **145 trainsets at 14 stations**; largest initial station queue **20**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **130 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **117 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0619-0561-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0553-0563-s001337 | forward | revenue | 4 | pending |
| line-1 | line-1-0553-0563-s001337 | reverse | revenue | 4 | pending |
| line-1 | line-1-0428-0566-s003861 | forward | revenue | 4 | pending |
| line-1 | line-1-0428-0566-s003861 | reverse | revenue | 4 | pending |
| line-1 | line-1-0252-0571-s007435 | forward | revenue | 4 | pending |
| line-1 | line-1-0252-0571-s007435 | reverse | revenue | 3 | pending |
| line-1 | line-1-0097-0569-s010993 | reverse | revenue | 3 | pending |
| line-1 | line-1-0252-0571-s007435 | reverse | spare | 1 | pending |
| line-1 | line-1-0097-0569-s010993 | reverse | spare | 1 | pending |
| line-1 | line-1-0619-0561-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0553-0563-s001337 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0544-0867-s000000 | forward | revenue | 10 | pending |
| line-2 | line-2-0460-0650-s005083 | forward | revenue | 9 | pending |
| line-2 | line-2-0460-0650-s005083 | reverse | revenue | 9 | pending |
| line-2 | line-2-0428-0566-s007051 | forward | revenue | 9 | pending |
| line-2 | line-2-0428-0566-s007051 | reverse | revenue | 9 | pending |
| line-2 | line-2-0216-0107-s019806 | reverse | revenue | 9 | pending |
| line-2 | line-2-0460-0650-s005083 | forward | spare | 1 | pending |
| line-2 | line-2-0460-0650-s005083 | reverse | spare | 1 | pending |
| line-2 | line-2-0428-0566-s007051 | forward | spare | 1 | pending |
| line-2 | line-2-0428-0566-s007051 | reverse | spare | 1 | pending |
| line-2 | line-2-0216-0107-s019806 | reverse | spare | 1 | pending |
| line-2 | line-2-0544-0867-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0089-1001-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0310-0793-s007002 | forward | revenue | 6 | pending |
| line-3 | line-3-0310-0793-s007002 | reverse | revenue | 6 | pending |
| line-3 | line-3-0460-0650-s011667 | forward | revenue | 6 | pending |
| line-3 | line-3-0460-0650-s011667 | reverse | revenue | 6 | pending |
| line-3 | line-3-0553-0563-s014552 | forward | revenue | 5 | pending |
| line-3 | line-3-0553-0563-s014552 | reverse | revenue | 5 | pending |
| line-3 | line-3-0600-0518-s016006 | reverse | revenue | 5 | pending |
| line-3 | line-3-0553-0563-s014552 | forward | spare | 1 | pending |
| line-3 | line-3-0553-0563-s014552 | reverse | spare | 1 | pending |
| line-3 | line-3-0600-0518-s016006 | reverse | spare | 1 | pending |
| line-3 | line-3-0089-1001-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0310-0793-s007002 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**105 trainsets exceed the reference platform envelope**, requiring **6,247.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0097-0569-s010993 | 4 | 2 | 2 | 119.0 |
| line-1-0252-0571-s007435 | 8 | 2 | 6 | 357.0 |
| line-1-0428-0566-s003861 | 8 | 4 | 4 | 238.0 |
| line-1-0553-0563-s001337 | 9 | 4 | 5 | 297.5 |
| line-1-0619-0561-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0216-0107-s019806 | 10 | 2 | 8 | 476.0 |
| line-2-0428-0566-s007051 | 20 | 4 | 16 | 952.0 |
| line-2-0460-0650-s005083 | 20 | 4 | 16 | 952.0 |
| line-2-0544-0867-s000000 | 11 | 2 | 9 | 535.5 |
| line-3-0089-1001-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0310-0793-s007002 | 13 | 2 | 11 | 654.5 |
| line-3-0460-0650-s011667 | 12 | 4 | 8 | 476.0 |
| line-3-0553-0563-s014552 | 12 | 4 | 8 | 476.0 |
| line-3-0600-0518-s016006 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Jaffna/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
