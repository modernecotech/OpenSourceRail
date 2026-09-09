# Station and depot overnight allocation

Plan: **36 trainsets at stations + 45 at depots = 81 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0583-0785-s012962 | 45 | 2,677.5 | 13 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0480-0430-s003024 | station | forward | revenue | 1 |
| line-1 | line-1-0480-0430-s003024 | station | reverse | revenue | 1 |
| line-1 | line-1-0481-0306-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0505-0497-s005124 | station | forward | revenue | 1 |
| line-1 | line-1-0505-0497-s005124 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0646-s009281 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0646-s009281 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0553-s007210 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0553-s007210 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0785-s012962 | station | reverse | revenue | 2 |
| line-2 | line-2-0321-0576-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0413-0595-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0413-0595-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0477-0567-s004919 | station | forward | revenue | 1 |
| line-2 | line-2-0477-0567-s004919 | station | reverse | revenue | 1 |
| line-2 | line-2-0553-0553-s006817 | station | forward | revenue | 1 |
| line-2 | line-2-0553-0553-s006817 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0553-s008825 | station | forward | revenue | 1 |
| line-2 | line-2-0604-0553-s008825 | station | reverse | revenue | 1 |
| line-2 | line-2-0661-0612-s010820 | station | forward | revenue | 1 |
| line-2 | line-2-0661-0612-s010820 | station | reverse | revenue | 1 |
| line-2 | line-2-0732-0616-s012835 | station | reverse | revenue | 2 |
| line-3 | line-3-0345-0481-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0457-0503-s003007 | station | forward | revenue | 1 |
| line-3 | line-3-0457-0503-s003007 | station | reverse | revenue | 1 |
| line-3 | line-3-0553-0553-s005802 | station | forward | revenue | 1 |
| line-3 | line-3-0553-0553-s005802 | station | reverse | revenue | 1 |
| line-3 | line-3-0589-0448-s008349 | station | forward | revenue | 1 |
| line-3 | line-3-0589-0448-s008349 | station | reverse | revenue | 1 |
| line-3 | line-3-0692-0360-s011703 | station | reverse | revenue | 2 |
| line-1 | line-1-0583-0785-s012962 | depot | — | revenue | 13 |
| line-1 | line-1-0583-0785-s012962 | depot | — | spare | 2 |
| line-1 | line-1-0583-0785-s012962 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0583-0785-s012962 | depot | — | revenue | 10 |
| line-2 | line-1-0583-0785-s012962 | depot | — | spare | 2 |
| line-2 | line-1-0583-0785-s012962 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0583-0785-s012962 | depot | — | revenue | 13 |
| line-3 | line-1-0583-0785-s012962 | depot | — | spare | 2 |
| line-3 | line-1-0583-0785-s012962 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (13 trains), line-3 (16 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **81 trainsets at 18 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **72 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **45 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0481-0306-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0480-0430-s003024 | forward | revenue | 3 | pending |
| line-1 | line-1-0480-0430-s003024 | reverse | revenue | 3 | pending |
| line-1 | line-1-0505-0497-s005124 | forward | revenue | 3 | pending |
| line-1 | line-1-0505-0497-s005124 | reverse | revenue | 3 | pending |
| line-1 | line-1-0553-0553-s007210 | forward | revenue | 2 | pending |
| line-1 | line-1-0553-0553-s007210 | reverse | revenue | 2 | pending |
| line-1 | line-1-0551-0646-s009281 | forward | revenue | 2 | pending |
| line-1 | line-1-0551-0646-s009281 | reverse | revenue | 2 | pending |
| line-1 | line-1-0583-0785-s012962 | reverse | revenue | 2 | pending |
| line-1 | line-1-0553-0553-s007210 | forward | spare | 1 | pending |
| line-1 | line-1-0553-0553-s007210 | reverse | spare | 1 | pending |
| line-1 | line-1-0551-0646-s009281 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0321-0576-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0413-0595-s003006 | forward | revenue | 2 | pending |
| line-2 | line-2-0413-0595-s003006 | reverse | revenue | 2 | pending |
| line-2 | line-2-0477-0567-s004919 | forward | revenue | 2 | pending |
| line-2 | line-2-0477-0567-s004919 | reverse | revenue | 2 | pending |
| line-2 | line-2-0553-0553-s006817 | forward | revenue | 2 | pending |
| line-2 | line-2-0553-0553-s006817 | reverse | revenue | 2 | pending |
| line-2 | line-2-0604-0553-s008825 | forward | revenue | 2 | pending |
| line-2 | line-2-0604-0553-s008825 | reverse | revenue | 2 | pending |
| line-2 | line-2-0661-0612-s010820 | forward | revenue | 2 | pending |
| line-2 | line-2-0661-0612-s010820 | reverse | revenue | 2 | pending |
| line-2 | line-2-0732-0616-s012835 | reverse | revenue | 2 | pending |
| line-2 | line-2-0321-0576-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0413-0595-s003006 | forward | spare | 1 | pending |
| line-2 | line-2-0413-0595-s003006 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0345-0481-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0457-0503-s003007 | forward | revenue | 3 | pending |
| line-3 | line-3-0457-0503-s003007 | reverse | revenue | 3 | pending |
| line-3 | line-3-0553-0553-s005802 | forward | revenue | 3 | pending |
| line-3 | line-3-0553-0553-s005802 | reverse | revenue | 3 | pending |
| line-3 | line-3-0589-0448-s008349 | forward | revenue | 3 | pending |
| line-3 | line-3-0589-0448-s008349 | reverse | revenue | 3 | pending |
| line-3 | line-3-0692-0360-s011703 | reverse | revenue | 2 | pending |
| line-3 | line-3-0692-0360-s011703 | reverse | spare | 1 | pending |
| line-3 | line-3-0345-0481-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0457-0503-s003007 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**39 trainsets exceed the reference platform envelope**, requiring **2,320.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0480-0430-s003024 | 6 | 2 | 4 | 238.0 |
| line-1-0481-0306-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0505-0497-s005124 | 6 | 2 | 4 | 238.0 |
| line-1-0551-0646-s009281 | 5 | 2 | 3 | 178.5 |
| line-1-0553-0553-s007210 | 6 | 4 | 2 | 119.0 |
| line-1-0583-0785-s012962 | 2 | 2 | 0 | 0.0 |
| line-2-0321-0576-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0413-0595-s003006 | 6 | 2 | 4 | 238.0 |
| line-2-0477-0567-s004919 | 4 | 2 | 2 | 119.0 |
| line-2-0553-0553-s006817 | 4 | 4 | 0 | 0.0 |
| line-2-0604-0553-s008825 | 4 | 2 | 2 | 119.0 |
| line-2-0661-0612-s010820 | 4 | 2 | 2 | 119.0 |
| line-2-0732-0616-s012835 | 2 | 2 | 0 | 0.0 |
| line-3-0345-0481-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0457-0503-s003007 | 7 | 2 | 5 | 297.5 |
| line-3-0553-0553-s005802 | 6 | 4 | 2 | 119.0 |
| line-3-0589-0448-s008349 | 6 | 2 | 4 | 238.0 |
| line-3-0692-0360-s011703 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Oujda/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
