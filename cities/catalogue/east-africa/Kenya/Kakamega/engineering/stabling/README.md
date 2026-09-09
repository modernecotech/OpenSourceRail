# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **83 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0296-0125-s000000 | forward | 4 | pending |
| line-1 | line-1-0376-0243-s003023 | forward | 4 | pending |
| line-1 | line-1-0376-0243-s003023 | reverse | 4 | pending |
| line-1 | line-1-0372-0368-s006097 | forward | 3 | pending |
| line-1 | line-1-0372-0368-s006097 | reverse | 3 | pending |
| line-1 | line-1-0455-0478-s009843 | forward | 3 | pending |
| line-1 | line-1-0455-0478-s009843 | reverse | 3 | pending |
| line-1 | line-1-0477-0623-s013606 | reverse | 3 | pending |
| line-2 | line-2-0086-0716-s000000 | forward | 3 | pending |
| line-2 | line-2-0147-0574-s003616 | forward | 3 | pending |
| line-2 | line-2-0147-0574-s003616 | reverse | 3 | pending |
| line-2 | line-2-0258-0485-s006620 | forward | 3 | pending |
| line-2 | line-2-0258-0485-s006620 | reverse | 3 | pending |
| line-2 | line-2-0326-0424-s008532 | forward | 3 | pending |
| line-2 | line-2-0326-0424-s008532 | reverse | 2 | pending |
| line-2 | line-2-0372-0368-s010466 | forward | 2 | pending |
| line-2 | line-2-0372-0368-s010466 | reverse | 2 | pending |
| line-2 | line-2-0427-0289-s012939 | forward | 2 | pending |
| line-2 | line-2-0427-0289-s012939 | reverse | 2 | pending |
| line-2 | line-2-0450-0180-s015425 | reverse | 2 | pending |
| line-3 | line-3-0181-0288-s000000 | forward | 4 | pending |
| line-3 | line-3-0288-0352-s003006 | forward | 4 | pending |
| line-3 | line-3-0288-0352-s003006 | reverse | 3 | pending |
| line-3 | line-3-0372-0368-s005086 | forward | 3 | pending |
| line-3 | line-3-0372-0368-s005086 | reverse | 3 | pending |
| line-3 | line-3-0477-0364-s007639 | forward | 3 | pending |
| line-3 | line-3-0477-0364-s007639 | reverse | 3 | pending |
| line-3 | line-3-0702-0427-s013132 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kakamega/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
