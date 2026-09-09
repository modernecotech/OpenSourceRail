# Station and depot overnight allocation

Plan: **20 trainsets at stations + 62 at depots = 82 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0756-0267-s019958 | 62 | 3,689.0 | 13 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0469-1000-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0550-0551-s010961 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0551-s010961 | station | reverse | revenue | 1 |
| line-1 | line-1-0556-0468-s013046 | station | forward | revenue | 1 |
| line-1 | line-1-0556-0468-s013046 | station | reverse | revenue | 1 |
| line-1 | line-1-0581-0706-s007007 | station | forward | revenue | 1 |
| line-1 | line-1-0581-0706-s007007 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0618-s008991 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0618-s008991 | station | reverse | revenue | 1 |
| line-1 | line-1-0756-0267-s019958 | station | reverse | revenue | 2 |
| line-2 | line-2-0487-0999-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0488-0674-s007012 | station | forward | revenue | 1 |
| line-2 | line-2-0488-0674-s007012 | station | reverse | revenue | 1 |
| line-2 | line-2-0538-0417-s014181 | station | reverse | revenue | 2 |
| line-2 | line-2-0550-0551-s010619 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0551-s010619 | station | reverse | revenue | 1 |
| line-1 | line-1-0756-0267-s019958 | depot | — | revenue | 30 |
| line-1 | line-1-0756-0267-s019958 | depot | — | spare | 4 |
| line-1 | line-1-0756-0267-s019958 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0756-0267-s019958 | depot | — | revenue | 23 |
| line-2 | line-1-0756-0267-s019958 | depot | — | spare | 3 |
| line-2 | line-1-0756-0267-s019958 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (27 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **82 trainsets at 10 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **73 revenue, 7 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **62 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **10 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0469-1000-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0581-0706-s007007 | forward | revenue | 5 | pending |
| line-1 | line-1-0581-0706-s007007 | reverse | revenue | 4 | pending |
| line-1 | line-1-0588-0618-s008991 | forward | revenue | 4 | pending |
| line-1 | line-1-0588-0618-s008991 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0551-s010961 | forward | revenue | 4 | pending |
| line-1 | line-1-0550-0551-s010961 | reverse | revenue | 4 | pending |
| line-1 | line-1-0556-0468-s013046 | forward | revenue | 4 | pending |
| line-1 | line-1-0556-0468-s013046 | reverse | revenue | 4 | pending |
| line-1 | line-1-0756-0267-s019958 | reverse | revenue | 4 | pending |
| line-1 | line-1-0581-0706-s007007 | reverse | spare | 1 | pending |
| line-1 | line-1-0588-0618-s008991 | forward | spare | 1 | pending |
| line-1 | line-1-0588-0618-s008991 | reverse | spare | 1 | pending |
| line-1 | line-1-0550-0551-s010961 | forward | spare | 1 | pending |
| line-1 | line-1-0550-0551-s010961 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0487-0999-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0488-0674-s007012 | forward | revenue | 5 | pending |
| line-2 | line-2-0488-0674-s007012 | reverse | revenue | 5 | pending |
| line-2 | line-2-0550-0551-s010619 | forward | revenue | 5 | pending |
| line-2 | line-2-0550-0551-s010619 | reverse | revenue | 5 | pending |
| line-2 | line-2-0538-0417-s014181 | reverse | revenue | 5 | pending |
| line-2 | line-2-0488-0674-s007012 | forward | spare | 1 | pending |
| line-2 | line-2-0488-0674-s007012 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0551-s010619 | forward | spare | 1 | pending |
| line-2 | line-2-0550-0551-s010619 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**58 trainsets exceed the reference platform envelope**, requiring **3,451.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0469-1000-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0550-0551-s010961 | 10 | 4 | 6 | 357.0 |
| line-1-0556-0468-s013046 | 8 | 2 | 6 | 357.0 |
| line-1-0581-0706-s007007 | 10 | 2 | 8 | 476.0 |
| line-1-0588-0618-s008991 | 10 | 2 | 8 | 476.0 |
| line-1-0756-0267-s019958 | 4 | 2 | 2 | 119.0 |
| line-2-0487-0999-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0488-0674-s007012 | 12 | 2 | 10 | 595.0 |
| line-2-0538-0417-s014181 | 5 | 2 | 3 | 178.5 |
| line-2-0550-0551-s010619 | 12 | 4 | 8 | 476.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Chimoio/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
