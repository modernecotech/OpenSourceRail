# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 55 at depots = 97 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0055-0553-s012782 | line-1 | declared-depot | 15 | 735.0 | 4 |
| line-2-0499-0328-s000000 | line-2 | declared-depot | 5 | 245.0 | 2 |
| line-3-0380-0462-s000000 | line-3 | declared-depot | 17 | 833.0 | 4 |
| line-4-0370-0415-s000000 | line-4 | declared-depot | 5 | 245.0 | 2 |
| line-5-0568-0433-s000000 | line-5 | declared-depot | 6 | 294.0 | 2 |
| line-6-0585-0374-s000000 | line-6 | declared-depot | 7 | 343.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0055-0553-s012782 | station | reverse | revenue | 2 |
| line-1 | line-1-0179-0452-s008801 | station | forward | revenue | 1 |
| line-1 | line-1-0179-0452-s008801 | station | reverse | revenue | 1 |
| line-1 | line-1-0253-0438-s007205 | station | forward | revenue | 1 |
| line-1 | line-1-0253-0438-s007205 | station | reverse | revenue | 1 |
| line-1 | line-1-0370-0415-s004651 | station | forward | revenue | 1 |
| line-1 | line-1-0370-0415-s004651 | station | reverse | revenue | 1 |
| line-1 | line-1-0474-0395-s002394 | station | forward | revenue | 1 |
| line-1 | line-1-0474-0395-s002394 | station | reverse | revenue | 1 |
| line-1 | line-1-0536-0384-s001069 | station | forward | revenue | 1 |
| line-1 | line-1-0536-0384-s001069 | station | reverse | revenue | 1 |
| line-1 | line-1-0585-0374-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0499-0328-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0536-0384-s001494 | station | forward | revenue | 1 |
| line-2 | line-2-0536-0384-s001494 | station | reverse | revenue | 1 |
| line-2 | line-2-0568-0433-s002824 | station | forward | revenue | 1 |
| line-2 | line-2-0568-0433-s002824 | station | reverse | revenue | 1 |
| line-2 | line-2-0587-0461-s003588 | station | reverse | revenue | 2 |
| line-3 | line-3-0041-0657-s009072 | station | reverse | revenue | 2 |
| line-3 | line-3-0289-0520-s002394 | station | forward | revenue | 1 |
| line-3 | line-3-0289-0520-s002394 | station | reverse | revenue | 1 |
| line-3 | line-3-0380-0462-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0370-0415-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0439-0340-s002849 | station | reverse | revenue | 2 |
| line-5 | line-5-0385-0536-s004513 | station | reverse | revenue | 2 |
| line-5 | line-5-0463-0487-s002547 | station | forward | revenue | 1 |
| line-5 | line-5-0463-0487-s002547 | station | reverse | revenue | 1 |
| line-5 | line-5-0568-0433-s000000 | station | forward | revenue | 2 |
| line-6 | line-6-0585-0374-s000000 | station | forward | revenue | 2 |
| line-6 | line-6-0686-0235-s003617 | station | reverse | revenue | 2 |
| line-1 | line-1-0055-0553-s012782 | depot | — | revenue | 12 |
| line-1 | line-1-0055-0553-s012782 | depot | — | spare | 2 |
| line-1 | line-1-0055-0553-s012782 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0499-0328-s000000 | depot | — | revenue | 3 |
| line-2 | line-2-0499-0328-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0499-0328-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0380-0462-s000000 | depot | — | revenue | 14 |
| line-3 | line-3-0380-0462-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0380-0462-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0370-0415-s000000 | depot | — | revenue | 3 |
| line-4 | line-4-0370-0415-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0370-0415-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0568-0433-s000000 | depot | — | revenue | 4 |
| line-5 | line-5-0568-0433-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0568-0433-s000000 | depot | — | cold_reserve | 1 |
| line-6 | line-6-0585-0374-s000000 | depot | — | revenue | 5 |
| line-6 | line-6-0585-0374-s000000 | depot | — | spare | 1 |
| line-6 | line-6-0585-0374-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sidon-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **97 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 8 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **55 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0585-0374-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0536-0384-s001069 | forward | revenue | 3 | pending |
| line-1 | line-1-0536-0384-s001069 | reverse | revenue | 2 | pending |
| line-1 | line-1-0474-0395-s002394 | forward | revenue | 2 | pending |
| line-1 | line-1-0474-0395-s002394 | reverse | revenue | 2 | pending |
| line-1 | line-1-0370-0415-s004651 | forward | revenue | 2 | pending |
| line-1 | line-1-0370-0415-s004651 | reverse | revenue | 2 | pending |
| line-1 | line-1-0253-0438-s007205 | forward | revenue | 2 | pending |
| line-1 | line-1-0253-0438-s007205 | reverse | revenue | 2 | pending |
| line-1 | line-1-0179-0452-s008801 | forward | revenue | 2 | pending |
| line-1 | line-1-0179-0452-s008801 | reverse | revenue | 2 | pending |
| line-1 | line-1-0055-0553-s012782 | reverse | revenue | 2 | pending |
| line-1 | line-1-0536-0384-s001069 | reverse | spare | 1 | pending |
| line-1 | line-1-0474-0395-s002394 | forward | spare | 1 | pending |
| line-1 | line-1-0474-0395-s002394 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0499-0328-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0536-0384-s001494 | forward | revenue | 2 | pending |
| line-2 | line-2-0536-0384-s001494 | reverse | revenue | 2 | pending |
| line-2 | line-2-0568-0433-s002824 | forward | revenue | 2 | pending |
| line-2 | line-2-0568-0433-s002824 | reverse | revenue | 2 | pending |
| line-2 | line-2-0587-0461-s003588 | reverse | revenue | 1 | pending |
| line-2 | line-2-0587-0461-s003588 | reverse | spare | 1 | pending |
| line-2 | line-2-0499-0328-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0380-0462-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0289-0520-s002394 | forward | revenue | 5 | pending |
| line-3 | line-3-0289-0520-s002394 | reverse | revenue | 5 | pending |
| line-3 | line-3-0041-0657-s009072 | reverse | revenue | 5 | pending |
| line-3 | line-3-0380-0462-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0289-0520-s002394 | forward | spare | 1 | pending |
| line-3 | line-3-0289-0520-s002394 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0370-0415-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0439-0340-s002849 | reverse | revenue | 3 | pending |
| line-4 | line-4-0439-0340-s002849 | reverse | spare | 1 | pending |
| line-4 | line-4-0370-0415-s000000 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0568-0433-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0463-0487-s002547 | forward | revenue | 3 | pending |
| line-5 | line-5-0463-0487-s002547 | reverse | revenue | 2 | pending |
| line-5 | line-5-0385-0536-s004513 | reverse | revenue | 2 | pending |
| line-5 | line-5-0463-0487-s002547 | reverse | spare | 1 | pending |
| line-5 | line-5-0385-0536-s004513 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0585-0374-s000000 | forward | revenue | 5 | pending |
| line-6 | line-6-0686-0235-s003617 | reverse | revenue | 4 | pending |
| line-6 | line-6-0686-0235-s003617 | reverse | spare | 1 | pending |
| line-6 | line-6-0585-0374-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**47 trainsets exceed the reference platform envelope**, requiring **2,303.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0055-0553-s012782 | 2 | 2 | 0 | 0.0 |
| line-1-0179-0452-s008801 | 4 | 2 | 2 | 98.0 |
| line-1-0253-0438-s007205 | 4 | 2 | 2 | 98.0 |
| line-1-0370-0415-s004651 | 4 | 4 | 0 | 0.0 |
| line-1-0474-0395-s002394 | 6 | 2 | 4 | 196.0 |
| line-1-0536-0384-s001069 | 6 | 4 | 2 | 98.0 |
| line-1-0585-0374-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0499-0328-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0536-0384-s001494 | 4 | 4 | 0 | 0.0 |
| line-2-0568-0433-s002824 | 4 | 4 | 0 | 0.0 |
| line-2-0587-0461-s003588 | 2 | 2 | 0 | 0.0 |
| line-3-0041-0657-s009072 | 5 | 2 | 3 | 147.0 |
| line-3-0289-0520-s002394 | 12 | 2 | 10 | 490.0 |
| line-3-0380-0462-s000000 | 6 | 2 | 4 | 196.0 |
| line-4-0370-0415-s000000 | 5 | 2 | 3 | 147.0 |
| line-4-0439-0340-s002849 | 4 | 2 | 2 | 98.0 |
| line-5-0385-0536-s004513 | 3 | 2 | 1 | 49.0 |
| line-5-0463-0487-s002547 | 6 | 2 | 4 | 196.0 |
| line-5-0568-0433-s000000 | 3 | 2 | 1 | 49.0 |
| line-6-0585-0374-s000000 | 6 | 2 | 4 | 196.0 |
| line-6-0686-0235-s003617 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Lebanon/Sidon/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
