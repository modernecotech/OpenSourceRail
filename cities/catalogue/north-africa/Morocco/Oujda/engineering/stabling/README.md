# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 87 at depots = 123 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0481-0306-s000000 | line-1 | declared-depot | 24 | 1,428.0 | 5 |
| line-2-0732-0616-s012835 | line-2 | declared-depot | 28 | 1,666.0 | 6 |
| line-3-0345-0481-s000000 | line-3 | declared-depot | 20 | 1,190.0 | 4 |
| line-4-0596-0533-s000000 | line-4 | declared-depot | 15 | 892.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0481-0306-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0506-0425-s002587 | station | forward | revenue | 1 |
| line-1 | line-1-0506-0425-s002587 | station | reverse | revenue | 1 |
| line-1 | line-1-0533-0550-s005311 | station | forward | revenue | 1 |
| line-1 | line-1-0533-0550-s005311 | station | reverse | revenue | 1 |
| line-1 | line-1-0564-0697-s008508 | station | forward | revenue | 1 |
| line-1 | line-1-0564-0697-s008508 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0785-s010425 | station | reverse | revenue | 2 |
| line-2 | line-2-0321-0576-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0413-0595-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0413-0595-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0533-0550-s006342 | station | forward | revenue | 1 |
| line-2 | line-2-0533-0550-s006342 | station | reverse | revenue | 1 |
| line-2 | line-2-0596-0533-s008359 | station | forward | revenue | 1 |
| line-2 | line-2-0596-0533-s008359 | station | reverse | revenue | 1 |
| line-2 | line-2-0599-0538-s008483 | station | forward | revenue | 1 |
| line-2 | line-2-0599-0538-s008483 | station | reverse | revenue | 1 |
| line-2 | line-2-0732-0616-s012835 | station | reverse | revenue | 2 |
| line-3 | line-3-0345-0481-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0506-0425-s003684 | station | forward | revenue | 1 |
| line-3 | line-3-0506-0425-s003684 | station | reverse | revenue | 1 |
| line-3 | line-3-0692-0360-s007954 | station | reverse | revenue | 2 |
| line-4 | line-4-0596-0533-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0599-0538-s000205 | station | forward | revenue | 1 |
| line-4 | line-4-0599-0538-s000205 | station | reverse | revenue | 1 |
| line-4 | line-4-0638-0439-s003527 | station | forward | revenue | 1 |
| line-4 | line-4-0638-0439-s003527 | station | reverse | revenue | 1 |
| line-4 | line-4-0725-0400-s006601 | station | reverse | revenue | 2 |
| line-1 | line-1-0481-0306-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0481-0306-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0481-0306-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0732-0616-s012835 | depot | — | revenue | 24 |
| line-2 | line-2-0732-0616-s012835 | depot | — | spare | 3 |
| line-2 | line-2-0732-0616-s012835 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0345-0481-s000000 | depot | — | revenue | 17 |
| line-3 | line-3-0345-0481-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0345-0481-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0596-0533-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0596-0533-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0596-0533-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/oujda-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **123 trainsets at 18 stations**; largest initial station queue **13**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **109 revenue, 10 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **87 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0481-0306-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0506-0425-s002587 | forward | revenue | 4 | pending |
| line-1 | line-1-0506-0425-s002587 | reverse | revenue | 4 | pending |
| line-1 | line-1-0533-0550-s005311 | forward | revenue | 4 | pending |
| line-1 | line-1-0533-0550-s005311 | reverse | revenue | 4 | pending |
| line-1 | line-1-0564-0697-s008508 | forward | revenue | 4 | pending |
| line-1 | line-1-0564-0697-s008508 | reverse | revenue | 3 | pending |
| line-1 | line-1-0583-0785-s010425 | reverse | revenue | 3 | pending |
| line-1 | line-1-0564-0697-s008508 | reverse | spare | 1 | pending |
| line-1 | line-1-0583-0785-s010425 | reverse | spare | 1 | pending |
| line-1 | line-1-0481-0306-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0506-0425-s002587 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0321-0576-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0413-0595-s003006 | forward | revenue | 4 | pending |
| line-2 | line-2-0413-0595-s003006 | reverse | revenue | 4 | pending |
| line-2 | line-2-0533-0550-s006342 | forward | revenue | 4 | pending |
| line-2 | line-2-0533-0550-s006342 | reverse | revenue | 4 | pending |
| line-2 | line-2-0596-0533-s008359 | forward | revenue | 4 | pending |
| line-2 | line-2-0596-0533-s008359 | reverse | revenue | 3 | pending |
| line-2 | line-2-0599-0538-s008483 | forward | revenue | 3 | pending |
| line-2 | line-2-0599-0538-s008483 | reverse | revenue | 3 | pending |
| line-2 | line-2-0732-0616-s012835 | reverse | revenue | 3 | pending |
| line-2 | line-2-0596-0533-s008359 | reverse | spare | 1 | pending |
| line-2 | line-2-0599-0538-s008483 | forward | spare | 1 | pending |
| line-2 | line-2-0599-0538-s008483 | reverse | spare | 1 | pending |
| line-2 | line-2-0732-0616-s012835 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0345-0481-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0506-0425-s003684 | forward | revenue | 6 | pending |
| line-3 | line-3-0506-0425-s003684 | reverse | revenue | 6 | pending |
| line-3 | line-3-0692-0360-s007954 | reverse | revenue | 5 | pending |
| line-3 | line-3-0692-0360-s007954 | reverse | spare | 1 | pending |
| line-3 | line-3-0345-0481-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0425-s003684 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0596-0533-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0599-0538-s000205 | forward | revenue | 4 | pending |
| line-4 | line-4-0599-0538-s000205 | reverse | revenue | 3 | pending |
| line-4 | line-4-0638-0439-s003527 | forward | revenue | 3 | pending |
| line-4 | line-4-0638-0439-s003527 | reverse | revenue | 3 | pending |
| line-4 | line-4-0725-0400-s006601 | reverse | revenue | 3 | pending |
| line-4 | line-4-0599-0538-s000205 | reverse | spare | 1 | pending |
| line-4 | line-4-0638-0439-s003527 | forward | spare | 1 | pending |
| line-4 | line-4-0638-0439-s003527 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**73 trainsets exceed the reference platform envelope**, requiring **4,343.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0481-0306-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0506-0425-s002587 | 9 | 4 | 5 | 297.5 |
| line-1-0533-0550-s005311 | 8 | 4 | 4 | 238.0 |
| line-1-0564-0697-s008508 | 8 | 2 | 6 | 357.0 |
| line-1-0583-0785-s010425 | 4 | 2 | 2 | 119.0 |
| line-2-0321-0576-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0413-0595-s003006 | 8 | 2 | 6 | 357.0 |
| line-2-0533-0550-s006342 | 8 | 4 | 4 | 238.0 |
| line-2-0596-0533-s008359 | 8 | 4 | 4 | 238.0 |
| line-2-0599-0538-s008483 | 8 | 4 | 4 | 238.0 |
| line-2-0732-0616-s012835 | 4 | 2 | 2 | 119.0 |
| line-3-0345-0481-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0506-0425-s003684 | 13 | 4 | 9 | 535.5 |
| line-3-0692-0360-s007954 | 6 | 2 | 4 | 238.0 |
| line-4-0596-0533-s000000 | 4 | 2 | 2 | 119.0 |
| line-4-0599-0538-s000205 | 8 | 4 | 4 | 238.0 |
| line-4-0638-0439-s003527 | 8 | 2 | 6 | 357.0 |
| line-4-0725-0400-s006601 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Oujda/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
