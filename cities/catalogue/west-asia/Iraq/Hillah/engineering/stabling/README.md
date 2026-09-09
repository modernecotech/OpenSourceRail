# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **125 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0278-0667-s000000 | forward | 4 | pending |
| line-1 | line-1-0367-0647-s003022 | forward | 4 | pending |
| line-1 | line-1-0367-0647-s003022 | reverse | 4 | pending |
| line-1 | line-1-0489-0616-s006026 | forward | 4 | pending |
| line-1 | line-1-0489-0616-s006026 | reverse | 4 | pending |
| line-1 | line-1-0555-0583-s007706 | forward | 4 | pending |
| line-1 | line-1-0555-0583-s007706 | reverse | 3 | pending |
| line-1 | line-1-0603-0599-s009034 | forward | 3 | pending |
| line-1 | line-1-0603-0599-s009034 | reverse | 3 | pending |
| line-1 | line-1-0730-0541-s012054 | forward | 3 | pending |
| line-1 | line-1-0730-0541-s012054 | reverse | 3 | pending |
| line-1 | line-1-1072-0471-s019474 | reverse | 3 | pending |
| line-2 | line-2-0032-0601-s000000 | forward | 4 | pending |
| line-2 | line-2-0246-0611-s007011 | forward | 4 | pending |
| line-2 | line-2-0246-0611-s007011 | reverse | 4 | pending |
| line-2 | line-2-0341-0536-s010016 | forward | 4 | pending |
| line-2 | line-2-0341-0536-s010016 | reverse | 4 | pending |
| line-2 | line-2-0469-0531-s013026 | forward | 3 | pending |
| line-2 | line-2-0469-0531-s013026 | reverse | 3 | pending |
| line-2 | line-2-0561-0517-s014982 | forward | 3 | pending |
| line-2 | line-2-0561-0517-s014982 | reverse | 3 | pending |
| line-2 | line-2-0636-0491-s016920 | forward | 3 | pending |
| line-2 | line-2-0636-0491-s016920 | reverse | 3 | pending |
| line-2 | line-2-0687-0442-s018881 | reverse | 3 | pending |
| line-3 | line-3-0598-0069-s000000 | forward | 4 | pending |
| line-3 | line-3-0597-0344-s007019 | forward | 4 | pending |
| line-3 | line-3-0597-0344-s007019 | reverse | 4 | pending |
| line-3 | line-3-0563-0480-s010044 | forward | 4 | pending |
| line-3 | line-3-0563-0480-s010044 | reverse | 4 | pending |
| line-3 | line-3-0555-0583-s012336 | forward | 4 | pending |
| line-3 | line-3-0555-0583-s012336 | reverse | 3 | pending |
| line-3 | line-3-0503-0654-s014732 | forward | 3 | pending |
| line-3 | line-3-0503-0654-s014732 | reverse | 3 | pending |
| line-3 | line-3-0433-0712-s017123 | forward | 3 | pending |
| line-3 | line-3-0433-0712-s017123 | reverse | 3 | pending |
| line-3 | line-3-0404-0807-s019508 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Hillah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
