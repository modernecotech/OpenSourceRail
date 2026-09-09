# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **78 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0040-0699-s000000 | forward | 3 | pending |
| line-1 | line-1-0122-0602-s003011 | forward | 3 | pending |
| line-1 | line-1-0122-0602-s003011 | reverse | 3 | pending |
| line-1 | line-1-0227-0509-s006408 | forward | 3 | pending |
| line-1 | line-1-0227-0509-s006408 | reverse | 3 | pending |
| line-1 | line-1-0284-0443-s009010 | forward | 3 | pending |
| line-1 | line-1-0284-0443-s009010 | reverse | 2 | pending |
| line-1 | line-1-0354-0386-s011309 | forward | 2 | pending |
| line-1 | line-1-0354-0386-s011309 | reverse | 2 | pending |
| line-1 | line-1-0362-0294-s013409 | forward | 2 | pending |
| line-1 | line-1-0362-0294-s013409 | reverse | 2 | pending |
| line-1 | line-1-0323-0219-s015490 | reverse | 2 | pending |
| line-2 | line-2-0437-0275-s000000 | forward | 3 | pending |
| line-2 | line-2-0354-0386-s003585 | forward | 3 | pending |
| line-2 | line-2-0354-0386-s003585 | reverse | 3 | pending |
| line-2 | line-2-0278-0362-s005744 | forward | 3 | pending |
| line-2 | line-2-0278-0362-s005744 | reverse | 3 | pending |
| line-2 | line-2-0222-0297-s007889 | reverse | 2 | pending |
| line-3 | line-3-0433-0385-s000000 | forward | 4 | pending |
| line-3 | line-3-0354-0386-s002233 | forward | 3 | pending |
| line-3 | line-3-0354-0386-s002233 | reverse | 3 | pending |
| line-3 | line-3-0353-0460-s004120 | forward | 3 | pending |
| line-3 | line-3-0353-0460-s004120 | reverse | 3 | pending |
| line-3 | line-3-0281-0508-s006007 | forward | 3 | pending |
| line-3 | line-3-0281-0508-s006007 | reverse | 3 | pending |
| line-3 | line-3-0154-0560-s009023 | forward | 3 | pending |
| line-3 | line-3-0154-0560-s009023 | reverse | 3 | pending |
| line-3 | line-3-0000-0751-s015542 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Entebbe/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
