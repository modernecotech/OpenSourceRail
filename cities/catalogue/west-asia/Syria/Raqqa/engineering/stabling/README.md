# Station and depot overnight allocation

Plan: **34 trainsets at stations + 71 at depots = 105 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0480-0367-s018333 | 71 | 4,224.5 | 16 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0524-0338-s005648 | station | forward | revenue | 1 |
| line-1 | line-1-0524-0338-s005648 | station | reverse | revenue | 1 |
| line-1 | line-1-0525-0460-s008665 | station | forward | revenue | 1 |
| line-1 | line-1-0525-0460-s008665 | station | reverse | revenue | 1 |
| line-1 | line-1-0529-0080-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0549-0550-s010942 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0550-s010942 | station | reverse | revenue | 1 |
| line-1 | line-1-0568-0607-s013452 | station | forward | revenue | 1 |
| line-1 | line-1-0568-0607-s013452 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0716-s015956 | station | reverse | revenue | 2 |
| line-2 | line-2-0294-0806-s014449 | station | reverse | revenue | 2 |
| line-2 | line-2-0455-0604-s007622 | station | forward | revenue | 1 |
| line-2 | line-2-0455-0604-s007622 | station | reverse | revenue | 1 |
| line-2 | line-2-0549-0550-s004203 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0550-s004203 | station | reverse | revenue | 1 |
| line-2 | line-2-0589-0478-s002105 | station | forward | revenue | 1 |
| line-2 | line-2-0589-0478-s002105 | station | reverse | revenue | 1 |
| line-2 | line-2-0628-0393-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0480-0367-s018333 | station | reverse | revenue | 2 |
| line-3 | line-3-0491-0458-s015643 | station | forward | revenue | 1 |
| line-3 | line-3-0491-0458-s015643 | station | reverse | revenue | 1 |
| line-3 | line-3-0531-0650-s010035 | station | forward | revenue | 1 |
| line-3 | line-3-0531-0650-s010035 | station | reverse | revenue | 1 |
| line-3 | line-3-0549-0550-s013202 | station | forward | revenue | 1 |
| line-3 | line-3-0549-0550-s013202 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-1029-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0601-0731-s007015 | station | forward | revenue | 1 |
| line-3 | line-3-0601-0731-s007015 | station | reverse | revenue | 1 |
| line-1 | line-3-0480-0367-s018333 | depot | — | revenue | 19 |
| line-1 | line-3-0480-0367-s018333 | depot | — | spare | 3 |
| line-1 | line-3-0480-0367-s018333 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0480-0367-s018333 | depot | — | revenue | 17 |
| line-2 | line-3-0480-0367-s018333 | depot | — | spare | 2 |
| line-2 | line-3-0480-0367-s018333 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0480-0367-s018333 | depot | — | revenue | 24 |
| line-3 | line-3-0480-0367-s018333 | depot | — | spare | 3 |
| line-3 | line-3-0480-0367-s018333 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (23 trains), line-2 (20 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **105 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **94 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **71 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0529-0080-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0524-0338-s005648 | forward | revenue | 3 | pending |
| line-1 | line-1-0524-0338-s005648 | reverse | revenue | 3 | pending |
| line-1 | line-1-0525-0460-s008665 | forward | revenue | 3 | pending |
| line-1 | line-1-0525-0460-s008665 | reverse | revenue | 3 | pending |
| line-1 | line-1-0549-0550-s010942 | forward | revenue | 3 | pending |
| line-1 | line-1-0549-0550-s010942 | reverse | revenue | 3 | pending |
| line-1 | line-1-0568-0607-s013452 | forward | revenue | 3 | pending |
| line-1 | line-1-0568-0607-s013452 | reverse | revenue | 3 | pending |
| line-1 | line-1-0571-0716-s015956 | reverse | revenue | 3 | pending |
| line-1 | line-1-0524-0338-s005648 | forward | spare | 1 | pending |
| line-1 | line-1-0524-0338-s005648 | reverse | spare | 1 | pending |
| line-1 | line-1-0525-0460-s008665 | forward | spare | 1 | pending |
| line-1 | line-1-0525-0460-s008665 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0628-0393-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0589-0478-s002105 | forward | revenue | 4 | pending |
| line-2 | line-2-0589-0478-s002105 | reverse | revenue | 4 | pending |
| line-2 | line-2-0549-0550-s004203 | forward | revenue | 3 | pending |
| line-2 | line-2-0549-0550-s004203 | reverse | revenue | 3 | pending |
| line-2 | line-2-0455-0604-s007622 | forward | revenue | 3 | pending |
| line-2 | line-2-0455-0604-s007622 | reverse | revenue | 3 | pending |
| line-2 | line-2-0294-0806-s014449 | reverse | revenue | 3 | pending |
| line-2 | line-2-0549-0550-s004203 | forward | spare | 1 | pending |
| line-2 | line-2-0549-0550-s004203 | reverse | spare | 1 | pending |
| line-2 | line-2-0455-0604-s007622 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0591-1029-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0601-0731-s007015 | forward | revenue | 4 | pending |
| line-3 | line-3-0601-0731-s007015 | reverse | revenue | 4 | pending |
| line-3 | line-3-0531-0650-s010035 | forward | revenue | 4 | pending |
| line-3 | line-3-0531-0650-s010035 | reverse | revenue | 4 | pending |
| line-3 | line-3-0549-0550-s013202 | forward | revenue | 4 | pending |
| line-3 | line-3-0549-0550-s013202 | reverse | revenue | 3 | pending |
| line-3 | line-3-0491-0458-s015643 | forward | revenue | 3 | pending |
| line-3 | line-3-0491-0458-s015643 | reverse | revenue | 3 | pending |
| line-3 | line-3-0480-0367-s018333 | reverse | revenue | 3 | pending |
| line-3 | line-3-0549-0550-s013202 | reverse | spare | 1 | pending |
| line-3 | line-3-0491-0458-s015643 | forward | spare | 1 | pending |
| line-3 | line-3-0491-0458-s015643 | reverse | spare | 1 | pending |
| line-3 | line-3-0480-0367-s018333 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**65 trainsets exceed the reference platform envelope**, requiring **3,867.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0524-0338-s005648 | 8 | 2 | 6 | 357.0 |
| line-1-0525-0460-s008665 | 8 | 2 | 6 | 357.0 |
| line-1-0529-0080-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0549-0550-s010942 | 6 | 4 | 2 | 119.0 |
| line-1-0568-0607-s013452 | 6 | 2 | 4 | 238.0 |
| line-1-0571-0716-s015956 | 3 | 2 | 1 | 59.5 |
| line-2-0294-0806-s014449 | 3 | 2 | 1 | 59.5 |
| line-2-0455-0604-s007622 | 7 | 2 | 5 | 297.5 |
| line-2-0549-0550-s004203 | 8 | 4 | 4 | 238.0 |
| line-2-0589-0478-s002105 | 8 | 2 | 6 | 357.0 |
| line-2-0628-0393-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0480-0367-s018333 | 4 | 2 | 2 | 119.0 |
| line-3-0491-0458-s015643 | 8 | 2 | 6 | 357.0 |
| line-3-0531-0650-s010035 | 8 | 2 | 6 | 357.0 |
| line-3-0549-0550-s013202 | 8 | 4 | 4 | 238.0 |
| line-3-0591-1029-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0601-0731-s007015 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Raqqa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
