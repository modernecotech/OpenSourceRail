# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 52 at depots = 96 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0433-0474-s000000 | line-1 | declared-depot | 8 | 392.0 | 3 |
| line-2-0226-0282-s000000 | line-2 | declared-depot | 5 | 245.0 | 2 |
| line-3-0375-0406-s008508 | line-3 | declared-depot | 10 | 490.0 | 3 |
| line-4-0338-0391-s000000 | line-4 | declared-depot | 5 | 245.0 | 2 |
| line-5-0274-0217-s000000 | line-5 | declared-depot | 8 | 392.0 | 2 |
| line-6-0209-0337-s000000 | line-6 | declared-depot | 11 | 539.0 | 3 |
| line-7-0307-0377-s000000 | line-7 | declared-depot | 5 | 245.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0274-0217-s006738 | station | reverse | revenue | 2 |
| line-1 | line-1-0319-0289-s004844 | station | forward | revenue | 1 |
| line-1 | line-1-0319-0289-s004844 | station | reverse | revenue | 1 |
| line-1 | line-1-0364-0362-s002940 | station | forward | revenue | 1 |
| line-1 | line-1-0364-0362-s002940 | station | reverse | revenue | 1 |
| line-1 | line-1-0433-0474-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0226-0282-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0319-0289-s001918 | station | forward | revenue | 1 |
| line-2 | line-2-0319-0289-s001918 | station | reverse | revenue | 1 |
| line-2 | line-2-0369-0293-s002951 | station | reverse | revenue | 2 |
| line-3 | line-3-0027-0326-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0209-0337-s004546 | station | forward | revenue | 1 |
| line-3 | line-3-0209-0337-s004546 | station | reverse | revenue | 1 |
| line-3 | line-3-0307-0377-s006884 | station | forward | revenue | 1 |
| line-3 | line-3-0307-0377-s006884 | station | reverse | revenue | 1 |
| line-3 | line-3-0338-0391-s007632 | station | forward | revenue | 1 |
| line-3 | line-3-0338-0391-s007632 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0406-s008508 | station | reverse | revenue | 2 |
| line-4 | line-4-0338-0391-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0338-0511-s002798 | station | reverse | revenue | 2 |
| line-5 | line-5-0274-0217-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0288-0037-s005488 | station | reverse | revenue | 2 |
| line-5 | line-5-0361-0062-s003821 | station | forward | revenue | 1 |
| line-5 | line-5-0361-0062-s003821 | station | reverse | revenue | 1 |
| line-6 | line-6-0209-0337-s000000 | station | forward | revenue | 2 |
| line-6 | line-6-0264-0538-s005840 | station | reverse | revenue | 2 |
| line-7 | line-7-0307-0377-s000000 | station | forward | revenue | 2 |
| line-7 | line-7-0364-0362-s001455 | station | forward | revenue | 1 |
| line-7 | line-7-0364-0362-s001455 | station | reverse | revenue | 1 |
| line-7 | line-7-0464-0390-s003687 | station | reverse | revenue | 2 |
| line-1 | line-1-0433-0474-s000000 | depot | — | revenue | 6 |
| line-1 | line-1-0433-0474-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0433-0474-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0226-0282-s000000 | depot | — | revenue | 3 |
| line-2 | line-2-0226-0282-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0226-0282-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0375-0406-s008508 | depot | — | revenue | 8 |
| line-3 | line-3-0375-0406-s008508 | depot | — | spare | 1 |
| line-3 | line-3-0375-0406-s008508 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0338-0391-s000000 | depot | — | revenue | 3 |
| line-4 | line-4-0338-0391-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0338-0391-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0274-0217-s000000 | depot | — | revenue | 6 |
| line-5 | line-5-0274-0217-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0274-0217-s000000 | depot | — | cold_reserve | 1 |
| line-6 | line-6-0209-0337-s000000 | depot | — | revenue | 9 |
| line-6 | line-6-0209-0337-s000000 | depot | — | spare | 1 |
| line-6 | line-6-0209-0337-s000000 | depot | — | cold_reserve | 1 |
| line-7 | line-7-0307-0377-s000000 | depot | — | revenue | 3 |
| line-7 | line-7-0307-0377-s000000 | depot | — | spare | 1 |
| line-7 | line-7-0307-0377-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kisii-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **96 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **82 revenue, 7 spare, 7 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **52 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0433-0474-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0364-0362-s002940 | forward | revenue | 3 | pending |
| line-1 | line-1-0364-0362-s002940 | reverse | revenue | 2 | pending |
| line-1 | line-1-0319-0289-s004844 | forward | revenue | 2 | pending |
| line-1 | line-1-0319-0289-s004844 | reverse | revenue | 2 | pending |
| line-1 | line-1-0274-0217-s006738 | reverse | revenue | 2 | pending |
| line-1 | line-1-0364-0362-s002940 | reverse | spare | 1 | pending |
| line-1 | line-1-0319-0289-s004844 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0226-0282-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0319-0289-s001918 | forward | revenue | 2 | pending |
| line-2 | line-2-0319-0289-s001918 | reverse | revenue | 2 | pending |
| line-2 | line-2-0369-0293-s002951 | reverse | revenue | 2 | pending |
| line-2 | line-2-0319-0289-s001918 | forward | spare | 1 | pending |
| line-2 | line-2-0319-0289-s001918 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0027-0326-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0209-0337-s004546 | forward | revenue | 3 | pending |
| line-3 | line-3-0209-0337-s004546 | reverse | revenue | 2 | pending |
| line-3 | line-3-0307-0377-s006884 | forward | revenue | 2 | pending |
| line-3 | line-3-0307-0377-s006884 | reverse | revenue | 2 | pending |
| line-3 | line-3-0338-0391-s007632 | forward | revenue | 2 | pending |
| line-3 | line-3-0338-0391-s007632 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-0406-s008508 | reverse | revenue | 2 | pending |
| line-3 | line-3-0209-0337-s004546 | reverse | spare | 1 | pending |
| line-3 | line-3-0307-0377-s006884 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0338-0391-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0338-0511-s002798 | reverse | revenue | 3 | pending |
| line-4 | line-4-0338-0511-s002798 | reverse | spare | 1 | pending |
| line-4 | line-4-0338-0391-s000000 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0274-0217-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0361-0062-s003821 | forward | revenue | 3 | pending |
| line-5 | line-5-0361-0062-s003821 | reverse | revenue | 3 | pending |
| line-5 | line-5-0288-0037-s005488 | reverse | revenue | 3 | pending |
| line-5 | line-5-0274-0217-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0361-0062-s003821 | forward | cold_reserve | 1 | pending |
| line-6 | line-6-0209-0337-s000000 | forward | revenue | 7 | pending |
| line-6 | line-6-0264-0538-s005840 | reverse | revenue | 6 | pending |
| line-6 | line-6-0264-0538-s005840 | reverse | spare | 1 | pending |
| line-6 | line-6-0209-0337-s000000 | forward | cold_reserve | 1 | pending |
| line-7 | line-7-0307-0377-s000000 | forward | revenue | 3 | pending |
| line-7 | line-7-0364-0362-s001455 | forward | revenue | 2 | pending |
| line-7 | line-7-0364-0362-s001455 | reverse | revenue | 2 | pending |
| line-7 | line-7-0464-0390-s003687 | reverse | revenue | 2 | pending |
| line-7 | line-7-0364-0362-s001455 | forward | spare | 1 | pending |
| line-7 | line-7-0364-0362-s001455 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**38 trainsets exceed the reference platform envelope**, requiring **1,862.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0274-0217-s006738 | 2 | 2 | 0 | 0.0 |
| line-1-0319-0289-s004844 | 5 | 4 | 1 | 49.0 |
| line-1-0364-0362-s002940 | 6 | 4 | 2 | 98.0 |
| line-1-0433-0474-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0226-0282-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0319-0289-s001918 | 6 | 4 | 2 | 98.0 |
| line-2-0369-0293-s002951 | 2 | 2 | 0 | 0.0 |
| line-3-0027-0326-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0209-0337-s004546 | 6 | 4 | 2 | 98.0 |
| line-3-0307-0377-s006884 | 5 | 4 | 1 | 49.0 |
| line-3-0338-0391-s007632 | 4 | 4 | 0 | 0.0 |
| line-3-0375-0406-s008508 | 2 | 2 | 0 | 0.0 |
| line-4-0338-0391-s000000 | 5 | 2 | 3 | 147.0 |
| line-4-0338-0511-s002798 | 4 | 2 | 2 | 98.0 |
| line-5-0274-0217-s000000 | 4 | 2 | 2 | 98.0 |
| line-5-0288-0037-s005488 | 3 | 2 | 1 | 49.0 |
| line-5-0361-0062-s003821 | 7 | 2 | 5 | 245.0 |
| line-6-0209-0337-s000000 | 8 | 2 | 6 | 294.0 |
| line-6-0264-0538-s005840 | 7 | 2 | 5 | 245.0 |
| line-7-0307-0377-s000000 | 3 | 2 | 1 | 49.0 |
| line-7-0364-0362-s001455 | 6 | 4 | 2 | 98.0 |
| line-7-0464-0390-s003687 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisii/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
