# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **93 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0693-0490-s000000 | forward | 4 | pending |
| line-1 | line-1-0653-0514-s003005 | forward | 4 | pending |
| line-1 | line-1-0653-0514-s003005 | reverse | 4 | pending |
| line-1 | line-1-0551-0553-s005665 | forward | 4 | pending |
| line-1 | line-1-0551-0553-s005665 | reverse | 4 | pending |
| line-1 | line-1-0537-0651-s009047 | forward | 4 | pending |
| line-1 | line-1-0537-0651-s009047 | reverse | 4 | pending |
| line-1 | line-1-0491-0817-s013635 | forward | 4 | pending |
| line-1 | line-1-0491-0817-s013635 | reverse | 4 | pending |
| line-1 | line-1-0371-0993-s018243 | reverse | 3 | pending |
| line-2 | line-2-0452-0423-s000000 | forward | 4 | pending |
| line-2 | line-2-0522-0520-s003004 | forward | 4 | pending |
| line-2 | line-2-0522-0520-s003004 | reverse | 3 | pending |
| line-2 | line-2-0551-0553-s004361 | forward | 3 | pending |
| line-2 | line-2-0551-0553-s004361 | reverse | 3 | pending |
| line-2 | line-2-0538-0601-s006016 | forward | 3 | pending |
| line-2 | line-2-0538-0601-s006016 | reverse | 3 | pending |
| line-2 | line-2-0400-0736-s011465 | reverse | 3 | pending |
| line-3 | line-3-0682-0473-s000000 | forward | 3 | pending |
| line-3 | line-3-0611-0492-s002060 | forward | 3 | pending |
| line-3 | line-3-0611-0492-s002060 | reverse | 3 | pending |
| line-3 | line-3-0551-0553-s004130 | forward | 3 | pending |
| line-3 | line-3-0551-0553-s004130 | reverse | 3 | pending |
| line-3 | line-3-0499-0511-s006021 | forward | 3 | pending |
| line-3 | line-3-0499-0511-s006021 | reverse | 3 | pending |
| line-3 | line-3-0406-0435-s009581 | forward | 3 | pending |
| line-3 | line-3-0406-0435-s009581 | reverse | 2 | pending |
| line-3 | line-3-0301-0356-s013135 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Latakia/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
