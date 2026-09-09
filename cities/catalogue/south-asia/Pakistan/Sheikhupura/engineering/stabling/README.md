# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **37 trainsets at 9 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0501-0372-s000000 | forward | 3 | pending |
| line-1 | line-1-0515-0511-s003026 | forward | 3 | pending |
| line-1 | line-1-0515-0511-s003026 | reverse | 3 | pending |
| line-1 | line-1-0551-0554-s004524 | forward | 2 | pending |
| line-1 | line-1-0551-0554-s004524 | reverse | 2 | pending |
| line-1 | line-1-0556-0617-s005931 | forward | 2 | pending |
| line-1 | line-1-0556-0617-s005931 | reverse | 2 | pending |
| line-1 | line-1-0599-0736-s008684 | reverse | 2 | pending |
| line-2 | line-2-0517-0430-s000000 | forward | 3 | pending |
| line-2 | line-2-0551-0554-s002915 | forward | 3 | pending |
| line-2 | line-2-0551-0554-s002915 | reverse | 3 | pending |
| line-2 | line-2-0596-0640-s005385 | forward | 3 | pending |
| line-2 | line-2-0596-0640-s005385 | reverse | 3 | pending |
| line-2 | line-2-0601-0732-s007869 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sheikhupura/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
