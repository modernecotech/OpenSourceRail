# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 26 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **75 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0023-1227-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0186-1061-s005634 | forward | revenue | 3 | pending |
| line-1 | line-1-0186-1061-s005634 | reverse | revenue | 3 | pending |
| line-1 | line-1-0381-0918-s011220 | forward | revenue | 3 | pending |
| line-1 | line-1-0381-0918-s011220 | reverse | revenue | 3 | pending |
| line-1 | line-1-0461-0801-s014246 | forward | revenue | 2 | pending |
| line-1 | line-1-0461-0801-s014246 | reverse | revenue | 2 | pending |
| line-1 | line-1-0534-0681-s017251 | forward | revenue | 2 | pending |
| line-1 | line-1-0534-0681-s017251 | reverse | revenue | 2 | pending |
| line-1 | line-1-0583-0595-s019466 | forward | revenue | 2 | pending |
| line-1 | line-1-0583-0595-s019466 | reverse | revenue | 2 | pending |
| line-1 | line-1-0690-0502-s022470 | forward | revenue | 2 | pending |
| line-1 | line-1-0690-0502-s022470 | reverse | revenue | 2 | pending |
| line-1 | line-1-0745-0386-s025263 | forward | revenue | 2 | pending |
| line-1 | line-1-0745-0386-s025263 | reverse | revenue | 2 | pending |
| line-1 | line-1-0790-0413-s026918 | reverse | revenue | 2 | pending |
| line-1 | line-1-0461-0801-s014246 | forward | spare | 1 | pending |
| line-1 | line-1-0461-0801-s014246 | reverse | spare | 1 | pending |
| line-1 | line-1-0534-0681-s017251 | forward | spare | 1 | pending |
| line-1 | line-1-0534-0681-s017251 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0638-0556-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0552-s002259 | forward | revenue | 3 | pending |
| line-2 | line-2-0558-0552-s002259 | reverse | revenue | 3 | pending |
| line-2 | line-2-0493-0637-s004626 | forward | revenue | 3 | pending |
| line-2 | line-2-0493-0637-s004626 | reverse | revenue | 3 | pending |
| line-2 | line-2-0383-0720-s007631 | forward | revenue | 3 | pending |
| line-2 | line-2-0383-0720-s007631 | reverse | revenue | 2 | pending |
| line-2 | line-2-0219-0819-s013733 | forward | revenue | 2 | pending |
| line-2 | line-2-0219-0819-s013733 | reverse | revenue | 2 | pending |
| line-2 | line-2-0061-0925-s019835 | reverse | revenue | 2 | pending |
| line-2 | line-2-0383-0720-s007631 | reverse | spare | 1 | pending |
| line-2 | line-2-0219-0819-s013733 | forward | spare | 1 | pending |
| line-2 | line-2-0219-0819-s013733 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0289-0675-s000000 | forward | revenue | 1 | pending |
| line-3 | line-3-0289-0675-s000000 | reverse | revenue | 1 | pending |
| line-3 | line-3-0198-0773-s003498 | reverse | revenue | 1 | pending |
| line-3 | line-3-0267-0665-s007007 | forward | revenue | 1 | pending |
| line-3 | line-3-0354-0639-s008963 | forward | revenue | 1 | pending |
| line-3 | line-3-0354-0639-s008963 | reverse | revenue | 1 | pending |
| line-3 | line-3-0445-0622-s010924 | reverse | revenue | 1 | pending |
| line-3 | line-3-0557-0527-s013951 | reverse | revenue | 1 | pending |
| line-3 | line-3-0736-0359-s018986 | forward | revenue | 1 | pending |
| line-3 | line-3-0798-0350-s020937 | forward | revenue | 1 | pending |
| line-3 | line-3-0798-0350-s020937 | reverse | revenue | 1 | pending |
| line-3 | line-3-0694-0378-s024442 | reverse | revenue | 1 | pending |
| line-3 | line-3-0570-0502-s027949 | forward | spare | 1 | pending |
| line-3 | line-3-0336-0645-s033814 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**36 trainsets exceed the reference platform envelope**, requiring **3,060.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0023-1227-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0186-1061-s005634 | 6 | 2 | 4 | 340.0 |
| line-1-0381-0918-s011220 | 6 | 2 | 4 | 340.0 |
| line-1-0461-0801-s014246 | 6 | 2 | 4 | 340.0 |
| line-1-0534-0681-s017251 | 6 | 2 | 4 | 340.0 |
| line-1-0583-0595-s019466 | 4 | 2 | 2 | 170.0 |
| line-1-0690-0502-s022470 | 4 | 2 | 2 | 170.0 |
| line-1-0745-0386-s025263 | 4 | 4 | 0 | 0.0 |
| line-1-0790-0413-s026918 | 2 | 2 | 0 | 0.0 |
| line-2-0061-0925-s019835 | 2 | 2 | 0 | 0.0 |
| line-2-0219-0819-s013733 | 6 | 2 | 4 | 340.0 |
| line-2-0383-0720-s007631 | 6 | 2 | 4 | 340.0 |
| line-2-0493-0637-s004626 | 6 | 2 | 4 | 340.0 |
| line-2-0558-0552-s002259 | 6 | 4 | 2 | 170.0 |
| line-2-0638-0556-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0198-0773-s003498 | 1 | 2 | 0 | 0.0 |
| line-3-0267-0665-s007007 | 1 | 2 | 0 | 0.0 |
| line-3-0289-0675-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0336-0645-s033814 | 1 | 2 | 0 | 0.0 |
| line-3-0354-0639-s008963 | 2 | 2 | 0 | 0.0 |
| line-3-0445-0622-s010924 | 1 | 2 | 0 | 0.0 |
| line-3-0557-0527-s013951 | 1 | 4 | 0 | 0.0 |
| line-3-0570-0502-s027949 | 1 | 2 | 0 | 0.0 |
| line-3-0694-0378-s024442 | 1 | 2 | 0 | 0.0 |
| line-3-0736-0359-s018986 | 1 | 4 | 0 | 0.0 |
| line-3-0798-0350-s020937 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Guinea/Conakry/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
