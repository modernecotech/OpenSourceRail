# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **102 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **92 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

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
