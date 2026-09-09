# Station and depot overnight allocation

Plan: **34 trainsets at stations + 58 at depots = 92 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0747-0629-s016962 | 58 | 3,451.0 | 14 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0078-0386-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0366-0491-s007017 | station | forward | revenue | 1 |
| line-1 | line-1-0366-0491-s007017 | station | reverse | revenue | 1 |
| line-1 | line-1-0483-0567-s010033 | station | forward | revenue | 1 |
| line-1 | line-1-0483-0567-s010033 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0561-s011561 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0561-s011561 | station | reverse | revenue | 1 |
| line-1 | line-1-0643-0582-s014260 | station | forward | revenue | 1 |
| line-1 | line-1-0643-0582-s014260 | station | reverse | revenue | 1 |
| line-1 | line-1-0747-0629-s016962 | station | reverse | revenue | 2 |
| line-2 | line-2-0523-0644-s005928 | station | forward | revenue | 1 |
| line-2 | line-2-0523-0644-s005928 | station | reverse | revenue | 1 |
| line-2 | line-2-0527-0431-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0544-0561-s003686 | station | forward | revenue | 1 |
| line-2 | line-2-0544-0561-s003686 | station | reverse | revenue | 1 |
| line-2 | line-2-0562-0740-s008171 | station | forward | revenue | 1 |
| line-2 | line-2-0562-0740-s008171 | station | reverse | revenue | 1 |
| line-2 | line-2-0617-0819-s010429 | station | reverse | revenue | 2 |
| line-3 | line-3-0354-0190-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0458-0322-s003502 | station | forward | revenue | 1 |
| line-3 | line-3-0458-0322-s003502 | station | reverse | revenue | 1 |
| line-3 | line-3-0475-0442-s007017 | station | forward | revenue | 1 |
| line-3 | line-3-0475-0442-s007017 | station | reverse | revenue | 1 |
| line-3 | line-3-0477-0747-s015498 | station | reverse | revenue | 2 |
| line-3 | line-3-0494-0649-s013000 | station | forward | revenue | 1 |
| line-3 | line-3-0494-0649-s013000 | station | reverse | revenue | 1 |
| line-3 | line-3-0544-0561-s010522 | station | forward | revenue | 1 |
| line-3 | line-3-0544-0561-s010522 | station | reverse | revenue | 1 |
| line-1 | line-1-0747-0629-s016962 | depot | — | revenue | 21 |
| line-1 | line-1-0747-0629-s016962 | depot | — | spare | 3 |
| line-1 | line-1-0747-0629-s016962 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0747-0629-s016962 | depot | — | revenue | 10 |
| line-2 | line-1-0747-0629-s016962 | depot | — | spare | 2 |
| line-2 | line-1-0747-0629-s016962 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0747-0629-s016962 | depot | — | revenue | 17 |
| line-3 | line-1-0747-0629-s016962 | depot | — | spare | 2 |
| line-3 | line-1-0747-0629-s016962 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (13 trains), line-3 (20 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **92 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **82 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **58 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0078-0386-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0366-0491-s007017 | forward | revenue | 4 | pending |
| line-1 | line-1-0366-0491-s007017 | reverse | revenue | 4 | pending |
| line-1 | line-1-0483-0567-s010033 | forward | revenue | 3 | pending |
| line-1 | line-1-0483-0567-s010033 | reverse | revenue | 3 | pending |
| line-1 | line-1-0544-0561-s011561 | forward | revenue | 3 | pending |
| line-1 | line-1-0544-0561-s011561 | reverse | revenue | 3 | pending |
| line-1 | line-1-0643-0582-s014260 | forward | revenue | 3 | pending |
| line-1 | line-1-0643-0582-s014260 | reverse | revenue | 3 | pending |
| line-1 | line-1-0747-0629-s016962 | reverse | revenue | 3 | pending |
| line-1 | line-1-0483-0567-s010033 | forward | spare | 1 | pending |
| line-1 | line-1-0483-0567-s010033 | reverse | spare | 1 | pending |
| line-1 | line-1-0544-0561-s011561 | forward | spare | 1 | pending |
| line-1 | line-1-0544-0561-s011561 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0527-0431-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0544-0561-s003686 | forward | revenue | 3 | pending |
| line-2 | line-2-0544-0561-s003686 | reverse | revenue | 3 | pending |
| line-2 | line-2-0523-0644-s005928 | forward | revenue | 3 | pending |
| line-2 | line-2-0523-0644-s005928 | reverse | revenue | 2 | pending |
| line-2 | line-2-0562-0740-s008171 | forward | revenue | 2 | pending |
| line-2 | line-2-0562-0740-s008171 | reverse | revenue | 2 | pending |
| line-2 | line-2-0617-0819-s010429 | reverse | revenue | 2 | pending |
| line-2 | line-2-0523-0644-s005928 | reverse | spare | 1 | pending |
| line-2 | line-2-0562-0740-s008171 | forward | spare | 1 | pending |
| line-2 | line-2-0562-0740-s008171 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0354-0190-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0458-0322-s003502 | forward | revenue | 3 | pending |
| line-3 | line-3-0458-0322-s003502 | reverse | revenue | 3 | pending |
| line-3 | line-3-0475-0442-s007017 | forward | revenue | 3 | pending |
| line-3 | line-3-0475-0442-s007017 | reverse | revenue | 3 | pending |
| line-3 | line-3-0544-0561-s010522 | forward | revenue | 3 | pending |
| line-3 | line-3-0544-0561-s010522 | reverse | revenue | 3 | pending |
| line-3 | line-3-0494-0649-s013000 | forward | revenue | 3 | pending |
| line-3 | line-3-0494-0649-s013000 | reverse | revenue | 3 | pending |
| line-3 | line-3-0477-0747-s015498 | reverse | revenue | 2 | pending |
| line-3 | line-3-0477-0747-s015498 | reverse | spare | 1 | pending |
| line-3 | line-3-0354-0190-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0458-0322-s003502 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**48 trainsets exceed the reference platform envelope**, requiring **2,856.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0078-0386-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0366-0491-s007017 | 8 | 2 | 6 | 357.0 |
| line-1-0483-0567-s010033 | 8 | 2 | 6 | 357.0 |
| line-1-0544-0561-s011561 | 8 | 4 | 4 | 238.0 |
| line-1-0643-0582-s014260 | 6 | 2 | 4 | 238.0 |
| line-1-0747-0629-s016962 | 3 | 2 | 1 | 59.5 |
| line-2-0523-0644-s005928 | 6 | 4 | 2 | 119.0 |
| line-2-0527-0431-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0544-0561-s003686 | 6 | 4 | 2 | 119.0 |
| line-2-0562-0740-s008171 | 6 | 2 | 4 | 238.0 |
| line-2-0617-0819-s010429 | 2 | 2 | 0 | 0.0 |
| line-3-0354-0190-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0458-0322-s003502 | 7 | 2 | 5 | 297.5 |
| line-3-0475-0442-s007017 | 6 | 2 | 4 | 238.0 |
| line-3-0477-0747-s015498 | 3 | 2 | 1 | 59.5 |
| line-3-0494-0649-s013000 | 6 | 4 | 2 | 119.0 |
| line-3-0544-0561-s010522 | 6 | 4 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Zagazig/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
