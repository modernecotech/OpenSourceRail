# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **60 trainsets at 13 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0690-0486-s000000 | forward | 4 | pending |
| line-1 | line-1-0512-0433-s004413 | forward | 4 | pending |
| line-1 | line-1-0512-0433-s004413 | reverse | 3 | pending |
| line-1 | line-1-0418-0412-s006467 | forward | 3 | pending |
| line-1 | line-1-0418-0412-s006467 | reverse | 3 | pending |
| line-1 | line-1-0378-0379-s008522 | forward | 3 | pending |
| line-1 | line-1-0378-0379-s008522 | reverse | 3 | pending |
| line-1 | line-1-0257-0324-s012179 | reverse | 3 | pending |
| line-2 | line-2-0506-0606-s000000 | forward | 3 | pending |
| line-2 | line-2-0485-0487-s003009 | forward | 3 | pending |
| line-2 | line-2-0485-0487-s003009 | reverse | 3 | pending |
| line-2 | line-2-0368-0447-s006014 | forward | 3 | pending |
| line-2 | line-2-0368-0447-s006014 | reverse | 3 | pending |
| line-2 | line-2-0378-0379-s008154 | forward | 2 | pending |
| line-2 | line-2-0378-0379-s008154 | reverse | 2 | pending |
| line-2 | line-2-0297-0414-s010664 | reverse | 2 | pending |
| line-3 | line-3-0271-0453-s000000 | forward | 4 | pending |
| line-3 | line-3-0378-0379-s003423 | forward | 3 | pending |
| line-3 | line-3-0378-0379-s003423 | reverse | 3 | pending |
| line-3 | line-3-0428-0348-s004984 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Tartus/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
