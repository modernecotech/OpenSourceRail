# Station and depot overnight allocation

Plan: **28 trainsets at stations + 45 at depots = 73 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0261-0658-s014237 | 45 | 2,677.5 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0261-0658-s014237 | station | reverse | revenue | 2 |
| line-1 | line-1-0346-0631-s012083 | station | forward | revenue | 1 |
| line-1 | line-1-0346-0631-s012083 | station | reverse | revenue | 1 |
| line-1 | line-1-0421-0590-s009941 | station | forward | revenue | 1 |
| line-1 | line-1-0421-0590-s009941 | station | reverse | revenue | 1 |
| line-1 | line-1-0540-0547-s006450 | station | forward | revenue | 1 |
| line-1 | line-1-0540-0547-s006450 | station | reverse | revenue | 1 |
| line-1 | line-1-0562-0431-s003002 | station | forward | revenue | 1 |
| line-1 | line-1-0562-0431-s003002 | station | reverse | revenue | 1 |
| line-1 | line-1-0573-0322-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0224-0478-s010935 | station | reverse | revenue | 2 |
| line-2 | line-2-0447-0518-s004850 | station | forward | revenue | 1 |
| line-2 | line-2-0447-0518-s004850 | station | reverse | revenue | 1 |
| line-2 | line-2-0540-0547-s002105 | station | forward | revenue | 1 |
| line-2 | line-2-0540-0547-s002105 | station | reverse | revenue | 1 |
| line-2 | line-2-0602-0522-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0312-0495-s007805 | station | reverse | revenue | 2 |
| line-3 | line-3-0398-0465-s005428 | station | forward | revenue | 1 |
| line-3 | line-3-0398-0465-s005428 | station | reverse | revenue | 1 |
| line-3 | line-3-0477-0391-s003027 | station | forward | revenue | 1 |
| line-3 | line-3-0477-0391-s003027 | station | reverse | revenue | 1 |
| line-3 | line-3-0518-0259-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0261-0658-s014237 | depot | — | revenue | 16 |
| line-1 | line-1-0261-0658-s014237 | depot | — | spare | 2 |
| line-1 | line-1-0261-0658-s014237 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0261-0658-s014237 | depot | — | revenue | 13 |
| line-2 | line-1-0261-0658-s014237 | depot | — | spare | 2 |
| line-2 | line-1-0261-0658-s014237 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0261-0658-s014237 | depot | — | revenue | 8 |
| line-3 | line-1-0261-0658-s014237 | depot | — | spare | 1 |
| line-3 | line-1-0261-0658-s014237 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (16 trains), line-3 (10 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **73 trainsets at 14 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **65 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **45 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0573-0322-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0562-0431-s003002 | forward | revenue | 3 | pending |
| line-1 | line-1-0562-0431-s003002 | reverse | revenue | 3 | pending |
| line-1 | line-1-0540-0547-s006450 | forward | revenue | 3 | pending |
| line-1 | line-1-0540-0547-s006450 | reverse | revenue | 3 | pending |
| line-1 | line-1-0421-0590-s009941 | forward | revenue | 3 | pending |
| line-1 | line-1-0421-0590-s009941 | reverse | revenue | 3 | pending |
| line-1 | line-1-0346-0631-s012083 | forward | revenue | 3 | pending |
| line-1 | line-1-0346-0631-s012083 | reverse | revenue | 2 | pending |
| line-1 | line-1-0261-0658-s014237 | reverse | revenue | 2 | pending |
| line-1 | line-1-0346-0631-s012083 | reverse | spare | 1 | pending |
| line-1 | line-1-0261-0658-s014237 | reverse | spare | 1 | pending |
| line-1 | line-1-0573-0322-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0602-0522-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0540-0547-s002105 | forward | revenue | 4 | pending |
| line-2 | line-2-0540-0547-s002105 | reverse | revenue | 4 | pending |
| line-2 | line-2-0447-0518-s004850 | forward | revenue | 3 | pending |
| line-2 | line-2-0447-0518-s004850 | reverse | revenue | 3 | pending |
| line-2 | line-2-0224-0478-s010935 | reverse | revenue | 3 | pending |
| line-2 | line-2-0447-0518-s004850 | forward | spare | 1 | pending |
| line-2 | line-2-0447-0518-s004850 | reverse | spare | 1 | pending |
| line-2 | line-2-0224-0478-s010935 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0518-0259-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0477-0391-s003027 | forward | revenue | 3 | pending |
| line-3 | line-3-0477-0391-s003027 | reverse | revenue | 3 | pending |
| line-3 | line-3-0398-0465-s005428 | forward | revenue | 3 | pending |
| line-3 | line-3-0398-0465-s005428 | reverse | revenue | 2 | pending |
| line-3 | line-3-0312-0495-s007805 | reverse | revenue | 2 | pending |
| line-3 | line-3-0398-0465-s005428 | reverse | spare | 1 | pending |
| line-3 | line-3-0312-0495-s007805 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**41 trainsets exceed the reference platform envelope**, requiring **2,439.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0261-0658-s014237 | 3 | 2 | 1 | 59.5 |
| line-1-0346-0631-s012083 | 6 | 2 | 4 | 238.0 |
| line-1-0421-0590-s009941 | 6 | 2 | 4 | 238.0 |
| line-1-0540-0547-s006450 | 6 | 4 | 2 | 119.0 |
| line-1-0562-0431-s003002 | 6 | 2 | 4 | 238.0 |
| line-1-0573-0322-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0224-0478-s010935 | 4 | 2 | 2 | 119.0 |
| line-2-0447-0518-s004850 | 8 | 2 | 6 | 357.0 |
| line-2-0540-0547-s002105 | 8 | 4 | 4 | 238.0 |
| line-2-0602-0522-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0312-0495-s007805 | 3 | 2 | 1 | 59.5 |
| line-3-0398-0465-s005428 | 6 | 2 | 4 | 238.0 |
| line-3-0477-0391-s003027 | 6 | 2 | 4 | 238.0 |
| line-3-0518-0259-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Garoua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
