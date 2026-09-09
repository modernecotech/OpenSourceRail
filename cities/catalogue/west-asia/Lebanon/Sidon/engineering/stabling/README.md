# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **79 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0585-0374-s000000 | forward | 4 | pending |
| line-1 | line-1-0465-0370-s003015 | forward | 4 | pending |
| line-1 | line-1-0465-0370-s003015 | reverse | 4 | pending |
| line-1 | line-1-0370-0384-s005527 | forward | 4 | pending |
| line-1 | line-1-0370-0384-s005527 | reverse | 4 | pending |
| line-1 | line-1-0322-0385-s007643 | forward | 4 | pending |
| line-1 | line-1-0322-0385-s007643 | reverse | 4 | pending |
| line-1 | line-1-0055-0553-s015039 | reverse | 3 | pending |
| line-2 | line-2-0499-0328-s000000 | forward | 3 | pending |
| line-2 | line-2-0370-0384-s003509 | forward | 3 | pending |
| line-2 | line-2-0370-0384-s003509 | reverse | 3 | pending |
| line-2 | line-2-0442-0433-s005605 | forward | 3 | pending |
| line-2 | line-2-0442-0433-s005605 | reverse | 3 | pending |
| line-2 | line-2-0519-0412-s007698 | forward | 2 | pending |
| line-2 | line-2-0519-0412-s007698 | reverse | 2 | pending |
| line-2 | line-2-0587-0461-s009803 | reverse | 2 | pending |
| line-3 | line-3-0380-0462-s000000 | forward | 5 | pending |
| line-3 | line-3-0370-0384-s001893 | forward | 5 | pending |
| line-3 | line-3-0370-0384-s001893 | reverse | 5 | pending |
| line-3 | line-3-0297-0445-s004620 | forward | 4 | pending |
| line-3 | line-3-0297-0445-s004620 | reverse | 4 | pending |
| line-3 | line-3-0041-0657-s012916 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Lebanon/Sidon/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
