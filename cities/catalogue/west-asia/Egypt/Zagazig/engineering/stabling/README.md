# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **92 trainsets at 17 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0078-0386-s000000 | forward | 4 | pending |
| line-1 | line-1-0366-0491-s007017 | forward | 4 | pending |
| line-1 | line-1-0366-0491-s007017 | reverse | 4 | pending |
| line-1 | line-1-0483-0567-s010033 | forward | 4 | pending |
| line-1 | line-1-0483-0567-s010033 | reverse | 4 | pending |
| line-1 | line-1-0544-0561-s011561 | forward | 4 | pending |
| line-1 | line-1-0544-0561-s011561 | reverse | 4 | pending |
| line-1 | line-1-0643-0582-s014260 | forward | 3 | pending |
| line-1 | line-1-0643-0582-s014260 | reverse | 3 | pending |
| line-1 | line-1-0747-0629-s016962 | reverse | 3 | pending |
| line-2 | line-2-0527-0431-s000000 | forward | 3 | pending |
| line-2 | line-2-0544-0561-s003686 | forward | 3 | pending |
| line-2 | line-2-0544-0561-s003686 | reverse | 3 | pending |
| line-2 | line-2-0523-0644-s005928 | forward | 3 | pending |
| line-2 | line-2-0523-0644-s005928 | reverse | 3 | pending |
| line-2 | line-2-0562-0740-s008171 | forward | 3 | pending |
| line-2 | line-2-0562-0740-s008171 | reverse | 3 | pending |
| line-2 | line-2-0617-0819-s010429 | reverse | 2 | pending |
| line-3 | line-3-0354-0190-s000000 | forward | 4 | pending |
| line-3 | line-3-0458-0322-s003502 | forward | 4 | pending |
| line-3 | line-3-0458-0322-s003502 | reverse | 3 | pending |
| line-3 | line-3-0475-0442-s007017 | forward | 3 | pending |
| line-3 | line-3-0475-0442-s007017 | reverse | 3 | pending |
| line-3 | line-3-0544-0561-s010522 | forward | 3 | pending |
| line-3 | line-3-0544-0561-s010522 | reverse | 3 | pending |
| line-3 | line-3-0494-0649-s013000 | forward | 3 | pending |
| line-3 | line-3-0494-0649-s013000 | reverse | 3 | pending |
| line-3 | line-3-0477-0747-s015498 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Zagazig/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
