# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 171 at depots = 215 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0215-0272-s025586 | line-1 | declared-depot | 60 | 3,570.0 | 11 |
| line-2-0980-0761-s000000 | line-2 | declared-depot | 56 | 3,332.0 | 10 |
| line-3-0198-0413-s000000 | line-3 | declared-depot | 55 | 3,272.5 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0272-s025586 | station | reverse | revenue | 2 |
| line-1 | line-1-0434-0460-s019122 | station | forward | revenue | 1 |
| line-1 | line-1-0434-0460-s019122 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0554-s015813 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0554-s015813 | station | reverse | revenue | 1 |
| line-1 | line-1-0591-0592-s014478 | station | forward | revenue | 1 |
| line-1 | line-1-0591-0592-s014478 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0679-s011451 | station | forward | revenue | 1 |
| line-1 | line-1-0694-0679-s011451 | station | reverse | revenue | 1 |
| line-1 | line-1-0796-0765-s008441 | station | forward | revenue | 1 |
| line-1 | line-1-0796-0765-s008441 | station | reverse | revenue | 1 |
| line-1 | line-1-0900-0838-s005432 | station | forward | revenue | 1 |
| line-1 | line-1-0900-0838-s005432 | station | reverse | revenue | 1 |
| line-1 | line-1-1093-0994-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0284-0038-s023099 | station | reverse | revenue | 2 |
| line-2 | line-2-0512-0291-s015833 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0291-s015833 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0375-s013413 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0375-s013413 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0478-s010403 | station | forward | revenue | 1 |
| line-2 | line-2-0665-0478-s010403 | station | reverse | revenue | 1 |
| line-2 | line-2-0749-0581-s007401 | station | forward | revenue | 1 |
| line-2 | line-2-0749-0581-s007401 | station | reverse | revenue | 1 |
| line-2 | line-2-0834-0685-s004383 | station | forward | revenue | 1 |
| line-2 | line-2-0834-0685-s004383 | station | reverse | revenue | 1 |
| line-2 | line-2-0980-0761-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0198-0413-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0316-0479-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0316-0479-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0424-0558-s006034 | station | forward | revenue | 1 |
| line-3 | line-3-0424-0558-s006034 | station | reverse | revenue | 1 |
| line-3 | line-3-0532-0638-s009056 | station | forward | revenue | 1 |
| line-3 | line-3-0532-0638-s009056 | station | reverse | revenue | 1 |
| line-3 | line-3-0641-0718-s012063 | station | forward | revenue | 1 |
| line-3 | line-3-0641-0718-s012063 | station | reverse | revenue | 1 |
| line-3 | line-3-0839-0864-s017537 | station | forward | revenue | 1 |
| line-3 | line-3-0839-0864-s017537 | station | reverse | revenue | 1 |
| line-3 | line-3-1002-1014-s023004 | station | reverse | revenue | 2 |
| line-1 | line-1-0215-0272-s025586 | depot | — | revenue | 53 |
| line-1 | line-1-0215-0272-s025586 | depot | — | spare | 6 |
| line-1 | line-1-0215-0272-s025586 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0980-0761-s000000 | depot | — | revenue | 49 |
| line-2 | line-2-0980-0761-s000000 | depot | — | spare | 6 |
| line-2 | line-2-0980-0761-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0198-0413-s000000 | depot | — | revenue | 48 |
| line-3 | line-3-0198-0413-s000000 | depot | — | spare | 6 |
| line-3 | line-3-0198-0413-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/khamis-mushait-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **215 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **194 revenue, 18 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **171 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1093-0994-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0900-0838-s005432 | forward | revenue | 5 | pending |
| line-1 | line-1-0900-0838-s005432 | reverse | revenue | 5 | pending |
| line-1 | line-1-0796-0765-s008441 | forward | revenue | 5 | pending |
| line-1 | line-1-0796-0765-s008441 | reverse | revenue | 5 | pending |
| line-1 | line-1-0694-0679-s011451 | forward | revenue | 5 | pending |
| line-1 | line-1-0694-0679-s011451 | reverse | revenue | 5 | pending |
| line-1 | line-1-0591-0592-s014478 | forward | revenue | 5 | pending |
| line-1 | line-1-0591-0592-s014478 | reverse | revenue | 5 | pending |
| line-1 | line-1-0547-0554-s015813 | forward | revenue | 5 | pending |
| line-1 | line-1-0547-0554-s015813 | reverse | revenue | 5 | pending |
| line-1 | line-1-0434-0460-s019122 | forward | revenue | 5 | pending |
| line-1 | line-1-0434-0460-s019122 | reverse | revenue | 5 | pending |
| line-1 | line-1-0215-0272-s025586 | reverse | revenue | 4 | pending |
| line-1 | line-1-0215-0272-s025586 | reverse | spare | 1 | pending |
| line-1 | line-1-1093-0994-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0900-0838-s005432 | forward | spare | 1 | pending |
| line-1 | line-1-0900-0838-s005432 | reverse | spare | 1 | pending |
| line-1 | line-1-0796-0765-s008441 | forward | spare | 1 | pending |
| line-1 | line-1-0796-0765-s008441 | reverse | spare | 1 | pending |
| line-1 | line-1-0694-0679-s011451 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0980-0761-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0834-0685-s004383 | forward | revenue | 6 | pending |
| line-2 | line-2-0834-0685-s004383 | reverse | revenue | 6 | pending |
| line-2 | line-2-0749-0581-s007401 | forward | revenue | 5 | pending |
| line-2 | line-2-0749-0581-s007401 | reverse | revenue | 5 | pending |
| line-2 | line-2-0665-0478-s010403 | forward | revenue | 5 | pending |
| line-2 | line-2-0665-0478-s010403 | reverse | revenue | 5 | pending |
| line-2 | line-2-0580-0375-s013413 | forward | revenue | 5 | pending |
| line-2 | line-2-0580-0375-s013413 | reverse | revenue | 5 | pending |
| line-2 | line-2-0512-0291-s015833 | forward | revenue | 5 | pending |
| line-2 | line-2-0512-0291-s015833 | reverse | revenue | 5 | pending |
| line-2 | line-2-0284-0038-s023099 | reverse | revenue | 5 | pending |
| line-2 | line-2-0749-0581-s007401 | forward | spare | 1 | pending |
| line-2 | line-2-0749-0581-s007401 | reverse | spare | 1 | pending |
| line-2 | line-2-0665-0478-s010403 | forward | spare | 1 | pending |
| line-2 | line-2-0665-0478-s010403 | reverse | spare | 1 | pending |
| line-2 | line-2-0580-0375-s013413 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0375-s013413 | reverse | spare | 1 | pending |
| line-2 | line-2-0512-0291-s015833 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0198-0413-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0316-0479-s003009 | forward | revenue | 6 | pending |
| line-3 | line-3-0316-0479-s003009 | reverse | revenue | 5 | pending |
| line-3 | line-3-0424-0558-s006034 | forward | revenue | 5 | pending |
| line-3 | line-3-0424-0558-s006034 | reverse | revenue | 5 | pending |
| line-3 | line-3-0532-0638-s009056 | forward | revenue | 5 | pending |
| line-3 | line-3-0532-0638-s009056 | reverse | revenue | 5 | pending |
| line-3 | line-3-0641-0718-s012063 | forward | revenue | 5 | pending |
| line-3 | line-3-0641-0718-s012063 | reverse | revenue | 5 | pending |
| line-3 | line-3-0839-0864-s017537 | forward | revenue | 5 | pending |
| line-3 | line-3-0839-0864-s017537 | reverse | revenue | 5 | pending |
| line-3 | line-3-1002-1014-s023004 | reverse | revenue | 5 | pending |
| line-3 | line-3-0316-0479-s003009 | reverse | spare | 1 | pending |
| line-3 | line-3-0424-0558-s006034 | forward | spare | 1 | pending |
| line-3 | line-3-0424-0558-s006034 | reverse | spare | 1 | pending |
| line-3 | line-3-0532-0638-s009056 | forward | spare | 1 | pending |
| line-3 | line-3-0532-0638-s009056 | reverse | spare | 1 | pending |
| line-3 | line-3-0641-0718-s012063 | forward | spare | 1 | pending |
| line-3 | line-3-0641-0718-s012063 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**171 trainsets exceed the reference platform envelope**, requiring **10,174.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0272-s025586 | 5 | 2 | 3 | 178.5 |
| line-1-0434-0460-s019122 | 10 | 2 | 8 | 476.0 |
| line-1-0547-0554-s015813 | 10 | 2 | 8 | 476.0 |
| line-1-0591-0592-s014478 | 10 | 2 | 8 | 476.0 |
| line-1-0694-0679-s011451 | 11 | 2 | 9 | 535.5 |
| line-1-0796-0765-s008441 | 12 | 2 | 10 | 595.0 |
| line-1-0900-0838-s005432 | 12 | 2 | 10 | 595.0 |
| line-1-1093-0994-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0284-0038-s023099 | 5 | 2 | 3 | 178.5 |
| line-2-0512-0291-s015833 | 11 | 2 | 9 | 535.5 |
| line-2-0580-0375-s013413 | 12 | 2 | 10 | 595.0 |
| line-2-0665-0478-s010403 | 12 | 2 | 10 | 595.0 |
| line-2-0749-0581-s007401 | 12 | 2 | 10 | 595.0 |
| line-2-0834-0685-s004383 | 12 | 2 | 10 | 595.0 |
| line-2-0980-0761-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0198-0413-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0316-0479-s003009 | 12 | 2 | 10 | 595.0 |
| line-3-0424-0558-s006034 | 12 | 2 | 10 | 595.0 |
| line-3-0532-0638-s009056 | 12 | 2 | 10 | 595.0 |
| line-3-0641-0718-s012063 | 12 | 2 | 10 | 595.0 |
| line-3-0839-0864-s017537 | 10 | 2 | 8 | 476.0 |
| line-3-1002-1014-s023004 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Khamis-Mushait/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
