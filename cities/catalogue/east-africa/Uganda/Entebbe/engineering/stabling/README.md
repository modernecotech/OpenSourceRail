# Station and depot overnight allocation

Plan: **34 trainsets at stations + 44 at depots = 78 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0000-0751-s015542 | 44 | 2,156.0 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0040-0699-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0122-0602-s003011 | station | forward | revenue | 1 |
| line-1 | line-1-0122-0602-s003011 | station | reverse | revenue | 1 |
| line-1 | line-1-0227-0509-s006408 | station | forward | revenue | 1 |
| line-1 | line-1-0227-0509-s006408 | station | reverse | revenue | 1 |
| line-1 | line-1-0284-0443-s009010 | station | forward | revenue | 1 |
| line-1 | line-1-0284-0443-s009010 | station | reverse | revenue | 1 |
| line-1 | line-1-0323-0219-s015490 | station | reverse | revenue | 2 |
| line-1 | line-1-0354-0386-s011309 | station | forward | revenue | 1 |
| line-1 | line-1-0354-0386-s011309 | station | reverse | revenue | 1 |
| line-1 | line-1-0362-0294-s013409 | station | forward | revenue | 1 |
| line-1 | line-1-0362-0294-s013409 | station | reverse | revenue | 1 |
| line-2 | line-2-0222-0297-s007889 | station | reverse | revenue | 2 |
| line-2 | line-2-0278-0362-s005744 | station | forward | revenue | 1 |
| line-2 | line-2-0278-0362-s005744 | station | reverse | revenue | 1 |
| line-2 | line-2-0354-0386-s003585 | station | forward | revenue | 1 |
| line-2 | line-2-0354-0386-s003585 | station | reverse | revenue | 1 |
| line-2 | line-2-0437-0275-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0000-0751-s015542 | station | reverse | revenue | 2 |
| line-3 | line-3-0154-0560-s009023 | station | forward | revenue | 1 |
| line-3 | line-3-0154-0560-s009023 | station | reverse | revenue | 1 |
| line-3 | line-3-0281-0508-s006007 | station | forward | revenue | 1 |
| line-3 | line-3-0281-0508-s006007 | station | reverse | revenue | 1 |
| line-3 | line-3-0353-0460-s004120 | station | forward | revenue | 1 |
| line-3 | line-3-0353-0460-s004120 | station | reverse | revenue | 1 |
| line-3 | line-3-0354-0386-s002233 | station | forward | revenue | 1 |
| line-3 | line-3-0354-0386-s002233 | station | reverse | revenue | 1 |
| line-3 | line-3-0433-0385-s000000 | station | forward | revenue | 2 |
| line-1 | line-3-0000-0751-s015542 | depot | — | revenue | 13 |
| line-1 | line-3-0000-0751-s015542 | depot | — | spare | 2 |
| line-1 | line-3-0000-0751-s015542 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0000-0751-s015542 | depot | — | revenue | 7 |
| line-2 | line-3-0000-0751-s015542 | depot | — | spare | 1 |
| line-2 | line-3-0000-0751-s015542 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0000-0751-s015542 | depot | — | revenue | 16 |
| line-3 | line-3-0000-0751-s015542 | depot | — | spare | 2 |
| line-3 | line-3-0000-0751-s015542 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (16 trains), line-2 (9 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **78 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **70 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **44 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0040-0699-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0122-0602-s003011 | forward | revenue | 3 | pending |
| line-1 | line-1-0122-0602-s003011 | reverse | revenue | 3 | pending |
| line-1 | line-1-0227-0509-s006408 | forward | revenue | 2 | pending |
| line-1 | line-1-0227-0509-s006408 | reverse | revenue | 2 | pending |
| line-1 | line-1-0284-0443-s009010 | forward | revenue | 2 | pending |
| line-1 | line-1-0284-0443-s009010 | reverse | revenue | 2 | pending |
| line-1 | line-1-0354-0386-s011309 | forward | revenue | 2 | pending |
| line-1 | line-1-0354-0386-s011309 | reverse | revenue | 2 | pending |
| line-1 | line-1-0362-0294-s013409 | forward | revenue | 2 | pending |
| line-1 | line-1-0362-0294-s013409 | reverse | revenue | 2 | pending |
| line-1 | line-1-0323-0219-s015490 | reverse | revenue | 2 | pending |
| line-1 | line-1-0227-0509-s006408 | forward | spare | 1 | pending |
| line-1 | line-1-0227-0509-s006408 | reverse | spare | 1 | pending |
| line-1 | line-1-0284-0443-s009010 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0437-0275-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0354-0386-s003585 | forward | revenue | 3 | pending |
| line-2 | line-2-0354-0386-s003585 | reverse | revenue | 3 | pending |
| line-2 | line-2-0278-0362-s005744 | forward | revenue | 2 | pending |
| line-2 | line-2-0278-0362-s005744 | reverse | revenue | 2 | pending |
| line-2 | line-2-0222-0297-s007889 | reverse | revenue | 2 | pending |
| line-2 | line-2-0278-0362-s005744 | forward | spare | 1 | pending |
| line-2 | line-2-0278-0362-s005744 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0433-0385-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0354-0386-s002233 | forward | revenue | 3 | pending |
| line-3 | line-3-0354-0386-s002233 | reverse | revenue | 3 | pending |
| line-3 | line-3-0353-0460-s004120 | forward | revenue | 3 | pending |
| line-3 | line-3-0353-0460-s004120 | reverse | revenue | 3 | pending |
| line-3 | line-3-0281-0508-s006007 | forward | revenue | 3 | pending |
| line-3 | line-3-0281-0508-s006007 | reverse | revenue | 3 | pending |
| line-3 | line-3-0154-0560-s009023 | forward | revenue | 3 | pending |
| line-3 | line-3-0154-0560-s009023 | reverse | revenue | 2 | pending |
| line-3 | line-3-0000-0751-s015542 | reverse | revenue | 2 | pending |
| line-3 | line-3-0154-0560-s009023 | reverse | spare | 1 | pending |
| line-3 | line-3-0000-0751-s015542 | reverse | spare | 1 | pending |
| line-3 | line-3-0433-0385-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**38 trainsets exceed the reference platform envelope**, requiring **1,862.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0040-0699-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0122-0602-s003011 | 6 | 2 | 4 | 196.0 |
| line-1-0227-0509-s006408 | 6 | 2 | 4 | 196.0 |
| line-1-0284-0443-s009010 | 5 | 2 | 3 | 147.0 |
| line-1-0323-0219-s015490 | 2 | 2 | 0 | 0.0 |
| line-1-0354-0386-s011309 | 4 | 4 | 0 | 0.0 |
| line-1-0362-0294-s013409 | 4 | 2 | 2 | 98.0 |
| line-2-0222-0297-s007889 | 2 | 2 | 0 | 0.0 |
| line-2-0278-0362-s005744 | 6 | 2 | 4 | 196.0 |
| line-2-0354-0386-s003585 | 6 | 4 | 2 | 98.0 |
| line-2-0437-0275-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0000-0751-s015542 | 3 | 2 | 1 | 49.0 |
| line-3-0154-0560-s009023 | 6 | 2 | 4 | 196.0 |
| line-3-0281-0508-s006007 | 6 | 2 | 4 | 196.0 |
| line-3-0353-0460-s004120 | 6 | 2 | 4 | 196.0 |
| line-3-0354-0386-s002233 | 6 | 4 | 2 | 98.0 |
| line-3-0433-0385-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Entebbe/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
