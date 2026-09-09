# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **119 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0601-0847-s000000 | forward | 4 | pending |
| line-1 | line-1-0578-0714-s003007 | forward | 3 | pending |
| line-1 | line-1-0578-0714-s003007 | reverse | 3 | pending |
| line-1 | line-1-0550-0652-s006018 | forward | 3 | pending |
| line-1 | line-1-0550-0652-s006018 | reverse | 3 | pending |
| line-1 | line-1-0546-0559-s008210 | forward | 3 | pending |
| line-1 | line-1-0546-0559-s008210 | reverse | 3 | pending |
| line-1 | line-1-0527-0507-s010648 | forward | 3 | pending |
| line-1 | line-1-0527-0507-s010648 | reverse | 3 | pending |
| line-1 | line-1-0443-0438-s013087 | forward | 3 | pending |
| line-1 | line-1-0443-0438-s013087 | reverse | 3 | pending |
| line-1 | line-1-0417-0352-s015517 | reverse | 3 | pending |
| line-2 | line-2-0179-0919-s000000 | forward | 4 | pending |
| line-2 | line-2-0365-0785-s007018 | forward | 4 | pending |
| line-2 | line-2-0365-0785-s007018 | reverse | 4 | pending |
| line-2 | line-2-0421-0694-s010034 | forward | 4 | pending |
| line-2 | line-2-0421-0694-s010034 | reverse | 3 | pending |
| line-2 | line-2-0434-0624-s011908 | forward | 3 | pending |
| line-2 | line-2-0434-0624-s011908 | reverse | 3 | pending |
| line-2 | line-2-0495-0578-s013509 | forward | 3 | pending |
| line-2 | line-2-0495-0578-s013509 | reverse | 3 | pending |
| line-2 | line-2-0546-0559-s014981 | forward | 3 | pending |
| line-2 | line-2-0546-0559-s014981 | reverse | 3 | pending |
| line-2 | line-2-0600-0537-s016513 | forward | 3 | pending |
| line-2 | line-2-0600-0537-s016513 | reverse | 3 | pending |
| line-2 | line-2-0659-0493-s018528 | forward | 3 | pending |
| line-2 | line-2-0659-0493-s018528 | reverse | 3 | pending |
| line-2 | line-2-0749-0477-s020544 | forward | 3 | pending |
| line-2 | line-2-0749-0477-s020544 | reverse | 3 | pending |
| line-2 | line-2-0777-0419-s022545 | reverse | 3 | pending |
| line-3 | line-3-0805-0639-s000000 | forward | 4 | pending |
| line-3 | line-3-0683-0575-s003015 | forward | 4 | pending |
| line-3 | line-3-0683-0575-s003015 | reverse | 4 | pending |
| line-3 | line-3-0546-0559-s006400 | forward | 4 | pending |
| line-3 | line-3-0546-0559-s006400 | reverse | 4 | pending |
| line-3 | line-3-0411-0543-s009637 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Ismailia/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
