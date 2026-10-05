# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 57 at depots = 87 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0615-0713-s000000 | line-1 | declared-depot | 22 | 1,309.0 | 5 |
| line-2-0575-0330-s000000 | line-2 | declared-depot | 11 | 654.5 | 3 |
| line-3-0541-0610-s010192 | line-3 | declared-depot | 24 | 1,428.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0615-0713-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0654-0553-s003547 | station | forward | revenue | 1 |
| line-1 | line-1-0654-0553-s003547 | station | reverse | revenue | 1 |
| line-1 | line-1-0667-0497-s004774 | station | forward | revenue | 1 |
| line-1 | line-1-0667-0497-s004774 | station | reverse | revenue | 1 |
| line-1 | line-1-0681-0441-s006010 | station | forward | revenue | 1 |
| line-1 | line-1-0681-0441-s006010 | station | reverse | revenue | 1 |
| line-1 | line-1-0723-0266-s009882 | station | reverse | revenue | 2 |
| line-2 | line-2-0575-0330-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0621-0460-s003016 | station | forward | revenue | 1 |
| line-2 | line-2-0621-0460-s003016 | station | reverse | revenue | 1 |
| line-2 | line-2-0642-0519-s004394 | station | forward | revenue | 1 |
| line-2 | line-2-0642-0519-s004394 | station | reverse | revenue | 1 |
| line-2 | line-2-0654-0553-s005173 | station | forward | revenue | 1 |
| line-2 | line-2-0654-0553-s005173 | station | reverse | revenue | 1 |
| line-2 | line-2-0657-0561-s005358 | station | reverse | revenue | 2 |
| line-3 | line-3-0541-0610-s010192 | station | reverse | revenue | 2 |
| line-3 | line-3-0642-0519-s007149 | station | forward | revenue | 1 |
| line-3 | line-3-0642-0519-s007149 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0497-s006396 | station | forward | revenue | 1 |
| line-3 | line-3-0667-0497-s006396 | station | reverse | revenue | 1 |
| line-3 | line-3-0711-0457-s005068 | station | forward | revenue | 1 |
| line-3 | line-3-0711-0457-s005068 | station | reverse | revenue | 1 |
| line-3 | line-3-0879-0306-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0615-0713-s000000 | depot | — | revenue | 19 |
| line-1 | line-1-0615-0713-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0615-0713-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0575-0330-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0575-0330-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0575-0330-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0541-0610-s010192 | depot | — | revenue | 20 |
| line-3 | line-3-0541-0610-s010192 | depot | — | spare | 3 |
| line-3 | line-3-0541-0610-s010192 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/aba-ng-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **87 trainsets at 15 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **78 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **57 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0615-0713-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0654-0553-s003547 | forward | revenue | 4 | pending |
| line-1 | line-1-0654-0553-s003547 | reverse | revenue | 4 | pending |
| line-1 | line-1-0667-0497-s004774 | forward | revenue | 4 | pending |
| line-1 | line-1-0667-0497-s004774 | reverse | revenue | 4 | pending |
| line-1 | line-1-0681-0441-s006010 | forward | revenue | 3 | pending |
| line-1 | line-1-0681-0441-s006010 | reverse | revenue | 3 | pending |
| line-1 | line-1-0723-0266-s009882 | reverse | revenue | 3 | pending |
| line-1 | line-1-0681-0441-s006010 | forward | spare | 1 | pending |
| line-1 | line-1-0681-0441-s006010 | reverse | spare | 1 | pending |
| line-1 | line-1-0723-0266-s009882 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0575-0330-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0621-0460-s003016 | forward | revenue | 3 | pending |
| line-2 | line-2-0621-0460-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0642-0519-s004394 | forward | revenue | 2 | pending |
| line-2 | line-2-0642-0519-s004394 | reverse | revenue | 2 | pending |
| line-2 | line-2-0654-0553-s005173 | forward | revenue | 2 | pending |
| line-2 | line-2-0654-0553-s005173 | reverse | revenue | 2 | pending |
| line-2 | line-2-0657-0561-s005358 | reverse | revenue | 2 | pending |
| line-2 | line-2-0642-0519-s004394 | forward | spare | 1 | pending |
| line-2 | line-2-0642-0519-s004394 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0879-0306-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0711-0457-s005068 | forward | revenue | 4 | pending |
| line-3 | line-3-0711-0457-s005068 | reverse | revenue | 4 | pending |
| line-3 | line-3-0667-0497-s006396 | forward | revenue | 4 | pending |
| line-3 | line-3-0667-0497-s006396 | reverse | revenue | 4 | pending |
| line-3 | line-3-0642-0519-s007149 | forward | revenue | 4 | pending |
| line-3 | line-3-0642-0519-s007149 | reverse | revenue | 3 | pending |
| line-3 | line-3-0541-0610-s010192 | reverse | revenue | 3 | pending |
| line-3 | line-3-0642-0519-s007149 | reverse | spare | 1 | pending |
| line-3 | line-3-0541-0610-s010192 | reverse | spare | 1 | pending |
| line-3 | line-3-0879-0306-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0711-0457-s005068 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**41 trainsets exceed the reference platform envelope**, requiring **2,439.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0615-0713-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0654-0553-s003547 | 8 | 4 | 4 | 238.0 |
| line-1-0667-0497-s004774 | 8 | 4 | 4 | 238.0 |
| line-1-0681-0441-s006010 | 8 | 4 | 4 | 238.0 |
| line-1-0723-0266-s009882 | 4 | 2 | 2 | 119.0 |
| line-2-0575-0330-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0621-0460-s003016 | 6 | 2 | 4 | 238.0 |
| line-2-0642-0519-s004394 | 6 | 4 | 2 | 119.0 |
| line-2-0654-0553-s005173 | 4 | 4 | 0 | 0.0 |
| line-2-0657-0561-s005358 | 2 | 2 | 0 | 0.0 |
| line-3-0541-0610-s010192 | 4 | 2 | 2 | 119.0 |
| line-3-0642-0519-s007149 | 8 | 4 | 4 | 238.0 |
| line-3-0667-0497-s006396 | 8 | 4 | 4 | 238.0 |
| line-3-0711-0457-s005068 | 9 | 4 | 5 | 297.5 |
| line-3-0879-0306-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Aba-Ng/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
