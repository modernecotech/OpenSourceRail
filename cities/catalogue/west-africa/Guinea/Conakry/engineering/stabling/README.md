# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 26 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0023-1227-s000000 | forward | 3 | pending |
| line-1 | line-1-0186-1061-s005634 | forward | 3 | pending |
| line-1 | line-1-0186-1061-s005634 | reverse | 3 | pending |
| line-1 | line-1-0381-0918-s011220 | forward | 3 | pending |
| line-1 | line-1-0381-0918-s011220 | reverse | 3 | pending |
| line-1 | line-1-0461-0801-s014246 | forward | 3 | pending |
| line-1 | line-1-0461-0801-s014246 | reverse | 3 | pending |
| line-1 | line-1-0534-0681-s017251 | forward | 3 | pending |
| line-1 | line-1-0534-0681-s017251 | reverse | 3 | pending |
| line-1 | line-1-0583-0595-s019466 | forward | 2 | pending |
| line-1 | line-1-0583-0595-s019466 | reverse | 2 | pending |
| line-1 | line-1-0690-0502-s022470 | forward | 2 | pending |
| line-1 | line-1-0690-0502-s022470 | reverse | 2 | pending |
| line-1 | line-1-0745-0386-s025263 | forward | 2 | pending |
| line-1 | line-1-0745-0386-s025263 | reverse | 2 | pending |
| line-1 | line-1-0790-0413-s026918 | reverse | 2 | pending |
| line-2 | line-2-0638-0556-s000000 | forward | 3 | pending |
| line-2 | line-2-0558-0552-s002259 | forward | 3 | pending |
| line-2 | line-2-0558-0552-s002259 | reverse | 3 | pending |
| line-2 | line-2-0493-0637-s004626 | forward | 3 | pending |
| line-2 | line-2-0493-0637-s004626 | reverse | 3 | pending |
| line-2 | line-2-0383-0720-s007631 | forward | 3 | pending |
| line-2 | line-2-0383-0720-s007631 | reverse | 3 | pending |
| line-2 | line-2-0219-0819-s013733 | forward | 3 | pending |
| line-2 | line-2-0219-0819-s013733 | reverse | 3 | pending |
| line-2 | line-2-0061-0925-s019835 | reverse | 2 | pending |
| line-3 | line-3-0289-0675-s000000 | forward | 1 | pending |
| line-3 | line-3-0289-0675-s000000 | reverse | 1 | pending |
| line-3 | line-3-0198-0773-s003498 | reverse | 1 | pending |
| line-3 | line-3-0267-0665-s007007 | forward | 1 | pending |
| line-3 | line-3-0354-0639-s008963 | forward | 1 | pending |
| line-3 | line-3-0354-0639-s008963 | reverse | 1 | pending |
| line-3 | line-3-0445-0622-s010924 | reverse | 1 | pending |
| line-3 | line-3-0557-0527-s013951 | reverse | 1 | pending |
| line-3 | line-3-0736-0359-s018986 | forward | 1 | pending |
| line-3 | line-3-0798-0350-s020937 | forward | 1 | pending |
| line-3 | line-3-0798-0350-s020937 | reverse | 1 | pending |
| line-3 | line-3-0694-0378-s024442 | reverse | 1 | pending |
| line-3 | line-3-0570-0502-s027949 | forward | 1 | pending |
| line-3 | line-3-0336-0645-s033814 | forward | 1 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Guinea/Conakry/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
