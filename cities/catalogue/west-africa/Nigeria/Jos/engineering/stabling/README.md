# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **102 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0125-0723-s000000 | forward | 4 | pending |
| line-1 | line-1-0234-0678-s003016 | forward | 4 | pending |
| line-1 | line-1-0234-0678-s003016 | reverse | 4 | pending |
| line-1 | line-1-0340-0685-s006019 | forward | 4 | pending |
| line-1 | line-1-0340-0685-s006019 | reverse | 3 | pending |
| line-1 | line-1-0447-0666-s009040 | forward | 3 | pending |
| line-1 | line-1-0447-0666-s009040 | reverse | 3 | pending |
| line-1 | line-1-0527-0573-s012145 | forward | 3 | pending |
| line-1 | line-1-0527-0573-s012145 | reverse | 3 | pending |
| line-1 | line-1-0647-0601-s015050 | forward | 3 | pending |
| line-1 | line-1-0647-0601-s015050 | reverse | 3 | pending |
| line-1 | line-1-0752-0600-s018026 | forward | 3 | pending |
| line-1 | line-1-0752-0600-s018026 | reverse | 3 | pending |
| line-1 | line-1-0886-0587-s020991 | reverse | 3 | pending |
| line-2 | line-2-0217-0514-s000000 | forward | 3 | pending |
| line-2 | line-2-0338-0554-s003016 | forward | 3 | pending |
| line-2 | line-2-0338-0554-s003016 | reverse | 3 | pending |
| line-2 | line-2-0424-0573-s005057 | forward | 3 | pending |
| line-2 | line-2-0424-0573-s005057 | reverse | 3 | pending |
| line-2 | line-2-0527-0573-s007117 | forward | 3 | pending |
| line-2 | line-2-0527-0573-s007117 | reverse | 2 | pending |
| line-2 | line-2-0599-0534-s009032 | forward | 2 | pending |
| line-2 | line-2-0599-0534-s009032 | reverse | 2 | pending |
| line-2 | line-2-0686-0505-s011162 | forward | 2 | pending |
| line-2 | line-2-0686-0505-s011162 | reverse | 2 | pending |
| line-2 | line-2-0782-0526-s013305 | reverse | 2 | pending |
| line-3 | line-3-0338-0806-s000000 | forward | 4 | pending |
| line-3 | line-3-0403-0747-s003004 | forward | 4 | pending |
| line-3 | line-3-0403-0747-s003004 | reverse | 3 | pending |
| line-3 | line-3-0516-0735-s006014 | forward | 3 | pending |
| line-3 | line-3-0516-0735-s006014 | reverse | 3 | pending |
| line-3 | line-3-0650-0711-s009026 | forward | 3 | pending |
| line-3 | line-3-0650-0711-s009026 | reverse | 3 | pending |
| line-3 | line-3-0711-0754-s011594 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Jos/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
