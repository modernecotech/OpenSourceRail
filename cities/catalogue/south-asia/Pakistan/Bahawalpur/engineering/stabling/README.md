# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **100 trainsets at 16 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0962-0331-s000000 | forward | 4 | pending |
| line-1 | line-1-0738-0445-s007010 | forward | 4 | pending |
| line-1 | line-1-0738-0445-s007010 | reverse | 4 | pending |
| line-1 | line-1-0612-0491-s010018 | forward | 4 | pending |
| line-1 | line-1-0612-0491-s010018 | reverse | 4 | pending |
| line-1 | line-1-0552-0549-s012289 | forward | 4 | pending |
| line-1 | line-1-0552-0549-s012289 | reverse | 4 | pending |
| line-1 | line-1-0499-0632-s014484 | forward | 3 | pending |
| line-1 | line-1-0499-0632-s014484 | reverse | 3 | pending |
| line-1 | line-1-0461-0724-s016691 | reverse | 3 | pending |
| line-2 | line-2-0153-0365-s000000 | forward | 5 | pending |
| line-2 | line-2-0412-0470-s007015 | forward | 5 | pending |
| line-2 | line-2-0412-0470-s007015 | reverse | 4 | pending |
| line-2 | line-2-0552-0549-s010701 | forward | 4 | pending |
| line-2 | line-2-0552-0549-s010701 | reverse | 4 | pending |
| line-2 | line-2-0573-0608-s012786 | forward | 4 | pending |
| line-2 | line-2-0573-0608-s012786 | reverse | 4 | pending |
| line-2 | line-2-0611-0693-s014879 | reverse | 4 | pending |
| line-3 | line-3-0662-0893-s000000 | forward | 4 | pending |
| line-3 | line-3-0590-0720-s005541 | forward | 4 | pending |
| line-3 | line-3-0590-0720-s005541 | reverse | 4 | pending |
| line-3 | line-3-0554-0626-s008548 | forward | 4 | pending |
| line-3 | line-3-0554-0626-s008548 | reverse | 4 | pending |
| line-3 | line-3-0552-0549-s010188 | forward | 3 | pending |
| line-3 | line-3-0552-0549-s010188 | reverse | 3 | pending |
| line-3 | line-3-0547-0439-s013275 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Bahawalpur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
