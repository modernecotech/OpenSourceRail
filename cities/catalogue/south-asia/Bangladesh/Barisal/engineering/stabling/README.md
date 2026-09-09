# Station and depot overnight allocation

Plan: **42 trainsets at stations + 88 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0879-0586-s015329 | line-1 | storage-at-existing-powered-service-point | 19 | 1,130.5 | 0 |
| line-2-1084-0450-s020325 | line-2 | storage-at-existing-powered-service-point | 27 | 1,606.5 | 0 |
| line-3-0761-0860-s025578 | line-3 | declared-depot | 42 | 2,499.0 | 20 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0279-0389-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0405-0476-s003756 | station | forward | revenue | 1 |
| line-1 | line-1-0405-0476-s003756 | station | reverse | revenue | 1 |
| line-1 | line-1-0473-0528-s005650 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0528-s005650 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0545-s007525 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0545-s007525 | station | reverse | revenue | 1 |
| line-1 | line-1-0614-0565-s008975 | station | forward | revenue | 1 |
| line-1 | line-1-0614-0565-s008975 | station | reverse | revenue | 1 |
| line-1 | line-1-0699-0614-s011097 | station | forward | revenue | 1 |
| line-1 | line-1-0699-0614-s011097 | station | reverse | revenue | 1 |
| line-1 | line-1-0793-0600-s013220 | station | forward | revenue | 1 |
| line-1 | line-1-0793-0600-s013220 | station | reverse | revenue | 1 |
| line-1 | line-1-0879-0586-s015329 | station | reverse | revenue | 2 |
| line-2 | line-2-0445-0723-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0471-0638-s003004 | station | forward | revenue | 1 |
| line-2 | line-2-0471-0638-s003004 | station | reverse | revenue | 1 |
| line-2 | line-2-0519-0578-s006019 | station | forward | revenue | 1 |
| line-2 | line-2-0519-0578-s006019 | station | reverse | revenue | 1 |
| line-2 | line-2-0555-0545-s007638 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0545-s007638 | station | reverse | revenue | 1 |
| line-2 | line-2-0673-0469-s010656 | station | forward | revenue | 1 |
| line-2 | line-2-0673-0469-s010656 | station | reverse | revenue | 1 |
| line-2 | line-2-0873-0483-s015548 | station | forward | revenue | 1 |
| line-2 | line-2-0873-0483-s015548 | station | reverse | revenue | 1 |
| line-2 | line-2-1084-0450-s020325 | station | reverse | revenue | 2 |
| line-3 | line-3-0078-0053-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0381-0365-s010502 | station | forward | revenue | 1 |
| line-3 | line-3-0381-0365-s010502 | station | reverse | revenue | 1 |
| line-3 | line-3-0518-0447-s014015 | station | forward | revenue | 1 |
| line-3 | line-3-0518-0447-s014015 | station | reverse | revenue | 1 |
| line-3 | line-3-0555-0545-s016442 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0545-s016442 | station | reverse | revenue | 1 |
| line-3 | line-3-0576-0675-s019388 | station | forward | revenue | 1 |
| line-3 | line-3-0576-0675-s019388 | station | reverse | revenue | 1 |
| line-3 | line-3-0761-0860-s025578 | station | reverse | revenue | 2 |
| line-1 | line-1-0879-0586-s015329 | depot | — | revenue | 15 |
| line-1 | line-1-0879-0586-s015329 | depot | — | spare | 3 |
| line-1 | line-1-0879-0586-s015329 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1084-0450-s020325 | depot | — | revenue | 23 |
| line-2 | line-2-1084-0450-s020325 | depot | — | spare | 3 |
| line-2 | line-2-1084-0450-s020325 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0761-0860-s025578 | depot | — | revenue | 37 |
| line-3 | line-3-0761-0860-s025578 | depot | — | spare | 4 |
| line-3 | line-3-0761-0860-s025578 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/barisal-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **117 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **88 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0279-0389-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0405-0476-s003756 | forward | revenue | 3 | pending |
| line-1 | line-1-0405-0476-s003756 | reverse | revenue | 3 | pending |
| line-1 | line-1-0473-0528-s005650 | forward | revenue | 2 | pending |
| line-1 | line-1-0473-0528-s005650 | reverse | revenue | 2 | pending |
| line-1 | line-1-0555-0545-s007525 | forward | revenue | 2 | pending |
| line-1 | line-1-0555-0545-s007525 | reverse | revenue | 2 | pending |
| line-1 | line-1-0614-0565-s008975 | forward | revenue | 2 | pending |
| line-1 | line-1-0614-0565-s008975 | reverse | revenue | 2 | pending |
| line-1 | line-1-0699-0614-s011097 | forward | revenue | 2 | pending |
| line-1 | line-1-0699-0614-s011097 | reverse | revenue | 2 | pending |
| line-1 | line-1-0793-0600-s013220 | forward | revenue | 2 | pending |
| line-1 | line-1-0793-0600-s013220 | reverse | revenue | 2 | pending |
| line-1 | line-1-0879-0586-s015329 | reverse | revenue | 2 | pending |
| line-1 | line-1-0473-0528-s005650 | forward | spare | 1 | pending |
| line-1 | line-1-0473-0528-s005650 | reverse | spare | 1 | pending |
| line-1 | line-1-0555-0545-s007525 | forward | spare | 1 | pending |
| line-1 | line-1-0555-0545-s007525 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0445-0723-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0471-0638-s003004 | forward | revenue | 3 | pending |
| line-2 | line-2-0471-0638-s003004 | reverse | revenue | 3 | pending |
| line-2 | line-2-0519-0578-s006019 | forward | revenue | 3 | pending |
| line-2 | line-2-0519-0578-s006019 | reverse | revenue | 3 | pending |
| line-2 | line-2-0555-0545-s007638 | forward | revenue | 3 | pending |
| line-2 | line-2-0555-0545-s007638 | reverse | revenue | 3 | pending |
| line-2 | line-2-0673-0469-s010656 | forward | revenue | 3 | pending |
| line-2 | line-2-0673-0469-s010656 | reverse | revenue | 3 | pending |
| line-2 | line-2-0873-0483-s015548 | forward | revenue | 3 | pending |
| line-2 | line-2-0873-0483-s015548 | reverse | revenue | 3 | pending |
| line-2 | line-2-1084-0450-s020325 | reverse | revenue | 3 | pending |
| line-2 | line-2-0471-0638-s003004 | forward | spare | 1 | pending |
| line-2 | line-2-0471-0638-s003004 | reverse | spare | 1 | pending |
| line-2 | line-2-0519-0578-s006019 | forward | spare | 1 | pending |
| line-2 | line-2-0519-0578-s006019 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0078-0053-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0381-0365-s010502 | forward | revenue | 5 | pending |
| line-3 | line-3-0381-0365-s010502 | reverse | revenue | 5 | pending |
| line-3 | line-3-0518-0447-s014015 | forward | revenue | 5 | pending |
| line-3 | line-3-0518-0447-s014015 | reverse | revenue | 5 | pending |
| line-3 | line-3-0555-0545-s016442 | forward | revenue | 5 | pending |
| line-3 | line-3-0555-0545-s016442 | reverse | revenue | 5 | pending |
| line-3 | line-3-0576-0675-s019388 | forward | revenue | 5 | pending |
| line-3 | line-3-0576-0675-s019388 | reverse | revenue | 5 | pending |
| line-3 | line-3-0761-0860-s025578 | reverse | revenue | 4 | pending |
| line-3 | line-3-0761-0860-s025578 | reverse | spare | 1 | pending |
| line-3 | line-3-0078-0053-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0381-0365-s010502 | forward | spare | 1 | pending |
| line-3 | line-3-0381-0365-s010502 | reverse | spare | 1 | pending |
| line-3 | line-3-0518-0447-s014015 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**82 trainsets exceed the reference platform envelope**, requiring **4,879.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0279-0389-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0405-0476-s003756 | 6 | 2 | 4 | 238.0 |
| line-1-0473-0528-s005650 | 6 | 2 | 4 | 238.0 |
| line-1-0555-0545-s007525 | 6 | 4 | 2 | 119.0 |
| line-1-0614-0565-s008975 | 4 | 2 | 2 | 119.0 |
| line-1-0699-0614-s011097 | 4 | 2 | 2 | 119.0 |
| line-1-0793-0600-s013220 | 4 | 2 | 2 | 119.0 |
| line-1-0879-0586-s015329 | 2 | 2 | 0 | 0.0 |
| line-2-0445-0723-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0471-0638-s003004 | 8 | 2 | 6 | 357.0 |
| line-2-0519-0578-s006019 | 8 | 2 | 6 | 357.0 |
| line-2-0555-0545-s007638 | 6 | 4 | 2 | 119.0 |
| line-2-0673-0469-s010656 | 6 | 2 | 4 | 238.0 |
| line-2-0873-0483-s015548 | 6 | 2 | 4 | 238.0 |
| line-2-1084-0450-s020325 | 3 | 2 | 1 | 59.5 |
| line-3-0078-0053-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0381-0365-s010502 | 12 | 2 | 10 | 595.0 |
| line-3-0518-0447-s014015 | 11 | 2 | 9 | 535.5 |
| line-3-0555-0545-s016442 | 10 | 4 | 6 | 357.0 |
| line-3-0576-0675-s019388 | 10 | 2 | 8 | 476.0 |
| line-3-0761-0860-s025578 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Barisal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
