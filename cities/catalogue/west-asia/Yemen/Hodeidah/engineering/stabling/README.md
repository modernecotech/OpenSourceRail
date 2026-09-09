# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **71 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0438-0661-s000000 | forward | 3 | pending |
| line-1 | line-1-0503-0587-s003011 | forward | 3 | pending |
| line-1 | line-1-0503-0587-s003011 | reverse | 3 | pending |
| line-1 | line-1-0551-0553-s004358 | forward | 3 | pending |
| line-1 | line-1-0551-0553-s004358 | reverse | 3 | pending |
| line-1 | line-1-0651-0539-s007010 | forward | 3 | pending |
| line-1 | line-1-0651-0539-s007010 | reverse | 3 | pending |
| line-1 | line-1-0761-0550-s009675 | reverse | 2 | pending |
| line-2 | line-2-0701-0650-s000000 | forward | 3 | pending |
| line-2 | line-2-0602-0608-s003023 | forward | 3 | pending |
| line-2 | line-2-0602-0608-s003023 | reverse | 3 | pending |
| line-2 | line-2-0551-0553-s005218 | forward | 3 | pending |
| line-2 | line-2-0551-0553-s005218 | reverse | 3 | pending |
| line-2 | line-2-0538-0470-s007331 | forward | 3 | pending |
| line-2 | line-2-0538-0470-s007331 | reverse | 3 | pending |
| line-2 | line-2-0464-0396-s009459 | forward | 2 | pending |
| line-2 | line-2-0464-0396-s009459 | reverse | 2 | pending |
| line-2 | line-2-0384-0342-s011570 | reverse | 2 | pending |
| line-3 | line-3-0512-0772-s000000 | forward | 4 | pending |
| line-3 | line-3-0528-0670-s003013 | forward | 4 | pending |
| line-3 | line-3-0528-0670-s003013 | reverse | 4 | pending |
| line-3 | line-3-0551-0553-s005843 | forward | 3 | pending |
| line-3 | line-3-0551-0553-s005843 | reverse | 3 | pending |
| line-3 | line-3-0433-0500-s009427 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Hodeidah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
