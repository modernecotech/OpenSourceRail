# Station and depot overnight allocation

Plan: **26 trainsets at stations + 40 at depots = 66 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0027-0511-s011741 | 40 | 1,960.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0164-0517-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0318-0426-s004410 | station | forward | revenue | 1 |
| line-1 | line-1-0318-0426-s004410 | station | reverse | revenue | 1 |
| line-1 | line-1-0373-0374-s006126 | station | forward | revenue | 1 |
| line-1 | line-1-0373-0374-s006126 | station | reverse | revenue | 1 |
| line-1 | line-1-0411-0321-s007771 | station | forward | revenue | 1 |
| line-1 | line-1-0411-0321-s007771 | station | reverse | revenue | 1 |
| line-1 | line-1-0466-0286-s009394 | station | reverse | revenue | 2 |
| line-2 | line-2-0027-0511-s011741 | station | reverse | revenue | 2 |
| line-2 | line-2-0269-0351-s004707 | station | forward | revenue | 1 |
| line-2 | line-2-0269-0351-s004707 | station | reverse | revenue | 1 |
| line-2 | line-2-0373-0374-s002356 | station | forward | revenue | 1 |
| line-2 | line-2-0373-0374-s002356 | station | reverse | revenue | 1 |
| line-2 | line-2-0383-0281-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0045-0480-s009080 | station | reverse | revenue | 2 |
| line-3 | line-3-0296-0391-s003003 | station | forward | revenue | 1 |
| line-3 | line-3-0296-0391-s003003 | station | reverse | revenue | 1 |
| line-3 | line-3-0373-0374-s001271 | station | forward | revenue | 1 |
| line-3 | line-3-0373-0374-s001271 | station | reverse | revenue | 1 |
| line-3 | line-3-0421-0361-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0027-0511-s011741 | depot | — | revenue | 8 |
| line-1 | line-2-0027-0511-s011741 | depot | — | spare | 1 |
| line-1 | line-2-0027-0511-s011741 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0027-0511-s011741 | depot | — | revenue | 15 |
| line-2 | line-2-0027-0511-s011741 | depot | — | spare | 2 |
| line-2 | line-2-0027-0511-s011741 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0027-0511-s011741 | depot | — | revenue | 10 |
| line-3 | line-2-0027-0511-s011741 | depot | — | spare | 1 |
| line-3 | line-2-0027-0511-s011741 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (10 trains), line-3 (12 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **66 trainsets at 13 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **59 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **40 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0164-0517-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0318-0426-s004410 | forward | revenue | 3 | pending |
| line-1 | line-1-0318-0426-s004410 | reverse | revenue | 2 | pending |
| line-1 | line-1-0373-0374-s006126 | forward | revenue | 2 | pending |
| line-1 | line-1-0373-0374-s006126 | reverse | revenue | 2 | pending |
| line-1 | line-1-0411-0321-s007771 | forward | revenue | 2 | pending |
| line-1 | line-1-0411-0321-s007771 | reverse | revenue | 2 | pending |
| line-1 | line-1-0466-0286-s009394 | reverse | revenue | 2 | pending |
| line-1 | line-1-0318-0426-s004410 | reverse | spare | 1 | pending |
| line-1 | line-1-0373-0374-s006126 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0383-0281-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0373-0374-s002356 | forward | revenue | 4 | pending |
| line-2 | line-2-0373-0374-s002356 | reverse | revenue | 4 | pending |
| line-2 | line-2-0269-0351-s004707 | forward | revenue | 4 | pending |
| line-2 | line-2-0269-0351-s004707 | reverse | revenue | 4 | pending |
| line-2 | line-2-0027-0511-s011741 | reverse | revenue | 3 | pending |
| line-2 | line-2-0027-0511-s011741 | reverse | spare | 1 | pending |
| line-2 | line-2-0383-0281-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0373-0374-s002356 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0421-0361-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0373-0374-s001271 | forward | revenue | 3 | pending |
| line-3 | line-3-0373-0374-s001271 | reverse | revenue | 3 | pending |
| line-3 | line-3-0296-0391-s003003 | forward | revenue | 3 | pending |
| line-3 | line-3-0296-0391-s003003 | reverse | revenue | 3 | pending |
| line-3 | line-3-0045-0480-s009080 | reverse | revenue | 3 | pending |
| line-3 | line-3-0421-0361-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0373-0374-s001271 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**34 trainsets exceed the reference platform envelope**, requiring **1,666.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0164-0517-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0318-0426-s004410 | 6 | 2 | 4 | 196.0 |
| line-1-0373-0374-s006126 | 5 | 4 | 1 | 49.0 |
| line-1-0411-0321-s007771 | 4 | 2 | 2 | 98.0 |
| line-1-0466-0286-s009394 | 2 | 2 | 0 | 0.0 |
| line-2-0027-0511-s011741 | 4 | 2 | 2 | 98.0 |
| line-2-0269-0351-s004707 | 8 | 2 | 6 | 294.0 |
| line-2-0373-0374-s002356 | 9 | 4 | 5 | 245.0 |
| line-2-0383-0281-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0045-0480-s009080 | 3 | 2 | 1 | 49.0 |
| line-3-0296-0391-s003003 | 6 | 2 | 4 | 196.0 |
| line-3-0373-0374-s001271 | 7 | 4 | 3 | 147.0 |
| line-3-0421-0361-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Beni-Mellal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
