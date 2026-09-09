# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **130 trainsets at 21 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0279-0389-s000000 | forward | 3 | pending |
| line-1 | line-1-0405-0476-s003756 | forward | 3 | pending |
| line-1 | line-1-0405-0476-s003756 | reverse | 3 | pending |
| line-1 | line-1-0473-0528-s005650 | forward | 3 | pending |
| line-1 | line-1-0473-0528-s005650 | reverse | 3 | pending |
| line-1 | line-1-0555-0545-s007525 | forward | 3 | pending |
| line-1 | line-1-0555-0545-s007525 | reverse | 3 | pending |
| line-1 | line-1-0614-0565-s008975 | forward | 2 | pending |
| line-1 | line-1-0614-0565-s008975 | reverse | 2 | pending |
| line-1 | line-1-0699-0614-s011097 | forward | 2 | pending |
| line-1 | line-1-0699-0614-s011097 | reverse | 2 | pending |
| line-1 | line-1-0793-0600-s013220 | forward | 2 | pending |
| line-1 | line-1-0793-0600-s013220 | reverse | 2 | pending |
| line-1 | line-1-0879-0586-s015329 | reverse | 2 | pending |
| line-2 | line-2-0445-0723-s000000 | forward | 4 | pending |
| line-2 | line-2-0471-0638-s003004 | forward | 4 | pending |
| line-2 | line-2-0471-0638-s003004 | reverse | 4 | pending |
| line-2 | line-2-0519-0578-s006019 | forward | 4 | pending |
| line-2 | line-2-0519-0578-s006019 | reverse | 4 | pending |
| line-2 | line-2-0555-0545-s007638 | forward | 3 | pending |
| line-2 | line-2-0555-0545-s007638 | reverse | 3 | pending |
| line-2 | line-2-0673-0469-s010656 | forward | 3 | pending |
| line-2 | line-2-0673-0469-s010656 | reverse | 3 | pending |
| line-2 | line-2-0873-0483-s015548 | forward | 3 | pending |
| line-2 | line-2-0873-0483-s015548 | reverse | 3 | pending |
| line-2 | line-2-1084-0450-s020325 | reverse | 3 | pending |
| line-3 | line-3-0078-0053-s000000 | forward | 6 | pending |
| line-3 | line-3-0381-0365-s010502 | forward | 6 | pending |
| line-3 | line-3-0381-0365-s010502 | reverse | 6 | pending |
| line-3 | line-3-0518-0447-s014015 | forward | 6 | pending |
| line-3 | line-3-0518-0447-s014015 | reverse | 5 | pending |
| line-3 | line-3-0555-0545-s016442 | forward | 5 | pending |
| line-3 | line-3-0555-0545-s016442 | reverse | 5 | pending |
| line-3 | line-3-0576-0675-s019388 | forward | 5 | pending |
| line-3 | line-3-0576-0675-s019388 | reverse | 5 | pending |
| line-3 | line-3-0761-0860-s025578 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Barisal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
