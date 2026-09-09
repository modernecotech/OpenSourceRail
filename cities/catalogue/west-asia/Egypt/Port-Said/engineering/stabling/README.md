# Station and depot overnight allocation

Plan: **30 trainsets at stations + 34 at depots = 64 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0524-0309-s012126 | 34 | 2,023.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0523-0402-s009887 | station | forward | revenue | 1 |
| line-1 | line-1-0523-0402-s009887 | station | reverse | revenue | 1 |
| line-1 | line-1-0524-0309-s012126 | station | reverse | revenue | 2 |
| line-1 | line-1-0558-0545-s005753 | station | forward | revenue | 1 |
| line-1 | line-1-0558-0545-s005753 | station | reverse | revenue | 1 |
| line-1 | line-1-0570-0483-s007630 | station | forward | revenue | 1 |
| line-1 | line-1-0570-0483-s007630 | station | reverse | revenue | 1 |
| line-1 | line-1-0653-0595-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0653-0595-s003005 | station | reverse | revenue | 1 |
| line-1 | line-1-0781-0625-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0532-0606-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0558-0545-s002347 | station | forward | revenue | 1 |
| line-2 | line-2-0558-0545-s002347 | station | reverse | revenue | 1 |
| line-2 | line-2-0599-0476-s004850 | station | forward | revenue | 1 |
| line-2 | line-2-0599-0476-s004850 | station | reverse | revenue | 1 |
| line-2 | line-2-0644-0359-s008173 | station | reverse | revenue | 2 |
| line-3 | line-3-0558-0545-s004289 | station | forward | revenue | 1 |
| line-3 | line-3-0558-0545-s004289 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-0580-s003015 | station | forward | revenue | 1 |
| line-3 | line-3-0591-0580-s003015 | station | reverse | revenue | 1 |
| line-3 | line-3-0624-0503-s006037 | station | forward | revenue | 1 |
| line-3 | line-3-0624-0503-s006037 | station | reverse | revenue | 1 |
| line-3 | line-3-0670-0414-s008895 | station | reverse | revenue | 2 |
| line-3 | line-3-0684-0677-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0524-0309-s012126 | depot | — | revenue | 12 |
| line-1 | line-1-0524-0309-s012126 | depot | — | spare | 2 |
| line-1 | line-1-0524-0309-s012126 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0524-0309-s012126 | depot | — | revenue | 8 |
| line-2 | line-1-0524-0309-s012126 | depot | — | spare | 1 |
| line-2 | line-1-0524-0309-s012126 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0524-0309-s012126 | depot | — | revenue | 7 |
| line-3 | line-1-0524-0309-s012126 | depot | — | spare | 1 |
| line-3 | line-1-0524-0309-s012126 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (10 trains), line-3 (9 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **64 trainsets at 15 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **57 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **34 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0781-0625-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0653-0595-s003005 | forward | revenue | 3 | pending |
| line-1 | line-1-0653-0595-s003005 | reverse | revenue | 3 | pending |
| line-1 | line-1-0558-0545-s005753 | forward | revenue | 3 | pending |
| line-1 | line-1-0558-0545-s005753 | reverse | revenue | 2 | pending |
| line-1 | line-1-0570-0483-s007630 | forward | revenue | 2 | pending |
| line-1 | line-1-0570-0483-s007630 | reverse | revenue | 2 | pending |
| line-1 | line-1-0523-0402-s009887 | forward | revenue | 2 | pending |
| line-1 | line-1-0523-0402-s009887 | reverse | revenue | 2 | pending |
| line-1 | line-1-0524-0309-s012126 | reverse | revenue | 2 | pending |
| line-1 | line-1-0558-0545-s005753 | reverse | spare | 1 | pending |
| line-1 | line-1-0570-0483-s007630 | forward | spare | 1 | pending |
| line-1 | line-1-0570-0483-s007630 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0532-0606-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0545-s002347 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0545-s002347 | reverse | revenue | 3 | pending |
| line-2 | line-2-0599-0476-s004850 | forward | revenue | 3 | pending |
| line-2 | line-2-0599-0476-s004850 | reverse | revenue | 2 | pending |
| line-2 | line-2-0644-0359-s008173 | reverse | revenue | 2 | pending |
| line-2 | line-2-0599-0476-s004850 | reverse | spare | 1 | pending |
| line-2 | line-2-0644-0359-s008173 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0684-0677-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0591-0580-s003015 | forward | revenue | 2 | pending |
| line-3 | line-3-0591-0580-s003015 | reverse | revenue | 2 | pending |
| line-3 | line-3-0558-0545-s004289 | forward | revenue | 2 | pending |
| line-3 | line-3-0558-0545-s004289 | reverse | revenue | 2 | pending |
| line-3 | line-3-0624-0503-s006037 | forward | revenue | 2 | pending |
| line-3 | line-3-0624-0503-s006037 | reverse | revenue | 2 | pending |
| line-3 | line-3-0670-0414-s008895 | reverse | revenue | 2 | pending |
| line-3 | line-3-0591-0580-s003015 | forward | spare | 1 | pending |
| line-3 | line-3-0591-0580-s003015 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**24 trainsets exceed the reference platform envelope**, requiring **1,428.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0523-0402-s009887 | 4 | 2 | 2 | 119.0 |
| line-1-0524-0309-s012126 | 2 | 2 | 0 | 0.0 |
| line-1-0558-0545-s005753 | 6 | 4 | 2 | 119.0 |
| line-1-0570-0483-s007630 | 6 | 4 | 2 | 119.0 |
| line-1-0653-0595-s003005 | 6 | 2 | 4 | 238.0 |
| line-1-0781-0625-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0532-0606-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0558-0545-s002347 | 6 | 4 | 2 | 119.0 |
| line-2-0599-0476-s004850 | 6 | 4 | 2 | 119.0 |
| line-2-0644-0359-s008173 | 3 | 2 | 1 | 59.5 |
| line-3-0558-0545-s004289 | 4 | 4 | 0 | 0.0 |
| line-3-0591-0580-s003015 | 6 | 2 | 4 | 238.0 |
| line-3-0624-0503-s006037 | 4 | 2 | 2 | 119.0 |
| line-3-0670-0414-s008895 | 2 | 2 | 0 | 0.0 |
| line-3-0684-0677-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Port-Said/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
