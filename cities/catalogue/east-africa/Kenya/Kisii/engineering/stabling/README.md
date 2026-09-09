# Station and depot overnight allocation

Plan: **24 trainsets at stations + 28 at depots = 52 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0375-0406-s010911 | 28 | 1,372.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0274-0217-s007109 | station | reverse | revenue | 2 |
| line-1 | line-1-0321-0298-s005038 | station | forward | revenue | 1 |
| line-1 | line-1-0321-0298-s005038 | station | reverse | revenue | 1 |
| line-1 | line-1-0371-0371-s002960 | station | forward | revenue | 1 |
| line-1 | line-1-0371-0371-s002960 | station | reverse | revenue | 1 |
| line-1 | line-1-0433-0474-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0226-0282-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0304-0366-s003002 | station | forward | revenue | 1 |
| line-2 | line-2-0304-0366-s003002 | station | reverse | revenue | 1 |
| line-2 | line-2-0369-0293-s006259 | station | reverse | revenue | 2 |
| line-2 | line-2-0371-0371-s004682 | station | forward | revenue | 1 |
| line-2 | line-2-0371-0371-s004682 | station | reverse | revenue | 1 |
| line-3 | line-3-0027-0326-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0252-0359-s006340 | station | forward | revenue | 1 |
| line-3 | line-3-0252-0359-s006340 | station | reverse | revenue | 1 |
| line-3 | line-3-0315-0414-s008361 | station | forward | revenue | 1 |
| line-3 | line-3-0315-0414-s008361 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0406-s010911 | station | reverse | revenue | 2 |
| line-1 | line-3-0375-0406-s010911 | depot | — | revenue | 6 |
| line-1 | line-3-0375-0406-s010911 | depot | — | spare | 1 |
| line-1 | line-3-0375-0406-s010911 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0375-0406-s010911 | depot | — | revenue | 5 |
| line-2 | line-3-0375-0406-s010911 | depot | — | spare | 1 |
| line-2 | line-3-0375-0406-s010911 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0375-0406-s010911 | depot | — | revenue | 11 |
| line-3 | line-3-0375-0406-s010911 | depot | — | spare | 1 |
| line-3 | line-3-0375-0406-s010911 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (8 trains), line-2 (7 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **52 trainsets at 12 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **46 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **28 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0433-0474-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0371-0371-s002960 | forward | revenue | 3 | pending |
| line-1 | line-1-0371-0371-s002960 | reverse | revenue | 2 | pending |
| line-1 | line-1-0321-0298-s005038 | forward | revenue | 2 | pending |
| line-1 | line-1-0321-0298-s005038 | reverse | revenue | 2 | pending |
| line-1 | line-1-0274-0217-s007109 | reverse | revenue | 2 | pending |
| line-1 | line-1-0371-0371-s002960 | reverse | spare | 1 | pending |
| line-1 | line-1-0321-0298-s005038 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0226-0282-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0304-0366-s003002 | forward | revenue | 2 | pending |
| line-2 | line-2-0304-0366-s003002 | reverse | revenue | 2 | pending |
| line-2 | line-2-0371-0371-s004682 | forward | revenue | 2 | pending |
| line-2 | line-2-0371-0371-s004682 | reverse | revenue | 2 | pending |
| line-2 | line-2-0369-0293-s006259 | reverse | revenue | 2 | pending |
| line-2 | line-2-0304-0366-s003002 | forward | spare | 1 | pending |
| line-2 | line-2-0304-0366-s003002 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0027-0326-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0252-0359-s006340 | forward | revenue | 3 | pending |
| line-3 | line-3-0252-0359-s006340 | reverse | revenue | 3 | pending |
| line-3 | line-3-0315-0414-s008361 | forward | revenue | 3 | pending |
| line-3 | line-3-0315-0414-s008361 | reverse | revenue | 3 | pending |
| line-3 | line-3-0375-0406-s010911 | reverse | revenue | 3 | pending |
| line-3 | line-3-0252-0359-s006340 | forward | spare | 1 | pending |
| line-3 | line-3-0252-0359-s006340 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**24 trainsets exceed the reference platform envelope**, requiring **1,176.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0274-0217-s007109 | 2 | 2 | 0 | 0.0 |
| line-1-0321-0298-s005038 | 5 | 2 | 3 | 147.0 |
| line-1-0371-0371-s002960 | 6 | 4 | 2 | 98.0 |
| line-1-0433-0474-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0226-0282-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0304-0366-s003002 | 6 | 2 | 4 | 196.0 |
| line-2-0369-0293-s006259 | 2 | 2 | 0 | 0.0 |
| line-2-0371-0371-s004682 | 4 | 4 | 0 | 0.0 |
| line-3-0027-0326-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0252-0359-s006340 | 8 | 2 | 6 | 294.0 |
| line-3-0315-0414-s008361 | 6 | 2 | 4 | 196.0 |
| line-3-0375-0406-s010911 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisii/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
