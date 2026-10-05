# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **19 trainsets at stations + 15 at depots = 34 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **FAIL**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0788-0713-s012557 | line-1 | declared-depot | 13 | 1,105.0 | 4 |
| line-2-0801-0801-s000000 | line-2 | declared-depot | 2 | 170.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0788-0713-s012557 | station | reverse | revenue | 2 |
| line-1 | line-1-0855-0760-s010734 | station | forward | revenue | 1 |
| line-1 | line-1-0855-0760-s010734 | station | reverse | revenue | 1 |
| line-1 | line-1-0989-0856-s007013 | station | forward | revenue | 1 |
| line-1 | line-1-0989-0856-s007013 | station | reverse | revenue | 1 |
| line-1 | line-1-1116-0945-s003513 | station | forward | revenue | 1 |
| line-1 | line-1-1116-0945-s003513 | station | reverse | revenue | 1 |
| line-1 | line-1-1244-1036-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0798-1029-s006033 | station | forward | revenue | 1 |
| line-2 | line-2-0798-1029-s006033 | station | reverse | revenue | 1 |
| line-2 | line-2-0801-0801-s000000 | station | forward | revenue | 1 |
| line-2 | line-2-0801-0801-s000000 | station | reverse | revenue | 1 |
| line-2 | line-2-0816-0916-s003019 | station | forward | revenue | 1 |
| line-2 | line-2-0825-0986-s012051 | station | forward | revenue | 1 |
| line-2 | line-2-0849-1090-s009038 | station | reverse | revenue | 1 |
| line-2 | line-2-0898-0870-s015079 | station | forward | revenue | 1 |
| line-2 | line-2-0898-0870-s015079 | station | reverse | revenue | 1 |
| line-1 | line-1-0788-0713-s012557 | depot | — | revenue | 10 |
| line-1 | line-1-0788-0713-s012557 | depot | — | spare | 2 |
| line-1 | line-1-0788-0713-s012557 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0801-0801-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0801-0801-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate unavailable: morning station allocation is incomplete.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **34 trainsets at 13 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **29 revenue, 3 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **8 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **4 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1244-1036-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-1116-0945-s003513 | forward | revenue | 3 | pending |
| line-1 | line-1-1116-0945-s003513 | reverse | revenue | 3 | pending |
| line-1 | line-1-0989-0856-s007013 | forward | revenue | 3 | pending |
| line-1 | line-1-0989-0856-s007013 | reverse | revenue | 2 | pending |
| line-1 | line-1-0855-0760-s010734 | forward | revenue | 2 | pending |
| line-1 | line-1-0855-0760-s010734 | reverse | revenue | 2 | pending |
| line-1 | line-1-0788-0713-s012557 | reverse | revenue | 2 | pending |
| line-1 | line-1-0989-0856-s007013 | reverse | spare | 1 | pending |
| line-1 | line-1-0855-0760-s010734 | forward | spare | 1 | pending |
| line-1 | line-1-0855-0760-s010734 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0801-0801-s000000 | forward | revenue | 1 | pending |
| line-2 | line-2-0801-0801-s000000 | reverse | revenue | 1 | pending |
| line-2 | line-2-0816-0916-s003019 | forward | revenue | 1 | pending |
| line-2 | line-2-0798-1029-s006033 | forward | revenue | 1 | pending |
| line-2 | line-2-0798-1029-s006033 | reverse | revenue | 1 | pending |
| line-2 | line-2-0849-1090-s009038 | reverse | revenue | 1 | pending |
| line-2 | line-2-0825-0986-s012051 | forward | revenue | 1 | pending |
| line-2 | line-2-0898-0870-s015079 | forward | revenue | 1 | pending |
| line-2 | line-2-0898-0870-s015079 | reverse | revenue | 1 | pending |
| line-2 | line-2-0855-0760-s017905 | reverse | spare | 1 | pending |
| line-2 | line-2-0788-0713-s021930 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**11 trainsets exceed the reference platform envelope**, requiring **935.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0788-0713-s012557 | 2 | 2 | 0 | 0.0 |
| line-1-0855-0760-s010734 | 6 | 4 | 2 | 170.0 |
| line-1-0989-0856-s007013 | 6 | 2 | 4 | 340.0 |
| line-1-1116-0945-s003513 | 6 | 2 | 4 | 340.0 |
| line-1-1244-1036-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0788-0713-s021930 | 1 | 4 | 0 | 0.0 |
| line-2-0798-1029-s006033 | 2 | 2 | 0 | 0.0 |
| line-2-0801-0801-s000000 | 2 | 2 | 0 | 0.0 |
| line-2-0816-0916-s003019 | 1 | 2 | 0 | 0.0 |
| line-2-0825-0986-s012051 | 1 | 2 | 0 | 0.0 |
| line-2-0849-1090-s009038 | 1 | 2 | 0 | 0.0 |
| line-2-0855-0760-s017905 | 1 | 4 | 0 | 0.0 |
| line-2-0898-0870-s015079 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Kananga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
