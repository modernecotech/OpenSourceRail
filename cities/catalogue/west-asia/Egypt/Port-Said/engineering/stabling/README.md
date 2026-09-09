# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **64 trainsets at 15 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0781-0625-s000000 | forward | 3 | pending |
| line-1 | line-1-0653-0595-s003005 | forward | 3 | pending |
| line-1 | line-1-0653-0595-s003005 | reverse | 3 | pending |
| line-1 | line-1-0558-0545-s005753 | forward | 3 | pending |
| line-1 | line-1-0558-0545-s005753 | reverse | 3 | pending |
| line-1 | line-1-0570-0483-s007630 | forward | 3 | pending |
| line-1 | line-1-0570-0483-s007630 | reverse | 3 | pending |
| line-1 | line-1-0523-0402-s009887 | forward | 2 | pending |
| line-1 | line-1-0523-0402-s009887 | reverse | 2 | pending |
| line-1 | line-1-0524-0309-s012126 | reverse | 2 | pending |
| line-2 | line-2-0532-0606-s000000 | forward | 3 | pending |
| line-2 | line-2-0558-0545-s002347 | forward | 3 | pending |
| line-2 | line-2-0558-0545-s002347 | reverse | 3 | pending |
| line-2 | line-2-0599-0476-s004850 | forward | 3 | pending |
| line-2 | line-2-0599-0476-s004850 | reverse | 3 | pending |
| line-2 | line-2-0644-0359-s008173 | reverse | 3 | pending |
| line-3 | line-3-0684-0677-s000000 | forward | 3 | pending |
| line-3 | line-3-0591-0580-s003015 | forward | 3 | pending |
| line-3 | line-3-0591-0580-s003015 | reverse | 3 | pending |
| line-3 | line-3-0558-0545-s004289 | forward | 2 | pending |
| line-3 | line-3-0558-0545-s004289 | reverse | 2 | pending |
| line-3 | line-3-0624-0503-s006037 | forward | 2 | pending |
| line-3 | line-3-0624-0503-s006037 | reverse | 2 | pending |
| line-3 | line-3-0670-0414-s008895 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Port-Said/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
