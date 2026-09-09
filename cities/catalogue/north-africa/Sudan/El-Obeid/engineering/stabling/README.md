# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **102 trainsets at 19 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0431-0673-s000000 | forward | 3 | pending |
| line-1 | line-1-0515-0619-s003018 | forward | 3 | pending |
| line-1 | line-1-0515-0619-s003018 | reverse | 3 | pending |
| line-1 | line-1-0559-0554-s005270 | forward | 3 | pending |
| line-1 | line-1-0559-0554-s005270 | reverse | 3 | pending |
| line-1 | line-1-0633-0594-s007140 | forward | 3 | pending |
| line-1 | line-1-0633-0594-s007140 | reverse | 3 | pending |
| line-1 | line-1-0725-0594-s009030 | forward | 3 | pending |
| line-1 | line-1-0725-0594-s009030 | reverse | 3 | pending |
| line-1 | line-1-0938-0541-s014730 | forward | 3 | pending |
| line-1 | line-1-0938-0541-s014730 | reverse | 3 | pending |
| line-1 | line-1-1002-0556-s016349 | reverse | 3 | pending |
| line-2 | line-2-0437-0770-s000000 | forward | 4 | pending |
| line-2 | line-2-0485-0682-s003011 | forward | 3 | pending |
| line-2 | line-2-0485-0682-s003011 | reverse | 3 | pending |
| line-2 | line-2-0572-0613-s006028 | forward | 3 | pending |
| line-2 | line-2-0572-0613-s006028 | reverse | 3 | pending |
| line-2 | line-2-0559-0554-s007478 | forward | 3 | pending |
| line-2 | line-2-0559-0554-s007478 | reverse | 3 | pending |
| line-2 | line-2-0620-0530-s009045 | forward | 3 | pending |
| line-2 | line-2-0620-0530-s009045 | reverse | 3 | pending |
| line-2 | line-2-0723-0472-s012068 | forward | 3 | pending |
| line-2 | line-2-0723-0472-s012068 | reverse | 3 | pending |
| line-2 | line-2-0933-0407-s017459 | reverse | 3 | pending |
| line-3 | line-3-0999-0567-s000000 | forward | 4 | pending |
| line-3 | line-3-0878-0642-s003518 | forward | 4 | pending |
| line-3 | line-3-0878-0642-s003518 | reverse | 4 | pending |
| line-3 | line-3-0757-0717-s007018 | forward | 4 | pending |
| line-3 | line-3-0757-0717-s007018 | reverse | 4 | pending |
| line-3 | line-3-0669-0719-s010031 | forward | 3 | pending |
| line-3 | line-3-0669-0719-s010031 | reverse | 3 | pending |
| line-3 | line-3-0578-0800-s013439 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/El-Obeid/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
