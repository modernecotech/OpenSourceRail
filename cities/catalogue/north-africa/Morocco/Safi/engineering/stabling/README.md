# Station and depot overnight allocation

Plan: **34 trainsets at stations + 52 at depots = 86 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0400-0426-s019811 | 52 | 3,094.0 | 13 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0400-0426-s019811 | station | reverse | revenue | 2 |
| line-1 | line-1-0443-0496-s017916 | station | forward | revenue | 1 |
| line-1 | line-1-0443-0496-s017916 | station | reverse | revenue | 1 |
| line-1 | line-1-0519-0519-s016045 | station | forward | revenue | 1 |
| line-1 | line-1-0519-0519-s016045 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0553-s014466 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0553-s014466 | station | reverse | revenue | 1 |
| line-1 | line-1-0578-0612-s013038 | station | forward | revenue | 1 |
| line-1 | line-1-0578-0612-s013038 | station | reverse | revenue | 1 |
| line-1 | line-1-0653-0671-s010014 | station | forward | revenue | 1 |
| line-1 | line-1-0653-0671-s010014 | station | reverse | revenue | 1 |
| line-1 | line-1-0929-1021-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0398-0611-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0490-0576-s002191 | station | forward | revenue | 1 |
| line-2 | line-2-0490-0576-s002191 | station | reverse | revenue | 1 |
| line-2 | line-2-0553-0553-s004099 | station | forward | revenue | 1 |
| line-2 | line-2-0553-0553-s004099 | station | reverse | revenue | 1 |
| line-2 | line-2-0639-0513-s006831 | station | forward | revenue | 1 |
| line-2 | line-2-0639-0513-s006831 | station | reverse | revenue | 1 |
| line-2 | line-2-0760-0495-s010364 | station | reverse | revenue | 2 |
| line-3 | line-3-0543-0652-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0553-0553-s002186 | station | forward | revenue | 1 |
| line-3 | line-3-0553-0553-s002186 | station | reverse | revenue | 1 |
| line-3 | line-3-0654-0562-s004474 | station | forward | revenue | 1 |
| line-3 | line-3-0654-0562-s004474 | station | reverse | revenue | 1 |
| line-3 | line-3-0754-0544-s006779 | station | forward | revenue | 1 |
| line-3 | line-3-0754-0544-s006779 | station | reverse | revenue | 1 |
| line-3 | line-3-0835-0476-s009080 | station | reverse | revenue | 2 |
| line-1 | line-1-0400-0426-s019811 | depot | — | revenue | 25 |
| line-1 | line-1-0400-0426-s019811 | depot | — | spare | 3 |
| line-1 | line-1-0400-0426-s019811 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0400-0426-s019811 | depot | — | revenue | 10 |
| line-2 | line-1-0400-0426-s019811 | depot | — | spare | 2 |
| line-2 | line-1-0400-0426-s019811 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0400-0426-s019811 | depot | — | revenue | 8 |
| line-3 | line-1-0400-0426-s019811 | depot | — | spare | 1 |
| line-3 | line-1-0400-0426-s019811 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (13 trains), line-3 (10 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **86 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **77 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **52 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0929-1021-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0653-0671-s010014 | forward | revenue | 4 | pending |
| line-1 | line-1-0653-0671-s010014 | reverse | revenue | 4 | pending |
| line-1 | line-1-0578-0612-s013038 | forward | revenue | 3 | pending |
| line-1 | line-1-0578-0612-s013038 | reverse | revenue | 3 | pending |
| line-1 | line-1-0553-0553-s014466 | forward | revenue | 3 | pending |
| line-1 | line-1-0553-0553-s014466 | reverse | revenue | 3 | pending |
| line-1 | line-1-0519-0519-s016045 | forward | revenue | 3 | pending |
| line-1 | line-1-0519-0519-s016045 | reverse | revenue | 3 | pending |
| line-1 | line-1-0443-0496-s017916 | forward | revenue | 3 | pending |
| line-1 | line-1-0443-0496-s017916 | reverse | revenue | 3 | pending |
| line-1 | line-1-0400-0426-s019811 | reverse | revenue | 3 | pending |
| line-1 | line-1-0578-0612-s013038 | forward | spare | 1 | pending |
| line-1 | line-1-0578-0612-s013038 | reverse | spare | 1 | pending |
| line-1 | line-1-0553-0553-s014466 | forward | spare | 1 | pending |
| line-1 | line-1-0553-0553-s014466 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0398-0611-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0490-0576-s002191 | forward | revenue | 3 | pending |
| line-2 | line-2-0490-0576-s002191 | reverse | revenue | 3 | pending |
| line-2 | line-2-0553-0553-s004099 | forward | revenue | 3 | pending |
| line-2 | line-2-0553-0553-s004099 | reverse | revenue | 2 | pending |
| line-2 | line-2-0639-0513-s006831 | forward | revenue | 2 | pending |
| line-2 | line-2-0639-0513-s006831 | reverse | revenue | 2 | pending |
| line-2 | line-2-0760-0495-s010364 | reverse | revenue | 2 | pending |
| line-2 | line-2-0553-0553-s004099 | reverse | spare | 1 | pending |
| line-2 | line-2-0639-0513-s006831 | forward | spare | 1 | pending |
| line-2 | line-2-0639-0513-s006831 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0543-0652-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0553-0553-s002186 | forward | revenue | 3 | pending |
| line-3 | line-3-0553-0553-s002186 | reverse | revenue | 2 | pending |
| line-3 | line-3-0654-0562-s004474 | forward | revenue | 2 | pending |
| line-3 | line-3-0654-0562-s004474 | reverse | revenue | 2 | pending |
| line-3 | line-3-0754-0544-s006779 | forward | revenue | 2 | pending |
| line-3 | line-3-0754-0544-s006779 | reverse | revenue | 2 | pending |
| line-3 | line-3-0835-0476-s009080 | reverse | revenue | 2 | pending |
| line-3 | line-3-0553-0553-s002186 | reverse | spare | 1 | pending |
| line-3 | line-3-0654-0562-s004474 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**46 trainsets exceed the reference platform envelope**, requiring **2,737.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0400-0426-s019811 | 3 | 2 | 1 | 59.5 |
| line-1-0443-0496-s017916 | 6 | 2 | 4 | 238.0 |
| line-1-0519-0519-s016045 | 6 | 2 | 4 | 238.0 |
| line-1-0553-0553-s014466 | 8 | 4 | 4 | 238.0 |
| line-1-0578-0612-s013038 | 8 | 2 | 6 | 357.0 |
| line-1-0653-0671-s010014 | 8 | 2 | 6 | 357.0 |
| line-1-0929-1021-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0398-0611-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0490-0576-s002191 | 6 | 2 | 4 | 238.0 |
| line-2-0553-0553-s004099 | 6 | 4 | 2 | 119.0 |
| line-2-0639-0513-s006831 | 6 | 2 | 4 | 238.0 |
| line-2-0760-0495-s010364 | 2 | 2 | 0 | 0.0 |
| line-3-0543-0652-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0553-0553-s002186 | 6 | 4 | 2 | 119.0 |
| line-3-0654-0562-s004474 | 5 | 2 | 3 | 178.5 |
| line-3-0754-0544-s006779 | 4 | 2 | 2 | 119.0 |
| line-3-0835-0476-s009080 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Safi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
