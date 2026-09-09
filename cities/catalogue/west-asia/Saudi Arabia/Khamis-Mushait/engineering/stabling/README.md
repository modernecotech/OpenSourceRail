# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **217 trainsets at 25 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1093-0994-s000000 | forward | 5 | pending |
| line-1 | line-1-0902-0838-s005711 | forward | 5 | pending |
| line-1 | line-1-0902-0838-s005711 | reverse | 5 | pending |
| line-1 | line-1-0783-0768-s009656 | forward | 5 | pending |
| line-1 | line-1-0783-0768-s009656 | reverse | 5 | pending |
| line-1 | line-1-0753-0643-s012656 | forward | 5 | pending |
| line-1 | line-1-0753-0643-s012656 | reverse | 5 | pending |
| line-1 | line-1-0640-0560-s015674 | forward | 5 | pending |
| line-1 | line-1-0640-0560-s015674 | reverse | 5 | pending |
| line-1 | line-1-0558-0544-s017967 | forward | 5 | pending |
| line-1 | line-1-0558-0544-s017967 | reverse | 5 | pending |
| line-1 | line-1-0500-0469-s020426 | forward | 5 | pending |
| line-1 | line-1-0500-0469-s020426 | reverse | 5 | pending |
| line-1 | line-1-0398-0392-s023444 | forward | 5 | pending |
| line-1 | line-1-0398-0392-s023444 | reverse | 4 | pending |
| line-1 | line-1-0215-0272-s029101 | reverse | 4 | pending |
| line-2 | line-2-0980-0761-s000000 | forward | 6 | pending |
| line-2 | line-2-0834-0685-s004323 | forward | 6 | pending |
| line-2 | line-2-0834-0685-s004323 | reverse | 6 | pending |
| line-2 | line-2-0786-0557-s007519 | forward | 6 | pending |
| line-2 | line-2-0786-0557-s007519 | reverse | 6 | pending |
| line-2 | line-2-0698-0471-s010912 | forward | 6 | pending |
| line-2 | line-2-0698-0471-s010912 | reverse | 6 | pending |
| line-2 | line-2-0573-0413-s013916 | forward | 6 | pending |
| line-2 | line-2-0573-0413-s013916 | reverse | 6 | pending |
| line-2 | line-2-0520-0326-s016926 | forward | 5 | pending |
| line-2 | line-2-0520-0326-s016926 | reverse | 5 | pending |
| line-2 | line-2-0284-0038-s025542 | reverse | 5 | pending |
| line-3 | line-3-0198-0413-s000000 | forward | 5 | pending |
| line-3 | line-3-0315-0464-s003009 | forward | 5 | pending |
| line-3 | line-3-0315-0464-s003009 | reverse | 5 | pending |
| line-3 | line-3-0423-0552-s006015 | forward | 5 | pending |
| line-3 | line-3-0423-0552-s006015 | reverse | 5 | pending |
| line-3 | line-3-0507-0584-s008065 | forward | 5 | pending |
| line-3 | line-3-0507-0584-s008065 | reverse | 4 | pending |
| line-3 | line-3-0558-0544-s010119 | forward | 4 | pending |
| line-3 | line-3-0558-0544-s010119 | reverse | 4 | pending |
| line-3 | line-3-0636-0634-s013660 | forward | 4 | pending |
| line-3 | line-3-0636-0634-s013660 | reverse | 4 | pending |
| line-3 | line-3-0711-0748-s017179 | forward | 4 | pending |
| line-3 | line-3-0711-0748-s017179 | reverse | 4 | pending |
| line-3 | line-3-0834-0853-s020673 | forward | 4 | pending |
| line-3 | line-3-0834-0853-s020673 | reverse | 4 | pending |
| line-3 | line-3-1002-1014-s026523 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Khamis-Mushait/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
