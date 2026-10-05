# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 126 at depots = 166 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0325-0925-s000000 | line-1 | declared-depot | 31 | 1,844.5 | 7 |
| line-2-0859-1060-s022005 | line-2 | declared-depot | 55 | 3,272.5 | 10 |
| line-3-0764-0574-s000000 | line-3 | declared-depot | 40 | 2,380.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0325-0925-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0401-0809-s003020 | station | forward | revenue | 1 |
| line-1 | line-1-0401-0809-s003020 | station | reverse | revenue | 1 |
| line-1 | line-1-0449-0727-s005140 | station | forward | revenue | 1 |
| line-1 | line-1-0449-0727-s005140 | station | reverse | revenue | 1 |
| line-1 | line-1-0501-0639-s007424 | station | forward | revenue | 1 |
| line-1 | line-1-0501-0639-s007424 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0575-s009089 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0575-s009089 | station | reverse | revenue | 1 |
| line-1 | line-1-0590-0488-s011345 | station | forward | revenue | 1 |
| line-1 | line-1-0590-0488-s011345 | station | reverse | revenue | 1 |
| line-1 | line-1-0642-0400-s013595 | station | reverse | revenue | 2 |
| line-2 | line-2-0309-0394-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0422-0462-s003004 | station | forward | revenue | 1 |
| line-2 | line-2-0422-0462-s003004 | station | reverse | revenue | 1 |
| line-2 | line-2-0501-0639-s007808 | station | forward | revenue | 1 |
| line-2 | line-2-0501-0639-s007808 | station | reverse | revenue | 1 |
| line-2 | line-2-0506-0565-s006029 | station | forward | revenue | 1 |
| line-2 | line-2-0506-0565-s006029 | station | reverse | revenue | 1 |
| line-2 | line-2-0535-0683-s009040 | station | forward | revenue | 1 |
| line-2 | line-2-0535-0683-s009040 | station | reverse | revenue | 1 |
| line-2 | line-2-0631-0806-s012541 | station | forward | revenue | 1 |
| line-2 | line-2-0631-0806-s012541 | station | reverse | revenue | 1 |
| line-2 | line-2-0859-1060-s022005 | station | reverse | revenue | 2 |
| line-3 | line-3-0104-0927-s016891 | station | reverse | revenue | 2 |
| line-3 | line-3-0270-0813-s012083 | station | forward | revenue | 1 |
| line-3 | line-3-0270-0813-s012083 | station | reverse | revenue | 1 |
| line-3 | line-3-0449-0727-s007708 | station | forward | revenue | 1 |
| line-3 | line-3-0449-0727-s007708 | station | reverse | revenue | 1 |
| line-3 | line-3-0537-0684-s005568 | station | forward | revenue | 1 |
| line-3 | line-3-0537-0684-s005568 | station | reverse | revenue | 1 |
| line-3 | line-3-0641-0634-s003027 | station | forward | revenue | 1 |
| line-3 | line-3-0641-0634-s003027 | station | reverse | revenue | 1 |
| line-3 | line-3-0764-0574-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0325-0925-s000000 | depot | — | revenue | 26 |
| line-1 | line-1-0325-0925-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0325-0925-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0859-1060-s022005 | depot | — | revenue | 48 |
| line-2 | line-2-0859-1060-s022005 | depot | — | spare | 6 |
| line-2 | line-2-0859-1060-s022005 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0764-0574-s000000 | depot | — | revenue | 35 |
| line-3 | line-3-0764-0574-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0764-0574-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/bukavu-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **166 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **149 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **126 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0325-0925-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0809-s003020 | forward | revenue | 4 | pending |
| line-1 | line-1-0401-0809-s003020 | reverse | revenue | 4 | pending |
| line-1 | line-1-0449-0727-s005140 | forward | revenue | 4 | pending |
| line-1 | line-1-0449-0727-s005140 | reverse | revenue | 3 | pending |
| line-1 | line-1-0501-0639-s007424 | forward | revenue | 3 | pending |
| line-1 | line-1-0501-0639-s007424 | reverse | revenue | 3 | pending |
| line-1 | line-1-0539-0575-s009089 | forward | revenue | 3 | pending |
| line-1 | line-1-0539-0575-s009089 | reverse | revenue | 3 | pending |
| line-1 | line-1-0590-0488-s011345 | forward | revenue | 3 | pending |
| line-1 | line-1-0590-0488-s011345 | reverse | revenue | 3 | pending |
| line-1 | line-1-0642-0400-s013595 | reverse | revenue | 3 | pending |
| line-1 | line-1-0449-0727-s005140 | reverse | spare | 1 | pending |
| line-1 | line-1-0501-0639-s007424 | forward | spare | 1 | pending |
| line-1 | line-1-0501-0639-s007424 | reverse | spare | 1 | pending |
| line-1 | line-1-0539-0575-s009089 | forward | spare | 1 | pending |
| line-1 | line-1-0539-0575-s009089 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0309-0394-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0422-0462-s003004 | forward | revenue | 6 | pending |
| line-2 | line-2-0422-0462-s003004 | reverse | revenue | 5 | pending |
| line-2 | line-2-0506-0565-s006029 | forward | revenue | 5 | pending |
| line-2 | line-2-0506-0565-s006029 | reverse | revenue | 5 | pending |
| line-2 | line-2-0501-0639-s007808 | forward | revenue | 5 | pending |
| line-2 | line-2-0501-0639-s007808 | reverse | revenue | 5 | pending |
| line-2 | line-2-0535-0683-s009040 | forward | revenue | 5 | pending |
| line-2 | line-2-0535-0683-s009040 | reverse | revenue | 5 | pending |
| line-2 | line-2-0631-0806-s012541 | forward | revenue | 5 | pending |
| line-2 | line-2-0631-0806-s012541 | reverse | revenue | 5 | pending |
| line-2 | line-2-0859-1060-s022005 | reverse | revenue | 5 | pending |
| line-2 | line-2-0422-0462-s003004 | reverse | spare | 1 | pending |
| line-2 | line-2-0506-0565-s006029 | forward | spare | 1 | pending |
| line-2 | line-2-0506-0565-s006029 | reverse | spare | 1 | pending |
| line-2 | line-2-0501-0639-s007808 | forward | spare | 1 | pending |
| line-2 | line-2-0501-0639-s007808 | reverse | spare | 1 | pending |
| line-2 | line-2-0535-0683-s009040 | forward | spare | 1 | pending |
| line-2 | line-2-0535-0683-s009040 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0764-0574-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0641-0634-s003027 | forward | revenue | 5 | pending |
| line-3 | line-3-0641-0634-s003027 | reverse | revenue | 5 | pending |
| line-3 | line-3-0537-0684-s005568 | forward | revenue | 5 | pending |
| line-3 | line-3-0537-0684-s005568 | reverse | revenue | 5 | pending |
| line-3 | line-3-0449-0727-s007708 | forward | revenue | 5 | pending |
| line-3 | line-3-0449-0727-s007708 | reverse | revenue | 5 | pending |
| line-3 | line-3-0270-0813-s012083 | forward | revenue | 4 | pending |
| line-3 | line-3-0270-0813-s012083 | reverse | revenue | 4 | pending |
| line-3 | line-3-0104-0927-s016891 | reverse | revenue | 4 | pending |
| line-3 | line-3-0270-0813-s012083 | forward | spare | 1 | pending |
| line-3 | line-3-0270-0813-s012083 | reverse | spare | 1 | pending |
| line-3 | line-3-0104-0927-s016891 | reverse | spare | 1 | pending |
| line-3 | line-3-0764-0574-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0641-0634-s003027 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**110 trainsets exceed the reference platform envelope**, requiring **6,545.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0325-0925-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0401-0809-s003020 | 8 | 2 | 6 | 357.0 |
| line-1-0449-0727-s005140 | 8 | 4 | 4 | 238.0 |
| line-1-0501-0639-s007424 | 8 | 4 | 4 | 238.0 |
| line-1-0539-0575-s009089 | 8 | 4 | 4 | 238.0 |
| line-1-0590-0488-s011345 | 6 | 2 | 4 | 238.0 |
| line-1-0642-0400-s013595 | 3 | 2 | 1 | 59.5 |
| line-2-0309-0394-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0422-0462-s003004 | 12 | 2 | 10 | 595.0 |
| line-2-0501-0639-s007808 | 12 | 4 | 8 | 476.0 |
| line-2-0506-0565-s006029 | 12 | 4 | 8 | 476.0 |
| line-2-0535-0683-s009040 | 12 | 4 | 8 | 476.0 |
| line-2-0631-0806-s012541 | 10 | 2 | 8 | 476.0 |
| line-2-0859-1060-s022005 | 5 | 2 | 3 | 178.5 |
| line-3-0104-0927-s016891 | 5 | 2 | 3 | 178.5 |
| line-3-0270-0813-s012083 | 10 | 2 | 8 | 476.0 |
| line-3-0449-0727-s007708 | 10 | 4 | 6 | 357.0 |
| line-3-0537-0684-s005568 | 10 | 4 | 6 | 357.0 |
| line-3-0641-0634-s003027 | 11 | 2 | 9 | 535.5 |
| line-3-0764-0574-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Bukavu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
