# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **98 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0509-0798-s000000 | forward | 4 | pending |
| line-1 | line-1-0499-0673-s003049 | forward | 4 | pending |
| line-1 | line-1-0499-0673-s003049 | reverse | 3 | pending |
| line-1 | line-1-0559-0556-s006410 | forward | 3 | pending |
| line-1 | line-1-0559-0556-s006410 | reverse | 3 | pending |
| line-1 | line-1-0493-0475-s009024 | reverse | 3 | pending |
| line-2 | line-2-0561-0605-s000000 | forward | 5 | pending |
| line-2 | line-2-0591-0566-s002100 | forward | 5 | pending |
| line-2 | line-2-0591-0566-s002100 | reverse | 5 | pending |
| line-2 | line-2-0726-0575-s005101 | forward | 5 | pending |
| line-2 | line-2-0726-0575-s005101 | reverse | 5 | pending |
| line-2 | line-2-0761-0446-s008592 | forward | 4 | pending |
| line-2 | line-2-0761-0446-s008592 | reverse | 4 | pending |
| line-2 | line-2-1096-0417-s016706 | reverse | 4 | pending |
| line-3 | line-3-0531-0609-s000000 | forward | 6 | pending |
| line-3 | line-3-0559-0556-s001315 | forward | 5 | pending |
| line-3 | line-3-0559-0556-s001315 | reverse | 5 | pending |
| line-3 | line-3-0606-0545-s002665 | forward | 5 | pending |
| line-3 | line-3-0606-0545-s002665 | reverse | 5 | pending |
| line-3 | line-3-0698-0622-s005674 | forward | 5 | pending |
| line-3 | line-3-0698-0622-s005674 | reverse | 5 | pending |
| line-3 | line-3-1014-1054-s018676 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Sohag/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
