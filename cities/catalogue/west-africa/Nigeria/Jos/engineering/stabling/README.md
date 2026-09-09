# Station and depot overnight allocation

Plan: **40 trainsets at stations + 62 at depots = 102 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0886-0587-s020991 | line-1 | declared-depot | 30 | 1,785.0 | 16 |
| line-2-0782-0526-s013305 | line-2 | storage-at-existing-powered-service-point | 16 | 952.0 | 0 |
| line-3-0711-0754-s011594 | line-3 | storage-at-existing-powered-service-point | 16 | 952.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0125-0723-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0234-0678-s003016 | station | forward | revenue | 1 |
| line-1 | line-1-0234-0678-s003016 | station | reverse | revenue | 1 |
| line-1 | line-1-0340-0685-s006019 | station | forward | revenue | 1 |
| line-1 | line-1-0340-0685-s006019 | station | reverse | revenue | 1 |
| line-1 | line-1-0447-0666-s009040 | station | forward | revenue | 1 |
| line-1 | line-1-0447-0666-s009040 | station | reverse | revenue | 1 |
| line-1 | line-1-0527-0573-s012145 | station | forward | revenue | 1 |
| line-1 | line-1-0527-0573-s012145 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0601-s015050 | station | forward | revenue | 1 |
| line-1 | line-1-0647-0601-s015050 | station | reverse | revenue | 1 |
| line-1 | line-1-0752-0600-s018026 | station | forward | revenue | 1 |
| line-1 | line-1-0752-0600-s018026 | station | reverse | revenue | 1 |
| line-1 | line-1-0886-0587-s020991 | station | reverse | revenue | 2 |
| line-2 | line-2-0217-0514-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0338-0554-s003016 | station | forward | revenue | 1 |
| line-2 | line-2-0338-0554-s003016 | station | reverse | revenue | 1 |
| line-2 | line-2-0424-0573-s005057 | station | forward | revenue | 1 |
| line-2 | line-2-0424-0573-s005057 | station | reverse | revenue | 1 |
| line-2 | line-2-0527-0573-s007117 | station | forward | revenue | 1 |
| line-2 | line-2-0527-0573-s007117 | station | reverse | revenue | 1 |
| line-2 | line-2-0599-0534-s009032 | station | forward | revenue | 1 |
| line-2 | line-2-0599-0534-s009032 | station | reverse | revenue | 1 |
| line-2 | line-2-0686-0505-s011162 | station | forward | revenue | 1 |
| line-2 | line-2-0686-0505-s011162 | station | reverse | revenue | 1 |
| line-2 | line-2-0782-0526-s013305 | station | reverse | revenue | 2 |
| line-3 | line-3-0338-0806-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0403-0747-s003004 | station | forward | revenue | 1 |
| line-3 | line-3-0403-0747-s003004 | station | reverse | revenue | 1 |
| line-3 | line-3-0516-0735-s006014 | station | forward | revenue | 1 |
| line-3 | line-3-0516-0735-s006014 | station | reverse | revenue | 1 |
| line-3 | line-3-0650-0711-s009026 | station | forward | revenue | 1 |
| line-3 | line-3-0650-0711-s009026 | station | reverse | revenue | 1 |
| line-3 | line-3-0711-0754-s011594 | station | reverse | revenue | 2 |
| line-1 | line-1-0886-0587-s020991 | depot | — | revenue | 25 |
| line-1 | line-1-0886-0587-s020991 | depot | — | spare | 4 |
| line-1 | line-1-0886-0587-s020991 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0782-0526-s013305 | depot | — | revenue | 13 |
| line-2 | line-2-0782-0526-s013305 | depot | — | spare | 2 |
| line-2 | line-2-0782-0526-s013305 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0711-0754-s011594 | depot | — | revenue | 13 |
| line-3 | line-3-0711-0754-s011594 | depot | — | spare | 2 |
| line-3 | line-3-0711-0754-s011594 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jos-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **102 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **91 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **62 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0125-0723-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0234-0678-s003016 | forward | revenue | 3 | pending |
| line-1 | line-1-0234-0678-s003016 | reverse | revenue | 3 | pending |
| line-1 | line-1-0340-0685-s006019 | forward | revenue | 3 | pending |
| line-1 | line-1-0340-0685-s006019 | reverse | revenue | 3 | pending |
| line-1 | line-1-0447-0666-s009040 | forward | revenue | 3 | pending |
| line-1 | line-1-0447-0666-s009040 | reverse | revenue | 3 | pending |
| line-1 | line-1-0527-0573-s012145 | forward | revenue | 3 | pending |
| line-1 | line-1-0527-0573-s012145 | reverse | revenue | 3 | pending |
| line-1 | line-1-0647-0601-s015050 | forward | revenue | 3 | pending |
| line-1 | line-1-0647-0601-s015050 | reverse | revenue | 3 | pending |
| line-1 | line-1-0752-0600-s018026 | forward | revenue | 3 | pending |
| line-1 | line-1-0752-0600-s018026 | reverse | revenue | 3 | pending |
| line-1 | line-1-0886-0587-s020991 | reverse | revenue | 2 | pending |
| line-1 | line-1-0886-0587-s020991 | reverse | spare | 1 | pending |
| line-1 | line-1-0125-0723-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0234-0678-s003016 | forward | spare | 1 | pending |
| line-1 | line-1-0234-0678-s003016 | reverse | spare | 1 | pending |
| line-1 | line-1-0340-0685-s006019 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0217-0514-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0338-0554-s003016 | forward | revenue | 3 | pending |
| line-2 | line-2-0338-0554-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0424-0573-s005057 | forward | revenue | 2 | pending |
| line-2 | line-2-0424-0573-s005057 | reverse | revenue | 2 | pending |
| line-2 | line-2-0527-0573-s007117 | forward | revenue | 2 | pending |
| line-2 | line-2-0527-0573-s007117 | reverse | revenue | 2 | pending |
| line-2 | line-2-0599-0534-s009032 | forward | revenue | 2 | pending |
| line-2 | line-2-0599-0534-s009032 | reverse | revenue | 2 | pending |
| line-2 | line-2-0686-0505-s011162 | forward | revenue | 2 | pending |
| line-2 | line-2-0686-0505-s011162 | reverse | revenue | 2 | pending |
| line-2 | line-2-0782-0526-s013305 | reverse | revenue | 2 | pending |
| line-2 | line-2-0424-0573-s005057 | forward | spare | 1 | pending |
| line-2 | line-2-0424-0573-s005057 | reverse | spare | 1 | pending |
| line-2 | line-2-0527-0573-s007117 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0338-0806-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0403-0747-s003004 | forward | revenue | 3 | pending |
| line-3 | line-3-0403-0747-s003004 | reverse | revenue | 3 | pending |
| line-3 | line-3-0516-0735-s006014 | forward | revenue | 3 | pending |
| line-3 | line-3-0516-0735-s006014 | reverse | revenue | 3 | pending |
| line-3 | line-3-0650-0711-s009026 | forward | revenue | 3 | pending |
| line-3 | line-3-0650-0711-s009026 | reverse | revenue | 3 | pending |
| line-3 | line-3-0711-0754-s011594 | reverse | revenue | 2 | pending |
| line-3 | line-3-0711-0754-s011594 | reverse | spare | 1 | pending |
| line-3 | line-3-0338-0806-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0403-0747-s003004 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**58 trainsets exceed the reference platform envelope**, requiring **3,451.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0125-0723-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0234-0678-s003016 | 8 | 2 | 6 | 357.0 |
| line-1-0340-0685-s006019 | 7 | 2 | 5 | 297.5 |
| line-1-0447-0666-s009040 | 6 | 2 | 4 | 238.0 |
| line-1-0527-0573-s012145 | 6 | 4 | 2 | 119.0 |
| line-1-0647-0601-s015050 | 6 | 2 | 4 | 238.0 |
| line-1-0752-0600-s018026 | 6 | 2 | 4 | 238.0 |
| line-1-0886-0587-s020991 | 3 | 2 | 1 | 59.5 |
| line-2-0217-0514-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0338-0554-s003016 | 6 | 2 | 4 | 238.0 |
| line-2-0424-0573-s005057 | 6 | 2 | 4 | 238.0 |
| line-2-0527-0573-s007117 | 5 | 4 | 1 | 59.5 |
| line-2-0599-0534-s009032 | 4 | 2 | 2 | 119.0 |
| line-2-0686-0505-s011162 | 4 | 2 | 2 | 119.0 |
| line-2-0782-0526-s013305 | 2 | 2 | 0 | 0.0 |
| line-3-0338-0806-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0403-0747-s003004 | 7 | 2 | 5 | 297.5 |
| line-3-0516-0735-s006014 | 6 | 2 | 4 | 238.0 |
| line-3-0650-0711-s009026 | 6 | 2 | 4 | 238.0 |
| line-3-0711-0754-s011594 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Jos/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
