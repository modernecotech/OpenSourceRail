# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 145 at depots = 181 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0437-0220-s023316 | line-1 | declared-depot | 55 | 3,272.5 | 10 |
| line-2-0346-0285-s000000 | line-2 | declared-depot | 50 | 2,975.0 | 8 |
| line-3-0306-1057-s000000 | line-3 | declared-depot | 40 | 2,380.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0437-0220-s023316 | station | reverse | revenue | 2 |
| line-1 | line-1-0490-0306-s021063 | station | forward | revenue | 1 |
| line-1 | line-1-0490-0306-s021063 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0392-s018791 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0392-s018791 | station | reverse | revenue | 1 |
| line-1 | line-1-0595-0599-s013045 | station | forward | revenue | 1 |
| line-1 | line-1-0595-0599-s013045 | station | reverse | revenue | 1 |
| line-1 | line-1-0597-0478-s016538 | station | forward | revenue | 1 |
| line-1 | line-1-0597-0478-s016538 | station | reverse | revenue | 1 |
| line-1 | line-1-0704-0693-s010030 | station | forward | revenue | 1 |
| line-1 | line-1-0704-0693-s010030 | station | reverse | revenue | 1 |
| line-1 | line-1-0765-0747-s007019 | station | forward | revenue | 1 |
| line-1 | line-1-0765-0747-s007019 | station | reverse | revenue | 1 |
| line-1 | line-1-0880-1029-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0346-0285-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0449-0483-s004954 | station | forward | revenue | 1 |
| line-2 | line-2-0449-0483-s004954 | station | reverse | revenue | 1 |
| line-2 | line-2-0526-0631-s008681 | station | forward | revenue | 1 |
| line-2 | line-2-0526-0631-s008681 | station | reverse | revenue | 1 |
| line-2 | line-2-0784-1025-s018855 | station | reverse | revenue | 2 |
| line-3 | line-3-0306-1057-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0445-0807-s007004 | station | forward | revenue | 1 |
| line-3 | line-3-0445-0807-s007004 | station | reverse | revenue | 1 |
| line-3 | line-3-0526-0631-s011277 | station | forward | revenue | 1 |
| line-3 | line-3-0526-0631-s011277 | station | reverse | revenue | 1 |
| line-3 | line-3-0561-0556-s013103 | station | forward | revenue | 1 |
| line-3 | line-3-0561-0556-s013103 | station | reverse | revenue | 1 |
| line-3 | line-3-0597-0478-s014996 | station | forward | revenue | 1 |
| line-3 | line-3-0597-0478-s014996 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0427-s016238 | station | reverse | revenue | 2 |
| line-1 | line-1-0437-0220-s023316 | depot | — | revenue | 48 |
| line-1 | line-1-0437-0220-s023316 | depot | — | spare | 6 |
| line-1 | line-1-0437-0220-s023316 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0346-0285-s000000 | depot | — | revenue | 44 |
| line-2 | line-2-0346-0285-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0346-0285-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0306-1057-s000000 | depot | — | revenue | 35 |
| line-3 | line-3-0306-1057-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0306-1057-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/galle-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **181 trainsets at 18 stations**; largest initial station queue **20**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **163 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **145 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0880-1029-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0765-0747-s007019 | forward | revenue | 5 | pending |
| line-1 | line-1-0765-0747-s007019 | reverse | revenue | 5 | pending |
| line-1 | line-1-0704-0693-s010030 | forward | revenue | 5 | pending |
| line-1 | line-1-0704-0693-s010030 | reverse | revenue | 5 | pending |
| line-1 | line-1-0595-0599-s013045 | forward | revenue | 5 | pending |
| line-1 | line-1-0595-0599-s013045 | reverse | revenue | 5 | pending |
| line-1 | line-1-0597-0478-s016538 | forward | revenue | 5 | pending |
| line-1 | line-1-0597-0478-s016538 | reverse | revenue | 4 | pending |
| line-1 | line-1-0544-0392-s018791 | forward | revenue | 4 | pending |
| line-1 | line-1-0544-0392-s018791 | reverse | revenue | 4 | pending |
| line-1 | line-1-0490-0306-s021063 | forward | revenue | 4 | pending |
| line-1 | line-1-0490-0306-s021063 | reverse | revenue | 4 | pending |
| line-1 | line-1-0437-0220-s023316 | reverse | revenue | 4 | pending |
| line-1 | line-1-0597-0478-s016538 | reverse | spare | 1 | pending |
| line-1 | line-1-0544-0392-s018791 | forward | spare | 1 | pending |
| line-1 | line-1-0544-0392-s018791 | reverse | spare | 1 | pending |
| line-1 | line-1-0490-0306-s021063 | forward | spare | 1 | pending |
| line-1 | line-1-0490-0306-s021063 | reverse | spare | 1 | pending |
| line-1 | line-1-0437-0220-s023316 | reverse | spare | 1 | pending |
| line-1 | line-1-0880-1029-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0346-0285-s000000 | forward | revenue | 9 | pending |
| line-2 | line-2-0449-0483-s004954 | forward | revenue | 9 | pending |
| line-2 | line-2-0449-0483-s004954 | reverse | revenue | 9 | pending |
| line-2 | line-2-0526-0631-s008681 | forward | revenue | 9 | pending |
| line-2 | line-2-0526-0631-s008681 | reverse | revenue | 8 | pending |
| line-2 | line-2-0784-1025-s018855 | reverse | revenue | 8 | pending |
| line-2 | line-2-0526-0631-s008681 | reverse | spare | 1 | pending |
| line-2 | line-2-0784-1025-s018855 | reverse | spare | 1 | pending |
| line-2 | line-2-0346-0285-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0449-0483-s004954 | forward | spare | 1 | pending |
| line-2 | line-2-0449-0483-s004954 | reverse | spare | 1 | pending |
| line-2 | line-2-0526-0631-s008681 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0306-1057-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0445-0807-s007004 | forward | revenue | 5 | pending |
| line-3 | line-3-0445-0807-s007004 | reverse | revenue | 5 | pending |
| line-3 | line-3-0526-0631-s011277 | forward | revenue | 5 | pending |
| line-3 | line-3-0526-0631-s011277 | reverse | revenue | 5 | pending |
| line-3 | line-3-0561-0556-s013103 | forward | revenue | 5 | pending |
| line-3 | line-3-0561-0556-s013103 | reverse | revenue | 5 | pending |
| line-3 | line-3-0597-0478-s014996 | forward | revenue | 4 | pending |
| line-3 | line-3-0597-0478-s014996 | reverse | revenue | 4 | pending |
| line-3 | line-3-0621-0427-s016238 | reverse | revenue | 4 | pending |
| line-3 | line-3-0597-0478-s014996 | forward | spare | 1 | pending |
| line-3 | line-3-0597-0478-s014996 | reverse | spare | 1 | pending |
| line-3 | line-3-0621-0427-s016238 | reverse | spare | 1 | pending |
| line-3 | line-3-0306-1057-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0445-0807-s007004 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**137 trainsets exceed the reference platform envelope**, requiring **8,151.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0437-0220-s023316 | 5 | 2 | 3 | 178.5 |
| line-1-0490-0306-s021063 | 10 | 2 | 8 | 476.0 |
| line-1-0544-0392-s018791 | 10 | 2 | 8 | 476.0 |
| line-1-0595-0599-s013045 | 10 | 2 | 8 | 476.0 |
| line-1-0597-0478-s016538 | 10 | 4 | 6 | 357.0 |
| line-1-0704-0693-s010030 | 10 | 2 | 8 | 476.0 |
| line-1-0765-0747-s007019 | 10 | 2 | 8 | 476.0 |
| line-1-0880-1029-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0346-0285-s000000 | 10 | 2 | 8 | 476.0 |
| line-2-0449-0483-s004954 | 20 | 2 | 18 | 1,071.0 |
| line-2-0526-0631-s008681 | 19 | 4 | 15 | 892.5 |
| line-2-0784-1025-s018855 | 9 | 2 | 7 | 416.5 |
| line-3-0306-1057-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0445-0807-s007004 | 11 | 2 | 9 | 535.5 |
| line-3-0526-0631-s011277 | 10 | 4 | 6 | 357.0 |
| line-3-0561-0556-s013103 | 10 | 2 | 8 | 476.0 |
| line-3-0597-0478-s014996 | 10 | 4 | 6 | 357.0 |
| line-3-0621-0427-s016238 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Galle/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
