# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **129 trainsets at 15 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0457-0559-s000000 | forward | 3 | pending |
| line-1 | line-1-0549-0556-s002531 | forward | 3 | pending |
| line-1 | line-1-0549-0556-s002531 | reverse | 3 | pending |
| line-1 | line-1-0571-0599-s004234 | forward | 3 | pending |
| line-1 | line-1-0571-0599-s004234 | reverse | 3 | pending |
| line-1 | line-1-0630-0629-s005944 | forward | 3 | pending |
| line-1 | line-1-0630-0629-s005944 | reverse | 3 | pending |
| line-1 | line-1-0704-0697-s008058 | forward | 3 | pending |
| line-1 | line-1-0704-0697-s008058 | reverse | 3 | pending |
| line-1 | line-1-0717-0786-s010172 | reverse | 3 | pending |
| line-2 | line-2-0742-0447-s000000 | forward | 7 | pending |
| line-2 | line-2-0604-0486-s003199 | forward | 7 | pending |
| line-2 | line-2-0604-0486-s003199 | reverse | 7 | pending |
| line-2 | line-2-0549-0556-s005328 | forward | 7 | pending |
| line-2 | line-2-0549-0556-s005328 | reverse | 7 | pending |
| line-2 | line-2-0181-1033-s018352 | reverse | 7 | pending |
| line-3 | line-3-0212-1034-s000000 | forward | 8 | pending |
| line-3 | line-3-0503-0660-s010315 | forward | 7 | pending |
| line-3 | line-3-0503-0660-s010315 | reverse | 7 | pending |
| line-3 | line-3-0549-0556-s012866 | forward | 7 | pending |
| line-3 | line-3-0549-0556-s012866 | reverse | 7 | pending |
| line-3 | line-3-0732-0385-s019095 | forward | 7 | pending |
| line-3 | line-3-0732-0385-s019095 | reverse | 7 | pending |
| line-3 | line-3-0885-0164-s025052 | reverse | 7 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Rahim-Yar-Khan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
