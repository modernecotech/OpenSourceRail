# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 103 at depots = 135 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0361-1048-s018712 | line-1 | declared-depot | 47 | 2,796.5 | 9 |
| line-2-0486-0817-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0267-0585-s000000 | line-3 | declared-depot | 34 | 2,023.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0361-1048-s018712 | station | reverse | revenue | 2 |
| line-1 | line-1-0405-0701-s010827 | station | forward | revenue | 1 |
| line-1 | line-1-0405-0701-s010827 | station | reverse | revenue | 1 |
| line-1 | line-1-0424-0623-s009098 | station | forward | revenue | 1 |
| line-1 | line-1-0424-0623-s009098 | station | reverse | revenue | 1 |
| line-1 | line-1-0441-0553-s007534 | station | forward | revenue | 1 |
| line-1 | line-1-0441-0553-s007534 | station | reverse | revenue | 1 |
| line-1 | line-1-0474-0418-s004525 | station | forward | revenue | 1 |
| line-1 | line-1-0474-0418-s004525 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0215-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0486-0817-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0528-0738-s001998 | station | forward | revenue | 1 |
| line-2 | line-2-0528-0738-s001998 | station | reverse | revenue | 1 |
| line-2 | line-2-0571-0658-s004001 | station | forward | revenue | 1 |
| line-2 | line-2-0571-0658-s004001 | station | reverse | revenue | 1 |
| line-2 | line-2-0614-0578-s006016 | station | forward | revenue | 1 |
| line-2 | line-2-0614-0578-s006016 | station | reverse | revenue | 1 |
| line-2 | line-2-0656-0499-s007979 | station | forward | revenue | 1 |
| line-2 | line-2-0656-0499-s007979 | station | reverse | revenue | 1 |
| line-2 | line-2-0698-0421-s009957 | station | reverse | revenue | 2 |
| line-3 | line-3-0267-0585-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0424-0623-s003478 | station | forward | revenue | 1 |
| line-3 | line-3-0424-0623-s003478 | station | reverse | revenue | 1 |
| line-3 | line-3-0571-0658-s006708 | station | forward | revenue | 1 |
| line-3 | line-3-0571-0658-s006708 | station | reverse | revenue | 1 |
| line-3 | line-3-0883-0735-s013610 | station | reverse | revenue | 2 |
| line-1 | line-1-0361-1048-s018712 | depot | — | revenue | 41 |
| line-1 | line-1-0361-1048-s018712 | depot | — | spare | 5 |
| line-1 | line-1-0361-1048-s018712 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0486-0817-s000000 | depot | — | revenue | 18 |
| line-2 | line-2-0486-0817-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0486-0817-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0267-0585-s000000 | depot | — | revenue | 30 |
| line-3 | line-3-0267-0585-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0267-0585-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/huambo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **135 trainsets at 16 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **121 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **103 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0511-0215-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0474-0418-s004525 | forward | revenue | 6 | pending |
| line-1 | line-1-0474-0418-s004525 | reverse | revenue | 6 | pending |
| line-1 | line-1-0441-0553-s007534 | forward | revenue | 5 | pending |
| line-1 | line-1-0441-0553-s007534 | reverse | revenue | 5 | pending |
| line-1 | line-1-0424-0623-s009098 | forward | revenue | 5 | pending |
| line-1 | line-1-0424-0623-s009098 | reverse | revenue | 5 | pending |
| line-1 | line-1-0405-0701-s010827 | forward | revenue | 5 | pending |
| line-1 | line-1-0405-0701-s010827 | reverse | revenue | 5 | pending |
| line-1 | line-1-0361-1048-s018712 | reverse | revenue | 5 | pending |
| line-1 | line-1-0441-0553-s007534 | forward | spare | 1 | pending |
| line-1 | line-1-0441-0553-s007534 | reverse | spare | 1 | pending |
| line-1 | line-1-0424-0623-s009098 | forward | spare | 1 | pending |
| line-1 | line-1-0424-0623-s009098 | reverse | spare | 1 | pending |
| line-1 | line-1-0405-0701-s010827 | forward | spare | 1 | pending |
| line-1 | line-1-0405-0701-s010827 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0486-0817-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0528-0738-s001998 | forward | revenue | 3 | pending |
| line-2 | line-2-0528-0738-s001998 | reverse | revenue | 3 | pending |
| line-2 | line-2-0571-0658-s004001 | forward | revenue | 3 | pending |
| line-2 | line-2-0571-0658-s004001 | reverse | revenue | 3 | pending |
| line-2 | line-2-0614-0578-s006016 | forward | revenue | 3 | pending |
| line-2 | line-2-0614-0578-s006016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0656-0499-s007979 | forward | revenue | 3 | pending |
| line-2 | line-2-0656-0499-s007979 | reverse | revenue | 3 | pending |
| line-2 | line-2-0698-0421-s009957 | reverse | revenue | 3 | pending |
| line-2 | line-2-0486-0817-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0738-s001998 | forward | spare | 1 | pending |
| line-2 | line-2-0528-0738-s001998 | reverse | spare | 1 | pending |
| line-2 | line-2-0571-0658-s004001 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0267-0585-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0424-0623-s003478 | forward | revenue | 7 | pending |
| line-3 | line-3-0424-0623-s003478 | reverse | revenue | 6 | pending |
| line-3 | line-3-0571-0658-s006708 | forward | revenue | 6 | pending |
| line-3 | line-3-0571-0658-s006708 | reverse | revenue | 6 | pending |
| line-3 | line-3-0883-0735-s013610 | reverse | revenue | 6 | pending |
| line-3 | line-3-0424-0623-s003478 | reverse | spare | 1 | pending |
| line-3 | line-3-0571-0658-s006708 | forward | spare | 1 | pending |
| line-3 | line-3-0571-0658-s006708 | reverse | spare | 1 | pending |
| line-3 | line-3-0883-0735-s013610 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**95 trainsets exceed the reference platform envelope**, requiring **5,652.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0361-1048-s018712 | 5 | 2 | 3 | 178.5 |
| line-1-0405-0701-s010827 | 12 | 2 | 10 | 595.0 |
| line-1-0424-0623-s009098 | 12 | 4 | 8 | 476.0 |
| line-1-0441-0553-s007534 | 12 | 2 | 10 | 595.0 |
| line-1-0474-0418-s004525 | 12 | 2 | 10 | 595.0 |
| line-1-0511-0215-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0486-0817-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0528-0738-s001998 | 8 | 2 | 6 | 357.0 |
| line-2-0571-0658-s004001 | 7 | 4 | 3 | 178.5 |
| line-2-0614-0578-s006016 | 6 | 2 | 4 | 238.0 |
| line-2-0656-0499-s007979 | 6 | 2 | 4 | 238.0 |
| line-2-0698-0421-s009957 | 3 | 2 | 1 | 59.5 |
| line-3-0267-0585-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0424-0623-s003478 | 14 | 4 | 10 | 595.0 |
| line-3-0571-0658-s006708 | 14 | 4 | 10 | 595.0 |
| line-3-0883-0735-s013610 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Huambo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
