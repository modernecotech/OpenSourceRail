# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **61 trainsets at 11 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0437-0399-s000000 | forward | 4 | pending |
| line-1 | line-1-0372-0374-s002051 | forward | 4 | pending |
| line-1 | line-1-0372-0374-s002051 | reverse | 4 | pending |
| line-1 | line-1-0296-0314-s004635 | forward | 4 | pending |
| line-1 | line-1-0296-0314-s004635 | reverse | 4 | pending |
| line-1 | line-1-0091-0118-s011307 | reverse | 4 | pending |
| line-2 | line-2-0521-0676-s000000 | forward | 4 | pending |
| line-2 | line-2-0433-0448-s006249 | forward | 4 | pending |
| line-2 | line-2-0433-0448-s006249 | reverse | 4 | pending |
| line-2 | line-2-0372-0374-s009276 | forward | 3 | pending |
| line-2 | line-2-0372-0374-s009276 | reverse | 3 | pending |
| line-2 | line-2-0315-0387-s010668 | reverse | 3 | pending |
| line-3 | line-3-0389-0349-s000000 | forward | 4 | pending |
| line-3 | line-3-0353-0461-s003570 | forward | 4 | pending |
| line-3 | line-3-0353-0461-s003570 | reverse | 4 | pending |
| line-3 | line-3-0357-0605-s007141 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Hoima/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
