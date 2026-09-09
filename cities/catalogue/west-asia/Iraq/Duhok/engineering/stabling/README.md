# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **122 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0682-0744-s000000 | forward | 3 | pending |
| line-1 | line-1-0651-0583-s003970 | forward | 3 | pending |
| line-1 | line-1-0651-0583-s003970 | reverse | 3 | pending |
| line-1 | line-1-0595-0461-s006984 | forward | 3 | pending |
| line-1 | line-1-0595-0461-s006984 | reverse | 3 | pending |
| line-1 | line-1-0539-0432-s008415 | forward | 3 | pending |
| line-1 | line-1-0539-0432-s008415 | reverse | 3 | pending |
| line-1 | line-1-0566-0376-s009996 | forward | 3 | pending |
| line-1 | line-1-0566-0376-s009996 | reverse | 3 | pending |
| line-1 | line-1-0564-0233-s013017 | forward | 3 | pending |
| line-1 | line-1-0564-0233-s013017 | reverse | 3 | pending |
| line-1 | line-1-0588-0118-s015762 | forward | 3 | pending |
| line-1 | line-1-0588-0118-s015762 | reverse | 2 | pending |
| line-1 | line-1-0584-0017-s018536 | reverse | 2 | pending |
| line-2 | line-2-0530-0094-s000000 | forward | 4 | pending |
| line-2 | line-2-0523-0228-s003005 | forward | 4 | pending |
| line-2 | line-2-0523-0228-s003005 | reverse | 4 | pending |
| line-2 | line-2-0542-0366-s006029 | forward | 4 | pending |
| line-2 | line-2-0542-0366-s006029 | reverse | 3 | pending |
| line-2 | line-2-0539-0432-s007556 | forward | 3 | pending |
| line-2 | line-2-0539-0432-s007556 | reverse | 3 | pending |
| line-2 | line-2-0515-0486-s009049 | forward | 3 | pending |
| line-2 | line-2-0515-0486-s009049 | reverse | 3 | pending |
| line-2 | line-2-0543-0667-s013673 | forward | 3 | pending |
| line-2 | line-2-0543-0667-s013673 | reverse | 3 | pending |
| line-2 | line-2-0533-0854-s018320 | reverse | 3 | pending |
| line-3 | line-3-0658-0007-s000000 | forward | 4 | pending |
| line-3 | line-3-0638-0211-s004697 | forward | 4 | pending |
| line-3 | line-3-0638-0211-s004697 | reverse | 4 | pending |
| line-3 | line-3-0617-0353-s007711 | forward | 4 | pending |
| line-3 | line-3-0617-0353-s007711 | reverse | 4 | pending |
| line-3 | line-3-0539-0432-s010654 | forward | 4 | pending |
| line-3 | line-3-0539-0432-s010654 | reverse | 3 | pending |
| line-3 | line-3-0599-0530-s013111 | forward | 3 | pending |
| line-3 | line-3-0599-0530-s013111 | reverse | 3 | pending |
| line-3 | line-3-0599-0652-s015551 | forward | 3 | pending |
| line-3 | line-3-0599-0652-s015551 | reverse | 3 | pending |
| line-3 | line-3-0540-0838-s020428 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Duhok/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
