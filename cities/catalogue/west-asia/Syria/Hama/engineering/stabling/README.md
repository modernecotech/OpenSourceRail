# Station and depot overnight allocation

Plan: **38 trainsets at stations + 76 at depots = 114 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0708-0757-s020923 | 76 | 4,522.0 | 18 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0194-0142-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0432-0345-s007014 | station | forward | revenue | 1 |
| line-1 | line-1-0432-0345-s007014 | station | reverse | revenue | 1 |
| line-1 | line-1-0475-0454-s010036 | station | forward | revenue | 1 |
| line-1 | line-1-0475-0454-s010036 | station | reverse | revenue | 1 |
| line-1 | line-1-0541-0621-s015984 | station | forward | revenue | 1 |
| line-1 | line-1-0541-0621-s015984 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0551-s013769 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0551-s013769 | station | reverse | revenue | 1 |
| line-1 | line-1-0620-0708-s018465 | station | forward | revenue | 1 |
| line-1 | line-1-0620-0708-s018465 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0757-s020923 | station | reverse | revenue | 2 |
| line-2 | line-2-0313-0629-s011524 | station | reverse | revenue | 2 |
| line-2 | line-2-0369-0566-s009226 | station | forward | revenue | 1 |
| line-2 | line-2-0369-0566-s009226 | station | reverse | revenue | 1 |
| line-2 | line-2-0470-0534-s006925 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0534-s006925 | station | reverse | revenue | 1 |
| line-2 | line-2-0550-0551-s004625 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0551-s004625 | station | reverse | revenue | 1 |
| line-2 | line-2-0621-0545-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0621-0545-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0768-0539-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0504-0373-s007020 | station | forward | revenue | 1 |
| line-3 | line-3-0504-0373-s007020 | station | reverse | revenue | 1 |
| line-3 | line-3-0531-0651-s016060 | station | forward | revenue | 1 |
| line-3 | line-3-0531-0651-s016060 | station | reverse | revenue | 1 |
| line-3 | line-3-0550-0551-s013648 | station | forward | revenue | 1 |
| line-3 | line-3-0550-0551-s013648 | station | reverse | revenue | 1 |
| line-3 | line-3-0581-0072-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0586-0750-s018998 | station | reverse | revenue | 2 |
| line-3 | line-3-0616-0448-s010026 | station | forward | revenue | 1 |
| line-3 | line-3-0616-0448-s010026 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0757-s020923 | depot | — | revenue | 27 |
| line-1 | line-1-0708-0757-s020923 | depot | — | spare | 4 |
| line-1 | line-1-0708-0757-s020923 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0708-0757-s020923 | depot | — | revenue | 12 |
| line-2 | line-1-0708-0757-s020923 | depot | — | spare | 2 |
| line-2 | line-1-0708-0757-s020923 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0708-0757-s020923 | depot | — | revenue | 25 |
| line-3 | line-1-0708-0757-s020923 | depot | — | spare | 3 |
| line-3 | line-1-0708-0757-s020923 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (15 trains), line-3 (29 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **114 trainsets at 19 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **102 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **76 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0194-0142-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0432-0345-s007014 | forward | revenue | 4 | pending |
| line-1 | line-1-0432-0345-s007014 | reverse | revenue | 4 | pending |
| line-1 | line-1-0475-0454-s010036 | forward | revenue | 4 | pending |
| line-1 | line-1-0475-0454-s010036 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0551-s013769 | forward | revenue | 3 | pending |
| line-1 | line-1-0550-0551-s013769 | reverse | revenue | 3 | pending |
| line-1 | line-1-0541-0621-s015984 | forward | revenue | 3 | pending |
| line-1 | line-1-0541-0621-s015984 | reverse | revenue | 3 | pending |
| line-1 | line-1-0620-0708-s018465 | forward | revenue | 3 | pending |
| line-1 | line-1-0620-0708-s018465 | reverse | revenue | 3 | pending |
| line-1 | line-1-0708-0757-s020923 | reverse | revenue | 3 | pending |
| line-1 | line-1-0550-0551-s013769 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0551-s013769 | reverse | spare | 1 | pending |
| line-1 | line-1-0541-0621-s015984 | forward | spare | 1 | pending |
| line-1 | line-1-0541-0621-s015984 | reverse | spare | 1 | pending |
| line-1 | line-1-0620-0708-s018465 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0768-0539-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0621-0545-s003006 | forward | revenue | 3 | pending |
| line-2 | line-2-0621-0545-s003006 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0551-s004625 | forward | revenue | 3 | pending |
| line-2 | line-2-0550-0551-s004625 | reverse | revenue | 2 | pending |
| line-2 | line-2-0470-0534-s006925 | forward | revenue | 2 | pending |
| line-2 | line-2-0470-0534-s006925 | reverse | revenue | 2 | pending |
| line-2 | line-2-0369-0566-s009226 | forward | revenue | 2 | pending |
| line-2 | line-2-0369-0566-s009226 | reverse | revenue | 2 | pending |
| line-2 | line-2-0313-0629-s011524 | reverse | revenue | 2 | pending |
| line-2 | line-2-0550-0551-s004625 | reverse | spare | 1 | pending |
| line-2 | line-2-0470-0534-s006925 | forward | spare | 1 | pending |
| line-2 | line-2-0470-0534-s006925 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0581-0072-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0504-0373-s007020 | forward | revenue | 4 | pending |
| line-3 | line-3-0504-0373-s007020 | reverse | revenue | 4 | pending |
| line-3 | line-3-0616-0448-s010026 | forward | revenue | 4 | pending |
| line-3 | line-3-0616-0448-s010026 | reverse | revenue | 4 | pending |
| line-3 | line-3-0550-0551-s013648 | forward | revenue | 4 | pending |
| line-3 | line-3-0550-0551-s013648 | reverse | revenue | 4 | pending |
| line-3 | line-3-0531-0651-s016060 | forward | revenue | 3 | pending |
| line-3 | line-3-0531-0651-s016060 | reverse | revenue | 3 | pending |
| line-3 | line-3-0586-0750-s018998 | reverse | revenue | 3 | pending |
| line-3 | line-3-0531-0651-s016060 | forward | spare | 1 | pending |
| line-3 | line-3-0531-0651-s016060 | reverse | spare | 1 | pending |
| line-3 | line-3-0586-0750-s018998 | reverse | spare | 1 | pending |
| line-3 | line-3-0581-0072-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**70 trainsets exceed the reference platform envelope**, requiring **4,165.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0194-0142-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0432-0345-s007014 | 8 | 2 | 6 | 357.0 |
| line-1-0475-0454-s010036 | 8 | 2 | 6 | 357.0 |
| line-1-0541-0621-s015984 | 8 | 2 | 6 | 357.0 |
| line-1-0550-0551-s013769 | 8 | 4 | 4 | 238.0 |
| line-1-0620-0708-s018465 | 7 | 2 | 5 | 297.5 |
| line-1-0708-0757-s020923 | 3 | 2 | 1 | 59.5 |
| line-2-0313-0629-s011524 | 2 | 2 | 0 | 0.0 |
| line-2-0369-0566-s009226 | 4 | 2 | 2 | 119.0 |
| line-2-0470-0534-s006925 | 6 | 2 | 4 | 238.0 |
| line-2-0550-0551-s004625 | 6 | 4 | 2 | 119.0 |
| line-2-0621-0545-s003006 | 6 | 2 | 4 | 238.0 |
| line-2-0768-0539-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0504-0373-s007020 | 8 | 2 | 6 | 357.0 |
| line-3-0531-0651-s016060 | 8 | 2 | 6 | 357.0 |
| line-3-0550-0551-s013648 | 8 | 4 | 4 | 238.0 |
| line-3-0581-0072-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0586-0750-s018998 | 4 | 2 | 2 | 119.0 |
| line-3-0616-0448-s010026 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Hama/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
