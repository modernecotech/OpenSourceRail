# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **96 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0726-0492-s000000 | forward | 4 | pending |
| line-1 | line-1-0627-0492-s003006 | forward | 3 | pending |
| line-1 | line-1-0627-0492-s003006 | reverse | 3 | pending |
| line-1 | line-1-0542-0554-s005313 | forward | 3 | pending |
| line-1 | line-1-0542-0554-s005313 | reverse | 3 | pending |
| line-1 | line-1-0410-0471-s009032 | forward | 3 | pending |
| line-1 | line-1-0410-0471-s009032 | reverse | 3 | pending |
| line-1 | line-1-0318-0458-s012053 | forward | 3 | pending |
| line-1 | line-1-0318-0458-s012053 | reverse | 3 | pending |
| line-1 | line-1-0199-0416-s014781 | forward | 3 | pending |
| line-1 | line-1-0199-0416-s014781 | reverse | 3 | pending |
| line-1 | line-1-0096-0402-s017512 | reverse | 3 | pending |
| line-2 | line-2-0637-0296-s000000 | forward | 3 | pending |
| line-2 | line-2-0610-0337-s001620 | forward | 3 | pending |
| line-2 | line-2-0610-0337-s001620 | reverse | 3 | pending |
| line-2 | line-2-0603-0444-s004632 | forward | 3 | pending |
| line-2 | line-2-0603-0444-s004632 | reverse | 3 | pending |
| line-2 | line-2-0542-0554-s007646 | forward | 3 | pending |
| line-2 | line-2-0542-0554-s007646 | reverse | 3 | pending |
| line-2 | line-2-0532-0653-s009917 | forward | 2 | pending |
| line-2 | line-2-0532-0653-s009917 | reverse | 2 | pending |
| line-2 | line-2-0473-0714-s012175 | reverse | 2 | pending |
| line-3 | line-3-0027-0206-s000000 | forward | 4 | pending |
| line-3 | line-3-0169-0376-s005406 | forward | 4 | pending |
| line-3 | line-3-0169-0376-s005406 | reverse | 4 | pending |
| line-3 | line-3-0213-0482-s008415 | forward | 4 | pending |
| line-3 | line-3-0213-0482-s008415 | reverse | 4 | pending |
| line-3 | line-3-0314-0548-s011433 | forward | 4 | pending |
| line-3 | line-3-0314-0548-s011433 | reverse | 4 | pending |
| line-3 | line-3-0432-0677-s015136 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Beira/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
