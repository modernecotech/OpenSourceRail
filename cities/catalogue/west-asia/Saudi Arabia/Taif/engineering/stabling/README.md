# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 138 at depots = 176 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0335-0312-s023887 | line-1 | declared-depot | 62 | 3,689.0 | 11 |
| line-2-0876-0538-s000000 | line-2 | declared-depot | 29 | 1,725.5 | 6 |
| line-3-0354-0936-s000000 | line-3 | declared-depot | 47 | 2,796.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0335-0312-s023887 | station | reverse | revenue | 2 |
| line-1 | line-1-0424-0407-s020957 | station | forward | revenue | 1 |
| line-1 | line-1-0424-0407-s020957 | station | reverse | revenue | 1 |
| line-1 | line-1-0513-0502-s018038 | station | forward | revenue | 1 |
| line-1 | line-1-0513-0502-s018038 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0545-s016686 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0545-s016686 | station | reverse | revenue | 1 |
| line-1 | line-1-0636-0633-s014036 | station | forward | revenue | 1 |
| line-1 | line-1-0636-0633-s014036 | station | reverse | revenue | 1 |
| line-1 | line-1-0742-0746-s010535 | station | forward | revenue | 1 |
| line-1 | line-1-0742-0746-s010535 | station | reverse | revenue | 1 |
| line-1 | line-1-0939-1100-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0412-0236-s012368 | station | reverse | revenue | 2 |
| line-2 | line-2-0587-0350-s007689 | station | forward | revenue | 1 |
| line-2 | line-2-0587-0350-s007689 | station | reverse | revenue | 1 |
| line-2 | line-2-0643-0386-s006212 | station | forward | revenue | 1 |
| line-2 | line-2-0643-0386-s006212 | station | reverse | revenue | 1 |
| line-2 | line-2-0756-0460-s003198 | station | forward | revenue | 1 |
| line-2 | line-2-0756-0460-s003198 | station | reverse | revenue | 1 |
| line-2 | line-2-0876-0538-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0936-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0424-0686-s007016 | station | forward | revenue | 1 |
| line-3 | line-3-0424-0686-s007016 | station | reverse | revenue | 1 |
| line-3 | line-3-0483-0563-s010023 | station | forward | revenue | 1 |
| line-3 | line-3-0483-0563-s010023 | station | reverse | revenue | 1 |
| line-3 | line-3-0513-0502-s011503 | station | forward | revenue | 1 |
| line-3 | line-3-0513-0502-s011503 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0440-s013027 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0440-s013027 | station | reverse | revenue | 1 |
| line-3 | line-3-0587-0350-s015238 | station | forward | revenue | 1 |
| line-3 | line-3-0587-0350-s015238 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0201-s018877 | station | reverse | revenue | 2 |
| line-1 | line-1-0335-0312-s023887 | depot | — | revenue | 55 |
| line-1 | line-1-0335-0312-s023887 | depot | — | spare | 6 |
| line-1 | line-1-0335-0312-s023887 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0876-0538-s000000 | depot | — | revenue | 25 |
| line-2 | line-2-0876-0538-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0876-0538-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0936-s000000 | depot | — | revenue | 41 |
| line-3 | line-3-0354-0936-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0354-0936-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/taif-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **176 trainsets at 19 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **159 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **138 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0939-1100-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0742-0746-s010535 | forward | revenue | 6 | pending |
| line-1 | line-1-0742-0746-s010535 | reverse | revenue | 6 | pending |
| line-1 | line-1-0636-0633-s014036 | forward | revenue | 6 | pending |
| line-1 | line-1-0636-0633-s014036 | reverse | revenue | 6 | pending |
| line-1 | line-1-0554-0545-s016686 | forward | revenue | 6 | pending |
| line-1 | line-1-0554-0545-s016686 | reverse | revenue | 6 | pending |
| line-1 | line-1-0513-0502-s018038 | forward | revenue | 6 | pending |
| line-1 | line-1-0513-0502-s018038 | reverse | revenue | 6 | pending |
| line-1 | line-1-0424-0407-s020957 | forward | revenue | 5 | pending |
| line-1 | line-1-0424-0407-s020957 | reverse | revenue | 5 | pending |
| line-1 | line-1-0335-0312-s023887 | reverse | revenue | 5 | pending |
| line-1 | line-1-0424-0407-s020957 | forward | spare | 1 | pending |
| line-1 | line-1-0424-0407-s020957 | reverse | spare | 1 | pending |
| line-1 | line-1-0335-0312-s023887 | reverse | spare | 1 | pending |
| line-1 | line-1-0939-1100-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0742-0746-s010535 | forward | spare | 1 | pending |
| line-1 | line-1-0742-0746-s010535 | reverse | spare | 1 | pending |
| line-1 | line-1-0636-0633-s014036 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0876-0538-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0756-0460-s003198 | forward | revenue | 5 | pending |
| line-2 | line-2-0756-0460-s003198 | reverse | revenue | 5 | pending |
| line-2 | line-2-0643-0386-s006212 | forward | revenue | 4 | pending |
| line-2 | line-2-0643-0386-s006212 | reverse | revenue | 4 | pending |
| line-2 | line-2-0587-0350-s007689 | forward | revenue | 4 | pending |
| line-2 | line-2-0587-0350-s007689 | reverse | revenue | 4 | pending |
| line-2 | line-2-0412-0236-s012368 | reverse | revenue | 4 | pending |
| line-2 | line-2-0643-0386-s006212 | forward | spare | 1 | pending |
| line-2 | line-2-0643-0386-s006212 | reverse | spare | 1 | pending |
| line-2 | line-2-0587-0350-s007689 | forward | spare | 1 | pending |
| line-2 | line-2-0587-0350-s007689 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0354-0936-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0424-0686-s007016 | forward | revenue | 5 | pending |
| line-3 | line-3-0424-0686-s007016 | reverse | revenue | 5 | pending |
| line-3 | line-3-0483-0563-s010023 | forward | revenue | 5 | pending |
| line-3 | line-3-0483-0563-s010023 | reverse | revenue | 5 | pending |
| line-3 | line-3-0513-0502-s011503 | forward | revenue | 5 | pending |
| line-3 | line-3-0513-0502-s011503 | reverse | revenue | 5 | pending |
| line-3 | line-3-0543-0440-s013027 | forward | revenue | 4 | pending |
| line-3 | line-3-0543-0440-s013027 | reverse | revenue | 4 | pending |
| line-3 | line-3-0587-0350-s015238 | forward | revenue | 4 | pending |
| line-3 | line-3-0587-0350-s015238 | reverse | revenue | 4 | pending |
| line-3 | line-3-0658-0201-s018877 | reverse | revenue | 4 | pending |
| line-3 | line-3-0543-0440-s013027 | forward | spare | 1 | pending |
| line-3 | line-3-0543-0440-s013027 | reverse | spare | 1 | pending |
| line-3 | line-3-0587-0350-s015238 | forward | spare | 1 | pending |
| line-3 | line-3-0587-0350-s015238 | reverse | spare | 1 | pending |
| line-3 | line-3-0658-0201-s018877 | reverse | spare | 1 | pending |
| line-3 | line-3-0354-0936-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**130 trainsets exceed the reference platform envelope**, requiring **7,735.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0335-0312-s023887 | 6 | 2 | 4 | 238.0 |
| line-1-0424-0407-s020957 | 12 | 2 | 10 | 595.0 |
| line-1-0513-0502-s018038 | 12 | 4 | 8 | 476.0 |
| line-1-0554-0545-s016686 | 12 | 2 | 10 | 595.0 |
| line-1-0636-0633-s014036 | 13 | 2 | 11 | 654.5 |
| line-1-0742-0746-s010535 | 14 | 2 | 12 | 714.0 |
| line-1-0939-1100-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0412-0236-s012368 | 4 | 2 | 2 | 119.0 |
| line-2-0587-0350-s007689 | 10 | 4 | 6 | 357.0 |
| line-2-0643-0386-s006212 | 10 | 2 | 8 | 476.0 |
| line-2-0756-0460-s003198 | 10 | 2 | 8 | 476.0 |
| line-2-0876-0538-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0354-0936-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0424-0686-s007016 | 10 | 2 | 8 | 476.0 |
| line-3-0483-0563-s010023 | 10 | 2 | 8 | 476.0 |
| line-3-0513-0502-s011503 | 10 | 4 | 6 | 357.0 |
| line-3-0543-0440-s013027 | 10 | 2 | 8 | 476.0 |
| line-3-0587-0350-s015238 | 10 | 4 | 6 | 357.0 |
| line-3-0658-0201-s018877 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Taif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
