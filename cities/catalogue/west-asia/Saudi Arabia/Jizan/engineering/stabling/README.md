# Station and depot overnight allocation

Plan: **34 trainsets at stations + 68 at depots = 102 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0057-0560-s020895 | line-1 | declared-depot | 31 | 1,844.5 | 16 |
| line-2-0435-0789-s007884 | line-2 | storage-at-existing-powered-service-point | 10 | 595.0 | 0 |
| line-3-0382-0565-s019081 | line-3 | storage-at-existing-powered-service-point | 27 | 1,606.5 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0057-0560-s020895 | station | reverse | revenue | 2 |
| line-1 | line-1-0216-0505-s016674 | station | forward | revenue | 1 |
| line-1 | line-1-0216-0505-s016674 | station | reverse | revenue | 1 |
| line-1 | line-1-0387-0550-s012473 | station | forward | revenue | 1 |
| line-1 | line-1-0387-0550-s012473 | station | reverse | revenue | 1 |
| line-1 | line-1-0539-0573-s008852 | station | forward | revenue | 1 |
| line-1 | line-1-0539-0573-s008852 | station | reverse | revenue | 1 |
| line-1 | line-1-0633-0625-s006436 | station | forward | revenue | 1 |
| line-1 | line-1-0633-0625-s006436 | station | reverse | revenue | 1 |
| line-1 | line-1-0857-0824-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0435-0789-s007884 | station | reverse | revenue | 2 |
| line-2 | line-2-0494-0687-s005227 | station | forward | revenue | 1 |
| line-2 | line-2-0494-0687-s005227 | station | reverse | revenue | 1 |
| line-2 | line-2-0528-0461-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0539-0573-s002557 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0573-s002557 | station | reverse | revenue | 1 |
| line-3 | line-3-0382-0565-s019081 | station | reverse | revenue | 2 |
| line-3 | line-3-0458-0579-s017094 | station | forward | revenue | 1 |
| line-3 | line-3-0458-0579-s017094 | station | reverse | revenue | 1 |
| line-3 | line-3-0539-0573-s015110 | station | forward | revenue | 1 |
| line-3 | line-3-0539-0573-s015110 | station | reverse | revenue | 1 |
| line-3 | line-3-0562-0661-s013159 | station | forward | revenue | 1 |
| line-3 | line-3-0562-0661-s013159 | station | reverse | revenue | 1 |
| line-3 | line-3-0664-0741-s010152 | station | forward | revenue | 1 |
| line-3 | line-3-0664-0741-s010152 | station | reverse | revenue | 1 |
| line-3 | line-3-0786-0848-s006825 | station | forward | revenue | 1 |
| line-3 | line-3-0786-0848-s006825 | station | reverse | revenue | 1 |
| line-3 | line-3-0953-1061-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0057-0560-s020895 | depot | — | revenue | 27 |
| line-1 | line-1-0057-0560-s020895 | depot | — | spare | 3 |
| line-1 | line-1-0057-0560-s020895 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0435-0789-s007884 | depot | — | revenue | 8 |
| line-2 | line-2-0435-0789-s007884 | depot | — | spare | 1 |
| line-2 | line-2-0435-0789-s007884 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0382-0565-s019081 | depot | — | revenue | 23 |
| line-3 | line-3-0382-0565-s019081 | depot | — | spare | 3 |
| line-3 | line-3-0382-0565-s019081 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jizan-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **102 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **92 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **68 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0857-0824-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0633-0625-s006436 | forward | revenue | 4 | pending |
| line-1 | line-1-0633-0625-s006436 | reverse | revenue | 4 | pending |
| line-1 | line-1-0539-0573-s008852 | forward | revenue | 4 | pending |
| line-1 | line-1-0539-0573-s008852 | reverse | revenue | 4 | pending |
| line-1 | line-1-0387-0550-s012473 | forward | revenue | 4 | pending |
| line-1 | line-1-0387-0550-s012473 | reverse | revenue | 4 | pending |
| line-1 | line-1-0216-0505-s016674 | forward | revenue | 4 | pending |
| line-1 | line-1-0216-0505-s016674 | reverse | revenue | 4 | pending |
| line-1 | line-1-0057-0560-s020895 | reverse | revenue | 3 | pending |
| line-1 | line-1-0057-0560-s020895 | reverse | spare | 1 | pending |
| line-1 | line-1-0857-0824-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0633-0625-s006436 | forward | spare | 1 | pending |
| line-1 | line-1-0633-0625-s006436 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0528-0461-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0539-0573-s002557 | forward | revenue | 3 | pending |
| line-2 | line-2-0539-0573-s002557 | reverse | revenue | 3 | pending |
| line-2 | line-2-0494-0687-s005227 | forward | revenue | 3 | pending |
| line-2 | line-2-0494-0687-s005227 | reverse | revenue | 2 | pending |
| line-2 | line-2-0435-0789-s007884 | reverse | revenue | 2 | pending |
| line-2 | line-2-0494-0687-s005227 | reverse | spare | 1 | pending |
| line-2 | line-2-0435-0789-s007884 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0953-1061-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0786-0848-s006825 | forward | revenue | 3 | pending |
| line-3 | line-3-0786-0848-s006825 | reverse | revenue | 3 | pending |
| line-3 | line-3-0664-0741-s010152 | forward | revenue | 3 | pending |
| line-3 | line-3-0664-0741-s010152 | reverse | revenue | 3 | pending |
| line-3 | line-3-0562-0661-s013159 | forward | revenue | 3 | pending |
| line-3 | line-3-0562-0661-s013159 | reverse | revenue | 3 | pending |
| line-3 | line-3-0539-0573-s015110 | forward | revenue | 3 | pending |
| line-3 | line-3-0539-0573-s015110 | reverse | revenue | 3 | pending |
| line-3 | line-3-0458-0579-s017094 | forward | revenue | 3 | pending |
| line-3 | line-3-0458-0579-s017094 | reverse | revenue | 3 | pending |
| line-3 | line-3-0382-0565-s019081 | reverse | revenue | 3 | pending |
| line-3 | line-3-0786-0848-s006825 | forward | spare | 1 | pending |
| line-3 | line-3-0786-0848-s006825 | reverse | spare | 1 | pending |
| line-3 | line-3-0664-0741-s010152 | forward | spare | 1 | pending |
| line-3 | line-3-0664-0741-s010152 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**60 trainsets exceed the reference platform envelope**, requiring **3,570.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0057-0560-s020895 | 4 | 2 | 2 | 119.0 |
| line-1-0216-0505-s016674 | 8 | 2 | 6 | 357.0 |
| line-1-0387-0550-s012473 | 8 | 4 | 4 | 238.0 |
| line-1-0539-0573-s008852 | 8 | 4 | 4 | 238.0 |
| line-1-0633-0625-s006436 | 10 | 2 | 8 | 476.0 |
| line-1-0857-0824-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0435-0789-s007884 | 3 | 2 | 1 | 59.5 |
| line-2-0494-0687-s005227 | 6 | 2 | 4 | 238.0 |
| line-2-0528-0461-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0539-0573-s002557 | 6 | 4 | 2 | 119.0 |
| line-3-0382-0565-s019081 | 3 | 2 | 1 | 59.5 |
| line-3-0458-0579-s017094 | 6 | 2 | 4 | 238.0 |
| line-3-0539-0573-s015110 | 6 | 4 | 2 | 119.0 |
| line-3-0562-0661-s013159 | 6 | 2 | 4 | 238.0 |
| line-3-0664-0741-s010152 | 8 | 2 | 6 | 357.0 |
| line-3-0786-0848-s006825 | 8 | 2 | 6 | 357.0 |
| line-3-0953-1061-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Jizan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
