# Station and depot overnight allocation

Plan: **10 trainsets at stations + 13 at depots = 23 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0423-0452-s010266 | 13 | 773.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0373-0716-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0423-0452-s010266 | station | reverse | revenue | 2 |
| line-1 | line-1-0433-0610-s003011 | station | forward | revenue | 1 |
| line-1 | line-1-0433-0610-s003011 | station | reverse | revenue | 1 |
| line-1 | line-1-0512-0579-s005072 | station | forward | revenue | 1 |
| line-1 | line-1-0512-0579-s005072 | station | reverse | revenue | 1 |
| line-1 | line-1-0520-0539-s007143 | station | forward | revenue | 1 |
| line-1 | line-1-0520-0539-s007143 | station | reverse | revenue | 1 |
| line-1 | line-1-0423-0452-s010266 | depot | — | revenue | 10 |
| line-1 | line-1-0423-0452-s010266 | depot | — | spare | 2 |
| line-1 | line-1-0423-0452-s010266 | depot | — | cold_reserve | 1 |

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **23 trainsets at 5 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **20 revenue, 2 spare, 1 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **10 positions**; **13 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **4 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0373-0716-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0433-0610-s003011 | forward | revenue | 3 | pending |
| line-1 | line-1-0433-0610-s003011 | reverse | revenue | 3 | pending |
| line-1 | line-1-0512-0579-s005072 | forward | revenue | 3 | pending |
| line-1 | line-1-0512-0579-s005072 | reverse | revenue | 2 | pending |
| line-1 | line-1-0520-0539-s007143 | forward | revenue | 2 | pending |
| line-1 | line-1-0520-0539-s007143 | reverse | revenue | 2 | pending |
| line-1 | line-1-0423-0452-s010266 | reverse | revenue | 2 | pending |
| line-1 | line-1-0512-0579-s005072 | reverse | spare | 1 | pending |
| line-1 | line-1-0520-0539-s007143 | forward | spare | 1 | pending |
| line-1 | line-1-0520-0539-s007143 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**13 trainsets exceed the reference platform envelope**, requiring **773.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0373-0716-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0423-0452-s010266 | 2 | 2 | 0 | 0.0 |
| line-1-0433-0610-s003011 | 6 | 2 | 4 | 238.0 |
| line-1-0512-0579-s005072 | 6 | 2 | 4 | 238.0 |
| line-1-0520-0539-s007143 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Quelimane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
