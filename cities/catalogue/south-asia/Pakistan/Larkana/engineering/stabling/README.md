# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **79 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0944-0310-s000000 | forward | 4 | pending |
| line-1 | line-1-0652-0430-s007008 | forward | 4 | pending |
| line-1 | line-1-0652-0430-s007008 | reverse | 4 | pending |
| line-1 | line-1-0545-0502-s009815 | forward | 4 | pending |
| line-1 | line-1-0545-0502-s009815 | reverse | 4 | pending |
| line-1 | line-1-0548-0552-s011105 | forward | 4 | pending |
| line-1 | line-1-0548-0552-s011105 | reverse | 3 | pending |
| line-1 | line-1-0489-0555-s012815 | forward | 3 | pending |
| line-1 | line-1-0489-0555-s012815 | reverse | 3 | pending |
| line-1 | line-1-0420-0615-s015243 | forward | 3 | pending |
| line-1 | line-1-0420-0615-s015243 | reverse | 3 | pending |
| line-1 | line-1-0323-0675-s017680 | forward | 3 | pending |
| line-1 | line-1-0323-0675-s017680 | reverse | 3 | pending |
| line-1 | line-1-0223-0854-s022548 | reverse | 3 | pending |
| line-2 | line-2-0599-0582-s000000 | forward | 4 | pending |
| line-2 | line-2-0548-0552-s001269 | forward | 4 | pending |
| line-2 | line-2-0548-0552-s001269 | reverse | 4 | pending |
| line-2 | line-2-0477-0525-s003012 | forward | 4 | pending |
| line-2 | line-2-0477-0525-s003012 | reverse | 4 | pending |
| line-2 | line-2-0386-0600-s006019 | forward | 4 | pending |
| line-2 | line-2-0386-0600-s006019 | reverse | 4 | pending |
| line-2 | line-2-0029-0740-s014417 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Larkana/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
