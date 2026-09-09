# Station and depot overnight allocation

Plan: **14 trainsets at stations + 23 at depots = 37 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0325-0358-s011140 | 23 | 1,127.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0172-0388-s005672 | station | reverse | revenue | 2 |
| line-1 | line-1-0290-0389-s003011 | station | forward | revenue | 1 |
| line-1 | line-1-0290-0389-s003011 | station | reverse | revenue | 1 |
| line-1 | line-1-0347-0350-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0325-0358-s011140 | station | reverse | revenue | 2 |
| line-2 | line-2-0332-0287-s006778 | station | forward | revenue | 1 |
| line-2 | line-2-0332-0287-s006778 | station | reverse | revenue | 1 |
| line-2 | line-2-0364-0009-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0373-0373-s009592 | station | forward | revenue | 1 |
| line-2 | line-2-0373-0373-s009592 | station | reverse | revenue | 1 |
| line-1 | line-2-0325-0358-s011140 | depot | — | revenue | 5 |
| line-1 | line-2-0325-0358-s011140 | depot | — | spare | 1 |
| line-1 | line-2-0325-0358-s011140 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0325-0358-s011140 | depot | — | revenue | 13 |
| line-2 | line-2-0325-0358-s011140 | depot | — | spare | 2 |
| line-2 | line-2-0325-0358-s011140 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (7 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **37 trainsets at 7 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **32 revenue, 3 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **14 positions**; **23 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **7 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0347-0350-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0290-0389-s003011 | forward | revenue | 3 | pending |
| line-1 | line-1-0290-0389-s003011 | reverse | revenue | 3 | pending |
| line-1 | line-1-0172-0388-s005672 | reverse | revenue | 2 | pending |
| line-1 | line-1-0172-0388-s005672 | reverse | spare | 1 | pending |
| line-1 | line-1-0347-0350-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0364-0009-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0332-0287-s006778 | forward | revenue | 4 | pending |
| line-2 | line-2-0332-0287-s006778 | reverse | revenue | 4 | pending |
| line-2 | line-2-0373-0373-s009592 | forward | revenue | 3 | pending |
| line-2 | line-2-0373-0373-s009592 | reverse | revenue | 3 | pending |
| line-2 | line-2-0325-0358-s011140 | reverse | revenue | 3 | pending |
| line-2 | line-2-0373-0373-s009592 | forward | spare | 1 | pending |
| line-2 | line-2-0373-0373-s009592 | reverse | spare | 1 | pending |
| line-2 | line-2-0325-0358-s011140 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**23 trainsets exceed the reference platform envelope**, requiring **1,127.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0172-0388-s005672 | 3 | 2 | 1 | 49.0 |
| line-1-0290-0389-s003011 | 6 | 2 | 4 | 196.0 |
| line-1-0347-0350-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0325-0358-s011140 | 4 | 2 | 2 | 98.0 |
| line-2-0332-0287-s006778 | 8 | 2 | 6 | 294.0 |
| line-2-0364-0009-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0373-0373-s009592 | 8 | 2 | 6 | 294.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Songea/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
