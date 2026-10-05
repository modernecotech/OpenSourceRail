# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 101 at depots = 141 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0601-0847-s000000 | line-1 | declared-depot | 27 | 1,606.5 | 6 |
| line-2-0777-0419-s019288 | line-2 | declared-depot | 49 | 2,915.5 | 9 |
| line-3-0805-0639-s000000 | line-3 | declared-depot | 25 | 1,487.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0417-0352-s011565 | station | reverse | revenue | 2 |
| line-1 | line-1-0456-0458-s009087 | station | forward | revenue | 1 |
| line-1 | line-1-0456-0458-s009087 | station | reverse | revenue | 1 |
| line-1 | line-1-0496-0564-s006600 | station | forward | revenue | 1 |
| line-1 | line-1-0496-0564-s006600 | station | reverse | revenue | 1 |
| line-1 | line-1-0510-0601-s005744 | station | forward | revenue | 1 |
| line-1 | line-1-0510-0601-s005744 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0719-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0719-s003005 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0847-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0179-0920-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0433-0653-s010012 | station | forward | revenue | 1 |
| line-2 | line-2-0433-0653-s010012 | station | reverse | revenue | 1 |
| line-2 | line-2-0510-0601-s012065 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0601-s012065 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0576-s013039 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0576-s013039 | station | reverse | revenue | 1 |
| line-2 | line-2-0629-0520-s015280 | station | forward | revenue | 1 |
| line-2 | line-2-0629-0520-s015280 | station | reverse | revenue | 1 |
| line-2 | line-2-0655-0502-s015972 | station | forward | revenue | 1 |
| line-2 | line-2-0655-0502-s015972 | station | reverse | revenue | 1 |
| line-2 | line-2-0777-0419-s019288 | station | reverse | revenue | 2 |
| line-3 | line-3-0411-0543-s011679 | station | reverse | revenue | 2 |
| line-3 | line-3-0496-0564-s009805 | station | forward | revenue | 1 |
| line-3 | line-3-0496-0564-s009805 | station | reverse | revenue | 1 |
| line-3 | line-3-0546-0576-s008705 | station | forward | revenue | 1 |
| line-3 | line-3-0546-0576-s008705 | station | reverse | revenue | 1 |
| line-3 | line-3-0629-0520-s005904 | station | forward | revenue | 1 |
| line-3 | line-3-0629-0520-s005904 | station | reverse | revenue | 1 |
| line-3 | line-3-0655-0502-s004885 | station | forward | revenue | 1 |
| line-3 | line-3-0655-0502-s004885 | station | reverse | revenue | 1 |
| line-3 | line-3-0698-0578-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0698-0578-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0805-0639-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0601-0847-s000000 | depot | — | revenue | 23 |
| line-1 | line-1-0601-0847-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0601-0847-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0777-0419-s019288 | depot | — | revenue | 43 |
| line-2 | line-2-0777-0419-s019288 | depot | — | spare | 5 |
| line-2 | line-2-0777-0419-s019288 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0805-0639-s000000 | depot | — | revenue | 21 |
| line-3 | line-3-0805-0639-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0805-0639-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ismailia-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **141 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **127 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **101 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0601-0847-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0553-0719-s003005 | forward | revenue | 4 | pending |
| line-1 | line-1-0553-0719-s003005 | reverse | revenue | 4 | pending |
| line-1 | line-1-0510-0601-s005744 | forward | revenue | 4 | pending |
| line-1 | line-1-0510-0601-s005744 | reverse | revenue | 4 | pending |
| line-1 | line-1-0496-0564-s006600 | forward | revenue | 3 | pending |
| line-1 | line-1-0496-0564-s006600 | reverse | revenue | 3 | pending |
| line-1 | line-1-0456-0458-s009087 | forward | revenue | 3 | pending |
| line-1 | line-1-0456-0458-s009087 | reverse | revenue | 3 | pending |
| line-1 | line-1-0417-0352-s011565 | reverse | revenue | 3 | pending |
| line-1 | line-1-0496-0564-s006600 | forward | spare | 1 | pending |
| line-1 | line-1-0496-0564-s006600 | reverse | spare | 1 | pending |
| line-1 | line-1-0456-0458-s009087 | forward | spare | 1 | pending |
| line-1 | line-1-0456-0458-s009087 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0179-0920-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0433-0653-s010012 | forward | revenue | 5 | pending |
| line-2 | line-2-0433-0653-s010012 | reverse | revenue | 5 | pending |
| line-2 | line-2-0510-0601-s012065 | forward | revenue | 5 | pending |
| line-2 | line-2-0510-0601-s012065 | reverse | revenue | 5 | pending |
| line-2 | line-2-0546-0576-s013039 | forward | revenue | 5 | pending |
| line-2 | line-2-0546-0576-s013039 | reverse | revenue | 5 | pending |
| line-2 | line-2-0629-0520-s015280 | forward | revenue | 5 | pending |
| line-2 | line-2-0629-0520-s015280 | reverse | revenue | 5 | pending |
| line-2 | line-2-0655-0502-s015972 | forward | revenue | 4 | pending |
| line-2 | line-2-0655-0502-s015972 | reverse | revenue | 4 | pending |
| line-2 | line-2-0777-0419-s019288 | reverse | revenue | 4 | pending |
| line-2 | line-2-0655-0502-s015972 | forward | spare | 1 | pending |
| line-2 | line-2-0655-0502-s015972 | reverse | spare | 1 | pending |
| line-2 | line-2-0777-0419-s019288 | reverse | spare | 1 | pending |
| line-2 | line-2-0179-0920-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0433-0653-s010012 | forward | spare | 1 | pending |
| line-2 | line-2-0433-0653-s010012 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0805-0639-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0698-0578-s003009 | forward | revenue | 3 | pending |
| line-3 | line-3-0698-0578-s003009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0655-0502-s004885 | forward | revenue | 3 | pending |
| line-3 | line-3-0655-0502-s004885 | reverse | revenue | 3 | pending |
| line-3 | line-3-0629-0520-s005904 | forward | revenue | 3 | pending |
| line-3 | line-3-0629-0520-s005904 | reverse | revenue | 3 | pending |
| line-3 | line-3-0546-0576-s008705 | forward | revenue | 3 | pending |
| line-3 | line-3-0546-0576-s008705 | reverse | revenue | 3 | pending |
| line-3 | line-3-0496-0564-s009805 | forward | revenue | 3 | pending |
| line-3 | line-3-0496-0564-s009805 | reverse | revenue | 3 | pending |
| line-3 | line-3-0411-0543-s011679 | reverse | revenue | 2 | pending |
| line-3 | line-3-0411-0543-s011679 | reverse | spare | 1 | pending |
| line-3 | line-3-0805-0639-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0698-0578-s003009 | forward | spare | 1 | pending |
| line-3 | line-3-0698-0578-s003009 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**81 trainsets exceed the reference platform envelope**, requiring **4,819.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0417-0352-s011565 | 3 | 2 | 1 | 59.5 |
| line-1-0456-0458-s009087 | 8 | 2 | 6 | 357.0 |
| line-1-0496-0564-s006600 | 8 | 4 | 4 | 238.0 |
| line-1-0510-0601-s005744 | 8 | 4 | 4 | 238.0 |
| line-1-0553-0719-s003005 | 8 | 2 | 6 | 357.0 |
| line-1-0601-0847-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0179-0920-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0433-0653-s010012 | 12 | 2 | 10 | 595.0 |
| line-2-0510-0601-s012065 | 10 | 4 | 6 | 357.0 |
| line-2-0546-0576-s013039 | 10 | 4 | 6 | 357.0 |
| line-2-0629-0520-s015280 | 10 | 4 | 6 | 357.0 |
| line-2-0655-0502-s015972 | 10 | 4 | 6 | 357.0 |
| line-2-0777-0419-s019288 | 5 | 2 | 3 | 178.5 |
| line-3-0411-0543-s011679 | 3 | 2 | 1 | 59.5 |
| line-3-0496-0564-s009805 | 6 | 4 | 2 | 119.0 |
| line-3-0546-0576-s008705 | 6 | 4 | 2 | 119.0 |
| line-3-0629-0520-s005904 | 6 | 4 | 2 | 119.0 |
| line-3-0655-0502-s004885 | 6 | 4 | 2 | 119.0 |
| line-3-0698-0578-s003009 | 8 | 2 | 6 | 357.0 |
| line-3-0805-0639-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Ismailia/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
