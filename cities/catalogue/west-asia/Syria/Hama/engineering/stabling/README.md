# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **114 trainsets at 19 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0194-0142-s000000 | forward | 4 | pending |
| line-1 | line-1-0432-0345-s007014 | forward | 4 | pending |
| line-1 | line-1-0432-0345-s007014 | reverse | 4 | pending |
| line-1 | line-1-0475-0454-s010036 | forward | 4 | pending |
| line-1 | line-1-0475-0454-s010036 | reverse | 4 | pending |
| line-1 | line-1-0550-0551-s013769 | forward | 4 | pending |
| line-1 | line-1-0550-0551-s013769 | reverse | 4 | pending |
| line-1 | line-1-0541-0621-s015984 | forward | 4 | pending |
| line-1 | line-1-0541-0621-s015984 | reverse | 4 | pending |
| line-1 | line-1-0620-0708-s018465 | forward | 4 | pending |
| line-1 | line-1-0620-0708-s018465 | reverse | 3 | pending |
| line-1 | line-1-0708-0757-s020923 | reverse | 3 | pending |
| line-2 | line-2-0768-0539-s000000 | forward | 3 | pending |
| line-2 | line-2-0621-0545-s003006 | forward | 3 | pending |
| line-2 | line-2-0621-0545-s003006 | reverse | 3 | pending |
| line-2 | line-2-0550-0551-s004625 | forward | 3 | pending |
| line-2 | line-2-0550-0551-s004625 | reverse | 3 | pending |
| line-2 | line-2-0470-0534-s006925 | forward | 3 | pending |
| line-2 | line-2-0470-0534-s006925 | reverse | 3 | pending |
| line-2 | line-2-0369-0566-s009226 | forward | 2 | pending |
| line-2 | line-2-0369-0566-s009226 | reverse | 2 | pending |
| line-2 | line-2-0313-0629-s011524 | reverse | 2 | pending |
| line-3 | line-3-0581-0072-s000000 | forward | 5 | pending |
| line-3 | line-3-0504-0373-s007020 | forward | 4 | pending |
| line-3 | line-3-0504-0373-s007020 | reverse | 4 | pending |
| line-3 | line-3-0616-0448-s010026 | forward | 4 | pending |
| line-3 | line-3-0616-0448-s010026 | reverse | 4 | pending |
| line-3 | line-3-0550-0551-s013648 | forward | 4 | pending |
| line-3 | line-3-0550-0551-s013648 | reverse | 4 | pending |
| line-3 | line-3-0531-0651-s016060 | forward | 4 | pending |
| line-3 | line-3-0531-0651-s016060 | reverse | 4 | pending |
| line-3 | line-3-0586-0750-s018998 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Hama/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
