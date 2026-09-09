# Station and depot overnight allocation

Plan: **20 trainsets at stations + 16 at depots = 36 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **FAIL**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0788-0713-s015879 | 16 | 1,360.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0788-0713-s015879 | station | reverse | revenue | 2 |
| line-1 | line-1-0855-0751-s012170 | station | forward | revenue | 1 |
| line-1 | line-1-0855-0751-s012170 | station | reverse | revenue | 1 |
| line-1 | line-1-0935-0749-s010321 | station | forward | revenue | 1 |
| line-1 | line-1-0935-0749-s010321 | station | reverse | revenue | 1 |
| line-1 | line-1-0992-0866-s007016 | station | forward | revenue | 1 |
| line-1 | line-1-0992-0866-s007016 | station | reverse | revenue | 1 |
| line-1 | line-1-1101-0959-s003498 | station | forward | revenue | 1 |
| line-1 | line-1-1101-0959-s003498 | station | reverse | revenue | 1 |
| line-1 | line-1-1244-1036-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0797-1060-s006024 | station | forward | revenue | 1 |
| line-2 | line-2-0801-0801-s000000 | station | forward | revenue | 1 |
| line-2 | line-2-0801-0801-s000000 | station | reverse | revenue | 1 |
| line-2 | line-2-0814-0932-s003009 | station | reverse | revenue | 1 |
| line-2 | line-2-0825-0977-s010999 | station | forward | revenue | 1 |
| line-2 | line-2-0825-0977-s010999 | station | reverse | revenue | 1 |
| line-2 | line-2-0830-1056-s009030 | station | forward | revenue | 1 |
| line-2 | line-2-0876-0899-s012981 | station | reverse | revenue | 1 |
| line-1 | line-1-0788-0713-s015879 | depot | — | revenue | 11 |
| line-1 | line-1-0788-0713-s015879 | depot | — | spare | 2 |
| line-1 | line-1-0788-0713-s015879 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0788-0713-s015879 | depot | — | spare | 1 |
| line-2 | line-1-0788-0713-s015879 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (2 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **36 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **31 revenue, 3 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **8 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **5 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1244-1036-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-1101-0959-s003498 | forward | revenue | 3 | pending |
| line-1 | line-1-1101-0959-s003498 | reverse | revenue | 3 | pending |
| line-1 | line-1-0992-0866-s007016 | forward | revenue | 2 | pending |
| line-1 | line-1-0992-0866-s007016 | reverse | revenue | 2 | pending |
| line-1 | line-1-0935-0749-s010321 | forward | revenue | 2 | pending |
| line-1 | line-1-0935-0749-s010321 | reverse | revenue | 2 | pending |
| line-1 | line-1-0855-0751-s012170 | forward | revenue | 2 | pending |
| line-1 | line-1-0855-0751-s012170 | reverse | revenue | 2 | pending |
| line-1 | line-1-0788-0713-s015879 | reverse | revenue | 2 | pending |
| line-1 | line-1-0992-0866-s007016 | forward | spare | 1 | pending |
| line-1 | line-1-0992-0866-s007016 | reverse | spare | 1 | pending |
| line-1 | line-1-0935-0749-s010321 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0801-0801-s000000 | forward | revenue | 1 | pending |
| line-2 | line-2-0801-0801-s000000 | reverse | revenue | 1 | pending |
| line-2 | line-2-0814-0932-s003009 | reverse | revenue | 1 | pending |
| line-2 | line-2-0797-1060-s006024 | forward | revenue | 1 | pending |
| line-2 | line-2-0830-1056-s009030 | forward | revenue | 1 | pending |
| line-2 | line-2-0825-0977-s010999 | forward | revenue | 1 | pending |
| line-2 | line-2-0825-0977-s010999 | reverse | revenue | 1 | pending |
| line-2 | line-2-0876-0899-s012981 | reverse | revenue | 1 | pending |
| line-2 | line-2-0855-0751-s016569 | forward | spare | 1 | pending |
| line-2 | line-2-0788-0713-s020302 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**12 trainsets exceed the reference platform envelope**, requiring **1,020.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0788-0713-s015879 | 2 | 2 | 0 | 0.0 |
| line-1-0855-0751-s012170 | 4 | 4 | 0 | 0.0 |
| line-1-0935-0749-s010321 | 5 | 2 | 3 | 255.0 |
| line-1-0992-0866-s007016 | 6 | 2 | 4 | 340.0 |
| line-1-1101-0959-s003498 | 6 | 2 | 4 | 340.0 |
| line-1-1244-1036-s000000 | 3 | 2 | 1 | 85.0 |
| line-2-0788-0713-s020302 | 1 | 4 | 0 | 0.0 |
| line-2-0797-1060-s006024 | 1 | 2 | 0 | 0.0 |
| line-2-0801-0801-s000000 | 2 | 2 | 0 | 0.0 |
| line-2-0814-0932-s003009 | 1 | 2 | 0 | 0.0 |
| line-2-0825-0977-s010999 | 2 | 2 | 0 | 0.0 |
| line-2-0830-1056-s009030 | 1 | 2 | 0 | 0.0 |
| line-2-0855-0751-s016569 | 1 | 4 | 0 | 0.0 |
| line-2-0876-0899-s012981 | 1 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Kananga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
