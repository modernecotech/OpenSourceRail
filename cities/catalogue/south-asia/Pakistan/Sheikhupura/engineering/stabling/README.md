# Station and depot overnight allocation

Plan: **18 trainsets at stations + 19 at depots = 37 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0599-0736-s008684 | 19 | 1,130.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0501-0372-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0515-0511-s003026 | station | forward | revenue | 1 |
| line-1 | line-1-0515-0511-s003026 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0554-s004524 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0554-s004524 | station | reverse | revenue | 1 |
| line-1 | line-1-0556-0617-s005931 | station | forward | revenue | 1 |
| line-1 | line-1-0556-0617-s005931 | station | reverse | revenue | 1 |
| line-1 | line-1-0599-0736-s008684 | station | reverse | revenue | 2 |
| line-2 | line-2-0517-0430-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0551-0554-s002915 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0554-s002915 | station | reverse | revenue | 1 |
| line-2 | line-2-0596-0640-s005385 | station | forward | revenue | 1 |
| line-2 | line-2-0596-0640-s005385 | station | reverse | revenue | 1 |
| line-2 | line-2-0601-0732-s007869 | station | reverse | revenue | 2 |
| line-1 | line-1-0599-0736-s008684 | depot | — | revenue | 7 |
| line-1 | line-1-0599-0736-s008684 | depot | — | spare | 1 |
| line-1 | line-1-0599-0736-s008684 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0599-0736-s008684 | depot | — | revenue | 8 |
| line-2 | line-1-0599-0736-s008684 | depot | — | spare | 1 |
| line-2 | line-1-0599-0736-s008684 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (10 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **37 trainsets at 9 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **33 revenue, 2 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **18 positions**; **19 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **8 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0501-0372-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0515-0511-s003026 | forward | revenue | 2 | pending |
| line-1 | line-1-0515-0511-s003026 | reverse | revenue | 2 | pending |
| line-1 | line-1-0551-0554-s004524 | forward | revenue | 2 | pending |
| line-1 | line-1-0551-0554-s004524 | reverse | revenue | 2 | pending |
| line-1 | line-1-0556-0617-s005931 | forward | revenue | 2 | pending |
| line-1 | line-1-0556-0617-s005931 | reverse | revenue | 2 | pending |
| line-1 | line-1-0599-0736-s008684 | reverse | revenue | 2 | pending |
| line-1 | line-1-0515-0511-s003026 | forward | spare | 1 | pending |
| line-1 | line-1-0515-0511-s003026 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0517-0430-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0554-s002915 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0554-s002915 | reverse | revenue | 3 | pending |
| line-2 | line-2-0596-0640-s005385 | forward | revenue | 3 | pending |
| line-2 | line-2-0596-0640-s005385 | reverse | revenue | 2 | pending |
| line-2 | line-2-0601-0732-s007869 | reverse | revenue | 2 | pending |
| line-2 | line-2-0596-0640-s005385 | reverse | spare | 1 | pending |
| line-2 | line-2-0601-0732-s007869 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**15 trainsets exceed the reference platform envelope**, requiring **892.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0501-0372-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0515-0511-s003026 | 6 | 2 | 4 | 238.0 |
| line-1-0551-0554-s004524 | 4 | 4 | 0 | 0.0 |
| line-1-0556-0617-s005931 | 4 | 2 | 2 | 119.0 |
| line-1-0599-0736-s008684 | 2 | 2 | 0 | 0.0 |
| line-2-0517-0430-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0551-0554-s002915 | 6 | 4 | 2 | 119.0 |
| line-2-0596-0640-s005385 | 6 | 2 | 4 | 238.0 |
| line-2-0601-0732-s007869 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sheikhupura/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
