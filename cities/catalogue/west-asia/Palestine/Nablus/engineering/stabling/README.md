# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **174 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0541-0831-s000000 | forward | 5 | pending |
| line-1 | line-1-0578-0720-s003005 | forward | 5 | pending |
| line-1 | line-1-0578-0720-s003005 | reverse | 5 | pending |
| line-1 | line-1-0577-0633-s005066 | forward | 5 | pending |
| line-1 | line-1-0577-0633-s005066 | reverse | 5 | pending |
| line-1 | line-1-0548-0557-s007130 | forward | 5 | pending |
| line-1 | line-1-0548-0557-s007130 | reverse | 5 | pending |
| line-1 | line-1-0534-0459-s010651 | forward | 5 | pending |
| line-1 | line-1-0534-0459-s010651 | reverse | 5 | pending |
| line-1 | line-1-0528-0122-s020455 | reverse | 5 | pending |
| line-2 | line-2-0783-0930-s000000 | forward | 6 | pending |
| line-2 | line-2-0628-0776-s004913 | forward | 6 | pending |
| line-2 | line-2-0628-0776-s004913 | reverse | 6 | pending |
| line-2 | line-2-0621-0635-s007918 | forward | 6 | pending |
| line-2 | line-2-0621-0635-s007918 | reverse | 6 | pending |
| line-2 | line-2-0548-0557-s010828 | forward | 6 | pending |
| line-2 | line-2-0548-0557-s010828 | reverse | 6 | pending |
| line-2 | line-2-0462-0551-s013336 | forward | 5 | pending |
| line-2 | line-2-0462-0551-s013336 | reverse | 5 | pending |
| line-2 | line-2-0387-0440-s016842 | forward | 5 | pending |
| line-2 | line-2-0387-0440-s016842 | reverse | 5 | pending |
| line-2 | line-2-0071-0128-s028312 | reverse | 5 | pending |
| line-3 | line-3-0065-1031-s000000 | forward | 8 | pending |
| line-3 | line-3-0423-0670-s014038 | forward | 7 | pending |
| line-3 | line-3-0423-0670-s014038 | reverse | 7 | pending |
| line-3 | line-3-0511-0653-s017089 | forward | 7 | pending |
| line-3 | line-3-0511-0653-s017089 | reverse | 7 | pending |
| line-3 | line-3-0548-0557-s019585 | forward | 7 | pending |
| line-3 | line-3-0548-0557-s019585 | reverse | 7 | pending |
| line-3 | line-3-0667-0454-s022961 | reverse | 7 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Nablus/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
